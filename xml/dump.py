import requests as req
from fake_useragent import FakeUserAgent

with open("teste.html", "w") as f:
    f.write(req.get("https://www.futebolinterior.com.br/campeonato/libertadores-unica-2025/", headers={"User-Agent": FakeUserAgent().chrome}).text)
