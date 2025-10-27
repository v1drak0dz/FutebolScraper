from bs4 import BeautifulSoup
import pandas as pd

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
