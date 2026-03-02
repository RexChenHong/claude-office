# Claude Office - 技術架構

## 系統架構圖

```
┌─────────────────────────────────────────────────────────────────┐
│                        Claude Office 系統                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐     WebSocket      ┌─────────────────────┐    │
│  │   瀏覽器     │ ←───────────────→ │   狀態監控服務       │    │
│  │  PixiJS     │                    │   (Node.js)         │    │
│  │  :8051      │                    │   :8052             │    │
│  └─────────────┘                    └──────────┬──────────┘    │
│                                                │                │
│                                                │ 輪詢           │
│                                                ↓                │
│                                     ┌─────────────────────┐    │
│                                     │   OpenClaw Gateway   │    │
│                                     │   sessions_list API  │    │
│                                     └─────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Session 狀態監聽方案

### 設計原則
- **不影響 OpenClaw 核心運作**
- **獨立服務，低耦合**
- **只關注四個狀態**

### 狀態判定邏輯

| 狀態 | 判定條件 |
|-----|---------|
| **開啟** | session 從無到有（新增） |
| **工作** | session 存在 + `updatedAt` 在 5 秒內有變化 |
| **閒置** | session 存在 + `updatedAt` 超過 5 秒未變化 |
| **關閉** | session 從有到無（消失） |

### 技術實現

**1. 狀態監控服務（session-monitor）**
- 獨立 Node.js 服務
- 每 2 秒調用 OpenClaw `sessions_list` API
- 比對前後狀態，判斷變化
- 透過 WebSocket 推送給前端

**2. 前端（claude-office-ui）**
- PixiJS 場景渲染
- WebSocket 接收狀態更新
- 角色狀態機控制動畫

---

## 部署規劃

| 服務 | Port | 說明 |
|-----|------|------|
| claude-office-ui | 8051 | PixiJS 前端網頁 |
| session-monitor | 8052 | 狀態監控 WebSocket |

---

## 檔案結構

```
/mnt/e_drive/claude-office/
├── docs/                    # 文檔
│   ├── REQUIREMENTS.md      # 需求
│   ├── PROGRESS.md          # 進度
│   └── ARCHITECTURE.md      # 架構（本文件）
├── knowledge/               # 知識庫
│   └── TECH_STACK.md        # 技術選型
├── assets/                  # 美術資產
│   ├── characters/          # 角色素材
│   ├── backgrounds/         # 背景素材
│   └── animations/          # 動畫素材
├── src/
│   ├── session-monitor/     # 狀態監控服務
│   │   ├── package.json
│   │   └── index.js
│   └── ui/                  # 前端
│       ├── index.html
│       ├── package.json
│       └── src/
│           ├── main.js
│           ├── scenes/
│           ├── characters/
│           └── states/
└── README.md
```

---
*建立日期：2026-03-02*
