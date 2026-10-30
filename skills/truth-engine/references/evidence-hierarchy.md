# 證據層級與發現

按「對這個命題有多直接」排序，不按網站名氣投票。原始證據可能有偏見；證據量也不等於獨立性。

| 主張 | 優先資料 | 不能代替的內容 |
|---|---|---|
| 科學效應 | 論文全文、方法、補充資料、登錄、資料集；後續系統回顧 | DOI metadata 不能證明結論或同行審查 |
| 商業數字 | 財報、申報、交易所、IR、會議逐字稿 | 新聞轉述不能取代口徑及財年說明 |
| 法律政策 | 法條原文、公報、法院文件、官方版本 | 摘要不證明當前生效或適用管轄區 |
| 社會事件 | 原始紀錄、完整影片、公開聲明及獨立採訪 | 官方聲明可證明機構說過什麼，不必然證明事件 |
| 媒體上下文 | 早期可驗證版本、公開典藏、原檔、公共地標 | EXIF、搜尋排序或偵測器不能單獨證明真偽 |

Crossref 無 key 的 metadata 搜尋適合發現論文線索；agent 仍需讀出版商／原文。Google Fact Check optional key 搜尋既有查核及 ClaimReview，只是線索；核對它引用的原始資料。沒有 key 時保留 Crossref 與人工／agent 公開搜尋，不宣稱搜尋完整網路。

Provider adapter 交接需保存 provider、query、時間、頁碼／token、狀態、候選 URL 與錯誤；先查實作支援參數，不假定每站有 API。限制、配額、空結果與網路失敗分開記錄。搜尋摘要不能當讀過全文。

技術來源（非案例查核）：[Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)；[Google claims.search](https://developers.google.com/fact-check/tools/api/reference/rest/v1alpha1/claims/search)。僅確認介面用途，未驗證任一案例事實。
