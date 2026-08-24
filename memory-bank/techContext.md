# Tech Context

## Current Dataset Format

- CSV files.
- One file per calendar month.
- Separate bid and ask sides.
- Timestamp is Unix epoch milliseconds.
- Timezone is UTC.

Current paths are intentionally preserved:

```text
xauusd/ask/m1/
xauusd/bid/m1/
```

## Future Migration

A future path migration may move raw files under a dataset-unit directory, but only after updating and validating consumers such as `Strategy-Backtest-Lab`.

