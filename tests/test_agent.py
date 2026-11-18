
import json
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


def test_agent_plan_changes_for_ambiguous_request():
    agent = create_agent(
        make_parser_result(
            confidence=0.2,
            clarification="What kind of music would you like?"
        )
    )

    result = agent.run("Play something.")

    actions = [
        step["action"]
        for step in result["execution_trace"]
    ]

    assert result["status"] == "needs_clarification"
    assert "ask_clarification" in actions
    assert "inspect_catalog" not in actions
    assert "rank_candidates" not in actions


def test_agent_inspects_catalog_for_explicit_constraints():
    agent = create_agent(
        make_parser_result(
            constraints=["instrumental only"]
        )
    )

    result = agent.run("I want instrumental music only.")

    actions = [
        step["action"]
        for step in result["execution_trace"]
    ]

    assert result["status"] == "success"
    assert "inspect_catalog" in actions
    assert "filter_candidates" in actions
    assert "rank_candidates" in actions
    assert "validate_recommendations" in actions


def test_agent_stops_when_no_candidates_match():
    agent = create_agent(
        make_parser_result(
            constraints=["Release decade: 1990s"],
            decade=1990
        )
    )

    result = agent.run("Only music from the 1990s.")

    actions = [
        step["action"]
        for step in result["execution_trace"]
    ]

    assert result["status"] == "no_valid_matches"
    assert "decide_no_matches" in actions
    assert "rank_candidates" not in actions


def test_agent_skips_filtering_without_explicit_constraints():
    agent = create_agent(make_parser_result())

    result = agent.run("Give me some music.")

    actions = [
        step["action"]
        for step in result["execution_trace"]
    ]

    assert result["status"] == "success"
    assert "use_full_catalog" in actions
    assert "inspect_catalog" not in actions
    assert "filter_candidates" not in actions


def test_agent_saves_execution_trace(tmp_path):
    agent = create_agent(make_parser_result())

    agent.trace_path = tmp_path / "agentic_traces.jsonl"

    result = agent.run("Give me some music.")

    assert agent.trace_path.exists()

    with agent.trace_path.open(encoding="utf-8") as file:
        saved_record = json.loads(file.readline())

    assert saved_record["status"] == "success"
    assert len(saved_record["steps"]) > 0
    assert result["execution_trace"] == saved_record["steps"]
