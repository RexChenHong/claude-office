/**
 * Claude Office - Session Monitor
 *
 * 監控 Claude CLI 的 session 狀態，透過 WebSocket 推送給前端
 */

import { watch } from 'chokidar';
import { WebSocketServer } from 'ws';
import { resolve, basename } from 'path';
import { statSync } from 'fs';

// ============ 配置 ============
const CONFIG = {
  // Claude CLI 資料目錄（真實路徑，避免 symlink 問題）
  claudeDir: process.env.CLAUDE_DIR || '/mnt/e_drive/claude-config',
  projectsDir: process.env.CLAUDE_PROJECTS_DIR || '/mnt/e_drive/claude-config/projects',

  // WebSocket 設定
  wsPort: parseInt(process.env.WS_PORT) || 8053,

  // 狀態判定時間閾值（毫秒）
  workingThreshold: 3000,  // 3 秒內有更新 = 工作中
  checkInterval: 1000,     // 每秒檢查一次閒置狀態

  // 最大 session 數量（對應角色數）
  maxSessions: 5,
};

// ============ 狀態管理 ============
const sessions = new Map(); // sessionId -> SessionInfo

/**
 * @typedef {Object} SessionInfo
 * @property {string} id - Session ID
 * @property {string} project - 專案路徑
 * @property {'open' | 'working' | 'idle' | 'closed'} status - 狀態
 * @property {number} lastUpdate - 最後更新時間戳
 * @property {string} filePath - 對應的 .jsonl 檔案路徑
 */

/**
 * 從檔案路徑提取 session ID
 */
function extractSessionId(filePath) {
  const filename = basename(filePath);
  return filename.replace('.jsonl', '');
}

/**
 * 從檔案路徑提取專案名稱
 */
function extractProjectName(filePath) {
  const parts = filePath.split('/');
  const projectsIndex = parts.findIndex(p => p === 'projects');
  if (projectsIndex !== -1 && parts.length > projectsIndex + 1) {
    return parts[projectsIndex + 1];
  }
  return 'unknown';
}

// ============ WebSocket 服務 ============
let wss = null;
const clients = new Set();

function initWebSocket() {
  wss = new WebSocketServer({ port: CONFIG.wsPort });

  wss.on('connection', (ws) => {
    console.log(`[WS] 客戶端已連接，當前連接數: ${clients.size + 1}`);
    clients.add(ws);

    // 連接時發送當前所有 session 狀態
    sendSync(ws);

    ws.on('close', () => {
      clients.delete(ws);
      console.log(`[WS] 客戶端已斷開，當前連接數: ${clients.size}`);
    });

    ws.on('error', (err) => {
      console.error('[WS] 錯誤:', err.message);
      clients.delete(ws);
    });
  });

  console.log(`[WS] WebSocket 服務已啟動，端口: ${CONFIG.wsPort}`);
}

/**
 * 發送同步訊息給特定客戶端
 */
function sendSync(ws) {
  const sessionList = Array.from(sessions.values());
  const msg = JSON.stringify({
    type: 'sync',
    timestamp: Date.now(),
    sessions: sessionList,
  });
  ws.send(msg);
}

/**
 * 廣播訊息給所有客戶端
 */
function broadcast(event) {
  const msg = JSON.stringify({
    ...event,
    timestamp: event.timestamp || Date.now(),
  });

  let sent = 0;
  clients.forEach((ws) => {
    if (ws.readyState === 1) { // WebSocket.OPEN
      ws.send(msg);
      sent++;
    }
  });

  console.log(`[Broadcast] ${event.type} → ${sent} 客戶端`);
}

// ============ Session 管理 ============

/**
 * 註冊新 session
 */
function registerSession(filePath) {
  const id = extractSessionId(filePath);
  const project = extractProjectName(filePath);

  // 檢查檔案最後修改時間，只追蹤最近 10 分鐘內活躍的 session
  try {
    const stats = statSync(filePath);
    const fileAge = Date.now() - stats.mtimeMs;
    const maxAge = 10 * 60 * 1000; // 10 分鐘

    if (fileAge > maxAge) {
      // 舊檔案，不追蹤
      return null;
    }
  } catch (err) {
    // 檔案可能已被刪除
    return null;
  }

  // 檢查是否超過上限
  if (sessions.size >= CONFIG.maxSessions && !sessions.has(id)) {
    console.log(`[Session] 達到上限 ${CONFIG.maxSessions}，忽略新 session: ${id}`);
    return null;
  }

  const sessionInfo = {
    id,
    project,
    status: 'open',
    lastUpdate: Date.now(),
    filePath,
  };

  sessions.set(id, sessionInfo);
  console.log(`[Session] 開啟: ${id} (專案: ${project})`);

  // 廣播開啟事件
  broadcast({
    type: 'session_open',
    sessionId: id,
    project,
  });

  return sessionInfo;
}

/**
 * 更新 session 狀態為「工作中」
 */
function updateSessionWorking(filePath) {
  const id = extractSessionId(filePath);
  const session = sessions.get(id);

  if (!session) {
    // 可能是新 session，嘗試註冊
    registerSession(filePath);
    return;
  }

  const now = Date.now();
  session.lastUpdate = now;

  // 只有從非 working 狀態切換時才廣播
  if (session.status !== 'working') {
    session.status = 'working';
    console.log(`[Session] 工作中: ${id}`);

    broadcast({
      type: 'session_working',
      sessionId: id,
    });
  }
}

/**
 * 標記 session 為已關閉
 */
function closeSession(filePath) {
  const id = extractSessionId(filePath);
  const session = sessions.get(id);

  if (!session) return;

  sessions.delete(id);
  console.log(`[Session] 關閉: ${id}`);

  broadcast({
    type: 'session_close',
    sessionId: id,
  });
}

/**
 * 定期檢查閒置狀態
 */
function checkIdleStatus() {
  const now = Date.now();

  sessions.forEach((session, id) => {
    if (session.status === 'working') {
      const idleTime = now - session.lastUpdate;

      if (idleTime > CONFIG.workingThreshold) {
        session.status = 'idle';
        console.log(`[Session] 閒置: ${id} (閒置 ${Math.round(idleTime / 1000)}秒)`);

        broadcast({
          type: 'session_idle',
          sessionId: id,
        });
      }
    }
  });
}

/**
 * 定期清理過期 session（10 分鐘無更新）
 */
function cleanupStaleSessions() {
  const now = Date.now();
  const maxAge = 10 * 60 * 1000; // 10 minutes

  sessions.forEach((session, id) => {
    try {
      const stats = statSync(session.filePath);
      const fileAge = now - stats.mtimeMs;
      if (fileAge > maxAge) {
        console.log(`[Session] 過期清理: ${id} (${Math.round(fileAge / 60000)}分鐘無更新)`);
        closeSession(session.filePath);
      }
    } catch (err) {
      // File no longer exists, clean up
      closeSession(session.filePath);
    }
  });
}

// ============ 檔案監控 ============

function initWatcher() {
  const watchPath = CONFIG.projectsDir;

  console.log(`[Watcher] 監控路徑: ${watchPath}`);

  const watcher = watch(watchPath, {
    ignored: [
      /(^|[\/\\])\../, // 忽略隱藏檔案
      /(^|[\/\\])node_modules/, // 忽略 node_modules
    ],
    persistent: true,
    ignoreInitial: false, // 初始化時也觸發 add 事件
    depth: 99, // 遞歸深度
  });

  // Only track top-level .jsonl files (not subagents/)
  const isTopLevelSession = (path) => {
    if (!path.endsWith('.jsonl')) return false;
    if (path.includes('/subagents/')) return false;
    return true;
  };

  watcher
    .on('add', (path) => {
      if (!isTopLevelSession(path)) return;
      console.log(`[Watcher] 新增檔案: ${path}`);
      registerSession(path);
    })
    .on('change', (path) => {
      if (!isTopLevelSession(path)) return;
      updateSessionWorking(path);
    })
    .on('unlink', (path) => {
      if (!isTopLevelSession(path)) return;
      console.log(`[Watcher] 刪除檔案: ${path}`);
      closeSession(path);
    })
    .on('error', (error) => {
      console.error(`[Watcher] 錯誤:`, error);
    })
    .on('ready', () => {
      console.log('[Watcher] 初始掃描完成，開始監控');
    });

  return watcher;
}

// ============ 主程式 ============

function main() {
  console.log('========================================');
  console.log('  Claude Office - Session Monitor');
  console.log('========================================');
  console.log(`Claude 目錄: ${CONFIG.claudeDir}`);
  console.log(`專案目錄: ${CONFIG.projectsDir}`);
  console.log(`WebSocket 端口: ${CONFIG.wsPort}`);
  console.log(`最大 Session 數: ${CONFIG.maxSessions}`);
  console.log('========================================\n');

  // 初始化 WebSocket
  initWebSocket();

  // 初始化檔案監控
  const watcher = initWatcher();

  // 定期檢查閒置狀態
  const idleChecker = setInterval(checkIdleStatus, CONFIG.checkInterval);

  // 定期清理過期 session
  const staleChecker = setInterval(cleanupStaleSessions, 30 * 1000);

  // 優雅關閉
  process.on('SIGINT', () => {
    console.log('\n[Main] 收到 SIGINT，正在關閉...');

    clearInterval(idleChecker);
    clearInterval(staleChecker);
    watcher.close();

    if (wss) {
      wss.close(() => {
        console.log('[WS] WebSocket 服務已關閉');
        process.exit(0);
      });
    } else {
      process.exit(0);
    }
  });

  process.on('SIGTERM', () => {
    console.log('\n[Main] 收到 SIGTERM，正在關閉...');
    process.exit(0);
  });
}

main();
