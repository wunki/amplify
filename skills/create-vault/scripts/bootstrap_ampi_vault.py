#!/usr/bin/env python3
"""Bootstrap an Ampi-ready SQLite vault from an existing source table.

Outputs:
- canonical `chunks` and `docs` views
- `chunks_fts` keyword index (FTS5)
- optional sparse semantic tables + compatibility views
- `search_schema` + `build_info` metadata
- `amplify_search_manifest` manifest table
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import re
import shlex
import sqlite3
import subprocess
import zipfile
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SAFE_IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9']+")

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "he",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "that",
    "the",
    "to",
    "was",
    "were",
    "will",
    "with",
}

FIELD_CANDIDATES: dict[str, list[str]] = {
    "id_field": ["id", "_row_id", "chunk_id", "segment_id", "row_id", "uuid"],
    "text_field": ["text", "content", "body", "transcript_text", "transcript", "message", "note"],
    "doc_id_field": [
        "doc_id",
        "document_id",
        "episode_id",
        "account_id",
        "customer_id",
        "project_id",
        "thread_id",
        "conversation_id",
        "parent_id",
        "source_id",
    ],
    "slug_field": ["slug", "path", "uri", "file_path", "source_path"],
    "timestamp_field": ["timestamp", "ts", "created_at", "updated_at", "publish_date", "published_at"],
    "title_field": ["title", "name", "subject", "headline"],
    "author_field": ["author", "speaker", "guest", "owner", "username"],
    "collection_field": ["collection", "topic", "topic_slug", "category", "tags", "bucket"],
    "url_field": ["url", "source_url", "youtube_url", "link"],
}


@dataclass(frozen=True)
class FieldMapping:
    source_table: str
    id_field: str
    text_field: str
    doc_id_field: str
    slug_field: str | None
    timestamp_field: str | None
    title_field: str | None
    author_field: str | None
    collection_field: str | None
    url_field: str | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_table": self.source_table,
            "id_field": self.id_field,
            "text_field": self.text_field,
            "doc_id_field": self.doc_id_field,
            "slug_field": self.slug_field,
            "timestamp_field": self.timestamp_field,
            "title_field": self.title_field,
            "author_field": self.author_field,
            "collection_field": self.collection_field,
            "url_field": self.url_field,
        }


def default_contract_version() -> str:
    today = dt.datetime.now(dt.timezone.utc).date()
    return f"{today:%Y.%m.%d}.1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create or validate an Ampi-ready SQLite vault.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_build_like_args(
        cmd: argparse.ArgumentParser,
        *,
        include_db: bool,
        include_source_table: bool,
        source_required: bool,
        source_default: str | None = None,
        source_help: str = "Source table with row-level content.",
    ) -> None:
        if include_db:
            cmd.add_argument("--db", required=True, help="SQLite database path.")
        if include_source_table:
            kwargs: dict[str, Any] = {"help": source_help}
            if source_required:
                kwargs["required"] = True
            elif source_default is not None:
                kwargs["default"] = source_default
            cmd.add_argument("--source-table", **kwargs)

        cmd.add_argument("--id-field", help="Stable row ID field. Inferred when --auto-map is enabled.")
        cmd.add_argument("--text-field", help="Main text field. Inferred when --auto-map is enabled.")
        cmd.add_argument("--doc-id-field", help="Document/group ID field. Falls back to ID field.")
        cmd.add_argument("--slug-field", help="Optional slug/path field.")
        cmd.add_argument("--timestamp-field", help="Optional timestamp field.")
        cmd.add_argument("--title-field", help="Optional title field.")
        cmd.add_argument("--author-field", help="Optional author/speaker field.")
        cmd.add_argument("--collection-field", help="Optional topic/collection field.")
        cmd.add_argument("--url-field", help="Optional URL field.")
        cmd.add_argument("--auto-map", dest="auto_map", action="store_true", default=True, help="Infer fields from common names.")
        cmd.add_argument("--no-auto-map", dest="auto_map", action="store_false", help="Disable field inference.")
        cmd.add_argument("--print-mapping", action="store_true", help="Print resolved field mapping in output.")
        cmd.add_argument("--chunks-entity-name", help="Manifest entity name for chunk-level records. Default: source table name.")
        cmd.add_argument("--docs-entity-name", help="Manifest entity name for doc-level records. Default: <chunks-entity-name>_docs.")
        cmd.add_argument("--contract-version", default=default_contract_version(), help="CalVer contract version.")
        cmd.add_argument("--manifest-version", type=int, default=1, help="Manifest schema version (integer).")
        cmd.add_argument("--top-k-terms", type=int, default=24, help="Top weighted terms kept per chunk for sparse index.")
        cmd.add_argument("--aliases-json", help="Optional alias expansion JSON file.")
        cmd.add_argument("--no-semantic", action="store_true", help="Skip sparse semantic tables and semantic/deep capabilities.")
        cmd.add_argument("--vacuum", action="store_true", help="Run VACUUM after build.")

    inspect = subparsers.add_parser("inspect", help="Inspect source schema and suggest mapping/build command.")
    inspect.add_argument("--db", required=True, help="SQLite database path.")
    inspect.add_argument("--source-table", required=True, help="Source table with row-level content.")

    build = subparsers.add_parser("build", help="Build Ampi contract objects in SQLite.")
    add_build_like_args(
        build,
        include_db=True,
        include_source_table=True,
        source_required=True,
    )

    easy = subparsers.add_parser("easy", help="One-command path for existing SQLite: build then check.")
    add_build_like_args(
        easy,
        include_db=True,
        include_source_table=True,
        source_required=True,
    )
    easy.add_argument("--skip-check", action="store_true", help="Skip post-build validation check.")

    documents = subparsers.add_parser(
        "documents",
        help="Ingest markdown/txt/docx/doc files into SQLite, then build and check an Ampi vault.",
    )
    documents.add_argument("--db", required=True, help="SQLite database path to create or reuse.")
    documents.add_argument("--input-dir", required=True, help="Directory containing source documents.")
    documents.add_argument(
        "--source-table",
        default="source_rows",
        help="Destination table for ingested document chunks (default: source_rows).",
    )
    documents.add_argument(
        "--extensions",
        default="md,markdown,txt,docx,doc",
        help="Comma-separated file extensions to ingest (default: md,markdown,txt,docx,doc).",
    )
    documents.add_argument(
        "--chunk-size",
        type=int,
        default=1600,
        help="Target chunk size in characters per row (default: 1600).",
    )
    documents.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="Chunk overlap in characters (default: 200).",
    )
    documents.add_argument(
        "--overwrite-table",
        action="store_true",
        help="Drop and recreate the source table before ingest.",
    )
    documents.add_argument(
        "--skip-check",
        action="store_true",
        help="Skip post-build validation check.",
    )
    documents.add_argument(
        "--chunks-entity-name",
        help="Manifest entity name for chunk-level records. Default: source table name.",
    )
    documents.add_argument(
        "--docs-entity-name",
        help="Manifest entity name for doc-level records. Default: <chunks-entity-name>_docs.",
    )
    documents.add_argument("--contract-version", default=default_contract_version(), help="CalVer contract version.")
    documents.add_argument("--manifest-version", type=int, default=1, help="Manifest schema version (integer).")
    documents.add_argument("--top-k-terms", type=int, default=24, help="Top weighted terms kept per chunk for sparse index.")
    documents.add_argument("--aliases-json", help="Optional alias expansion JSON file.")
    documents.add_argument("--no-semantic", action="store_true", help="Skip sparse semantic tables and semantic/deep capabilities.")
    documents.add_argument("--vacuum", action="store_true", help="Run VACUUM after build.")

    check = subparsers.add_parser("check", help="Validate Ampi contract objects in SQLite.")
    check.add_argument("--db", required=True, help="SQLite database path.")

    return parser.parse_args()


def quote_ident(value: str) -> str:
    if not SAFE_IDENT_RE.match(value):
        raise RuntimeError(f"Unsafe SQL identifier: {value!r}")
    return f'"{value}"'


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def tokenize(text: str) -> list[str]:
    out: list[str] = []
    for token in TOKEN_RE.findall(text.lower()):
        if len(token) < 3:
            continue
        if token in STOPWORDS:
            continue
        if token.isdigit():
            continue
        out.append(token)
    return out


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA temp_store=MEMORY")
    return conn


def table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type IN ('table','view') AND name = ? LIMIT 1",
        (name,),
    ).fetchone()
    return row is not None


def object_type(conn: sqlite3.Connection, name: str) -> str | None:
    row = conn.execute("SELECT type FROM sqlite_master WHERE name = ? LIMIT 1", (name,)).fetchone()
    return None if row is None else str(row["type"])


def table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({quote_ident(table)})").fetchall()
    return {str(row["name"]) for row in rows}


def table_columns_with_types(conn: sqlite3.Connection, table: str) -> list[dict[str, str]]:
    rows = conn.execute(f"PRAGMA table_info({quote_ident(table)})").fetchall()
    return [{"name": str(row["name"]), "type": str(row["type"] or "")} for row in rows]


def infer_field_mapping(columns: set[str]) -> dict[str, str | None]:
    by_lower = {name.lower(): name for name in columns}

    def pick(candidates: list[str]) -> str | None:
        for candidate in candidates:
            mapped = by_lower.get(candidate.lower())
            if mapped is not None:
                return mapped
        return None

    inferred = {key: pick(candidates) for key, candidates in FIELD_CANDIDATES.items()}
    if inferred["doc_id_field"] is None:
        inferred["doc_id_field"] = inferred["id_field"]
    return inferred


def resolve_field_mapping(conn: sqlite3.Connection, args: argparse.Namespace) -> tuple[FieldMapping, dict[str, Any]]:
    if not table_exists(conn, args.source_table):
        raise RuntimeError(f"Source table not found: {args.source_table}")

    columns = table_columns(conn, args.source_table)
    inferred = infer_field_mapping(columns)

    def choose(name: str, explicit: str | None, required: bool = False, fallback: str | None = None) -> str | None:
        value = explicit
        if value is None and args.auto_map:
            value = inferred.get(name)  # type: ignore[assignment]
        if value is None:
            value = fallback

        if required and (value is None or value == ""):
            hints = inferred.get(name)
            hint_text = f" (inferred: {hints})" if hints else ""
            raise RuntimeError(
                f"Unable to resolve required field '{name}'. Pass --{name.replace('_', '-')} explicitly{hint_text}."
            )

        if value is not None and value not in columns:
            raise RuntimeError(f"Resolved field '{name}' points to missing column: {value}")

        return value

    id_field = choose("id_field", args.id_field, required=True)
    text_field = choose("text_field", args.text_field, required=True)
    doc_id_field = choose("doc_id_field", args.doc_id_field, fallback=id_field)
    slug_field = choose("slug_field", args.slug_field)
    timestamp_field = choose("timestamp_field", args.timestamp_field)
    title_field = choose("title_field", args.title_field)
    author_field = choose("author_field", args.author_field)
    collection_field = choose("collection_field", args.collection_field)
    url_field = choose("url_field", args.url_field)

    mapping = FieldMapping(
        source_table=args.source_table,
        id_field=str(id_field),
        text_field=str(text_field),
        doc_id_field=str(doc_id_field),
        slug_field=slug_field,
        timestamp_field=timestamp_field,
        title_field=title_field,
        author_field=author_field,
        collection_field=collection_field,
        url_field=url_field,
    )

    debug = {
        "auto_map": bool(args.auto_map),
        "available_columns": sorted(columns),
        "inferred_fields": inferred,
        "resolved_fields": mapping.as_dict(),
    }
    return mapping, debug


def default_entity_names(source_table: str, chunks_override: str | None, docs_override: str | None) -> tuple[str, str]:
    chunks_name = chunks_override or source_table
    docs_name = docs_override or f"{chunks_name}_docs"
    if docs_name == chunks_name:
        docs_name = f"{chunks_name}_docs"
    return chunks_name, docs_name


def text_expr(field: str | None) -> str:
    return f"CAST({quote_ident(field)} AS TEXT)" if field else "NULL"


def create_chunks_view(conn: sqlite3.Connection, mapping: FieldMapping) -> None:
    id_expr = quote_ident(mapping.id_field)
    doc_expr = quote_ident(mapping.doc_id_field)
    source_table = quote_ident(mapping.source_table)
    text_field = quote_ident(mapping.text_field)
    slug_expr = text_expr(mapping.slug_field)
    timestamp_expr = text_expr(mapping.timestamp_field)
    title_expr = text_expr(mapping.title_field)
    author_expr = text_expr(mapping.author_field)
    collection_expr = text_expr(mapping.collection_field)
    url_expr = text_expr(mapping.url_field)

    conn.execute("DROP VIEW IF EXISTS chunks")
    conn.execute(
        f"""
        CREATE VIEW chunks AS
        SELECT
          {id_expr} AS chunk_id,
          {id_expr} AS chunkid,
          {id_expr} AS segment_id,
          {doc_expr} AS doc_id,
          {doc_expr} AS docid,
          {doc_expr} AS episode_id,
          {slug_expr} AS slug,
          {author_expr} AS guest,
          {title_expr} AS title,
          NULL AS publish_date,
          {url_expr} AS youtube_url,
          NULL AS transcript_path,
          NULL AS segment_order,
          {author_expr} AS speaker,
          {timestamp_expr} AS timestamp,
          NULL AS timestamp_seconds,
          CAST({text_field} AS TEXT) AS text,
          {collection_expr} AS collection,
          {collection_expr} AS topic_names,
          {collection_expr} AS topic_slugs
        FROM {source_table}
        WHERE {text_field} IS NOT NULL
          AND trim(CAST({text_field} AS TEXT)) <> ''
        """
    )


def create_docs_view(conn: sqlite3.Connection) -> None:
    conn.execute("DROP VIEW IF EXISTS docs")
    conn.execute(
        """
        CREATE VIEW docs AS
        SELECT
          c.doc_id AS doc_id,
          c.doc_id AS docid,
          c.doc_id AS episode_id,
          MIN(c.slug) AS slug,
          MIN(c.guest) AS guest,
          MIN(c.title) AS title,
          NULL AS publish_date,
          MIN(c.youtube_url) AS youtube_url,
          NULL AS video_id,
          NULL AS description,
          NULL AS view_count,
          NULL AS channel,
          NULL AS word_count,
          NULL AS duration,
          NULL AS duration_seconds,
          NULL AS transcript_path,
          GROUP_CONCAT(DISTINCT c.collection) AS topic_names,
          GROUP_CONCAT(DISTINCT c.collection) AS topic_slugs,
          COUNT(
            DISTINCT CASE
              WHEN c.collection IS NULL OR trim(CAST(c.collection AS TEXT)) = '' THEN NULL
              ELSE c.collection
            END
          ) AS topic_count
        FROM chunks c
        GROUP BY c.doc_id
        """
    )


def create_keyword_index(conn: sqlite3.Connection) -> None:
    conn.execute("DROP TABLE IF EXISTS chunks_fts")
    conn.execute(
        """
        CREATE VIRTUAL TABLE chunks_fts USING fts5(
          chunk_id UNINDEXED,
          doc_id UNINDEXED,
          slug,
          guest,
          title,
          speaker,
          timestamp,
          collection,
          text,
          tokenize='porter unicode61'
        )
        """
    )
    conn.execute(
        """
        INSERT INTO chunks_fts(
          chunk_id,
          doc_id,
          slug,
          guest,
          title,
          speaker,
          timestamp,
          collection,
          text
        )
        SELECT
          chunk_id,
          doc_id,
          COALESCE(slug, ''),
          COALESCE(guest, ''),
          COALESCE(title, ''),
          COALESCE(speaker, ''),
          COALESCE(timestamp, ''),
          COALESCE(collection, ''),
          text
        FROM chunks
        """
    )


def ensure_semantic_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS semantic_term_stats (
          token TEXT PRIMARY KEY,
          df INTEGER NOT NULL,
          idf REAL NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS semantic_chunk_weights (
          chunk_id,
          token TEXT NOT NULL,
          weight REAL NOT NULL,
          PRIMARY KEY (chunk_id, token)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS semantic_chunk_norms (
          chunk_id PRIMARY KEY,
          norm REAL NOT NULL,
          token_count INTEGER NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS semantic_aliases (
          alias TEXT NOT NULL,
          token TEXT NOT NULL,
          weight REAL NOT NULL DEFAULT 1.0,
          PRIMARY KEY (alias, token)
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_semantic_chunk_weights_token ON semantic_chunk_weights(token)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_semantic_chunk_weights_chunk ON semantic_chunk_weights(chunk_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_semantic_aliases_alias ON semantic_aliases(alias)")


def parse_alias_rows(path: Path | None) -> list[tuple[str, str, float]]:
    if path is None:
        return []

    payload = json.loads(path.read_text())
    if not isinstance(payload, dict):
        raise RuntimeError("aliases JSON must be an object mapping alias -> tokens")

    rows: list[tuple[str, str, float]] = []
    for raw_alias, raw_value in payload.items():
        alias = str(raw_alias).strip().lower()
        if not alias:
            continue

        if isinstance(raw_value, dict):
            for token, weight in raw_value.items():
                token_text = str(token).strip().lower()
                if token_text:
                    rows.append((alias, token_text, float(weight)))
        elif isinstance(raw_value, list):
            for item in raw_value:
                if isinstance(item, str):
                    token_text = item.strip().lower()
                    if token_text:
                        rows.append((alias, token_text, 1.0))
                elif isinstance(item, list) and len(item) == 2:
                    token_text = str(item[0]).strip().lower()
                    if token_text:
                        rows.append((alias, token_text, float(item[1])))
                elif isinstance(item, dict):
                    token_text = str(item.get("token", "")).strip().lower()
                    if token_text:
                        rows.append((alias, token_text, float(item.get("weight", 1.0))))
        elif isinstance(raw_value, str):
            token_text = raw_value.strip().lower()
            if token_text:
                rows.append((alias, token_text, 1.0))

    return rows


def build_sparse_semantic(conn: sqlite3.Connection, top_k_terms: int, alias_path: Path | None) -> dict[str, int]:
    ensure_semantic_schema(conn)
    rows = conn.execute("SELECT chunk_id, text FROM chunks").fetchall()
    if not rows:
        raise RuntimeError("No rows available in chunks view, cannot build sparse semantic index.")

    total_chunks = len(rows)
    df: Counter[str] = Counter()
    chunk_tokens: dict[Any, Counter[str]] = {}

    for row in rows:
        chunk_id = row["chunk_id"]
        if chunk_id is None:
            continue
        tokens = tokenize(str(row["text"]))
        if not tokens:
            continue
        token_counts = Counter(tokens)
        chunk_tokens[chunk_id] = token_counts
        df.update(token_counts.keys())

    if not chunk_tokens:
        raise RuntimeError("All chunk rows were empty after tokenization.")

    conn.execute("DELETE FROM semantic_term_stats")
    conn.execute("DELETE FROM semantic_chunk_weights")
    conn.execute("DELETE FROM semantic_chunk_norms")
    conn.execute("DELETE FROM semantic_aliases")

    term_rows: list[tuple[str, int, float]] = []
    idf_map: dict[str, float] = {}
    for token, token_df in df.items():
        idf = math.log((total_chunks + 1.0) / (token_df + 1.0)) + 1.0
        idf_map[token] = idf
        term_rows.append((token, token_df, idf))
    conn.executemany("INSERT INTO semantic_term_stats(token, df, idf) VALUES (?, ?, ?)", term_rows)

    weight_rows: list[tuple[Any, str, float]] = []
    norm_rows: list[tuple[Any, float, int]] = []

    for chunk_id, token_counts in chunk_tokens.items():
        weighted: list[tuple[str, float]] = []
        for token, count in token_counts.items():
            idf = idf_map.get(token)
            if idf is None:
                continue
            weight = (1.0 + math.log(float(count))) * idf
            weighted.append((token, weight))

        if not weighted:
            continue

        weighted.sort(key=lambda item: item[1], reverse=True)
        kept = weighted[:max(top_k_terms, 4)]
        norm_sq = sum(weight * weight for _, weight in kept)
        norm = math.sqrt(norm_sq)
        if norm <= 0:
            continue

        norm_rows.append((chunk_id, norm, len(kept)))
        for token, weight in kept:
            weight_rows.append((chunk_id, token, weight))

    if weight_rows:
        conn.executemany(
            "INSERT INTO semantic_chunk_weights(chunk_id, token, weight) VALUES (?, ?, ?)",
            weight_rows,
        )
    if norm_rows:
        conn.executemany(
            "INSERT INTO semantic_chunk_norms(chunk_id, norm, token_count) VALUES (?, ?, ?)",
            norm_rows,
        )

    alias_rows = parse_alias_rows(alias_path)
    if alias_rows:
        conn.executemany("INSERT INTO semantic_aliases(alias, token, weight) VALUES (?, ?, ?)", alias_rows)

    return {
        "chunks_total": total_chunks,
        "chunks_indexed": len(norm_rows),
        "terms": len(term_rows),
        "aliases": len(alias_rows),
    }


def create_sparse_compat_views(conn: sqlite3.Connection) -> None:
    conn.execute("DROP VIEW IF EXISTS chunk_sparse_term_stats")
    conn.execute("DROP VIEW IF EXISTS chunk_sparse_weights")
    conn.execute("DROP VIEW IF EXISTS chunk_sparse_norms")
    conn.execute("DROP VIEW IF EXISTS query_expansion_aliases")

    conn.execute("CREATE VIEW chunk_sparse_term_stats AS SELECT token, df, idf FROM semantic_term_stats")
    conn.execute("CREATE VIEW chunk_sparse_weights AS SELECT chunk_id, token, weight FROM semantic_chunk_weights")
    conn.execute("CREATE VIEW chunk_sparse_norms AS SELECT chunk_id, norm, token_count FROM semantic_chunk_norms")
    conn.execute("CREATE VIEW query_expansion_aliases AS SELECT alias, token, weight FROM semantic_aliases")


def drop_sparse_compat_views(conn: sqlite3.Connection) -> None:
    conn.execute("DROP VIEW IF EXISTS chunk_sparse_term_stats")
    conn.execute("DROP VIEW IF EXISTS chunk_sparse_weights")
    conn.execute("DROP VIEW IF EXISTS chunk_sparse_norms")
    conn.execute("DROP VIEW IF EXISTS query_expansion_aliases")


def ensure_contract_tables(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS search_schema (
          key TEXT PRIMARY KEY,
          value TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS build_info (
          key TEXT PRIMARY KEY,
          value TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS amplify_search_manifest (
          id INTEGER PRIMARY KEY CHECK (id = 1),
          manifest_json TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS chunk_embeddings (
          chunk_id NOT NULL,
          embedding_model TEXT NOT NULL,
          embedding_dims INTEGER NOT NULL,
          embedding BLOB NOT NULL,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          PRIMARY KEY (chunk_id, embedding_model)
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_chunk_embeddings_model ON chunk_embeddings(embedding_model)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_chunk_embeddings_dims ON chunk_embeddings(embedding_dims)")


def semantic_query_sql() -> str:
    return (
        "WITH q AS ("
        "SELECT lower(CAST(?1 AS TEXT)) AS query, CAST(?2 AS TEXT) AS topic, "
        "CASE WHEN CAST(?3 AS INTEGER) > 0 THEN CAST(?3 AS INTEGER) ELSE 20 END AS lim"
        "), literal_terms AS ("
        "SELECT s.token AS token, 1.0 AS weight "
        "FROM semantic_term_stats s "
        "JOIN q "
        "WHERE instr(q.query, s.token) > 0 "
        "ORDER BY s.idf DESC "
        "LIMIT 96"
        "), alias_terms AS ("
        "SELECT a.token AS token, MAX(a.weight) AS weight "
        "FROM semantic_aliases a "
        "JOIN q "
        "WHERE instr(q.query, a.alias) > 0 "
        "GROUP BY a.token"
        "), query_terms AS ("
        "SELECT token, SUM(weight) AS weight "
        "FROM (SELECT token, weight FROM literal_terms UNION ALL SELECT token, weight FROM alias_terms) "
        "GROUP BY token"
        "), scored AS ("
        "SELECT w.chunk_id AS record_key, SUM(w.weight * qt.weight) / MAX(n.norm) AS cosine_score "
        "FROM query_terms qt "
        "JOIN semantic_chunk_weights w ON w.token = qt.token "
        "JOIN semantic_chunk_norms n ON n.chunk_id = w.chunk_id "
        "GROUP BY w.chunk_id "
        "HAVING cosine_score > 0 "
        "ORDER BY cosine_score DESC "
        "LIMIT (SELECT lim * 3 FROM q)"
        ") "
        "SELECT "
        "CAST(scored.record_key AS TEXT) AS record_key, "
        "CAST(CASE WHEN scored.cosine_score >= 1.0 THEN 0.0 ELSE (1.0 / scored.cosine_score) - 1.0 END AS REAL) AS distance, "
        "CAST(c.text AS TEXT) AS snippet, "
        "CAST(c.doc_id AS TEXT) AS docid, "
        "CAST(c.chunk_id AS TEXT) AS chunk_id, "
        "CAST(c.slug AS TEXT) AS episode_slug, "
        "CAST(c.timestamp AS TEXT) AS timestamp, "
        "CAST(c.collection AS TEXT) AS collection, "
        "CAST(c.topic_slugs AS TEXT) AS topic_slugs, "
        "CAST(c.topic_names AS TEXT) AS topic_names, "
        "CAST(c.guest AS TEXT) AS guest, "
        "CAST(c.title AS TEXT) AS title, "
        "CASE WHEN (SELECT topic FROM q) IS NULL OR length(trim((SELECT topic FROM q))) = 0 "
        "THEN NULL ELSE CAST((SELECT topic FROM q) AS TEXT) END AS topic_filter "
        "FROM scored "
        "JOIN chunks c ON CAST(c.chunk_id AS TEXT) = CAST(scored.record_key AS TEXT) "
        "WHERE (SELECT topic FROM q) IS NULL "
        "   OR length(trim((SELECT topic FROM q))) = 0 "
        "   OR instr(lower(COALESCE(c.topic_slugs, c.topic_names, c.collection)), lower((SELECT topic FROM q))) > 0 "
        "ORDER BY distance ASC, c.chunk_id ASC "
        "LIMIT (SELECT lim FROM q)"
    )


def manifest_payload(
    manifest_version: int,
    semantic_enabled: bool,
    chunks_entity_name: str,
    docs_entity_name: str,
) -> dict[str, Any]:
    if not SAFE_IDENT_RE.match(chunks_entity_name):
        raise RuntimeError(f"Invalid chunks entity name: {chunks_entity_name!r}")
    if not SAFE_IDENT_RE.match(docs_entity_name):
        raise RuntimeError(f"Invalid docs entity name: {docs_entity_name!r}")

    capabilities = {
        "keyword": True,
        "semantic": semantic_enabled,
        "deep": semantic_enabled,
        "lookup": True,
    }

    chunks_entity: dict[str, Any] = {
        "table": "chunks",
        "id_field": "chunk_id",
        "keyword": {
            "fts_table": "chunks_fts",
            "record_field": "chunk_id",
            "source_ref_fields": ["entity", "table", "docid", "chunk_id", "episode_slug", "timestamp", "collection"],
            "attribute_fields": ["docid", "chunk_id", "episode_slug", "timestamp", "collection"],
        },
        "lookup": {
            "fields": {
                "chunk_id": {"column": "chunk_id", "ops": ["eq", "neq", "in", "gt", "gte", "lt", "lte", "is_null", "not_null"]},
                "doc_id": {"column": "doc_id", "ops": ["eq", "neq", "in", "gt", "gte", "lt", "lte", "is_null", "not_null"]},
                "slug": {"column": "slug", "ops": ["eq", "neq", "in", "contains", "prefix", "suffix", "is_null", "not_null"]},
                "guest": {"column": "guest", "ops": ["eq", "neq", "in", "contains", "prefix", "suffix", "is_null", "not_null"]},
                "title": {"column": "title", "ops": ["eq", "neq", "contains", "prefix", "suffix", "is_null", "not_null"]},
                "speaker": {"column": "speaker", "ops": ["eq", "neq", "contains", "prefix", "suffix", "is_null", "not_null"]},
                "timestamp": {"column": "timestamp", "ops": ["eq", "neq", "contains", "prefix", "suffix", "is_null", "not_null"]},
                "collection": {"column": "collection", "ops": ["eq", "neq", "contains", "prefix", "suffix", "is_null", "not_null"]},
                "text": {"column": "text", "ops": ["contains", "prefix", "suffix"], "sortable": False, "aggregatable": False},
            },
            "default_fields": ["chunk_id", "doc_id", "slug", "timestamp", "text"],
            "default_sort": {"field": "chunk_id", "direction": "asc"},
            "default_limit": 20,
            "max_limit": 200,
            "aggregates": ["count", "count_distinct"],
        },
    }

    if semantic_enabled:
        chunks_entity["semantic"] = {
            "record_field": "chunk_id",
            "key_field": "record_key",
            "distance_field": "distance",
            "snippet_field": "snippet",
            "topic_field": "topic_filter",
            "source_ref_fields": ["entity", "table", "docid", "chunk_id", "episode_slug", "timestamp", "collection"],
            "attribute_fields": ["docid", "chunk_id", "episode_slug", "timestamp", "collection", "guest", "title"],
            "query_params": ["query", "topic", "limit"],
            "query_sql": semantic_query_sql(),
        }

    docs_entity = {
        "table": "docs",
        "id_field": "doc_id",
        "lookup": {
            "fields": {
                "doc_id": {"column": "doc_id", "ops": ["eq", "neq", "in", "gt", "gte", "lt", "lte", "is_null", "not_null"]},
                "slug": {"column": "slug", "ops": ["eq", "neq", "in", "contains", "prefix", "suffix", "is_null", "not_null"]},
                "guest": {"column": "guest", "ops": ["eq", "neq", "in", "contains", "prefix", "suffix", "is_null", "not_null"]},
                "title": {"column": "title", "ops": ["eq", "neq", "contains", "prefix", "suffix", "is_null", "not_null"]},
                "youtube_url": {"column": "youtube_url", "ops": ["eq", "neq", "contains", "prefix", "suffix", "is_null", "not_null"]},
                "topic_names": {"column": "topic_names", "ops": ["contains", "prefix", "suffix", "is_null", "not_null"]},
                "topic_count": {"column": "topic_count", "ops": ["eq", "neq", "gt", "gte", "lt", "lte"]},
            },
            "default_fields": ["doc_id", "slug", "guest", "title", "topic_names"],
            "default_sort": {"field": "doc_id", "direction": "asc"},
            "default_limit": 20,
            "max_limit": 100,
            "aggregates": ["count", "count_distinct", "min", "max", "sum", "avg"],
        },
    }

    return {
        "version": manifest_version,
        "capabilities": capabilities,
        "entities": {chunks_entity_name: chunks_entity, docs_entity_name: docs_entity},
    }


def write_contract_metadata(
    conn: sqlite3.Connection,
    *,
    contract_version: str,
    manifest_version: int,
    semantic_enabled: bool,
    chunks_entity_name: str,
    docs_entity_name: str,
) -> None:
    required_objects = [
        "docs",
        "chunks",
        "chunks_fts",
        "chunk_embeddings",
        "search_schema",
        "amplify_search_manifest",
    ]
    if semantic_enabled:
        required_objects.extend(
            [
                "semantic_term_stats",
                "semantic_chunk_weights",
                "semantic_chunk_norms",
                "semantic_aliases",
            ]
        )

    mode_string = "keyword,semantic,deep" if semantic_enabled else "keyword"
    sparse_tables = (
        "semantic_term_stats,semantic_chunk_weights,semantic_chunk_norms,semantic_aliases"
        if semantic_enabled
        else "not_built"
    )

    search_rows = [
        ("contract_version", contract_version),
        ("docs_object", "docs"),
        ("chunks_object", "chunks"),
        ("keyword_index", "chunks_fts"),
        ("dense_embeddings", "chunk_embeddings"),
        ("manifest_table", "amplify_search_manifest"),
    ]
    conn.executemany("INSERT OR REPLACE INTO search_schema(key, value) VALUES (?, ?)", search_rows)

    build_rows = [
        ("ampi_contract_version", contract_version),
        ("ampi_contract_docs_view", "docs"),
        ("ampi_contract_chunks_view", "chunks"),
        ("ampi_contract_keyword_index", "chunks_fts"),
        ("ampi_contract_sparse_semantic_tables", sparse_tables),
        ("ampi_contract_dense_embeddings_table", "chunk_embeddings"),
        ("ampi_contract_dense_semantic_status", "not_built"),
        ("ampi_contract_manifest_table", "amplify_search_manifest"),
        ("ampi_contract_manifest_source", "sqlite_table"),
        ("ampi_contract_modes", mode_string),
        ("ampi_contract_required_objects", ",".join(required_objects)),
        ("ampi_contract_built_at_utc", utc_now_iso()),
        ("ampi_manifest_version", str(manifest_version)),
    ]
    conn.executemany("INSERT OR REPLACE INTO build_info(key, value) VALUES (?, ?)", build_rows)

    manifest = manifest_payload(
        manifest_version=manifest_version,
        semantic_enabled=semantic_enabled,
        chunks_entity_name=chunks_entity_name,
        docs_entity_name=docs_entity_name,
    )
    conn.execute(
        "INSERT OR REPLACE INTO amplify_search_manifest(id, manifest_json) VALUES (1, ?)",
        (json.dumps(manifest, separators=(",", ":"), ensure_ascii=True),),
    )


def load_manifest(conn: sqlite3.Connection) -> dict[str, Any]:
    row = conn.execute("SELECT manifest_json FROM amplify_search_manifest WHERE id = 1").fetchone()
    if row is None or row["manifest_json"] is None:
        raise RuntimeError("Missing amplify_search_manifest row with id=1")
    decoded = json.loads(str(row["manifest_json"]))
    if not isinstance(decoded, dict):
        raise RuntimeError("Manifest JSON must decode to an object")
    return decoded


def summarize(conn: sqlite3.Connection) -> dict[str, Any]:
    build_info = {
        str(row["key"]): str(row["value"])
        for row in conn.execute("SELECT key, value FROM build_info WHERE key LIKE 'ampi_%' ORDER BY key")
    }
    manifest = load_manifest(conn)
    chunk_count = int(conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0])
    doc_count = int(conn.execute("SELECT COUNT(*) FROM docs").fetchone()[0])

    return {
        "contract_version": build_info.get("ampi_contract_version"),
        "modes": build_info.get("ampi_contract_modes"),
        "required_objects": build_info.get("ampi_contract_required_objects"),
        "manifest_version": manifest.get("version"),
        "manifest_capabilities": manifest.get("capabilities", {}),
        "entities": sorted((manifest.get("entities") or {}).keys()),
        "counts": {"chunks": chunk_count, "docs": doc_count},
    }


def build_command_hint(db_path: Path, mapping: FieldMapping) -> str:
    default_chunks_entity_name, default_docs_entity_name = default_entity_names(
        source_table=mapping.source_table,
        chunks_override=None,
        docs_override=None,
    )

    parts = [
        "python3",
        "skills/create-vault/scripts/bootstrap_ampi_vault.py",
        "build",
        "--db",
        str(db_path),
        "--source-table",
        mapping.source_table,
        "--id-field",
        mapping.id_field,
        "--text-field",
        mapping.text_field,
        "--chunks-entity-name",
        default_chunks_entity_name,
        "--docs-entity-name",
        default_docs_entity_name,
    ]
    if mapping.doc_id_field and mapping.doc_id_field != mapping.id_field:
        parts.extend(["--doc-id-field", mapping.doc_id_field])
    if mapping.slug_field:
        parts.extend(["--slug-field", mapping.slug_field])
    if mapping.timestamp_field:
        parts.extend(["--timestamp-field", mapping.timestamp_field])
    if mapping.title_field:
        parts.extend(["--title-field", mapping.title_field])
    if mapping.author_field:
        parts.extend(["--author-field", mapping.author_field])
    if mapping.collection_field:
        parts.extend(["--collection-field", mapping.collection_field])
    if mapping.url_field:
        parts.extend(["--url-field", mapping.url_field])
    return " ".join(shlex.quote(part) for part in parts)


def parse_extension_set(raw_extensions: str) -> set[str]:
    parsed = {
        value.strip().lower().lstrip(".")
        for value in raw_extensions.split(",")
        if value.strip()
    }
    if not parsed:
        raise RuntimeError("No file extensions configured, pass --extensions with at least one value.")
    return parsed


def normalize_text(raw_text: str) -> str:
    text = raw_text.replace("\x00", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def slugify(value: str) -> str:
    lowered = value.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return normalized or "document"


def discover_document_files(input_dir: Path, extensions: set[str]) -> list[Path]:
    files: list[Path] = []
    for path in input_dir.rglob("*"):
        if not path.is_file():
            continue
        extension = path.suffix.lower().lstrip(".")
        if extension in extensions:
            files.append(path)
    files.sort(key=lambda p: p.as_posix())
    return files


def extract_docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        try:
            xml_payload = archive.read("word/document.xml")
        except KeyError as exc:
            raise RuntimeError("DOCX missing word/document.xml") from exc

    root = ET.fromstring(xml_payload)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs: list[str] = []
    for paragraph in root.findall(".//w:p", ns):
        parts = [(node.text or "") for node in paragraph.findall(".//w:t", ns)]
        chunk = "".join(parts).strip()
        if chunk:
            paragraphs.append(chunk)
    return "\n\n".join(paragraphs)


def extract_doc_text(path: Path) -> tuple[str | None, str | None]:
    command_candidates = [
        ["textutil", "-convert", "txt", "-stdout", str(path)],
        ["antiword", str(path)],
    ]
    for command in command_candidates:
        try:
            result = subprocess.run(command, capture_output=True, check=True, text=False)
        except FileNotFoundError:
            continue
        except subprocess.CalledProcessError:
            continue

        decoded = result.stdout.decode("utf-8", errors="replace")
        normalized = normalize_text(decoded)
        if normalized:
            return normalized, None

    return None, "unable to parse .doc (install textutil/antiword or convert to .docx)"


def read_document_text(path: Path) -> tuple[str | None, str | None]:
    extension = path.suffix.lower().lstrip(".")

    if extension in {"md", "markdown", "txt"}:
        raw = path.read_text(encoding="utf-8", errors="replace")
        text = normalize_text(raw)
        return (text, None) if text else (None, "file is empty after normalization")

    if extension == "docx":
        try:
            text = normalize_text(extract_docx_text(path))
        except Exception as exc:
            return None, f"docx parse failed: {exc}"
        return (text, None) if text else (None, "docx is empty after normalization")

    if extension == "doc":
        return extract_doc_text(path)

    return None, f"unsupported extension: {extension}"


def split_into_chunks(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    if chunk_size <= 0:
        raise RuntimeError("chunk-size must be > 0")
    if chunk_overlap < 0:
        raise RuntimeError("chunk-overlap must be >= 0")
    if chunk_overlap >= chunk_size:
        raise RuntimeError("chunk-overlap must be smaller than chunk-size")

    normalized = normalize_text(text)
    if not normalized:
        return []

    chunks: list[str] = []
    cursor = 0
    text_length = len(normalized)

    while cursor < text_length:
        end = min(cursor + chunk_size, text_length)
        if end < text_length:
            boundary = -1
            search_start = cursor + max(1, chunk_size // 2)
            for marker in ("\n\n", "\n", " "):
                marker_pos = normalized.rfind(marker, search_start, end)
                if marker_pos > boundary:
                    boundary = marker_pos + len(marker)
            if boundary > cursor + (chunk_size // 3):
                end = boundary

        piece = normalized[cursor:end].strip()
        if piece:
            chunks.append(piece)
        if end >= text_length:
            break

        next_cursor = max(end - chunk_overlap, cursor + 1)
        if next_cursor <= cursor:
            next_cursor = end
        cursor = next_cursor

    return chunks


def derive_document_metadata(path: Path, input_dir: Path, text: str) -> dict[str, str | None]:
    relative_path = path.relative_to(input_dir).as_posix()
    relative_no_ext = str(Path(relative_path).with_suffix("")).replace("\\", "/")

    title: str | None = None
    for line in text.splitlines()[:40]:
        stripped = line.strip()
        if stripped.startswith("#"):
            candidate = stripped.lstrip("#").strip()
            if candidate:
                title = candidate
                break
    if title is None:
        title = re.sub(r"[-_]+", " ", path.stem).strip() or path.stem

    path_parts = Path(relative_path).parts
    collection = path_parts[0] if len(path_parts) > 1 else None

    return {
        "doc_id": slugify(relative_no_ext),
        "slug": relative_no_ext,
        "title": title,
        "collection": collection,
        "source_path": relative_path,
    }


def ensure_documents_source_table(conn: sqlite3.Connection, source_table: str, overwrite_table: bool) -> None:
    existing_type = object_type(conn, source_table)
    table_name = quote_ident(source_table)
    if existing_type is not None:
        if not overwrite_table:
            raise RuntimeError(
                f"Source table already exists: {source_table} (pass --overwrite-table to recreate it)"
            )
        conn.execute(f"DROP {existing_type.upper()} IF EXISTS {table_name}")

    conn.execute(
        f"""
        CREATE TABLE {table_name} (
          id TEXT PRIMARY KEY,
          doc_id TEXT NOT NULL,
          text TEXT NOT NULL,
          slug TEXT,
          title TEXT,
          collection TEXT,
          source_path TEXT NOT NULL,
          source_ext TEXT,
          chunk_index INTEGER NOT NULL
        )
        """
    )
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{source_table}_doc_id ON {table_name}(doc_id)")
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{source_table}_slug ON {table_name}(slug)")


def ingest_documents_to_sqlite(
    *,
    db_path: Path,
    input_dir: Path,
    source_table: str,
    raw_extensions: str,
    chunk_size: int,
    chunk_overlap: int,
    overwrite_table: bool,
) -> dict[str, Any]:
    if not input_dir.exists() or not input_dir.is_dir():
        raise RuntimeError(f"Input directory not found: {input_dir}")

    # Validate table name up front.
    quote_ident(source_table)

    extensions = parse_extension_set(raw_extensions)
    files = discover_document_files(input_dir, extensions)
    if not files:
        raise RuntimeError(
            f"No matching files found in {input_dir} for extensions: {', '.join(sorted(extensions))}"
        )

    warnings: list[str] = []
    documents_ingested = 0
    documents_skipped = 0
    chunks_inserted = 0
    seen_doc_ids: set[str] = set()
    table_name = quote_ident(source_table)

    if not db_path.parent.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)

    with connect(db_path) as conn:
        conn.execute("BEGIN")
        try:
            ensure_documents_source_table(conn, source_table, overwrite_table)
            insert_sql = (
                f"INSERT INTO {table_name} "
                "(id, doc_id, text, slug, title, collection, source_path, source_ext, chunk_index) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
            )

            batch: list[tuple[Any, ...]] = []
            for path in files:
                text, warning = read_document_text(path)
                rel_path = path.relative_to(input_dir).as_posix()
                if warning:
                    warnings.append(f"{rel_path}: {warning}")
                if text is None:
                    documents_skipped += 1
                    continue

                metadata = derive_document_metadata(path, input_dir, text)
                base_doc_id = str(metadata["doc_id"] or slugify(path.stem))
                doc_id = base_doc_id
                suffix = 2
                while doc_id in seen_doc_ids:
                    doc_id = f"{base_doc_id}-{suffix}"
                    suffix += 1
                seen_doc_ids.add(doc_id)

                chunks = split_into_chunks(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
                if not chunks:
                    warnings.append(f"{rel_path}: produced 0 chunks after normalization")
                    documents_skipped += 1
                    continue

                documents_ingested += 1
                for index, chunk in enumerate(chunks, start=1):
                    chunk_id = f"{doc_id}#{index:04d}"
                    batch.append(
                        (
                            chunk_id,
                            doc_id,
                            chunk,
                            metadata["slug"],
                            metadata["title"],
                            metadata["collection"],
                            metadata["source_path"],
                            path.suffix.lower().lstrip("."),
                            index,
                        )
                    )
                    chunks_inserted += 1

                    if len(batch) >= 500:
                        conn.executemany(insert_sql, batch)
                        batch.clear()

            if batch:
                conn.executemany(insert_sql, batch)

            if chunks_inserted == 0:
                raise RuntimeError("No chunks were inserted, nothing to build.")

            conn.commit()
        except Exception:
            conn.rollback()
            raise

    return {
        "db": str(db_path),
        "input_dir": str(input_dir),
        "source_table": source_table,
        "extensions": sorted(extensions),
        "files_discovered": len(files),
        "documents_ingested": documents_ingested,
        "documents_skipped": documents_skipped,
        "chunks_inserted": chunks_inserted,
        "warnings_count": len(warnings),
        "warnings": warnings[:50],
    }


def pick_probe_token(conn: sqlite3.Connection) -> str | None:
    row = conn.execute(
        "SELECT text FROM chunks WHERE text IS NOT NULL AND trim(CAST(text AS TEXT)) <> '' LIMIT 1"
    ).fetchone()
    if row is None:
        return None
    tokens = tokenize(str(row["text"]))
    return tokens[0] if tokens else None


def keyword_smoke_check(conn: sqlite3.Connection, probe_token: str | None) -> dict[str, Any]:
    if probe_token:
        fts_query = f'"{probe_token}"*'
        rows = conn.execute(
            "SELECT chunk_id, bm25(chunks_fts) AS score FROM chunks_fts WHERE chunks_fts MATCH ? ORDER BY bm25(chunks_fts) ASC LIMIT 3",
            (fts_query,),
        ).fetchall()
        return {"probe_token": probe_token, "rows": len(rows)}

    rows = conn.execute("SELECT chunk_id FROM chunks_fts LIMIT 1").fetchall()
    return {"probe_token": None, "rows": len(rows)}


def lookup_smoke_check(conn: sqlite3.Connection, manifest: dict[str, Any]) -> dict[str, Any]:
    entities = manifest.get("entities")
    if not isinstance(entities, dict):
        raise RuntimeError("Manifest entities must be an object")

    for entity_name in sorted(entities.keys()):
        entity = entities.get(entity_name)
        if not isinstance(entity, dict):
            continue
        lookup = entity.get("lookup")
        if not isinstance(lookup, dict):
            continue
        table = str(entity.get("table") or entity_name)
        fields = lookup.get("fields")
        if not isinstance(fields, dict) or not fields:
            continue

        chosen_column: str | None = None
        for field_name, definition in fields.items():
            if isinstance(definition, str):
                chosen_column = definition
            elif isinstance(definition, dict):
                chosen_column = str(definition.get("column") or "")
            elif isinstance(field_name, str):
                chosen_column = field_name

            if chosen_column:
                break

        if not chosen_column:
            continue

        sql = f"SELECT CAST({quote_ident(chosen_column)} AS TEXT) AS v FROM {quote_ident(table)} LIMIT 1"
        conn.execute(sql).fetchone()
        return {"entity": entity_name, "table": table, "column": chosen_column}

    conn.execute("SELECT chunk_id FROM chunks LIMIT 1").fetchone()
    return {"entity": "chunks", "table": "chunks", "column": "chunk_id", "fallback": True}


def semantic_smoke_check(conn: sqlite3.Connection, manifest: dict[str, Any], _probe_token: str | None) -> dict[str, Any]:
    capabilities = manifest.get("capabilities") or {}
    if not isinstance(capabilities, dict) or not bool(capabilities.get("semantic")):
        return {"skipped": True, "reason": "semantic_not_enabled"}

    entities = manifest.get("entities")
    if not isinstance(entities, dict):
        raise RuntimeError("Manifest entities missing")

    semantic_entity_name: str | None = None
    semantic: dict[str, Any] | None = None
    for entity_name, entity_config in entities.items():
        if not isinstance(entity_name, str) or not isinstance(entity_config, dict):
            continue
        candidate = entity_config.get("semantic")
        if isinstance(candidate, dict):
            semantic_entity_name = entity_name
            semantic = candidate
            break

    if semantic_entity_name is None or semantic is None:
        raise RuntimeError("Manifest semantic capability enabled but no semantic entity config found")

    query_sql = semantic.get("query_sql")
    if not isinstance(query_sql, str) or not query_sql.strip():
        raise RuntimeError("Manifest semantic query_sql missing")

    # Keep check cheap: validate that the query compiles and references resolvable
    # objects, without running a full sparse semantic retrieval.
    query = "__ampi_semantic_smoke_token__"
    plan_rows = conn.execute(f"EXPLAIN QUERY PLAN {query_sql}", (query, None, 1)).fetchall()
    stats_row = conn.execute("SELECT COUNT(*) FROM semantic_term_stats").fetchone()
    term_count = int(stats_row[0]) if stats_row else 0
    return {"entity": semantic_entity_name, "probe_query": query, "plan_steps": len(plan_rows), "term_count": term_count}


def run_inspect(args: argparse.Namespace) -> None:
    db_path = Path(args.db).expanduser().resolve()
    if not db_path.exists():
        raise RuntimeError(f"Database file not found: {db_path}")

    with connect(db_path) as conn:
        if not table_exists(conn, args.source_table):
            raise RuntimeError(f"Source table not found: {args.source_table}")

        columns = table_columns_with_types(conn, args.source_table)
        mapping_args = argparse.Namespace(
            source_table=args.source_table,
            id_field=None,
            text_field=None,
            doc_id_field=None,
            slug_field=None,
            timestamp_field=None,
            title_field=None,
            author_field=None,
            collection_field=None,
            url_field=None,
            auto_map=True,
        )
        mapping, debug = resolve_field_mapping(conn, mapping_args)
        row_count = int(conn.execute(f"SELECT COUNT(*) FROM {quote_ident(args.source_table)}").fetchone()[0])

    payload = {
        "ok": True,
        "db": str(db_path),
        "source_table": args.source_table,
        "row_count": row_count,
        "columns": columns,
        "inferred_mapping": mapping.as_dict(),
        "debug": debug,
        "suggested_build_command": build_command_hint(db_path, mapping),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


def run_build_impl(args: argparse.Namespace, *, emit: bool) -> dict[str, Any]:
    db_path = Path(args.db).expanduser().resolve()
    if not db_path.exists():
        raise RuntimeError(f"Database file not found: {db_path}")

    if args.manifest_version <= 0:
        raise RuntimeError("manifest-version must be a positive integer")

    semantic_enabled = not args.no_semantic
    alias_path = Path(args.aliases_json).expanduser().resolve() if args.aliases_json else None
    if alias_path and not alias_path.exists():
        raise RuntimeError(f"Alias file not found: {alias_path}")

    with connect(db_path) as conn:
        mapping, debug = resolve_field_mapping(conn, args)
        chunks_entity_name, docs_entity_name = default_entity_names(
            source_table=mapping.source_table,
            chunks_override=args.chunks_entity_name,
            docs_override=args.docs_entity_name,
        )

        if not SAFE_IDENT_RE.match(chunks_entity_name):
            raise RuntimeError("resolved chunks entity name must match [A-Za-z_][A-Za-z0-9_]*")
        if not SAFE_IDENT_RE.match(docs_entity_name):
            raise RuntimeError("resolved docs entity name must match [A-Za-z_][A-Za-z0-9_]*")

        sparse_stats: dict[str, int] | None = None

        try:
            conn.execute("BEGIN")
            create_chunks_view(conn, mapping)
            create_docs_view(conn)
            create_keyword_index(conn)
            ensure_contract_tables(conn)

            if semantic_enabled:
                sparse_stats = build_sparse_semantic(
                    conn,
                    top_k_terms=max(args.top_k_terms, 4),
                    alias_path=alias_path,
                )
                create_sparse_compat_views(conn)
            else:
                drop_sparse_compat_views(conn)

            write_contract_metadata(
                conn,
                contract_version=args.contract_version,
                manifest_version=args.manifest_version,
                semantic_enabled=semantic_enabled,
                chunks_entity_name=chunks_entity_name,
                docs_entity_name=docs_entity_name,
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise

        if args.vacuum:
            conn.execute("VACUUM")

        payload: dict[str, Any] = {
            "ok": True,
            "db": str(db_path),
            "summary": summarize(conn),
        }
        if args.print_mapping:
            payload["mapping"] = mapping.as_dict()
            payload["mapping_debug"] = debug
            payload["entity_names"] = {
                "chunks_entity_name": chunks_entity_name,
                "docs_entity_name": docs_entity_name,
            }
        if sparse_stats is not None:
            payload["sparse_semantic"] = sparse_stats

        if emit:
            print(json.dumps(payload, indent=2, sort_keys=True))
        return payload


def run_build(args: argparse.Namespace) -> None:
    _ = run_build_impl(args, emit=True)


def run_check_impl(args: argparse.Namespace, *, emit: bool, fail_on_error: bool) -> dict[str, Any]:
    db_path = Path(args.db).expanduser().resolve()
    if not db_path.exists():
        raise RuntimeError(f"Database file not found: {db_path}")

    required = [
        ("view", "docs"),
        ("view", "chunks"),
        ("table", "chunks_fts"),
        ("table", "search_schema"),
        ("table", "build_info"),
        ("table", "amplify_search_manifest"),
    ]

    errors: list[str] = []
    checks: dict[str, Any] = {}

    with connect(db_path) as conn:
        for expected_type, name in required:
            actual = object_type(conn, name)
            if actual is None:
                errors.append(f"Missing {expected_type}: {name}")
            elif actual != expected_type:
                errors.append(f"Object type mismatch for {name}: expected {expected_type}, got {actual}")

        manifest: dict[str, Any] = {}
        if not errors:
            try:
                manifest = load_manifest(conn)
            except Exception as exc:
                errors.append(str(exc))

        if not errors:
            version = manifest.get("version")
            if not isinstance(version, int) or version <= 0:
                errors.append("Manifest version must be a positive integer")

            capabilities = manifest.get("capabilities")
            if not isinstance(capabilities, dict):
                errors.append("Manifest capabilities must be an object")

        if not errors:
            probe_token = pick_probe_token(conn)

            try:
                checks["keyword_smoke"] = keyword_smoke_check(conn, probe_token)
            except Exception as exc:
                errors.append(f"Keyword smoke check failed: {exc}")

            try:
                checks["lookup_smoke"] = lookup_smoke_check(conn, manifest)
            except Exception as exc:
                errors.append(f"Lookup smoke check failed: {exc}")

            try:
                checks["semantic_smoke"] = semantic_smoke_check(conn, manifest, probe_token)
            except Exception as exc:
                errors.append(f"Semantic smoke check failed: {exc}")

        summary = summarize(conn) if not errors else {}

    payload = {
        "ok": len(errors) == 0,
        "db": str(db_path),
        "errors": errors,
        "checks": checks,
        "summary": summary,
    }
    if emit:
        print(json.dumps(payload, indent=2, sort_keys=True))
    if errors and fail_on_error:
        raise SystemExit(1)
    return payload


def run_check(args: argparse.Namespace) -> None:
    _ = run_check_impl(args, emit=True, fail_on_error=True)


def run_easy(args: argparse.Namespace) -> None:
    build_payload = run_build_impl(args, emit=False)
    output: dict[str, Any] = {
        "ok": bool(build_payload.get("ok")),
        "db": str(Path(args.db).expanduser().resolve()),
        "build": build_payload,
    }

    if args.skip_check:
        output["check"] = {"ok": True, "skipped": True}
    else:
        check_payload = run_check_impl(
            argparse.Namespace(db=args.db),
            emit=False,
            fail_on_error=False,
        )
        output["check"] = check_payload
        output["ok"] = bool(output["ok"] and check_payload.get("ok"))

    print(json.dumps(output, indent=2, sort_keys=True))
    if not output["ok"]:
        raise SystemExit(1)


def run_documents(args: argparse.Namespace) -> None:
    db_path = Path(args.db).expanduser().resolve()
    input_dir = Path(args.input_dir).expanduser().resolve()

    ingest_payload = ingest_documents_to_sqlite(
        db_path=db_path,
        input_dir=input_dir,
        source_table=args.source_table,
        raw_extensions=args.extensions,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        overwrite_table=bool(args.overwrite_table),
    )

    build_args = argparse.Namespace(
        db=str(db_path),
        source_table=args.source_table,
        id_field="id",
        text_field="text",
        doc_id_field="doc_id",
        slug_field="slug",
        timestamp_field=None,
        title_field="title",
        author_field=None,
        collection_field="collection",
        url_field="source_path",
        auto_map=False,
        print_mapping=True,
        chunks_entity_name=args.chunks_entity_name,
        docs_entity_name=args.docs_entity_name,
        contract_version=args.contract_version,
        manifest_version=args.manifest_version,
        top_k_terms=args.top_k_terms,
        aliases_json=args.aliases_json,
        no_semantic=args.no_semantic,
        vacuum=args.vacuum,
    )
    build_payload = run_build_impl(build_args, emit=False)
    output: dict[str, Any] = {
        "ok": bool(build_payload.get("ok")),
        "db": str(db_path),
        "documents_import": ingest_payload,
        "build": build_payload,
    }

    if args.skip_check:
        output["check"] = {"ok": True, "skipped": True}
    else:
        check_payload = run_check_impl(
            argparse.Namespace(db=args.db),
            emit=False,
            fail_on_error=False,
        )
        output["check"] = check_payload
        output["ok"] = bool(output["ok"] and check_payload.get("ok"))

    print(json.dumps(output, indent=2, sort_keys=True))
    if not output["ok"]:
        raise SystemExit(1)


def main() -> None:
    args = parse_args()
    if args.command == "inspect":
        run_inspect(args)
    elif args.command == "build":
        run_build(args)
    elif args.command == "easy":
        run_easy(args)
    elif args.command == "documents":
        run_documents(args)
    elif args.command == "check":
        run_check(args)
    else:
        raise SystemExit(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2), file=sys.stderr)
        raise SystemExit(1)
