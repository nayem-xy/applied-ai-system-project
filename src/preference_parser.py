
import csv
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field
from google.genai import types

from src.llm_client import GeminiClient


# ============================================================
# 1. STRUCTURED OUTPUT SCHEMA
# ============================================================

class PreferenceExtraction(BaseModel):
    """Structured preferences extracted from a user's request."""

    favorite_genre: Optional[str] = None
    favorite_mood: Optional[str] = None

    target_energy: Optional[float] = Field(
        default=None, ge=0, le=1
    )
    target_tempo: Optional[float] = Field(
        default=None, ge=40, le=220
    )
    target_valence: Optional[float] = Field(
        default=None, ge=0, le=1
    )
    target_danceability: Optional[float] = Field(
        default=None, ge=0, le=1
    )
    target_acousticness: Optional[float] = Field(
        default=None, ge=0, le=1
    )
    target_popularity: Optional[int] = Field(
        default=None, ge=0, le=100
    )
    preferred_decade: Optional[int] = None
    preferred_mood_tags: list[str] = Field(default_factory=list)
    preferred_language: Optional[str] = None
    target_instrumentalness: Optional[float] = Field(
        default=None, ge=0, le=1
    )

    listening_context: Optional[str] = None

    explicit_constraints: list[str] = Field(default_factory=list)
    explicit_preferences: list[str] = Field(default_factory=list)
    inferred_preferences: list[str] = Field(default_factory=list)

    confidence: float = Field(ge=0, le=1)
    clarification_question: Optional[str] = None


# ============================================================
# 2. PREFERENCE PARSER
# ============================================================

class PreferenceParser:
    """Convert natural-language requests into music preferences."""

    def __init__(self, gemini=None, csv_path=None):

        self.gemini = gemini or GeminiClient()

        project_root = Path(__file__).resolve().parents[1]

        self.csv_path = (
            Path(csv_path)
            if csv_path
            else project_root / "data" / "songs.csv"
        )

        self.catalog = self._load_catalog()

    def _load_catalog(self):
        """Read valid preference values from the song catalog."""

        with open(
            self.csv_path,
            newline="",
            encoding="utf-8"
        ) as file:
            songs = list(csv.DictReader(file))

        return {
            "genres": sorted({s["genre"].lower() for s in songs}),
            "moods": sorted({s["mood"].lower() for s in songs}),
            "languages": sorted({s["language"] for s in songs}),
            "decades": sorted({
                int(s["release_decade"]) for s in songs
            }),
            "mood_tags": sorted({
                tag.strip().lower()
                for s in songs
                for tag in s["mood_tags"].split("|")
                if tag.strip()
            })
        }

    def _build_prompt(self, user_request):
        """Give Gemini the request and valid catalog vocabulary."""

        return f"""
You are the preference extraction component of VibeFinder,
an AI-powered music recommendation system.

Analyze the user's request and extract music preferences.

USER REQUEST:
{user_request}

AVAILABLE CATALOG VALUES:
Genres: {self.catalog["genres"]}
Moods: {self.catalog["moods"]}
Languages: {self.catalog["languages"]}
Release decades: {self.catalog["decades"]}
Mood tags: {self.catalog["mood_tags"]}

RULES:

1. Only select genres, moods, languages, decades, and mood
   tags that exist in the catalog.

2. Use null when a preference cannot reasonably be determined.
   Do not invent preferences.

3. Energy, valence, danceability, acousticness, and
   instrumentalness range from 0.0 to 1.0.

4. Tempo is measured in beats per minute (BPM).

5. Popularity ranges from 0 to 100.

6. Instrumental music should map to high target_instrumentalness.
   Do not treat "Instrumental" as a spoken language preference.

7. Distinguish explicit preferences from inferred preferences.
   An explicit preference was directly stated by the user.
   An inferred preference is a reasonable interpretation.

8. Preserve explicit exclusions and restrictions in
   explicit_constraints. Do not silently discard them.

9. Confidence should reflect how clearly the request expresses
   its preferences.

10. If the request is too ambiguous to interpret, provide a
    clarification_question.

11. Do not invent a listening context.

Return only the structured fields defined by the response schema.
"""

    # ========================================================
    # 3. PARSE AND NORMALIZE
    # ========================================================

    def parse(self, user_request):
        """Extract and normalize preferences for the recommender."""

        if not isinstance(user_request, str) or not user_request.strip():
            raise ValueError("Please provide a non-empty music request.")

        prompt = self._build_prompt(user_request)

        response = self.gemini.client.models.generate_content(
            model=self.gemini.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=PreferenceExtraction
            )
        )

        extracted = response.parsed

        if extracted is None:
            raise RuntimeError(
                "Gemini did not return valid structured preferences."
            )

        data = extracted.model_dump()

        # Validate catalog values and replace unsupported selections.
        data["favorite_genre"] = self._catalog_value(
            data["favorite_genre"], "genres"
        )

        data["favorite_mood"] = self._catalog_value(
            data["favorite_mood"], "moods"
        )

        data["preferred_language"] = self._catalog_value(
            data["preferred_language"], "languages"
        )

        data["preferred_mood_tags"] = [
            tag.lower()
            for tag in data["preferred_mood_tags"]
            if tag.lower() in self.catalog["mood_tags"]
        ]

        if data["preferred_decade"] not in self.catalog["decades"]:
            data["preferred_decade"] = None

        # The original scoring engine requires these three fields.
        defaulted_fields = []

        defaults = {
            "favorite_genre": "pop",
            "favorite_mood": "happy",
            "target_energy": 0.5
        }

        for field, default in defaults.items():
            if data[field] is None:
                data[field] = default
                defaulted_fields.append(field)

        # Build the dictionary accepted by recommend_songs().
        recommender_fields = [
            "favorite_genre",
            "favorite_mood",
            "target_energy",
            "target_tempo",
            "target_valence",
            "target_danceability",
            "target_acousticness",
            "target_popularity",
            "preferred_decade",
            "preferred_mood_tags",
            "preferred_language",
            "target_instrumentalness"
        ]

        recommender_preferences = {
            field: data[field]
            for field in recommender_fields
        }
        needs_clarification = (
            data["confidence"] < 0.55
            or data["clarification_question"] is not None
        )
        metadata = {
            "listening_context": data["listening_context"],
            "explicit_constraints": data["explicit_constraints"],
            "explicit_preferences": data["explicit_preferences"],
            "inferred_preferences": data["inferred_preferences"],
            "confidence": data["confidence"],
            "clarification_question": data["clarification_question"],
            "defaulted_fields": defaulted_fields,
            "needs_clarification": needs_clarification
        }

        return {
            "recommender_preferences": recommender_preferences,
            "metadata": metadata
        }

    def _catalog_value(self, value, catalog_field):
        """Return a catalog-supported value or None."""

        if value is None:
            return None

        normalized = value.strip().lower()

        if normalized in self.catalog[catalog_field]:
            return normalized

        return None
