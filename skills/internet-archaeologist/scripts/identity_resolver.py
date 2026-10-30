"""Evidence-led identity decisions. Scores are not statistical probabilities."""
from typing import Any

LABELS = {"SAME_ENTITY", "POSSIBLY_SAME", "RELATED_BUT_DISTINCT", "DIFFERENT_ENTITY", "UNRESOLVED"}


def resolve(evidence: list[dict[str, Any]]) -> dict[str, Any]:
    """Evidence fields: source_url, observed_at, origin_id, kind, supports, detail.

    origin_id identifies the original assertion across copies/syndication. The
    Agent must establish it: this helper cannot infer source independence.
    """
    accepted, skipped = [], []
    seen: set[str] = set()
    seen_assertions: set[tuple[str, str, str, str]] = set()
    for item in evidence:
        if not isinstance(item, dict):
            raise ValueError("Every identity observation must be a JSON object")
        if not item.get("source_url") or not item.get("observed_at") or not item.get("detail"):
            skipped.append({"reason": "Missing provenance", "evidence": item})
            continue
        origin = item.get("origin_id")
        if not origin:
            skipped.append({"reason": "Independence unknown; assign a verified origin_id", "evidence": item})
            continue
        assertion = (str(origin), str(item.get("kind")), str(item.get("supports")), str(item["detail"]))
        if assertion in seen_assertions:
            skipped.append({"reason": "Copied/shared origin, not independent evidence", "evidence": item})
            continue
        seen.add(origin)
        seen_assertions.add(assertion)
        accepted.append(item)
    kinds = {r.get("kind") for r in accepted}
    strong = [r for r in accepted if r.get("supports") is True and r.get("kind") in {"official_rename", "official_migration", "repository_continuity", "verified_identical_hash"}]
    supports = [r for r in accepted if r.get("supports") is True]
    support_origins = {r["origin_id"] for r in supports}
    substantive_origins = {r["origin_id"] for r in supports if r.get("kind") not in {"title", "name", "appearance", "same_domain", "translated_name"}}
    conflicts = [r for r in accepted if r.get("supports") is False]
    hard = [r for r in conflicts if r.get("kind") in {"temporal_contradiction", "official_distinct", "ownership_discontinuity"}]
    if strong and hard:
        label, reason = "UNRESOLVED", "Strong supporting and conflicting evidence require reconciliation"
    elif "official_distinct" in {r.get("kind") for r in hard}:
        label, reason = "DIFFERENT_ENTITY", "Explicit primary evidence distinguishes the entities"
    elif hard:
        label, reason = "UNRESOLVED", "Material temporal/ownership contradiction blocks confirmation"
    elif strong and len(support_origins) >= 2 and not conflicts:
        label, reason = "SAME_ENTITY", "Direct continuity evidence corroborated by an independent origin"
    elif "related" in {r.get("kind") for r in supports}:
        label, reason = "RELATED_BUT_DISTINCT", "Evidence supports relationship but not identity"
    elif strong or len(substantive_origins) >= 2:
        label, reason = "POSSIBLY_SAME", "Suggestive evidence, insufficient independent primary confirmation"
    else:
        label, reason = "UNRESOLVED", "Insufficient evidence; name or appearance alone is not identity"
    return {"label": label, "reason": reason, "evidence": accepted, "excluded": skipped,
            "independent_origins": len(seen), "contradictions": conflicts,
            "confidence": "高" if label in {"SAME_ENTITY", "DIFFERENT_ENTITY"} else "中" if label == "POSSIBLY_SAME" else "無法判定"}
