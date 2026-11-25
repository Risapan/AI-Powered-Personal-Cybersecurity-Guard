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
| D3 | Git workflow | One branch per purpose (`feat/...`, `fix/...`, `docs/...`, `chore/...`, `test/...`). Each is merged into `develop` when it's done and tested, and `develop` is merged into `main` at milestones |
| D4 | Push automation | Not set up yet. Pushes are done by hand for now |

## Branch naming

- `feat/<area>-<thing>`: new functionality, e.g. `feat/engine-url-normalization`
- `fix/<area>-<thing>`: bug fixes
- `test/<area>`: test-only work
- `docs/<topic>`: documentation
- `chore/<thing>`: tooling, config, cleanup

Branches are never force-pushed. Short-lived branches can be deleted after they're merged.

## Known risks

- Rust isn't installed, and Tauri depends on it (see D2).
- Python 3.15 is very new, so some packages might not ship wheels for it yet. If that becomes a problem, I'll pin versions or drop to 3.12/3.13.
