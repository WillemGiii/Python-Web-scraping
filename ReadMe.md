# 🕷️ Python 網路爬蟲實戰課程 — 範例程式碼

> **適用對象**：具備 Python 基礎語法的學習者  
> **課程目標**：從靜態網頁爬取到動態網頁操作，循序漸進地掌握網路爬蟲的核心技能

---

## 📋 目錄

1. [學習路徑](#-學習路徑)
2. [環境建置](#-環境建置)
3. [模組說明](#-模組說明)
4. [綜合實戰案例](#-綜合實戰案例)
5. [補充教材](#-補充教材)
6. [學習守則](#-學習守則)

---

## 🗺️ 學習路徑

本課程採**循序漸進**的設計，請依照以下順序逐步學習：

```
00_Environment_Setup     ← 第一步：建立虛擬環境與安裝套件
        ↓
01_Module_Requests       ← 第二步：學習發送 HTTP 請求
        ↓
02_Module_BeautifulSoup  ← 第三步：學習解析靜態 HTML
        ↓
03_Module_Selenium       ← 第四步：學習操作動態網頁
        ↓
04_Intergrated_Cases     ← 第五步：綜合應用真實案例
```

> ⚠️ **重要提醒**：請勿跳過 `00_Environment_Setup`，  
> 正確的環境設定是所有後續練習能夠順利執行的基礎。

---

## ⚙️ 環境建置

**對應資料夾**：`00_Environment_Setup/`

| 檔案 | 說明 |
|---|---|
| `1_Virtual_Env_Setup.md` | 虛擬環境建立步驟教學（必讀） |
| `requirements.txt` | 本課程所需的全部 Python 套件清單 |

### 快速安裝步驟

請在本目錄（`2_Code_Examples/`）下，開啟 **PowerShell** 並依序執行：

```powershell
# 步驟 1：建立名為 .venv 的虛擬環境
python -m venv .venv

# 步驟 2：啟動虛擬環境
.\.venv\Scripts\Activate.ps1

# 步驟 3：安裝所有必要套件
pip install -r .\00_Environment_Setup\requirements.txt
```

> ✅ 安裝完成後，確認虛擬環境已啟動（命令提示字元前方會出現 `(.venv)` 字樣），  
> 再使用 VS Code 或 Jupyter Lab 開啟後續的 `.ipynb` 筆記本。

### 本課程核心套件一覽

| 套件 | 用途 |
|---|---|
| `requests` | 發送 HTTP/HTTPS 請求，取得網頁原始資料 |
| `beautifulsoup4` | 解析 HTML/XML，提取靜態網頁內容 |
| `lxml` | 高效能 HTML/XML 解析器（BeautifulSoup 後端） |
| `selenium` | 自動化瀏覽器操作，處理動態網頁（JavaScript 渲染） |
| `pandas` | 結構化資料整理、清洗與匯出 |
| `python-dotenv` | 管理 `.env` 環境變數，保護敏感資訊（如 API 金鑰） |

---

## 📚 模組說明

### 01 — `requests`：HTTP 請求基礎

**對應資料夾**：`01_Module_Requests/`

| 筆記本 | 學習重點 |
|---|---|
| `01_Get_Request.ipynb` | GET 請求語法、Response 物件屬性、狀態碼判讀、Headers 設定 |

**核心概念**：
- 理解 HTTP 請求與回應的生命週期
- 分辨 `response.text`（字串）與 `response.json()`（字典）的應用場景
- 使用 `headers` 模擬瀏覽器行為，避免被網站阻擋

---

### 02 — `BeautifulSoup 4`：靜態 HTML 解析

**對應資料夾**：`02_Module_BeautifulSoup/`

| 筆記本 | 學習重點 |
|---|---|
| `01_BS4_起手式_引入套件與實例化物件.ipynb` | 建立 `BeautifulSoup` 物件、指定解析器 |
| `02_BS4_定位_快速導航與屬性.ipynb` | 利用 `.` 點記法快速定位標籤與讀取屬性 |
| `03_BS4_搜尋_Find方法詳解.ipynb` | `find()` 與 `find_all()` 的完整用法與過濾條件 |
| `04_BS4_搜尋_利用CSS選擇器的Select方法.ipynb` | 使用 `select()` 與 CSS 選擇器語法精確定位元素 |
| `05_BS4_搜尋_層次關係選擇器.ipynb` | 父子、兄弟節點的層次關係遍歷 |
| `06_BS4_進階_子字串與文字提取.ipynb` | `.string`、`.get_text()` 的差異與文字清洗技巧 |

**建議學習順序**：依檔案編號 `01 → 06` 依序進行。

---

### 03 — `Selenium`：動態網頁自動化

**對應資料夾**：`03_Module_Selenium/`

| 檔案 | 學習重點 |
|---|---|
| `01_Selenium_模組引入與初始化_Locators定位器.ipynb` | WebDriver 初始化、By 類別、各種定位器策略 |
| `02_Selenium_ExplictWaits.ipynb` | `WebDriverWait` + `expected_conditions`，精確等待元素就緒 |
| `03_Selenium_HandleDynamicContent.ipynb` | 處理動態載入內容（AJAX、無限捲動）的策略 |
| `04_Selenium_JavaScript_scrollto.py` | 使用 `execute_script()` 執行 JavaScript 捲動頁面 |
| `implicit_wait_demo.html` | 隱式等待（Implicit Wait）示範用的靜態測試頁面 |
| `action_chains_demo.html` | ActionChains 示範用的靜態測試頁面 |

> 💡 **觀念釐清**：優先使用**顯式等待**（Explicit Wait），  
> 避免使用 `time.sleep()`，因為後者無法因應網路速度變化，容易造成不穩定。

---

## 🏆 綜合實戰案例

**對應資料夾**：`04_Intergrated_Cases 綜合實戰/`

以下案例結合前三個模組的技術，請在完成模組單元後再進行練習。

| 資料夾 | 技術棧 | 說明 |
|---|---|---|
| `Case01_Requests案例_臺灣氣象即時觀測/` | `requests` + `.env` | 串接氣象署開放 API，取得即時觀測資料並結構化 |
| `Case02__Requests案例_104API/` | `requests` + `pandas` | 爬取 104 人力銀行 API，清洗職缺資料並匯出 CSV/JSON |
| `Case03_靜態爬蟲案例_PTT/` | `requests` + `BeautifulSoup` | 爬取 PTT 股板文章列表，解析標題、作者、留言數 |
| `Case04_動態爬蟲案例_LineMovie/` | `Selenium` + `pandas` | 以動態爬蟲擷取 LINE Movie 評論資料並存為 CSV |
| `Assignment01_動態爬蟲案例_mangaz/` | `Selenium` | 課後作業：自行完成指定動態網站的爬取任務 |

---

## 📖 補充教材

| 資料夾 | 主題 | 說明 |
|---|---|---|
| `99_[Supplementary materials]_Regex_4StringParsing&PatternMatching/` | 正規表達式（Regex） | 字串搜尋、格式驗證與複雜文字提取 |
| `99_[Supplementary materials]__The_Python_Standard_Library_Datetime/` | `datetime` 模組 | 日期時間解析與格式轉換，常用於爬取資料的時間戳處理 |

> 📌 這些補充教材**不在主要學習路徑中**，  
> 但在實際爬蟲開發時會頻繁使用，遇到需求時可隨時參閱。

---

## 📐 學習守則

1. **先理解原理，再看程式碼**。每個 Notebook 的開頭說明是核心，請勿直接略過。
2. **動手執行每一個儲存格**（Cell），觀察輸出結果，思考「為什麼是這個結果」。
3. **尊重網站爬蟲政策**。使用前請閱讀目標網站的 `robots.txt`，並在請求間加入適當的延遲（`time.sleep()`）。
4. **保護敏感資訊**。API 金鑰、帳號密碼等憑證請存放於 `.env` 檔案中，切勿直接寫入程式碼或上傳至 Git。
5. **遇到錯誤請先自行排查**：確認虛擬環境已啟動、套件版本是否符合 `requirements.txt`。

---

<div align="center">

**祝您學習順利！** 🚀  
如有任何疑問，請於課堂中提出，或透過課程平台與講師聯繫。

</div>
