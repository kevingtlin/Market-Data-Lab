# Market-Data-Lab 規則入口

## 這個 repo 是什麼

管理歷史行情資料集：資料檔、metadata、驗證紀錄，以及取得與更新的來源紀錄。
目前資料集：`XAUUSD-DUKASCOPY-M1-BID-ASK`（XAUUSD Dukascopy M1 bid／ask，UTC 毫秒時間戳）。

## 開工前必讀

1. `memory-bank/activeContext.md`（目前狀態、資料涵蓋範圍、下一步）
2. 執行施工說明時：`docs/specs/` 下的那一份說明

## 依任務查閱

| 任務 | 讀這份 |
|---|---|
| 資料集的身分、schema、時區、bid／ask 定義 | `registry/datasets.yaml`、`datasets/XAUUSD-DUKASCOPY-M1-BID-ASK/` |
| 資料集說明（給人讀） | `XAUUSD_DUKASCOPY_M1_BID_ASK_README_ZH.md` |
| 更新資料的方法與歷次驗證 | `reports/` |
| 定位、技術與慣例 | `memory-bank/projectbrief.md`、`memory-bank/techContext.md`、`memory-bank/systemPatterns.md` |
| 術語稽核紀錄 | `memory-bank/terminology-governance.md` |
| 過去的工作紀錄 | `memory-bank/changeLog.md`（按需查，開工時不讀） |

## 本 repo 硬規則

- 現有 CSV 路徑 `xauusd/bid/m1/`、`xauusd/ask/m1/` 暫不搬移；回測程式依賴這些路徑。未來要改成 dataset-unit 路徑，必須先記錄遷移計畫、更新使用端並驗證相容。
- 結構調整時不得改變時間戳單位、時區假設、CSV 欄位或 bid／ask 的意義。
- 能從同供應商、同語義的 M1 資料推導的較高週期資料，不重複存放。
- repo 身分維持通用名稱，不改回綁定特定供應商、商品或週期的名稱。
- 更新資料時保留既有歷史列，並在 `reports/` 留下方法與驗證結果。

## 完成前必跑

```bash
pip install pyyaml
python tools/repo_check.py
```

<!-- BEGIN SHARED RULES profile=project source_commit=4745cf922beb sha256=85d58eff1ac856608c9edf544ef24ffad079e068a875f701c6dad55990fb30de tool_sha256=0d3503b1696a1cdd37eaebd4baa5778baa3f8acba9e866c542d17bab95152a1c -->
## 共用規則

本區塊由 Trading-Research-Workspace 的 `rules/` 自動產生，勿手改；要修改請改 WS 正本後重新同步。本 repo 硬規則與共用規則衝突時以較嚴格者為準；使用者當下的明確指示優先。

### 語言

- 新增或修改的 Markdown（含 AGENTS.md）預設使用繁體中文；擔心語義落差時，可在文末補簡短英文參考，英文不得取代中文主文。
- 程式識別字可以使用英文。

### 術語保存

- 優先沿用使用者或本 repo 已存在的正式名稱；不得為了結構化或專業感任意英文化、翻譯或改名。
- 首次引入使用者沒用過的英文專有名詞，須說明中文意思、當前含義、使用理由與來源。
- AI 為未命名概念取的名稱須標記「AI 暫稱」；未經使用者確認，不得成為正式術語或穩定資料契約的唯一名稱。重複使用不等於確認。
- 工程 identifier 可用英文，但須保留與中文主名稱的映射；實作改名不等於概念改名。
- 無法追溯名稱來源或定義時，標記「待追溯」並搜尋本 repo；不得猜測、合併或拆分概念。
- 本 repo 若有術語 registry 或術語文件，以它為主紀錄；新增、改名、合併、拆分、棄用都須保留舊名稱映射。

### 最小忠實實作

- 把使用者的概念轉成程式、指標、回測、資料欄位或畫面時，只實作足以忠實表達「已確認概念」的最小集合。
- 內容分三類：使用者已確認的核心（可直接實作）；讓核心能執行的必要工程細節（採最小設計，會影響語意或結果時先說明）；AI 想到的擴充或候選變數（只能提議，不得實作）。
- 以下新增或變更須先取得使用者明確確認：可調參數、門檻、權重、模式、尺度；正式定義與判定條件；額外濾波、fallback、例外規則；新增輸出欄位或視覺元素；讓既有項目彼此連動的新機制。
- 不得以「先做進去之後再刪」取代事前確認；每項新增都應能追溯到已確認需求或施工說明。
- 原本變數很少的概念，實作後突然出現大量參數或畫面元素，視為需求擴張警訊，停下來回報。

### 多 AI 協作

- 使用者同時使用 Claude 與 GPT。分工：Claude 負責規劃、施工說明與驗收測試；GPT 負責實作；驗收者由使用者指定。
- 每個 commit 訊息內文須有一行 `Agent: Claude`、`Agent: GPT` 或 `Agent: 使用者`。
- 寫入決策、提議、結論或交接的段落，標示 `[Claude YYYY-MM-DD]` 或 `[GPT YYYY-MM-DD]`（Asia/Taipei 日期），並標明 `使用者已確認`、`AI 提議（未確認）` 或 `AI 意見分歧（待使用者裁決）`。程式碼與一般文件修正不需逐段標記。
- 只有使用者能把內容升級為「使用者已確認」；一個 AI 的提議不因另一個 AI 引用或同意而變成已確認。
- 不直接改寫另一個 AI 的結論，改以「回應」段落表達；明確事實錯誤可直接修正，但須註明修正者、日期與依據。
- 以 GitHub 上的版本為準：開工前先 pull，用 `git log` 確認他人近期修改；成果須 commit，不能只存在對話中。
- 發現另一個 AI 正在修改同一份檔案時，停下來告知使用者，不自行合併或覆蓋。

### 安全

- 不提交 secrets、憑證、帳號資訊、`.env`、金鑰檔或本機設定；本機設定以 `*.example` 範本提供。
- 追蹤檔案不寫入本機絕對路徑；引用檔案一律用 repo 相對路徑，跨 repo 用 repo 名稱或 registry ID。
- 不用破壞性 Git 操作（force push、`reset --hard`、丟棄未提交修改、靜默 stash）處理不確定狀況。
- 不搬移或改寫使用者既有的本機工作目錄。

### 證據與授權

- 宣稱完成前，必須執行本 repo 的「完成前必跑」指令並回報實際輸出；沒有證據不得宣稱完成。
- 結構重構不得改變交易語義、指標定義、資料語義或正式術語；需要改變時先停下來取得使用者確認。
- 「分析／規劃」「修改」「commit」「push」是不同的授權節點；實作完成不代表可以 commit 或 push，除非使用者已明確授權。
- 跨 repo 影響不得在未授權下自動同步；回報使用者，並由 Trading-Research-Workspace 的 `registry/pending-impacts.yaml` 追蹤。

### 施工說明

- 交給實作者的工作以施工說明描述，放在目標 repo 的 `docs/specs/`，格式依 `docs/specs/TEMPLATE.md`。
- 執行施工說明時只做說明範圍內的事；說明沒寫到的地方先問，不自行補完。
- 遇到說明列出的「停下來問」條件，或發現說明與現況矛盾時，停止並回報。
- 不得修改說明列為「受保護檔案」的路徑（驗收測試、基準結果）；認為驗收測試有錯時停下來回報。`tools/repo_check.py` 會檢查。
- 完成時回報：驗收指令的實際輸出、變更檔案清單、說明未涵蓋而需要使用者決定的事項。
- 驗收發現的偏差記入該說明的「偏差紀錄」，由規劃者轉成新的檢查或規則。

### Commit 與回報（讓使用者不靠 AI 也能審查）

- commit 訊息用繁體中文：第一行說明做了什麼；內文列出主要變更與原因（多個面向時分點），並有一行「驗證：…」寫明跑了什麼檢查與結果，未驗證須寫明原因。`Agent:` 行與英文 trailer（如 `Co-Authored-By`）放在最後。
- 一個 commit 只放一個可獨立回退的變更；不確定怎麼切時先問。
- 新寫或修改的程式註解、docstring、錯誤訊息與工具輸出用繁體中文；識別字維持英文。
- 交給使用者的完成回報與 PR 說明用繁體中文，先寫結論，再列細節。

### 檔案格式

- 參數檔與設定檔（策略參數、回測設定、機器人 preset 與實例設定、工具設定）一律使用 JSON。
- registry 與文件型資料清單維持 YAML；文件用 Markdown。
- 本機專用設定以 `*.example.json` 範本提交，實際檔案不提交；secrets 另放 `.env` 類檔案，不寫進 JSON 參數檔。
- 既有的 YAML 參數檔在各自的搬遷階段改為 JSON，搬遷前不單獨改格式。

### Codebase Memory（CBM）

- CBM（程式碼知識圖譜，`codebase-memory-mcp`）是選用工具：環境有此工具時，跨檔案分析前可優先查詢本 repo 的 CBM project；沒有時直接讀原始碼，不視為阻塞。
- CBM 結果必須回到目前原始碼驗證；宣稱「某符號不存在或沒有呼叫者」前，須確認索引新鮮度或直接搜尋原始碼。
- 每個 repo 是獨立 CBM project，共享索引位於 `.codebase-memory/graph.db.zst`。有工具且做了結構性變更時，順手刷新並提交索引；沒有工具時不必補做，也不建立 PENDING。
<!-- END SHARED RULES -->
