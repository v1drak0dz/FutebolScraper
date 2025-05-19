from bs4 import BeautifulSoup
import pandas as pd

def parse_rodadas(html: str) -> pd.DataFrame:
    soup = BeautifulSoup(html, "html.parser")
    matches = soup.select("article.card-match")

    data = []
    for match in matches:
        try:
            date = match.select_one("div.card-match__header time").get_text(strip=True)
            status = match.select_one("span.card-match__bagde").get_text(strip=True)

            teams = match.select("figcaption.card-match__short-name")
            home_team = teams[0].get_text(strip=True)
            away_team = teams[1].get_text(strip=True)

            scores = match.select("figure.card-match__score-result span.card-match__score-number")
            home_goals = scores[0].get_text(strip=True)
            away_goals = scores[1].get_text(strip=True)

            data.append([date, status, home_team, home_goals, away_goals, away_team])
        except Exception as e:
            print("Erro ao processar uma partida:", e)

    columns = ["Data", "Status", "Mandante", "Gols_Mandante", "Gols_Visitante", "Visitante"]
    return pd.DataFrame(data, columns=columns)
