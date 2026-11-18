
class AgentPlanner:
    """
    Creates an execution plan based on the user's extracted preferences.

    The planner makes conditional decisions about which tools
    the recommendation agent should execute.
    """

    def create_plan(self, preferences, metadata):
        plan = []

        # Decision 1: Is the user's request clear enough?
        if metadata.get("needs_clarification", False):
            plan.append({
                "action": "ask_clarification",
                "reason": "The user's request is ambiguous or has low confidence."
            })

            return plan

        # Decision 2: Does the request contain explicit restrictions?
        constraints = metadata.get("explicit_constraints", [])
        preferred_decade = preferences.get("preferred_decade")

        if constraints or preferred_decade is not None:
            plan.append({
                "action": "inspect_catalog",
                "reason": "Explicit restrictions require checking available catalog data."
            })

            plan.append({
                "action": "filter_candidates",
                "reason": "Only songs satisfying the user's restrictions should be considered."
            })

        else:
            plan.append({
                "action": "use_full_catalog",
                "reason": "No explicit restrictions require removing catalog candidates."
            })

        # Decision 3: Rank the eligible songs.
        plan.append({
            "action": "rank_candidates",
            "reason": "Eligible songs must be scored against the user's preferences."
        })

        # Decision 4: Validate before returning recommendations.
        plan.append({
            "action": "validate_recommendations",
            "reason": "Recommendations must pass reliability checks before delivery."
        })

        return plan
