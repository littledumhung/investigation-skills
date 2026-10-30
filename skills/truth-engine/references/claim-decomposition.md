# 原子主張拆解

## 建立可查單位

保存原文及段落／時間碼。每項只保留一個可驗證命題；不要丟掉否定、量詞、比較基準或引用者。將作者的說法與作者引用他人的說法分離。翻譯同時存原文及譯文，重要詞的多義性列為 ambiguity。

每項記錄 claim_id、original_text、normalized_claim、claim_type、subject、predicate、object、time_scope、geographic_scope、required_evidence、checkability、ambiguity、dependencies。這是語義契約，實際 JSON 欄位採現有 schema，額外欄位不得強塞進禁止擴充的結構。

claim_type 區別客觀、數值、因果、比較、預測、意見、價值判斷、不可驗證；checkability 說明可查條件及缺口。「將會成功」無時限或標準不能即判假。「世界第一」需領域、指標、基準與期間。

## 拆解例（合成）

「甲研發增 40%，所以技術超越乙，乙又抄襲甲。」拆成支出增幅、技術比較、公開成果使用、未授權／不當歸屬、支出導致領先五項。採用開源方法的證據不直接支持侵權；支出數字不證明性能。

dependencies 是推論依賴，不能讓上游 TRUE 自動傳播為下游 TRUE。因果項需額外設計證據。模糊詞影響判定時列數個明確版本，或請使用者指定；可先查無歧義部分。

## 交接檢查

拆解由 agent，標點切分只是候選句子。CLI 輸出未審查候選不能稱完整原子化。人工／agent 確認語義與原文一致後再送 Evidence JSON。數量多時優先重要且可查的主張，記錄未涵蓋範圍。
