import json
import os
import requests
import re
import tqdm

def sanitize_filename(name):
    return re.sub(r'[^\w\-_. ]', '_', name).strip().replace(' ', '_') + '.webp'

url = 'http://localhost:8000/bot/matches'  # ou seu endpoint real

for file in os.listdir('.'):
    if file.endswith('.json') and 'backup.json' != file:
        with open(file, encoding='utf-8') as f:
            data = json.load(f)

        for row in tqdm.tqdm(data, desc=f'Inserindo Partidas do Campeonato: {file.replace('_backup.json', '')}', unit='Partidas'):
            home_filename = sanitize_filename(row['homeTeam'])
            outer_filename = sanitize_filename(row['outerTeam'])

            row['shieldHome'] = f'/public/shields/{home_filename}'
            row['shieldOuter'] = f'/public/shields/{outer_filename}'

            try:
                response = requests.post(url, headers={'Content-Type': 'application/json'}, json=row)
                # print(f'{response.status_code} {row["homeTeam"]} x {row["outerTeam"]}')
            except Exception as e:
                print(f'Erro ao enviar partida: {e}')
