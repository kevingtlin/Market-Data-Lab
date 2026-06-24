# XAUUSD Dukascopy M1 Bid/Ask History

Generated: 2026-06-24 20:24:09 +08:00

This dataset contains historical one-minute OHLC data for XAUUSD, downloaded from Dukascopy via `dukascopy-node`. It includes both bid and ask prices and is intended for strategy research, backtesting, spread analysis, and later-stage validation with more realistic execution assumptions.

## What This Data Is

- Instrument: `XAUUSD` / spot gold quoted in USD.
- Timeframe: `m1`, one-minute candles.
- Price sides: both `bid` and `ask` are stored separately.
- Source tool: `npx dukascopy-node`.
- Source venue/data provider: Dukascopy historical price data.
- Format: CSV.
- Time zone: UTC (`UTC Offset: 0` in the downloader output).
- Storage style: one CSV file per calendar month.

## Dataset Structure

The package is organized from the dataset root as follows:

```text
dataset root
  xauusd
    ask
      m1
        xauusd_ask_m1_YYYY_MM.csv
    bid
      m1
        xauusd_bid_m1_YYYY_MM.csv
```

Audit and download logs are stored beside each side's data:

```text
ask m1 audit: ask_m1_file_audit.csv
ask m1 download log: download_ask_m1_log.csv
bid m1 audit: bid_m1_file_audit.csv
bid m1 download log: download_bid_m1_log.csv
```

## Current Coverage

| Side | Files | Size MB | First file | Last file | First timestamp UTC | Last timestamp UTC |
|---|---:|---:|---|---|---|---|
| ask | 198 | 410.58 | `xauusd_ask_m1_2010_01.csv` | `xauusd_ask_m1_2026_06.csv` | 2010-01-01 00:00:00 UTC | 2026-06-23 16:59:00 UTC |
| bid | 198 | 410.65 | `xauusd_bid_m1_2010_01.csv` | `xauusd_bid_m1_2026_06.csv` | 2010-01-01 00:00:00 UTC | 2026-06-23 17:59:00 UTC |

The final month file, `2026_06`, is a partial current-month file because the download was run on 2026-06-24.

## CSV Schema

Every monthly CSV has this header:

```csv
timestamp,open,high,low,close
```

Column meaning:

- `timestamp`: Unix epoch time in milliseconds. Example: `1262304000000` means `2010-01-01 00:00:00 UTC`.
- `open`: first price of the one-minute candle.
- `high`: highest price within the minute.
- `low`: lowest price within the minute.
- `close`: last price of the one-minute candle.

Example from bid:

```csv
timestamp,open,high,low,close
1262304000000,1096.093,1096.093,1096.093,1096.093
```

Example from ask:

```csv
timestamp,open,high,low,close
1262304000000,1096.597,1096.597,1096.597,1096.597
```

## How To Interpret Bid And Ask

Use `bid` when modelling sell-side execution or prices that can be sold into.

Use `ask` when modelling buy-side execution or prices that must be paid to buy.

The spread at a timestamp can be estimated as:

```text
spread = ask.close - bid.close
```

A conservative backtest convention is:

- Long entry: use ask.
- Long exit: use bid.
- Short entry: use bid.
- Short exit: use ask.

Using only one price stream or only a mid price can overstate performance because it ignores spread cost.

## Suggested Strategy Validation Workflow

Do not start by running the entire 2010-to-present dataset. The full dataset is large, and early strategy iterations are easier to debug on a smaller but recent sample.

For early validation, start with data from `2024-01` to the latest available month:

```text
ask files from xauusd_ask_m1_2024_01.csv onward
bid files from xauusd_bid_m1_2024_01.csv onward
```

Early validation goals:

1. Confirm that the data can be read and merged correctly.
2. Confirm timestamp parsing and time-zone handling.
3. Confirm entry and exit direction logic.
4. Confirm acceptable backtest speed.
5. Check basic strategy behavior in a recent market environment.

After strategy logic, parameter ranges, execution-cost handling, and risk rules are stable, move to full historical validation.

## Later-Stage Full Data Validation

For later-stage validation, use the full `2010-01` to latest available bid/ask dataset.

Recommended process:

1. Concatenate all ask monthly files in filename order.
2. Concatenate all bid monthly files in filename order.
3. Convert `timestamp` to UTC datetime.
4. Merge ask and bid on `timestamp`.
5. Check for missing ask or bid timestamps after merging.
6. Apply execution prices according to trade direction.
7. Evaluate results by year, month, market regime, and volatility environment.

At minimum, review:

- Yearly performance.
- Monthly performance.
- Maximum drawdown.
- Win rate and payoff ratio.
- Number of trades.
- Average holding time.
- Spread impact on performance.
- Differences between high-volatility and low-volatility periods.

## Later-Stage Bid/Ask Execution Modelling

For later-stage validation, avoid idealized close-price-only backtests. Use bid/ask to model transaction cost more realistically.

### Long Trades

Long entry means buying, so use ask:

```text
long_entry_price = ask price
```

Long exit means selling, so use bid:

```text
long_exit_price = bid price
```

Simplified long PnL:

```text
pnl = bid_exit - ask_entry
```

### Short Trades

Short entry means selling, so use bid:

```text
short_entry_price = bid price
```

Short exit means buying back, so use ask:

```text
short_exit_price = ask price
```

Simplified short PnL:

```text
pnl = bid_entry - ask_exit
```

### Which OHLC Field To Use

If a signal is generated after a candle closes, a more conservative assumption is to execute on the next candle's open instead of the same candle's close.

Example:

- Candle N close generates a long signal.
- Candle N+1 uses ask open for entry.
- Exit uses bid open or bid close, depending on the backtest assumption.

For stop-loss or take-profit logic, use high/low to check whether a level was touched within the minute. A one-minute OHLC candle does not reveal intraminute price order. If both stop-loss and take-profit are touched in the same candle, use a conservative assumption or validate with finer-grained data.

## Completeness Checks

For complete historical months, expected line count is:

```text
expected_lines = days_in_month * 1440 + 1
```

The `+ 1` is the CSV header row.

Expected examples:

| Month length | Expected lines |
|---:|---:|
| 28 days | 40321 |
| 29 days | 41761 |
| 30 days | 43201 |
| 31 days | 44641 |

The downloader sometimes returned success while producing a 0-byte or partial file. Because of that, downloads must be validated by line count, not only by process exit code.

Current validation result:

- Ask: checked and repaired. No full historical month is missing or partial.
- Bid: checked and repaired. No full historical month is missing or partial.
- `2026_06` is intentionally partial because it is the current month at download time.

## Re-download Command Pattern

Ask month:

```powershell
npx dukascopy-node -i xauusd -from 2010-01-01 -to 2010-02-01 -t m1 -p ask -f csv --cache -dir <ask-m1-folder> -fn xauusd_ask_m1_2010_01 -r 5 -rp 3000
```

Bid month:

```powershell
npx dukascopy-node -i xauusd -from 2010-01-01 -to 2010-02-01 -t m1 -p bid -f csv --cache -dir <bid-m1-folder> -fn xauusd_bid_m1_2010_01 -r 5 -rp 3000
```

Important: after any re-download, verify file size and expected row count.

## Python Usage Example

```python
from pathlib import Path
import pandas as pd

DATASET_ROOT = Path("<folder where this dataset package is unpacked>")

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

For early validation from `2024-01` onward, either load files from `2024_*`, `2025_*`, `2026_*`, or filter by `timestamp >= 2024-01-01 00:00:00 UTC` after loading.

## Agent Usage Guidance

1. This dataset is XAUUSD one-minute OHLC, separated into bid and ask.
2. `timestamp` is milliseconds, not seconds.
3. Timestamps are UTC.
4. Early strategy validation should start from `2024-01` to the latest available data.
5. Later validation should use the full `2010-01` to latest available data.
6. Long entry uses ask; long exit uses bid.
7. Short entry uses bid; short exit uses ask.
8. Merge bid and ask using `timestamp`.
9. `2026_06` is a partial current-month file; exclude or refresh it when a complete month is required.
10. Check the audit CSV files before using the dataset.
## TradingView Pepperstone Calibration Note

A small TradingView Pepperstone export was compared against this Dukascopy bid/ask dataset to decide which side should be used for early-stage structure and feature analysis.

Compared file:

```text
F:\code\AutoRunForex\History_Data\tradingview_pepperstone\PEPPERSTONE_XAUUSD, 1_6f14b.csv
```

TradingView file coverage:

```text
2023-12-29 11:44 UTC to 2024-01-02 18:59 UTC
```

Because this file does not include `2024-01-03 02:34 UTC`, calibration was performed on overlapping timestamps.

### Sample OHLC Comparison

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

### Overlap Statistics

Overlap sample size: `1199` one-minute candles.

| Comparison | Mean close difference | Mean absolute close difference |
|---|---:|---:|
| TradingView Pepperstone close - Dukascopy BID close | +0.0871 | 0.0883 |
| TradingView Pepperstone close - Dukascopy ASK close | -0.2392 | 0.2392 |

Closer side count:

```text
Closer to Dukascopy BID: 1157 candles
Closer to Dukascopy ASK: 37 candles
```

### Practical Recommendation

The TradingView Pepperstone XAUUSD 1-minute OHLC export is much closer to Dukascopy BID than to Dukascopy ASK in the tested overlap.

For early-stage analysis intended to match TradingView chart structure more closely, use:

```text
Signal / BOS / CHoCH / pivot generation: Dukascopy BID candles
```

For later-stage execution and account-growth validation, still use the conservative bid/ask execution model:

```text
Long entry: ASK
Long exit: BID
Short entry: BID
Short exit: ASK
```

Recommended workflow:

```text
Early feature analysis: use BID to reduce chart-data mismatch.
Final execution validation: use BID/ASK to include spread cost.
```
