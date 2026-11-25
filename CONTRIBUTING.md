# Contributing to Friday

Thanks for taking a look. Friday is a security tool, so the bar for changes is a bit higher than usual: every change should be tested, easy to review, and must not quietly collect or send data.

## Setup

You'll need:

- Python 3.12+ and [uv](https://docs.astral.sh/uv/)
- Node.js 22+ and npm
- [gitleaks](https://github.com/gitleaks/gitleaks) (`brew install gitleaks` on macOS)
- Optional: [Ollama](https://ollama.com) if you're working on AI explanations

```sh
git clone https://github.com/Risapan/AI-Powered-Personal-Cybersecurity-Guard.git friday
cd friday
./scripts/install-hooks.sh        # secret scan before every commit

cd engine && uv sync && cd ..     # Python tools
cd extension && npm ci && cd ..   # TypeScript tools
```

## Running the checks

```sh
./scripts/check.sh
```

This runs the secret scan, then ruff (format and lint), mypy and pytest for the engine, then Prettier, ESLint, tsc and Vitest for the extension. Run it before opening a PR. CI will run the same checks.

## Branches (Git Flow)

| Branch | Use it for |
|---|---|
| `main` | Released versions only. Don't commit here |
| `develop` | Where finished work comes together. Don't commit here directly either |
| `feature/FRI-<n>-<short-desc>` | A task, branched from `develop` |
| `bugfix/FRI-<n>-<short-desc>` | A fix for something not released yet |
| `release/<version>` | Getting a version ready |
| `hotfix/<version>-<short-desc>` | An urgent fix to a released version |

Each task has an ID (`FRI-<n>`), listed in [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md). Keep one task per branch, and put the code, tests and docs for it on the same branch.

## Commits

- Start the message with the task ID: `FRI-7: Add URL normalization`
- One logical change per commit. Don't make "fix typo" commits on a branch that isn't merged yet; fold them in instead
- Never commit secrets, `.env` files, local databases, or anything from a real browsing session

## Pull requests

- Open the PR against `develop`, and say what changed, why, and which checks you ran
- `./scripts/check.sh` must pass
- Merge with a merge commit, then delete the branch

## Security rules for code

These come from the [threat model](docs/THREAT_MODEL.md) and aren't optional:

- No `shell=True`, `eval`, `new Function`, or building commands out of strings
- Treat URLs, page titles, file names and LLM output as untrusted data
- Nothing leaves the machine unless the user has turned that feature on
- Don't log full URLs, tokens or personal data. Redact first
- Adding a new dependency needs a reason in the PR description

## Reporting a security issue

Please don't open a public issue for a vulnerability. Contact the maintainer privately through GitHub instead.
