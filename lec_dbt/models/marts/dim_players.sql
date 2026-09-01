with unnested AS (

    SELECT
        team_id,
        unnest(players) as player
    FROM {{ ref('stg_teams') }}

)

SELECT
    player.id as player_id,
    player.name as player_name,
    player.role as player_role,
    player.nationality,
    player.age,
    player.active,
    player.image_url as player_photo,
    team_id
FROM unnested