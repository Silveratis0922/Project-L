# LEC Stats Pipeline

![Status](https://img.shields.io/badge/Statut-Termin%C3%A9-brightgreen)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Airflow](https://img.shields.io/badge/Apache%20Airflow-3.3-orange)
![dbt](https://img.shields.io/badge/dbt-1.12-red)
![Streamlit](https://img.shields.io/badge/Streamlit-1.62-FF4B4B)
![Docker](https://img.shields.io/badge/Docker%20Compose-2496ED)

## Description

Pipeline de données de bout en bout collectant les résultats de la LEC
(League of Legends European Championship) via l'API PandaScore, modélisés
en schéma en étoile et exposés dans un dashboard Streamlit (calendrier,
classement).

Projet portfolio réalisé dans le cadre d'une recherche d'alternance Data
Engineer.

## Aperçu

**Dashboard — Calendrier**
![Calendrier](screenshots/calendrier.png)

**Dashboard — Classement**
![Classement](screenshots/classement.png)

**Monitoring Grafana**
![Grafana](screenshots/grafana.png)

**Modélisation (schéma en étoile)**
![Schéma en étoile](screenshots/dbdiagram.png)

## Architecture

```mermaid
flowchart LR
    API[API PandaScore]
    EXT[Extraction<br/>Python]
    BRONZE[(MinIO<br/>Bronze — JSON brut)]
    SILVER[(DuckDB<br/>Silver — staging)]
    GOLD[(DuckDB<br/>Gold — schéma en étoile)]
    DASH[Streamlit<br/>Dashboard]
    MON[Grafana<br/>Monitoring]
    AIRFLOW{{Apache Airflow<br/>2 DAGs}}
    CI[[GitHub Actions<br/>CI/CD]]

    API --> EXT --> BRONZE --> SILVER --> GOLD --> DASH
    AIRFLOW -.orchestre.-> EXT
    AIRFLOW -.orchestre.-> SILVER
    AIRFLOW -.orchestre.-> GOLD
    AIRFLOW -.suivi des runs.-> MON
    CI -.valide.-> SILVER
    CI -.valide.-> GOLD
```

## Stack technique

| Couche | Technologie |
|---|---|
| Extraction | Python, Pandas |
| Data Lake (Bronze) | MinIO (S3-compatible) |
| Entrepôt (Silver/Gold) | DuckDB — schéma en étoile |
| Transformation | dbt |
| Orchestration | Apache Airflow |
| Visualisation | Streamlit |
| Monitoring | Grafana |
| Infrastructure | Docker, Docker Compose |

Choix techniques détaillés: [ARCHITECTURE.md](ARCHITECTURE.md)

## Lancer le projet

Nécessite un fichier `.env` (token PandaScore + identifiants MinIO/Airflow/Grafana).

```
docker compose up -d
streamlit run app.py (Dans un second terminal, ouve)
```

Accès :
- Dashboard : http://localhost:8501
- Airflow : http://localhost:8080
- Grafana : http://localhost:3000
- Console MinIO : http://localhost:9001
