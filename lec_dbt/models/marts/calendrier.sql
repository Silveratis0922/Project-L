SELECT
    match_id,
    serie_id,
    tournament_id,
    match_name,
    status,
    begin_at,
    team1_name,
    team2_name,
    team1_score,
    team2_score,
from {{ ref('stg_matches') }}
order by begin_at