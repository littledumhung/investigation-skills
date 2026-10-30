# 合成影片取樣演練

本例素材由本機 ffmpeg 的 testsrc 產生，沒有真實人物／地點，不能用來證明地理定位。

```sh
ffmpeg -f lavfi -i testsrc=size=160x120:rate=10 -t 3 -pix_fmt yuv420p public-demo.mp4
python scripts/cli.py --input public-demo.mp4 --type video --text "分析合成影片可見線索" --scope public --extract-frames --output cases/video-demo
```

CLI 將保留定間隔取樣影格至 case/frames，原片不改寫；暫存區離開 context 後清理。測試 `test_video_frames_and_cleanup` 使用更短 0.5 秒間隔驗證三張影格及清理。

Agent 看圖後只應辨認為測試圖樣，不可捏造街景或真實拍攝地。真實影片應另外檢查字幕、浮水印、切鏡、剪接與前後畫面一致性，記錄原始時間軸；若精準時間重要需使用專門解碼工具，此版只給近似取樣時間。
