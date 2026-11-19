# 施工說明 1-C：Market-Data-Lab 套用共用規則

- 文件狀態：使用者已確認方向（2026-11-19）
- 撰寫：[Claude 2026-11-20]
- 實作：GPT
- 目標 repo：Market-Data-Lab
- 分支：從 `claude/phase1-plan` 開出 `gpt/phase1c`
- 基準（base）：`origin/claude/phase1-plan`（已寫在 `.repo-check.json`）
- 執行順序與暫停點：見 Trading-Research-Workspace `docs/specs/2026-11-20-phase1-CDEF-overview.md`。**本 repo 是第一段第 1 項。**

## 1. 目標

本 repo 通過 `python tools/repo_check.py` 全部檢查，且每次 push 由 GitHub 自動檢查。

## 2. 已完成的部分（Claude）與決策

| 已完成 | 內容 |
|---|---|
| `AGENTS.md` | 改寫成繁體中文路由表，保留全部既有硬規則（CSV 路徑不搬、不改時間戳／時區／schema／bid-ask 語義等），同步 project 共用區塊 |
| `.repo-check.json` | 檢查設定；`scan_exclude` 排除 `xauusd/*`（CSV 資料，避免每次掃描約 10 秒） |
| `tools/repo_check.py`、`docs/specs/TEMPLATE.md` | 由同步工具複製 |

Memory Bank 原本就在行數上限內，這次不動。

| # | 決策 | 狀態 |
|---|---|---|
| D1 | CI checkout 加 `filter: blob:none`：只下載目前版本需要的檔案內容，不下載全部歷史 CSV（repo 約 834 MB）；C07／C08 只需要 commit 與檔名，不受影響 | AI 提議（未確認） |

## 3. 範圍

只能新增 `.github/workflows/repo-check.yml`。

## 4. 不做清單

- 不修改任何資料檔、registry、文件或受保護檔案。
- workflow 只照第 6 節，不加其他步驟。
- 不 push 到 `main` 或 `claude/phase1-plan`。

## 5. 停下來問的條件

- GitHub Actions 的 checkout 超過 10 分鐘或失敗。
- repo_check 有 FAIL，且修正需要改受保護檔案。

## 6. 步驟

1. 從 `claude/phase1-plan` 開分支 `gpt/phase1c`。
2. 新增 `.github/workflows/repo-check.yml`，內容為總覽第 3 節的基本版，並在 checkout 的 `with:` 加上 `filter: blob:none`。
3. commit（依共用規則），push 到 `gpt/phase1c`，確認 GitHub Actions 成功。

## 7. 驗收指令

```bash
pip install pyyaml
git fetch origin claude/phase1-plan
python tools/repo_check.py
```

全部 PASS 或 SKIP，結束碼 0；GitHub Actions 成功。

## 8. 受保護檔案

`.github/` 以外的所有檔案（見 `.repo-check.json` 的 `protected_paths`）。

## 9. 偏差紀錄

| 代號 | 日期 | 發現者 | 偏差 | 責任 | 處理方式 |
|---|---|---|---|---|---|

## 附錄：AGENTS.md 舊規則對照

| 舊內容 | 新位置 |
|---|---|
| Scope、Current dataset | 「這個 repo 是什麼」 |
| Current Conservative Policy（CSV 路徑不搬） | 本 repo 硬規則第 1 條 |
| CBM 規則 | 共用區塊「CBM」（已改為選用） |
| 術語保存規則 | 共用區塊「術語保存」；本 repo 稽核紀錄見 `memory-bank/terminology-governance.md` |
| Hard Rules 五條 | 本 repo 硬規則第 1～4 條；「不提交本機路徑」在共用區塊「安全」 |
