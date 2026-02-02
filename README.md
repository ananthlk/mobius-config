# mobius-config

Shared credential and env configuration for Mobius modules. Each app repo (mobius-chat, mobius-os, mobius-rag, mobius-dbt) can run standalone with its own `.env`; this repo is the **canonical** place to define and inject shared credentials when working across modules.

**Helper:** `env_helper.load_env(module_root)` — check env in *my* (module) environment first; if a variable isn’t set there, use global. One function, any module. `GOOGLE_APPLICATION_CREDENTIALS`: placeholders (e.g. `/path/to/your-service-account.json`) are ignored; if unset or invalid, env_helper looks for the first `*.json` in the module’s `credentials/` or `mobius-config/credentials/`.

## Layout

- **`credentials/`** — Put shared credential files here (e.g. GCP service account JSON). Gitignored except README. In `.env` set full path to the key so modules never reference other folders.
- **`.env.example`** — Canonical list of env vars used by all modules. Copy to `.env` and fill in values; never commit `.env`.
- **`inject_env.sh`** — Copy this repo’s `.env` (or `.env.example`) into a target module’s directory so that module picks it up when run from its root.
- **`run_with_shared_env.sh`** — Source this repo’s `.env` and run a command (e.g. start one of the apps). Use when you want one shared `.env` and don’t want to copy into each repo.

## Prerequisites

- Repos are siblings under a common parent (e.g. `Mobius/mobius-config`, `Mobius/mobius-chat`, …).
- You have created `.env` from `.env.example` and set your secrets.

## Usage

### Option 1: Inject .env into a module

From this directory:

```bash
# Copy .env into mobius-chat (so mobius-chat/.env exists)
./inject_env.sh mobius-chat

# Copy into mobius-rag
./inject_env.sh mobius-rag

# Copy into mobius-dbt
./inject_env.sh mobius-dbt

# Copy into mobius-os backend
./inject_env.sh mobius-os/backend
```

Then run the app from **that module’s root** (e.g. `cd ../mobius-chat && ./mchatc`). The app will load its `.env` as usual.

### Option 2: Run a module with shared env (no copy)

Source this repo’s `.env` and run a command:

```bash
# Start mobius-chat API (from mobius-config dir)
./run_with_shared_env.sh ../mobius-chat ./mchatc

# Start mobius-chat worker
./run_with_shared_env.sh ../mobius-chat ./mchatcw

# Start mobius-rag backend
./run_with_shared_env.sh ../mobius-rag ./start_backend.sh

# Run dbt (from mobius-dbt root)
./run_with_shared_env.sh ../mobius-dbt ./scripts/land_and_dbt_run.sh
```

The script `cd`s into the given directory, then sources `mobius-config/.env`, then runs the rest of the arguments. So the app runs from its **own repo root** with env vars from mobius-config.

### Option 3: Use each repo’s own .env

You can still keep a `.env` in each repo and run from that repo’s root. mobius-config is optional and for sharing one set of credentials across repos.

## Which vars go where

- **mobius-chat:** `CHAT_RAG_DATABASE_URL`, `VERTEX_*`, `GOOGLE_APPLICATION_CREDENTIALS`, queue/storage vars. See mobius-chat/docs/ENV.md.
- **mobius-os:** `POSTGRES_*_LOCAL` or `POSTGRES_*_CLOUD`, `DATABASE_MODE`, `GCP_*`, `FLASK_*`. Use `.env` in `mobius-os/backend/`.
- **mobius-rag:** `DATABASE_URL`, `GCS_BUCKET`, `VERTEX_*`, `GOOGLE_APPLICATION_CREDENTIALS`. See mobius-rag/.env.example.
- **mobius-dbt:** `POSTGRES_*` (RAG read), `CHAT_DATABASE_URL` (Chat write), `BQ_*`, `VERTEX_*`. See mobius-dbt/.env.example.

Many vars (e.g. `VERTEX_PROJECT_ID`, `GOOGLE_APPLICATION_CREDENTIALS`) are shared; one `.env` in mobius-config can supply them for all.

### RAG shows “I don’t have access to our materials right now”

Chat RAG needs three vars set (in mobius-config/.env or mobius-chat/.env):

1. **CHAT_RAG_DATABASE_URL** — Already in `.env.example`. Same DB as dbt’s `CHAT_DATABASE_URL` (published_rag_metadata).
2. **VERTEX_INDEX_ENDPOINT_ID** — From GCP: Vertex AI → Vector Search → Index Endpoints → your endpoint → copy the resource name (e.g. `projects/mobiusos-new/locations/us-central1/indexEndpoints/123...`).
3. **VERTEX_DEPLOYED_INDEX_ID** — Same page → **Deployed indexes** table → **ID** column (e.g. `endpoint_mobius_chat_publi_1769989702095`).

Copy `mobius-config/.env.example` to `mobius-config/.env`, uncomment and fill the two Vertex vars, then run `./inject_env.sh mobius-chat` or restart chat so it loads the updated env.
