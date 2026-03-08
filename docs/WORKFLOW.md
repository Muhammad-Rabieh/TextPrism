# TextPrism Development Workflow

This document defines the lifecycle of development, debugging, and documentation for TextPrism. Following this workflow ensures that any agent (AI or Human) can quickly understand the project state and contribute effectively.

## 🔄 The Development Cycle

1.  **Planning**: Research the codebase, identify dependencies, and create an `implementation_plan.md` (brain artifact).
2.  **Implementation**: Write clean, modular code. Use the virtual environment (`venv`).
3.  **Verification**: Conduct E2E tests (e.g., via Playwright) and unit tests.
4.  **Documentation**: Update `walkthrough.md` with proof of work and `task.md` for status.
5.  **Synchronization**: Ensure key changes are reflected in `docs/CODE_MAP.md` and `docs/PROGRESS.md`.

## 🕒 Timestamping Requirement

Every entry in the development history (tasks, walkthroughs, logs) MUST include a UTC/Local timestamp in the format `[YYYY-MM-DDTHH:MM:SS]`. This creates a chronological audit trail for debugging and feature tracking.

-   **Tasks**: Each bullet point in `task.md` should have a timestamp of when it was created or updated.
-   **Execution**: Log entries or command outputs should be referenced with time markers.

## 🗺️ Code Map Maintenance

Whenever a new module is added or a core component's logic changes significantly, `docs/CODE_MAP.md` must be updated to maintain an accurate architectural overview.

---
*Ensuring clarity for LLMs and Human collaborators alike.*
