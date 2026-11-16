
class RecommendationReliability:
    """
    Enforces explicit user constraints before recommendations
    are ranked by the existing recommendation engine.
    """

    INSTRUMENTAL_THRESHOLD = 0.80
    MAX_LOW_ENERGY = 0.50

    def filter_candidates(self, songs, preferences, metadata):
        """
        Remove songs that violate explicitly stated constraints.

        Returns eligible songs and an audit report.
        """

        constraints = [
            str(item).lower()
            for item in metadata.get("explicit_constraints", [])
        ]

        instrumental_only = any(
            "instrumental only" in item
            or "only instrumental" in item
            or "no vocals" in item
            for item in constraints
        )

        decade_only = (
            preferences.get("preferred_decade") is not None
            and any(
                "decade" in item
                for item in constraints
            )
        )

        low_energy_only = any(
            phrase in item
            for item in constraints
            for phrase in (
                "nothing too energetic",
                "not too energetic",
                "no energetic songs",
                "avoid high energy",
                "low energy only"
            )
        )

        eligible_songs = []
        excluded_songs = []

        for song in songs:
            reasons = []

            if (
                instrumental_only
                and song["instrumentalness"] < self.INSTRUMENTAL_THRESHOLD
            ):
                reasons.append("Does not meet instrumentalness threshold")

            if (
                decade_only
                and song["release_decade"]
                != preferences["preferred_decade"]
            ):
                reasons.append("Does not match requested release decade")

            if (
                low_energy_only
                and song["energy"] > self.MAX_LOW_ENERGY
            ):
                reasons.append("Exceeds maximum permitted energy")

            if reasons:
                excluded_songs.append({
                    "song_id": song["id"],
                    "title": song["title"],
                    "reasons": reasons
                })
            else:
                eligible_songs.append(song)

        report = {
            "original_count": len(songs),
            "eligible_count": len(eligible_songs),
            "excluded_count": len(excluded_songs),
            "instrumental_only": instrumental_only,
            "decade_only": decade_only,
            "low_energy_only": low_energy_only,
            "excluded_songs": excluded_songs,
            "no_valid_matches": len(eligible_songs) == 0
        }

        return eligible_songs, report

    def validate_recommendations(self, recommendations, eligible_songs):
        """
        Verify that recommendations come from the eligible catalog
        and contain valid scores and explanations.
        """

        eligible_ids = {
            song["id"] for song in eligible_songs
        }

        errors = []

        for item in recommendations:
            song = item.get("song", {})

            if song.get("id") not in eligible_ids:
                errors.append(
                    f"Invalid or ineligible song: {song.get('title')}"
                )

            if not isinstance(item.get("score"), (int, float)):
                errors.append("Recommendation has an invalid score")

            if not isinstance(item.get("explanation"), str):
                errors.append("Recommendation has an invalid explanation")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "validated_count": len(recommendations)
        }
