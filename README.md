# WiFi Mouse & Keyboard

這是一個透過區域網路 (WiFi) 讓手機變成電腦無線滑鼠與鍵盤的開源專案。
不需要安裝任何手機 APP，只要電腦啟動伺服器，手機掃描 QR Code 即可連線控制！

## 🌟 專案功能

- **無線滑鼠控制**：支援單指觸控板滑動控制游標，支援左鍵與右鍵點擊。
- **滑鼠滾輪模擬**：支援觸控板雙指上下滑動來滾動網頁。
- **手機虛擬鍵盤**：透過手機的鍵盤打字，支援中英打字選字後一次送出到電腦。
- **即時通訊**：使用 WebSocket 技術，達到幾乎零延遲的操作體驗。
- **美觀介面**：深色系 (Dark Mode) 與毛玻璃 (Glassmorphism) 的現代感前端介面。
- **自動彈出 QR Code**：啟動後自動顯示 QR Code 圖片供手機掃描，不用手動輸入 IP。

## 🛠️ 技術架構

- **後端 (Backend)**：`Python`, `FastAPI`, `Uvicorn`, `WebSockets`
- **系統控制 (OS Control)**：`pynput` (負責模擬滑鼠與鍵盤操作)
- **前端 (Frontend)**：`HTML5`, `CSS3`, `Vanilla JavaScript` (Touch Events)
- **環境管理**：`uv` (極速 Python 專案管理工具)

## 🚀 如何執行

1. **確認環境**：確保您已安裝 [uv](https://github.com/astral-sh/uv) (或者使用傳統的 `pip` 安裝 `pyproject.toml` 中的依賴)。
2. **啟動伺服器**：您可以直接點擊兩下專案中的 `start_server.bat` 來啟動，或在終端機執行：
   ```bash
   uv run python main.py
   ```
3. **連線使用**：
   - 確保手機與電腦連線至**同一個 WiFi 網路**。
   - 電腦畫面會自動彈出一個包含 QR Code 的視窗。
   - 用手機相機掃描 QR Code，在瀏覽器開啟網頁即可開始控制電腦！

## 📂 專案結構

- `main.py`: 後端主程式，負責啟動伺服器、產生 QR Code 與處理 WebSocket 訊息。
- `static/index.html`: 前端手機介面，包含觸控板與鍵盤的 UI 與互動邏輯。
- `tutorial.md`: 開發教學文檔，詳細記錄了此專案的開發流程與技術原理。
- `start_server.bat`: 快速啟動伺服器的批次檔 (推薦使用)，也可設定為開機啟動。
- `start_server.vbs`: 提供給 Windows 使用者設定「開機自動隱藏啟動」的腳本 (無黑畫面)。

## 💡 學習資源

如果您對這個專案是如何開發的感興趣，請務必閱讀本專案內附的 [tutorial.md](./tutorial.md) 教學文檔，裡面有詳細的觀念與程式碼原理解析！
