SELECT
    team_id,
    team_name,
    team_acronym,
    team_logo,
    team_dark_logo,
    location,
FROM {{ ref('stg_teams') }}