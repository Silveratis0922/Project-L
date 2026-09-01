with deduplicated as (

    SELECT
        *,
        row_number() over (PARTITION BY id ORDER BY modified_at DESC) as rn
    FROM {{ source('bronze', 'teams_raw') }}
)

SELECT
    id as team_id,
    name as team_name,
    acronym as team_acronym,
    image_url as team_logo,
    dark_mode_image_url as team_dark_logo,
    location,
    players
FROM deduplicated
WHERE rn = 1

