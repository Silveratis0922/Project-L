from main import flatten_match


def test_flatten_match_finished():
    match = {
        "id": 1,
        "serie_id": 100,
        "tournament_id": 10,
        "name": "A vs B",
        "status": "finished",
        "begin_at": "2026-01-01T00:00:00Z",
        "winner_id": 1,
        "opponents": [
            {"opponent": {"id": 1, "name": "Team A"}},
            {"opponent": {"id": 2, "name": "Team B"}},
        ],
        "results": [
            {"team_id": 1, "score": 2},
            {"team_id": 2, "score": 0},
        ],
    }

    result = flatten_match(match)

    assert result["team1"] == "Team A"
    assert result["team2"] == "Team B"
    assert result["score1"] == 2
    assert result["score2"] == 0
    assert result["winner_id"] == 1


def test_flatten_match_no_opponents():
    match = {
        "id": 2,
        "serie_id": 100,
        "tournament_id": 10,
        "name": "TBD vs TBD",
        "status": "not_started",
        "begin_at": "2026-01-02T00:00:00Z",
        "winner_id": None,
        "opponents": [],
        "results": [],
    }

    result = flatten_match(match)

    assert result["team1"] is None
    assert result["team2"] is None
    assert result["score1"] is None
    assert result["score2"] is None
