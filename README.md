# TRPG Discord Bot (Python Version)

這是一個用 Python 編寫的 Discord 機器人，專為TRPG設計。

## 功能特性

- **擲骰系統**：支援 D&D 和 CoC 7e 擲骰
- **日誌系統**：即時串流和批次日誌記錄
- **管理功能**：重啟機器人、管理開發者等
- **配置管理**：JSON 格式的持久化配置

## 技術特點

- 使用 Python 編程語言，易於維護和擴展
- 基於 [discord.py](https://github.com/Rapptz/discord.py) 框架構建，提供現代化的 Slash 指令體驗
- 模組化設計便於擴展
- 透過 `.env` 管理敏感設定，並內建 JSON 配置持久化

## 安裝和運行

```bash
# 克隆項目
git clone <repository-url>
cd trpg-discord-bot-python

# 安裝依賴
pip install -r requirements.txt

# 設置環境變量
cp .env.example .env
# 編輯 .env 文件，將 'your_discord_bot_token_here' 替換為您的實際 Discord Bot Token

# 運行
python main.py
```

## 指令列表

### 擲骰指令

- `/roll <骰子表達式>` - D&D 擲骰
- `/coc <技能值> [次數]` - CoC 7e 擲骰，支援 1-10 次連續判定
- `/skill add <名稱> <類型> <等級> <效果>` - 新增或更新個人技能
- `/skill show <名稱>` - 支援模糊搜尋技能名稱，查詢自己的技能
- `/skill delete <名稱>` - 刪除此伺服器中符合的技能（含其他玩家），需要按鈕確認

### 日誌指令

- `/log-stream <on|off> [頻道]` - 控制日誌串流開關
- `/log-stream-mode <live|batch>` - 切換串流模式
- `/crit <success|fail> [頻道]` - 設定大成功/大失敗紀錄頻道，紀錄訊息會標註觸發頻道

### 管理指令

- `/admin restart` - 確認後重新啟動機器人
- `/admin shutdown` - 確認後關閉機器人
- `/admin dev-add <用戶>` - 添加開發者（需按鈕確認）
- `/admin dev-remove <用戶>` - 移除開發者（需按鈕確認）
- `/admin dev-list` - 展示開發者列表

### 幫助指令

- `/help` - 顯示指令說明

## 當前狀態

機器人功能完整且可正常運行。

## 未來計劃

1. **更多指令與系統支援**：擴充更多 TRPG 系統與自訂化功能。
2. **測試補強**：加入整合測試確保核心指令穩定性。
3. **性能優化**：進一步優化資源使用。

## 貢獻

歡迎提交 Issue 和 Pull Request 來改進這個項目！

## 許可證

MIT License