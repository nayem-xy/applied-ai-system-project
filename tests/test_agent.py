
from src.agent import MusicRecommendationAgent


class FakeGemini:
    """Prevents tests from making real Gemini API calls."""

    def close(self):
        pass


class FakeParser:
    """Returns predefined preferences instead of calling Gemini."""

    def __init__(self, result):
        self.result = result

    def parse(self, user_request):
        return self.result


def make_parser_result(
    constraints=None,
    decade=None,
    confidence=0.95,
    clarification=None
):
    preferences = {
        "favorite_genre": "lofi",
        "favorite_mood": "focused",
        "target_energy": 0.4,
        "target_tempo": None,
        "target_valence": None,
        "target_danceability": None,
        "target_acousticness": None,
        "target_popularity": None,
        "preferred_decade": decade,
        "preferred_mood_tags": [],
        "preferred_language": None,
        "target_instrumentalness": None
    }

    metadata = {
        "listening_context": "studying",
        "explicit_constraints": constraints or [],
        "explicit_preferences": [],
        "inferred_preferences": [],
        "confidence": confidence,
        "clarification_question": clarification,
        "defaulted_fields": [],
        "needs_clarification": (
            confidence < 0.55 or clarification is not None
        )
    }

    return {
        "recommender_preferences": preferences,
        "metadata": metadata
    }


def create_agent(parser_result):
    agent = MusicRecommendationAgent(gemini=FakeGemini())
    agent.parser = FakeParser(parser_result)
    return agent


def test_agent_successful_recommendations():
    parser_result = make_parser_result(
        constraints=["instrumental only"]
    )

    agent = create_agent(parser_result)

    result = agent.run("I want instrumental music for studying.")

    assert result["status"] == "success"
    assert len(result["recommendations"]) > 0
    assert result["validation"]["valid"] is True

    for item in result["recommendations"]:
        assert item["song"]["instrumentalness"] >= 0.80


def test_agent_no_valid_matches():
    parser_result = make_parser_result(
        constraints=["Release decade: 1990s"],
        decade=1990
    )

    agent = create_agent(parser_result)

    result = agent.run("I only want music from the 1990s.")

    assert result["status"] == "no_valid_matches"
    assert result["recommendations"] == []
    assert result["reliability_report"]["no_valid_matches"] is True


def test_agent_requests_clarification():
    parser_result = make_parser_result(
        confidence=0.2,
        clarification="What kind of music would you like?"
    )

    agent = create_agent(parser_result)

    result = agent.run("Play something.")

    assert result["status"] == "needs_clarification"
    assert result["recommendations"] == []
    assert result["clarification_question"] is not None
