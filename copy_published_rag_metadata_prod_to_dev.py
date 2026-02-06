#!/usr/bin/env python3
"""
Copy production Chat Postgres table -> dev Chat Postgres.

Default behavior:
- Source (prod): uses env PROD_CHAT_DATABASE_URL (required)
- Destination (dev): loads mobius-chat env and uses CHAT_RAG_DATABASE_URL

Copies ONLY public.published_rag_metadata.
Safe-ish behavior:
- Runs inside a dev transaction: TRUNCATE + insert; rolls back on failure.
- Does not print any database URLs or secrets.

Usage (from repo root, using shared venv):
  # PROD_CHAT_DATABASE_URL must be set in the environment (do NOT commit it)
  .venv/bin/python3 mobius-config/copy_published_rag_metadata_prod_to_dev.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Iterable, List, Sequence


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_dev_env() -> None:
    """Load env for mobius-chat (module + global)."""
    root = _repo_root()
    cfg_dir = root / "mobius-config"
    if cfg_dir.exists() and str(cfg_dir) not in sys.path:
        sys.path.insert(0, str(cfg_dir))
    try:
        from env_helper import load_env  # type: ignore

        load_env(root / "mobius-chat")
    except Exception:
        # If env_helper isn't available, we still try to proceed with whatever env is set.
        pass


def _require(name: str) -> str:
    v = (os.getenv(name) or "").strip()
    if not v:
        raise SystemExit(f"Missing required env var: {name}")
    return v


def _get_columns(conn, table: str) -> list[str]:
    import psycopg2  # noqa: F401

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema='public'
              AND table_name=%s
            ORDER BY ordinal_position
            """,
            (table,),
        )
        return [r[0] for r in cur.fetchall()]


def _count_rows(conn, table: str) -> int:
    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) FROM public.{table}")
        return int(cur.fetchone()[0])


def _iter_rows(conn, table: str, cols: Sequence[str], batch_size: int = 1000) -> Iterable[list[tuple]]:
    """
    Stream rows from source using a server-side cursor to avoid loading everything in memory.
    """
    col_sql = ", ".join([f'"{c}"' for c in cols])
    # Named cursor = server-side in psycopg2.
    cur = conn.cursor(name="src_stream")
    cur.itersize = batch_size
    cur.execute(f'SELECT {col_sql} FROM public.{table}')
    while True:
        rows = cur.fetchmany(batch_size)
        if not rows:
            break
        yield rows
    cur.close()


def main() -> int:
    _load_dev_env()

    table = "published_rag_metadata"
    prod_url = _require("PROD_CHAT_DATABASE_URL")
    dev_url = _require("CHAT_RAG_DATABASE_URL")

    try:
        import psycopg2
        from psycopg2.extras import execute_values
    except Exception as e:
        print(f"ERROR: psycopg2 is required in the venv: {e}")
        return 2

    print("Copying published_rag_metadata: prod -> dev")

    # Source connection: read-only.
    src = psycopg2.connect(prod_url)
    src.autocommit = False
    # Destination connection: TRUNCATE + insert in one transaction.
    dst = psycopg2.connect(dev_url)
    dst.autocommit = False

    try:
        prod_cols = _get_columns(src, table)
        dev_cols = _get_columns(dst, table)

        if not prod_cols:
            raise RuntimeError("Source table has no columns (table missing?)")
        if not dev_cols:
            raise RuntimeError("Destination table has no columns (table missing?)")

        if prod_cols != dev_cols:
            # Allow a copy only if destination columns are a subset of source columns.
            missing_in_src = [c for c in dev_cols if c not in prod_cols]
            if missing_in_src:
                raise RuntimeError(
                    "Schema mismatch: destination has columns not present in prod: "
                    + ", ".join(missing_in_src)
                )
            # Use destination column order (stable).
            cols = dev_cols
            print("NOTE: schema differs; copying intersection columns in dev order.")
        else:
            cols = dev_cols

        prod_n = _count_rows(src, table)
        dev_n_before = _count_rows(dst, table)
        print(f"- source_rows={prod_n}")
        print(f"- dest_rows_before={dev_n_before}")

        with dst.cursor() as cur:
            cur.execute(f"TRUNCATE TABLE public.{table}")

        col_sql = ", ".join([f'"{c}"' for c in cols])
        insert_sql = f"INSERT INTO public.{table} ({col_sql}) VALUES %s"

        written = 0
        for batch in _iter_rows(src, table, cols, batch_size=1000):
            with dst.cursor() as cur:
                execute_values(cur, insert_sql, batch, page_size=500)
            written += len(batch)
            if written % 5000 == 0:
                print(f"- copied_rows={written}")

        dst.commit()
        src.commit()

        dev_n_after = _count_rows(dst, table)
        print(f"- copied_rows_total={written}")
        print(f"- dest_rows_after={dev_n_after}")
        return 0
    except Exception as e:
        try:
            dst.rollback()
        except Exception:
            pass
        try:
            src.rollback()
        except Exception:
            pass
        print(f"ERROR: copy failed: {e}")
        return 1
    finally:
        try:
            src.close()
        except Exception:
            pass
        try:
            dst.close()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())

