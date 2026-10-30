"""Conservative deterministic expansion; translations here are a small glossary."""
import re
from datetime import date
from typing import Any


def temporal_range(text: str, today: date | None = None) -> dict[str, Any]:
    today = today or date.today()
    years = [int(y) for y in re.findall(r"(?<!\d)(?:19|20)\d{2}(?!\d)", text)]
    inferred, reason = False, "explicit years"
    start: int | None = None
    end: int | None = None
    if years:
        start, end = min(years), max(years)
        if any(word in text.lower() for word in ("以前", "之前", "before")):
            start = None
            end = years[0] - 1
        elif len(years) == 1 and any(word in text.lower() for word in ("左右", "around", "大約")):
            start, end, inferred = years[0] - 2, years[0] + 2, True
    else:
        match = re.search(r"(\d+|十幾|十|五|二十)\s*(?:年|years?)\s*(?:前|ago)", text, re.I)
        if match:
            values = {"十": 10, "五": 5, "二十": 20, "十幾": 15}
            n = values[match[1]] if match[1] in values else int(match[1])
            spread = 4 if match[1] == "十幾" else 2
            start, end = today.year - n - spread, today.year - n + spread
            inferred, reason = True, f"Relative memory anchored to {today.isoformat()}"
        elif "xp" in text.lower():
            start, end, inferred, reason = 2001, 2014, True, "Windows XP lifecycle heuristic; later use remains possible"
        elif "flash" in text.lower():
            start, end, inferred, reason = 1996, 2020, True, "Flash era heuristic; not an exclusion constraint"
        else:
            reason = "No usable date; ask for remembered platform or period"
    return {"start_year": start, "end_year": end, "inferred": inferred, "reason": reason, "anchor_date": today.isoformat()}


GLOSSARY = {
    "藍色": ("blue", "青い"), "方塊": ("block cube", "ブロック"),
    "黑色背景": ("black background", "黒い背景"), "白色": ("white", "白い"),
    "網頁遊戲": ("browser game", "ブラウザゲーム"), "解謎": ("puzzle", "パズル"),
    "小工具": ("utility freeware", "フリーソフト"), "跳躍": ("platformer", "アクション"),
    "遊戲": ("game", "ゲーム"), "軟體": ("software", "ソフトウェア"),
}


def expand(query: str, today: date | None = None, seen: list[str] | None = None,
           new_clues: list[str] | None = None, limit: int = 12) -> dict[str, Any]:
    temporal = temporal_range(query, today)
    clues = [c.strip() for c in (new_clues or []) if c.strip()]
    root = " ".join([query.strip(), *clues])
    english, japanese = [], []
    for word, translations in GLOSSARY.items():
        if word in root:
            english.append(translations[0])
            japanese.append(translations[1])
    variants = [(root, "original", "Preserve user vocabulary and new evidence")]
    if english: variants.append((" ".join(dict.fromkeys(english)), "en", "Glossary translation; Agent should refine syntax"))
    if japanese: variants.append((" ".join(dict.fromkeys(japanese)), "ja", "Glossary translation; not a complete translation"))
    variants.append((root + " history", "mixed", "Historical references"))
    if "flash" in root.lower():
        variants.extend([(root + " archive", "mixed", "Historical references"),
                         (root + " old name", "en", "Rename hypothesis"),
                         (root + " filetype:swf", "en", "Flash file-name lead")])
    for year in dict.fromkeys([temporal["start_year"], temporal["end_year"]]):
        if year: variants.append((root + f" {year}", "mixed", "Year is a search hint, not publication proof"))
    if match := re.search(r'"([^"\n]+)"', query):
        variants.append((f'"{match[1]}"', "original", "Exact remembered phrase"))
    excluded = {q.casefold().strip() for q in (seen or [])}
    queries = []
    for text, language, reason in variants:
        key = text.casefold().strip()
        if key not in excluded:
            queries.append({"query": text, "language": language, "reason": reason})
            excluded.add(key)
    return {"temporal": temporal, "queries": queries[:limit], "new_clues": clues,
            "requires_agent": ["Full translation", "Hypothesis refinement", "Image/OCR/reverse-image tools if provided"],
            "stop": "No new query remains" if not queries else None}
