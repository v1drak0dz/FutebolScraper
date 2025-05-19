from Raw import main
from Brasoes import extract_brasao
from Matches import parse_rodadas

import os

data = main()
for item in data[0]:
    if not os.path.exists(f'src'):
        os.mkdir(f'src')
    try:
        extract_brasao(item['table'], 'src')
        df = parse_rodadas(item['table'], 'src')
        print(df.to_json(orient='records'))
    except:
        print(item['name'])
