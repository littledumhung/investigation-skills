# 歷史實體解析

標籤：SAME_ENTITY、POSSIBLY_SAME、RELATED_BUT_DISTINCT、DIFFERENT_ENTITY、UNRESOLVED。

證據物件：source_url、observed_at（本次觀察 UTC）、origin_id（原始斷言來源，鏡像共用）、kind、supports（布林）、detail；必要時另附事件日期和內容雜湊。origin_id 必須由 Agent 回溯確認；腳本不會自動識破抄襲。未知 origin 不能當獨立證據。

強證據 kind：official_rename、official_migration、repository_continuity、verified_identical_hash。弱證據如 title、appearance、same_domain、developer、mention 只能輔助。檔案 hash 同一不能單獨證明整個網站或公司同一；確保比對實體範圍一致。

阻擋條件：temporal_contradiction、official_distinct、ownership_discontinuity（supports=false）。直證與重大矛盾同時存在回 UNRESOLVED；不能靠更多重複支持票淹沒反證。直證加至少一個獨立來源、無矛盾才可 SAME_ENTITY；官方明示兩個不同作品可 DIFFERENT_ENTITY。僅名稱／外觀相同維持 UNRESOLVED。

`python scripts/cli.py --query "target" --plan-only --identity-evidence evidence.json --output case` 可對本機證據清單產生判斷。標籤是可稽核規則，不是機率，Agent 必須先檢查輸入事實；腳本無法證明「official」欄位真的官方。

確定 MOVED_TO／RENAMED_TO 關係需附 direct_evidence；否則用 POSSIBLY_SAME_AS。同網域隔年內容不同可能是換手；連續 UI 設計也可能是仿站，需作者／公告／版本歷史交叉驗證。
