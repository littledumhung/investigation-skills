# 合成公共地標演練（非實地調查）

輸入 `public-clue.txt`：兩個拱門、道路右彎。兩個候選都具拱門，不能僅憑外觀判定。

演練中的 plan-a 與 survey-a 是明確標示 synthetic 的獨立測試來源；A 的拱門與道路都相符，B 的直路則與輸入矛盾。資料來源只用作驗證引擎行為，不代表真實網站、真實地點或真實地圖座標。

```sh
python scripts/cli.py --input examples/public-clue.txt --text "合成地標候選比較" --scope public --evidence examples/public-landmark.evidence.json --output cases/landmark-demo
```

讀 `report.json`：H1 分數 8、H2 分數 -3。合成來源與其限制必須保留；不提供真實座標。把此流程換成照片時，先實際讀圖，再查官方平面圖與合法街景工具，不能沿用合成證據。

下一步：以有授權的公共地標照片進行宿主端到端測試，記實際來源與反證。
