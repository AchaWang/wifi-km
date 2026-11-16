# 深入解析：WiFi 無線滑鼠與鍵盤開發教學

這份教學文檔旨在帶您從零開始，徹底了解我們剛剛開發的「WiFi 無線滑鼠與鍵盤」專案的觀念、原理以及開發流程。

---

## 1. 系統架構與核心概念 (Architecture & Concepts)

這個專案是一個標準的 **Client-Server (主從式架構)** 應用：
- **Server (伺服器端 - 電腦)**：執行 Python 程式碼，負責「聆聽」手機傳來的指令，並對電腦的滑鼠和鍵盤進行實體控制。
- **Client (客戶端 - 手機)**：透過瀏覽器開啟一個網頁介面，負責捕捉使用者的手指滑動與打字操作，並將這些操作轉譯成指令發送出去。

### 為什麼使用 WebSocket？
傳統的 HTTP 請求 (像是您瀏覽網頁) 是**單向且短暫**的：「手機發出請求 ➡️ 伺服器回傳網頁 ➡️ 斷開連線」。
但滑鼠移動需要**極高的即時性**，如果手機每移動一毫米就發送一次 HTTP 請求，會造成巨大的網路延遲與負擔。

**WebSocket** 解決了這個問題。它會在手機與電腦之間建立一條**持續開啟的雙向通道**。一旦連線建立，手機就可以幾乎零延遲地將滑鼠的 `dx` (X軸位移) 與 `dy` (Y軸位移) 像流水一樣不斷傳給電腦。

---

## 2. 關鍵技術堆疊 (Tech Stack)

了解我們為什麼選擇這些工具，是學習架構設計的第一步：

1. **`uv` (專案管理)**：新一代極速的 Python 套件管理工具。用來取代傳統的 `pip` 與 `venv`，能更乾淨地管理專案的依賴環境。
2. **`FastAPI` (後端框架)**：目前最主流、效能極高的 Python Web 框架。我們用它來做兩件事：
   - 提供靜態網頁 (把 HTML/CSS/JS 傳給手機)。
   - 建立 WebSocket 端點 (負責即時接收資料)。
3. **`pynput` (系統控制)**：這是一個能與作業系統底層 API 溝通的套件，可以模擬真實的滑鼠移動、點擊和鍵盤敲擊。
4. **HTML5 Touch Events (前端技術)**：手機瀏覽器專屬的 JavaScript 事件 (`touchstart`, `touchmove`, `touchend`)，用來精準捕捉多指觸控。

---

## 3. 開發流程大解密 (Development Workflow)

我們剛剛的開發過程，其實遵循了一個非常經典的軟體工程迭代流程：

### 第一步：環境建置與初始化
我們使用 `uv init` 建立專案，並使用 `uv add` 安裝了 `fastapi`, `uvicorn`, `websockets`, `pynput`, `qrcode`, `pillow`。
**觀念**：好的開始是成功的一半，將套件統一記錄在 `pyproject.toml` 中，確保專案未來在別台電腦也能一鍵安裝運行。

### 第二步：打通基礎通訊 (後端伺服器)
在撰寫複雜的控制邏輯前，我們必須先讓手機「連得上」電腦。
1. 寫一個小函數 `get_local_ip()`，讓電腦自動查出自己在 WiFi 路由器下的 IP 地址 (例如 `192.168.1.50`)。
2. 使用 `qrcode` 套件，把網址 (`http://192.168.1.50:8000`) 轉成圖片並彈出。這樣使用者就不用辛苦手打網址。
3. 建立 FastAPI 的 `/ws` (WebSocket) 端點，用一個 `while True:` 迴圈持續接收訊息。

### 第三步：實作前端操作介面 (UI & UX)
網頁不僅要能用，還要好看。我們使用了 CSS 的 **Glassmorphism (毛玻璃)** 風格設計觸控板：
- **擷取位移原理**：在 `touchstart` 時記錄手指按下的起始座標 $(x_1, y_1)$。在 `touchmove` 時取得當前座標 $(x_2, y_2)$，計算出位移量 $dx = x_2 - x_1$ 和 $dy = y_2 - y_1$。
- **發送資料**：將算出的 $dx, dy$ 包裝成 JSON 格式 `{"type": "move", "dx": 5, "dy": -2}` 傳送給後端。傳完後，要把 $(x_2, y_2)$ 設為新的起始座標，為下一次滑動做準備。

### 第四步：後端解析與執行控制
電腦端收到 JSON 後，進行解析 (Parse)：
```python
# 概念示範
if type == "move":
    mouse.move(dx, dy)
elif type == "type_text":
    keyboard.type(text)
```
這裡依賴了 `pynput` 將虛擬的數據轉換成實體的電腦游標移動。

### 第五步：功能迭代 (Iteration) - 解決打字痛點
在初步完成後，我們發現了一個體驗問題：「手機每打一個字就傳送，會導致選字困難」。
這正是軟體開發中常見的 **User Feedback Loop (使用者反饋迴圈)**。
- **舊做法 (Real-time Input)**：監聽手機隱藏輸入框的 `input` 事件，打一個字傳一個字。
- **新做法 (Batch Submit)**：改成讓使用者在手機上看到完整的輸入框，安心選字、修改，直到按下「送出文字」按鈕時，才把整串文字打包成 `{"type": "type_text", "text": "你好"}` 一次發送給電腦。

---

## 4. 進階學習：程式碼中的魔鬼細節

### 1. 為何前端要加 `e.preventDefault()`？
在手機瀏覽器上滑動時，預設行為是「捲動網頁 (Scroll)」。如果不加 `e.preventDefault()` 阻止預設行為，當您在觸控板滑鼠時，整個網頁會跟著上下滾動，導致滑鼠控制完全失效。

### 2. 靈敏度 (Sensitivity) 的魔法
在前端 JS 中我們有一個變數 `const sensitivity = 1.8;`。手機螢幕很小，電腦螢幕很大；如果不乘上這個放大倍率，您在手機上滑了半天，電腦游標可能只移動了一小段距離。這就是常見的「滑鼠加速/靈敏度」原理。

### 3. JSON 的重要性
WebSocket 只負責傳送「字串」。我們必須用 JSON (`JSON.stringify` 和 `json.loads`) 把複雜的結構 (例如包含指令類型、X座標、Y座標的物件) 轉換成字串傳送，接收端再還原成物件。這是現代網路通訊的通用語言。

---

## 5. 軟體發布：打包成獨立執行檔 (PyInstaller)

當我們寫好程式後，如果要分享給沒有安裝 Python 的朋友，最好的方式就是把它打包成一個獨立的 `.exe` 執行檔。我們使用了著名的 `PyInstaller` 工具來完成這件事。

### 核心挑戰：靜態檔案的「迷航」
如果您只是單純打包純 Python 程式，通常沒什麼問題。但我們的專案包含了一個 `static/` 資料夾（裡面有我們精心設計的 HTML 網頁）。
當 PyInstaller 建立 `--onefile` (單一執行檔) 時，程式在執行瞬間，會把所有檔案解壓縮到電腦的一個**隱藏的隨機暫存資料夾**（通常叫做 `_MEIxxxxx`）。這會導致 FastAPI 原本設定的相對路徑找不到 `static` 資料夾，造成網頁無法顯示。

### 解決方案：動態路徑判斷
為了讓程式知道自己「現在是被當作原始碼執行，還是被打包成了 EXE」，我們在 `main.py` 加入了一段非常經典的判斷邏輯：
```python
import sys, os

# 判斷是否被 PyInstaller 打包 (frozen 狀態)
if getattr(sys, 'frozen', False):
    # 如果是打包狀態，使用 PyInstaller 提供的 _MEIPASS 暫存目錄
    base_dir = sys._MEIPASS
else:
    # 如果是正常執行，使用腳本原本所在的目錄
    base_dir = os.path.dirname(os.path.abspath(__file__))

# 組合出正確的靜態檔案路徑
static_dir = os.path.join(base_dir, "static")
```

### 打包指令解析
修改好程式後，我們執行了這串威力強大的編譯指令：
```bash
uv run pyinstaller --name WiFiMouse --onefile --add-data "static;static" --collect-all uvicorn --collect-all fastapi main.py
```
- `--name WiFiMouse`：設定最終產生的檔案名稱。
- `--onefile`：告訴工具把所有東西 (包含 Python 直譯器) 揉合進一個乾淨的 `.exe` 中。
- `--add-data "static;static"`：把我們的網頁資料夾一併塞進去。
- `--collect-all`：因為 FastAPI 與 Uvicorn 是非常複雜的框架，有很多隱藏的依賴（Hidden Imports），使用這個參數能強制把所有需要的底層零件都打包進去，防止執行時報錯。

---

## 結語

開發這個專案，您實際上已經觸及了全端工程師 (Full-stack Developer) 的核心技能：
1. **後端** API 與 WebSocket 伺服器建置 (Python)。
2. **前端** UI 切版與 DOM 事件控制 (HTML/CSS/JS)。
3. **系統整合** 與作業系統底層 API 的呼叫 (滑鼠鍵盤控制)。

如果您想進一步練習，可以試著自己為專案加入「**雙指上下滑動 = 滑鼠滾輪 (Scroll)**」的功能，這會是個絕佳的練手挑戰！
