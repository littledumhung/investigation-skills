# 設備型號演練

示範輸入：「公開博物館設備銘牌看似 X1O，右側三個圓形接頭；請辨識型號。」這是文字流程範例，沒有實際照片或已查證型號。

1. 記 observation：「X1O／X10 未確認」，method=ocr 或 manual，uncertain=true。
2. 候選先保留 X1O 與 X10；沒有真實候選時不能憑字串造廠商。
3. 用宿主搜尋精確銘牌＋museum／manufacturer／manual，打開官方圖或手冊。
4. 比接頭數量、面板與年代；搜尋地區版、改裝及同型號異物。
5. 如果三個接頭的照片未取得，unverified 不清空，不能高可信。

可執行的離線起點：

```sh
python scripts/cli.py --text "公開博物館設備銘牌 X1O 或 X10，三個接頭，查型號" --scope public --output cases/product-demo
```

預期 partial／無法判定，而非任意品牌答案。取得實際來源後依 report-schema 建 bundle，再用新的 --output 匯入。
