"""SQLite graph with provenance, deterministic deduplication and search log."""
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any
from .models import utcnow

NODE_TYPES = {"Website", "Domain", "Page", "Snapshot", "Software", "Game", "Developer", "Organization", "Media", "Release", "Source"}
RELATIONS = {"ARCHIVED_AS", "MOVED_TO", "RENAMED_TO", "RELEASED_BY", "MENTIONED_IN", "SUPERSEDED_BY", "POSSIBLY_SAME_AS", "CONTRADICTS", "DERIVED_FROM"}


class EvidenceStore:
    def __init__(self, path: Path | str) -> None:
        self.db = sqlite3.connect(str(path))
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS nodes(id TEXT PRIMARY KEY, kind TEXT NOT NULL, data TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS edges(id TEXT PRIMARY KEY, src TEXT REFERENCES nodes(id), dst TEXT REFERENCES nodes(id), relation TEXT, source_url TEXT, observed_at TEXT, data TEXT);
            CREATE TABLE IF NOT EXISTS search_log(id INTEGER PRIMARY KEY, searched_at TEXT, provider TEXT, query TEXT, result_count INTEGER, status TEXT, clues TEXT, next_reason TEXT);
        ''')

    def node(self, node_id: str, kind: str, data: dict[str, Any]) -> None:
        if kind not in NODE_TYPES: raise ValueError("Invalid node type")
        self.db.execute("INSERT OR REPLACE INTO nodes VALUES(?,?,?)", (node_id, kind, json.dumps(data, ensure_ascii=False)))
        self.db.commit()

    def edge(self, src: str, dst: str, relation: str, source_url: str,
             observed_at: str, data: dict[str, Any]) -> str:
        if relation not in RELATIONS or not source_url or not observed_at:
            raise ValueError("Every relationship requires a valid type, source and time")
        if relation in {"MOVED_TO", "RENAMED_TO"} and not data.get("direct_evidence"):
            raise ValueError("Confirmed moves/renames require direct evidence")
        key = hashlib.sha256(json.dumps([src, dst, relation, source_url, observed_at]).encode()).hexdigest()
        self.db.execute("INSERT OR IGNORE INTO edges VALUES(?,?,?,?,?,?,?)", (key, src, dst, relation, source_url, observed_at, json.dumps(data, ensure_ascii=False)))
        self.db.commit()
        return key

    def log(self, provider: str, query: str, count: int, status: str,
            clues: list[str], next_reason: str) -> None:
        self.db.execute("INSERT INTO search_log(searched_at,provider,query,result_count,status,clues,next_reason) VALUES(?,?,?,?,?,?,?)",
                        (utcnow(), provider, query, count, status, json.dumps(clues, ensure_ascii=False), next_reason))
        self.db.commit()

    def export(self) -> dict[str, Any]:
        return {"nodes": [{"id": r[0], "kind": r[1], "data": json.loads(r[2])} for r in self.db.execute("SELECT * FROM nodes ORDER BY id")],
                "edges": [{"id": r[0], "src": r[1], "dst": r[2], "relation": r[3], "source_url": r[4], "observed_at": r[5], "data": json.loads(r[6])} for r in self.db.execute("SELECT * FROM edges ORDER BY id")],
                "search_log": [{"searched_at": r[1], "provider": r[2], "query": r[3], "result_count": r[4], "status": r[5], "clues": json.loads(r[6]), "next_reason": r[7]} for r in self.db.execute("SELECT * FROM search_log ORDER BY id")]}

    def close(self) -> None:
        self.db.close()
