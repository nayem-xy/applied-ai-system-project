# VibeFinder 2.0 — AI-Powered Music Discovery Assistant

## 1. System Name

**VibeFinder 2.0 — AI-Powered Music Discovery Assistant**

VibeFinder 2.0 extends the original VibeFinder 1.0 content-based music recommendation simulation into a natural-language AI recommendation application.

The system allows users to describe the music they want in everyday language. A Gemini-powered preference parser converts the request into structured preferences, while the existing Python recommendation engine ranks songs from a local catalog.

The application combines generative AI with deterministic recommendation logic and a reliability layer.

## 2. Goal and Task

The goal is to make music discovery more accessible by allowing users to describe their listening needs naturally instead of manually entering individual music preferences.

For example:

> I want calm instrumental music for studying, nothing too energetic.

The system attempts to:

1. Understand the user's natural-language request.
2. Extract relevant musical preferences and constraints.
3. Ask for clarification when the request is too ambiguous.
4. Filter songs according to supported explicit constraints.
5. Rank eligible songs using the existing recommendation engine.
6. Validate the recommendations before returning them.
7. Explain why each song was recommended.

VibeFinder is a classroom demonstration of how a language model can work alongside a traditional recommendation algorithm.

## 3. System Architecture

VibeFinder 2.0 uses a hybrid architecture.

### Main Components

**1. Gemini Preference Parser**

The application uses Google's Gemini API to interpret natural-language requests.

The parser uses structured JSON output and Pydantic validation to extract fields such as:

- Favorite genre
- Favorite mood
- Target energy
- Target tempo
- Target valence
- Target danceability
- Target acousticness
- Preferred popularity
- Preferred release decade
- Preferred language
- Preferred instrumentalness
- Listening context
- Explicit preferences and constraints
- Inferred preferences
- Confidence and clarification information

The parser checks extracted categorical preferences against the available song catalog. It also tracks when defaults are applied.

**2. Music Recommendation Agent**

The agent coordinates the application workflow. It connects preference extraction, reliability checks, the existing recommendation engine, and output validation.

**3. Reliability Layer**

The reliability component checks supported explicit constraints before recommendations are ranked.

Current supported constraint checks include:

- Instrumental-only requests: instrumentalness must be at least 0.80.
- Low-energy requests: energy must not exceed 0.50.
- Release-decade requests: songs must match the requested decade when a decade constraint is explicitly identified.

If no songs satisfy the supported constraints, the application returns a no-valid-matches response rather than recommending an ineligible song.

**4. Existing Recommendation Engine**

The original content-based recommendation engine remains responsible for calculating scores and ranking songs.

It uses deterministic Python logic rather than asking Gemini to invent or rank songs.

**5. Output Validation**

Before returning recommendations, the system checks that:

- Recommended songs belong to the eligible catalog.
- Recommendation scores are numeric.
- Explanations are strings.

Invalid results are rejected.

### Architecture Diagram

The complete system architecture is available in:

`diagrams/architecture.mmd`

## 4. Data Used

The application uses a local CSV dataset containing **18 songs**.

Each song contains:

- ID
- Title
- Artist
- Genre
- Mood
- Energy
- Tempo
- Valence
- Danceability
- Acousticness
- Popularity
- Release decade
- Mood tags
- Language
- Instrumentalness

The dataset includes genres such as pop, rock, lofi, jazz, ambient, synthwave, indie pop, country, R&B, blues, reggae, metal, classical, funk, and house.

Some additional metadata is illustrative and simulated rather than verified information from a commercial music catalog.

The dataset is small and was designed for experimentation and classroom demonstration. It is not representative of the diversity or scale of a commercial streaming catalog.

## 5. Recommendation Algorithm

VibeFinder uses content-based filtering.

The recommendation engine compares the extracted user preferences with song attributes and calculates scores using the existing weighted scoring logic.

The original VibeFinder 1.0 scoring configuration included:

- Genre match: 2.0 points
- Mood match: 1.0 point
- Energy similarity: up to 1.5 points
- Tempo similarity: up to 1.5 points
- Valence similarity: up to 1.0 point
- Danceability similarity: up to 1.0 point
- Acousticness similarity: up to 1.0 point

The maximum baseline score was 9 points.

VibeFinder 1.0 also introduced four recommendation strategies through the Strategy design pattern:

- **BalancedStrategy:** Balances the recommendation features.
- **GenreFirstStrategy:** Prioritizes genre similarity.
- **MoodFirstStrategy:** Prioritizes mood similarity.
- **EnergyFirstStrategy:** Prioritizes energy similarity.

These strategies remain part of the underlying recommendation project.

In VibeFinder 2.0, the AI parser translates natural-language requests into structured preferences. The deterministic recommendation engine then uses those preferences to calculate and rank recommendations.

The language model does not directly calculate recommendation scores or create songs that are absent from the catalog.

## 6. Reliability, Guardrails, and Error Handling

Reliability is an important part of VibeFinder 2.0.

The application includes several checks to reduce incorrect or misleading recommendations.

### Preference Validation

- Structured output is validated using Pydantic.
- Extracted categorical preferences are checked against catalog values.
- Missing preferences may receive documented defaults.
- Low-confidence or ambiguous requests can trigger a clarification response.

The clarification threshold currently uses a confidence score below 0.55, or a clarification question returned by the parser.

### Explicit Constraint Filtering

The reliability layer filters candidates before recommendation ranking.

Examples:

| User constraint | Current behavior |
|---|---|
| Instrumental only | Excludes songs below 0.80 instrumentalness |
| Nothing too energetic | Excludes songs above 0.50 energy |
| Only music from the 2000s | Keeps songs matching the requested decade when identified as an explicit decade constraint |

These are engineering thresholds chosen for this demonstration. They have not been scientifically validated.

The application currently supports only a limited set of explicit constraint phrases. It does not guarantee enforcement of every possible natural-language restriction.

### Recommendation Validation

The system checks that recommendations come from the eligible candidate list and contain valid score and explanation fields.

If validation fails, the application returns a validation-failure response rather than displaying the invalid recommendations as successful results.

### Error Handling

The CLI catches request-processing errors and allows the user to try again.

External Gemini API failures, including temporary service-unavailable errors, can prevent a live recommendation request from completing.

The system therefore depends on external API availability for natural-language preference extraction.

## 7. Evaluation and Testing

The project includes automated tests for the original recommendation functionality, reliability checks, and agent workflow.

The current automated test suite reports:

**12 passed.**

The tests cover:

- Existing recommendation functionality.
- Instrumental constraint filtering.
- Low-energy constraint filtering.
- Release-decade filtering.
- Cases with no eligible songs.
- Recommendation validation.
- Successful agent workflow using mocked components.
- Clarification behavior.
- No-valid-matches behavior.

The agent tests use mocked preference extraction so that the application workflow can be tested without depending on live Gemini API availability.

### Representative Evaluation Scenarios

**Scenario 1 — Successful recommendation**

Input:

> I want instrumental music for studying.

Expected behavior:

- Extract music preferences.
- Apply the instrumental-only constraint.
- Exclude songs below the instrumentalness threshold.
- Rank eligible songs.
- Validate the returned recommendations.

**Scenario 2 — No valid matches**

Input:

> I only want music from the 1990s.

Expected behavior:

- Identify the requested decade.
- Apply the decade constraint.
- Return a no-valid-matches response if no catalog songs qualify.
- Do not recommend songs that violate the constraint.

**Scenario 3 — Ambiguous request**

Input:

> Play something.

Expected behavior:

- Detect insufficient information or low confidence.
- Ask the user a clarification question.
- Avoid generating recommendations until clarification is provided.

Additional scenario documentation is available in:

`logs/agent_traces.md`

These are representative workflow traces, not recordings of successful live Gemini API calls.

### Live API Testing

The CLI was launched and a natural-language request was submitted to Gemini.

The API returned a `503 UNAVAILABLE` response because the selected model was experiencing high demand.

This demonstrated that the application can encounter external service-availability limitations. The mocked automated tests remain independent of that external service.

## 8. Baseline Evaluation: VibeFinder 1.0

Before introducing the AI-powered workflow, VibeFinder 1.0 was evaluated using four predefined profiles:

1. High-Energy Pop
2. Chill Lofi
3. Deep Intense Rock
4. High-Energy Melancholic

The original baseline produced these top recommendations:

| Profile | Top recommendation | Score |
|---|---|---:|
| High-Energy Pop | Sunrise City | 8.40/9 |
| Chill Lofi | Library Rain | 8.87/9 |
| Deep Intense Rock | Storm Runner | 8.76/9 |
| High-Energy Melancholic | Gym Hero | 7.04/9 |

The High-Energy Melancholic profile revealed a weakness: Gym Hero ranked first even though its mood did not match the requested melancholic mood.

This illustrated how numerical similarities and other feature weights can outweigh an important preference mismatch.

### Weight-Shift Experiment

An experiment reduced genre weight from 2 to 1 and increased energy weight from 1.5 to 3.

The maximum score increased from 9 to 9.5.

The top-ranked songs remained unchanged for all four profiles, although several lower-ranked songs became more competitive.

For example, Iron Thunder became more competitive for the Deep Intense Rock profile because of its high energy similarity.

This experiment demonstrated that changing weights affects ranking scores but does not necessarily improve recommendation quality.

The original detailed baseline and weight-shift results are documented in the project's earlier VibeFinder 1.0 evaluation.

## 9. Strengths and Limitations

### Strengths

- Accepts natural-language music requests.
- Separates language understanding from deterministic recommendation scoring.
- Uses structured output validation.
- Includes explicit constraint filtering.
- Supports clarification for ambiguous requests.
- Provides recommendation explanations.
- Includes automated tests for important workflow behaviors.
- Builds on the original Strategy-pattern recommendation engine.

### Limitations

- The song catalog contains only 18 songs.
- The dataset includes illustrative metadata.
- Constraint filtering supports only a limited number of explicit phrase patterns.
- The reliability thresholds are manually selected engineering choices.
- The system does not learn from listening history or user feedback.
- The system does not implement collaborative filtering.
- The application depends on external Gemini API availability.
- No large-scale user study or recommendation-quality evaluation has been performed.
- The current system does not implement retrieval-augmented generation, model fine-tuning, or an autonomous multi-tool agent workflow.

These limitations mean that VibeFinder 2.0 should be treated as an educational prototype rather than a production-ready recommendation platform.

## 10. Intended Use and Non-Intended Use

### Intended Use

VibeFinder is designed for:

- Classroom demonstrations.
- Experimenting with recommendation algorithms.
- Learning how language models can interpret user requests.
- Exploring structured outputs and validation.
- Understanding how deterministic software components can complement generative AI.
- Demonstrating reliability checks in an AI application.

### Non-Intended Use

VibeFinder is not intended to:

- Replace commercial music streaming platforms.
- Provide large-scale personalized music discovery.
- Guarantee that every recommendation matches a user's subjective taste.
- Infer sensitive personal information from listening preferences.
- Make claims about the quality of music beyond the available catalog metadata.

## 11. Ethical Considerations and Human Oversight

The system uses a small local catalog rather than collecting users' listening histories.

However, recommendations can still be affected by dataset limitations, scoring weights, and incomplete preference extraction.

A language model may misunderstand a request or infer a preference that the user did not explicitly state.

The application attempts to reduce these risks through structured parsing, clarification, constraint filtering, and output validation.

Users should review recommendations and decide whether they match their needs.

The developer remains responsible for testing system behavior and documenting limitations rather than treating AI-generated outputs as automatically correct.

## 12. Future Improvements

Potential future improvements include:

- Expanding the song catalog using a larger and more reliable dataset.
- Improving natural-language constraint recognition.
- Adding stronger handling of conflicting preferences.
- Improving recommendation diversity.
- Incorporating user feedback.
- Exploring retrieval-augmented generation for larger music catalogs.
- Adding a more extensive evaluation harness.
- Comparing recommendation quality across different language models and preference-extraction approaches.

## 13. AI Collaboration and Development Reflection

AI tools were used during development to brainstorm system architecture, explore structured preference extraction, implement and debug Python components, and develop test scenarios.

Several design decisions were made to keep the system reliable and understandable.

For example, using Gemini to calculate song rankings was not adopted. Instead, Gemini interprets user requests while the existing Python recommendation engine remains responsible for deterministic scoring.

The development process also involved debugging test expectations against the actual dataset. One low-energy filtering test initially expected nine eligible songs, but inspection showed that the correct number was eight. The test expectation was revised based on the actual data.

A more complex retrieval system was considered but deferred because the existing catalog contains only 18 songs and the immediate goal was to complete a working, testable AI application.

The project reinforced the importance of verifying AI-generated code, testing actual behavior, separating responsibilities between system components, and documenting limitations.

## 14. Project Files

| File | Purpose |
|---|---|
| `src/agent.py` | Coordinates the AI recommendation workflow |
| `src/preference_parser.py` | Extracts structured preferences using Gemini |
| `src/llm_client.py` | Handles Gemini API communication |
| `src/reliability.py` | Applies constraints and validates recommendations |
| `src/recommender.py` | Existing deterministic recommendation engine |
| `src/ai_main.py` | AI-powered command-line interface |
| `diagrams/architecture.mmd` | System architecture diagram |
| `logs/agent_traces.md` | Representative workflow traces |
| `tests/` | Automated tests |
| `ai_interactions.md` | AI collaboration and development notes |

---

**Project:** VibeFinder 2.0 — AI-Powered Music Discovery Assistant  
**Project Type:** Applied AI System / Educational Prototype  
**Core Approach:** Gemini-powered natural-language understanding + deterministic content-based recommendation + reliability validation