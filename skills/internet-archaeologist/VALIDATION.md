# 實際驗證紀錄

日期：2026-10-30（Asia/Taipei）。環境：Windows、Python 3.11.15。macOS、Linux、Claude Code 未在本次環境執行；相容性來自標準函式庫與檔案格式設計，不是實測承諾。

## 離線測試

`python scripts/validate.py`：**50 tests，全部通過**。測試沒有網路、Key 或未知程式執行；FakeTransport 與合成 observation 明確限於測試。

覆蓋需求 17 種情境：多年份快照、無存檔、404、網域換手、跨語言名稱、外觀相似不同遊戲、repo 改名、第三方殘存引用、殘缺 HTML、五年記憶範圍、發布／快照日期區隔、API 失效、prompt injection、未知安裝檔、UNRESOLVED、同源去重、年代矛盾阻擋。

另外驗證 CDX 兩種 resume 格式、重試／預算、快取、私人位址與 redirect、HTTPS 降級、Key 回應不落快取、graph 來源要求、Markdown 反證、錯誤 evidence 結構等。`python -X utf8 .../skill-creator/scripts/quick_validate.py internet-archaeologist`：**Skill is valid!** Windows 的舊版 validator 預設 cp950，因此用 -X utf8；不需要修改 skill 成其他編碼。

## 獨立行為驗證

獨立 reviewer 在 work/review 隔離資料夾，以禁止網路／mock transport 跑模糊遊戲、惡意歷史 HTML、同源矛盾與 chronology 案例。首次找出四個確定問題：去重誤丟反證、弱外觀線索門檻、HTTPS 降級帶憑證、Markdown 未列反證。全部修正並加入回歸測試；reviewer 再測無剩餘可重現失敗。其複查時為 48 tests，之後增加兩項 evidence 輸入／負向關係測試，最終為 50。

## Live smoke tests

以下數量是本次取得紀錄，非完整來源總數。原始中繼資料與網路 log 在 examples/results/*/report.json；所有 target identification 預設維持 UNRESOLVED，需 Agent 閱讀與整合。

| 案例 | 實際結果 | 限制 |
|---|---|---|
| example.com / 2015 / QUICK | Wayback 8 筆，Common Crawl 0 筆 | Wayback 月份抽樣且達 QUICK 限額；CC 僅抽 3 collections |
| example.com / 2015 / RECONSTRUCT | Wayback 12 筆月份抽樣，兩份 HTML 成功取得、preview／diff 已產出 | 不抓 CSS、圖片或完整 UI |
| ruffle-rs/ruffle / QUICK | GitHub 73 筆 repository／releases／tags／commits | 各類最多三頁，結果截斷；不是停更專案 |
| mozilla/shumway / QUICK | GitHub 25 筆，repo archived=true，release/tag 為空，24 筆 commits | 不把 commit 稱為最後正式版本 |
| flash puzzle game blue block | Archive.org 8 筆、Wikipedia 8 筆 | 廣義中繼資料雜訊多，不等於候選確認 |

首次 Wayback live response 使用 JSON 尾端 resume 列，導致初版解析回 partial；已修正並重跑。本次早期 Common Crawl 回 504；重跑回應正常但抽樣結果為空。不能把短暫失效說成永久不支援，也不能把抽樣空結果說成從未存在。

Agent 額外閱讀 Red Remover 作者平台、Kongregate、Bloxorz 平台、Shumway 官方 repo、Ruffle 官方網站，整合於三份展示案例。沒有下載或執行遊戲、SWF 或安裝檔。

## 尚未驗證／未實作

- Brave：沒有配置 API Key，僅測未設定時的明確錯誤，未做 live 搜尋。
- GitLab：已實作公開 project 搜尋與錯誤處理，本次未做 live smoke test。
- Wiki zh/ja：程式提供 language 參數，本次 live 使用 en，沒有逐語言實測。
- 圖片理解、OCR、反向搜圖：依宿主工具，Python 沒有此能力。
- 完整 CSS／圖片重建、WARC 擷取、SavePageNow、自動執行歷史程式：本版本未提供。
- 任意自然語言的跨語翻譯、多輪搜尋、來源獨立性鑑定：依 Agent；小型詞彙表與規則引擎不能取代它。

## 建議改進

優先增加跨平台 CI、provider contract fixtures、可持續分頁、WARC 內容擷取、更多查詢詞與候選特徵 schema。實際研究時依服務規則調整預算，不以重試或新 CLI 規避限流。
