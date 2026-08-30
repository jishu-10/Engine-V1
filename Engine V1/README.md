# Similarity Engine V1

Similarity Engine V1 is a standalone FastAPI backend for evidence-based people-to-people similarity. It implements the deterministic pipeline from the provided specification:

Curated MCQs -> deterministic signal mappings -> user signal profiles -> pairwise similarity -> structured evidence -> optional LLM explanation.

The LLM is never the source of truth. It only turns verified evidence into natural language, and the service works without it.

## What V1 Does

- Serves the 10 production onboarding prompts.
- Stores placeholder/test users and MCQ responses.
- Preserves prompt version with every response.
- Maps each selected option to deterministic signal observations.
- Aggregates observations into user signal profiles.
- Calculates signal-level, area-level, and overall similarity.
- Handles missing data by excluding it from comparison.
- Calculates area and overall evidence coverage separately from similarity.
- Stores traceable similarity evidence.
- Stores prompt/version snapshots on similarity results and evidence.
- Generates fallback explanations without an LLM.
- Supports an Anthropic-backed `LLMService` when configured.
- Exposes validation metrics for small human pilots.

## What V1 Does Not Do

V1 does not implement authentication, verification, dating UI, matching, likes, chat, communities, events, notifications, embeddings, recommendation models, complementarity, friction, relationship-success prediction, MBTI, Big Five scoring, attachment-style diagnosis, or clinical personality classification.

## Architecture

The code is layered so scoring logic does not live in routes:

- `app/api/routes`: REST endpoints under `/api/v1`
- `app/data/prompt_config.py`: V1 areas, signals, prompts, options, mappings
- `app/models.py`: SQLAlchemy schema
- `app/services/response_service.py`: response ingestion and observation creation
- `app/services/profile_service.py`: signal aggregation, confidence, completion
- `app/services/similarity_service.py`: deterministic comparison and evidence
- `app/services/llm_service.py`: provider-independent explanation layer
- `app/services/analytics_service.py`: validation/pilot metrics

## Technology Stack

Python, FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL, Pytest, Docker Compose, and GitHub Actions.

## Local Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

For Docker:

```powershell
docker compose up --build
```

The API will be available at `http://localhost:8000`, with OpenAPI docs at `http://localhost:8000/docs`.

## Environment Variables

Key settings:

- `DATABASE_URL`: SQLAlchemy database URL.
- `CREATE_TABLES_ON_STARTUP`: optional local-only table creation.
- `SEED_ON_STARTUP`: optional local-only prompt seeding.
- `ALGORITHM_VERSION`: defaults to `similarity_v1`.
- `ONTOLOGY_VERSION`: defaults to `1.0`.
- `MAPPING_VERSION`: defaults to `1.0`.
- `LLM_PROVIDER`: `disabled` or `anthropic`.
- `ANTHROPIC_API_KEY`: required only when using Anthropic.
- `ANTHROPIC_MODEL`: defaults to `claude-haiku-4-5`.

## Database Setup

With PostgreSQL running:

```powershell
.\.venv\Scripts\alembic upgrade head
.\.venv\Scripts\python -m app.seed
```

The seed is idempotent for the initial prompt/config set.

## Running The API

```powershell
.\.venv\Scripts\uvicorn app.main:app --reload
```

For a no-Postgres local smoke test, set a SQLite URL and enable startup setup:

```powershell
$env:DATABASE_URL = "sqlite:///./local.db"
$env:CREATE_TABLES_ON_STARTUP = "true"
$env:SEED_ON_STARTUP = "true"
.\.venv\Scripts\uvicorn app.main:app --reload
```

## API Endpoints

- `GET /api/v1/health`
- `POST /api/v1/users`
- `GET /api/v1/prompts/onboarding`
- `GET /api/v1/prompts/next?user_id=...`
- `POST /api/v1/responses`
- `GET /api/v1/responses?user_id=...`
- `GET /api/v1/profile?user_id=...`
- `GET /api/v1/profile/completion?user_id=...`
- `POST /api/v1/similarity/compare`
- `GET /api/v1/similarity/{result_id}`
- `POST /api/v1/similarity/{result_id}/explanation`
- `GET /api/v1/validation/metrics`

## Example Workflow

```powershell
curl -X POST http://localhost:8000/api/v1/users -H "Content-Type: application/json" -d "{\"id\":\"user_a\"}"
curl -X POST http://localhost:8000/api/v1/users -H "Content-Type: application/json" -d "{\"id\":\"user_b\"}"
curl http://localhost:8000/api/v1/prompts/onboarding
curl -X POST http://localhost:8000/api/v1/responses -H "Content-Type: application/json" -d "{\"user_id\":\"user_a\",\"prompt_id\":\"P01\",\"selected_option\":\"A\"}"
curl -X POST http://localhost:8000/api/v1/responses -H "Content-Type: application/json" -d "{\"user_id\":\"user_b\",\"prompt_id\":\"P01\",\"selected_option\":\"B\"}"
curl -X POST http://localhost:8000/api/v1/similarity/compare -H "Content-Type: application/json" -d "{\"user_a_id\":\"user_a\",\"user_b_id\":\"user_b\"}"
```

## Deterministic Engine

Signal values use the spec's normalized `[-1, +1]` scale. Signal similarity is calculated as:

```text
1 - abs(value_a - value_b) / 2
```

Area scores are confidence-weighted averages of comparable primary signals. Overall score is an area-weighted average using:

- Values & Priorities: `0.30`
- Communication & Social: `0.30`
- Interests & Lifestyle: `0.15`
- Connection Style: `0.25`

Missing signals are excluded. Observed zero values are kept as real midpoint evidence.

## Versioning Strategy

Responses store prompt version. Similarity results store algorithm, ontology, mapping, LLM prompt version, and a per-user prompt-version snapshot. Evidence rows also snapshot the prompt ID, option key, and prompt version for both people. This keeps historical results explainable when prompts, mappings, or later responses change.

## LLM Configuration

The standard engine path does not need an LLM. To enable Anthropic:

```powershell
$env:LLM_PROVIDER = "anthropic"
$env:ANTHROPIC_API_KEY = "..."
```

If the provider fails, returns malformed JSON, references unknown evidence, or introduces unsupported claims, the backend stores a deterministic fallback explanation instead.

## Running Tests

```powershell
.\.venv\Scripts\python -m pytest
```

The standard test suite uses SQLite and mocks/fakes LLM behavior. It does not make real LLM calls.

## Assumptions

The extracted document omitted rendered formulas, so the implementation uses the formulas implied by the examples and prose: distance-over-range signal similarity, confidence-weighted area averages, area-weighted overall similarity, and separately area-weighted evidence coverage. Auxiliary axes from P01 and P04 are seeded and observed, but marked non-primary so they do not drive V1 similarity.

## Future Campus Chemistry Integration

This service is ready to sit behind a future app layer. Authentication, real authorization, profile UI, discovery, matching, chat, notifications, and richer compatibility components can be added around this engine without letting those features rewrite the deterministic measurement layer.
