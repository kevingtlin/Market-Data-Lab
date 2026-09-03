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

## Codebase Memory（CBM）

本 repository 使用 `codebase-memory-mcp` 維護共享程式碼知識圖譜。進行廣泛程式探索、架構分析、跨檔案依賴分析、呼叫鏈分析、dead-code 判斷或修改影響分析前，應先查詢本 repo 對應的 CBM project。

必要工作流程：

- 重要 CBM 結果必須回到目前 checkout 的原始碼、測試與設定檔驗證。
- 在宣稱某個符號、呼叫者、依賴、受影響路徑或相關實作不存在之前，必須檢查索引新鮮度與索引覆蓋範圍。
- 本 repository 必須作為獨立 CBM project 索引；不得使用 `Trading-Research-Workspace` 根目錄索引取代。
- 查詢時要明確選擇本 repo 的 CBM project，避免混入其他 repository 的結果。
- 共享索引固定存放於 `.codebase-memory/graph.db.zst`。
- 新增、刪除或重新命名模組、資料流、依賴或可索引結構後，交付前必須顯式執行 `index_repository` 並提交更新後的共享索引。
- 只有資料、文件、註解或格式變更，且不影響可索引結構時，不強制刷新共享索引。
- 不得假設背景 watcher 已產生最終共享索引；結構性變更提交前必須顯式索引。
- 若共享索引與目前 checkout 原始碼衝突，以原始碼為準並重建索引。
- 本機必須安裝 `codebase-memory-mcp` 才能查詢或更新索引。
- CBM 是結構導航與證據輔助，不取代原始碼檢查、資料驗證或 Workspace Memory Bank。

Workspace 層級治理、受管 repository registry 與 onboarding 政策由 `Trading-Research-Workspace` Memory Bank 維護。

## 術語保存規則

- 優先沿用使用者或本 repo 已存在的正式名稱，不得為了結構化或專業感任意英文化、翻譯或重新命名。
- 首次引入使用者尚未使用的新英文專有名詞時，必須同時說明中文意思、當前含義、使用理由與來源。
- AI 為未命名概念建立的名稱必須標記為「AI 暫稱」；未經使用者確認，不得成為正式術語或穩定資料契約的唯一名稱。
- 工程 identifier 可以使用英文，但必須保留與正式中文名稱／原始概念的映射；實作改名不等於概念改名。
- 無法追溯名稱來源或定義時，標記待追溯並搜尋本 repo；不得猜測、合併或拆分概念。
- 本 repo 必須能獨立執行這些規則，不假設 Trading-Research-Workspace 或私人 Knowledge Lab 存在。第一輪稽核與本地規則見 memory-bank/terminology-governance.md。

## Hard Rules

- Do not rename repository identity back to a provider/instrument/timeframe-specific name.
- Do not duplicate coarser timeframe datasets if they can be derived from M1 with the same provider and semantics.
- Do not change timestamp units, timezone assumptions, CSV schema, or bid/ask meaning during structural refactors.
- Do not commit machine-local paths.
- Record future dataset-unit path migration before moving raw data.
