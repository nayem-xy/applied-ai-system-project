# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

<!-- Describe the goal you asked the agent to accomplish -->

**Prompts used:**

<!-- Paste the key prompts you gave the agent -->

**What did the agent generate or change?**

<!-- List the files edited, code generated, or commands run -->

**What did you verify or fix manually?**

<!-- Describe anything the agent got wrong or that required human review -->

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

<!-- e.g., Strategy, Factory, Observer, etc. -->

**How did AI help you brainstorm or implement it?**

<!-- Describe the conversation or suggestions that led to your decision -->

**How does the pattern appear in your final code?**

<!-- Point to the relevant class or method -->

---

## Project Development Log — Stage 0 Baseline

**Date:** November 15, 2026

### Environment setup
- Created and activated a local Python virtual environment: `.venv`.
- Upgraded pip.
- Installed project dependencies from `requirements.txt`.
- Confirmed the environment uses Python 3.14.2.

### Baseline verification
- Ran `python -m pytest -q`: **2 tests passed**.
- Ran `python -m src.main`: successfully loaded all 18 songs.
- Confirmed recommendations were generated for four profiles:
  - High-Energy Pop
  - Chill Lofi
  - Deep Intense Rock
  - Advanced High-Energy Pop
- Confirmed the original scoring strategies and recommendation explanations still work.

### Human verification
Reviewed the terminal output and confirmed that the original recommendation engine runs successfully in the new repository environment.

### Baseline conclusion
VibeFinder 1.0 is functional in the new Applied AI project repository. This verified version will serve as the baseline for evaluating VibeFinder 2.0.

## Agentic Workflow Enhancement

We extended the original recommendation agent with a conditional planning and tool-execution architecture.

### Components Added

- `src/agent_planner.py`: Creates execution plans from extracted preferences.
- `src/agent_tools.py`: Provides catalog inspection, filtering, ranking, and validation tools.
- `src/agent.py`: Coordinates execution and records structured traces.

### Planning Decisions

The planner determines whether clarification is needed and whether explicit restrictions require catalog filtering.

Examples:

- Ambiguous requests take the clarification path.
- Instrumental-only requests trigger catalog inspection and filtering.
- Unrestricted requests use the full catalog.
- Requests with no eligible matches stop before ranking.
- Valid recommendations pass through a validation step.

### Execution Traces

Execution steps are recorded in `logs/agentic_traces.jsonl`. These traces demonstrate successful recommendations, no-match handling, and clarification behavior.

### Verification

- 8 agent tests passed.
- 17 tests passed across the complete project.
- Agent, planner, and tool modules passed Python compilation.

## Few-Shot Prompt Specialization

We added a `prompt_style` option to the preference parser:

- `baseline`
- `specialized`

The specialized prompt includes examples covering instrumental music, decade restrictions, and ambiguous requests.

We created `src/compare_prompts.py` to compare both prompt configurations.

### Experiment Limitations

The baseline completed 13 out of 13 evaluated checks in the recorded run. The specialized run encountered Gemini 503 service-unavailable errors, preventing a reliable comparison.

We therefore do not claim that few-shot specialization improved measured accuracy. More successful repeated runs are needed.

This work changes the prompt, not the underlying model weights. It is prompt specialization rather than model fine-tuning.

## Human Review and Verification

The developer reviewed the architecture, inspected generated code, ran automated tests, and examined execution traces. AI-generated suggestions were treated as development assistance and were verified rather than automatically accepted.