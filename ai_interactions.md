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

