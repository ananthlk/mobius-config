# Mobius Environment Variables Matrix

This document defines the canonical environment variables for each service across all environments.  
**Source of Truth**: Production (`mobiusos-new`)

---

## GCP Project & Resource Naming Convention

### Project IDs (Immutable)

| Environment | GCP Project ID | Display Name |
|-------------|----------------|--------------|
| **Production** | `mobiusos-new` | MobiusOS - Production |
| **Staging** | `mobius-staging-mobius` | MobiusOS - Staging |
| **Dev** | `mobius-os-dev` | MobiusOS - Dev |

### Resource Naming Convention

All resources should follow: `mobius-{resource}-{env}` pattern. Isolation is achieved via **project ID**, not resource name suffix.

| Resource Type | Production (`mobiusos-new`) | Staging (`mobius-staging-mobius`) | Dev (`mobius-os-dev`) |
|---------------|------------|---------|-----|
| **Cloud SQL** | `mobius-platform-db` | `mobius-platform-staging-db` | `mobius-platform-dev-db` |
| **Redis** | `mobius-redis` (10.30.217.227) | `mobius-staging-redis` (10.121.0.3) | `mobius-dev-redis` |
| **GCS Bucket (RAG)** | `mobius-rag-uploads-mobiusos` | `mobius-rag-uploads-staging` | `mobius-rag-uploads-dev` |
| **GCS Bucket (Vertex)** | `mobiusos-new-vertex-index` | `mobius-staging-vertex-index` | `mobius-dev-vertex-index` |
| **BigQuery Landing** | `landing_rag` | `landing_rag` | `landing_rag` |
| **BigQuery Mart** | `mobius_rag` | `mobius_rag` | `mobius_rag` |
| **Vertex AI Index Endpoint** | `4513040034206580736` | `6304346785993195520` | TBD |
| **Service Account** | `mobius-platform-sa@...` | `mobius-platform-staging@...` | `mobius-platform-dev@...` |
| **VPC Connector** | `mobius-redis-connector` | `mobius-staging-vpc-connector` | `mobius-dev-vpc-connector` |

### Current Resource Inventory

#### Production (`mobiusos-new`) - COMPLETE
| Resource | Name | Status |
|----------|------|--------|
| Cloud SQL | `mobius-platform-db` | Active |
| Cloud SQL | `mobius-db` | Active (legacy) |
| Redis | `mobius-redis` (10.30.217.227) | Active |
| GCS | `mobius-rag-uploads-mobiusos` | Active |
| GCS | `mobiusos-new-vertex-index` | Active |
| BigQuery | `landing_rag.rag_published_embeddings` | Active |
| BigQuery | `mobius_rag.sync_runs` | Active |
| BigQuery | `mobius_rag.published_rag_embeddings` | Created by dbt run |
| Cloud Run | 10 services | Active |

#### Staging (`mobius-staging-mobius`) - COMPLETE
| Resource | Name | Status |
|----------|------|--------|
| Cloud SQL | `mobius-platform-staging-db` | Active |
| Redis | `mobius-staging-redis` (10.121.0.3) | Active |
| GCS | `mobius-rag-uploads-staging` | Active |
| BigQuery | `landing_rag.rag_published_embeddings` | Active |
| BigQuery | `mobius_rag.sync_runs` | Active |
| BigQuery | `mobius_rag.published_rag_embeddings` | Created by dbt run |
| Cloud Run | 10 services | Active |

#### Dev (`mobius-os-dev`) - NEEDS SETUP
| Resource | Target Name | Status |
|----------|-------------|--------|
| Cloud SQL | `mobius-platform-dev-db` (34.135.72.145) | Active |
| Redis | `mobius-dev-redis` (10.40.102.67) | Active |
| GCS | `mobius-rag-uploads-dev` | Active |
| GCS | `mobius-dev-vertex-index` | Active |
| BigQuery | `landing_rag.rag_published_embeddings` | Active |
| BigQuery | `mobius_rag.sync_runs` | Active |
| BigQuery | `mobius_rag.published_rag_embeddings` | Created by dbt run |
| VPC Connector | `mobius-dev-vpc-connector` (10.9.0.0/28) | Active |
| Service Account | `mobius-platform-dev@mobius-os-dev.iam.gserviceaccount.com` | Active |
| Cloud Run | 10 services | **TO CREATE** |

---

## Environment-Specific Values

| Variable | Dev (`mobius-os-dev`) | Staging (`mobius-staging-mobius`) | Production (`mobiusos-new`) |
|----------|----------------------|-----------------------------------|----------------------------|
| `GCP_PROJECT_ID` | `mobius-os-dev` | `mobius-staging-mobius` | `mobiusos-new` |
| `CLOUDSQL_INSTANCE` | `mobius-os-dev:us-central1:mobius-platform-dev-db` | `mobius-staging-mobius:us-central1:mobius-platform-staging-db` | `mobiusos-new:us-central1:mobius-platform-db` |
| `REDIS_IP` | `10.40.102.67` | `10.121.0.3` | `10.30.217.227` |
| `GCS_BUCKET` | `mobius-rag-uploads-dev` | `mobius-rag-uploads-staging` | `mobius-rag-uploads-mobiusos` |
| `VERTEX_INDEX_ENDPOINT_ID` | `projects/mobius-os-dev/locations/us-central1/indexEndpoints/156370344679047168` | `projects/mobius-staging-mobius/locations/us-central1/indexEndpoints/6304346785993195520` | `projects/mobiusos-new/locations/us-central1/indexEndpoints/4513040034206580736` |
| `VERTEX_DEPLOYED_INDEX_ID` | `mobius_chat_dev` (deploying) | `mobius_chat_staging_1770153134390` | `endpoint_mobius_chat_publi_1769989702095` |

---

## Service: mobius-chat-api

| Variable | Required | Dev (`mobius-os-dev`) | Staging (`mobius-staging-mobius`) | Production (`mobiusos-new`) |
|----------|----------|----------------------|-----------------------------------|----------------------------|
| `CHAT_RAG_DATABASE_URL` | Yes | `postgresql://postgres:{pwd}@/mobius_chat?host=/cloudsql/mobius-os-dev:us-central1:mobius-platform-dev-db` | `postgresql://mobius_app:{pwd}@/mobius_chat?host=/cloudsql/mobius-staging-mobius:us-central1:mobius-platform-staging-db` | `postgresql://postgres:{pwd}@/mobius_chat?host=/cloudsql/mobiusos-new:us-central1:mobius-platform-db` |
| `QUEUE_TYPE` | Yes | `redis` | `redis` | `redis` |
| `REDIS_URL` | Yes | `redis://10.40.102.67:6379/0` | `redis://10.121.0.3:6379/0` | `redis://10.30.217.227:6379/0` |
| `VERTEX_PROJECT_ID` | Yes | `mobius-os-dev` | `mobius-staging-mobius` | `mobiusos-new` |
| `VERTEX_LOCATION` | Yes | `us-central1` | `us-central1` | `us-central1` |
| `JWT_SECRET` | Yes | (Secret Manager: `jwt-secret`) | (Secret Manager: `jwt-secret`) | (Secret Manager: `jwt-secret`) |
| `MOBIUS_OS_AUTH_URL` | No | `https://mobius-os-backend-xxx.run.app` | `https://mobius-os-backend-xxx.run.app` | `https://mobius-os-backend-xxx.run.app` |
| `RAG_APP_API_BASE` | No | `https://mobius-rag-xxx.run.app` | `https://mobius-rag-xxx.run.app` | `https://mobius-rag-xxx.run.app` |

---

## Service: mobius-chat-worker

| Variable | Required | Dev (`mobius-os-dev`) | Staging (`mobius-staging-mobius`) | Production (`mobiusos-new`) |
|----------|----------|----------------------|-----------------------------------|----------------------------|
| `CHAT_RAG_DATABASE_URL` | Yes | `postgresql://postgres:{pwd}@/mobius_chat?host=/cloudsql/mobius-os-dev:us-central1:mobius-platform-dev-db` | `postgresql://mobius_app:{pwd}@/mobius_chat?host=/cloudsql/mobius-staging-mobius:us-central1:mobius-platform-staging-db` | `postgresql://postgres:{pwd}@/mobius_chat?host=/cloudsql/mobiusos-new:us-central1:mobius-platform-db` |
| `QUEUE_TYPE` | Yes | `redis` | `redis` | `redis` |
| `REDIS_URL` | Yes | `redis://10.40.102.67:6379/0` | `redis://10.121.0.3:6379/0` | `redis://10.30.217.227:6379/0` |
| `VERTEX_PROJECT_ID` | Yes | `mobius-os-dev` | `mobius-staging-mobius` | `mobiusos-new` |
| `VERTEX_LOCATION` | Yes | `us-central1` | `us-central1` | `us-central1` |
| `VERTEX_MODEL` | Yes | `gemini-2.5-flash` | `gemini-2.5-flash` | `gemini-2.5-flash` |
| `LLM_PROVIDER` | Yes | `vertex` | `vertex` | `vertex` |
| `VERTEX_INDEX_ENDPOINT_ID` | Yes | `projects/mobius-os-dev/locations/us-central1/indexEndpoints/{TBD}` | `projects/mobius-staging-mobius/locations/us-central1/indexEndpoints/{TBD}` | `projects/mobiusos-new/locations/us-central1/indexEndpoints/4513040034206580736` |
| `VERTEX_DEPLOYED_INDEX_ID` | Yes | `{TBD}` | `mobius_chat_staging_1770153134390` | `endpoint_mobius_chat_publi_1769989702095` |
| `JWT_SECRET` | Yes | (Secret Manager: `jwt-secret`) | (Secret Manager: `jwt-secret`) | (Secret Manager: `jwt-secret`) |
| `GOOGLE_APPLICATION_CREDENTIALS` | Local dev only | `/path/to/credentials.json` | N/A (uses SA) | N/A (uses SA) |

---

## Service: mobius-rag

| Variable | Required | Dev (`mobius-os-dev`) | Staging (`mobius-staging-mobius`) | Production (`mobiusos-new`) |
|----------|----------|----------------------|-----------------------------------|----------------------------|
| `DATABASE_URL` | Yes | `postgresql+asyncpg://postgres:{pwd}@/mobius_rag?host=/cloudsql/mobius-os-dev:us-central1:mobius-platform-dev-db` | `postgresql+asyncpg://mobius_app:{pwd}@/mobius_rag?host=/cloudsql/mobius-staging-mobius:us-central1:mobius-platform-staging-db` | `postgresql+asyncpg://postgres:{pwd}@/mobius_rag?host=/cloudsql/mobiusos-new:us-central1:mobius-platform-db` |
| `GCS_BUCKET` | Yes | `mobius-rag-uploads-dev` | `mobius-rag-uploads-staging` | `mobius-rag-uploads-mobiusos` |
| `VERTEX_PROJECT_ID` | Yes | `mobius-os-dev` | `mobius-staging-mobius` | `mobiusos-new` |
| `VERTEX_LOCATION` | Yes | `us-central1` | `us-central1` | `us-central1` |
| `VERTEX_MODEL` | Yes | `gemini-1.5-pro` | `gemini-1.5-pro` | `gemini-1.5-pro` |
| `LLM_PROVIDER` | Yes | `vertex` | `vertex` | `vertex` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Local dev only | `/path/to/credentials.json` | N/A (uses SA) | N/A (uses SA) |
| `ENV` | No | `dev` | `staging` | `prod` |

---

## Service: mobius-rag-chunking-worker

| Variable | Required | Dev (`mobius-os-dev`) | Staging (`mobius-staging-mobius`) | Production (`mobiusos-new`) |
|----------|----------|----------------------|-----------------------------------|----------------------------|
| `ENV` | Yes | `dev` | `staging` | `prod` |
| `DATABASE_URL` | Yes | `postgresql+asyncpg://postgres:{pwd}@/mobius_rag?host=/cloudsql/mobius-os-dev:us-central1:mobius-platform-dev-db` | `postgresql+asyncpg://mobius_app:{pwd}@/mobius_rag?host=/cloudsql/mobius-staging-mobius:us-central1:mobius-platform-staging-db` | `postgresql+asyncpg://postgres:{pwd}@/mobius_rag?host=/cloudsql/mobiusos-new:us-central1:mobius-platform-db` |
| `GCS_BUCKET` | Yes | `mobius-rag-uploads-dev` | `mobius-rag-uploads-staging` | `mobius-rag-uploads-mobiusos` |
| `VERTEX_PROJECT_ID` | Yes | `mobius-os-dev` | `mobius-staging-mobius` | `mobiusos-new` |
| `VERTEX_LOCATION` | Yes | `us-central1` | `us-central1` | `us-central1` |
| `VERTEX_MODEL` | Yes | `gemini-1.5-pro` | `gemini-1.5-pro` | `gemini-1.5-pro` |
| `LLM_PROVIDER` | Yes | `vertex` | `vertex` | `vertex` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Local dev only | `/path/to/credentials.json` | N/A (uses SA) | N/A (uses SA) |

---

## Service: mobius-rag-embedding-worker

| Variable | Required | Dev (`mobius-os-dev`) | Staging (`mobius-staging-mobius`) | Production (`mobiusos-new`) |
|----------|----------|----------------------|-----------------------------------|----------------------------|
| `ENV` | Yes | `dev` | `staging` | `prod` |
| `DATABASE_URL` | Yes | `postgresql+asyncpg://postgres:{pwd}@/mobius_rag?host=/cloudsql/mobius-os-dev:us-central1:mobius-platform-dev-db` | `postgresql+asyncpg://mobius_app:{pwd}@/mobius_rag?host=/cloudsql/mobius-staging-mobius:us-central1:mobius-platform-staging-db` | `postgresql+asyncpg://postgres:{pwd}@/mobius_rag?host=/cloudsql/mobiusos-new:us-central1:mobius-platform-db` |
| `GCS_BUCKET` | Yes | `mobius-rag-uploads-dev` | `mobius-rag-uploads-staging` | `mobius-rag-uploads-mobiusos` |
| `VERTEX_PROJECT_ID` | Yes | `mobius-os-dev` | `mobius-staging-mobius` | `mobiusos-new` |
| `VERTEX_LOCATION` | Yes | `us-central1` | `us-central1` | `us-central1` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Local dev only | `/path/to/credentials.json` | N/A (uses SA) | N/A (uses SA) |

---

## Service: mobius-skills-scraper-api

| Variable | Required | Dev (`mobius-os-dev`) | Staging (`mobius-staging-mobius`) | Production (`mobiusos-new`) |
|----------|----------|----------------------|-----------------------------------|----------------------------|
| `REDIS_URL` | Yes | `redis://10.40.102.67:6379/0` | `redis://10.121.0.3:6379/0` | `redis://10.30.217.227:6379/0` |
| `GCS_BUCKET` | Yes | `mobius-rag-uploads-dev` | `mobius-rag-uploads-staging` | `mobius-rag-uploads-mobiusos` |
| `SCRAPER_REQUEST_KEY` | No | `mobius:scraper:requests` | `mobius:scraper:requests` | `mobius:scraper:requests` |
| `SCRAPER_RESPONSE_KEY_PREFIX` | No | `mobius:scraper:response:` | `mobius:scraper:response:` | `mobius:scraper:response:` |
| `SCRAPER_RESPONSE_TTL_SECONDS` | No | `3600` | `3600` | `3600` |
| `TREE_MAX_DEPTH` | No | `3` | `3` | `3` |
| `TREE_MAX_PAGES` | No | `100` | `100` | `100` |

---

## Service: mobius-skills-scraper-worker

| Variable | Required | Dev (`mobius-os-dev`) | Staging (`mobius-staging-mobius`) | Production (`mobiusos-new`) |
|----------|----------|----------------------|-----------------------------------|----------------------------|
| `REDIS_URL` | Yes | `redis://10.40.102.67:6379/0` | `redis://10.121.0.3:6379/0` | `redis://10.30.217.227:6379/0` |
| `GCS_BUCKET` | Yes | `mobius-rag-uploads-dev` | `mobius-rag-uploads-staging` | `mobius-rag-uploads-mobiusos` |
| `WORKER_MODE` | Yes | `true` | `true` | `true` |
| `SCRAPER_REQUEST_KEY` | No | `mobius:scraper:requests` | `mobius:scraper:requests` | `mobius:scraper:requests` |

---

## Service: mobius-os-backend

| Variable | Required | Dev (`mobius-os-dev`) | Staging (`mobius-staging-mobius`) | Production (`mobiusos-new`) |
|----------|----------|----------------------|-----------------------------------|----------------------------|
| `DATABASE_MODE` | Yes | `cloud` | `cloud` | `cloud` |
| `GCP_PROJECT_ID` | Yes | `mobius-os-dev` | `mobius-staging-mobius` | `mobiusos-new` |
| `CLOUDSQL_CONNECTION_NAME` | Yes | `mobius-os-dev:us-central1:mobius-platform-dev-db` | `mobius-staging-mobius:us-central1:mobius-platform-staging-db` | `mobiusos-new:us-central1:mobius-platform-db` |
| `SECRET_KEY` | Yes | (Secret Manager: `app-secret-key`) | (Secret Manager: `app-secret-key`) | (Secret Manager: `app-secret-key`) |
| `POSTGRES_PASSWORD_CLOUD` | Yes | (Secret Manager: `db-password`) | (Secret Manager: `db-password-mobius`) | (Secret Manager: `db-password`) |
| `FLASK_ENV` | No | `development` | `production` | `production` |
| `GCP_CREDENTIALS_PATH` | Local dev only | `/path/to/credentials.json` | N/A (uses SA) | N/A (uses SA) |

---

## Service: Mobius-user

| Variable | Required | Dev (`mobius-os-dev`) | Staging (`mobius-staging-mobius`) | Production (`mobiusos-new`) |
|----------|----------|----------------------|-----------------------------------|----------------------------|
| `USER_DATABASE_URL` | Yes | `postgresql://postgres:{pwd}@/mobius_user?host=/cloudsql/mobius-os-dev:us-central1:mobius-platform-dev-db` | `postgresql://mobius_app:{pwd}@/mobius_user?host=/cloudsql/mobius-staging-mobius:us-central1:mobius-platform-staging-db` | `postgresql://postgres:{pwd}@/mobius_user?host=/cloudsql/mobiusos-new:us-central1:mobius-platform-db` |
| `JWT_SECRET` | Yes | (Secret Manager: `jwt-secret`) | (Secret Manager: `jwt-secret`) | (Secret Manager: `jwt-secret`) |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | `30` | `30` |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | No | `7` | `7` | `7` |
| `DEFAULT_TENANT_ID` | No | `default` | `default` | `default` |
| `DEFAULT_TENANT_NAME` | No | `Default Tenant` | `Default Tenant` | `Default Tenant` |

---

## Service: mobius-dbt

| Variable | Required | Dev (`mobius-os-dev`) | Staging (`mobius-staging-mobius`) | Production (`mobiusos-new`) |
|----------|----------|----------------------|-----------------------------------|----------------------------|
| `POSTGRES_HOST` | Yes | `/cloudsql/mobius-os-dev:us-central1:mobius-platform-dev-db` | `/cloudsql/mobius-staging-mobius:us-central1:mobius-platform-staging-db` | `/cloudsql/mobiusos-new:us-central1:mobius-platform-db` |
| `POSTGRES_PORT` | Yes | `5432` | `5432` | `5432` |
| `POSTGRES_DB` | Yes | `mobius_rag` | `mobius_rag` | `mobius_rag` |
| `POSTGRES_USER` | Yes | `postgres` | `mobius_app` | `postgres` |
| `POSTGRES_PASSWORD` | Yes | (Secret Manager: `db-password`) | (Secret Manager: `db-password-mobius-rag`) | (Secret Manager: `db-password`) |
| `BQ_PROJECT` | Yes | `mobius-os-dev` | `mobius-staging-mobius` | `mobiusos-new` |
| `BQ_LANDING_DATASET` | Yes | `landing_rag` | `landing_rag` | `landing_rag` |
| `BQ_DATASET` | Yes | `mobius_rag` | `mobius_rag` | `mobius_rag` |
| `CHAT_DATABASE_URL` | Yes | `postgresql://postgres:{pwd}@/mobius_chat?host=/cloudsql/mobius-os-dev:us-central1:mobius-platform-dev-db` | `postgresql://mobius_app:{pwd}@/mobius_chat?host=/cloudsql/mobius-staging-mobius:us-central1:mobius-platform-staging-db` | `postgresql://postgres:{pwd}@/mobius_chat?host=/cloudsql/mobiusos-new:us-central1:mobius-platform-db` |
| `VERTEX_PROJECT` | Yes | `mobius-os-dev` | `mobius-staging-mobius` | `mobiusos-new` |
| `VERTEX_REGION` | Yes | `us-central1` | `us-central1` | `us-central1` |
| `GCS_BUCKET` | Yes | `mobius-rag-uploads-dev` | `mobius-rag-uploads-staging` | `mobius-rag-uploads-mobiusos` |

---

## Known Issues to Fix

### Production (`mobiusos-new`)
- [x] `mobius-rag` service missing `LLM_PROVIDER` and `VERTEX_MODEL` - FIXED 2026-02-05
- [x] `mobius-rag` uses `GCS_BUCKET=mobius-rag-uploads` - FIXED to `mobius-rag-uploads-mobiusos` 2026-02-05
- [x] `mobius-skills-scraper` uses `GCS_BUCKET=mobius-rag-uploads` - FIXED to `mobius-rag-uploads-mobiusos` 2026-02-05

### Staging (`mobius-staging-mobius`)
- [x] `VERTEX_PROJECT_ID` standardized to `mobius-staging-mobius` for all services - FIXED 2026-02-05
- [x] `VERTEX_INDEX_ENDPOINT_ID` updated to staging's own endpoint - FIXED 2026-02-05
- [x] `mobius-rag` added missing `ENV=staging`, `VERTEX_MODEL`, `LLM_PROVIDER` - FIXED 2026-02-05
- [x] `mobius-rag-chunking-worker` changed `ENV=prod` to `ENV=staging` - FIXED 2026-02-05
- [x] `mobius-rag-embedding-worker` changed `ENV=prod` to `ENV=staging` - FIXED 2026-02-05
- [x] `mobius-skills-scraper-worker` added `WORKER_MODE=true` - FIXED 2026-02-05

### Dev (`mobius-os-dev`)
- [x] Create Cloud SQL instance `mobius-platform-dev-db` (34.135.72.145) - DONE 2026-02-06
- [x] Create Redis instance `mobius-dev-redis` (10.40.102.67) - DONE 2026-02-06
- [x] Create GCS bucket `mobius-rag-uploads-dev` - DONE 2026-02-06
- [x] Create GCS bucket `mobius-dev-vertex-index` - DONE 2026-02-06
- [x] Create VPC connector `mobius-dev-vpc-connector` (10.9.0.0/28) - DONE 2026-02-06
- [x] Create service account `mobius-platform-dev@mobius-os-dev.iam.gserviceaccount.com` - DONE 2026-02-06
- [ ] Enable required APIs (Cloud SQL, Redis, Cloud Run, Vertex AI, etc.)
- [x] Create Vertex AI index endpoint for dev (`156370344679047168`) - DONE 2026-02-06
- [x] Create Vertex AI index (`8112788326987071488`, 8128 vectors) - DONE 2026-02-06
- [ ] Deploy Vertex AI index to endpoint (deployment in progress, deployed_index_id: `mobius_chat_dev`)
- [ ] Deploy all 10 Cloud Run services
- [x] Update local `.env` and `.env.example` files with ENV_MODE toggle (local/dev-cloud) - DONE 2026-02-06

---

## Dev Environment Setup Commands

```bash
# Set project
export DEV_PROJECT_ID=mobius-os-dev
export REGION=us-central1
gcloud config set project $DEV_PROJECT_ID

# Enable APIs
gcloud services enable \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  aiplatform.googleapis.com \
  storage.googleapis.com

# Create Service Account
gcloud iam service-accounts create mobius-platform-dev \
  --display-name="Mobius Platform Dev Service Account"

# Create Cloud SQL
gcloud sql instances create mobius-platform-dev-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=$REGION \
  --root-password=YOUR_PASSWORD

# Create databases
gcloud sql databases create mobius_rag --instance=mobius-platform-dev-db
gcloud sql databases create mobius_chat --instance=mobius-platform-dev-db
gcloud sql databases create mobius_os --instance=mobius-platform-dev-db
gcloud sql databases create mobius_user --instance=mobius-platform-dev-db

# Create Redis (requires VPC)
gcloud redis instances create mobius-dev-redis \
  --size=1 \
  --region=$REGION \
  --network=default

# Create GCS Buckets
gsutil mb -p $DEV_PROJECT_ID -l $REGION gs://mobius-rag-uploads-dev/
gsutil mb -p $DEV_PROJECT_ID -l $REGION gs://mobius-dev-vertex-index/

# Create Secrets
echo -n "YOUR_JWT_SECRET" | gcloud secrets create jwt-secret --data-file=-
echo -n "YOUR_DB_PASSWORD" | gcloud secrets create db-password --data-file=-

# Grant permissions to service account
gcloud projects add-iam-policy-binding $DEV_PROJECT_ID \
  --member="serviceAccount:mobius-platform-dev@${DEV_PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding $DEV_PROJECT_ID \
  --member="serviceAccount:mobius-platform-dev@${DEV_PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $DEV_PROJECT_ID \
  --member="serviceAccount:mobius-platform-dev@${DEV_PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $DEV_PROJECT_ID \
  --member="serviceAccount:mobius-platform-dev@${DEV_PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

---

## Secrets (Never in .env files, use Secret Manager in cloud)

| Secret Name | Services Using It |
|-------------|-------------------|
| `jwt-secret` | mobius-chat-api, mobius-chat-worker, Mobius-user |
| `db-password` | mobius-os-backend, mobius-rag, mobius-chat |
| `db-password-mobius-chat` | mobius-chat-api, mobius-chat-worker (staging only) |
| `app-secret-key` | mobius-os-backend |

---

---

## Cloud Run Services Checklist

All environments should have these 10 services deployed:

| Service | Production | Staging | Dev |
|---------|------------|---------|-----|
| `mobius-chat-api` | Deployed | Deployed | TO CREATE |
| `mobius-chat-worker` | Deployed | Deployed | TO CREATE |
| `mobius-dbt-ui` | Deployed | Deployed | TO CREATE |
| `mobius-os-backend` | Deployed | Deployed | TO CREATE |
| `mobius-rag` | Deployed | Deployed | TO CREATE |
| `mobius-rag-chunking-worker` | Deployed | Deployed | TO CREATE |
| `mobius-rag-embedding-worker` | Deployed | Deployed | TO CREATE |
| `mobius-skills-scraper` | Deployed | Deployed | TO CREATE |
| `mobius-skills-scraper-worker` | Deployed | Deployed | TO CREATE |
| `module-hub` | Deployed | Deployed | TO CREATE |

---

*Last updated: 2026-02-06*
