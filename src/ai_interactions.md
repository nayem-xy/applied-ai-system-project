# AI Interaction Log – VibeFinder 1.0

## Challenge 1: Advanced Song Attributes

### Objective
Expand the music recommendation system by introducing at least five additional song attributes and incorporating them into the recommendation scoring algorithm.

### 1. Advanced Attributes Added

Five attributes were added to `data/songs.csv`:

| Attribute | Description |
|---|---|
| `popularity` | Song popularity score from 0–100 |
| `release_decade` | Decade in which the song was released |
| `mood_tags` | Multiple descriptive mood tags |
| `language` | Song language |
| `instrumentalness` | Degree to which a song is instrumental (0–1) |

The additional metadata in the demonstration dataset is illustrative and simulated.

### 2. AI Assistance

ChatGPT was used to:
- Brainstorm useful advanced song attributes.
- Help update the CSV structure.
- Modify `load_songs()` to parse the new attributes into appropriate Python data types.
- Extend `score_song()` to calculate similarity using the new attributes.
- Generate explanations showing why each song received additional points.
- Troubleshoot CSV formatting and Python implementation errors.

### 3. Scoring Implementation

The original scoring system had a maximum possible score of 9.5 points.

The advanced features introduced these additional weights:

| Feature | Maximum points |
|---|---:|
| Popularity similarity | 0.5 |
| Release decade match | 0.5 |
| Mood tag similarity | 1.0 |
| Language match | 0.5 |
| Instrumentalness similarity | 0.5 |
| **Total additional points** | **3.0** |

Advanced preferences are optional. The original profiles continue using the original scoring system, while profiles specifying advanced preferences receive additional scoring opportunities.

### 4. Testing and Verification

The following tests were completed:

- Successfully loaded all 18 songs from the updated CSV.
- Verified that the five new attributes were parsed correctly.
- Tested the original three user profiles.
- Created an advanced High-Energy Pop profile using all five new attributes.
- Verified that the advanced profile's maximum possible score was 12.5.
- Confirmed that recommendations included explanations for advanced feature matches.

**Example result:** Sunrise City ranked first for Advanced High-Energy Pop with a score of 11.69/12.5.

### 5. What I Learned

This challenge helped me understand how adding more meaningful features can improve a recommendation system. I also learned how optional user preferences without breaking its original behavior.

AI assistance was useful for brainstorming, implementation guidance, and debugging, but I manually ran the program and verified the resulting recommendations and scores.

---

## Challenge 2: Strategy Pattern

### Objective

Refactor the recommendation system to support multiple recommendation strategies using object-oriented programming and the Strategy design pattern.

### 1. Strategies Implemented

Four recommendation strategies were added:

| Strategy | Description |
|---|---|
| `BalancedStrategy` | Uses balanced weights across recommendation features |
| `GenreFirstStrategy` | Gives greater importance to matching the user's favorite genre |
| `MoodFirstStrategy` | Gives greater importance to matching the user's preferred mood |
| `EnergyFirstStrategy` | Gives greater importance to matching the user's target energy level |

A shared `ScoringStrategy` class provides the scoring structure. Each strategy uses different feature weights to influence the final ranking.

### 2. AI Assistance

ChatGPT was used to:
- Understand the Strategy design pattern and how it applies to recommendation systems.
- Plan the strategy class structure.
- Refactor the scoring logic into reusable classes.
- Implement the four recommendation strategies.
- Add the ability to change the active strategy using `set_strategy()`.
- Troubleshoot implementation issues while preserving the existing function-based API.

### 3. Implementation

The `Recommender` class accepts a strategy object and uses it to rank songs. The active strategy can be changed without rewriting the recommendation logic.

The existing functions, including `score_song()` and `recommend_songs()`, were preserved so the original application could continue working.

This design separates the recommendation process from the scoring weights. It makes the system easier to extend because a new strategy can be added without rewriting the entire recommender.

### 4. Testing and Verification

The following tests and experiments were completed:

- Tested all four strategies using the same songs and user profile.
- Compared the rankings produced by each strategy.
- Verified that different strategies could produce different recommendation orders.
- Confirmed that the application still ran successfully.
- Ran the automated test suite successfully: **2 tests passed**.

**Example results:**

| Strategy | First recommended song |
|---|---|
| Genre First | Pop Track |
| Mood First | Happy Rock |
| Energy First | Pop Track |
| Balanced | Pop Track |

The Mood First strategy ranked Happy Rock first, while Genre First ranked Pop Track first. This demonstrated how changing feature weights can influence recommendation results.

### 5. What I Learned

This challenge helped me understand how the Strategy design pattern can make a recommendation system more flexible and maintainable. I learned how to use classes and objects to separate scoring behavior from the main recommendation process.

I also learned that different recommendation strategies can use the same underlying features but prioritize them differently. This allows a system to support different recommendation approaches without duplicating the entire algorithm.

AI assistance helped me understand the design pattern, organize the implementation, and debug issues. I tested the strategies and verified the application and automated tests myself.


---

## Project Development Log — AI Collaboration Reflection

### How AI contributed to development

AI assistance was used throughout the development of VibeFinder 2.0 to brainstorm the architecture, explain implementation choices, generate code suggestions, troubleshoot errors, and design tests.

The main development discussions focused on:

- Integrating Gemini to translate natural-language music requests into structured preferences.
- Preserving the original deterministic recommendation engine rather than allowing an LLM to invent songs or recommendation scores.
- Designing a reliability layer to enforce explicit user constraints before ranking.
- Creating automated tests for successful recommendations, invalid matches, and ambiguous requests.

### Important design decisions

**1. Separating language understanding from recommendation ranking**

We chose to use Gemini for understanding user intent and generating structured preferences. The existing Python recommendation engine remains responsible for scoring and ranking songs.

This separation makes recommendation results more predictable and easier to test.

**2. Adding deterministic constraint filtering**

The original recommendation engine was designed to rank songs based on similarity. It did not guarantee that every explicit user restriction would be enforced.

AI assistance helped identify this limitation and design a separate reliability component to filter ineligible songs before ranking.

**3. Using mocked tests**

Instead of depending on live Gemini API calls for every test, we introduced mocked components to test the agent's decision-making independently.

This makes testing faster, more reproducible, and less dependent on API availability.

### Debugging and human verification

During reliability testing, one test initially failed because the expected number of low-energy songs was incorrect. The implementation correctly returned eight songs, while the test expected nine.

We inspected the actual catalog values and corrected the test expectation rather than changing working filtering logic.

The agent and reliability components were also tested independently and together.

The human developer reviewed generated code, executed terminal commands, inspected outputs, and verified the test results.

### AI suggestions accepted and revised

- **Accepted:** Using structured JSON preference extraction instead of relying on free-form LLM responses.
- **Accepted:** Keeping recommendation scoring deterministic and separate from Gemini.
- **Accepted:** Adding a reliability layer to enforce explicit constraints.
- **Revised:** The initial low-energy test expectation was corrected after checking the actual dataset.
- **Deferred:** Building a more complex retrieval infrastructure until the core recommendation pipeline and documentation are complete.

### Limitations and future improvements

- The current music catalog contains only 18 songs, limiting recommendation diversity.
- Constraint interpretation currently supports a limited set of explicit phrases.
- Instrumentalness and low-energy thresholds are engineering choices that need further evaluation.
- Gemini responses may introduce latency or become unavailable.
- The current system does not yet have a large-scale retrieval index or extensive real-user evaluation.
- Future improvements include expanding the music catalog, improving retrieval, supporting more natural-language constraints, and evaluating recommendation quality with a larger test dataset.

### Human responsibility

AI-generated code and suggestions were treated as assistance rather than automatically accepted solutions. The developer remained responsible for reviewing implementation decisions, running tests, checking outputs, and determining whether the system behaved as intended.