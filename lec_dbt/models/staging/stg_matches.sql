with deduplicated as (
    select
        *,
        row_number() over (partition by id order by modified_at desc) as rn
    from {{ source('bronze', 'matches_raw') }}
),

latest as (
    select * from deduplicated where rn = 1
)

select
    id as match_id,
    serie_id,
    tournament_id,
    tournament.name as tournament_name,
    name as match_name,
    status,
    begin_at,
    end_at,
    winner_id,
    opponents[1].opponent.id as team1_id,
    opponents[1].opponent.name as team1_name,
    opponents[2].opponent.id as team2_id,
    opponents[2].opponent.name as team2_name,
    list_filter(results, x -> x.team_id = opponents[1].opponent.id)[1].score as team1_score,
    list_filter(results, x -> x.team_id = opponents[2].opponent.id)[1].score as team2_score
from latest