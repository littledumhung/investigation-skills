# 獨立 forward-testing 評估

實際可用性：agent 完成語義工作後，現有 CLI 的 Evidence JSON → 驗證 → JSON／Markdown／證據圖流程成功，沒有阻塞。僅用題目合成數據，全程未連線、未補來源、未讀其他測試結果或 examples；所有 Python 呼叫均用 -B，子程序另設 PYTHONDONTWRITEBYTECODE=1。未修改專案程式、schema 或文件，產物僅寫本 independent 目錄。

## 查核結果與責任邊界

- C1、C2：UNVERIFIED。100與50是題目給定的合成前提，不能當真實公司財報已驗證。
- C3：MISLEADING。現有 statistics_engine 重現 (50−100)/100×100 = −50.0000%；但全年與單季期間不同，不能推導同比或環比暴跌。未將季度乘四冒充實際全年數字。
- C4：UNVERIFIED。兩筆收入不構成管理層詐欺證據，亦不證明沒有詐欺。

原子拆解、口徑辨識、反證策略、證據關係、信心與結論均由本 agent 完成。程式執行數值公式、schema／引用／日期／圖檢查及排版；驗證通過不等於事實或法律認定成立。唯一來源 url:null、missing_reason:'user supplied synthetic'、accessible:true、content 為完整原題，hash 由 UTF-8 原文計算，沒有假造URL。

## 實際執行結果

CLI --help 與 validate.py --help 已實際執行，stdout 存 execution-log.json。首輪正向流程全部 exit 0；最新重跑 validator、JSON、Markdown、graph 全部 exit 0。最新 claims schema minItems=1，真實 content hash 通過。

有界負控制：首輪錯誤計算結果被 CLI 拒絕（exit 2，僅泛化 ValueError），直接 validator exit 1，明確訊息 Calculation cannot be reproduced。最新空 claims 與錯誤 content hash 各執行一次 validator，預期拒絕，具體 stderr／traceback、exit code、執行起訖時間與前後 scripts/schema SHA-256 全存 execution-log.json；摘要見 final-validation.json。這些是刻意無效輸入，不是主流程失敗。

## 非阻塞限制與版本觀察

1. --input --format markdown 實際仍輸出 JSON，status=AWAITING_AGENT_DECOMPOSITION、claims=[]，exit 0。這是交接 intake，不能稱已自動產生查核報告；需要 agent 填好 Evidence JSON 後走 --evidence。
2. 首輪 URL:null 在 Markdown 形成 缺失URL的錯誤連結 連結，保留於 report-first-pass.md。最新 report_generator 已改為明示無URL及 missing_reason；重跑的 report.md 已不含此連結。因此首輪問題非阻塞，且最新版本已改善。
3. CLI 驗證失敗僅顯示泛化錯誤；需直接 validate.py 才能看到具體原因。本輪已保存兩者實際錯誤。
4. 最初讀取三份 references 回傳 Cannot find path（該 PowerShell 呼叫 exit 1）；使用者說明 sidecar 仍生成中，故只記錄暫態，不列最終缺陷。未以初始缺漏推定最新狀態。
5. 專案存在其他生成者；本 agent 僅唯讀。首次雜湊快照至首輪結束所檢查48個檔案相同；後續版本的 hash 差異不能歸因於本 agent。readonly-before.json、readonly-verification.json、latest-version.json 與逐命令版本雜湊保存可得版本證據。首輪 subprocess log 沒有逐命令時間／hash，只有原始快照與 Evidence checked_at 可供參照；不能事後補造精確執行時刻或宣稱首輪每次都用相同版本。
6. 「53 tests」僅為使用者提供資訊，本 agent 未執行或引用其結果。沒有進行無關廣測，也沒有檢驗搜尋、OCR 或外部服務能力。

## 產物

同目錄 evidence.json、agent-evidence.json、report.md、report-first-pass.md、evidence-graph.json、execution-log.json、final-validation.json、latest-version.json、readonly-before.json、readonly-verification.json、context-comparison.json、input.txt，以及隔離的負控制 JSON 與執行腳本。execution-log 保存實際命令、stdout、stderr、exit code；最新輪附時間與版本雜湊。負控制不屬可採用的查核結果。

## 最後版本更正（parent 實測）

使用者通知修正後，parent 再執行 cli.py --input input.txt --format markdown，exit 0，實際輸出 Markdown「Truth Engine 待處理資料」，明示 AWAITING_AGENT_DECOMPOSITION、尚未查核或判定。輸出保存 ../intake-latest.md。上文第1項與 final-validation.json 的 intake_markdown_is_json 屬前版觀察，已不代表目前缺陷。null URL 呈現亦已修正。文件 sidecar 尚生成中，不列缺陷。其餘已觀察問題為 CLI 對無效 Evidence 只提供泛化錯誤；直接 validate.py 可取得具體原因。未發現本案例主流程另有阻塞。

## 交付版本註記
本頁保存獨立評估的版本觀察；文中內部執行紀錄位於開發工作區，未全部納入可攜套件。最終交付已修正intake Markdown與缺失URL呈現，validate.py改為不回顯原文的欄位／完整性錯誤。可直接重跑本套件tests與兩份Evidence JSON；最終實測以VERIFICATION.md為準。
