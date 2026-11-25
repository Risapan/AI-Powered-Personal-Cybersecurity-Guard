# Friday: Roadmap

This is the rough order I plan to build Friday in. The scope and requirements are in [REQUIREMENTS.md](REQUIREMENTS.md).

## Phases

| Phase | What gets built | Done when |
|---|---|---|
| 1. Foundations | Architecture and threat model, tooling, data schemas, SQLite storage, URL checks, risk scoring | Everything is covered by tests |
| 2. Browser + local AI | Chrome extension (Manifest V3) talking to the local engine; explanations from Ollama | URL checks work end to end, and still work with the AI turned off |
| 3. Desktop app + intel | Dashboard, history, notifications, optional reputation lookups, checking a file you pick | You can review findings and change settings in the app |
| 4. Hardening + release | Extension permission review, read-only system views, security checklist, incident reports, CI, docs | Release candidate passes the acceptance criteria |

## Planned layout

```
engine/      Python: detection, risk scoring, storage, intel and LLM adapters, local API
extension/   TypeScript: Chrome extension
desktop/     Desktop app (Tauri + React + TypeScript)
docs/        Requirements, architecture, threat model, privacy notes
```

## Decisions

| | Decision | Choice |
|---|---|---|
| D1 | License | Apache-2.0 |
| D2 | Desktop shell | Tauri is the plan. It needs a Rust toolchain, which isn't installed yet. The fallback is a local web UI served by the engine |
| D3 | Git workflow | Git Flow (see below) |
| D4 | Push automation | Not set up yet. Pushes are done by hand for now |

## Git workflow (Git Flow)

| Branch | Purpose | Branches off | Merges into |
|---|---|---|---|
| `main` | Released versions only. Every merge is tagged (`v0.1.0`, ...) | | |
| `develop` | Integration branch; always builds and passes tests | `main` | `release/*` |
| `feature/FRI-<n>-<desc>` | One task, e.g. `feature/FRI-4-url-engine` | `develop` | `develop` |
| `bugfix/FRI-<n>-<desc>` | A fix for something not released yet | `develop` | `develop` |
| `release/<version>` | Stabilising a version: final fixes, docs, version bump | `develop` | `main` and `develop` |
| `hotfix/<version>-<desc>` | An urgent fix to a released version | `main` | `main` and `develop` |

Rules:

- Every task has an ID (`FRI-<n>`). It goes in the branch name and at the start of each commit message, e.g. `FRI-4: Normalize IDN hostnames`.
- One branch per task, not per file. Code, tests and docs for a task go on the same branch.
- Everything reaches `develop` and `main` through a pull request. Nobody commits to them directly.
- A PR is merged only when its checks pass. The branch is deleted after merging.
- No force pushes to shared branches.

## Tasks

| ID | Task |
|---|---|
| FRI-1 | Project setup (README, .gitignore, license) |
| FRI-2 | Requirements and roadmap |
| FRI-3 | Architecture and threat model |
| FRI-4 | Python engine tooling (ruff, mypy, pytest) |
| FRI-5 | Extension tooling (TypeScript, ESLint, Prettier, Vitest) |
| FRI-6 | Repo hygiene: editorconfig, secret scanning, check script, contributing guide |

New tasks are added here as they start.

## Known risks

- Rust isn't installed, and Tauri depends on it (see D2).
- Python 3.15 is very new, so some packages might not ship wheels for it yet. If that becomes a problem, I'll pin versions or drop to 3.12/3.13.
