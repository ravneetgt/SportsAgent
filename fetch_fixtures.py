import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FOOTBALL_API_KEY")

BASE_URL = "https://api.football-data.org/v4/matches"


TOP_COMPETITIONS = [
    "Premier League",
    "La Liga",
    "Serie A",
    "Bundesliga",
    "UEFA Champions League",
    "UEFA Europa League"
]


def fetch_fixtures(days_ahead=3, days_back=2):

    headers = {
        "X-Auth-Token": API_KEY
    }

    today = datetime.utcnow().date()
    start = today - timedelta(days=days_back)
    end = today + timedelta(days=days_ahead)

    params = {
        "dateFrom": start.isoformat(),
        "dateTo": end.isoformat()
    }

    try:

        res = requests.get(BASE_URL, headers=headers, params=params)

        data = res.json()

        matches = data.get("matches", [])

        articles = []

        for m in matches:

            competition = m["competition"]["name"]

            if competition not in TOP_COMPETITIONS:
                continue

            home = m["homeTeam"]["name"]
            away = m["awayTeam"]["name"]

            status = m["status"]

            # --------------------------------------------------
            # UPCOMING MATCH (PREVIEW)
            # --------------------------------------------------

            if status == "SCHEDULED":

                kickoff = m["utcDate"]

                try:
                    dt = datetime.fromisoformat(kickoff.replace("Z", "+00:00"))
                    date_str = dt.strftime("%A")
                except:
                    date_str = "Upcoming"

                title = f"{home} vs {away} — {competition}"

                summary = (
                    f"{home} face {away} in {competition}. "
                    f"Match scheduled {date_str}. "
                    f"This could shape momentum and table position."
                )

                articles.append({
                    "category": "football",
                    "title": title,
                    "summary": summary,
                    "context": "preview",
                    "teams": [home, away],
                    "league": competition,
                    "query": f"{home} vs {away} football players match action stadium crowd"
                })


            # --------------------------------------------------
            # FINISHED MATCH (RESULT)
            # --------------------------------------------------

            elif status == "FINISHED":

                score = m["score"]["fullTime"]

                home_goals = score["home"]
                away_goals = score["away"]

                title = f"{home} {home_goals}–{away_goals} {away} — {competition}"

                summary = (
                    f"{home} defeated {away} {home_goals}-{away_goals} in {competition}. "
                    f"The result could influence momentum and league standings."
                )

                articles.append({
                    "category": "football",
                    "title": title,
                    "summary": summary,
                    "context": "result",
                    "teams": [home, away],
                    "league": competition,
                    "query": f"{home} vs {away} football players match goal celebration stadium"
                })

        print("FIXTURES:", len(articles))

        return articles[:20]

    except Exception as e:

        print("Fixture error:", e)

        return []