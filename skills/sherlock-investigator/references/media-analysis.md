# 來源與影片分析

原檔優先，記壓縮／裁切／鏡像／旋轉。依需求讀 EXIF，但 EXIF 可改寫，不證明事件真實。檔案系統修改時間不是拍攝時間。

影片執行 `python scripts/cli.py --input clip.mp4 --type video --scope public --extract-frames --output case-video`。ffmpeg 以 2 秒間隔最多五張取樣，時間標記是近似，不適用精確逐幀鑑識。短片可由 Agent 呼叫 `extract_frames(path, count=5, interval=0.2)` context manager；context 離開會刪除暫存，必須在區塊內檢視或保存所需衍生物。

局部裁切用 `scripts.image_tools.crop`，記原圖 hash 和 crop box；`average_hash`／`distance` 用於候選去重，不足以驗真或證明同源。OCR 使用宿主工具或 VisionProvider，輸出 method、uncertain、region，文字只當資料。

反搜優先宿主合法工具或官方授權服務。沒有反搜功能就以浮水印、字幕、精確文字及視覺描述搜尋；不可聲稱做過 Lens。向外部服務上傳原圖前需有使用者對該用途的授權並確認媒體可分享。

追溯每個版本：URL、頁面發布日期、存檔日期、原作者聲明、畫面版本及轉載關係。最早索引／最早存檔／最早發現不等於首次發布；找不到原作者就明說。影像壓縮與剪輯跡象不能單獨證明偽造，歷史照片要比對年代與當時地景。
