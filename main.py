import os
import json
import xml.etree.ElementTree as ET
from tqdm import tqdm
from parsel import Selector

from fetcher import PageFetcher
from extract_matches import parse_rodadas
from extract_teams import add_team
from utils import normalize_name, prettify_xml

# --- CONFIGURAÇÕES ---
LEAGUES = {
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
}

# --- OBJETOS PRINCIPAIS ---
fetcher = PageFetcher()
teams = {}
partidas_full = []

# --- PROCESSO PRINCIPAL ---
for league, url in LEAGUES.items():
    print(f"\n🏆 {league}")
    sel = fetcher.get_selector(url)

    matches_id = sel.xpath('.//section[@id="tabela"]/form/select/option/@value').getall() or ['1']

    for match_id in tqdm(matches_id, desc=f"Rodadas {league}", unit='rodada'):
        rodada_url = f"{url}?rodada={match_id}"
        rodada_html = fetcher.get_html(rodada_url)
        df = parse_rodadas(rodada_html)

        for _, item in df.iterrows():
            home_name = normalize_name(item['Mandante'])
            away_name = normalize_name(item['Visitante'])

            partida = {
                'date': item['Data'],
                'status': item['Status'],
                'homeTeam': home_name,
                'goalsHome': item['Gols_Mandante'],
                'shieldHome': item['Brasao_Mandante'],
                'outerTeam': away_name,
                'goalsOuter': item['Gols_Visitante'],
                'shieldOuter': item['Brasao_Visitante'],
                'league': league
            }
            partidas_full.append(partida)

            # adiciona times
            add_team(teams, league, home_name, item['Brasao_Mandante'], '')
            add_team(teams, league, away_name, item['Brasao_Visitante'], '')

# --- CRIAÇÃO DE XML ---
root_partidas = ET.Element('Partidas')
for partida in partidas_full:
    p_elem = ET.SubElement(root_partidas, 'Partida')
    for k, v in partida.items():
        child = ET.SubElement(p_elem, k)
        child.text = str(v)

root_teams = ET.Element('Teams')
for league, league_teams in teams.items():
    league_elem = ET.SubElement(root_teams, 'League', name=league)
    for team_name, meta in league_teams.items():
        t_elem = ET.SubElement(league_elem, 'Team')
        ET.SubElement(t_elem, 'Name').text = team_name
        ET.SubElement(t_elem, 'brasao').text = meta.get('brasao', '')

# --- SALVA ARQUIVOS ---
os.makedirs('xml', exist_ok=True)
os.makedirs('json', exist_ok=True)

with open('xml/all_backup.xml', 'w', encoding='utf-8') as f:
    f.write(prettify_xml(root_partidas))
with open('xml/teams.xml', 'w', encoding='utf-8') as f:
    f.write(prettify_xml(root_teams))
with open('json/all_backup.json', 'w', encoding='utf-8') as f:
    json.dump(partidas_full, f, ensure_ascii=False, indent=2)

print("\n✅ Arquivos gerados:")
print(" - xml/all_backup.xml")
print(" - xml/teams.xml")
print(" - json/all_backup.json")
