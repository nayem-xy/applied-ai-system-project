
import json
from datetime import datetime, timezone
from pathlib import Path

from src.llm_client import GeminiClient
from src.preference_parser import PreferenceParser
from src.reliability import RecommendationReliability
from src.agent_planner import AgentPlanner
from src.agent_tools import AgentTools


class MusicRecommendationAgent:
    """
    Agentic music recommendation system.

    The agent:
    1. Understands the user's request.
    2. Creates a conditional execution plan.
    3. Executes selected tools.
    4. Makes decisions based on tool results.
    5. Validates recommendations.
    6. Saves an execution trace.
    """

    def __init__(self, gemini=None, songs_path=None):
        self.gemini = gemini or GeminiClient()
        self.parser = PreferenceParser(gemini=self.gemini)

        project_root = Path(__file__).resolve().parents[1]

        self.songs_path = (
            Path(songs_path)
            if songs_path
            else project_root / "data" / "songs.csv"
        )

        self.songs = self._load_catalog()

        self.planner = AgentPlanner()
        self.tools = AgentTools()
        self.reliability = RecommendationReliability()

        self.trace_path = project_root / "logs" / "agentic_traces.jsonl"
        self.trace_path.parent.mkdir(parents=True, exist_ok=True)

    def _load_catalog(self):
        from src.recommender import load_songs

        return load_songs(str(self.songs_path))

    def _record_step(self, trace, action, reason, status, output=None):
        """Record an individual agent action."""

        step = {
            "step": len(trace) + 1,
            "action": action,
            "reason": reason,
            "status": status,
            "output": output or {}
        }

        trace.append(step)
        return step

    def _save_trace(self, trace, status):
        """Persist the execution trace as one JSONL record."""

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "steps": trace
        }

        with self.trace_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, default=str) + "\n")

    def _finish(self, result, trace):
        """Attach and save the execution trace."""

        result["execution_trace"] = trace
        self._save_trace(trace, result["status"])

        return result

    def run(self, user_request, k=5, strategy=None):
        trace = []

        # STEP 1: Understand the user's request.
        parsed_result = self.parser.parse(user_request)

        preferences = parsed_result["recommender_preferences"]
        metadata = parsed_result["metadata"]

        self._record_step(
            trace,
            "parse_request",
            "Extract user preferences and request metadata.",
            "success",
            {
                "confidence": metadata.get("confidence"),
                "needs_clarification": metadata.get(
                    "needs_clarification", False
                )
            }
        )

        # STEP 2: Ask the planner to choose the workflow.
        plan = self.planner.create_plan(preferences, metadata)

        self._record_step(
            trace,
            "create_plan",
            "Select actions based on request clarity and restrictions.",
            "success",
            {"planned_actions": [item["action"] for item in plan]}
        )

        # STEP 3: Execute the selected actions conditionally.
        eligible_songs = None
        reliability_report = None
        recommendations = None
        validation = None
        catalog_report = None

        for planned_action in plan:
            action = planned_action["action"]
            reason = planned_action["reason"]

            if action == "ask_clarification":
                self._record_step(
                    trace,
                    action,
                    reason,
                    "completed",
                    {"decision": "Stop recommendation workflow."}
                )

                return self._finish({
                    "status": "needs_clarification",
                    "clarification_question": metadata.get(
                        "clarification_question"
                    ),
                    "preferences": preferences,
                    "metadata": metadata,
                    "recommendations": []
                }, trace)

            elif action == "inspect_catalog":
                catalog_report = self.tools.inspect_catalog(self.songs)

                self._record_step(
                    trace,
                    action,
                    reason,
                    "success",
                    catalog_report
                )

            elif action == "filter_candidates":
                eligible_songs, reliability_report = (
                    self.tools.filter_candidates(
                        self.songs,
                        preferences,
                        metadata
                    )
                )

                self._record_step(
                    trace,
                    action,
                    reason,
                    "success",
                    {
                        "eligible_count": len(eligible_songs),
                        "excluded_count": reliability_report[
                            "excluded_count"
                        ]
                    }
                )

                # Make a decision based on the filtering result.
                if not eligible_songs:
                    self._record_step(
                        trace,
                        "decide_no_matches",
                        "No catalog songs satisfy the user's restrictions.",
                        "completed",
                        {"decision": "Stop before ranking."}
                    )

                    return self._finish({
                        "status": "no_valid_matches",
                        "preferences": preferences,
                        "metadata": metadata,
                        "reliability_report": reliability_report,
                        "recommendations": []
                    }, trace)

            elif action == "use_full_catalog":
                eligible_songs = self.songs

                self._record_step(
                    trace,
                    action,
                    reason,
                    "success",
                    {"eligible_count": len(eligible_songs)}
                )

            elif action == "rank_candidates":
                if eligible_songs is None:
                    raise RuntimeError(
                        "Planner did not provide eligible candidates."
                    )

                recommendations = self.tools.rank_candidates(
                    eligible_songs,
                    preferences,
                    k=k,
                    strategy=strategy
                )

                formatted_recommendations = [
                    {
                        "song": song,
                        "score": score,
                        "explanation": explanation
                    }
                    for song, score, explanation in recommendations
                ]

                self._record_step(
                    trace,
                    action,
                    reason,
                    "success",
                    {
                        "ranked_count": len(formatted_recommendations),
                        "strategy": (
                            type(strategy).__name__
                            if strategy is not None
                            else "BalancedStrategy"
                        )
                    }
                )

            elif action == "validate_recommendations":
                if recommendations is None:
                    raise RuntimeError(
                        "Planner attempted validation before ranking."
                    )

                validation = self.tools.validate_recommendations(
                    formatted_recommendations,
                    eligible_songs
                )

                self._record_step(
                    trace,
                    action,
                    reason,
                    "success" if validation["valid"] else "failed",
                    validation
                )

                if not validation["valid"]:
                    return self._finish({
                        "status": "validation_failed",
                        "preferences": preferences,
                        "metadata": metadata,
                        "reliability_report": reliability_report,
                        "validation": validation,
                        "recommendations": []
                    }, trace)

        # STEP 4: Return validated recommendations.
        if validation is None or not validation["valid"]:
            raise RuntimeError(
                "The workflow ended without successful validation."
            )

        return self._finish({
            "status": "success",
            "preferences": preferences,
            "metadata": metadata,
            "catalog_report": catalog_report,
            "reliability_report": reliability_report,
            "validation": validation,
            "recommendations": formatted_recommendations
        }, trace)

    def close(self):
        self.gemini.close()
