import requests
from parsel import Selector

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
    'Sul-Americana'
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
    'Sul-Americana': 'https://www.futebolinterior.com.br/campeonato/copa-sul-americana-unica-2025/'
}


def main():
    tables = []
    matches = []
    for league in leagues:
            # 'https://www.futebolinterior.com.br/campeonato/brasileirao-serie-a-2025/'
        url = URLS[league]
        response = requests.get(url)
        response.encoding = 'utf-8'
        sel = Selector(response.text)
        table = sel.css('section#classificacao-geral').css('table.table-classification--expansive').get()
        rounds_title = sel.css("div.rounds").css('h3.rounds__title::text').get().strip()
        rounds = sel.xpath('.//article[contains(@class, "card-match")]').getall()

        tables.append({ 'name': league, 'table': table})
        matches.append({ league: { 'title': rounds_title, 'rounds': rounds} })
    return tables,matches

