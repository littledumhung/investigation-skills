# 實際驗證紀錄

v0.1.1 定位答題更新：`python scripts/validate.py` 實際通過 33 項測試、零跳過。新增 game 情境（允許住宅街景／仍阻擋人物追蹤）、座標答題報告、非法經緯度拒絕。原 30 項測試持續通過。未製作瀏覽器擴充套件介面。

日期：2026-10-30（Asia/Taipei）。Windows、Python 3.11.15；已具 Pillow、jsonschema、PyYAML 與 ffmpeg。

實際執行：

```text
python scripts/validate.py
Ran 30 tests
OK
JSON Schema: validated
exit code 0; no skips

python -X utf8 <codex-skills>/.system/skill-creator/scripts/quick_validate.py outputs/sherlock-investigator
Skill is valid!
exit code 0

python -m pip install --no-deps --no-build-isolation --target work/sherlock-package-test ./outputs/sherlock-investigator
Successfully built sherlock-investigator-skill
Successfully installed sherlock-investigator-skill-0.1.0
exit code 0
```

打包測試驗證 wheel 建立與隔離安裝；其後報告修正由最終 30 項測試覆蓋。完整 Skill 請用 ZIP 或整份目錄安裝，wheel 僅是 Python helper。

| 驗收 | 實測 |
|---|---|
| GPS EXIF | 自行產生 JPEG，座標讀取比對 |
| 無 EXIF | GPS=None，不虛構 |
| 相似地點／反證 | 合成 H2 因道路矛盾降至負分 |
| OCR 不確定性 | 保留 uncertain，限制正向分數 |
| 同源轉載／單源 | 十份鏡像只計一組，不能高可信 |
| API 失效 | Mock timeout 重試，partial 報告 |
| 影片 | 實際 ffmpeg 合成／解碼、三張影格與清理 |
| 解碼逾時 | Mock TimeoutExpired 可降級 |
| URL | scheme、credentials、ports、IPv4/IPv6、混合 DNS 拒絕 |
| Injection | 來源字串不執行，HTML 逸出；不代表 LLM 全面免疫 |
| 私人定位 | 拒絕且不讀媒體／不輸出候選 |
| Schema | Draft 2020-12、日期格式、非法可信度被拒 |
| 跨平台路徑 | Windows/Unix 名稱、Windows 中文空白實際檔案 |
| 離線 | resolver 封鎖時本地 CLI 仍可執行 |

獨立 Agent 已按 Skill 完成合成案例，正確指出無法證明真實地點。發現的合成候選可信度、逐項標示、替代候選反證摘要問題已修正並測試。試用曾用系統 TEMP，未完全符合指定工作目錄隔離，未碰外部服務。

quick_validate 初次受 Windows cp950 影響，改用 `-X utf8` 正常；環境說明移入正文以相容該驗證器。最終 Skill 驗證通過。

未實測：真實世界定位準確率、第三方反搜／街景／OCR、自訂 HTTP provider、Claude Code、macOS、Linux。不得宣稱這些已驗收。
