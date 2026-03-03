/**
 * Claude Office - Frontend Main
 *
 * 使用 PixiJS 渲染辦公室場景，透過 WebSocket 接收 session 狀態
 * 美術素材：Stable Diffusion 生成原神風格 6 頭身立繪
 */

import { Application, Container, Graphics, Text, Assets, Sprite } from 'pixi.js';

// ============ 配置 ============
const CONFIG = {
  // WebSocket 服務地址
  wsUrl: `ws://${window.location.hostname}:8053`,

  // 場景尺寸
  width: 1200,
  height: 700,

  // 角色配置
  characters: [
    { id: 1, name: '櫻', color: 0xffb7c5, hair: 'pink', folder: 'sakura' },
    { id: 2, name: '焰', color: 0xff6b6b, hair: 'red', folder: 'homura' },
    { id: 3, name: '涼', color: 0x74b9ff, hair: 'blue', folder: 'ryo' },
    { id: 4, name: '琴', color: 0xffd93d, hair: 'yellow', folder: 'koto' },
    { id: 5, name: '宵', color: 0xa29bfe, hair: 'purple', folder: 'yoi' },
  ],

  // 美術素材路徑
  assets: {
    backgrounds: '/assets/backgrounds',
    characters: '/assets/characters',
  },
};

// ============ 全域狀態 ============
let app = null;
let ws = null;
let office = null;
const characterSprites = new Map();
const sessionAssignments = new Map(); // sessionId -> characterId
const sessionDetails = new Map(); // sessionId -> { project, status, lastUpdate }
let nextCharacterIndex = 0;
let assetsLoaded = false;

// ============ 資源載入 ============

async function loadAssets() {
  console.log('[Assets] 開始載入美術素材...');

  // 載入背景
  Assets.add({ alias: 'bgWork', src: `${CONFIG.assets.backgrounds}/work_area.png` });
  Assets.add({ alias: 'bgLounge', src: `${CONFIG.assets.backgrounds}/lounge_area.png` });

  // 載入角色立繪
  CONFIG.characters.forEach((char) => {
    ['idle', 'working', 'waiting'].forEach((state) => {
      const key = `${char.folder}_${state}`;
      const path = `${CONFIG.assets.characters}/${char.folder}/${state}.png`;
      Assets.add({ alias: key, src: path });
    });
  });

  try {
    // 批次載入所有資源
    const backgrounds = await Assets.load(['bgWork', 'bgLounge']);
    console.log('[Assets] 背景載入完成');

    // 載入所有角色立繪
    const characterKeys = [];
    CONFIG.characters.forEach((char) => {
      ['idle', 'working', 'waiting'].forEach((state) => {
        characterKeys.push(`${char.folder}_${state}`);
      });
    });

    await Assets.load(characterKeys);
    console.log('[Assets] 角色立繪載入完成');

    assetsLoaded = true;
    console.log('[Assets] ✅ 所有素材載入完成');
  } catch (err) {
    console.error('[Assets] 載入失敗:', err);
    // 繼續使用 fallback 繪圖模式
    assetsLoaded = false;
  }
}

// ============ WebSocket 連接 ============

function connectWebSocket() {
  const statusEl = document.getElementById('ws-status');

  ws = new WebSocket(CONFIG.wsUrl);

  ws.onopen = () => {
    console.log('[WS] 已連接');
    statusEl.textContent = '✅ 已連接';
    statusEl.className = 'connected';
  };

  ws.onclose = () => {
    console.log('[WS] 已斷開');
    statusEl.textContent = '❌ 已斷開，重連中...';
    statusEl.className = 'disconnected';

    // 3 秒後重連
    setTimeout(connectWebSocket, 3000);
  };

  ws.onerror = (err) => {
    console.error('[WS] 錯誤:', err);
    statusEl.textContent = '❌ 連接錯誤';
    statusEl.className = 'disconnected';
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    handleMessage(data);
  };
}

function handleMessage(data) {
  console.log('[WS] 收到訊息:', data);

  switch (data.type) {
    case 'sync':
      handleSync(data.sessions);
      break;

    case 'session_open':
      handleSessionOpen(data.sessionId, data.project);
      break;

    case 'session_working':
      handleSessionWorking(data.sessionId);
      break;

    case 'session_idle':
      handleSessionIdle(data.sessionId);
      break;

    case 'session_close':
      handleSessionClose(data.sessionId);
      break;

    default:
      console.warn('[WS] 未知訊息類型:', data.type);
  }
}

// ============ Session 狀態處理 ============

function handleSync(sessions) {
  console.log('[Sync] 同步 session 狀態:', sessions);

  // 重置所有角色到休息區
  characterSprites.forEach((sprite, charId) => {
    updateCharacterState(sprite, 'idle');
    sprite.sessionId = null;
    moveToLounge(sprite);
  });

  sessionAssignments.clear();
  nextCharacterIndex = 0;

  // 重新分配活躍的 session
  sessions.forEach((session) => {
    assignCharacterToSession(session.id, session.project);

    if (session.status === 'working') {
      handleSessionWorking(session.id);
    } else if (session.status === 'idle') {
      handleSessionIdle(session.id);
    }
  });
}

function handleSessionOpen(sessionId, project) {
  console.log(`[Session] 開啟: ${sessionId}`);
  assignCharacterToSession(sessionId, project);
  sessionDetails.set(sessionId, {
    project,
    status: 'open',
    lastUpdate: Date.now(),
  });
  renderSessionPanel();
}

function handleSessionWorking(sessionId) {
  console.log(`[Session] 工作中: ${sessionId}`);

  const charId = sessionAssignments.get(sessionId);
  if (!charId) return;

  const sprite = characterSprites.get(charId);
  if (sprite) {
    updateCharacterState(sprite, 'working');
    moveToDesk(sprite);
  }

  updateSessionInfo(sessionId, 'working');
}

function handleSessionIdle(sessionId) {
  console.log(`[Session] 閂置: ${sessionId}`);

  const charId = sessionAssignments.get(sessionId);
  if (!charId) return;

  const sprite = characterSprites.get(charId);
  if (sprite) {
    updateCharacterState(sprite, 'waiting');
    moveToDesk(sprite); // 留在座位但狀態是等待
  }

  updateSessionInfo(sessionId, 'idle');
}

function handleSessionClose(sessionId) {
  console.log(`[Session] 關閉: ${sessionId}`);

  const charId = sessionAssignments.get(sessionId);
  if (!charId) return;

  const sprite = characterSprites.get(charId);
  if (sprite) {
    updateCharacterState(sprite, 'idle');
    sprite.sessionId = null;
    moveToLounge(sprite);
  }

  sessionAssignments.delete(sessionId);
  sessionDetails.delete(sessionId);
  renderSessionPanel();
}

function assignCharacterToSession(sessionId, project) {
  if (sessionAssignments.has(sessionId)) return;

  // 找一個閒置的角色
  const charConfig = CONFIG.characters[nextCharacterIndex % CONFIG.characters.length];
  nextCharacterIndex++;

  const sprite = characterSprites.get(charConfig.id);
  if (sprite) {
    sprite.sessionId = sessionId;
    sessionAssignments.set(sessionId, charConfig.id);
    console.log(`[Assign] Session ${sessionId} → 角色 ${charConfig.name}`);
  }
}

// ============ 場景渲染 ============

async function initPixi() {
  app = new Application();

  await app.init({
    width: CONFIG.width,
    height: CONFIG.height,
    backgroundColor: 0x1a1a2e,
    antialias: true,
    resolution: window.devicePixelRatio || 1,
    autoDensity: true,
  });

  document.getElementById('game-container').appendChild(app.canvas);

  // 建立場景
  createOffice();
  createCharacters();

  console.log('[Pixi] 初始化完成');
}

function createOffice() {
  office = new Container();
  app.stage.addChild(office);

  // 嘗試載入背景圖片
  if (assetsLoaded) {
    try {
      // 工作區背景
      const bgWork = new Sprite(Assets.get('bgWork'));
      bgWork.x = 600;
      bgWork.y = 0;
      bgWork.width = 600;
      bgWork.height = CONFIG.height;
      office.addChild(bgWork);

      // 休息區背景
      const bgLounge = new Sprite(Assets.get('bgLounge'));
      bgLounge.x = 0;
      bgLounge.y = 0;
      bgLounge.width = 600;
      bgLounge.height = CONFIG.height;
      office.addChild(bgLounge);

      console.log('[Office] 背景圖片載入成功');
      return;
    } catch (err) {
      console.warn('[Office] 背景圖片載入失敗，使用 fallback:', err);
    }
  }

  // Fallback: 繪製簡單背景
  createFallbackBackground();
}

function createFallbackBackground() {
  console.log('[Office] 使用 fallback 背景');

  // 地板
  const floor = new Graphics();
  floor.rect(0, 0, CONFIG.width, CONFIG.height);
  floor.fill({ color: 0x1e272e });
  office.addChild(floor);

  // 地板格紋
  for (let x = 0; x < CONFIG.width; x += 60) {
    const line = new Graphics();
    line.moveTo(x, 0);
    line.lineTo(x, CONFIG.height);
    line.stroke({ color: 0x2d3436, width: 1, alpha: 0.3 });
    office.addChild(line);
  }
  for (let y = 0; y < CONFIG.height; y += 60) {
    const line = new Graphics();
    line.moveTo(0, y);
    line.lineTo(CONFIG.width, y);
    line.stroke({ color: 0x2d3436, width: 1, alpha: 0.3 });
    office.addChild(line);
  }

  // ===== 辦公區（右側）=====
  const workBg = new Graphics();
  workBg.rect(600, 0, 600, CONFIG.height);
  workBg.fill({ color: 0x2d3436, alpha: 0.6 });
  office.addChild(workBg);

  const workTitle = new Text({
    text: '💼 工作區',
    style: { fontSize: 22, fill: 0xffffff, fontWeight: 'bold', fontFamily: 'Arial' },
  });
  workTitle.x = 620;
  workTitle.y = 20;
  office.addChild(workTitle);

  // ===== 休息區（左側）=====
  const loungeBg = new Graphics();
  loungeBg.rect(0, 0, 600, CONFIG.height);
  loungeBg.fill({ color: 0x6c5ce7, alpha: 0.35 });
  office.addChild(loungeBg);

  const loungeTitle = new Text({
    text: '🛋️ 休息區',
    style: { fontSize: 22, fill: 0xffffff, fontWeight: 'bold', fontFamily: 'Arial' },
  });
  loungeTitle.x = 20;
  loungeTitle.y = 20;
  office.addChild(loungeTitle);

  // 5 個辦公桌位置標記
  for (let i = 0; i < 5; i++) {
    const deskMarker = new Graphics();
    deskMarker.roundRect(620 + (i % 3) * 180, 80 + Math.floor(i / 3) * 300, 150, 200, 10);
    deskMarker.stroke({ color: 0x636e72, width: 2, alpha: 0.5 });
    office.addChild(deskMarker);
  }

  // 5 個沙發位置標記
  for (let i = 0; i < 5; i++) {
    const sofaMarker = new Graphics();
    sofaMarker.roundRect(30 + (i % 3) * 180, 80 + Math.floor(i / 3) * 300, 150, 200, 10);
    sofaMarker.stroke({ color: 0xa29bfe, width: 2, alpha: 0.5 });
    office.addChild(sofaMarker);
  }
}

function createCharacters() {
  CONFIG.characters.forEach((charConfig, index) => {
    const char = createCharacter(charConfig);

    // 初始位置在休息區
    char.x = 120 + (index % 3) * 180;
    char.y = 200 + Math.floor(index / 3) * 300;

    office.addChild(char);
    characterSprites.set(charConfig.id, char);
  });
}

function createCharacter(config) {
  const char = new Container();
  char.state = 'idle';
  char.charData = config;
  char.interactive = true;
  char.cursor = 'pointer';

  // 嘗試載入角色立繪
  if (assetsLoaded) {
    try {
      const textureKey = `${config.folder}_idle`;
      const sprite = new Sprite(Assets.get(textureKey));

      // 調整大小（假設原圖是 512x768，縮放到適合場景）
      const scale = 0.3; // 可根據實際圖片調整
      sprite.scale.set(scale);
      sprite.anchor.set(0.5, 1); // 底部中心為錨點

      char.sprite = sprite;
      char.addChild(sprite);

      console.log(`[Character] ${config.name} 立繪載入成功`);
    } catch (err) {
      console.warn(`[Character] ${config.name} 立繪載入失敗，使用 fallback:`, err);
      char.sprite = null;
      createFallbackCharacter(char, config);
    }
  } else {
    char.sprite = null;
    createFallbackCharacter(char, config);
  }

  // 角色名字標籤
  const nameBg = new Graphics();
  nameBg.roundRect(-35, -85, 70, 24, 8);
  nameBg.fill({ color: config.color, alpha: 0.9 });
  nameBg.stroke({ color: 0xffffff, width: 1.5 });
  char.addChild(nameBg);

  const name = new Text({
    text: config.name,
    style: { fontSize: 14, fill: 0xffffff, fontWeight: 'bold', fontFamily: 'Arial' },
  });
  name.anchor.set(0.5, 0.5);
  name.y = -73;
  char.addChild(name);

  // 狀態標籤
  const label = new Text({
    text: '休息中',
    style: { fontSize: 11, fill: 0xdfe6e9, fontWeight: '500', fontFamily: 'Arial' },
  });
  label.anchor.set(0.5, 0.5);
  label.y = 60;
  char.label = label;
  char.addChild(label);

  // 互動效果
  char.on('pointerover', () => {
    char.scale.set(1.1);
  });

  char.on('pointerout', () => {
    char.scale.set(1);
  });

  char.on('pointerdown', () => {
    showCharacterInfo(config, char);
  });

  return char;
}

function createFallbackCharacter(char, config) {
  const hairColor = getHairColor(config.hair);

  // 陰影
  const shadow = new Graphics();
  shadow.ellipse(0, 40, 30, 10);
  shadow.fill({ color: 0x000000, alpha: 0.25 });
  char.addChild(shadow);

  // 簡易人形
  const body = new Graphics();
  body.roundRect(-18, -15, 36, 55, 5);
  body.fill({ color: 0xffffff });
  body.stroke({ color: config.color, width: 2 });
  char.addChild(body);

  // 頭
  const head = new Graphics();
  head.ellipse(0, -35, 16, 18);
  head.fill({ color: 0xffe4c4 });
  char.addChild(head);

  // 頭髮
  const hair = new Graphics();
  hair.roundRect(-18, -52, 36, 20, 10);
  hair.fill({ color: hairColor });
  char.addChild(hair);
}

function updateCharacterState(sprite, newState) {
  sprite.state = newState;

  // 更換立繪
  if (sprite.sprite && assetsLoaded) {
    try {
      const textureKey = `${sprite.charData.folder}_${newState}`;
      const newTexture = Assets.get(textureKey);
      if (newTexture) {
        sprite.sprite.texture = newTexture;
      }
    } catch (err) {
      console.warn(`[Character] 無法更新立繪狀態:`, err);
    }
  }

  // 更新狀態標籤
  const stateLabels = {
    idle: '休息中',
    working: '⌨️ 打字中...',
    waiting: '📱 滑手機...',
  };
  if (sprite.label) {
    sprite.label.text = stateLabels[newState] || newState;
  }
}

function showCharacterInfo(config, sprite) {
  const info = document.getElementById('character-info');
  if (!info) return;

  const stateLabels = {
    idle: '休息中',
    working: '工作中',
    waiting: '等待中',
  };

  info.innerHTML = `
    <div style="background: rgba(0,0,0,0.8); padding: 10px; border-radius: 8px;">
      <strong style="color: #${config.color.toString(16).padStart(6, '0')};">${config.name}</strong>
      <div style="font-size: 11px; color: #dfe6e9; margin-top: 5px;">
        狀態：${stateLabels[sprite.state] || sprite.state}<br>
        ${sprite.sessionId ? `Session: ${sprite.sessionId.substring(0, 12)}...` : ''}
      </div>
    </div>
  `;

  setTimeout(() => {
    info.innerHTML = '';
  }, 3000);
}

function getHairColor(hairType) {
  const colors = {
    pink: 0xffb7c5,
    red: 0xe74c3c,
    blue: 0x3498db,
    yellow: 0xf39c12,
    purple: 0x9b59b6,
  };
  return colors[hairType] || 0x333333;
}

// ============ 角色移動 ============

const animations = new Map();

function animateTo(sprite, targetX, targetY, duration = 500) {
  if (animations.has(sprite)) {
    animations.delete(sprite);
  }

  const startX = sprite.x;
  const startY = sprite.y;
  const startTime = Date.now();

  animations.set(sprite, {
    sprite,
    startX,
    startY,
    targetX,
    targetY,
    duration,
    startTime,
  });

  if (!app.ticker.has(updateAnimations)) {
    app.ticker.add(updateAnimations);
  }
}

function updateAnimations() {
  const now = Date.now();
  const completed = [];

  animations.forEach((anim, sprite) => {
    const elapsed = now - anim.startTime;
    const progress = Math.min(elapsed / anim.duration, 1);

    // ease-out
    const eased = 1 - Math.pow(1 - progress, 3);

    sprite.x = anim.startX + (anim.targetX - anim.startX) * eased;
    sprite.y = anim.startY + (anim.targetY - anim.startY) * eased;

    if (progress >= 1) {
      completed.push(sprite);
    }
  });

  completed.forEach((sprite) => animations.delete(sprite));

  if (animations.size === 0) {
    app.ticker.remove(updateAnimations);
  }
}

function moveToDesk(sprite) {
  const charIndex = CONFIG.characters.findIndex((c) => c.id === sprite.charData.id);
  const targetX = 700 + (charIndex % 3) * 180;
  const targetY = 450 + Math.floor(charIndex / 3) * 300;
  animateTo(sprite, targetX, targetY, 600);
}

function moveToLounge(sprite) {
  const charIndex = CONFIG.characters.findIndex((c) => c.id === sprite.charData.id);
  const targetX = 120 + (charIndex % 3) * 180;
  const targetY = 450 + Math.floor(charIndex / 3) * 300;
  animateTo(sprite, targetX, targetY, 600);
}

// ============ Session 資訊面板 ============

function updateSessionInfo(sessionId, status) {
  sessionDetails.set(sessionId, {
    status,
    lastUpdate: Date.now(),
  });
  renderSessionPanel();
}

function renderSessionPanel() {
  const panel = document.getElementById('session-info');
  if (!panel) return;

  const activeCount = sessionAssignments.size;
  const workingCount = Array.from(sessionDetails.values()).filter((s) => s.status === 'working').length;
  const idleCount = activeCount - workingCount;

  panel.innerHTML = `
    <div>📊 活躍: ${activeCount}/5</div>
    <div>⌨️ 工作: ${workingCount} | 💤 閒置: ${idleCount}</div>
  `;
}

// ============ 啟動 ============

async function main() {
  console.log('🚀 Claude Office 啟動中...');

  // 先載入美術素材
  await loadAssets();

  // 初始化 PixiJS
  await initPixi();

  // 連接 WebSocket
  connectWebSocket();

  console.log('✅ Claude Office 已啟動');
}

main();
