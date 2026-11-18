import json
from pathlib import Path

from src.llm_client import GeminiClient
from src.preference_parser import PreferenceParser


TEST_CASES = [
    {
        "name": "Calm instrumental study music",
        "request": (
            "I want calm instrumental music for studying, "
            "nothing too energetic."
        ),
        "checks": {
            "high_instrumentalness": lambda r: (
                r["recommender_preferences"]["target_instrumentalness"]
                is not None
                and r["recommender_preferences"]["target_instrumentalness"] >= 0.8
            ),
            "low_energy": lambda r: (
                r["recommender_preferences"]["target_energy"] is not None
                and r["recommender_preferences"]["target_energy"] <= 0.5
            ),
            "study_context": lambda r: (
                "stud" in str(r["metadata"]["listening_context"]).lower()
            ),
            "energy_restriction_preserved": lambda r: (
                "energetic" in " ".join(
                    r["metadata"]["explicit_constraints"]
                ).lower()
            ),
        },
    },
    {
        "name": "2000s decade restriction",
        "request": "I only want music from the 2000s.",
        "checks": {
            "correct_decade": lambda r: (
                r["recommender_preferences"]["preferred_decade"] == 2000
            ),
            "restriction_preserved": lambda r: (
                "2000" in " ".join(
                    r["metadata"]["explicit_constraints"]
                ).lower()
            ),
        },
    },
    {
        "name": "Ambiguous request",
        "request": "Play something.",
        "checks": {
            "clarification_requested": lambda r: (
                r["metadata"]["needs_clarification"] is True
                and bool(r["metadata"]["clarification_question"])
            ),
        },
    },
    {
        "name": "No invented genre or context",
        "request": "I want music from the 2000s.",
        "checks": {
            "correct_decade": lambda r: (
                r["recommender_preferences"]["preferred_decade"] == 2000
            ),
            "no_invented_context": lambda r: (
                r["metadata"]["listening_context"] is None
            ),
            "no_invented_explicit_preferences": lambda r: (
                len(r["metadata"]["explicit_preferences"]) <= 1
            ),
        },
    },
    {
        "name": "Explicit versus inferred preferences",
        "request": (
            "I prefer relaxed music with acoustic instruments. "
            "I will be listening while reading."
        ),
        "checks": {
            "reading_context": lambda r: (
                "read" in str(r["metadata"]["listening_context"]).lower()
            ),
            "acoustic_preference": lambda r: (
                r["recommender_preferences"]["target_acousticness"] is not None
                and r["recommender_preferences"]["target_acousticness"] >= 0.6
            ),
            "relaxed_mood": lambda r: (
                "relax" in str(
                    r["recommender_preferences"]["favorite_mood"]
                ).lower()
            ),
        },
    },
]


def main():
    client = GeminiClient()

    report = {
        "evaluation_type": "Live Gemini prompt comparison",
        "note": (
            "Small predefined test set. Results are not statistically "
            "conclusive. API errors are excluded from accuracy."
        ),
        "results": {},
    }

    try:
        for style in ("baseline", "specialized"):
            parser = PreferenceParser(
                gemini=client,
                prompt_style=style
            )

            style_results = []
            passed_checks = 0
            total_checks = 0
            api_errors = 0
            completed_cases = 0

            print(f"\n{'=' * 55}")
            print(f"PROMPT MODE: {style.upper()}")
            print("=" * 55)

            for case in TEST_CASES:
                print(f"\nTesting: {case['name']}")

                try:
                    result = parser.parse(case["request"])
                    checks = {}

                    for check_name, check in case["checks"].items():
                        checks[check_name] = bool(check(result))

                    passed = sum(checks.values())
                    total = len(checks)

                    passed_checks += passed
                    total_checks += total
                    completed_cases += 1

                    case_result = {
                        "name": case["name"],
                        "status": "evaluated",
                        "checks": checks,
                        "passed": passed,
                        "total": total,
                        "confidence": result["metadata"]["confidence"],
                        "extracted_preferences": result[
                            "recommender_preferences"
                        ],
                        "metadata": result["metadata"],
                    }

                    print(f"  Checks passed: {passed}/{total}")

                    for name, success in checks.items():
                        status = "PASS" if success else "FAIL"
                        print(f"  [{status}] {name}")

                except Exception as error:
                    api_errors += 1

                    case_result = {
                        "name": case["name"],
                        "status": "api_or_parsing_error",
                        "error": str(error)[:500],
                    }

                    print(f"  [ERROR] {str(error)[:200]}")

                style_results.append(case_result)

            accuracy = (
                round(passed_checks / total_checks * 100, 1)
                if total_checks else None
            )

            coverage = round(
                completed_cases / len(TEST_CASES) * 100, 1
            )

            report["results"][style] = {
                "cases": style_results,
                "passed_checks": passed_checks,
                "total_checks": total_checks,
                "accuracy": accuracy,
                "completed_cases": completed_cases,
                "total_cases": len(TEST_CASES),
                "coverage": coverage,
                "api_errors": api_errors,
            }

            print(f"\n{style.title()} accuracy: {accuracy}%")
            print(
                f"Test coverage: {completed_cases}/{len(TEST_CASES)} ({coverage}%)")
            print(f"API/parsing errors: {api_errors}")

    finally:
        client.close()

    output_path = Path("reports/prompt_comparison.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8"
    )

    print("\n" + "=" * 55)
    print("FINAL PROMPT COMPARISON")
    print("=" * 55)

    for style, results in report["results"].items():
        print(f"\n{style.upper()}")
        print(f"Accuracy: {results['accuracy']}%")
        print(
            f"Coverage: {results['completed_cases']}/"
            f"{results['total_cases']} ({results['coverage']}%)"
        )
        print(f"API errors: {results['api_errors']}")

    print(f"\nDetailed report saved to: {output_path}")


if __name__ == "__main__":
    main()
