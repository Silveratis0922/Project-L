# Architecture

Ce document retrace comment la stack de ce projet est arrivée à sa forme
actuelle : ce qui était prévu au départ, les problèmes rencontrés en
route, et la stack finale qui en résulte.

## Stack initiale envisagée

Python, Pandas, Airflow, **Databricks** (Delta Lake), dbt, Streamlit,
Grafana, **Terraform**, **Azure DevOps**, Docker, Git, API PandaScore.

L'idée de départ : un pipeline cloud-native classique — Databricks pour le
stockage/traitement analytique, Airflow pour l'orchestrer, Terraform pour
provisionner l'infrastructure, Azure DevOps pour le CI/CD.

## Problèmes rencontrés et changements de cap

1. **Databricks** — le plan gratuit ne donne pas accès à l'API Databricks.
   Sans API, ni Airflow (orchestration) ni Terraform (provisioning) ne
   peuvent s'y connecter. Databricks abandonné.

2. **Terraform** — sans Databricks, plus d'infrastructure cloud à
   provisionner. Terraform devient inutile.

3. **Azure DevOps** — prévu pour orchestrer un déploiement cloud qui
   n'existe plus. Remplacé par **GitHub Actions**, suffisant pour du CI/CD
   sur un projet 100% local.

4. **Stockage analytique** — il fallait un remplaçant à Databricks pour la
   partie stockage/traitement. Premier réflexe : **PostgreSQL**, une base
   déjà connue. Mais PostgreSQL est une base **transactionnelle** (OLTP,
   orientée ligne), pas conçue pour de l'agrégation analytique sur
   beaucoup de colonnes — mauvais outil pour ce besoin.

5. Recherche du côté des vraies bases **OLAP** : BigQuery et Snowflake
   évalués — mais toutes les deux cloud et payantes au-delà d'un petit
   quota gratuit, incompatibles avec la contrainte "100% gratuit".

6. **DuckDB** retenu à la place de PostgreSQL : moteur OLAP embarqué,
   gratuit, 100% local (un simple fichier, pas de serveur), avec un
   adapter dbt officiel.

7. **Stockage brut (Bronze)** — MinIO plutôt qu'un simple dossier local :
   compatible avec l'API S3 (le même SDK `boto3` fonctionnerait avec un
   vrai cloud plus tard), et accessible par tous les conteneurs (Airflow,
   dbt, Streamlit) via une seule adresse réseau, sans partager de volumes
   Docker entre eux.

8. **Extraction des équipes** — plutôt que de reconstruire la liste des
   équipes depuis les matchs déjà récupérés, utilisation de l'endpoint
   dédié `/lol/series/{id}/teams`, qui donne en bonus le roster complet
   des joueurs sans appel supplémentaire.

9. **Modélisation des données** — première version avec une seule table
    (les infos d'équipe répétées à chaque match). Refactorisée en schéma
    en étoile (`dim_teams`, `dim_players`, `dim_tournaments`,
    `fct_matches`) : chaque info stockée une seule fois, tests
    d'intégrité entre les tables possibles.

10. **Deux DAGs séparés** — les matchs changent chaque jour (extraction
    quotidienne), mais les équipes changent rarement en cours de saison
    (extraction hebdomadaire, décalée dans le temps pour éviter que les
    deux DAGs écrivent dans DuckDB en même temps — DuckDB n'accepte qu'un
    seul écrivain à la fois).

11. **Tests dbt en CI** — utilisation d'une petite fixture JSON versionnée
    dans le repo plutôt que MinIO/l'API réels : CI rapide, reproductible,
    sans dépendance à un service externe ni à un vrai token.

## Stack finale

| Étape | Outil |
|---|---|
| Extraction | Python, Pandas |
| Data Lake (Bronze) | MinIO (S3-compatible) |
| Entrepôt (Silver/Gold) | DuckDB — schéma en étoile |
| Transformation | dbt |
| Orchestration | Apache Airflow (LocalExecutor, 2 DAGs) |
| Visualisation | Streamlit |
| Monitoring | Grafana |
| CI/CD | GitHub Actions |
| Infrastructure | Docker, Docker Compose |

100% local et gratuit — aucun service cloud payant.
