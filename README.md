# Market Data Lab

`Market-Data-Lab` manages historical market data acquisition, metadata, validation, and reproducible dataset usage.

The repository is no longer conceptually tied to one provider, instrument, or timeframe, even though the current dataset is XAUUSD Dukascopy M1 bid/ask.

## Current Dataset

- Dataset ID: `XAUUSD-DUKASCOPY-M1-BID-ASK`
- Provider: Dukascopy
- Instrument: XAUUSD
- Base resolution: M1
- Price sides: bid and ask
- Timezone: UTC
- CSV schema: `timestamp,open,high,low,close`

Existing detailed dataset docs:

- `XAUUSD_DUKASCOPY_M1_BID_ASK_README.md`
- `XAUUSD_DUKASCOPY_M1_BID_ASK_README_ZH.md`

## Current Layout Policy

The first migration step is conservative. Existing CSV paths are preserved:

```text
xauusd/
  ask/m1/
  bid/m1/
```

Dataset metadata is layered around the current files through:

```text
registry/datasets.yaml
datasets/XAUUSD-DUKASCOPY-M1-BID-ASK/metadata.yaml
memory-bank/
```

Future phases may move raw files into a dataset-unit path only after compatibility updates and validation.

