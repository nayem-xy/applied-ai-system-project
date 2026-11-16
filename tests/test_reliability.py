from src.recommender import load_songs
from src.reliability import RecommendationReliability


def setup_reliability():
    songs = load_songs("data/songs.csv")
    reliability = RecommendationReliability()
    return songs, reliability


def test_instrumental_only_filter():
    songs, reliability = setup_reliability()

    metadata = {"explicit_constraints": ["instrumental only"]}

    eligible, report = reliability.filter_candidates(
        songs, {}, metadata
    )

    assert len(eligible) == 6
    assert all(song["instrumentalness"] >= 0.80 for song in eligible)


def test_decade_only_filter():
    songs, reliability = setup_reliability()

    preferences = {"preferred_decade": 2000}
    metadata = {"explicit_constraints": ["Release decade: 2000s"]}

    eligible, report = reliability.filter_candidates(
        songs, preferences, metadata
    )

    assert len(eligible) == 3
    assert all(song["release_decade"] == 2000 for song in eligible)


def test_low_energy_filter():
    songs, reliability = setup_reliability()

    metadata = {"explicit_constraints": ["nothing too energetic"]}

    eligible, report = reliability.filter_candidates(
        songs, {}, metadata
    )

    assert len(eligible) == 8
    assert all(song["energy"] <= 0.50 for song in eligible)


def test_combined_constraints():
    songs, reliability = setup_reliability()

    preferences = {"preferred_decade": 2000}
    metadata = {
        "explicit_constraints": [
            "instrumental only",
            "Release decade: 2000s"
        ]
    }

    eligible, report = reliability.filter_candidates(
        songs, preferences, metadata
    )

    assert len(eligible) == 1
    assert eligible[0]["title"] == "Dreamscape"


def test_no_valid_matches():
    songs, reliability = setup_reliability()

    preferences = {"preferred_decade": 1990}
    metadata = {"explicit_constraints": ["Release decade: 1990s"]}

    eligible, report = reliability.filter_candidates(
        songs, preferences, metadata
    )

    assert eligible == []
    assert report["no_valid_matches"] is True


def test_valid_recommendation():
    songs, reliability = setup_reliability()

    recommendations = [{
        "song": songs[0],
        "score": 4.5,
        "explanation": "Matches the requested mood and energy."
    }]

    result = reliability.validate_recommendations(
        recommendations, songs
    )

    assert result["valid"] is True
    assert result["validated_count"] == 1


def test_reject_ineligible_recommendation():
    songs, reliability = setup_reliability()

    eligible = [
        song for song in songs
        if song["instrumentalness"] >= 0.80
    ]

    recommendations = [{
        "song": songs[0],
        "score": 4.5,
        "explanation": "This is a test recommendation."
    }]

    result = reliability.validate_recommendations(
        recommendations, eligible
    )

    assert result["valid"] is False
    assert len(result["errors"]) > 0
