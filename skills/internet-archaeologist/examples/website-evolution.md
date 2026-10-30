# 額外展示：歷史 HTML 文字重建

示範輸入：「把 example.com 2015 年抽樣快照的內容做比較。」查證日期：2026-10-30（Asia/Taipei）。

```bash
python scripts/cli.py --url https://example.com --year 2015 --providers wayback --mode reconstruct --output examples/results/website-evolution
```

## 目標與找到的內容

真實執行產生 [report.json](results/website-evolution/report.json)、[第一份文字預覽](results/website-evolution/preview-1.html)、[第二份文字預覽](results/website-evolution/preview-2.html) 與 [diff.json](results/website-evolution/diff.json)。所有日期與重播網址以 JSON 中本次成功取得的記錄為準。

## 原始歷史與時間軸

Wayback 以月份抽樣 2015 年，本次最多抓最早及最晚可用的 text/html 兩份。這可跨月份比對，不能證明每次改版都被涵蓋。captured_at 是索引快照日期，並非內容發布日期。

## 比對依據與可信程度

標題由已擷取 HTML 解析，差異只根據觀察到的文字與資源參考。文字無差異時，只代表這兩份抽樣文字一致，不代表全年沒有 CSS、版型或功能改動。這是可稽核的文字抽取，沒有推定完整畫面。

## 其他候選、缺失與下一步

本例只研究指定 URL，無需捏造候選。外部圖片／CSS 沒有抓取或驗證；缺少的資源不會被畫成假原始頁面。要研究更細的改版需改用更窄日期範圍或擴充抓取策略，並遵守總預算。

預覽是逃逸後的惰性文字，保留 CSP，無腳本、frame、form 或主動網路資源。不要把預覽稱作原站精確還原。
