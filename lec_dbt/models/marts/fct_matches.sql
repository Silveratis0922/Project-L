SELECT
    match_id,
    serie_id,
    tournament_id,
    match_name,
    status,
    begin_at,
    end_at,
    team1_id,
    team2_id,
    team1_score,
    team2_score,
    winner_id
FROM {{ ref('stg_matches') }}