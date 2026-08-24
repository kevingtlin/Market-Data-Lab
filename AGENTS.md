# Market Data Lab Agent Guide

## Scope

This repository manages historical market datasets, metadata, validation notes, and acquisition/update provenance.

Current dataset:

- `XAUUSD-DUKASCOPY-M1-BID-ASK`

## Current Conservative Policy

Do not move the existing CSV files yet.

The current data paths remain:

```text
xauusd/ask/m1/
xauusd/bid/m1/
```

This preserves compatibility with existing backtest loaders while the repository gains dataset registry and Memory Bank structure.

## Hard Rules

- Do not rename repository identity back to a provider/instrument/timeframe-specific name.
- Do not duplicate coarser timeframe datasets if they can be derived from M1 with the same provider and semantics.
- Do not change timestamp units, timezone assumptions, CSV schema, or bid/ask meaning during structural refactors.
- Do not commit machine-local paths.
- Record future dataset-unit path migration before moving raw data.

