# LEC Stats Pipeline

Pipeline de données de bout en bout collectant les résultats de la LEC
(League of Legends European Championship) via l'API PandaScore, pour
alimenter un dashboard Streamlit (calendrier, classement Regular Season /
Playoffs).

Projet portfolio réalisé dans le cadre d'une recherche d'alternance Data
Engineer.

## Scope

- Ligue : LEC uniquement (`league_id=4197`)
- Série suivie : la série en cours, récupérée dynamiquement (actuellement
  Summer 2026)
- Pas de stats joueurs/équipes/pick-ban détaillées pour l'instant — nécessite
  le plan payant PandaScore "Historical", accès demandé mais pas encore
  obtenu

## Stack

| Étape | Outil |
|---|---|
| Extraction | Python + Pandas |
| Stockage Bronze (JSON brut) | MinIO |
| Stockage Silver/Gold (OLAP) | DuckDB |
| Transformation | dbt-core (adapter `dbt-duckdb`) |
| Orchestration | Apache Airflow |
| Dashboard | Streamlit |
| Conteneurisation | Docker / Docker Compose |
| CI/CD | GitHub Actions |
| Monitoring (bonus) | Grafana |

100% local et gratuit — pas de service cloud payant.

Détail des choix techniques et de leurs justifications : voir
[ARCHITECTURE.md](ARCHITECTURE.md).

## Statut

🚧 En cours de développement.

- [x] Extraction API — premiers appels PandaScore validés
- [ ] Stockage Bronze (MinIO)
- [ ] Modélisation Silver/Gold (DuckDB + dbt)
- [ ] Dashboard Streamlit
- [ ] Orchestration Airflow
- [ ] CI/CD GitHub Actions
- [ ] Monitoring Grafana

## Setup

Nécessite un token API PandaScore (gratuit) dans un fichier `.env` :

```
PANDASCORE_TOKEN=xxxxx
```
