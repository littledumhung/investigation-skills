# JSON 1.0 與輸出

CLI 產出 report.md、report.json、evidence-時間.sqlite，可選 parsed／preview／diff。未知欄位用 null；缺資料不是空字串或猜值。蒐集報告與 Agent 最終調查報告分兩個階段。

頂層：schema_version、generated_at、target、mode、collection_status、identification、most_likely_target、original_history、candidate_matches、query_plan、providers、records、timeline、evidence_graph、investigation_log、missing、next_steps、network_log、http_calls_used、agent_work_required。

collection_status：completed/partial/plan_only，表示蒐集狀態而非辨識是否成功。Agent 完成後以另檔 final-report.json 保存補齊候選與結論，保留 CLI 原始 report.json，agent_work_required=false（只有實際完成來源閱讀與比對才可設）。

Snapshot：snapshot_id、original_url、archive_url、captured_at、content_timestamp、http_status、mime_type、content_hash、archive_provider、available_assets、limitations。Common Crawl archive_url=null，warc 另含 filename/offset/length；不可捏造可重播 URL。

Candidate：name、type、aliases、release_year、developer、platform、mechanics、visual_features、matching_clues、contradicting_clues、source_urls、availability、identity_label。欄位可隨目標擴充，所有判斷附證據。identification 含 label、confidence、reason、evidence、contradictions；label 使用五種身分判斷值。

Timeline：date、date_type、source_url、snapshot_id、description、http_status。Graph 節點 kind 為 Website/Domain/Page/Snapshot/Software/Game/Developer/Organization/Media/Release/Source；邊 relation 為 ARCHIVED_AS/MOVED_TO/RENAMED_TO/RELEASED_BY/MENTIONED_IN/SUPERSEDED_BY/POSSIBLY_SAME_AS/CONTRADICTS/DERIVED_FROM，並有 source_url、observed_at、data。

調查 log：searched_at、provider、query、result_count（實際取得）、status、clues、next_reason。圖的來源獨立性由 Agent 驗證，不能用節點數當證據數。

自然語言報告套用 assets/historical-report-template.md：最可能目標、原始歷史、找到的內容、時間軸、特徵比對、其他候選、可信程度、缺失、下一步。每個來源為可點擊原始連結，包含 API 失效與未確認的原因。
