# XAUUSD Dukascopy M1 Bid/Ask History

Generated: 2026-08-23 02:16:39 +08:00

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
| ask | 200 | 413.71 | `xauusd_ask_m1_2010_01.csv` | `xauusd_ask_m1_2026_08.csv` | 2010-01-01 00:00:00 UTC | 2026-08-20 23:58:00 UTC |
| bid | 200 | 413.77 | `xauusd_bid_m1_2010_01.csv` | `xauusd_bid_m1_2026_08.csv` | 2010-01-01 00:00:00 UTC | 2026-08-20 23:58:00 UTC |

The latest month file, `2026_08`, is partial. The latest data currently available in the downloaded files ends at about `2026-08-20 23:58:00 UTC`. Re-download `2026_08` when more recent data is needed.

## CSV Schema

```csv
timestamp,open,high,low,close
```

- `timestamp`: Unix epoch time in milliseconds. Example: `1262304000000` means `2010-01-01 00:00:00 UTC`.
- `open`: first price of the one-minute candle.
- `high`: highest price within the minute.
- `low`: lowest price within the minute.
- `close`: last price of the one-minute candle.

## How To Interpret Bid And Ask

Use `bid` when modelling sell-side execution or prices that can be sold into. Use `ask` when modelling buy-side execution or prices that must be paid to buy.

```text
spread = ask.close - bid.close
```

A conservative backtest convention is:

- Long entry: use ask.
- Long exit: use bid.
- Short entry: use bid.
- Short exit: use ask.

## Suggested Strategy Validation Workflow

For early validation, start with data from `2024-01` to the latest available month. Do not start by running the entire 2010-to-present dataset because early strategy iterations are easier to debug on a smaller but recent sample.

After strategy logic, parameter ranges, execution-cost handling, and risk rules are stable, move to full historical validation from `2010-01` onward.

## Later-Stage Bid/Ask Execution Modelling

Long trades:

```text
long_entry_price = ask price
long_exit_price = bid price
pnl = bid_exit - ask_entry
```

Short trades:

```text
short_entry_price = bid price
short_exit_price = ask price
pnl = bid_entry - ask_exit
```

If a signal is generated after a candle closes, a more conservative assumption is to execute on the next candle's open instead of the same candle's close.

For stop-loss or take-profit logic, use high/low to check whether a level was touched within the minute. A one-minute OHLC candle does not reveal intraminute price order. If both stop-loss and take-profit are touched in the same candle, use a conservative assumption or validate with finer-grained data.

## Completeness Checks

For complete calendar-minute coverage, expected line count is:

```text
expected_lines = days_in_month * 1440 + 1
```

The `+ 1` is the CSV header row.

Some recent files may contain market-session rows only, meaning non-trading minutes are not present. This can make their line count lower than the full calendar-minute formula even when the first and last timestamps cover the available trading sessions. Always check the audit CSV files before using the dataset.

Current validation result:

- Ask: checked and repaired for zero-byte and partial-download failures.
- Bid: checked and repaired for zero-byte and partial-download failures.
- `2026_08` is intentionally partial because it is the latest in-progress month.
- When bid/ask are merged for execution modelling, use an inner join on `timestamp`; this excludes any timestamp present on only one side.

## Python Usage Example

```python
from pathlib import Path
import pandas as pd

DATASET_ROOT = Path("<folder where this dataset package is unpacked>")

bid_files = sorted((DATASET_ROOT / "xauusd" / "bid" / "m1").glob("xauusd_bid_m1_*.csv"))
ask_files = sorted((DATASET_ROOT / "xauusd" / "ask" / "m1").glob("xauusd_ask_m1_*.csv"))

bid = pd.concat((pd.read_csv(f) for f in bid_files), ignore_index=True)
ask = pd.concat((pd.read_csv(f) for f in ask_files), ignore_index=True)

merged = bid.merge(ask, on="timestamp", suffixes=("_bid", "_ask"), how="inner")
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
8. Merge bid and ask using `timestamp` with an inner join.
9. The latest month may be partial; refresh it when a complete month is required.
10. Check the audit CSV files before using the dataset.