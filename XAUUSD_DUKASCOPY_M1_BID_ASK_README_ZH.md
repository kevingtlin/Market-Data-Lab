# XAUUSD Dukascopy M1 Bid/Ask 歷史資料說明

產生時間：2026-06-24 20:24:09 +08:00

這份資料是從 Dukascopy 透過 `dukascopy-node` 下載的 XAUUSD 一分鐘 K 線歷史資料，包含 `bid` 與 `ask` 兩份價格。用途主要是策略研究、回測、交易成本估算，以及後期比較接近實盤成交邏輯的驗證。

## 資料是什麼

- 商品：`XAUUSD`，也就是現貨黃金兌美元。
- 週期：`m1`，一分鐘 K 線。
- 價格類型：分成 `bid` 與 `ask` 兩份資料。
- 資料來源：Dukascopy historical price data。
- 下載工具：`npx dukascopy-node`。
- 檔案格式：CSV。
- 時區：UTC。下載器輸出顯示 `UTC Offset: 0`。
- 儲存方式：每個月份一個 CSV 檔案。

## 資料包結構

這份資料包以根目錄為基準，結構如下：

```text
資料包根目錄
  xauusd
    ask
      m1
        xauusd_ask_m1_YYYY_MM.csv
    bid
      m1
        xauusd_bid_m1_YYYY_MM.csv
```

稽核與下載紀錄放在對應的 bid 或 ask m1 資料夾中：

```text
ask m1 稽核檔：ask_m1_file_audit.csv
ask m1 下載紀錄：download_ask_m1_log.csv
bid m1 稽核檔：bid_m1_file_audit.csv
bid m1 下載紀錄：download_bid_m1_log.csv
```

## 目前資料範圍

- Ask：`2010-01` 到 `2026-06`，共 198 個月檔案。
- Bid：`2010-01` 到 `2026-06`，共 198 個月檔案。
- `2026_06` 是下載當下的當月資料，因此不是完整月份。
- 完整歷史月份已做過行數檢查與修復，目前沒有已知 0 bytes 或只下載部分月份的檔案。

## CSV 欄位說明

每個 CSV 的欄位都是：

```csv
timestamp,open,high,low,close
```

欄位意思：

- `timestamp`：Unix epoch milliseconds，Unix 時間戳的毫秒格式。
- `open`：這一分鐘的開盤價。
- `high`：這一分鐘的最高價。
- `low`：這一分鐘的最低價。
- `close`：這一分鐘的收盤價。

例如：

```csv
timestamp,open,high,low,close
1262304000000,1096.093,1096.093,1096.093,1096.093
```

其中 `1262304000000` 代表：

```text
2010-01-01 00:00:00 UTC
2010-01-01 08:00:00 Asia/Taipei / 台灣時間
```

## Bid 與 Ask 怎麼理解

`bid` 是市場願意買入的價格，也就是你要賣出時通常會成交在 bid 附近。

`ask` 是市場願意賣出的價格，也就是你要買入時通常會成交在 ask 附近。

價差可以用同一個 timestamp 的 ask 與 bid 估算：

```text
spread = ask.close - bid.close
```

常見回測成交價格假設：

- 做多進場：用 ask。
- 做多出場：用 bid。
- 做空進場：用 bid。
- 做空出場：用 ask。

如果策略只用單一價格，例如只用 bid 或只用 mid price，回測結果可能會高估績效，因為沒有反映買賣價差成本。

## 建議的策略驗證流程

初期不要直接用 2010 至今的全部資料跑。全部資料量很大，策略參數、資料讀取、回測速度、交易邏輯還沒穩定前，直接跑全資料會浪費很多時間，也比較難快速定位問題。

建議初期先使用 `2024-01` 至目前最新資料，也就是：

```text
xauusd_ask_m1_2024_01.csv 到目前最新 ask 月份
xauusd_bid_m1_2024_01.csv 到目前最新 bid 月份
```

初期驗證目標：

1. 確認資料可以正確讀取與合併。
2. 確認 timestamp 轉換與時區處理正確。
3. 確認策略進出場邏輯沒有方向錯誤。
4. 確認回測速度可以接受。
5. 先用較新的市場環境檢查策略是否有基本合理性。

當策略邏輯、參數範圍、交易成本處理、風控規則都穩定後，再進入後期驗證。

## 後期如何用全部資料驗證

後期應使用 `2010-01` 至目前最新月份的完整 bid/ask 資料做長週期驗證。

建議做法：

1. 將所有 ask 月份依檔名排序後串接。
2. 將所有 bid 月份依檔名排序後串接。
3. 將 timestamp 轉為 UTC datetime。
4. 用 `timestamp` 將 ask 與 bid 合併。
5. 檢查合併後是否有缺 ask 或缺 bid 的 timestamp。
6. 依策略方向套用成交價格。
7. 針對不同年份、市場階段、波動環境分段統計績效。

後期驗證時不要只看總損益，至少應該分段看：

- 每年績效。
- 每月績效。
- 最大回撤。
- 勝率與賺賠比。
- 交易次數。
- 平均持倉時間。
- spread 對績效的影響。
- 高波動年份與低波動年份的差異。

## 動態風險與容量模型

目前交易策略採用動態風險與容量框架，用來把勝率、年下單量、停損距離分佈、券商摩擦成本與下單容量限制，轉換成同一個可比較的年度增長品質標準。

當策略訊號邏輯已經穩定到可以估算以下數值後，就應該套用本模型：

- `p`：系統勝率。例如 `0.60` 代表 60%。
- `N`：年目標下單量。例如 `6000`。
- `r`：單筆風險百分比，也就是每筆交易佔當下總資金的比例。例如 `0.02` 代表 2%。
- `R`：理論賺賠比，以 R 倍數表示。例如 `1.0` 代表 1R。
- `mu_M`：平均停損點數。目前基準範例為 `361.5` pips。
- `sigma_M`：停損點數的標準差，用來衡量停損距離分佈的不穩定度。
- `C`：每手來回手續費折合點數。基準機構摩擦成本範例為 `0.7` pips。

### 隨機手續費拖累

因為手續費拖累與停損距離呈反比，過小或不穩定的停損距離會造成非線性摩擦。模型將停損距離 `M` 視為隨機變數，並使用二階近似估算實質手續費期望值：

```text
f_bar = (C / mu_M) * (1 + (sigma_M^2 / mu_M^2))
```

解讀方式：

- `sigma_M` 越高，即使平均停損距離不變，實質手續費拖累也會上升。
- `mu_M` 越小，固定手續費相對於停損距離越大，摩擦成本會快速放大。
- 回測時應從實際產生的每筆交易統計 `mu_M` 與 `sigma_M`，不要只用人工挑選的範例估算。

### 等效年度增長標準

策略以年度幾何增長能量常數作為比較基準：

```text
N * [ p * alpha - beta ] = K
```

其中：

```text
alpha = r * R * (1 - f_bar) + r * (1 + f_bar) - ((r^2 * R^2) / 2) * (1 - f_bar)^2 + ((r^2) / 2) * (1 + f_bar)^2

beta = r * (1 + f_bar) + ((r^2) / 2) * (1 + f_bar)^2
```

`K` 是年度系統增長能量常數。目前規格書建議可用一組基準效能指標鎖定目標值，例如：

```text
p = 0.60
N = 6000
mu_M = 361.5
```

測試新的參數組合時，計算：

```text
current_K = new_N * (new_p * alpha - beta)
```

若 `current_K >= target_K`，代表新的勝率、下單量、停損波動與成本拖累組合，已達到或超過原策略的獲利標準。

### 實作順序

1. 使用 bid/ask 成交規則回測策略，並收集每筆交易的實際停損距離 `M`。
2. 從交易樣本計算 `mu_M` 與 `sigma_M`。
3. 將券商來回手續費換算成 pips，得到 `C`。
4. 計算 `f_bar`。
5. 計算 `alpha` 與 `beta`。
6. 將 `current_K` 與鎖定的基準 `target_K` 比較。
7. 報告勝率 `p`、年化下單量 `N`、平均停損距離、停損距離標準差與是否通過標準。

### 風險邊界

- 波動度擴張：如果 `sigma_M` 快速放大，必須重新校正 `f_bar`、`alpha`、`beta` 與 `current_K`。停損距離越不穩定，策略實質容量越低，可能需要更高勝率、更低下單頻率、更低單筆風險或更嚴格的濾網。
- 微小停損陷阱：如果 `mu_M` 相對於 `C` 太小，交易成本會吞噬策略優勢。接受參數組合前，應使用硬性濾網，例如 `mu_M > 20 * C`。
- 券商容量天花板：本模型建立在幾何複利可持續放大的假設上。當帳戶資金已使單筆下單量接近券商上限，例如 100 標準手時，必須切換成固定手數執行，並停止用等比複利假設估算後續成長。

## 後期如何使用 Bid/Ask 做更接近實盤的驗證

後期驗證不要只用 close price 做理想化回測，應盡量用 bid/ask 模擬成交成本。

### 做多策略

做多進場代表買入，因此使用 ask：

```text
long_entry_price = ask price
```

做多出場代表賣出，因此使用 bid：

```text
long_exit_price = bid price
```

做多損益簡化表示：

```text
pnl = bid_exit - ask_entry
```

### 做空策略

做空進場代表賣出，因此使用 bid：

```text
short_entry_price = bid price
```

做空出場代表買回，因此使用 ask：

```text
short_exit_price = ask price
```

做空損益簡化表示：

```text
pnl = bid_entry - ask_exit
```

### 使用哪個 OHLC 欄位

如果策略是在 K 線收盤後才下單，通常使用下一根 K 線的開盤價來模擬成交，比直接使用訊號當根 close 更保守。

例如：

- 第 N 根 K 線 close 產生做多訊號。
- 第 N+1 根 K 線用 ask open 進場。
- 出場時用 bid open 或 bid close，取決於你的回測假設。

如果策略使用停損或停利，則需要用 high/low 判斷該分鐘內是否觸價，但要注意一分鐘 K 線不知道分鐘內價格先後順序。對同一根 K 線同時碰到停利與停損的情況，應使用保守假設，或改用更細週期資料驗證。

## 完整性檢查邏輯

完整月份的預期行數：

```text
expected_lines = days_in_month * 1440 + 1
```

`+ 1` 是 CSV header。

對照表：

| 月份天數 | 預期行數 |
|---:|---:|
| 28 天 | 40321 |
| 29 天 | 41761 |
| 30 天 | 43201 |
| 31 天 | 44641 |

下載時曾遇到 `dukascopy-node` 回傳成功但檔案是 0 bytes 或只有部分資料的情況，所以不能只看下載指令是否成功，也要看檔案大小與行數。

## Python 讀取範例

```python
from pathlib import Path
import pandas as pd

DATASET_ROOT = Path("<資料包解壓縮後的根目錄>")

bid_files = sorted((DATASET_ROOT / "xauusd" / "bid" / "m1").glob("xauusd_bid_m1_*.csv"))
ask_files = sorted((DATASET_ROOT / "xauusd" / "ask" / "m1").glob("xauusd_ask_m1_*.csv"))

bid = pd.concat((pd.read_csv(f) for f in bid_files), ignore_index=True)
ask = pd.concat((pd.read_csv(f) for f in ask_files), ignore_index=True)

bid["datetime_utc"] = pd.to_datetime(bid["timestamp"], unit="ms", utc=True)
ask["datetime_utc"] = pd.to_datetime(ask["timestamp"], unit="ms", utc=True)

merged = bid.merge(
    ask,
    on="timestamp",
    suffixes=("_bid", "_ask"),
    how="inner",
)

merged["datetime_utc"] = pd.to_datetime(merged["timestamp"], unit="ms", utc=True)
merged["spread_close"] = merged["close_ask"] - merged["close_bid"]
```

若要初期使用 `2024-01` 至目前最新資料，可讀取所有 `2024_*`、`2025_*`、`2026_*` 檔案，或用日期條件過濾 `timestamp >= 2024-01-01 00:00:00 UTC`。

## 給其他 Agent 的使用提醒

1. 這份資料是 XAUUSD 一分鐘 OHLC，分成 bid 與 ask。
2. timestamp 是毫秒，不是秒。
3. timestamp 時區是 UTC。
4. 初期策略驗證建議從 `2024-01` 至目前最新資料開始。
5. 後期驗證再使用 `2010-01` 至目前最新資料。
6. 做多進場用 ask，做多出場用 bid。
7. 做空進場用 bid，做空出場用 ask。
8. 合併 bid/ask 時使用 `timestamp` 欄位。
9. `2026_06` 是當月未完整資料；需要完整月份時要排除或重新下載。
10. 使用資料前先查看 audit CSV，確認沒有缺檔或行數異常。
11. 做容量評估時，應從實際回測交易計算 `p`、年化 `N`、`mu_M`、`sigma_M`、`f_bar`、`alpha`、`beta` 與 `current_K`。
12. 只有在 `current_K >= target_K`，且停損距離與券商容量風險邊界仍成立時，才接受新的策略參數組合。
## TradingView Pepperstone 校準說明

已使用一份 TradingView Pepperstone 匯出的 XAUUSD 1 分 K 檔案，與本 Dukascopy bid/ask 資料集進行比對，用來判斷前期特徵分析應優先使用 bid 還是 ask。

比對檔案：

```text
F:\code\AutoRunForex\History_Data\tradingview_pepperstone\PEPPERSTONE_XAUUSD, 1_6f14b.csv
```

TradingView 檔案涵蓋範圍：

```text
2023-12-29 11:44 UTC 到 2024-01-02 18:59 UTC
```

因為該檔案不包含 `2024-01-03 02:34 UTC`，所以改用重疊區間內的 K 線進行資料源校準。

### 相同時間點 OHLC 對照

| Time UTC | Source | Open | High | Low | Close |
|---|---|---:|---:|---:|---:|
| 2024-01-02 00:35 | TradingView Pepperstone | 2063.850 | 2063.910 | 2063.810 | 2063.840 |
| 2024-01-02 00:35 | Dukascopy BID | 2063.845 | 2063.905 | 2063.785 | 2063.845 |
| 2024-01-02 00:35 | Dukascopy ASK | 2064.152 | 2064.222 | 2064.122 | 2064.122 |
| 2024-01-02 05:35 | TradingView Pepperstone | 2071.710 | 2072.120 | 2071.700 | 2071.980 |
| 2024-01-02 05:35 | Dukascopy BID | 2071.625 | 2072.135 | 2071.625 | 2071.965 |
| 2024-01-02 05:35 | Dukascopy ASK | 2071.935 | 2072.452 | 2071.935 | 2072.295 |
| 2024-01-02 09:42 | TradingView Pepperstone | 2078.010 | 2078.080 | 2077.540 | 2077.590 |
| 2024-01-02 09:42 | Dukascopy BID | 2077.935 | 2077.968 | 2077.438 | 2077.498 |
| 2024-01-02 09:42 | Dukascopy ASK | 2078.275 | 2078.295 | 2077.775 | 2077.815 |

### 重疊區間統計

重疊樣本數：`1199` 根 1 分 K。

| 比較 | 平均 close 差異 | 平均絕對 close 差異 |
|---|---:|---:|
| TradingView Pepperstone close - Dukascopy BID close | +0.0871 | 0.0883 |
| TradingView Pepperstone close - Dukascopy ASK close | -0.2392 | 0.2392 |

接近程度：

```text
更接近 Dukascopy BID：1157 根
更接近 Dukascopy ASK：37 根
```

### 實務建議

目前重疊樣本顯示，TradingView Pepperstone 的 XAUUSD 1 分 K OHLC 明顯更接近 Dukascopy BID，而不是 ASK。

因此，如果目標是讓前期特徵分析更貼近 TradingView 圖表上看到的結構，建議使用：

```text
結構訊號 / BOS / CHoCH / pivot 判定：Dukascopy BID K 線
```

但如果目標是做後期實盤執行與資金曲線驗證，仍應使用較保守的 bid/ask 執行模型：

```text
多單進場：ASK
多單出場：BID
空單進場：BID
空單出場：ASK
```

建議工作流：

```text
前期特徵分析：使用 BID，降低與 TradingView 圖表的資料落差。
後期實盤驗證：使用 BID/ASK，納入 spread 成本。
```
