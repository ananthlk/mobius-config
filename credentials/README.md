# Shared credentials (mobius-config)

Put shared credential files **here** so modules do not reference paths outside their repo or outside this config repo.

- Copy your GCP service account JSON here, e.g. `gcp-service-account.json` or `mobius-platform-dev-mobius-os-dev.json`.
- In `mobius-config/.env` set the **full path** to that file, e.g.:
  ```bash
  GOOGLE_APPLICATION_CREDENTIALS=/Users/ananth/Mobius/mobius-config/credentials/mobiusos-new-090a058b63d9.json
  ```
  (Use your actual path to the Mobius folder; no spaces.)
- **For BigQuery / provider roster report on dev:** Use the key for **mobius-platform-dev@mobius-os-dev.iam.gserviceaccount.com** (Mobius Platform dev). Set `GOOGLE_APPLICATION_CREDENTIALS` in `mobius-config/.env` to the **full path** of that key, and ensure `BQ_PROJECT=mobius-os-dev` in the same `.env`. If you have multiple keys in this folder, `env_helper` uses the first one found; point `GOOGLE_APPLICATION_CREDENTIALS` explicitly at the dev key so the report uses it.
- When you use `inject_env.sh` or `run_with_shared_env.sh`, modules get this path from the shared `.env` and do not need their own copy of the key.
- Do **not** commit key files. This folder is gitignored except this README.
