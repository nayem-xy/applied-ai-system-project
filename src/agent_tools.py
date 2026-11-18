
from src.reliability import RecommendationReliability
from src.recommender import recommend_songs


class AgentTools:
    """Tools available to the music recommendation agent."""

    def __init__(self):
        self.reliability = RecommendationReliability()

    def inspect_catalog(self, songs):
        """Inspect available catalog information."""

        return {
            "total_songs": len(songs),
            "available_genres": sorted({
                song["genre"] for song in songs
            }),
            "available_decades": sorted({
                song["release_decade"] for song in songs
            }),
            "available_languages": sorted({
                song["language"] for song in songs
            })
        }

    def filter_candidates(self, songs, preferences, metadata):
        """Filter songs against explicit user restrictions."""

        return self.reliability.filter_candidates(
            songs,
            preferences,
            metadata
        )

    def rank_candidates(
        self,
        songs,
        preferences,
        k=5,
        strategy=None
    ):
        """Rank eligible songs using the selected strategy."""

        return recommend_songs(
            user_prefs=preferences,
            songs=songs,
            k=k,
            strategy=strategy
        )

    def validate_recommendations(self, recommendations, eligible_songs):
        """Validate recommendations before returning them."""

        return self.reliability.validate_recommendations(
            recommendations,
            eligible_songs
        )
