/**
 * Claude Office - 遊戲主程式（簡化版）
 * 展示遊戲概念：一致的角色 + 動態場景
 */

import { Application, Container, Graphics, Text } from 'pixi.js';
import { GameCharacter, CHARACTER_CONFIGS } from './GameCharacter.js';

// ============ 配置 ============
const CONFIG = {
  width: 1200,
  height: 700,
  characters: Object.values(CHARACTER_CONFIGS),
  
  // 場景配置
  loungeArea: { x: 50, y: 50, width: 500, height: 600 },
  workArea: { x: 600, y: 50, width: 550, height: 600 },
  
  // 角色位置
  loungePositions: [
    { x: 150, y: 600 },
    { x: 300, y: 600 },
    { x: 450, y: 600 },
  ],
  
  deskPositions: [
    { x: 700, y: 600 },
    { x: 850, y: 600 },
    { x: 1000, y: 600 },
  ],
};

// ============ 全域狀態 ============
let app = null;
const characters = new Map();

// ============ 初始化 ============

async function init() {
  console.log('[Game] 初始化遊戲...');
  
  // 創建 PixiJS 應用
  app = new Application();
  await app.init({
    width: CONFIG.width,
    height: CONFIG.height,
    backgroundColor: 0x2c3e50,
    antialias: true,
  });
  
  // PixiJS 7+ 使用 app.canvas
  const canvas = app.canvas;
  document.getElementById('game-container').appendChild(canvas);
  
  console.log('[Game] Canvas 創建完成');
  
  // 創建場景
  createScene();
  
  // 創建角色
  createCharacters();
  
  // 啟動遊戲循環
  app.ticker.add((ticker) => {
    update(ticker.deltaTime);
  });
  
  console.log('[Game] 遊戲啟動完成！');
}

function createScene() {
  // 場景容器
  const scene = new Container();
  app.stage.addChild(scene);
  
  // 繪製地板
  const floor = new Graphics();
  floor.rect(0, 500, CONFIG.width, 200);
  floor.fill({ color: 0x8B4513 }); // 木地板顏色
  scene.addChild(floor);
  
  // 繪製牆壁
  const wall = new Graphics();
  wall.rect(0, 0, CONFIG.width, 500);
  wall.fill({ color: 0xE8DCC8 }); // 米色牆壁
  scene.addChild(wall);
  
  // 休息區標籤
  const loungeLabel = new Text({
    text: '休息區',
    style: { fontSize: 24, fill: 0xFFFFFF, fontWeight: 'bold' }
  });
  loungeLabel.x = 250;
  loungeLabel.y = 50;
  scene.addChild(loungeLabel);
  
  // 工作區標籤
  const workLabel = new Text({
    text: '工作區',
    style: { fontSize: 24, fill: 0xFFFFFF, fontWeight: 'bold' }
  });
  workLabel.x = 850;
  workLabel.y = 50;
  scene.addChild(workLabel);
  
  // 繪製沙發（休息區）
  for (let i = 0; i < 3; i++) {
    const sofa = new Graphics();
    sofa.roundRect(CONFIG.loungePositions[i].x - 50, CONFIG.loungePositions[i].y - 30, 100, 60, 10);
    sofa.fill({ color: 0x6B8E23 }); // 綠色沙發
    scene.addChild(sofa);
  }
  
  // 繪製辦公桌（工作區）
  for (let i = 0; i < 3; i++) {
    const desk = new Graphics();
    desk.roundRect(CONFIG.deskPositions[i].x - 40, CONFIG.deskPositions[i].y - 60, 80, 40, 5);
    desk.fill({ color: 0x8B4513 }); // 木頭桌子
    scene.addChild(desk);
    
    // 電腦螢幕
    const monitor = new Graphics();
    monitor.rect(CONFIG.deskPositions[i].x - 20, CONFIG.deskPositions[i].y - 100, 40, 30);
    monitor.fill({ color: 0x000000 });
    scene.addChild(monitor);
  }
  
  // 添加動態元素：雲朵
  createClouds(scene);
}

function createClouds(scene) {
  // 雲朵 1
  const cloud1 = new Graphics();
  cloud1.circle(0, 0, 30);
  cloud1.fill({ color: 0xFFFFFF, alpha: 0.8 });
  cloud1.circle(25, 0, 25);
  cloud1.fill({ color: 0xFFFFFF, alpha: 0.8 });
  cloud1.circle(50, 0, 30);
  cloud1.fill({ color: 0xFFFFFF, alpha: 0.8 });
  cloud1.x = 100;
  cloud1.y = 100;
  scene.addChild(cloud1);
  
  // 保存到 scene 上
  scene.cloud1 = cloud1;
  scene.cloud1Speed = 0.5;
  
  // 雲朵 2
  const cloud2 = new Graphics();
  cloud2.circle(0, 0, 20);
  cloud2.fill({ color: 0xFFFFFF, alpha: 0.6 });
  cloud2.circle(20, 0, 25);
  cloud2.fill({ color: 0xFFFFFF, alpha: 0.6 });
  cloud2.x = 500;
  cloud2.y = 150;
  scene.addChild(cloud2);
  
  scene.cloud2 = cloud2;
  scene.cloud2Speed = 0.3;
  
  // 保存 scene 引用
  scene.clouds = { cloud1, cloud2 };
}

function createCharacters() {
  console.log('[Game] 創建角色...');
  
  // 創建 3 個角色（測試用）
  const testCharacters = ['sakura', 'homura', 'ryo'];
  
  testCharacters.forEach((charId, index) => {
    const config = CHARACTER_CONFIGS[charId];
    const character = new GameCharacter(config);
    
    // 設置初始位置（休息區）
    const pos = CONFIG.loungePositions[index];
    character.setPosition(pos.x, pos.y);
    
    // 添加到場景
    app.stage.addChild(character.container);
    
    // 保存到 Map
    characters.set(charId, character);
    
    console.log(`[Game] 創建角色: ${config.name}`);
  });
}

function update(deltaTime) {
  // 更新所有角色動畫
  characters.forEach(character => {
    character.update(deltaTime);
  });
  
  // 更新雲朵動畫
  if (app.stage.clouds) {
    const { cloud1, cloud2 } = app.stage.clouds;
    
    if (cloud1) {
      cloud1.x += app.stage.cloud1Speed * deltaTime;
      if (cloud1.x > CONFIG.width + 100) {
        cloud1.x = -100;
      }
    }
    
    if (cloud2) {
      cloud2.x += app.stage.cloud2Speed * deltaTime;
      if (cloud2.x > CONFIG.width + 100) {
        cloud2.x = -100;
      }
    }
  }
}

// ============ 啟動遊戲 ============
init().catch(err => {
  console.error('[Game] 初始化失敗:', err);
  document.getElementById('error-message').textContent = `錯誤: ${err.message}`;
});
