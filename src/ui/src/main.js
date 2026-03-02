/**
 * Claude Office - Frontend Main
 *
 * 使用 PixiJS 渲染辦公室場景，透過 WebSocket 接收 session 狀態
 */

import { Application, Container, Graphics, Text, Assets } from 'pixi.js';

// ============ 配置 ============
const CONFIG = {
  // WebSocket 服務地址
  wsUrl: `ws://${window.location.hostname}:8053`,

  // 場景尺寸
  width: 1200,
  height: 700,

  // 角色配置
  characters: [
    { id: 1, name: '櫻', color: 0xffb7c5, hair: 'pink' },
    { id: 2, name: '焰', color: 0xff6b6b, hair: 'red' },
    { id: 3, name: '涼', color: 0x74b9ff, hair: 'blue' },
    { id: 4, name: '琴', color: 0xffd93d, hair: 'yellow' },
    { id: 5, name: '宵', color: 0xa29bfe, hair: 'purple' },
  ],
};

// ============ 全域狀態 ============
let app = null;
let ws = null;
let office = null;
const characterSprites = new Map();
const sessionAssignments = new Map(); // sessionId -> characterId
let nextCharacterIndex = 0;

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
      // 同步所有 session 狀態
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
    sprite.state = 'idle';
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
}

function handleSessionWorking(sessionId) {
  console.log(`[Session] 工作中: ${sessionId}`);

  const charId = sessionAssignments.get(sessionId);
  if (!charId) return;

  const sprite = characterSprites.get(charId);
  if (sprite) {
    sprite.state = 'working';
    sprite.label.text = '⌨️ 打字中...';
    moveToDesk(sprite);
    startTypingAnimation(sprite);
  }
}

function handleSessionIdle(sessionId) {
  console.log(`[Session] 閒置: ${sessionId}`);

  const charId = sessionAssignments.get(sessionId);
  if (!charId) return;

  const sprite = characterSprites.get(charId);
  if (sprite) {
    sprite.state = 'waiting';
    sprite.label.text = '📱 滑手機...';
    stopTypingAnimation(sprite);
    startIdleAnimation(sprite);
  }
}

function handleSessionClose(sessionId) {
  console.log(`[Session] 關閉: ${sessionId}`);

  const charId = sessionAssignments.get(sessionId);
  if (!charId) return;

  const sprite = characterSprites.get(charId);
  if (sprite) {
    sprite.state = 'idle';
    sprite.sessionId = null;
    stopTypingAnimation(sprite);
    stopIdleAnimation(sprite);
    moveToLounge(sprite);
    sprite.label.text = `${sprite.charData.name} (休息中)`;
  }

  sessionAssignments.delete(sessionId);
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
    // 只分配，不改變狀態（狀態由 handleSessionWorking/handleSessionIdle 處理）
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

  // ===== 辦公區（右側）=====
  const workArea = new Container();
  workArea.x = 600;
  workArea.y = 50;
  office.addChild(workArea);

  // 辦公區背景
  const workBg = new Graphics();
  workBg.rect(0, 0, 550, 600);
  workBg.fill({ color: 0x2d3436, alpha: 0.5 });
  workArea.addChild(workBg);

  // 辦公區標題
  const workTitle = new Text({
    text: '💼 工作區',
    style: { fontSize: 20, fill: 0xffffff, fontWeight: 'bold' },
  });
  workTitle.x = 20;
  workTitle.y = 10;
  workArea.addChild(workTitle);

  // 5 個辦公桌位置
  for (let i = 0; i < 5; i++) {
    const desk = createDesk(i);
    desk.x = 50 + (i % 3) * 180;
    desk.y = 60 + Math.floor(i / 3) * 280;
    workArea.addChild(desk);
  }

  // ===== 休息區（左側）=====
  const loungeArea = new Container();
  loungeArea.x = 50;
  loungeArea.y = 50;
  office.addChild(loungeArea);

  // 休息區背景
  const loungeBg = new Graphics();
  loungeBg.rect(0, 0, 500, 600);
  loungeBg.fill({ color: 0x6c5ce7, alpha: 0.3 });
  loungeArea.addChild(loungeBg);

  // 休息區標題
  const loungeTitle = new Text({
    text: '🛋️ 休息區',
    style: { fontSize: 20, fill: 0xffffff, fontWeight: 'bold' },
  });
  loungeTitle.x = 20;
  loungeTitle.y = 10;
  loungeArea.addChild(loungeTitle);

  // 5 個沙發位置
  for (let i = 0; i < 5; i++) {
    const sofa = createSofa(i);
    sofa.x = 50 + (i % 3) * 150;
    sofa.y = 80 + Math.floor(i / 3) * 280;
    loungeArea.addChild(sofa);
  }
}

function createDesk(index) {
  const desk = new Container();
  desk.name = `desk-${index}`;

  // 桌子
  const table = new Graphics();
  table.rect(0, 0, 140, 80);
  table.fill({ color: 0x636e72 });
  table.rect(0, 80, 140, 120);
  table.fill({ color: 0x2d3436 });
  desk.addChild(table);

  // 螢幕
  const monitor = new Graphics();
  monitor.rect(30, 20, 80, 50);
  monitor.fill({ color: 0x0984e3 });
  monitor.rect(35, 25, 70, 40);
  monitor.fill({ color: 0x74b9ff });
  desk.addChild(monitor);

  // 座位標籤
  const label = new Text({
    text: `座位 ${index + 1}`,
    style: { fontSize: 12, fill: 0xb2bec3 },
  });
  label.x = 40;
  label.y = 210;
  desk.addChild(label);

  return desk;
}

function createSofa(index) {
  const sofa = new Container();
  sofa.name = `sofa-${index}`;

  // 沙發主體
  const body = new Graphics();
  body.roundRect(0, 0, 120, 60, 10);
  body.fill({ color: 0xa29bfe });
  sofa.addChild(body);

  // 沙發靠背
  const back = new Graphics();
  back.roundRect(0, 0, 120, 20, { tl: 10, tr: 10, bl: 0, br: 0 });
  back.fill({ color: 0x6c5ce7 });
  sofa.addChild(back);

  // 座位標籤
  const label = new Text({
    text: `座位 ${index + 1}`,
    style: { fontSize: 12, fill: 0xdfe6e9 },
  });
  label.x = 30;
  label.y = 70;
  sofa.addChild(label);

  return sofa;
}

function createCharacters() {
  CONFIG.characters.forEach((charConfig, index) => {
    const char = createCharacter(charConfig);
    char.charData = charConfig;

    // 初始位置在休息區
    char.x = 100 + (index % 3) * 150;
    char.y = 200 + Math.floor(index / 3) * 280;

    office.addChild(char);
    characterSprites.set(charConfig.id, char);
  });
}

function createCharacter(config) {
  const char = new Container();
  char.state = 'idle';
  char.charData = config;

  // 角色身體（臨時用圓形代表）
  const body = new Graphics();
  body.circle(0, 0, 30);
  body.fill({ color: config.color });
  body.stroke({ color: 0xffffff, width: 3 });
  char.addChild(body);

  // 角色名字
  const name = new Text({
    text: config.name,
    style: { fontSize: 16, fill: 0xffffff, fontWeight: 'bold' },
  });
  name.anchor.set(0.5, 0.5);
  name.y = -50;
  char.addChild(name);

  // 狀態標籤
  const label = new Text({
    text: `${config.name} (休息中)`,
    style: { fontSize: 12, fill: 0xdfe6e9 },
  });
  label.anchor.set(0.5, 0.5);
  label.y = 50;
  char.label = label;
  char.addChild(label);

  return char;
}

// ============ 角色移動（平滑動畫） ============

const animations = new Map(); // sprite.id -> animation

function animateTo(sprite, targetX, targetY, duration = 500) {
  // 取消現有動畫
  if (animations.has(sprite)) {
    animations.delete(sprite);
  }

  const startX = sprite.x;
  const startY = sprite.y;
  const startTime = Date.now();

  const animation = {
    sprite,
    startX,
    startY,
    targetX,
    targetY,
    duration,
    startTime,
  };

  animations.set(sprite, animation);

  // 使用 PixiJS ticker 驅動動畫
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

    // 緩動函數（ease-out cubic）
    const eased = 1 - Math.pow(1 - progress, 3);

    sprite.x = anim.startX + (anim.targetX - anim.startX) * eased;
    sprite.y = anim.startY + (anim.targetY - anim.startY) * eased;

    if (progress >= 1) {
      completed.push(sprite);
    }
  });

  completed.forEach(sprite => animations.delete(sprite));

  // 如果沒有動畫了，移除 ticker
  if (animations.size === 0) {
    app.ticker.remove(updateAnimations);
  }
}

function moveToDesk(sprite) {
  const charIndex = CONFIG.characters.findIndex(c => c.id === sprite.charData.id);
  const targetX = 700 + (charIndex % 3) * 180;
  const targetY = 200 + Math.floor(charIndex / 3) * 280;
  animateTo(sprite, targetX, targetY, 600);
}

function moveToLounge(sprite) {
  const charIndex = CONFIG.characters.findIndex(c => c.id === sprite.charData.id);
  const targetX = 100 + (charIndex % 3) * 150;
  const targetY = 200 + Math.floor(charIndex / 3) * 280;
  animateTo(sprite, targetX, targetY, 600);
}

// ============ 打字動畫 ============

const typingAnimations = new Map();
const idleAnimations = new Map();

function startTypingAnimation(sprite) {
  // 停止閒置動畫
  stopIdleAnimation(sprite);

  if (typingAnimations.has(sprite)) return;

  const originalY = sprite.y;
  let time = 0;

  const animate = () => {
    if (!typingAnimations.has(sprite)) return;
    time += 0.15;
    // 輕微上下搖晃
    sprite.y = originalY + Math.sin(time * 3) * 3;
    sprite.scale.set(1 + Math.sin(time * 5) * 0.02);
    requestAnimationFrame(animate);
  };

  typingAnimations.set(sprite, true);
  animate();
}

function stopTypingAnimation(sprite) {
  if (typingAnimations.has(sprite)) {
    typingAnimations.delete(sprite);
    sprite.scale.set(1);
  }
}

function startIdleAnimation(sprite) {
  if (idleAnimations.has(sprite)) return;

  let time = 0;

  const animate = () => {
    if (!idleAnimations.has(sprite)) return;
    time += 0.05;
    // 輕微漂浮
    sprite.alpha = 0.8 + Math.sin(time) * 0.2;
    requestAnimationFrame(animate);
  };

  idleAnimations.set(sprite, true);
  animate();
}

function stopIdleAnimation(sprite) {
  if (idleAnimations.has(sprite)) {
    idleAnimations.delete(sprite);
    sprite.alpha = 1;
  }
}

// ============ 啟動 ============

async function main() {
  console.log('🚀 Claude Office 啟動中...');

  await initPixi();
  connectWebSocket();

  console.log('✅ Claude Office 已啟動');
}

main();
