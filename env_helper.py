"""
One helper for any module: check env in my (module) environment first;
if a variable is not set there, use the global mobius-config/.env.
Call load_env(module_root) once at startup; then use os.getenv() or get_env().
"""
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def _is_placeholder_credentials(value: str) -> bool:
    """True if value looks like a placeholder (e.g. /path/to/your-service-account.json)."""
    if not value or not value.strip():
        return True
    v = value.strip()
    if "/path/to/" in v or "your-service-account" in v or "your-" in v.lower():
        return True
    return False


def _resolve_credentials_path(module_root: Path) -> Optional[str]:
    """
    Look for a GCP service account JSON: module credentials/ then global mobius-config/credentials/.
    Returns first existing *.json path as string, or None.
    """
    module_root = Path(module_root).resolve()
    candidates = [
        *(module_root / "credentials").glob("*.json"),
        *(module_root.parent / "mobius-config" / "credentials").glob("*.json"),
    ]
    for p in candidates:
        if p.is_file():
            return str(p.resolve())
    return None


def load_env(module_root: Path) -> None:
    """
    Check env in my environment first; if not available, use global.
    Any module can call this with its repo root (e.g. mobius-chat, mobius-rag).
    Normalizes GOOGLE_APPLICATION_CREDENTIALS: treat placeholders as unset, resolve to local or global credentials/ if needed.
    """
    module_root = Path(module_root).resolve()
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    # 1) Module .env — wins (override=True)
    env_file = module_root / ".env"
    if env_file.exists():
        load_dotenv(env_file, override=True)
        logger.info(
            "[env_helper] loaded module .env: path=%s VERTEX_DEPLOYED_INDEX_ID=%r",
            env_file,
            os.environ.get("VERTEX_DEPLOYED_INDEX_ID"),
        )
    # 2) Global mobius-config/.env — fill in only what is not set (override=False)
    global_dir = module_root.parent / "mobius-config"
    global_env = global_dir / ".env"
    if global_env.exists():
        before = os.environ.get("VERTEX_DEPLOYED_INDEX_ID")
        load_dotenv(global_env, override=False)
        after = os.environ.get("VERTEX_DEPLOYED_INDEX_ID")
        logger.info(
            "[env_helper] loaded global .env: path=%s override=False → VERTEX_DEPLOYED_INDEX_ID before=%r after=%r",
            global_env,
            before,
            after,
        )

    # 3) GOOGLE_APPLICATION_CREDENTIALS: if placeholder or file missing, unset and try to resolve from local/global credentials/
    current = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or ""
    if _is_placeholder_credentials(current):
        os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
    else:
        p = Path(current).expanduser()
        if not p.is_absolute():
            p = (module_root / current).resolve()
        if p.is_file():
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(p)
        else:
            os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        resolved = _resolve_credentials_path(module_root)
        if resolved:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = resolved


def get_env(key: str, default: Optional[str] = None, placeholders: Optional[list[str]] = None) -> Optional[str]:
    """
    Read env var: value from current environment (after load_env).
    If value is missing, empty, or in placeholders, return default.
    """
    value = os.environ.get(key)
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return default
    if placeholders and value in placeholders:
        return default
    # Treat common placeholder patterns as "not set"
    if placeholders is None:
        placeholders = []
    if "/path/to/" in value or "your-service-account" in value or "your-" in value.lower():
        return default
    return value


def get_env_or(key: str, default: str, placeholders: Optional[list[str]] = None) -> str:
    """Like get_env but always returns a string (uses default if missing)."""
    return get_env(key, default=default, placeholders=placeholders) or default
