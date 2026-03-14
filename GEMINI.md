Before any code edit, use the Repomix MCP tool to gather **targeted context**. 

### Rule for Token Efficiency:
1. **Targeted Context**: Use the `--include` flag to specify only files relevant to the current task (e.g., `src/app.py,templates/*.html`).
2. **Minimize Footprint**: Always ignore `data/`, `tests/**/*.html`, and large assets. Use the `--compress` flag for a structural overview if needed.
3. **Update Map**: After edits, update the codebase context or code map to ensure accurate future planning.

### Agent Behavioral Policy:
- **Automatic Awareness**: I read this file automatically at the start of every session; do not remind me to use Repomix in your prompts.
- **Self-Triggering**: I will trigger Repomix autonomously ONLY when logically required (e.g., starting a new feature, complex debugging, or architectural changes).
- **Token Safety**: For small talk, simple questions, or minor 1-line fixes, I will explicitly SKIP Repomix to save your tokens.
### Rule for documentation:
- keep add data you generate like plan and walkthrough in markdown files each in the corresponding file  in project root for future need documents.
- use project docs at first to know details of the project and if files is very long use Repomix MCP tool to help for token saving and general overview.
