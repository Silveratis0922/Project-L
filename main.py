import json
import os
from datetime import date

import boto3
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("PANDASCORE_TOKEN")
BASE_URL = "https://api.pandascore.co"
LEAGUE_ID = 4197  # LEC

MINIO_ENDPOINT= os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
MINIO_ACCESS_KEY= os.getenv("MINIO_ROOT_USER")
MINIO_SECRET_KEY= os.getenv("MINIO_ROOT_PASSWORD")


headers = {"Authorization": f"Bearer {TOKEN}"}
s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY
)


def get_current_serie_id() -> int:
    """Récupère la série la plus récente de la LEC (triée par begin_at décroissant)."""
    response = requests.get(
        f"{BASE_URL}/lol/series",
        headers=headers,
        params={
            "filter[league_id]": LEAGUE_ID,
            "sort": "-begin_at",
            "page[size]": 1,
        },
    )
    response.raise_for_status()
    series = response.json()

    if not series:
        raise RuntimeError("Aucune série trouvée pour cette ligue")

    serie = series[0]
    print(f"Série trouvée : {serie['full_name']} (id={serie['id']}, begin_at={serie['begin_at']})")
    return serie["id"]


def get_matches(serie_id: int) -> list[dict]:
    """Récupère les matchs d'une série, quel que soit leur status (past, running, upcoming)."""
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


def flatten_match(match: dict) -> dict:
    """Réduit un match brut (imbriqué) à une ligne plate exploitable en DataFrame."""
    opponents = match.get("opponents") or []
    team_names = [o["opponent"]["name"] for o in opponents if o.get("opponent")]
    team1 = team_names[0] if len(team_names) > 0 else None
    team2 = team_names[1] if len(team_names) > 1 else None

    scores_by_team_id = {r["team_id"]: r["score"] for r in (match.get("results") or [])}
    team_ids = [o["opponent"]["id"] for o in opponents if o.get("opponent")]
    score1 = scores_by_team_id.get(team_ids[0]) if len(team_ids) > 0 else None
    score2 = scores_by_team_id.get(team_ids[1]) if len(team_ids) > 1 else None

    return {
        "match_id": match["id"],
        "serie_id": match["serie_id"],
        "tournament_id": match["tournament_id"],
        "name": match["name"],
        "status": match["status"],
        "begin_at": match["begin_at"],
        "team1": team1,
        "team2": team2,
        "score1": score1,
        "score2": score2,
        "winner_id": match.get("winner_id"),
    }


def main() -> None:
    if not TOKEN:
        raise ValueError("PANDASCORE_TOKEN manquant dans le .env")
        
    serie_id = get_current_serie_id()

    all_matches = get_matches(serie_id)
    print(f"{len(all_matches)} matchs au total.")

    s3_key = f"lec/summer2026/matches_serie{serie_id}_{date.today().isoformat()}.json"
    s3_client.put_object(
        Bucket="bronze",
        Key=s3_key,
        Body=json.dumps(all_matches, ensure_ascii=False, indent=2),
    )
    print(f"Uplode dans MinIO : bronze/{s3_key}")

    df = pd.DataFrame([flatten_match(m) for m in all_matches])
    df = df.sort_values("begin_at").reset_index(drop=True)
    print()
    print(df[["name", "status", "begin_at", "team1", "team2", "score1", "score2"]].to_string())


if __name__ == "__main__":
    main()
