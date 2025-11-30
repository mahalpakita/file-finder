<!--
Guidance for AI coding agents working on this repository.
This file is intentionally concise and focused on what's immediately
discoverable in the workspace as of this commit.
-->

# Copilot / AI Agent Instructions

Purpose: help an AI coding agent be productive immediately in this repository.

- **Repository snapshot:** single-file project. Key file: `main.py` (currently empty).
- **Environment notes:** repository path contains spaces (`file finder`). Primary OS is Windows; default shell is PowerShell (`powershell.exe`).

What to assume before making changes
- This repo currently has no tests, no README, and no dependencies declared.
- Ask a clarifying question before making large design changes (e.g., adding packages, CI, or new top-level folders).

Practical editing rules (project-specific)
- When working with filesystem paths prefer `pathlib.Path` and avoid hard-coded backslashes. Example: `Path(r"C:\Users\My PC\...\myfile.txt")` or `Path.cwd() / 'relative'`.
- Be defensive about spaces in paths (the workspace path contains spaces). Always quote paths when generating PowerShell commands.
- Use standard CLI patterns if adding a script interface: `if __name__ == '__main__':` and `argparse` for options.

Developer workflows (what an agent can run/test locally)
- Run the script in PowerShell with: `python "main.py"` (quote path if needed).
- If you add dependencies, update a `requirements.txt` and include install/run hints in a short `README.md`.

Patterns & boundaries
- Single-file scripts belong at repository root (no package structure detected). If you split into modules, create a package folder and update imports to use relative imports.
- Keep changes minimal and focused: prefer adding small, self-contained features rather than a full refactor without user approval.

Integration points / external dependencies
- None detected. If you add external services (APIs, DBs), include clear environment-variable names and a `.env.example` file.

Commit / PR guidance
- Small, focused commits. Each PR should include a one-line summary and a short description of why the change was needed.
- When adding runtime requirements, include usage and quick run commands in `README.md`.

When unsure — ask the user
- Before introducing new directories, CI, or a dependency manager, prompt the repo owner for requirements and preferred Python versions.

Files to reference while editing
- `main.py` — entry point; inspect and modify here.

End of guidance.
