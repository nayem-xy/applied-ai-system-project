
from pathlib import Path

from src.llm_client import GeminiClient
from src.preference_parser import PreferenceParser
from src.recommender import load_songs, recommend_songs
from src.reliability import RecommendationReliability


class MusicRecommendationAgent:
    def __init__(self, gemini=None, songs_path=None):
        self.gemini = gemini or GeminiClient()
        self.parser = PreferenceParser(gemini=self.gemini)

        project_root = Path(__file__).resolve().parents[1]

        self.songs_path = (
            Path(songs_path)
            if songs_path
            else project_root / "data" / "songs.csv"
        )

        self.songs = load_songs(str(self.songs_path))
        self.reliability = RecommendationReliability()

    def run(self, user_request, k=5, strategy=None):
        # STEP 1: Understand the user's natural-language request.
        parsed_result = self.parser.parse(user_request)

        preferences = parsed_result["recommender_preferences"]
        metadata = parsed_result["metadata"]

        # STEP 2: Ask for clarification if the request is ambiguous.
        if metadata["needs_clarification"]:
            return {
                "status": "needs_clarification",
                "clarification_question": metadata["clarification_question"],
                "preferences": preferences,
                "metadata": metadata,
                "recommendations": []
            }

        # STEP 3: Enforce explicit constraints before ranking.
        eligible_songs, reliability_report = (
            self.reliability.filter_candidates(
                self.songs,
                preferences,
                metadata
            )
        )

        # STEP 4: Stop if no songs satisfy the constraints.
        if not eligible_songs:
            return {
                "status": "no_valid_matches",
                "preferences": preferences,
                "metadata": metadata,
                "reliability_report": reliability_report,
                "recommendations": []
            }

        # STEP 5: Rank only eligible songs using the existing engine.
        recommendations = recommend_songs(
            user_prefs=preferences,
            songs=eligible_songs,
            k=k,
            strategy=strategy
        )

        formatted_recommendations = []

        for song, score, explanation in recommendations:
            formatted_recommendations.append({
                "song": song,
                "score": score,
                "explanation": explanation
            })

        # STEP 6: Validate the generated recommendations.
        validation = self.reliability.validate_recommendations(
            formatted_recommendations,
            eligible_songs
        )

        # STEP 7: Do not return invalid recommendations as successful.
        if not validation["valid"]:
            return {
                "status": "validation_failed",
                "preferences": preferences,
                "metadata": metadata,
                "reliability_report": reliability_report,
                "validation": validation,
                "recommendations": []
            }

        # STEP 8: Return validated recommendations and audit information.
        return {
            "status": "success",
            "preferences": preferences,
            "metadata": metadata,
            "reliability_report": reliability_report,
            "validation": validation,
            "recommendations": formatted_recommendations
        }

    def close(self):
        self.gemini.close()
