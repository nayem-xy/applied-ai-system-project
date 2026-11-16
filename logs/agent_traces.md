# VibeFinder 2.0 — Agent Execution Traces

## Purpose

This document records representative execution paths through the VibeFinder 2.0 recommendation agent. It shows how natural-language requests are processed, how explicit constraints are enforced, and how recommendation results are validated.

## Trace 1: Successful recommendation

**Test type:** Offline agent test using mocked preference extraction.

**User request:** "I want instrumental music for studying."

| Step | Component | Action |
|---|---|---|
| 1 | Preference parser | Supplies structured music preferences |
| 2 | Agent | Checks whether clarification is needed |
| 3 | Reliability layer | Applies the instrumental-only constraint |
| 4 | Recommendation engine | Ranks eligible songs |
| 5 | Output validator | Checks song eligibility, scores, and explanations |
| 6 | Agent | Returns validated recommendations |

**Expected outcome:** `success`

**Verification:** Every returned song has an instrumentalness value of at least 0.80.

## Trace 2: No valid matches

**Test type:** Offline agent test using mocked preference extraction.

**User request:** "I only want music from the 1990s."

| Step | Component | Action |
|---|---|---|
| 1 | Preference parser | Supplies a 1990s release preference |
| 2 | Agent | Determines that clarification is not needed |
| 3 | Reliability layer | Filters the catalog for the 1990s |
| 4 | Reliability layer | Finds no eligible songs |
| 5 | Agent | Stops instead of returning unrelated recommendations |

**Expected outcome:** `no_valid_matches`

**Verification:** The recommendation list is empty and the reliability report indicates no valid matches.

## Trace 3: Ambiguous request

**Test type:** Offline agent test using mocked preference extraction.

**User request:** "Play something."

| Step | Component | Action |
|---|---|---|
| 1 | Preference parser | Supplies a low-confidence result |
| 2 | Agent | Checks the clarification flag |
| 3 | Agent | Stops the recommendation process |
| 4 | Agent | Returns a clarification question |

**Expected outcome:** `needs_clarification`

**Verification:** No recommendations are generated.

## Testing summary

The three agent scenarios above are covered by automated tests in `tests/test_agent.py`.

The reliability component is independently tested in `tests/test_reliability.py`.

These traces demonstrate the expected decision paths under mocked conditions. They are not presented as live Gemini API execution logs.