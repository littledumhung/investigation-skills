# 能力盤點與 Provider Adapter

| 能力 | 內建 | 替代路徑 |
|---|---|---|
| hash／案件／輸入檢查／報告／評分 | Python 標準庫 | 可離線 |
| EXIF／crop／average hash | 選配 Pillow | 宿主讀圖，不虛構 metadata |
| 影片取樣 | 選配 ffmpeg | 宿主影片工具或提供影格 |
| 視覺推理／OCR | VisionProvider 契約 | 宿主工具；沒有則保留未知 |
| 網頁／圖片／反搜／地圖／街景 | SearchProvider 契約 | 宿主工具＋JSON 證據匯入 |
| 地理編碼／Overpass／Commons／存檔 | capability 標記 | 合法公開資料工具或手動連結 |

宿主工具接入是本版主要可用路徑：Agent 呼叫當前工具 → 閱讀來源 → 寫 JSON → `--evidence` 匯入。工具結果不得直接當可信結論。

Python 自訂接入：實作 `name`、`capabilities: set[str]` 及 `search(query, capability, timeout) -> list[dict]`，將實例傳給 `Research([provider], mode='standard')`。成功回傳結果至少含 url、title、snippet、retrieved_at；失敗丟 ProviderUnavailable／TimeoutError／ConnectionError。Research 重試一次並留不含 API key 的失敗紀錄。空陣列代表未找到，不是支持或反對。CLI 不從任意模組路徑動態載入 provider。

例如宿主已輸出 JSON，Agent 直接把來源轉入 bundle，不需額外 SDK。不得把固定測試 Fixture 註冊成正式搜尋服務。API keys 由提供者自身管理，核心不載入 .env、不記 URL query 或秘密。

任何新增 HTTP provider 必須：驗證 HTTP(S)、拒絕 credentials／內網 IP、對 DNS 所有 A/AAAA 做公開性檢查、連線 pin 受驗 IP、保留 TLS hostname 驗證、每次重新導向重新審查、限定 bytes、timeout、content type，避免代理環境繞過。`validate_url` 是 intake 防線，不是完整安全 fetcher；本版沒有通用 HTTP 下載器，因此不會由 CLI 發起 SSRF HTTP 連線。DNS 查詢本身受作業系統 resolver 控制，未設可攜硬逾時。

Google Lens／Maps／Street View 不假設有通用免費 API；只有既有合規宿主能力或授權 API 才使用。無工具時提供 manual_links 並標未執行。不要繞過登入、robots／服務限制或付費牆。
