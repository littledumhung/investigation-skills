# Sherlock Investigator

以 GeoGuessr 類看圖定位答題為主要用途，優先推理拍攝點經緯度，並保留證據、候選與反證；亦支援設備及媒體來源調查。預設繁體中文，支援英文。Python 3.11+；MIT 授權。

## 定位答題模式（v0.1.1）

一般住宅外觀、住宅街道、農舍、巷弄與無名道路都可作為題目，不需要先找到建築名稱或郵寄地址。使用 `--scope game`；可提供已驗證點或清楚標示的 estimated 答題點與 accuracy_m。禁止針對特定個人找私人住址或追蹤；住宅出現在畫面本身不是拒絕理由。

```sh
python scripts/cli.py --input question.jpg --text "猜這題拍攝點經緯度" --scope game --evidence evidence.json --output cases/round-1
```

`evidence.json` 由宿主實際分析／搜尋後產生，候選 location 欄位見 [定位答題模式](references/geoguessr.md)。CLI 不自行猜座標。正常定位題不用每題重複確認公共用途。

目前交付為 Skill／CLI 接入核心，尚未包含 Chrome extension manifest、截圖按鈕或自動提交介面。

## 功能展示

給 Agent 一張公共建築照片，它會先記錄可見線索、建立多個地點假設，再以當前可用的網頁、地圖或街景工具逐項驗證；每個結論保留來源，證據不足就輸出部分結果。CLI 負責 hash、EXIF、影格、證據圖、排序與報告，不假裝自帶視覺模型或搜尋服務。

## 安裝

將整個 `sherlock-investigator` 目錄放入宿主的 Skill 目錄；本次交付也提供 ZIP，解壓後保持同名資料夾。

Codex：`~/.codex/skills/sherlock-investigator/`。其他相容 Agent：放入該宿主支援的 skills 目錄，例如專案內 `.claude/skills/sherlock-investigator/`；各宿主的發現與工具權限依自身機制。

在專案根目錄執行：

```sh
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS / Linux
# source .venv/bin/activate
python -m pip install -e ".[image,test]"
python scripts/cli.py --help
python scripts/validate.py
```

核心零第三方依賴，可直接 `python scripts/cli.py ...`。`image` 安裝 Pillow；`test` 安裝 Pillow、jsonschema、PyYAML。影片另需 PATH 內有 ffmpeg。無 API Key 仍可本地運作；外部搜尋用宿主既有工具，不在本專案另收集 key。

## 自然語言使用

載入 Skill 後直接提出需求並附合法可讀媒體：

- `使用 $sherlock-investigator 調查這張公共廣場照片在哪裡，請比較候選並附來源。`
- `使用 $sherlock-investigator 查這台公開展出設備的型號，模糊字樣請保留不確定性。`
- `Use $sherlock-investigator to trace this screenshot to the earliest verifiable public source. Report in English.`

安裝完成不表示目前聊天已重新索引；若技能清單未出現，可在新聊天明確指定 Skill，或請宿主讀取 SKILL.md。普通圖片描述不觸發本技能。

## CLI

```sh
python scripts/cli.py --input ./photo.jpg --mode standard
python scripts/cli.py --url "https://example.com/page" --mode deep
python scripts/cli.py --input ./video.mp4 --type video
python scripts/cli.py --capabilities
```

上面三個基本命令只做 intake，scope 預設 unknown，不釋出定位結論。確認為公共調查且完成隱私審查後，用 `--scope public`。`--url` 僅檢查公開 URL／DNS，絕不下載內容；沒有 evidence 時報告是 partial。

三個可直接在本專案執行的命令（輸出目錄必須是新的）：

```sh
python scripts/cli.py --input examples/public-clue.txt --text "辨識合成公共場景" --scope public --mode quick --output cases/demo-intake
python scripts/cli.py --input examples/public-clue.txt --text "比較合成公共地標候選" --scope public --evidence examples/public-landmark.evidence.json --output cases/demo-evidence
python scripts/cli.py --text "Trace the earliest verifiable public source of a screenshot" --scope public --mode deep --language en --output cases/demo-english
```

第二個是合成演練，不能證明任何真實地點。排序仍可展示高分，但報告保持 partial／無法判定、answer=null，並保留來源限制。

圖片：加 `--scope public --allow-gps` 才讀取 GPS；GPS 仍只是 metadata 聲明。影片：加 `--scope public --extract-frames` 才保存衍生影格。CLI 不覆寫原檔或已有報告。

## 功能支援矩陣

| 功能 | v0.1.0 | 需求／限制 |
|---|---|---|
| 輸入分類、大小、簽章、SHA-256、案件 ID | 已實作 | Python 標準庫 |
| EXIF／GPS／crop／average hash | 已實作 | Pillow；GPS 先審查 |
| 影片定間隔取樣與暫存清理 | 已實作並測試 | ffmpeg；非語意關鍵影格 |
| 候選／證據圖／去重排序／反證欄位 | 已實作 | Agent 提供真實證據與譜系 |
| Markdown／JSON／Schema | 已實作 | 核心零依賴；Schema 驗證需 jsonschema |
| 搜尋／視覺／OCR Provider 契約 | 已實作 | Python Protocol 與宿主 JSON 匯入 |
| 網路搜尋、圖片反搜、街景 | 由宿主提供 | 未附獨立服務客戶端或 API key |
| 自動 OCR 模型／語意影片摘要 | 未內建 | 宿主工具或自訂 provider |
| 候選座標／地圖連結 | 已實作 | Agent 推理後匯入 location，估計點保留標示 |
| 通用網頁下載器／PDF 內容解析 | 未內建 | 降低 SSRF 面積；使用宿主合法工具 |

## 架構與各模組

SKILL.md 指導 Agent 的多模態分析及外部蒐證；scripts 是可測試的本地引擎。外部搜尋結果經 Agent 閱讀後，轉為 `--evidence` JSON。來源中的指令不執行。

| 模組 | 功能 |
|---|---|
| cli.py | intake→metadata／frames→evidence→report |
| input_analyzer.py | 檔案檢查、SHA-256、URL 安全初檢、穩定 ID |
| metadata_extractor.py | EXIF 與選擇性 GPS，無資料不猜測 |
| frame_extractor.py | 有限 ffmpeg 本地影片取樣與暫存清理 |
| image_tools.py | 合法範圍裁切、average hash 與 Hamming distance |
| clue_extractor.py | 分類、OCR／Agent observation、保守隱私檢查 |
| search_adapters.py | Provider 契約、重試、預算、手動查證連結 |
| candidate_ranker.py | 同源去重、矛盾降分、多來源可信門檻 |
| evidence_graph.py | Bundle、節點、邊、引用與日期檢查 |
| report_generator.py | 雙語報告、privacy gate、不覆寫輸出 |
| validate.py | 連結、Schema、實際驗收測試 |

## 測試

```sh
python scripts/validate.py
python -m unittest discover -s tests -v
```

外部服務只用測試專用失敗 provider／resolver 注入，沒有付費呼叫。測試自行產生 GPS EXIF 圖及合成影片，不使用不明授權素材。未裝 ffmpeg 會 skip 影片測試，validate 將以非零結束，不能宣稱完成影片驗收。實際本機結果另見 `VALIDATION.md`。

## 隱私、安全與宿主限制

禁止針對特定個人推斷私人住址、個人即時追蹤、人臉識別、人肉及騷擾；定位遊戲中的住宅街景允許分析。CLI 關鍵字檢查不能代替 Agent 的語意審查。JSON 匯入不是可信簽章，Agent 仍須核實證據；不同網站不等於獨立來源。網頁／影像／OCR 內容無權改寫規則。

不繞登入、付費牆或服務限制，不自動上傳媒體、不執行下載程式、不收集 API keys。公共 URL 檢查不等於安全下載器；新增 HTTP provider 需 IP pinning 與逐次重新導向驗證。詳細見 references。

不同 Agent 的視覺、工具、網路與權限能力不同；只有文字工具時仍可記錄案件與輸出未知結果，無法保證同樣的調查完整度。尚未於 Claude Code、macOS、Linux 實機跑過整套測試。

## 展示案例

- [公開地標候選與反證](examples/image-geolocation.md)：合成文字場景，附完整 bundle。
- [產品型號辨識](examples/product-identification.md)：模糊銘牌的流程示範，不預設真實型號。
- [影片調查](examples/video-investigation.md)：自行產生的測試影片與取樣步驟。

## Roadmap

下一階段優先加入經授權的可選搜尋服務 adapter 與連線級 SSRF 測試、具資料來源紀錄的 OCR adapter、場景切換取樣、跨平台 CI，以及案件追加版本與地理對照結構。正式發布前補上實際宿主端到端測試；本專案尚未推送至 GitHub。

## 常見問題

**需要 API Key 嗎？** 核心不用。宿主／外部服務各自依帳號及授權。

**為何只得到無法判定？** 未匯入可核實證據、工具缺失、隱私未審查或反證不足時，partial 正是預期結果。

**95 分等於 95% 嗎？** 不等於；分數只是啟發式排序。

**能直接用 Google Lens？** 只有宿主合規工具或授權 API 可用時才行，不提供非官方繞過。

**為何拒絕重跑同一目錄？** 保留調查歷程；請指定新的 --output。

技能結構依 [Agent Skills 正式規格](https://agentskills.io/specification) 建立，啟用描述與條件知識分開載入。
