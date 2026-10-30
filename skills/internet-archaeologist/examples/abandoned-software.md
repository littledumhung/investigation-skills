# 展示三：Mozilla 以前的 Flash 相容工具

示範輸入：「Mozilla 曾有一個用 JavaScript 做的 Flash 專案，現在停更了，它叫什麼？最後版本是什麼？」查證日期：2026-10-30（Asia/Taipei）。

## 最可能找到的目標

**Shumway**，Mozilla 支持的 SWF 技術實驗。名稱與用途有官方 repository 直接支持；最後正式版本仍無法確認。這不是「Ruffle 的舊名」。

## 原始歷史資訊

[官方 repository](https://github.com/mozilla/shumway) 的說明可確認身分；GitHub 頁面顯示 2019-07-03 封存為唯讀。本次 API 顯示 created_at=2011-12-18，這只是 repository 建立時間，不能直接稱為專案首版日期。

## 找到的內容

```bash
python scripts/cli.py --repo mozilla/shumway --mode quick --output examples/results/abandoned-software
```

API 返回 25 筆：1 筆 repository 與 24 筆 sampled commits。releases／tags 查詢是空陣列，不等於「從未有版本」。[原始 JSON](results/abandoned-software/report.json) 保存 API 呼叫與證據。

| 欄位 | 結果 |
|---|---|
| 原名 | Shumway |
| 維護組織 | Mozilla repository；作者群以官方紀錄為準 |
| 技術／用途 | JavaScript SWF runtime 實驗 |
| 第一個有證據版本 | null，本次沒有版本標籤證據 |
| 最後已知正式版本 | null，本次 API 無 releases／tags |
| 本次 default-branch 頂端 commit | 16451d8836fa85f4b16eeda8b4bda2fa9e2b22b0 |
| 來源標示 commit 時間 | 2016-03-29T14:51:46Z |
| 是否開源 | 官方 repo 有 LICENSE；精確條款應讀檔案 |
| 已驗證安全的安裝檔 | null，未下載、未驗證、未執行 |

## 歷史時間軸

- 2011-12-18：GitHub repository 建立紀錄，不是首發版本。
- 2016-03-29：本次 default branch 頂端 commit 的 committer 日期；不是「最後發布」。[commit](https://github.com/mozilla/shumway/commit/16451d8836fa85f4b16eeda8b4bda2fa9e2b22b0)。
- 2019-07-03：GitHub 頁面顯示 owner 封存日期；不是已證明的最後開發日。

## 為什麼認為是它

Mozilla 組織、JavaScript、SWF runtime 三個關鍵條件都符合官方 repo。對這個具體描述，Shumway 是明確對應目標；但「同一實體跨名稱延續」仍需獨立證據，不憑 repo 數據自動給 SAME_ENTITY。

## 其他可能候選

[Ruffle 官方網站](https://ruffle.rs/) 也提供 Flash 相容方案，屬相關但不同專案。本次 [Ruffle API 研究](results/software-history/report.json) 顯示 ruffle-rs/ruffle repository，描述 Rust 實作；不能把它與 JavaScript 的 Shumway 混同。它可以作現代研究方向，不保證相容每一個舊作品。

## 可信程度、缺失與下一步

名稱／官方身份信心高；最後正式版本與歷史安裝檔安全性無法判定。沿官方 changelog、網站存檔與 Firefox 歷史整合紀錄繼續查，才能回答具體發布版本問題。本次不下載 README 提及的舊擴充檔，不把 commit SHA 當發布版本。
