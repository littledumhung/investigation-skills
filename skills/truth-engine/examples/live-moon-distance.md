# Truth Engine 查核報告

## 總結
月球與地球的平均距離約為384,400公里，有NASA官方科普資料支持。這是平均值，不能當成任一時刻的固定距離；本例由Agent實際查詢與讀取後建立JSON，CLI只驗證與格式化。

查核基準：2026-10-30；查核時間：2026-10-30T17:17:58.339121+08:00

## 主張拆解
- C1：地月平均距離約384,400公里。（NUMERIC；時間：一般軌道近似值，非即時距離）

## 逐項查核結果

### C1：TRUE
官方資料支持平均值，不支持固定距離的延伸解讀。
- 支持證據：
  - NASA資料列出平均距離384,400公里。 — [Moon Facts — NASA Science](https://science.nasa.gov/moon/facts/)；位置：Size and Distance
- 反面證據：
  - 未取得；不能解讀為不存在。
- 來源品質：NASA官方科普解說；非獨立重算原始測量。
- 限制：本例使用NASA官方科普頁，未重新分析軌道測量原始數據。；兩頁同屬NASA，不計作兩份已證明獨立的證據。；來源發布日期未驗證，保留null；取用時間不代表發布時間。

## 原始資料
- S1 [Moon Facts — NASA Science](https://science.nasa.gov/moon/facts/)；PRIMARY；發布：未知；更正：NONE_KNOWN
- S2 [How Far Away Is the Moon? — NASA Space Place](https://spaceplace.nasa.gov/moon-distance/en/)；PRIMARY；發布：未知；更正：NONE_KNOWN

## 是否存在誤導
參見各主張判定及限制；數值正確不代表比較期間、母體或因果推論成立。

## 查核可信程度
- C1：HIGH；NASA官方科普解說；非獨立重算原始測量。

## 目前無法確定的部分
- 本例使用NASA官方科普頁，未重新分析軌道測量原始數據。
- 兩頁同屬NASA，不計作兩份已證明獨立的證據。
- 來源發布日期未驗證，保留null；取用時間不代表發布時間。

## 更精確的說法
月球與地球的平均距離約384,400公里，實際距離會隨軌道位置變動。
