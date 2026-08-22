# XAUUSD Dukascopy M1 Bid/Ask 歷史資料說明

產生時間：2026-08-23 02:16:39 +08:00

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

| 類型 | 檔案數 | 大小 MB | 第一個檔案 | 最新檔案 | 第一筆 UTC | 最新一筆 UTC |
|---|---:|---:|---|---|---|---|
| ask | 200 | 413.71 | `xauusd_ask_m1_2010_01.csv` | `xauusd_ask_m1_2026_08.csv` | 2010-01-01 00:00:00 UTC | 2026-08-20 23:58:00 UTC |
| bid | 200 | 413.77 | `xauusd_bid_m1_2010_01.csv` | `xauusd_bid_m1_2026_08.csv` | 2010-01-01 00:00:00 UTC | 2026-08-20 23:58:00 UTC |

最新月份 `2026_08` 是未完整月份。目前下載到的最新資料約到 `2026-08-20 23:58:00 UTC`。之後若需要更新資料，請重新下載 `2026_08`。

## CSV 欄位說明

```csv
timestamp,open,high,low,close
```

- `timestamp`：Unix epoch milliseconds，Unix 時間戳的毫秒格式。例如 `1262304000000` 代表 `2010-01-01 00:00:00 UTC`。
- `open`：這一分鐘的開盤價。
- `high`：這一分鐘的最高價。
- `low`：這一分鐘的最低價。
- `close`：這一分鐘的收盤價。

## Bid 與 Ask 怎麼理解

`bid` 是市場願意買入的價格，也就是你要賣出時通常會成交在 bid 附近。`ask` 是市場願意賣出的價格，也就是你要買入時通常會成交在 ask 附近。

```text
spread = ask.close - bid.close
```

常見回測成交價格假設：

- 做多進場：用 ask。
- 做多出場：用 bid。
- 做空進場：用 bid。
- 做空出場：用 ask。

## 建議的策略驗證流程

初期不要直接用 2010 至今的全部資料跑。全部資料量很大，策略參數、資料讀取、回測速度、交易邏輯還沒穩定前，直接跑全資料會浪費很多時間，也比較難快速定位問題。

建議初期先使用 `2024-01` 至目前最新資料。當策略邏輯、參數範圍、交易成本處理、風控規則都穩定後，再使用 `2010-01` 至目前最新資料做長週期驗證。

後期驗證時不要只看總損益，至少應該分段看每年績效、每月績效、最大回撤、勝率與賺賠比、交易次數、平均持倉時間、spread 對績效的影響，以及高低波動環境的差異。

## 後期如何使用 Bid/Ask 做更接近實盤的驗證

做多：

```text
long_entry_price = ask price
long_exit_price = bid price
pnl = bid_exit - ask_entry
```

做空：

```text
short_entry_price = bid price
short_exit_price = ask price
pnl = bid_entry - ask_exit
```

如果策略是在 K 線收盤後才下單，通常使用下一根 K 線的開盤價來模擬成交，比直接使用訊號當根 close 更保守。

如果策略使用停損或停利，則需要用 high/low 判斷該分鐘內是否觸價，但要注意一分鐘 K 線不知道分鐘內價格先後順序。對同一根 K 線同時碰到停利與停損的情況，應使用保守假設，或改用更細週期資料驗證。

## 完整性檢查邏輯

如果檔案是完整自然月每分鐘補齊，預期行數是：

```text
expected_lines = days_in_month * 1440 + 1
```

`+ 1` 是 CSV header。

有些較新的檔案可能只包含交易時段資料，也就是非交易分鐘不會出現在 CSV 裡。這種情況下，行數會低於完整自然月公式，但只要首尾 timestamp 覆蓋該月份可交易區間、且不是 0 bytes 或明顯截斷，就不一定代表下載壞掉。

下載時曾遇到 `dukascopy-node` 回傳成功但檔案是 0 bytes 或只有部分資料的情況，所以不能只看下載指令是否成功，也要看檔案大小、行數、首尾 timestamp 和 bid/ask 是否能用 `timestamp` 對齊。

目前檢查結果：

- Ask：已檢查並修復 0 bytes 與明顯部分下載問題。
- Bid：已檢查並修復 0 bytes 與明顯部分下載問題。
- `2026_08` 是最新未完整月份。
- 合併 bid/ask 做策略驗證時，建議用 `timestamp` 做 inner join，這會排除只存在於單邊的 timestamp。

## Python 讀取範例

```python
from pathlib import Path
import pandas as pd

DATASET_ROOT = Path("<資料包解壓縮後的根目錄>")

bid_files = sorted((DATASET_ROOT / "xauusd" / "bid" / "m1").glob("xauusd_bid_m1_*.csv"))
ask_files = sorted((DATASET_ROOT / "xauusd" / "ask" / "m1").glob("xauusd_ask_m1_*.csv"))

bid = pd.concat((pd.read_csv(f) for f in bid_files), ignore_index=True)
ask = pd.concat((pd.read_csv(f) for f in ask_files), ignore_index=True)

merged = bid.merge(ask, on="timestamp", suffixes=("_bid", "_ask"), how="inner")
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
8. 合併 bid/ask 時使用 `timestamp`，建議使用 inner join。
9. 最新月份可能不是完整月份；需要完整月份時要排除或重新下載。
10. 使用資料前先查看 audit CSV，確認沒有缺檔或行數異常。