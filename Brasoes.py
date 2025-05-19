from bs4 import BeautifulSoup
import requests
from PIL import Image
from io import BytesIO
import os
import re

def sanitize_filename(name):
    """Remove caracteres inválidos para nomes de arquivos"""
    return re.sub(r'[\\/:"*?<>|]+', "", name).strip()

def extract_brasao(table, path):
    soup = BeautifulSoup(table, "html.parser")
    rows = soup.select("tbody.table-classification--expansive__body tr")
    brasoes = []

    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 2:
            continue
        try:
            nome = cells[1].find("span").get_text(strip=True)
            img_tag = cells[1].find("img")
            img_url = img_tag["src"] if img_tag and img_tag.has_attr("src") else None
            brasoes.append((nome, img_url))
        except Exception as e:
            print(f"Erro ao processar linha: {e}")

    # Cria diretório de brasões se não existir
    brasoes_dir = os.path.join(path, "brasoes")
    os.makedirs(brasoes_dir, exist_ok=True)

    for nome, img_url in brasoes:
        if img_url:
            try:
                response = requests.get(img_url)
                response.raise_for_status()
                print(f"Baixando imagem do brasão para o time {nome}...")

                img = Image.open(BytesIO(response.content)).convert("RGBA")
                nome_sanitizado = sanitize_filename(nome)
                img_path = os.path.join(brasoes_dir, f"{nome_sanitizado}.webp")
                img.save(img_path, format="WEBP")

                print(f"Imagem salva em: {img_path}")
            except Exception as e:
                print(f"Erro ao baixar/salvar imagem para {nome}: {e}")
        else:
            print(f"Imagem do brasão para o time {nome} não encontrada.")
