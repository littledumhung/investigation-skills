# Agent JSON 介面
權威機器契約為 ../schemas/report.schema.json；scripts/report.schema.json為wheel內相同副本。請先閱讀Schema或有效實例 ../examples/live-moon-distance.json，再建立JSON；不要靠本文件猜欄位。大部分欄位必填，未知nullable欄位用null、集合用[]，不能刪欄位。至少一項claim；所有節點ID全域唯一。

頂層：schema_version=1.0、as_of、checked_at、mode、summary、limitations、precise_wording、claims、sources、evidence、quotes、datasets、calculations、contradictions、verdicts、relations、search_log。時間戳需時區，未知發布日期null。沒有來源URL用null並填missing_reason；不能為過Schema編網址。

Claim保存原文、原子主張、類型、主詞／述詞／受詞、時間地點、required_evidence、checkability、ambiguity與dependencies。Source保存角色、作者日期、取得的內容、可選SHA256、可存取狀態、publication_type、correction_status、derived_from及可選日期值。類型值見Schema，不把主張字串當成所有欄位。

Evidence連claim及source，relation為SUPPORTS／CONTRADICTS／CONTEXT。Quote需是該source.content內精確存在的短原文，附locator。語義支持仍由agent判讀。Calculation由statistics_engine.calculate結果加calculation_id，sources指Source IDs；會重算並核公式、結果、rounding。

Verdict保存verdict_id、claim_id、判定、summary、strongest_support／strongest_counterevidence的Evidence IDs、來源品質、限制、信心、checked_at及counterevidence_search（queries、status、notes）。每claim恰一判定，意見不判真假。graph自動從結構建立證據、來源與判定連結，並合併手寫relations；拒絕懸空關係。

執行 `python scripts/validate.py report.json`，再 `python scripts/cli.py --evidence report.json --format markdown --output report.md`。技術驗證不能證明captured內容真的出自聲稱的URL；仍需研究審核。
