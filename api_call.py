import os

import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("PANDASCORE_TOKEN")
BASE_URL = "https://api.pandascore.co"
LEAGUE_ID = 4197 # LEC

headers = {"Authorization": f"Bearer {TOKEN}"}

def get_current_serie_id() -> int:
    """Recupere la serie la plus recente (ou en cours) de la LEC."""
    response = requests.get(
        f"{BASE_URL}/lol/series",
        headers=headers,
        params={
            "filter[league_id]": LEAGUE_ID,
            "sort": "-begin_at",
            "page[size]": 1,
        }
    )
    response.raise_for_status()
    series = response.json()

    if not series:
        raise RuntimeError("Aucune serie trouvee pour cette ligue")

    serie = series[0]
    print(f"Serie trouvee: {serie['full_name']} (id={serie['id']}, begin_at={serie['begin_at']})")
    return serie["id"]


def get_matches(serie_id: int) -> list[dict]:
    """Recupere tous les matchs d'une serie, quel que soit leur status."""
    response = requests.get(
        f"{BASE_URL}/lol/matches",
        headers=headers,
        params={
            "filter[serie_id]": serie_id,
            "page[size]": 100,
        },
    )
    response.raise_for_status()
    return response.json()


def get_teams(serie_id: int) -> list[dict]:
    """Recupere les equipes participant a une serie."""
    response = requests.get(
        f"{BASE_URL}/lol/series/{serie_id}/teams",
        headers=headers,
    )
    response.raise_for_status()
    return response.json()