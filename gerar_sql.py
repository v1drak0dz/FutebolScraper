import json
import os

# LEAGUES = os.listdir('json')
LEAGUE = 'Brasileirão Série B'

# for LEAGUE in LEAGUES:
with open(f'json/all_backup.json') as f:
    partidas = json.load(f)

with open(f'sql/all.sql', 'a', encoding='utf-8') as f:
    for partida in partidas:
        # if partida['ended'] == 0: continue
        gols_casa = partida.get("goalsHome")
        gols_fora = partida.get("goalsOuter")

        gols_casa = int(gols_casa) if str(gols_casa).isdigit() else 0
        gols_fora = int(gols_fora) if str(gols_fora).isdigit() else 0
        f.write(f"""
-- Inserir partida (só se ainda não existir por causa do UNIQUE KEY)
INSERT IGNORE INTO partidas (
  campeonato, grupo, rodada, data_partida,
  time_casa, time_fora, gols_casa, gols_fora, finalizada
) VALUES (
  '{partida.get('league', '')}', '{partida.get('group', '')}', {partida.get('match', 1)}, '{partida.get('date', '')}',
  '{partida.get('homeTeam', '')}', '{partida.get('outerTeam', '')}', {gols_casa}, {gols_fora}, {partida.get('ended', 0)}
);

-- Inserir time da casa (só se ainda não existir no campeonato)
INSERT IGNORE INTO times_campeonato (
  time_nome, campeonato, grupo, brasao_url
) VALUES (
  '{partida.get('homeTeam', '')}', '{partida.get('league', '')}', '{partida.get('group', '')}', '{partida.get('shieldHome', '')}'
);

-- Inserir time de fora (só se ainda não existir no campeonato)
INSERT IGNORE INTO times_campeonato (
  time_nome, campeonato, grupo, brasao_url
) VALUES (
  '{partida.get('outerTeam', '')}', '{partida.get('league', '')}', '{partida.get('group', '')}', '{partida.get('shieldOuter', '')}'
);

    """)
