# Truth Engine

從主張到證據的事實查核 Agent Skill，預設繁體中文，支援中英及跨語來源。拆解原子主張、追溯第一手資料、查數字與時間、搜尋反證，逐項輸出 TRUE／MOSTLY_TRUE／MIXED／MISLEADING／FALSE／OUTDATED／UNVERIFIED／NOT_CHECKABLE。

**本版是可用的 Agent Skill 加確定性 Python 工具，不是獨立自主的 LLM 服務。** Agent負責拆解、搜尋策略、語義分析和判定；CLI負責安全抓取、資料交接、驗證、運算及報告。貼文字給CLI不會自動完成研究或產生假判定。

## 安裝

Python 3.11+；程式採跨平台標準庫，實機驗證Windows。進入本專案目錄後：

```sh
python -m pip install -e ".[test]"
python scripts/cli.py --help
python scripts/validate.py
python -m pytest tests -q
```

媒體metadata選用：`python -m pip install -e ".[media]"`。正式依賴僅jsonschema；pytest為測試、Pillow為選配。

將完整truth-engine資料夾放在宿主的skills搜尋目錄。Codex預設為 `~/.codex/skills/truth-engine`；本次交付已安裝於目前使用者此路徑。其他支援Agent Skills的宿主使用各自的skill目錄；不保證所有宿主皆提供網路、OCR或相同工具。進入新聊天後可用 `$truth-engine`。

## 不需API Key的使用方式

```text
使用 $truth-engine 查證：這篇文章的數字與結論是否成立？請拆解主張並找原始資料。
Use $truth-engine to verify this article, trace its primary sources, and report counterevidence and uncertainty.
```

宿主Agent使用現有搜尋工具；Python Crossref探索也不需key。Google既有查核搜尋需環境變數 GOOGLE_FACT_CHECK_API_KEY（見.env.example），不可將key提交git；未帶key實測。Crossref metadata與其他查核結論均只是研究起點。

## CLI

```sh
python scripts/cli.py --claim "某公司研發費用增加了40%"
python scripts/cli.py --url "https://science.nasa.gov/moon/facts/" --mode deep
python scripts/cli.py --input article.txt --mode forensic
python scripts/cli.py --claim "某統計數字" --as-of 2026-10-01
python scripts/cli.py --search "blood pressure randomized trial" --provider crossref
python scripts/cli.py --search "example claim" --provider google-fact-check
python scripts/validate.py examples/live-moon-distance.json
python scripts/cli.py --evidence examples/live-moon-distance.json --format markdown --output report.md
python scripts/cli.py --evidence examples/live-moon-distance.json --format graph --output graph.json
```

前三種輸入預設產生 AWAITING_AGENT_DECOMPOSITION 的JSON，包含原文、時間和預算，不是完成報告；`--format markdown`可產待處理Markdown。URL輸入為未信任HTML／文字，不自動進行全文語義分析。Agent按Schema補齊資料後用`--evidence`驗證。日期預設採執行環境本地日，已知使用者時區或歷史案例請明確給`--as-of`。URL重新導向不自動跟隨。

## 模式、輸入與來源

| 模式 | 搜尋 | 來源 | 工具呼叫 |
|---|---:|---:|---:|
| QUICK | 3 | 5 | 12 |
| DEEP | 12 | 20 | 45 |
| FORENSIC | 25 | 40 | 90 |

每次搜尋、分頁、重試計預算。CLI單次請求有Budget；跨CLI及宿主工具整案預算由Agent記帳，不能假稱跨程序強制限制。達任一上限／證據足夠／不可存取則停止，保留缺口，不用無限搜尋。

文字、新聞、社群貼文、廣告、論文、圖表、財報及公開發言由Agent處理；PDF、影片、圖片或截圖需要宿主適當提取工具。來源優先原論文／數據、財報／交易所申報、法規／官方統計、事件原紀錄，再到獨立報導；既有查核與轉載不能取代原始證據。來源角色相對於主張，不因官方或知名就保證內容正確。

## 架構與支援矩陣

| 模組 | 已實作 | 邊界 |
|---|---|---|
| claim_parser | Agent主張資料契約、依賴檢查、文字交接 | 不以規則假裝理解自然語言 |
| search_adapters | 可換Provider Protocol、Crossref、Google Fact Check、安全HTTPS、Budget | 非全網搜尋引擎；Google需key |
| source_tracer / source_deduplicator | 引用鏈停止點、循環、URL／hash／來源家族去重 | 語義同源與獨立性需Agent確認 |
| temporal_checker | ISO日期／時區、as-of、發布與生效狀態 | 不猜未知發布時間 |
| statistics_engine | 百分比、CAGR、平均、中位、比例、風險比與差、口徑比對 | 不自動讀任意圖表／做統計推斷 |
| scientific_analyzer | 預印本、更正、撤稿與全文能力標記 | 完整研究方法由Agent審查 |
| media_checker | 本機hash、可選EXIF／格式、保守UNVERIFIED | 無生成影像鑑真、OCR、反搜或影片工具整合 |
| contradiction_analyzer / verdict_engine | 反證紀錄檢查、修正差異、保守判定旗標 | 不自行語義裁決，不稱分數為機率 |
| evidence_graph | 8類節點、引用與證據關係、懸空／重複ID攔截 | Graph輸出為JSON，無互動渲染器 |
| validate / report_generator / cli | Schema、引用、hash、可重算公式、逐項報告、時間線及搜尋歷程 | 格式正確不能證明外部內容真實 |

詳見 [SKILL.md](SKILL.md)、[JSON契約](references/report-schema.md)、[實際測試](VERIFICATION.md)。未知日期用null；URL缺失必填missing_reason。引用短句須精確出現在取得內容內，還需人工／Agent核對與原網頁一致。

## 展示

五份合成教學報告（未冒稱外網查核）：

- [研究被誇大](examples/science-claim.md)
- [財務錯誤比較](examples/business-claim.md)
- [多主張混合真假](examples/viral-news.md)
- [誤導統計](examples/misleading-statistics.md)
- [舊圖調查因來源不足而無法確認](examples/media-context.md)

另有 [NASA實際查核](examples/live-moon-distance.md) 與 [有效Evidence JSON](examples/live-moon-distance.json)，已實際讀取兩官方網頁；同機構不算獨立佐證。[離線獨立試用](examples/offline-financial-report.md) 與 [獨立評估](examples/independent-evaluation.md) 顯示另一Agent成功完成資料交接及報告。

## 驗證、安全與限制

2026-10-30 Windows／Python3.11：**56 passed**；Skill格式、Schema、CLI、Crossref實際請求、NASA讀取、wheel建置及隔離安裝通過。詳見VERIFICATION.md；不宣稱已在macOS/Linux實機測試。

外部內容不是指令；不執行來源程式、不自動下載執行PDF／影音。公共HTTPS連線固定已驗證IP、拒私有地址、拒redirect及非允許內容、限制時間與大小。仍須使用更新工具及宿主權限，不能聲稱完全免疫Prompt Injection或解析器漏洞。不追蹤私人位置、不無根據指控犯罪；醫療法律提供證據整理及限制。短引述並尊重著作權，key不入日誌或git。

未實作：獨立LLM後端、自動研究排程／全網研究迴圈、付費來源繞過、OCR與影片擷取、反向圖片API、影像鑑真模型、任意圖表自動解讀、完整統計檢定與校準信心機率。無網路仍可做本機交接、計算、驗證和報告，對外部事實保留UNVERIFIED。

## Roadmap

依需求增加有界搜尋Providers與重試策略、可隔離的PDF/OCR／影片轉接、撤稿資料源整合、多平台CI、報告圖視覺化與有實際標註資料的Agent行為評估。增加功能前先保持來源契約、權限邊界及可重現測試。

## 規格與官方API參考

- [Agent Skills規格](https://github.com/agentskills/agentskills/blob/main/docs/specification.mdx)
- [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)
- [Google Fact Check claims.search](https://developers.google.com/fact-check/tools/api/reference/rest/v1alpha1/claims/search)

本專案MIT授權，見LICENSE；外部來源內容仍適用各自授權。
