SELECT DISTINCT
    tournament_id,
    tournament_name,
    serie_id
FROM {{ ref('stg_matches') }}