# 術語治理與第一輪稽核

## 本 repo 的獨立規則

本文件只保存 Market-Data-Lab 可獨立理解的術語邊界，不引用私人 Knowledge Lab。repository identity、dataset identity、storage path 與 schema field 不得混用。

## 第一輪稽核

| 名稱 | 狀態 | 本 repo 中的角色 |
|---|---|---|
| Market-Data-Lab | 已確認 | repository identity；不再綁定單一 provider、instrument 或 timeframe。 |
| dukascopy_XAUUSD_1m_Data | 已棄用舊 repo 名稱 | 只保留 migration provenance；目前應指向 Market-Data-Lab。 |
| XAUUSD-DUKASCOPY-M1-BID-ASK | 已確認 | 現有 dataset ID。 |
| Dukascopy／XAUUSD／M1／bid／ask／UTC | 外部資料與市場術語 | 是 dataset metadata，不任意翻譯成新的 schema identifier。 |
| timestamp／open／high／low／close | 穩定 schema field | 工程欄位；中文說明不得改變 CSV contract。 |
| xauusd/bid/m1、xauusd/ask/m1 | 現行 storage path | 不是 dataset identity；路徑遷移必須先更新 consumers 並驗證。 |

## 發現與處理

- 舊 repo 名稱只作可追溯別名，不得重新成為 canonical identity。
- 本輪沒有變更資料路徑、timestamp 單位、timezone、bid／ask 語意或 CSV schema。
- 新 dataset 必須先建立 dataset ID 與 metadata，不能由資料夾名稱代替概念定義。
