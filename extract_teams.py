import json
from datetime import date

from api_call import TOKEN, get_current_serie_id, get_teams
from main import s3_client


def main() -> None:
    if not TOKEN:
        raise ValueError("PANDASCORE_TOKEN manquant dans le .env")

    serie_id = get_current_serie_id()
    teams = get_teams(serie_id)
    print(f"{len(teams)} equipe recues pour la serie {serie_id}.")

    s3_key = f"lec/summer2026/teams_serie{serie_id}_{date.today().isoformat()}.json"
    s3_client.put_object(
        Bucket="bronze",
        Key=s3_key,
        Body=json.dumps(teams, ensure_ascii=False, indent=2),
    )
    print(f"Upload dans Minio: bronze/{s3_key}")
    print(f"{json.dumps(teams)}")


if __name__ == "__main__":
    main()