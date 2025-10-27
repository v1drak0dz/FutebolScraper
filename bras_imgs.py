import base64
import pathlib
import os
import json
import re

def sanitize_filename(name):
    return re.sub(r'[^\w\-_. ]', '_', name).strip().replace(' ', '_') + '.webp'

path = pathlib.Path('./public/shields')
path.mkdir(exist_ok=True, parents=True)

for file in os.listdir('.'):
    if file.endswith('.json') and file != 'backup.json':
        print(file)
        try:
            with open(file, encoding='utf-8') as f:
                data = json.load(f)

            for row in data:
                try:
                    home_filename = sanitize_filename(row['homeTeam'])
                    outer_filename = sanitize_filename(row['outerTeam'])

                    home_path = path / home_filename
                    outer_path = path / outer_filename

                    if not home_path.exists():
                        with open(home_path, 'wb') as f:
                            f.write(base64.b64decode(row['shieldHome'].encode('utf-8')))

                    if not outer_path.exists():
                        with open(outer_path, 'wb') as f:
                            f.write(base64.b64decode(row['shieldOuter'].encode('utf-8')))

                except Exception as e:
                    print(f"Erro ao salvar imagem de {row.get('homeTeam')} ou {row.get('outerTeam')}: {e}")

        except Exception as e:
            print(f"Erro ao processar arquivo {file}: {e}")
