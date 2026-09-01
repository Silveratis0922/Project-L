with team_matches as (

    SELECT
        tournament_id,
        team1_id as team_id,
        case WHEN winner_id = team1_id then 1 else 0 end as is_win,
        case WHEN winner_id = team2_id then 1 else 0 end as is_loss
    FROM {{ ref('fct_matches') }}
    where status = 'finished'

    union all

    SELECT
        tournament_id,
        team2_id as team_id,
        case WHEN winner_id = team2_id then 1 else 0 end as is_win,
        case WHEN winner_id = team1_id then 1 else 0 end as is_loss
    FROM {{ ref('fct_matches') }}
    where status = 'finished'

)

SELECT
    tm.tournament_id,
    dtn.tournament_name,
    tm.team_id,
    dte.team_name,
    dte.team_logo,
    dte.team_acronym,
    sum(tm.is_win)::BIGINT as wins,
    sum(tm.is_loss)::BIGINT as losses,
    count(*) as matches_played
FROM team_matches tm
JOIN {{ ref('dim_teams') }} dte on tm.team_id = dte.team_id
JOIN {{ ref('dim_tournaments') }} dtn on tm.tournament_id = dtn.tournament_id
GROUP BY tm.tournament_id, dtn.tournament_name, tm.team_id, dte.team_name, dte.team_logo, dte.team_acronym
ORDER BY tm.tournament_id, wins DESC