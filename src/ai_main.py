
from src.agent import MusicRecommendationAgent


def display_recommendations(result):
    """Display the agent's response in the terminal."""

    print("\n" + "=" * 60)
    print("             VIBEFINDER 2.0")
    print("       AI-POWERED MUSIC DISCOVERY")
    print("=" * 60)

    status = result["status"]

    if status == "needs_clarification":
        print("\nI need a little more information.")
        print(result["clarification_question"])
        return

    if status == "no_valid_matches":
        print("\nNo songs satisfy all your explicit constraints.")
        report = result["reliability_report"]
        print(f"Songs checked: {report['original_count']}")
        print(f"Songs excluded: {report['excluded_count']}")
        return

    if status == "validation_failed":
        print("\nRecommendation validation failed.")
        for error in result["validation"]["errors"]:
            print(f"- {error}")
        return

    if status != "success":
        print(f"\nUnexpected result: {status}")
        return

    print("\nYOUR RECOMMENDATIONS\n")

    for index, item in enumerate(result["recommendations"], start=1):
        song = item["song"]

        print(f"{index}. {song['title']} — {song['artist']}")
        print(f"   Genre: {song['genre']} | Mood: {song['mood']}")
        print(f"   Energy: {song['energy']}")
        print(f"   Score: {item['score']:.2f}")
        print(f"   Why: {item['explanation']}\n")

    report = result["reliability_report"]
    validation = result["validation"]

    print("-" * 60)
    print("RELIABILITY SUMMARY")
    print(f"Songs in catalog: {report['original_count']}")
    print(f"Eligible songs: {report['eligible_count']}")
    print(f"Excluded songs: {report['excluded_count']}")
    print(f"Validated recommendations: {validation['validated_count']}")
    print(f"Validation passed: {validation['valid']}")
    print("=" * 60)


def main():
    agent = None

    print("\nWelcome to VibeFinder 2.0!")
    print("Describe the kind of music you're looking for.")
    print("Type 'exit' to quit.\n")

    try:
        agent = MusicRecommendationAgent()

        while True:
            user_request = input(
                "\nWhat would you like to listen to? ").strip()

            if user_request.lower() in {"exit", "quit"}:
                print("\nThanks for using VibeFinder 2.0!")
                break

            if not user_request:
                print("Please enter a music request.")
                continue

            print("\nUnderstanding your preferences and finding music...")

            try:
                result = agent.run(user_request)
                display_recommendations(result)

            except Exception as error:
                print(f"\nUnable to process your request: {error}")
                print("Please try again.")

    except Exception as error:
        print(f"\nUnable to start VibeFinder: {error}")

    finally:
        if agent is not None:
            agent.close()


if __name__ == "__main__":
    main()
