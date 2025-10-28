import os
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import List, Dict, Optional
import re

import requests
from parsel import Selector
from tqdm import tqdm
from pandas import DataFrame

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

        data.append([date, status, home_team, home_goals, home_shield, away_goals, away_team, away_shield])
        # print('Dados partida: ', data)

    columns = ["Data", "Status", "Mandante", "Gols_Mandante", "Brasao_Mandante", "Gols_Visitante", "Visitante", "Brasao_Visitante"]
    return pd.DataFrame(data, columns=columns)

# --- CONFIGURAÇÕES ---
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

session = requests.Session()
session.headers.update({
    "User-Agent": "esportevale-scraper/1.0 (+https://seusite.example)"
})

partidas_full: List[Dict[str, str|int]] = []
# teams[league][team_name] = {'brasao':..., 'liga':..., 'group': ...}
teams: Dict[str, Dict[str, Dict[str, str]]] = {}


def normalize_name(name: Optional[str]) -> str:
    """Pequena normalização para matching consistente (trim + espaço + case)."""
    if name is None:
        return ''
    return re.sub(r'\s+', ' ', name).strip()


def guess_group_from_page(match_sel: Selector) -> Optional[str]:
    """
    Tenta várias estratégias para extrair o nome do grupo do HTML da rodada/página.
    Retorna string ou None.
    """
    # 1) procura blocos clássicos de classificação por grupo
    xpaths = [
        # possíveis locais de título de grupo
        './/div[contains(@class,"table-classification--group")]//h3/text()',
        './/div[contains(@class,"classificacao-grupo")]//h3/text()',
        './/h3[contains(@class,"title")]/text()',
        # título da tabela (ex.: "Grupo A", "Grupo 1")
        './/section[@id="tabela"]//h2/text()',
        './/section[@id="tabela"]//h3/text()',
        # fallback: rótulo perto da tabela
        './/label[contains(@class,"group")]/text()',
        # tenta buscar algo como "Grupo A" em qualquer texto da seção
        './/section[@id="tabela"]//text()'
    ]
    for xp in xpaths:
        texts = match_sel.xpath(xp).getall()
        if not texts:
            continue
        for t in texts:
            if not t:
                continue
            t2 = t.strip()
            # procura padrões como "Grupo A", "GRUPO A", "Grupo: A", "Grupo 1"
            m = re.search(r'(?i)grupo[\s:]*([A-Z0-9\-]+)', t2)
            if m:
                return m.group(1).strip()
            # procura por "A", "B", "1", "Fase de grupos - Grupo A", etc.
            # se a string for curta e pareça um nome de grupo, retorna
            if len(t2) <= 5 and re.match(r'^[A-Za-z0-9\- ]+$', t2):
                return t2
    return None


# --- COLETA DE PARTIDAS ---
for league in leagues:
    _url = URLS[league]
    response = session.get(_url)
    response.encoding = 'utf-8'
    sel = Selector(response.text)

    print(f"\n🏆 {league}")

    # pega lista de rodadas (fallbacks incluídos)
    matches_id = sel.xpath('.//section[@id="tabela"]/form/select[@class="select-tournament"]/optgroup/option/@value').getall()
    if not matches_id:
        matches_id = sel.xpath('.//section[@id="tabela"]/form/select[@class="select-tournament"]/option/@value').getall()
    if not matches_id:
        matches_id = ['1']  # fallback caso não haja rodadas

    for match_id in tqdm(matches_id, desc=f'Rodadas em {league}', unit='rodada'):
        response = session.get(_url + '/?rodada=' + match_id)
        response.encoding = 'utf-8'
        match_sel = Selector(response.text)

        # TENTATIVA: extrair o nome do grupo diretamente da página da rodada
        page_group = guess_group_from_page(match_sel)
        if page_group:
            page_group = normalize_name(page_group)

        rounds_title = match_sel.xpath(
            './/section[@id="tabela"]/form/select[@class="select-tournament"]/optgroup/option[@selected="selected"]/text()'
        ).get()
        rounds = match_sel.xpath('.//article[contains(@class, "card-match")]').getall()

        if rounds_title:
            rounds_title = rounds_title.strip().lower().replace('rodada', '').replace('º', '').replace('ª', '').strip()
        else:
            rounds_title = '1'

        if not rounds:
            print(f"Atenção: nenhuma partida encontrada para rodada {rounds_title} em {league}")
            continue

        for round_ in tqdm(rounds, desc=f"Partidas rodada {rounds_title}", unit="partida", leave=False):
            rodadas: DataFrame = parse_rodadas(round_)
            for index, item in rodadas.iterrows():
                # normaliza nomes
                home_name = normalize_name(item.get('Mandante'))
                away_name = normalize_name(item.get('Visitante'))

                # tenta inferir group:
                # prioridade:
                # 1) page_group (se extraiu do HTML)
                # 2) se ambos times já conhecidos e têm group consistente, usa ele
                # 3) se um dos times conhecido com group, usa esse
                # 4) fallback: vazio
                inferred_group = ''
                if page_group:
                    inferred_group = page_group
                else:
                    # checa teams[league] se já tem info
                    h_meta = teams.get(league, {}).get(home_name)
                    a_meta = teams.get(league, {}).get(away_name)
                    if h_meta and a_meta and h_meta.get('group') and a_meta.get('group') and h_meta.get('group') == a_meta.get('group'):
                        inferred_group = h_meta.get('group')
                    elif h_meta and h_meta.get('group'):
                        inferred_group = h_meta.get('group')
                    elif a_meta and a_meta.get('group'):
                        inferred_group = a_meta.get('group')
                    else:
                        inferred_group = ''  # sem info

                data: Dict[str, str|int] = {
                    'date': ' - '.join([i.strip() for i in item['Data'].split('-')]),
                    'ended': 1 if str(item['Status']).lower() == 'finalizado' else 0,
                    'homeTeam': home_name,
                    'goalsHome': item['Gols_Mandante'],
                    'shieldHome': item['Brasao_Mandante'],
                    'outerTeam': away_name,
                    'goalsOuter': item['Gols_Visitante'],
                    'shieldOuter': item['Brasao_Visitante'],
                    'league': league,
                    'match': rounds_title,
                    'group': inferred_group
                }
                partidas_full.append(data)

                # Armazenar times por liga garantindo unicidade e salvando grupo
                if league not in teams:
                    teams[league] = {}

                # Mandante
                if home_name not in teams[league]:
                    teams[league][home_name] = {
                        'brasao': item.get('Brasao_Mandante') or '',
                        'liga': league,
                        'group': inferred_group
                    }
                else:
                    # atualiza brasao se vazio e info nova disponível
                    if not teams[league][home_name].get('brasao') and item.get('Brasao_Mandante'):
                        teams[league][home_name]['brasao'] = item.get('Brasao_Mandante')
                    # preenche group se estiver vazio
                    if not teams[league][home_name].get('group') and inferred_group:
                        teams[league][home_name]['group'] = inferred_group

                # Visitante
                if away_name not in teams[league]:
                    teams[league][away_name] = {
                        'brasao': item.get('Brasao_Visitante') or '',
                        'liga': league,
                        'group': inferred_group
                    }
                else:
                    if not teams[league][away_name].get('brasao') and item.get('Brasao_Visitante'):
                        teams[league][away_name]['brasao'] = item.get('Brasao_Visitante')
                    if not teams[league][away_name].get('group') and inferred_group:
                        teams[league][away_name]['group'] = inferred_group


# --- FUNÇÕES DE XML ---
def prettify_xml(elem: ET.Element) -> str:
    """Retorna XML bonito (com declaração) a partir de um ElementTree.Element"""
    rough = ET.tostring(elem, encoding='utf-8')
    reparsed = minidom.parseString(rough)
    return reparsed.toprettyxml(indent='  ', encoding='utf-8').decode('utf-8')


# --- CRIAÇÃO DO XML DAS PARTIDAS ---
root_partidas = ET.Element('Partidas')
for partida in partidas_full:
    p_elem = ET.SubElement(root_partidas, 'Partida')
    for k, v in partida.items():
        child = ET.SubElement(p_elem, k)
        child.text = str(v)

# --- CRIAÇÃO DO XML DOS TIMES (por liga) ---
root_teams = ET.Element('Teams')
for league, league_teams in teams.items():
    league_elem = ET.SubElement(root_teams, 'League', name=league)
    for team_name, meta in league_teams.items():
        t_elem = ET.SubElement(league_elem, 'Team')
        name_elem = ET.SubElement(t_elem, 'Name')
        name_elem.text = team_name
        # escreve brasao e group (se houver)
        brasao_elem = ET.SubElement(t_elem, 'brasao')
        brasao_elem.text = meta.get('brasao', '')
        if meta.get('group'):
            group_elem = ET.SubElement(t_elem, 'group')
            group_elem.text = meta.get('group')

# --- CRIAÇÃO DE DIRETÓRIOS DE SAÍDA ---
os.makedirs('xml', exist_ok=True)
os.makedirs('json', exist_ok=True)

# --- SALVA XML ---
with open(os.path.join('xml', 'all_backup.xml'), 'w', encoding='utf-8') as f:
    f.write(prettify_xml(root_partidas))

with open(os.path.join('xml', 'teams.xml'), 'w', encoding='utf-8') as f:
    f.write(prettify_xml(root_teams))

# --- SALVA JSON ---
with open(os.path.join('json', 'all_backup.json'), 'w', encoding='utf-8') as file:
    json.dump(partidas_full, file, ensure_ascii=False, indent=2)

print('\nArquivos gerados:')
print(' - xml/all_backup.xml')
print(' - xml/teams.xml')
print(' - json/all_backup.json')
