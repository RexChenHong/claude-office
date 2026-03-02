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
const sessionDetails = new Map(); // sessionId -> { project, status, lastUpdate }
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
    sprite.state = 'working';
    sprite.label.text = '⌨️ 打字中...';
    moveToDesk(sprite);
    startTypingAnimation(sprite);
  }

  updateSessionInfo(sessionId, 'working');
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

  updateSessionInfo(sessionId, 'idle');
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
  const workArea = new Container();
  workArea.x = 600;
  workArea.y = 50;
  office.addChild(workArea);

  // 辦公區背景（漸層效果）
  const workBg = new Graphics();
  workBg.rect(0, 0, 550, 600);
  workBg.fill({ color: 0x2d3436, alpha: 0.6 });
  workBg.rect(0, 0, 550, 5);
  workBg.fill({ color: 0x0984e3, alpha: 0.8 }); // 頂部藍色線條
  office.addChild(workBg);

  // 辦公區標題
  const workTitle = new Text({
    text: '💼 工作區',
    style: { fontSize: 22, fill: 0xffffff, fontWeight: 'bold', fontFamily: 'Arial' },
  });
  workTitle.x = 20;
  workTitle.y = 15;
  workArea.addChild(workTitle);

  // 辦公區裝飾 - 窗戶
  const window = new Graphics();
  window.rect(420, 80, 100, 120);
  window.fill({ color: 0x74b9ff, alpha: 0.3 });
  window.stroke({ color: 0xffffff, width: 3 });
  // 窗戶格線
  window.moveTo(470, 80);
  window.lineTo(470, 200);
  window.stroke({ color: 0xffffff, width: 2 });
  window.moveTo(420, 140);
  window.lineTo(520, 140);
  window.stroke({ color: 0xffffff, width: 2 });
  workArea.addChild(window);

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

  // 休息區背景（漸層效果）
  const loungeBg = new Graphics();
  loungeBg.rect(0, 0, 500, 600);
  loungeBg.fill({ color: 0x6c5ce7, alpha: 0.35 });
  loungeBg.rect(0, 0, 500, 5);
  loungeBg.fill({ color: 0xa29bfe, alpha: 0.8 }); // 頂部紫色線條
  office.addChild(loungeBg);

  // 休息區標題
  const loungeTitle = new Text({
    text: '🛋️ 休息區',
    style: { fontSize: 22, fill: 0xffffff, fontWeight: 'bold', fontFamily: 'Arial' },
  });
  loungeTitle.x = 20;
  loungeTitle.y = 15;
  loungeArea.addChild(loungeTitle);

  // 休息區裝飾 - 植物
  const plant = new Graphics();
  // 花盆
  plant.roundRect(400, 200, 50, 60, 5);
  plant.fill({ color: 0xd35400 });
  // 植物
  plant.circle(425, 180, 30);
  plant.fill({ color: 0x27ae60 });
  plant.circle(415, 170, 20);
  plant.fill({ color: 0x2ecc71 });
  plant.circle(435, 175, 18);
  plant.fill({ color: 0x2ecc71 });
  loungeArea.addChild(plant);

  // 5 個沙發位置
  for (let i = 0; i < 5; i++) {
    const sofa = createSofa(i);
    sofa.x = 50 + (i % 3) * 150;
    sofa.y = 80 + Math.floor(i / 3) * 280;
    loungeArea.addChild(sofa);
  }

  // 全局燈光效果（頂部漸層）
  const topLight = new Graphics();
  topLight.rect(0, 0, CONFIG.width, 100);
  const alpha = 0.15;
  topLight.fill({ color: 0xffffff, alpha });
  office.addChild(topLight);
}

function createDesk(index) {
  const desk = new Container();
  desk.name = `desk-${index}`;

  // 桌子陰影
  const shadow = new Graphics();
  shadow.ellipse(70, 150, 60, 15);
  shadow.fill({ color: 0x000000, alpha: 0.2 });
  desk.addChild(shadow);

  // 桌子主體
  const table = new Graphics();
  table.roundRect(0, 60, 140, 70, 5);
  table.fill({ color: 0x636e72 });
  table.stroke({ color: 0x2d3436, width: 2 });
  desk.addChild(table);

  // 桌腿
  const legs = new Graphics();
  legs.rect(10, 130, 15, 60);
  legs.rect(115, 130, 15, 60);
  legs.fill({ color: 0x2d3436 });
  desk.addChild(legs);

  // 螢幕
  const monitor = new Graphics();
  monitor.roundRect(30, 10, 80, 55, 3);
  monitor.fill({ color: 0x2d3436 });
  monitor.stroke({ color: 0x636e72, width: 2 });
  desk.addChild(monitor);

  // 螢幕內容（漸層效果）
  const screen = new Graphics();
  screen.rect(35, 15, 70, 40);
  screen.fill({ color: 0x0984e3 });
  desk.addChild(screen);

  // 螢幕上的文字線（模擬代碼）
  for (let i = 0; i < 4; i++) {
    const line = new Graphics();
    line.rect(40, 20 + i * 9, 50 - i * 5, 4);
    line.fill({ color: 0x74b9ff, alpha: 0.8 - i * 0.1 });
    desk.addChild(line);
  }

  // 螢幕支架
  const stand = new Graphics();
  stand.rect(60, 65, 20, 10);
  stand.fill({ color: 0x2d3436 });
  desk.addChild(stand);

  // 座位標籤
  const label = new Text({
    text: `座位 ${index + 1}`,
    style: { fontSize: 12, fill: 0xb2bec3 },
  });
  label.x = 45;
  label.y = 200;
  desk.addChild(label);

  return desk;
}

function createSofa(index) {
  const sofa = new Container();
  sofa.name = `sofa-${index}`;

  // 沙發陰影
  const shadow = new Graphics();
  shadow.ellipse(60, 70, 50, 12);
  shadow.fill({ color: 0x000000, alpha: 0.2 });
  sofa.addChild(shadow);

  // 沙發主體
  const body = new Graphics();
  body.roundRect(0, 20, 120, 50, 8);
  body.fill({ color: 0xa29bfe });
  body.stroke({ color: 0x6c5ce7, width: 2 });
  sofa.addChild(body);

  // 沙發靠背
  const back = new Graphics();
  back.roundRect(0, 0, 120, 25, { tl: 8, tr: 8, bl: 0, br: 0 });
  back.fill({ color: 0x6c5ce7 });
  sofa.addChild(back);

  // 沙發扶手
  const leftArm = new Graphics();
  leftArm.roundRect(-5, 10, 15, 55, 5);
  leftArm.fill({ color: 0x6c5ce7 });
  sofa.addChild(leftArm);

  const rightArm = new Graphics();
  rightArm.roundRect(110, 10, 15, 55, 5);
  rightArm.fill({ color: 0x6c5ce7 });
  sofa.addChild(rightArm);

  // 座位標籤
  const label = new Text({
    text: `座位 ${index + 1}`,
    style: { fontSize: 12, fill: 0xdfe6e9 },
  });
  label.x = 35;
  label.y = 85;
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

  const hairColor = getHairColor(config.hair);
  const skinColor = 0xffe4c4; // 膚色

  // 角色陰影
  const shadow = new Graphics();
  shadow.ellipse(0, 40, 30, 10);
  shadow.fill({ color: 0x000000, alpha: 0.25 });
  char.addChild(shadow);

  // 身體（辦公室服裝 - 白色襯衫）
  const body = new Graphics();
  // 上身（襯衫）
  body.roundRect(-18, -15, 36, 45, 5);
  body.fill({ color: 0xffffff });
  body.stroke({ color: 0xdfe6e9, width: 1 });
  // 領口
  body.moveTo(-8, -15);
  body.lineTo(0, -5);
  body.lineTo(8, -15);
  body.stroke({ color: config.color, width: 2 });
  // 裙子/褲子
  body.roundRect(-20, 30, 40, 25, 3);
  body.fill({ color: 0x2d3436 });
  char.addChild(body);

  // 頭部
  const head = new Graphics();
  head.ellipse(0, -30, 16, 18);
  head.fill({ color: skinColor });
  head.stroke({ color: 0xddd, width: 1 });
  char.addChild(head);

  // 頭髮（原神風格 - 豐厚且有層次）
  const hair = new Graphics();
  // 劉海
  hair.roundRect(-18, -52, 36, 18, { tl: 10, tr: 10, bl: 0, br: 0 });
  hair.fill({ color: hairColor });
  // 側邊髮絲
  hair.roundRect(-20, -40, 8, 30, 4);
  hair.fill({ color: hairColor });
  hair.roundRect(12, -40, 8, 30, 4);
  hair.fill({ color: hairColor });
  // 髮飾（小蝴蝶結或髮夾）
  hair.circle(-15, -45, 4);
  hair.fill({ color: config.color });
  char.addChild(hair);

  // 眼睛（大眼睛 - 動漫風格）
  const leftEyeWhite = new Graphics();
  leftEyeWhite.ellipse(-6, -32, 5, 6);
  leftEyeWhite.fill({ color: 0xffffff });
  char.addChild(leftEyeWhite);

  const leftEyeIris = new Graphics();
  leftEyeIris.ellipse(-6, -31, 3.5, 4);
  leftEyeIris.fill({ color: getEyeColor(config.hair) });
  char.addChild(leftEyeIris);

  const leftEyePupil = new Graphics();
  leftEyePupil.circle(-6, -30, 1.5);
  leftEyePupil.fill({ color: 0x000000 });
  char.addChild(leftEyePupil);

  const rightEyeWhite = new Graphics();
  rightEyeWhite.ellipse(6, -32, 5, 6);
  rightEyeWhite.fill({ color: 0xffffff });
  char.addChild(rightEyeWhite);

  const rightEyeIris = new Graphics();
  rightEyeIris.ellipse(6, -31, 3.5, 4);
  rightEyeIris.fill({ color: getEyeColor(config.hair) });
  char.addChild(rightEyeIris);

  const rightEyePupil = new Graphics();
  rightEyePupil.circle(6, -30, 1.5);
  rightEyePupil.fill({ color: 0x000000 });
  char.addChild(rightEyePupil);

  // 眼睛高光
  const leftHighlight = new Graphics();
  leftHighlight.circle(-7, -33, 1);
  leftHighlight.fill({ color: 0xffffff });
  char.addChild(leftHighlight);

  const rightHighlight = new Graphics();
  rightHighlight.circle(5, -33, 1);
  rightHighlight.fill({ color: 0xffffff });
  char.addChild(rightHighlight);

  // 嘴巴（微笑）
  const mouth = new Graphics();
  mouth.arc(0, -24, 3, 0.2, Math.PI - 0.2);
  mouth.stroke({ color: 0xd63031, width: 1.5 });
  char.addChild(mouth);

  // 腮紅
  const leftBlush = new Graphics();
  leftBlush.ellipse(-10, -26, 4, 2);
  leftBlush.fill({ color: 0xffb7c5, alpha: 0.4 });
  char.addChild(leftBlush);

  const rightBlush = new Graphics();
  rightBlush.ellipse(10, -26, 4, 2);
  rightBlush.fill({ color: 0xffb7c5, alpha: 0.4 });
  char.addChild(rightBlush);

  // 角色名字（背景）
  const nameBg = new Graphics();
  nameBg.roundRect(-28, -75, 56, 22, 8);
  nameBg.fill({ color: config.color, alpha: 0.9 });
  nameBg.stroke({ color: 0xffffff, width: 1.5 });
  char.addChild(nameBg);

  // 角色名字
  const name = new Text({
    text: config.name,
    style: { fontSize: 13, fill: 0xffffff, fontWeight: 'bold', fontFamily: 'Arial' },
  });
  name.anchor.set(0.5, 0.5);
  name.y = -64;
  char.addChild(name);

  // 狀態標籤
  const label = new Text({
    text: `${config.name} (休息中)`,
    style: { fontSize: 11, fill: 0xdfe6e9, fontWeight: '500', fontFamily: 'Arial' },
  });
  label.anchor.set(0.5, 0.5);
  label.y = 65;
  char.label = label;
  char.addChild(label);

  return char;
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

function getEyeColor(hairType) {
  const colors = {
    pink: 0xff69b4,   // 粉色眼睛
    red: 0xe74c3c,    // 紅色眼睛
    blue: 0x3498db,   // 藍色眼睛
    yellow: 0xf39c12, // 金色眼睛
    purple: 0x9b59b6, // 紫色眼睛
  };
  return colors[hairType] || 0x2d3436;
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

    // 更自然的緩動函數（ease-out-back）
    const c1 = 1.70158;
    const c3 = c1 + 1;
    const eased = 1 + c3 * Math.pow(progress - 1, 3) + c1 * Math.pow(progress - 1, 2);

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
    time += 0.12;
    // 更自然的打字動畫
    sprite.y = originalY + Math.sin(time * 2.5) * 2;
    sprite.scale.set(1 + Math.sin(time * 4) * 0.015);
    sprite.rotation = Math.sin(time * 3) * 0.02; // 輕微左右搖晃
    requestAnimationFrame(animate);
  };

  typingAnimations.set(sprite, { originalY });
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
    time += 0.03;
    // 溫和的呼吸動畫
    const breathe = Math.sin(time) * 0.03;
    sprite.scale.set(1 + breathe);
    sprite.alpha = 0.85 + Math.sin(time * 0.8) * 0.15;
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
  const workingCount = Array.from(sessionDetails.values()).filter(s => s.status === 'working').length;
  const idleCount = activeCount - workingCount;

  panel.innerHTML = `
    <div>📊 活躍: ${activeCount}/5</div>
    <div>⌨️ 工作: ${workingCount} | 💤 閒置: ${idleCount}</div>
  `;
}

// ============ 啟動 ============

async function main() {
  console.log('🚀 Claude Office 啟動中...');

  await initPixi();
  connectWebSocket();

  console.log('✅ Claude Office 已啟動');
}

main();
