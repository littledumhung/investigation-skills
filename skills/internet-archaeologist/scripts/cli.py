"""Public historical metadata collector and Agent investigation hand-off."""
import argparse
import json
import sqlite3
import sys
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = "scripts"

from .archive_parser import parse_html, safe_preview, compare
from .commoncrawl_client import CommonCrawlClient
from .evidence_store import EvidenceStore
from .github_history import GitHubHistory
from .identity_resolver import resolve
from .models import ProviderResult, utcnow
from .query_expander import expand
from .report_builder import build_report, write_report
from .search_providers import MetadataSearch, capabilities
from .transport import Transport, ProviderError, normalize_url
from .wayback_client import WaybackClient

BUDGETS = {"quick": (12, 90, 8), "deep": (40, 300, 30), "reconstruct": (48, 360, 30)}


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Internet Archaeologist — public historical evidence collector")
    p.add_argument("--url")
    p.add_argument("--query")
    p.add_argument("--repo", help="GitHub owner/repository")
    p.add_argument("--year", type=int)
    p.add_argument("--from-year", type=int)
    p.add_argument("--to-year", type=int)
    p.add_argument("--mode", type=str.lower, choices=BUDGETS, default="quick")
    p.add_argument("--today", type=date.fromisoformat, default=date.today(), help="Anchor relative memories, YYYY-MM-DD")
    p.add_argument("--providers", default=None, help="Comma-separated wayback,commoncrawl,github,archiveorg,wikipedia,gitlab,brave")
    p.add_argument("--output", type=Path, default=Path("investigation"))
    p.add_argument("--plan-only", action="store_true", help="Generate queries, no network")
    p.add_argument("--capabilities", action="store_true", help="Configuration/capabilities, not a live health guarantee")
    p.add_argument("--json", action="store_true", help="Also print complete JSON report")
    p.add_argument("--no-cache", action="store_true")
    p.add_argument("--seen-query", action="append", default=[])
    p.add_argument("--clue", action="append", default=[], help="New evidence to refine a later round")
    p.add_argument("--identity-evidence", type=Path, help="JSON list of sourced identity observations")
    p.add_argument("--offline-html", type=Path, help="Parse saved HTML without network; use --url as original base")
    return p


def run(args: argparse.Namespace) -> dict[str, Any]:
    target = args.query or args.url or args.repo
    if not target: raise ValueError("Provide --url, --query or --repo")
    if args.url: args.url = normalize_url(args.url)
    plan = expand(target, args.today, args.seen_query, args.clue)
    start = args.year if args.year is not None else args.from_year
    end = args.year if args.year is not None else args.to_year
    # Inferred ranges guide queries but never silently exclude contradictory dates.
    if start is None and not plan["temporal"]["inferred"]: start = plan["temporal"]["start_year"]
    if end is None and not plan["temporal"]["inferred"]: end = plan["temporal"]["end_year"]
    if start and end and start > end: raise ValueError("Start year must not exceed end year")
    for year in (start, end):
        if year is not None and not 1 <= year <= 9999: raise ValueError("Invalid year")
    calls, deadline, limit = BUDGETS[args.mode]
    plan["budget"] = {"http_calls_including_retries": calls, "deadline_seconds": deadline, "max_agent_search_calls": {"quick": 6, "deep": 20, "reconstruct": 16}[args.mode], "stop_after_no_new_evidence_rounds": 2}
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    transport = Transport(None if args.no_cache else output / "cache", budget=calls, deadline=deadline)
    # New run-local graph prevents old investigations contaminating this report.
    store = EvidenceStore(":memory:")
    results: list[dict[str, Any]] = []
    known = {"wayback", "commoncrawl", "github", "archiveorg", "wikipedia", "gitlab", "brave"}
    names = args.providers.split(",") if args.providers else (["wayback", "commoncrawl"] if args.url else ["github"] if args.repo else ["archiveorg", "wikipedia"])
    names = list(dict.fromkeys(n.strip() for n in names))
    if any(n not in known for n in names): raise ValueError("Unknown provider")
    try:
        if args.offline_html:
            if not args.url: raise ValueError("--offline-html requires --url for original link resolution")
            if args.offline_html.stat().st_size > transport.max_bytes: raise ValueError("HTML exceeds size limit")
            parsed = parse_html(args.offline_html.read_text(encoding="utf-8", errors="replace"), args.url)
            (output / "preview.html").write_text(safe_preview(parsed), encoding="utf-8")
            (output / "parsed.json").write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
            results.append(ProviderResult("offline-html", records=[{"url": args.url, "title": parsed["title"], "sha256": parsed["sha256"], "limitations": parsed["limitations"]}]).to_dict())
        elif not args.plan_only:
            for name in names:
                if name in {"wayback", "commoncrawl"}:
                    result = (WaybackClient(transport) if name == "wayback" else CommonCrawlClient(transport)).search(args.url, start, end, limit) if args.url else ProviderResult(name, status="not_applicable", errors=["URL required"])
                elif name == "github":
                    result = GitHubHistory(transport).search(args.repo, limit) if args.repo else ProviderResult(name, status="not_applicable", errors=["--repo required"])
                else:
                    result = MetadataSearch(transport, name).search(target, limit=min(limit, 20))
                results.append(result.to_dict())
                store.log(name, args.url or args.repo or target, len(result.records), result.status, [], "Verify returned records and refine using newly discovered names/URLs")
                for index, record in enumerate(result.records):
                    node_id = str(record.get("snapshot_id") or f"{name}:{index}")
                    store.node(node_id, "Snapshot" if record.get("snapshot_id") else "Source", record)
                    if record.get("snapshot_id") and record.get("original_url"):
                        page_id = "page:" + record["original_url"]
                        store.node(page_id, "Page", {"url": record["original_url"]})
                        source = record.get("archive_url") or "https://index.commoncrawl.org/"
                        store.edge(page_id, node_id, "ARCHIVED_AS", source, result.queried_at, {"captured_at": record.get("captured_at")})
            if args.mode == "reconstruct" and args.url:
                captures = sorted([r for p in results if p["provider"] == "wayback" for r in p["records"] if r.get("http_status") == 200 and r.get("archive_url") and "html" in (r.get("mime_type") or "")], key=lambda r: r["captured_at"])
                parsed_captures = []
                # Two observed endpoints; no speculative asset fetching.
                selected = [captures[0], captures[-1]] if len(captures) > 1 else captures
                for index, capture in enumerate(selected):
                    try:
                        archive_url = capture["archive_url"]
                        if urlsplit(archive_url).hostname != "web.archive.org": raise ValueError("Unexpected replay host")
                        replay = archive_url.replace("/" + archive_url.split("/web/")[1].split("/")[0] + "/", "/" + archive_url.split("/web/")[1].split("/")[0] + "id_/", 1)
                        body = transport.get(replay).decode("utf-8", errors="replace")
                        parsed = parse_html(body, capture["original_url"])
                        (output / f"preview-{index + 1}.html").write_text(safe_preview(parsed), encoding="utf-8")
                        (output / f"parsed-{index + 1}.json").write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
                        capture["replay_fetch_status"] = "retrieved"
                        capture["available_assets"] = []
                        capture["limitations"].append("Text fetched; referenced assets were not downloaded or verified")
                        parsed_captures.append(parsed)
                    except (ProviderError, ValueError) as exc:
                        capture["replay_fetch_status"] = "unavailable"
                        capture["limitations"].append(str(exc))
                if len(parsed_captures) == 2:
                    (output / "diff.json").write_text(json.dumps(compare(*parsed_captures), ensure_ascii=False, indent=2), encoding="utf-8")
        identity = None
        if args.identity_evidence:
            evidence = json.loads(args.identity_evidence.read_text(encoding="utf-8"))
            if not isinstance(evidence, list): raise ValueError("Identity evidence must be a JSON list")
            identity = resolve(evidence)
        report = build_report(target, args.mode, plan, results, store.export(), identity)
        report["network_log"] = transport.events
        report["http_calls_used"] = transport.calls
        report["agent_work_required"] = True
        if args.plan_only: report["collection_status"] = "plan_only"
        write_report(report, output)
        # Persist a fresh graph without deleting or replacing a user's previous database.
        destination = sqlite3.connect(str(output / ("evidence-" + utcnow().replace(":", "-") + ".sqlite")))
        try:
            store.db.backup(destination)
        finally:
            destination.close()
        return report
    finally:
        store.close()


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    p = parser()
    args = p.parse_args()
    if args.capabilities:
        print(json.dumps(capabilities(), ensure_ascii=False, indent=2))
        return 0
    try:
        report = run(args)
        print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else str(args.output.resolve() / "report.md"))
        return 2 if report["collection_status"] == "partial" else 0
    except (ValueError, OSError, TypeError) as exc:
        print(f"Input/output error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
