
from src.agent import MusicRecommendationAgent


class FakeGemini:
    """Prevent evaluation runs from calling the live Gemini API."""

    def close(self):
        pass


class FakeParser:
    """Return predefined structured preferences."""

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


def run_scenario(name, request, parser_result, check):
    """Run one end-to-end scenario and evaluate its result."""

    agent = MusicRecommendationAgent(gemini=FakeGemini())
    agent.parser = FakeParser(parser_result)

    try:
        result = agent.run(request)
        passed, details = check(result)
        return {
            "name": name,
            "passed": passed,
            "details": details
        }
    except Exception as error:
        return {
            "name": name,
            "passed": False,
            "details": f"Execution error: {error}"
        }


def check_success(result):
    passed = (
        result["status"] == "success"
        and len(result["recommendations"]) > 0
        and result["validation"]["valid"]
    )

    return passed, (
        f"Status: {result['status']}; "
        f"recommendations: {len(result['recommendations'])}"
    )


def check_instrumental(result):
    passed, _ = check_success(result)

    valid_songs = all(
        item["song"]["instrumentalness"] >= 0.80
        for item in result["recommendations"]
    )

    return passed and valid_songs, (
        f"Status: {result['status']}; "
        "all recommendations meet instrumental threshold"
    )


def check_low_energy(result):
    passed, _ = check_success(result)

    valid_songs = all(
        item["song"]["energy"] <= 0.50
        for item in result["recommendations"]
    )

    return passed and valid_songs, (
        f"Status: {result['status']}; "
        "all recommendations meet energy limit"
    )


def check_decade(result):
    passed, _ = check_success(result)

    valid_songs = all(
        item["song"]["release_decade"] == 2000
        for item in result["recommendations"]
    )

    return passed and valid_songs, (
        f"Status: {result['status']}; "
        "all recommendations are from the 2000s"
    )


def check_no_matches(result):
    passed = (
        result["status"] == "no_valid_matches"
        and len(result["recommendations"]) == 0
        and result["reliability_report"]["no_valid_matches"]
    )

    return passed, f"Status: {result['status']}"


def check_clarification(result):
    passed = (
        result["status"] == "needs_clarification"
        and len(result["recommendations"]) == 0
        and result["clarification_question"] is not None
    )

    return passed, f"Status: {result['status']}"


def main():
    scenarios = [
        (
            "Instrumental-only recommendations",
            "I want instrumental music for studying.",
            make_parser_result(["instrumental only"]),
            check_instrumental
        ),
        (
            "Low-energy recommendations",
            "I want something not too energetic.",
            make_parser_result(["nothing too energetic"]),
            check_low_energy
        ),
        (
            "2000s decade restriction",
            "I want music from the 2000s.",
            make_parser_result(
                ["Release decade: 2000s"],
                decade=2000
            ),
            check_decade
        ),
        (
            "No matching songs",
            "I only want music from the 1990s.",
            make_parser_result(
                ["Release decade: 1990s"],
                decade=1990
            ),
            check_no_matches
        ),
        (
            "Ambiguous request clarification",
            "Play something.",
            make_parser_result(
                confidence=0.2,
                clarification="What kind of music would you like?"
            ),
            check_clarification
        )
    ]

    results = []

    print("\nVIBEFINDER 2.0 - EVALUATION REPORT")
    print("=" * 48)

    for name, request, parser_result, check in scenarios:
        result = run_scenario(
            name, request, parser_result, check
        )
        results.append(result)

        status = "PASS" if result["passed"] else "FAIL"

        print(f"\n[{status}] {result['name']}")
        print(f"  {result['details']}")

    passed_count = sum(
        result["passed"] for result in results
    )
    total = len(results)
    score = (passed_count / total) * 100

    print("\n" + "=" * 48)
    print("FINAL EVALUATION SUMMARY")
    print(f"Passed: {passed_count}/{total}")
    print(f"Failed: {total - passed_count}/{total}")
    print(f"Success rate: {score:.1f}%")
    print("=" * 48)

    return 0 if passed_count == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
