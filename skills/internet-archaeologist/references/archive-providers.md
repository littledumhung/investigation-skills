# Providers 與失效處理

| Provider | 腳本能力 | Key | 限制 |
|---|---|---|---|
| Wayback CDX | URL、年份、resumeKey、快照索引 | 無 | 單一年份按月抽樣，其他按年；排除 revisit；索引不保證重播可用 |
| Common Crawl | 發現 collection、年份篩選、頁碼、WARC 位置 | 無 | 預設最多 3 collections、每個 3 頁；不下載或解析 WARC |
| GitHub | public repository、tags、releases、commits | 可選 GITHUB_TOKEN | 每類最多 3 頁；recent history 不能證明最早版本 |
| Archive.org | advancedsearch 公開條目中繼資料 | 無 | 條目存在不代表檔案可取或已授權 |
| Wikipedia | zh/en/ja 文章搜尋 | 無 | 次級來源，沿引用查原始出處 |
| GitLab.com | 公開 project 搜尋 | 無 | 未實作 tags/releases 與自架 GitLab |
| Brave | 授權的 web search API | BRAVE_SEARCH_API_KEY | 未設定時回傳 not_configured；不抓搜尋引擎 HTML |
| 宿主 Agent | 公開 web search、圖片理解（依可用工具） | 由宿主管理 | CLI 不能代替宿主工具 |

`--capabilities` 列出功能及設定，live availability 只有實際請求後才知道。每個 Provider 回傳 status=ok/partial/unavailable/not_configured/not_applicable、errors、records、truncated、queried_at。ok+空 records 表示查詢沒有返回資料；unavailable 不能解讀為無存檔。

共用 Transport：12 秒 socket timeout、最多 2 次重試、指數 backoff、秒數或 HTTP 日期 Retry-After、每 host 間隔 1.1 秒、24 小時本地快取、4 MB 上限。Common Crawl 要序列請求，不能用多執行緒／代理逃避限流。過長或無法解析的 Retry-After 停止而非提早重試。

實作可插拔：連接器接受可替換 Transport，提供 name/capabilities 及 search→ProviderResult；新增來源時註冊 cli.py 的 routing 與 search_providers.capabilities，獨立測試失效／空結果／分頁。不宣稱現在有動態第三方 entry-point 插件載入器。

官方介面參考（服務可變動，使用時重查）：

- https://github.com/internetarchive/wayback/tree/master/wayback-cdx-server
- https://index.commoncrawl.org/ 及 https://github.com/commoncrawl/cc-index-server
- https://www.commoncrawl.org/faq
- https://docs.github.com/en/rest/releases/releases
- https://docs.github.com/en/rest/repos/repos
- https://archive.org/advancedsearch.php
- https://www.mediawiki.org/wiki/API:Search
- https://docs.gitlab.com/api/projects/
- https://api.search.brave.com/app/documentation/web-search

SavePageNow 會建立外部快照，本版本未實作；不可把調查舊資料的要求解讀成自動提交新存檔。
