# Claude Office - Claude CLI Session 監聯方案

## 🎯 目標
監控 **Claude CLI** 的 session 狀態（不是 OpenClaw），四個狀態：
- 開啟、工作、閒置、關閉

---

## 📁 Claude CLI 資料結構

### Session 存放位置
```
~/.claude/projects/<project-path-hash>/<session-id>.jsonl
```

範例：
```
/mnt/e_drive/claude-config/projects/-mnt-e-drive-trading/d1874eac-f746-45c7-a42d-7dfaf406adfc.jsonl
```

### 歷史記錄
```
~/.claude/history.jsonl
```
包含 `sessionId`、`project`、`timestamp` 等資訊。

---

## 🔍 監聽策略

### 方案 A：檔案系統監控（推薦）

**原理**：使用 `fs.watch` 或 `inotify` 監控 session 檔案的變化

**優點**：
- 即時性好
- 不需要輪詢
- 資源消耗低

**判定邏輯**：
| 狀態 | 判定條件 |
|-----|---------|
| **開啟** | 新的 .jsonl 檔案被建立 |
| **工作** | .jsonl 檔案正在被寫入（mtime 變化 < 3秒） |
| **閒置** | .jsonl 檔案存在但 mtime 超過 3 秒未變化 |
| **關閉** | .jsonl 檔案的檔案句柄被釋放 / 進程結束 |

### 方案 B：進程監控

**原理**：監控 `claude` 進程及其開啟的檔案

```bash
# 找出所有 claude 進程
ps aux | grep claude

# 找出進程開啟的檔案
lsof -p <pid> | grep .jsonl
```

**優點**：
- 可以精確知道哪個 session 對應哪個進程
- 可以區分多個並發的 claude 實例

---

## 🏗️ 實現架構

```
┌─────────────────────────────────────────────────────────────┐
│                    Session Monitor 服務                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    fs.watch     ┌──────────────────┐     │
│  │ ~/.claude/   │ ──────────────→ │  Session Tracker │     │
│  │ projects/    │                 │  (狀態機)        │     │
│  └──────────────┘                 └────────┬─────────┘     │
│                                            │               │
│                                            │ WebSocket     │
│                                            ↓               │
│                                   ┌──────────────────┐     │
│                                   │  PixiJS Frontend │     │
│                                   │  :8051           │     │
│                                   └──────────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 技術實現

### 1. Session Monitor (Node.js)

```javascript
// 核心邏輯示意
const chokidar = require('chokidar');
const ws = require('ws');

const CLAUDE_DIR = '/home/rex/.claude/projects';
const sessions = new Map(); // sessionId -> { status, lastUpdate }

// 監控所有 .jsonl 檔案
const watcher = chokidar.watch(`${CLAUDE_DIR}/**/*.jsonl`);

watcher
  .on('add', path => {
    // 新 session 開啟
    const sessionId = path.split('/').pop().replace('.jsonl', '');
    sessions.set(sessionId, { status: 'open', lastUpdate: Date.now() });
    broadcast({ type: 'session_open', sessionId });
  })
  .on('change', path => {
    // session 正在工作
    const sessionId = path.split('/').pop().replace('.jsonl', '');
    const session = sessions.get(sessionId);
    if (session) {
      session.status = 'working';
      session.lastUpdate = Date.now();
      broadcast({ type: 'session_working', sessionId });
    }
  });

// 定期檢查閒置狀態
setInterval(() => {
  const now = Date.now();
  sessions.forEach((session, sessionId) => {
    if (session.status === 'working' && now - session.lastUpdate > 3000) {
      session.status = 'idle';
      broadcast({ type: 'session_idle', sessionId });
    }
  });
}, 1000);
```

### 2. WebSocket 協議

```typescript
// 服務端 → 客戶端
interface SessionEvent {
  type: 'session_open' | 'session_working' | 'session_idle' | 'session_close';
  sessionId: string;
  timestamp: number;
  projectPath?: string;
}

// 客戶端連接後，先發送當前狀態
interface SyncEvent {
  type: 'sync';
  sessions: SessionInfo[];
}
```

---

## ⚠️ 注意事項

1. **權限**：需要讀取 `~/.claude/` 目錄
2. **路徑**：溫水的 `.claude` 是 symlink 到 `/mnt/e_drive/claude-config`
3. **多專案**：需要支援多個專案路徑
4. **Session 上限**：最多 5 個活躍 session（對應 5 個角色）

---

## 🔧 下一步

1. 建立 `src/session-monitor/` 目錄
2. 實現檔案監控邏輯
3. 實現 WebSocket 服務
4. 測試與驗證

---
*建立日期：2026-03-02*
