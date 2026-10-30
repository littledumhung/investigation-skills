"""Evidence-only collection reports. Identification is a separate Agent step."""
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit
from .models import utcnow
from .timeline_builder import build_timeline


def build_report(target: str, mode: str, plan: dict[str, Any], providers: list[dict[str, Any]],
                 graph: dict[str, Any], identity: dict[str, Any] | None = None) -> dict[str, Any]:
    records, seen = [], set()
    for provider in providers:
        for record in provider["records"]:
            key = record.get("snapshot_id") or (provider["provider"], record.get("kind"), record.get("url"), record.get("name"))
            if key in seen: continue
            seen.add(key)
            records.append(record)
    return {"schema_version": "1.0", "generated_at": utcnow(), "target": target, "mode": mode,
            "collection_status": "partial" if any(p["status"] != "ok" or p["truncated"] for p in providers) else "completed",
            "identification": identity or {"label": "UNRESOLVED", "confidence": "無法判定", "reason": "Collected records have not yet been verified against the user's remembered target"},
            "most_likely_target": None, "original_history": None, "candidate_matches": [],
            "query_plan": plan, "providers": providers, "records": records, "timeline": build_timeline(records),
            "evidence_graph": graph, "investigation_log": graph["search_log"],
            "missing": ["Candidate feature comparison and independent primary-source verification require Agent review", "An index hit does not establish replay availability or copyright permission"],
            "next_steps": ["Read collected primary sources, compare features and contradictions", "Use Agent web search for refined multilingual queries; record independent origins", "If no new evidence remains, report UNRESOLVED and ask for the most discriminating clue"]}


def clean(value: Any) -> str:
    return str(value).replace("\n", " ").replace("\r", " ").replace("|", "\\|").replace("<", "&lt;").replace(">", "&gt;")


def link(url: Any) -> str:
    if not isinstance(url, str) or urlsplit(url).scheme not in {"http", "https"}: return "未取得"
    return "<" + url.replace("<", "%3C").replace(">", "%3E").replace("\n", "").replace("\r", "") + ">"


def markdown(report: dict[str, Any]) -> str:
    identity = report["identification"]
    lines = ["# Internet Archaeologist 調查報告", "", "## 最可能找到的目標", "",
             f"調查輸入：{clean(report['target'])}", "", "尚未確認；以下為實際查詢所得紀錄，需由 Agent 比對候選。", "",
             "## 原始歷史資訊", "", "最早存檔不等於創立日期；索引日期不等於內容發布日期。", "",
             "## 找到的內容", ""]
    for provider in report["providers"]:
        lines.append(f"- {provider['provider']}：{provider['status']}，{len(provider['records'])} 筆" + ("（結果受預算／抽樣限制）" if provider["truncated"] else ""))
        for error in provider["errors"]: lines.append(f"  - 錯誤：{clean(error)}")
    for record in report["records"]:
        title = record.get("title") or record.get("name") or record.get("original_url") or record.get("full_name") or "紀錄"
        lines.append(f"- {clean(title)} — {link(record.get('archive_url') or record.get('url'))}")
    if not report["records"]: lines.append("沒有取得紀錄；不代表目標從未存在。")
    lines += ["", "## 歷史時間軸", "", "| 日期 | 日期意義 | 證據 |", "|---|---|---|"]
    for event in report["timeline"]:
        lines.append(f"| {clean(event['date'])} | {clean(event['date_type'])} | {link(event['source_url'])} |")
    lines += ["", "## 為什麼認為是它", "", clean(identity["reason"]), "", "## 其他可能候選", "",
              "候選尚未完成驗證；同名、相似外觀或同網域均不足以確認。", "", "## 可信程度", "",
              f"{identity['confidence']}（{identity['label']}）", "", "## 尚未找到的部分", ""]
    if identity.get("evidence"):
        evidence_lines = ["", "### 身分比對證據", ""]
        for item in identity["evidence"]:
            evidence_lines.append(f"- {'支持' if item.get('supports') is True else '矛盾' if item.get('supports') is False else '觀察'}：{clean(item.get('detail'))}；類型 {clean(item.get('kind'))}；觀察時間 {clean(item.get('observed_at'))}；事件時間 {clean(item.get('event_date'))} — {link(item.get('source_url'))}")
        insert = lines.index("## 其他可能候選")
        lines[insert:insert] = evidence_lines
    lines += ["- " + text for text in report["missing"]]
    lines += ["", "## 下一步", ""] + ["- " + text for text in report["next_steps"]]
    return "\n".join(lines) + "\n"


def write_report(report: dict[str, Any], directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (directory / "report.md").write_text(markdown(report), encoding="utf-8")
