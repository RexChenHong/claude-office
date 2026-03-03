/**
 * Claude Office - Frontend Main (Sprite Animation Version)
 *
 * 使用 PixiJS + Sprite Sheet 實現遊戲級角色動畫
 */

import { Application, Container, Graphics, Text, Assets, AnimatedSprite, Spritesheet } from 'pixi.js';
import { CharacterAnimator, CharacterStateMachine } from './CharacterAnimator.js';

// ============ 配置 ============
const CONFIG = {
  wsUrl: `ws://${window.location.hostname}:8053`,
  width: 1200,
  height: 700,

  characters: [
    { id: 'sakura', name: '櫻', color: 0xffb7c5 },
    { id: 'homura', name: '焰', color: 0xff6b6b },
    { id: 'ryo', name: '涼', color: 0x74b9ff },
    { id: 'koto', name: '琴', color: 0xffd93d },
    { id: 'yoi', name: '宵', color: 0xa29bfe },
  ],

  // 場景配置
  loungeArea: { x: 50, y: 50, width: 500, height: 600 },
  workArea: { x: 600, y: 50, width: 550, height: 600 },

  // 角色初始位置（休息區）
  loungePositions: [
    { x: 150, y: 500 },
    { x: 300, y: 500 },
    { x: 450, y: 500 },
    { x: 225, y: 350 },
    { x: 375, y: 350 },
  ],

  // 辦公桌位置
  deskPositions: [
    { x: 700, y: 500 },
    { x: 850, y: 500 },
    { x: 1000, y: 500 },
    { x: 775, y: 350 },
    { x: 925, y: 350 },
  ],
};

// ============ 全域狀態 ============
let app = null;
let ws = null;
let office = null;
const characterAnimators = new Map();
const characterStateMachines = new Map();
const sessionAssignments = new Map();
const sessionDetails = new Map();
let nextCharacterIndex = 0;

// ============ 資源載入 ============

async function loadAssets() {
  console.log('[Assets] 開始載入...');

  // 載入背景
  Assets.add({ alias: 'bgWork', src: '/assets/backgrounds/work_area.png' });
  Assets.add({ alias: 'bgLounge', src: '/assets/backgrounds/lounge_area.png' });

  await Assets.load(['bgWork', 'bgLounge']);
  console.log('[Assets] 背景載入完成');

  // 載入第一個角色的 sprite sheets（測試用）
  await loadCharacterSprites('sakura');
}

async function loadCharacterSprites(characterId) {
  const animator = new CharacterAnimator();
  await animator.loadCharacterSprites(characterId);
  characterAnimators.set(characterId, animator);
  console.log(`[Assets] ${characterId} sprite sheets 載入完成`);
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
  }
}

// ============ Session 狀態處理 ============

function handleSync(sessions) {
  characterStateMachines.forEach((sm) => {
    sm.setState('idle');
    moveToLounge(sm);
  });

  sessionAssignments.clear();
  nextCharacterIndex = 0;

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
  const charConfig = assignCharacterToSession(sessionId, project);
  if (!charConfig) return;

  const sm = characterStateMachines.get(charConfig.id);
  if (!sm) return;

  // 走到辦公桌
  const deskPos = getDeskPosition(charConfig.id);
  sm.moveTo(deskPos.x, deskPos.y, () => {
    sm.setState('waiting'); // 坐下後等待
  });

  sessionDetails.set(sessionId, { project, status: 'open', lastUpdate: Date.now() });
  renderSessionPanel();
}

function handleSessionWorking(sessionId) {
  const charId = sessionAssignments.get(sessionId);
  if (!charId) return;

  const sm = characterStateMachines.get(charId);
  if (sm) {
    sm.setState('working');
  }

  sessionDetails.set(sessionId, { status: 'working', lastUpdate: Date.now() });
  renderSessionPanel();
}

function handleSessionIdle(sessionId) {
  const charId = sessionAssignments.get(sessionId);
  if (!charId) return;

  const sm = characterStateMachines.get(charId);
  if (sm) {
    sm.setState('waiting');
  }

  sessionDetails.set(sessionId, { status: 'idle', lastUpdate: Date.now() });
  renderSessionPanel();
}

function handleSessionClose(sessionId) {
  const charId = sessionAssignments.get(sessionId);
  if (!charId) return;

  const sm = characterStateMachines.get(charId);
  if (sm) {
    // 走回休息區
    const loungePos = getLoungePosition(charId);
    sm.moveTo(loungePos.x, loungePos.y, () => {
      sm.setState('idle');
    });
  }

  sessionAssignments.delete(sessionId);
  sessionDetails.delete(sessionId);
  renderSessionPanel();
}

function assignCharacterToSession(sessionId, project) {
  if (sessionAssignments.has(sessionId)) {
    return CONFIG.characters.find(c => c.id === sessionAssignments.get(sessionId));
  }

  const charConfig = CONFIG.characters[nextCharacterIndex % CONFIG.characters.length];
  nextCharacterIndex++;

  sessionAssignments.set(sessionId, charConfig.id);
  console.log(`[Assign] Session ${sessionId} → 角色 ${charConfig.name}`);

  return charConfig;
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

  createOffice();
  await createCharacters();

  console.log('[Pixi] 初始化完成');
}

function createOffice() {
  office = new Container();
  app.stage.addChild(office);

  // 背景
  const bgWork = new PIXI.Sprite(Assets.get('bgWork'));
  bgWork.x = CONFIG.workArea.x;
  bgWork.y = CONFIG.workArea.y;
  bgWork.width = CONFIG.workArea.width;
  bgWork.height = CONFIG.workArea.height;
  office.addChild(bgWork);

  const bgLounge = new PIXI.Sprite(Assets.get('bgLounge'));
  bgLounge.x = CONFIG.loungeArea.x;
  bgLounge.y = CONFIG.loungeArea.y;
  bgLounge.width = CONFIG.loungeArea.width;
  bgLounge.height = CONFIG.loungeArea.height;
  office.addChild(bgLounge);

  // 區域標籤
  const workTitle = new Text({
    text: '💼 工作區',
    style: { fontSize: 20, fill: 0xffffff, fontWeight: 'bold' },
  });
  workTitle.x = 620;
  workTitle.y = 20;
  office.addChild(workTitle);

  const loungeTitle = new Text({
    text: '🛋️ 休息區',
    style: { fontSize: 20, fill: 0xffffff, fontWeight: 'bold' },
  });
  loungeTitle.x = 70;
  loungeTitle.y = 20;
  office.addChild(loungeTitle);
}

async function createCharacters() {
  // 目前只創建一個測試角色
  const charConfig = CONFIG.characters[0]; // sakura

  const animator = characterAnimators.get(charConfig.id);
  if (!animator) {
    console.warn(`[Character] ${charConfig.name} animator 未載入`);
    return;
  }

  const charContainer = new Container();
  office.addChild(charContainer);

  const sprite = animator.createAnimatedSprite(charConfig.id, 'idle');
  if (sprite) {
    sprite.scale.set(0.5); // 調整大小
    charContainer.addChild(sprite);
  }

  // 名字標籤
  const nameBg = new Graphics();
  nameBg.roundRect(-30, -120, 60, 22, 8);
  nameBg.fill({ color: charConfig.color, alpha: 0.9 });
  charContainer.addChild(nameBg);

  const name = new Text({
    text: charConfig.name,
    style: { fontSize: 12, fill: 0xffffff, fontWeight: 'bold' },
  });
  name.anchor.set(0.5, 0.5);
  name.y = -109;
  charContainer.addChild(name);

  // 狀態機
  const sm = new CharacterStateMachine(animator, charConfig.id, charContainer);
  const pos = getLoungePosition(0);
  sm.setPosition(pos.x, pos.y);
  characterStateMachines.set(charConfig.id, sm);

  console.log(`[Character] ${charConfig.name} 創建完成`);
}

function getLoungePosition(index) {
  return CONFIG.loungePositions[index % CONFIG.loungePositions.length];
}

function getDeskPosition(index) {
  return CONFIG.deskPositions[index % CONFIG.deskPositions.length];
}

function moveToLounge(stateMachine) {
  const index = Array.from(characterStateMachines.values()).indexOf(stateMachine);
  const pos = getLoungePosition(index);
  stateMachine.moveTo(pos.x, pos.y, () => {
    stateMachine.setState('idle');
  });
}

// ============ Session 資訊面板 ============

function renderSessionPanel() {
  const panel = document.getElementById('session-info');
  if (!panel) return;

  const activeCount = sessionAssignments.size;
  const workingCount = Array.from(sessionDetails.values()).filter(s => s.status === 'working').length;

  panel.innerHTML = `
    <div>📊 活躍: ${activeCount}/5</div>
    <div>⌨️ 工作: ${workingCount} | 💤 閒置: ${activeCount - workingCount}</div>
  `;
}

// ============ 啟動 ============

async function main() {
  console.log('🚀 Claude Office (Sprite Animation) 啟動中...');

  await loadAssets();
  await initPixi();
  connectWebSocket();

  console.log('✅ Claude Office 已啟動');
}

main();
