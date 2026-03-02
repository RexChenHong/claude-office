# Claude Office

> 視覺化 Claude CLI Session 的辦公室場景

## 🎯 專案目標

以日系原神風格的辦公室場景，即時顯示 Claude CLI session 的狀態變化。

## 🏗️ 架構

```
┌─────────────────┐    WebSocket    ┌─────────────────┐
│  Claude CLI     │  ───────────→   │ Session Monitor │
│  (~/.claude/)   │                 │   :8053         │
└─────────────────┘                 └────────┬────────┘
                                             │
                                             ↓
                                    ┌─────────────────┐
                                    │  PixiJS UI      │
                                    │  :8051          │
                                    └─────────────────┘
```

**注意**: 端口 8052 已被硬體監控服務佔用，WebSocket 服務改用 8053。

## 🚀 快速開始

### 1. 安裝依賴

```bash
# Session Monitor
cd src/session-monitor
npm install

# UI
cd ../ui
npm install
```

### 2. 啟動服務

```bash
# 終端機 1：Session Monitor
cd src/session-monitor
npm start

# 終端機 2：UI
cd src/ui
npm run dev
```

### 3. 開啟瀏覽器

```
http://100.113.156.108:8051/
```

## 📁 目錄結構

```
claude-office/
├── docs/                    # 文檔
│   ├── REQUIREMENTS.md      # 需求
│   ├── ARCHITECTURE.md      # 架構
│   ├── CHARACTERS.md        # 角色設計
│   ├── SESSION_MONITOR.md   # Session 監控方案
│   ├── PROGRESS.md          # 進度
│   └── TODO.md              # 待辦
├── knowledge/               # 知識庫
│   └── TECH_STACK.md        # 技術選型
├── src/
│   ├── session-monitor/     # Session 監控服務
│   │   ├── index.js
│   │   └── package.json
│   └── ui/                  # 前端
│       ├── index.html
│       ├── vite.config.js
│       └── src/main.js
└── README.md
```

## 🎭 角色設計

| # | 名字 | 風格 | 個性 |
|---|-----|------|-----|
| 1 | 🌸 櫻 | 粉髮優雅秘書長 | 可靠、領導氣質 |
| 2 | 🔥 焰 | 紅髮熱血工程師 | 熱血、直接 |
| 3 | 💧 涼 | 藍髮冷靜分析師 | 理性、話少 |
| 4 | ⚡ 琴 | 金髮活力企劃 | 活潑、天然呆 |
| 5 | 🌙 宵 | 紫髮神秘守護者 | 腹黑、熬夜冠軍 |

## 🔌 WebSocket 協議

### 服務端 → 客戶端

```typescript
// 同步所有 session
{ type: 'sync', sessions: SessionInfo[] }

// Session 狀態變化
{ type: 'session_open', sessionId: string, project: string }
{ type: 'session_working', sessionId: string }
{ type: 'session_idle', sessionId: string }
{ type: 'session_close', sessionId: string }
```

## 📊 Session 狀態判定

| 狀態 | 判定條件 |
|-----|---------|
| 開啟 | 新的 .jsonl 檔案被建立 |
| 工作 | .jsonl 檔案正在被寫入（mtime 變化 < 3秒） |
| 閒置 | .jsonl 檔案存在但 mtime 超過 3 秒未變化 |
| 關閉 | Session 結束 |

## 📝 版本控管

```bash
git clone https://github.com/RexChenHong/claude-office.git
```

## 📄 License

MIT
