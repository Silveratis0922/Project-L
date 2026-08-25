with team_matches as (
    SELECT
        tournament_id,
        tournament_name,
        team1_id as team_id,
        team1_name as team_name,
        case WHEN winner_id = team1_id then 1 else 0 end as is_win,
        case WHEN winner_id = team2_id then 1 else 0 end as is_loss
    FROM {{ ref('stg_matches') }}
    where status = 'finished'

    union all

    SELECT
        tournament_id,
        tournament_name,
        team2_id as team_id,
        team2_name as team_name,
        case WHEN winner_id = team2_id then 1 else 0 end as is_win,
        case WHEN winner_id = team1_id then 1 else 0 end as is_loss
    FROM {{ ref('stg_matches') }}
    where status = 'finished'

)

SELECT
    tournament_id,
    tournament_name,
    team_id,
    team_name,
    sum(is_win) as wins,
    sum(is_loss) as losses,
    count(*) as matches_played
FROM team_matches
GROUP BY tournament_id, tournament_name, team_id, team_name
ORDER BY tournament_id, wins DESC