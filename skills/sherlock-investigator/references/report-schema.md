# Bundle 與報告契約

`--evidence` 接受 UTF-8 JSON，最多 5 MiB；可直接複製 `examples/public-landmark.evidence.json` 結構並替換為真實觀察。該檔明確是合成示例，不能當真實調查證據。

頂層：hypotheses、evidence、nodes、edges、contradiction_checks（皆陣列）。

Hypothesis 必填：id、name、type、supporting_clues（陣列）、contradicting_clues（陣列）、unverified（陣列）、next_step。name 是候選名稱，不可夾帶未證實的精確私人位置。

可選 location：latitude（-90..90）、longitude（-180..180）、role（poi_center/building_center/camera_position/estimated_photo_position）、verification（verified/estimated）、accuracy_m（正數）。GeoGuessr 類答題可給估計點，需保留 estimated 與精度。report.location 是最佳有支持候選的座標；低於高可信的 verified 自動降為 estimated。純合成證據不釋出真實座標。

Evidence 必填：evidence_id、source（URL 或本地來源標籤）、source_type、observed_at（ISO-8601）、original_observation、interpretation、supporting_claim_ids（graph Claim ID 陣列）、limitations（陣列）、hypothesis_id、kind。選填 published_at、uncertain、independence_group。unknown 日期用 null；不填猜測日期。網址只做語法與字面 IP 安全檢查，不代表已造訪或已證實內容。

Graph node：id、type（Claim/Observation/Source/Hypothesis/Location/Object/Media）、可加 label。edge：from、to、relation（SUPPORTS/CONTRADICTS/DERIVED_FROM/MATCHES/REQUIRES_VERIFICATION）。graph 是輔助模型，Evidence 記錄是評分來源。

Contradiction check：hypothesis_id、finding，建議加 query、source_urls、checked_at；finding 寫具體檢查和剩餘疑點，而非只寫「檢查完成」。

報告 `assets/report.schema.json` 採 JSON Schema Draft 2020-12。完整驗證：

```sh
python scripts/validate.py
```

`report.json` 包含 case_id、created_at、status、privacy、mode、budget、inputs、answer、confidence、hypotheses、evidence、graph、contradiction_checks、limitations、next_step、score_notice。CLI 另加 intents 及 manual_search_links。status=complete 只在高可信、無限制時成立，不代表來源經數位簽章認證。

重跑請指定新的 --output 目錄；不覆寫原報告以保存調查歷程。例：先 case-intake，再 case-final。公開發佈前清除不必要原始路徑與敏感 metadata。
