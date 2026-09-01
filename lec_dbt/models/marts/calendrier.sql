SELECT
    m.match_id,
    m.begin_at,
    m.status,
    t1.team_name as team1_name,
    t1.team_logo as team1_logo,
    t1.team_acronym as team1_acronym,
    t2.team_name as team2_name,
    t2.team_logo as team2_logo,
    t2.team_acronym as team2_acronym,
    m.team1_score,
    m.team2_score,
FROM {{ ref('fct_matches') }} m
JOIN {{ ref('dim_teams') }} t1 on m.team1_id = t1.team_id
JOIN {{ ref('dim_teams') }} t2 on m.team2_id = t2.team_id
ORDER BY m.begin_at