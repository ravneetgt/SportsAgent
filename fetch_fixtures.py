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


def fetch_fixtures(days_ahead=3):

    headers = {
        "X-Auth-Token": API_KEY
    }

    today = datetime.utcnow().date()
    future = today + timedelta(days=days_ahead)

    params = {
        "dateFrom": today.isoformat(),
        "dateTo": future.isoformat(),
        "status": "SCHEDULED"
    }

    try:
        res = requests.get(BASE_URL, headers=headers, params=params)
        data = res.json()

        matches = data.get("matches", [])

        articles = []

        for m in matches:

            competition = m["competition"]["name"]

            # filter
            if competition not in TOP_COMPETITIONS:
                continue

            home = m["homeTeam"]["name"]
            away = m["awayTeam"]["name"]

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
                "query": f"{home} vs {away} football players match action stadium crowd"
            })

        print("FIXTURES:", len(articles))

        return articles[:10]

    except Exception as e:
        print("Fixture error:", e)
        return []