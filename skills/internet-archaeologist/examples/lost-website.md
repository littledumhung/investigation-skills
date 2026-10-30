# 展示一：調查舊網址在 2015 年的痕跡

示範輸入：「https://example.com 在 2015 年留下哪些存檔？」這是文件用途網域，不假稱它是已關閉網站。查證日期：2026-10-30（Asia/Taipei）。

## 最可能找到的目標

本次目標為指定 URL 的存檔記錄；並未執行跨年代所有權身分確認。最早快照不等於創立。

## 原始歷史資訊與找到的內容

```bash
python scripts/cli.py --url https://example.com --year 2015 --providers wayback,commoncrawl --output examples/results/lost-website
```

實際回傳狀態、數量、原始 snapshot URLs 與失敗原因保存在 [report.json](results/lost-website/report.json)／[report.md](results/lost-website/report.md)。最新執行取得 8 筆 Wayback 月份抽樣（QUICK 限額），並不是全量存檔。Common Crawl 首次請求遇到 504；稍後重跑可回應，但抽樣 3 個 collections 內返回 0 筆，不能解讀為所有年代都沒有保存此網站。

第一次 live probe 揭露 CDX JSON 會把 resume token 放在表格尾部的空列與單欄列中。解析器已依真實回應修正，加入回歸測試並重跑；不是把錯誤資料補成假快照。

## 歷史時間軸

每個 captured_at 與 archive_url 都由實際索引列轉換。僅能說「本次抽樣中最早／最晚」，不能說網站在最早日期創立、最晚日期關站。索引的 status=null 也不能改寫成 200。

## 為什麼認為相關、其他候選與可信程度

這些是指定 URL 經 Wayback 索引回傳的記錄，可信範圍是「存在索引紀錄」。HTTP／HTTPS、www 等歷史變體仍保留原值；不把目前 DNS 或 URL 相似性當作過往經營者相同的證明。沒有其他需要憑空建立的候選。

## 尚未找到與下一步

本次 Common Crawl 結果僅涵蓋部分 collections，也沒有確定所有歷史資源可用。想核對實際文字可看 [重建案例](website-evolution.md)；要找搬站或換手則應再查官方聲明與相鄰年代。API 故障、抽樣空結果與從未存在分開呈現。
