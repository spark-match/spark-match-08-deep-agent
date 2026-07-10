# Changelog

All notable changes to the **Spark Match Deep Agent** are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added (PR #6 — Sprint 2 + correcciones pre-existentes)

- **FIX-1 — AG-UI endpoint migration**: replaced deprecated `create_endpoint(agent)` with `LangGraphAgent` wrapper + manual `/ag-ui` endpoint that uses `EventEncoder` + `RunAgentInput`. The new endpoint reads `thread_id` from the request body and uses it as the active session for budget tracking.
- **FIX-2 — mypy strict clean**: resolved 16 pre-existing mypy errors (was 18 → now 0):
  - Added `Career` and `AffinityResult` TypedDicts in `src/tools/catalog.py` and `src/tools/matching.py` to replace generic `dict[str, object]` / `list[dict]`.
  - Annotated `create_spark_agent()` return type as `CompiledStateGraph[Any, Any, Any, Any]`.
  - Added cast in `factory.py` to satisfy the `SubAgent` TypedDict contract.
  - Added return type annotation `-> object` on `create_profile_manager()`.
  - Added `[[tool.mypy.overrides]]` for `ag_ui_langgraph*`, `tavily*`, `langmem*`, `deepagents*` (lacking upstream py.typed markers).
  - Installed `types-PyYAML` dev dependency.
  - Fixed `StreamHandler` argument type in `src/utils/logging.py`.
- **§3.4 — Decoupled career catalog**: 10 careers moved from hard-coded Python `list[dict]` to Markdown files under `data/careers/` with YAML frontmatter. Added `Career` TypedDict, `load_career_catalog()`, `reload_career_catalog()`, `CATALOG_DIR` resolver. New `pyyaml>=6.0.3` dependency. Career body (description, resources) is now preserved for the planning subagent.
- **§4.2 — Web search budget guard**: per-session counter (`src/budget.py`) using `ContextVar` for active session. `web_search` tool now refuses calls beyond `settings.max_web_searches_per_session` (default 6) and returns a clear "budget exhausted" message instead of burning the Tavily quota. AG-UI endpoint calls `set_active_session(thread_id)` + `reset_session_budget(thread_id)` per request.
- **§5.3 — `__init__.py` re-exports**: top-level `src/__init__.py` now exports `create_spark_agent`, `Settings`, `get_settings`. `src/agent/__init__.py` and `src/config/__init__.py` have explicit re-exports for callers that prefer a flat import surface.
- **11 new tests in `tests/test_catalog.py`**: catalog loader on real `data/careers/` (count, uniqueness, RIASEC validity), parser edge cases (missing/malformed/incomplete frontmatter), cache invalidation.
- **6 new tests in `tests/test_budget.py`**: per-session counter, session isolation, active session context, default session id.
- **1 new test in `tests/test_tools.py`**: web search budget guard end-to-end.
- **Settings** gained `max_web_searches_per_session: int = 6` (env var `SPARK_MAX_WEB_SEARCHES_PER_SESSION`). Existing `max_turns` documented but enforcement deferred to Sprint 4 (post-model middleware).

### Changed

- **`src/tools/web_search.py`**: increments budget counter BEFORE performing the search (prevents retry storms on transient errors).
- **`src/tools/catalog.py`**: `search_careers` now also matches against `outlook` and `body` (description/resources), not just name/skills/field.
- **`src/api/app.py`**: registers `/ag-ui` and `/ag-ui/health` routes manually (not via `add_langgraph_fastapi_endpoint`) so we can hook the per-request budget reset.
- **`.env.example`**: added `SPARK_MAX_WEB_SEARCHES_PER_SESSION=6` and `SPARK_MAX_TURNS=50`.

### Fixed

- **AG-UI import error**: `from ag_ui_langgraph import create_endpoint` failed on `ag-ui-langgraph` 0.0.42 (the symbol was renamed). Now uses `LangGraphAgent` + manual endpoint following the new SDK API.
- **Type annotations**: `dict` → `dict[str, str]` / `dict[str, object]` where appropriate; `list[dict]` → `list[Career]` / `list[AffinityResult]`.
- **Sub-agent type mismatch**: factory now casts to `Sequence[SubAgent]` to satisfy deepagents' TypedDict contract.

## [0.2.0] - 2026-07-10 (PR #5 — Sprint 1)

### Added

- **Centralized logging** (`src/utils/logging.py`): idempotent `setup_logging()` with configurable level and quiet-down of noisy third-party loggers (`httpx`, `urllib3`). New `SPARK_LOG_LEVEL` env var (DEBUG/INFO/WARNING/ERROR/CRITICAL).
- **`Makefile`** with `help`, `qa`, `qa-fix`, `format-fix`, `lint-fix`, `format-check`, `lint-check`, `typecheck`, `test`, `test-cov`, `run-local`, `run-agentcore`, `run-debug`, `install`, `clean`. Fail-fast if `.env` is missing.
- **`.dockerignore`** for AgentCore container builds (excludes `.venv`, caches, secrets, IDE files, ML artifacts).
- **`SecretStr`** for `tavily_api_key` and `langsmith_api_key` in `Settings`. Web search now calls `get_secret_value()` for upstream auth. Logs and tracebacks no longer risk leaking API keys.
- **`LogLevel` StrEnum** in `Settings` (`log_level` field) with strict parsing.
- **Tests** (`tests/test_logging.py`): 7 cases covering idempotency, level changes, str/int/Logger inputs, third-party quiet-down, message emission.

### Changed

- **`.gitignore`** clarified: `uv.lock` and `.python-version` are explicitly documented as versioned (was previously listed as ignored, contradicting `git ls-files`).
- **`src/api/app.py` lifespan** now calls `setup_logging()` before constructing the agent and logs environment/model on startup/shutdown.

### Fixed

- **`.gitignore` contradiction**: lines 39 and 45 previously ignored `uv.lock` and `.python-version` while both files were tracked. Now consistent with `uv` best practices for applications.

## [0.1.0] - 2026-06-25

### Added

- Deep Agent coordinator with 3 subagents: `assessment`, `matching`, `planning`.
- AG-UI streaming endpoint at `POST /ag-ui` (FastAPI + sse-starlette).
- langmem-based `StudentProfile` extraction (`src/memory/profile_manager.py`).
- RIASEC assessment tool (`src/tools/assessment.py`) with weighted scoring.
- In-memory career catalog with 10 careers (`src/tools/catalog.py`).
- Affinity calculator (`src/tools/matching.py`) using positional RIASEC weighting.
- Web search tool (`src/tools/web_search.py`) with Tavily (primary) + DuckDuckGo (fallback).
- Bedrock (Claude Sonnet 4) as default LLM via `langchain-aws`.
- Unit tests for models and tools (`tests/test_models.py`, `tests/test_tools.py`).
- README with RIASEC model documentation, env config, troubleshooting.

[Unreleased]: https://github.com/spark-match/spark-match-08-deep-agent/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/spark-match/spark-match-08-deep-agent/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/spark-match/spark-match-08-deep-agent/releases/tag/v0.1.0