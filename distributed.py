import os
import json
import logging
import pandas as pd
import requests
from bs4 import BeautifulSoup
from parsel import Selector
from tqdm import tqdm

# === Configuração de Logging ===
LOG_FILE = "scraper.log"
logging.basicConfig(
    level=logging.DEBUG,  # DEBUG mostra tudo; mude para INFO se quiser menos
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),                # Console
        logging.FileHandler(LOG_FILE, encoding="utf-8")  # Arquivo
    ]
)

leagues = [
    'Brasileirão Série A',
    'Brasileirão Série B',
    'Brasileirão Série C',
    'Brasileirão Série D',
    'Paulista A1-2025',
    'Paulista A2-2025',
    'Paulista A4-2025',
    'Libertadores',
    'Copa do Brasil',
    'Sul-Americana',
    'Copa Paulista'
]

URLS = {
    'Brasileirão Série A': 'https://www.futebolinterior.com.br/campeonato/brasileirao-serie-a-2025/',
    'Brasileirão Série B': 'https://www.futebolinterior.com.br/campeonato/brasileirao-serie-b-2025/',
    'Brasileirão Série C': 'https://www.futebolinterior.com.br/campeonato/brasileirao-serie-c-2025/',
    'Brasileirão Série D': 'https://www.futebolinterior.com.br/campeonato/brasileirao-serie-d-2025/',
    'Paulista A1-2025': 'https://www.futebolinterior.com.br/campeonato/paulistao-a1-2025/',
    'Paulista A2-2025': 'https://www.futebolinterior.com.br/campeonato/paulistao-a2-2025/',
    'Paulista A4-2025': 'https://www.futebolinterior.com.br/campeonato/paulistao-a4-2025/',
    'Libertadores': 'https://www.futebolinterior.com.br/campeonato/libertadores-unica-2025/',
    'Copa do Brasil': 'https://www.futebolinterior.com.br/campeonato/copa-do-brasil-unica-2025/',
    'Sul-Americana': 'https://www.futebolinterior.com.br/campeonato/copa-sul-americana-unica-2025/',
    'Copa Paulista': 'https://www.futebolinterior.com.br/campeonato/copa-paulista-unica-2025/'
}

def parse_rodadas(html: str) -> pd.DataFrame:
    soup = BeautifulSoup(html, "html.parser")
    matches = soup.select("article.card-match")
    data = []

    for match in matches:
        date = match.select_one("div.card-match__header time").get_text(strip=True)
        status = match.select_one("span.card-match__bagde").get_text(strip=True)
        teams = match.select("figcaption.card-match__short-name")
        home_team = teams[0].get_text(strip=True)
        away_team = teams[1].get_text(strip=True)
        shields = match.select('img.card-match__score-team-img')
        home_shield = shields[0].attrs['src']
        away_shield = shields[1].attrs['src']
        scores = match.select("figure.card-match__score-result span.card-match__score-number")
        home_goals = scores[0].get_text(strip=True)
        away_goals = scores[1].get_text(strip=True)

        data.append([
            date, status, home_team, home_goals, home_shield,
            away_goals, away_team, away_shield
        ])

    columns = [
        "Data", "Status", "Mandante", "Gols_Mandante", "Brasao_Mandante",
        "Gols_Visitante", "Visitante", "Brasao_Visitante"
    ]
    return pd.DataFrame(data, columns=columns)

session = requests.Session()

for league in leagues:
    logging.info(f"Iniciando coleta da liga: {league}")
    partidas_full = []
    _url = URLS[league]

    try:
        response = session.get(_url)
        response.encoding = 'utf-8'
        sel = Selector(response.text)
    except Exception as e:
        logging.error(f"Erro ao acessar {league}: {e}")
        continue

    matches_id = sel.xpath(
        './/section[@id="tabela"]/form/select[@class="select-tournament"]/optgroup/option/@value'
    ).getall()
    logging.debug(f"Rodadas encontradas em {league}: {matches_id}")

    for match_id in tqdm(matches_id, desc=f'Rodadas em {league}', unit='rodada'):
        try:
            response = session.get(_url + '/?rodada=' + match_id)
            response.encoding = 'utf-8'
            match_sel = Selector(response.text)
        except Exception as e:
            logging.error(f"Erro ao buscar rodada {match_id} de {league}: {e}")
            continue

        rounds_title = match_sel.xpath(
            './/section[@id="tabela"]/form/select[@class="select-tournament"]/optgroup/option[@selected="selected"]/text()'
        ).get()

        rounds_title = (
            rounds_title.lower().replace('rodada', '').replace('º', '').replace('ª', '').strip()
            if rounds_title else '1'
        )

        rounds = match_sel.xpath('.//article[contains(@class, "card-match")]').getall()
        logging.debug(f"{len(rounds)} partidas na rodada {rounds_title} ({league})")

        for round_ in tqdm(rounds, desc=f"Partidas rodada {rounds_title}", unit="partida", leave=False):
            rodadas: pd.DataFrame = parse_rodadas(round_)
            for _, item in rodadas.iterrows():
                data = {
                    'data': ' - '.join([i.strip() for i in item['Data'].split('-')]),
                    'finalizada': 1 if item['Status'].lower() == 'finalizado' else 0,
                    'tcasa': item['Mandante'],
                    'gcasa': item['Gols_Mandante'],
                    'tfora': item['Visitante'],
                    'gfora': item['Gols_Visitante'],
                    'league': league,
                    'rodada': rounds_title,
                }
                partidas_full.append(data)

    logging.info(f"Total de partidas coletadas para {league}: {len(partidas_full)}")

    try:
        resp = session.post(
            'http://esportevale.com.br/bot/save',
            data={"data": json.dumps(partidas_full, ensure_ascii=False)}  # compatível com $_POST['data']
        )
        logging.info(f"Envio concluído para {league} - HTTP {resp.status_code}")
        logging.debug(f"Resposta: {resp.text}")
    except Exception as e:
        logging.error(f"Erro ao enviar partidas de {league}: {e}")

logging.info("Coleta finalizada para todas as ligas.")

session.close()