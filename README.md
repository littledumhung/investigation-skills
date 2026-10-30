# Investigation Skills

由 [littledumhung](https://github.com/littledumhung) 維護的個人 Codex skill 工具箱，包含三個完整 skill 與各自的 Python 工具、參考資料、範例和測試。

| Skill | 用途 | 文件 |
| --- | --- | --- |
| Sherlock Investigator | 看圖定位、GeoGuessr 座標推理、物品及媒體來源調查 | [使用說明](skills/sherlock-investigator/README.md) |
| Internet Archaeologist | 尋找消失網站、舊遊戲、軟體與歷史網頁 | [使用說明](skills/internet-archaeologist/README.md) |
| Truth Engine | 主張拆解、來源查核、反證及證據報告 | [使用說明](skills/truth-engine/README.md) |

## 安裝到 Codex

需要 Python 3.11+、Git，以及支援 skills 的 Codex 環境。在終端機執行：

```sh
git clone https://github.com/littledumhung/investigation-skills.git
cd investigation-skills
python -m pip install -r requirements.txt
python tools/install_skills.py
```

安裝工具尊重 `CODEX_HOME`，預設複製到 `~/.codex/skills`。已有同名 skill 會停止，不會覆蓋；若要保留舊版，可先將舊資料夾移到 skills 目錄外備份。可指定 `--dest /path/to/skills`，或用 `--dry-run` 預覽。安裝後開啟新對話使用。

```text
使用 $sherlock-investigator 分析這張看圖定位題，給我座標、依據與誤差範圍。
使用 $internet-archaeologist 找回我記憶中的舊網站，整理候選與存檔證據。
使用 $truth-engine 查證這段說法，找原始來源並搜尋反證。
```

## Python 工具與相關套件

`requirements.txt` 提供 jsonschema（報告驗證）與 Pillow（圖片處理）；`requirements-dev.txt` 另含 pytest、PyYAML。各 skill 的 `pyproject.toml` 保留套件定義。

三個原始套件都使用頂層模組名稱 `scripts`，因此請在各 skill 資料夾內直接執行 CLI；如需 `pip install .` 與命令列入口，每個套件須使用獨立虛擬環境，避免互相覆蓋。

```sh
cd skills/truth-engine
python scripts/cli.py --help
```

Sherlock 影片抽幀另需系統安裝 ffmpeg 並加入 PATH。搜尋、地圖、街景、OCR 與圖片理解取決於宿主提供的工具；這些 Python 套件本身不是自主研究模型。各 `.env.example` 僅供選用 API 設定；一般由宿主搜尋工具啟動，不需另買 API key。

## 驗證

```sh
python -m pip install -r requirements-dev.txt
python tools/validate_all.py
```

驗證工具以獨立程序執行三套測試，避免 `scripts` 模組衝突；缺少 ffmpeg 的影片測試會顯示 skipped。GitHub Actions 在 Ubuntu 與 Windows、Python 3.11 / 3.12 執行相同檢查，並安裝 ffmpeg。

各 skill 內的 VALIDATION.md / VERIFICATION.md 是原始版本的驗證紀錄；Internet Archaeologist 的執行產物 `examples/results` 不納入版本控制，可依範例重建。

## 授權

三個 skill 保留原始 MIT 授權及著作權聲明，詳見各資料夾的 LICENSE。本 repo 的整合工具與文件亦採 [MIT](LICENSE)。相依套件與外部服務各依自身授權和條款提供。
