#!/usr/bin/env python3
"""
Mobius environment doctor.

Goals:
- Load env the same way services do (module .env first, then global mobius-config/.env).
- Print key env vars (redacting secrets).
- Validate credentials: GOOGLE_APPLICATION_CREDENTIALS or gcloud ADC can mint an access token.

Usage:
  python mobius-config/env_doctor.py --module mobius-chat
  python mobius-config/env_doctor.py --module mobius-rag
  python mobius-config/env_doctor.py --module mobius-os/backend
  python mobius-config/env_doctor.py --module mobius-dbt
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Iterable


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _module_root_from_arg(module: str) -> Path:
    """
    module may be:
      - a known module name: mobius-chat | mobius-rag | mobius-dbt | mobius-os/backend | mobius-user
      - a relative/absolute path
    """
    module = (module or "").strip()
    if not module:
        raise ValueError("--module is required")
    root = _repo_root()
    p = Path(module)
    if p.is_absolute():
        return p.resolve()
    # allow passing "mobius-chat" etc
    return (root / module).resolve()


def _redact_value(key: str, value: str) -> str:
    k = (key or "").upper()
    if value is None:
        return ""
    v = str(value)
    # Never print secrets.
    if any(tok in k for tok in ("SECRET", "PASSWORD", "TOKEN", "API_KEY", "PRIVATE_KEY")):
        return "(set)" if v.strip() else "(unset)"
    if k in ("JWT_SECRET",):
        return "(set)" if v.strip() else "(unset)"
    return v


def _print_kv(key: str, value: str | None) -> None:
    if value is None or (isinstance(value, str) and value.strip() == ""):
        print(f"- {key}=<unset>")
    else:
        print(f"- {key}={_redact_value(key, value)}")


def _print_section(title: str) -> None:
    print("")
    print(f"== {title} ==")


def _exists(p: str | None) -> bool:
    if not p:
        return False
    try:
        return Path(p).expanduser().exists()
    except Exception:
        return False


def _load_env_for_module(module_root: Path) -> None:
    """
    Prefer mobius-config/env_helper.py if importable; otherwise fall back to python-dotenv.
    """
    # Ensure mobius-config is importable so env_helper is found when running from repo root.
    cfg_dir = _repo_root() / "mobius-config"
    if cfg_dir.exists():
        import sys

        if str(cfg_dir) not in sys.path:
            sys.path.insert(0, str(cfg_dir))

    try:
        from env_helper import load_env  # type: ignore

        load_env(module_root)
        return
    except Exception:
        pass

    # Fallback: only load module .env.
    try:
        from dotenv import load_dotenv  # type: ignore

        env_file = module_root / ".env"
        if env_file.exists():
            load_dotenv(env_file, override=True)
    except Exception:
        return


def _required_vars_for_module(module_root: Path) -> list[str]:
    """
    Minimal "key vars" list: not exhaustive, but what typically breaks runs.
    """
    name = module_root.name
    # Normalize mobius-os/backend path
    if name == "backend" and module_root.parent.name == "mobius-os":
        name = "mobius-os/backend"

    common = [
        "ENV",
        "QUEUE_TYPE",
        "REDIS_URL",
        "GOOGLE_APPLICATION_CREDENTIALS",
        "VERTEX_PROJECT_ID",
        "VERTEX_LOCATION",
        "VERTEX_MODEL",
    ]
    if name == "mobius-chat":
        return common + [
            # Chat persistence + RAG
            "CHAT_RAG_DATABASE_URL",
            "VERTEX_INDEX_ENDPOINT_ID",
            "VERTEX_DEPLOYED_INDEX_ID",
            # Chat overrides
            "CHAT_LLM_PROVIDER",
            "LLM_PROVIDER",
            "OLLAMA_BASE_URL",
            "OLLAMA_MODEL",
            "MOBIUS_OS_AUTH_URL",
            "USER_DATABASE_URL",
            "JWT_SECRET",
            "CHAT_LIVE_STREAM",
            "CHAT_DEBUG_TRACE",
        ]
    if name == "mobius-rag":
        return common + [
            "DATABASE_URL",
            "GCS_BUCKET",
            "VERTEX_INDEX_ENDPOINT_ID",
            "VERTEX_DEPLOYED_INDEX_ID",
            "LLM_PROVIDER",
        ]
    if name == "mobius-dbt":
        return common + [
            "DATABASE_URL",
            "CHAT_DATABASE_URL",
            "BQ_PROJECT",
            "BQ_DATASET",
            "BQ_LANDING_DATASET",
            "GCS_BUCKET",
            "VERTEX_PROJECT",
            "VERTEX_REGION",
        ]
    if name == "mobius-os/backend":
        return [
            "DATABASE_MODE",
            "CLOUDSQL_CONNECTION_NAME",
            "POSTGRES_HOST",
            "POSTGRES_PORT",
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
            "SECRET_KEY",
            "JWT_SECRET",
            "ENABLE_FIRESTORE",
            "GCP_PROJECT_ID",
            "GOOGLE_APPLICATION_CREDENTIALS",
        ]
    # default: best-effort common list
    return common


def _credential_sources() -> dict[str, str]:
    """
    Report the main credential sources.
    - GOOGLE_APPLICATION_CREDENTIALS (service account key file)
    - gcloud ADC file (user credentials)
    """
    gac = (os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or "").strip()
    adc = str(Path("~/.config/gcloud/application_default_credentials.json").expanduser())
    return {
        "GOOGLE_APPLICATION_CREDENTIALS": gac,
        "GCLOUD_ADC_PATH": adc,
    }


def _try_mint_access_token() -> tuple[bool, str]:
    """
    Validate we can mint an access token. This checks:
    - credentials file exists & is parseable, OR ADC exists.
    - network to Google token endpoint.

    It does NOT prove Vertex/DB permissions (IAM) — just that auth works.
    """
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
    try:
        gac = (os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or "").strip()
        from google.auth.transport.requests import Request  # type: ignore

        if gac:
            from google.oauth2 import service_account  # type: ignore

            p = Path(gac).expanduser()
            creds = service_account.Credentials.from_service_account_file(str(p), scopes=scopes)
            creds.refresh(Request())
            # Don't print token; just confirm.
            email = getattr(creds, "service_account_email", None) or "(unknown)"
            return (True, f"OK (service account): {email}")

        import google.auth  # type: ignore

        creds, project_id = google.auth.default(scopes=scopes)
        creds.refresh(Request())
        return (True, f"OK (application default credentials) project={project_id or '(unknown)'}")
    except Exception as e:
        return (False, f"FAILED to mint access token: {e}")


def _safe_json_summary(path: Path) -> dict:
    """
    Return non-sensitive summary fields from a service-account JSON.
    Never return private_key, token_uri, etc.
    """
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"ok": False, "error": "Could not read/parse JSON"}
    return {
        "ok": True,
        "type": obj.get("type"),
        "project_id": obj.get("project_id"),
        "client_email": obj.get("client_email"),
        "private_key_present": bool(obj.get("private_key")),
    }


def _verify_vertex_permissions() -> tuple[bool, str]:
    """
    Minimal Vertex permission check:
    - If VERTEX_INDEX_ENDPOINT_ID is set, call get_index_endpoint.

    This proves:
    - network reachability to Vertex API
    - credentials have permission to read that resource

    It does NOT prove:
    - Generative model (Gemini) access / allowlists
    """
    endpoint = (os.getenv("VERTEX_INDEX_ENDPOINT_ID") or "").strip()
    if not endpoint:
        return (False, "SKIPPED (VERTEX_INDEX_ENDPOINT_ID is unset)")
    try:
        from google.cloud import aiplatform_v1  # type: ignore
        import re

        # Matching Engine resources are regional; must use a regional API endpoint.
        m = re.search(r"/locations/([^/]+)/", endpoint)
        loc = (m.group(1) if m else (os.getenv("VERTEX_LOCATION") or "").strip() or "us-central1")
        api_endpoint = f"{loc}-aiplatform.googleapis.com"

        client = aiplatform_v1.IndexEndpointServiceClient(client_options={"api_endpoint": api_endpoint})
        obj = client.get_index_endpoint(name=endpoint)
        display_name = getattr(obj, "display_name", "") or ""
        return (True, f"OK get_index_endpoint (region={loc!r} display_name={display_name!r})")
    except Exception as e:
        return (False, f"FAILED get_index_endpoint: {e}")


def _print_credentials_diagnostics() -> None:
    s = _credential_sources()
    gac = s["GOOGLE_APPLICATION_CREDENTIALS"]
    adc = s["GCLOUD_ADC_PATH"]

    _print_section("Credentials")
    _print_kv("GOOGLE_APPLICATION_CREDENTIALS", gac or None)
    print(f"- GOOGLE_APPLICATION_CREDENTIALS_exists={'yes' if _exists(gac) else 'no'}")
    print(f"- gcloud_ADC_exists={'yes' if _exists(adc) else 'no'}")

    # If service account key exists, print safe summary (no secrets).
    summary: dict | None = None
    if gac and _exists(gac):
        p = Path(gac).expanduser()
        summary = _safe_json_summary(p)
        if summary.get("ok"):
            print("- service_account_json_summary=" + json.dumps(summary, ensure_ascii=False))
        else:
            print(f"- service_account_json_summary_error={summary.get('error')}")

    ok, msg = _try_mint_access_token()
    print(f"- can_mint_access_token={'yes' if ok else 'no'}")
    print(f"- auth_check={msg}")

    # Heuristic: credentials JSON's project_id might not match the Vertex project you're targeting.
    if summary and summary.get("ok"):
        cred_project = (summary.get("project_id") or "").strip()
        vertex_project = (os.getenv("VERTEX_PROJECT_ID") or "").strip()
        if cred_project and vertex_project and cred_project != vertex_project:
            print(
                f"- note=service-account key project_id={cred_project!r} differs from VERTEX_PROJECT_ID={vertex_project!r}; "
                "this is OK only if the service account has IAM roles in the Vertex project."
            )


def _print_required_vars(module_root: Path) -> None:
    keys = _required_vars_for_module(module_root)
    _print_section(f"Key environment variables ({module_root})")
    for k in keys:
        _print_kv(k, os.getenv(k))

    # Small heuristics / warnings that frequently cause surprises.
    _print_section("Heuristics / warnings")
    vertex_pid = (os.getenv("VERTEX_PROJECT_ID") or "").strip()
    llm_provider = ((os.getenv("CHAT_LLM_PROVIDER") or os.getenv("LLM_PROVIDER") or "").strip().lower())
    if vertex_pid and not llm_provider:
        print("- note=VERTEX_PROJECT_ID is set; some components default to Vertex/Gemini unless CHAT_LLM_PROVIDER/LLM_PROVIDER is explicitly set.")
    if llm_provider in ("vertex", "gemini") and not (os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or "").strip():
        print("- note=LLM provider is vertex but GOOGLE_APPLICATION_CREDENTIALS is unset; you must have gcloud ADC or workload identity available.")
    if (os.getenv("QUEUE_TYPE") or "").strip().lower() == "redis" and not (os.getenv("REDIS_URL") or "").strip():
        print("- warning=QUEUE_TYPE=redis but REDIS_URL is unset.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--module", required=True, help="Module name or path (e.g. mobius-chat, mobius-rag, mobius-os/backend)")
    ap.add_argument("--verify-vertex", action="store_true", help="Probe Vertex API permissions (get index endpoint).")
    args = ap.parse_args()

    module_root = _module_root_from_arg(args.module)
    if not module_root.exists():
        print(f"ERROR: module path not found: {module_root}")
        return 2

    # Load env before reading vars.
    _load_env_for_module(module_root)

    print("Mobius env doctor")
    print(f"- repo_root={_repo_root()}")
    print(f"- module_root={module_root}")
    print(f"- module_env_file_exists={'yes' if (module_root / '.env').exists() else 'no'}")
    print(f"- global_env_file_exists={'yes' if (_repo_root() / 'mobius-config' / '.env').exists() else 'no'}")

    _print_required_vars(module_root)
    _print_credentials_diagnostics()
    if args.verify_vertex:
        _print_section("Vertex permission probe")
        ok, msg = _verify_vertex_permissions()
        print(f"- vertex_get_index_endpoint={'yes' if ok else 'no'}")
        print(f"- vertex_probe={msg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

