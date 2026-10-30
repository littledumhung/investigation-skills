# 驗證紀錄

2026-10-30，Windows / Python 3.11。以下為本次實際執行，並非跨平台實測宣稱。

- `python -m pytest tests -q`：56 passed。
- `python -X utf8 <skill-creator>/scripts/quick_validate.py <skill-folder>`：Skill is valid。Windows cp950 環境需 `-X utf8` 讀取繁體中文文件。
- `python scripts/validate.py`：Schema 通過。
- CLI help、文字交接、as-of、來源搜尋、URL 擷取、證據 JSON 驗證、Markdown 與 graph JSON：已執行成功。
- Crossref 實際 API 搜尋成功；結果僅 metadata，不當作全文或研究結論。
- NASA 官方兩頁實際擷取並核對；完整結構見 `examples/live-moon-distance.json`，報告見同名 Markdown。未宣稱兩個同機構網頁相互獨立。
- Python wheel 建置、隔離安裝與隨套件 Schema 載入成功；不是只測 editable install。
- 獨立 Agent 在禁止連線、僅合成素材條件下完成財務案例；驗證 JSON / Markdown / graph 成功，錯誤計算、空主張、錯誤內容雜湊被拒絕。見 `examples/independent-evaluation.md` 與 `offline-financial-evidence.json`。

## 驗收範圍

自動測試涵蓋：多筆agent主張資料及依賴；意見分型保護；缺證據不判假；第一手與轉載來源鏈；同源去重；時間範圍／日期缺失／失效；百分比、CAGR、風險比與風險差；比較期間；撤稿與更正；預印本狀態；來源不可存取降級；引文內容存在性；反證搜尋紀錄／結論修正；相同結構政治主體一致；混合主張報告；Schema／證據連結／圖／內容雜湊／計算重現；SSRF、重新導向、回應大小與工具預算。

測試不能證明任意LLM的拆解、因果判斷、政治中立或Prompt Injection抵抗力。來源檔被當成資料、不執行任意程式，是程式層保護；Agent仍必須遵守SKILL的信任邊界。JSON通過也不能證明來源內容真實或完整。影像缺乏出處時不得宣稱真實；本版無自動影像鑑真模型。

## 已知限制與降級

無獨立LLM服務、自動網路研究迴圈、全網搜尋引擎、付費全文下載、OCR／影片關鍵影格或反向圖片搜尋整合；由宿主Agent現有工具承接。統計工具處理可重現基本運算與比較口徑，不自動辨讀任意圖表或重建統計檢定。Google Fact Check 需自備key，未進行帶key實測。macOS/Linux未實機驗證。

CLI格式化與資料工具不需要API key；JSON Schema套件需要安裝。外網不可用仍可處理本機資料、計算、驗證與報告，並保留UNVERIFIED。CLI錯誤訊息刻意不回顯遠端URL或key；需定位資料錯誤時使用 `python scripts/validate.py report.json`，驗證器會輸出欄位路徑或固定完整性錯誤，不回顯整份來源內容。
