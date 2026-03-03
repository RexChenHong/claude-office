/**
 * Claude Office - 遊戲視覺風格優化版
 * 使用日系原神風格的色彩和設計語言
 */

import { Application, Container, Graphics, Text, Assets, Sprite, AnimatedSprite } from 'pixi.js';

// ============ 配置 ============
const CONFIG = {
  width: 1200,
  height: 700,
  
  // 日系原神風格配色
  colors: {
    // 背景
    sky: 0x87CEEB,        // 天空藍
    cloud: 0xFFFFFF,       // 白雲
    wall: 0xFFF8DC,        // 米色牆壁
    floor: 0xD2691E,       // 木地板
    
    // 家具
    sofa: 0x9370DB,        // 紫色沙發
    desk: 0x8B4513,        // 木桌
    plant: 0x228B22,       // 綠色植物
    
    // 角色
    sakura: {
      hair: 0xFFB6C1,      // 粉色頭髮
      eye: 0x4169E1,       // 藍色眼睛
      skin: 0xFFE4C4,      // 膚色
      outfit: 0xFFFFFF,    // 白色校服
      accent: 0x4169E1     // 藍色蝴蝶結
    }
  }
};

// ============ 全域狀態 ============
let app = null;
const gameObjects = new Map();

// ============ 初始化 ============

async function init() {
  console.log('[Game] 初始化遊戲...');
  
  // 創建 PixiJS 應用
  app = new Application();
  await app.init({
    width: CONFIG.width,
    height: CONFIG.height,
    backgroundColor: CONFIG.colors.sky,
    antialias: true,
    resolution: window.devicePixelRatio || 1,
    autoDensity: true,
  });
  
  document.getElementById('game-container').appendChild(app.canvas);
  
  // 創建遊戲場景
  createGenshinStyleOffice();
  
  // 啟動遊戲循環
  app.ticker.add((ticker) => {
    update(ticker.deltaTime);
  });
  
  console.log('[Game] 遊戲啟動完成！');
}

function createGenshinStyleOffice() {
  console.log('[Game] 創建日系原神風格辦公室...');
  
  const scene = new Container();
  app.stage.addChild(scene);
  
  // 1. 背景層（天空 + 雲朵）
  createSkyBackground(scene);
  
  // 2. 建築層（牆壁 + 窗戶）
  createBuilding(scene);
  
  // 3. 地面層（木地板）
  createFloor(scene);
  
  // 4. 家具層（沙發、桌子、植物）
  createFurniture(scene);
  
  // 5. 角色層（使用簡化的日系風格）
  createCharacters(scene);
  
  // 6. UI 層（標籤、提示）
  createUI(scene);
}

function createSkyBackground(scene) {
  // 漸層天空
  const sky = new Graphics();
  
  // 天空漸層（從上到下）
  for (let y = 0; y < 300; y++) {
    const ratio = y / 300;
    const r = Math.floor(135 + (200 - 135) * ratio);
    const g = Math.floor(206 + (220 - 206) * ratio);
    const b = Math.floor(235 + (240 - 235) * ratio);
    const color = (r << 16) + (g << 8) + b;
    
    sky.rect(0, y, CONFIG.width, 1);
    sky.fill({ color });
  }
  
  scene.addChild(sky);
  
  // 動態雲朵
  for (let i = 0; i < 5; i++) {
    const cloud = createCloud();
    cloud.x = Math.random() * CONFIG.width;
    cloud.y = 50 + Math.random() * 150;
    cloud.speed = 0.2 + Math.random() * 0.3;
    scene.addChild(cloud);
    
    gameObjects.set(`cloud_${i}`, cloud);
  }
}

function createCloud() {
  const cloud = new Graphics();
  
  // 圓潤的雲朵形狀
  cloud.circle(0, 0, 30);
  cloud.fill({ color: CONFIG.colors.cloud, alpha: 0.9 });
  cloud.circle(25, -5, 25);
  cloud.fill({ color: CONFIG.colors.cloud, alpha: 0.9 });
  cloud.circle(50, 0, 30);
  cloud.fill({ color: CONFIG.colors.cloud, alpha: 0.9 });
  cloud.circle(15, 10, 20);
  cloud.fill({ color: CONFIG.colors.cloud, alpha: 0.8 });
  
  return cloud;
}

function createBuilding(scene) {
  // 牆壁
  const wall = new Graphics();
  wall.rect(0, 300, CONFIG.width, 400);
  wall.fill({ color: CONFIG.colors.wall });
  scene.addChild(wall);
  
  // 窗戶（左側）
  for (let i = 0; i < 3; i++) {
    const windowFrame = createWindow();
    windowFrame.x = 100 + i * 120;
    windowFrame.y = 320;
    scene.addChild(windowFrame);
  }
  
  // 窗戶（右側）
  for (let i = 0; i < 3; i++) {
    const windowFrame = createWindow();
    windowFrame.x = 700 + i * 120;
    windowFrame.y = 320;
    scene.addChild(windowFrame);
  }
}

function createWindow() {
  const window = new Graphics();
  
  // 窗框
  window.roundRect(0, 0, 80, 100, 10);
  window.fill({ color: 0x87CEEB }); // 窗外藍天
  window.stroke({ color: 0x8B4513, width: 4 }); // 木框
  
  // 窗格
  window.rect(38, 0, 4, 100);
  window.fill({ color: 0x8B4513 });
  window.rect(0, 48, 80, 4);
  window.fill({ color: 0x8B4513 });
  
  return window;
}

function createFloor(scene) {
  // 木地板
  const floor = new Graphics();
  floor.rect(0, 500, CONFIG.width, 200);
  floor.fill({ color: CONFIG.colors.floor });
  
  // 地板紋理
  for (let x = 0; x < CONFIG.width; x += 80) {
    floor.rect(x, 500, 2, 200);
    floor.fill({ color: 0xA0522D });
  }
  
  scene.addChild(floor);
}

function createFurniture(scene) {
  // 休息區標籤
  const loungeLabel = createLabel('休息區', 250, 520);
  scene.addChild(loungeLabel);
  
  // 沙發（休息區）
  for (let i = 0; i < 3; i++) {
    const sofa = createSofa();
    sofa.x = 100 + i * 150;
    sofa.y = 600;
    scene.addChild(sofa);
  }
  
  // 工作區標籤
  const workLabel = createLabel('工作區', 850, 520);
  scene.addChild(workLabel);
  
  // 辦公桌（工作區）
  for (let i = 0; i < 3; i++) {
    const desk = createDesk();
    desk.x = 650 + i * 150;
    desk.y = 600;
    scene.addChild(desk);
  }
  
  // 裝飾植物
  for (let i = 0; i < 4; i++) {
    const plant = createPlant();
    plant.x = 50 + i * 350;
    plant.y = 550;
    scene.addChild(plant);
    
    // 植物搖曳動畫
    gameObjects.set(`plant_${i}`, plant);
  }
}

function createSofa() {
  const sofa = new Graphics();
  
  // 沙發主體
  sofa.roundRect(-50, -30, 100, 60, 15);
  sofa.fill({ color: CONFIG.colors.sofa });
  
  // 沙發靠背
  sofa.roundRect(-50, -45, 100, 20, 10);
  sofa.fill({ color: 0x7B68EE }); // 稍深的紫色
  
  // 沙發扶手
  sofa.roundRect(-55, -35, 15, 50, 5);
  sofa.fill({ color: 0x8A2BE2 });
  sofa.roundRect(40, -35, 15, 50, 5);
  sofa.fill({ color: 0x8A2BE2 });
  
  return sofa;
}

function createDesk() {
  const desk = new Graphics();
  
  // 桌面
  desk.roundRect(-40, -20, 80, 40, 5);
  desk.fill({ color: CONFIG.colors.desk });
  
  // 桌腿
  desk.rect(-35, 20, 8, 40);
  desk.fill({ color: 0x6B4423 });
  desk.rect(27, 20, 8, 40);
  desk.fill({ color: 0x6B4423 });
  
  // 電腦螢幕
  desk.rect(-25, -60, 50, 35);
  desk.fill({ color: 0x000000 });
  desk.rect(-23, -58, 46, 31);
  desk.fill({ color: 0x1E90FF }); // 藍色螢幕光
  
  // 螢幕支架
  desk.rect(-5, -25, 10, 10);
  desk.fill({ color: 0x696969 });
  
  // 鍵盤
  desk.rect(-20, -15, 40, 8);
  desk.fill({ color: 0x2F4F4F });
  
  return desk;
}

function createPlant() {
  const plant = new Graphics();
  
  // 花盆
  plant.roundRect(-15, 20, 30, 25, 5);
  plant.fill({ color: 0xD2691E });
  
  // 植物葉片（動畫用）
  plant.moveTo(0, 20);
  plant.lineTo(-20, -20);
  plant.lineTo(0, -10);
  plant.lineTo(20, -25);
  plant.lineTo(0, 20);
  plant.fill({ color: CONFIG.colors.plant });
  
  return plant;
}

function createLabel(text, x, y) {
  const label = new Text({
    text,
    style: {
      fontSize: 20,
      fill: 0xFFFFFF,
      fontWeight: 'bold',
      stroke: { color: 0x000000, width: 3 },
      dropShadow: {
        color: 0x000000,
        blur: 2,
        distance: 2
      }
    }
  });
  
  label.anchor.set(0.5, 0.5);
  label.x = x;
  label.y = y;
  
  return label;
}

function createCharacters(scene) {
  // 創建簡化的日系風格角色
  const sakura = createGenshinStyleCharacter('sakura', 200, 580);
  scene.addChild(sakura.container);
  gameObjects.set('sakura', sakura);
  
  const homura = createGenshinStyleCharacter('homura', 300, 580);
  scene.addChild(homura.container);
  gameObjects.set('homura', homura);
  
  const ryo = createGenshinStyleCharacter('ryo', 700, 580);
  scene.addChild(ryo.container);
  gameObjects.set('ryo', ryo);
}

function createGenshinStyleCharacter(characterId, x, y) {
  const container = new Container();
  const graphics = new Graphics();
  
  // 角色配置
  const charConfigs = {
    sakura: {
      name: '櫻',
      hairColor: 0xFFB6C1, // 粉色
      eyeColor: 0x4169E1,  // 藍色
      outfitColor: 0xFFFFFF // 白色
    },
    homura: {
      name: '焰',
      hairColor: 0xDC143C, // 紅色
      eyeColor: 0xDC143C,  // 紅色
      outfitColor: 0x2F4F4F // 深灰
    },
    ryo: {
      name: '涼',
      hairColor: 0x4169E1, // 藍色
      eyeColor: 0x4169E1,  // 藍色
      outfitColor: 0x4169E1 // 藍色
    }
  };
  
  const config = charConfigs[characterId];
  
  // 繪製日系風格角色
  drawGenshinCharacter(graphics, config);
  
  container.addChild(graphics);
  container.x = x;
  container.y = y;
  
  // 名字標籤
  const nameTag = createLabel(config.name, 0, -120);
  container.addChild(nameTag);
  
  return {
    container,
    graphics,
    config,
    animationTime: Math.random() * 100 // 隨機起始時間
  };
}

function drawGenshinCharacter(g, config) {
  g.clear();
  
  // 動畫參數
  const breathe = Math.sin(Date.now() * 0.002) * 2;
  const blink = Math.sin(Date.now() * 0.01) > 0.95 ? 0.3 : 1;
  
  // 頭髮（後層）
  g.circle(0, -95 + breathe, 25);
  g.fill({ color: config.hairColor });
  
  // 雙馬尾
  g.ellipse(-30, -70, 12, 25);
  g.fill({ color: config.hairColor });
  g.ellipse(30, -70, 12, 25);
  g.fill({ color: config.hairColor });
  
  // 臉部
  g.circle(0, -85, 20);
  g.fill({ color: 0xFFE4C4 }); // 膚色
  
  // 頭髮（前層）
  g.arc(0, -85, 20, Math.PI, 0);
  g.fill({ color: config.hairColor });
  
  // 眼睛（日系大眼睛）
  g.circle(-7, -85, 4 * blink);
  g.fill({ color: config.eyeColor });
  g.circle(7, -85, 4 * blink);
  g.fill({ color: config.eyeColor });
  
  // 眼睛高光
  g.circle(-6, -86, 1.5);
  g.fill({ color: 0xFFFFFF });
  g.circle(8, -86, 1.5);
  g.fill({ color: 0xFFFFFF });
  
  // 微笑
  g.arc(0, -80, 5, 0, Math.PI);
  g.stroke({ color: 0xFF9999, width: 1 });
  
  // 身體
  g.roundRect(-15, -60, 30, 50, 5);
  g.fill({ color: config.outfitColor });
  
  // 蝴蝶結/領帶
  g.circle(0, -55, 5);
  g.fill({ color: config.eyeColor });
  
  // 手臂
  g.roundRect(-25, -50, 10, 30, 3);
  g.fill({ color: 0xFFE4C4 });
  g.roundRect(15, -50, 10, 30, 3);
  g.fill({ color: 0xFFE4C4 });
  
  // 裙子/褲子
  g.roundRect(-15, -10, 30, 35, 5);
  g.fill({ color: 0x4169E1 });
  
  // 腿
  g.roundRect(-12, 25, 10, 30, 3);
  g.fill({ color: 0xFFE4C4 });
  g.roundRect(2, 25, 10, 30, 3);
  g.fill({ color: 0xFFE4C4 });
  
  // 鞋子
  g.roundRect(-14, 55, 14, 8, 2);
  g.fill({ color: 0x8B4513 });
  g.roundRect(0, 55, 14, 8, 2);
  g.fill({ color: 0x8B4513 });
}

function createUI(scene) {
  // 遊戲標題
  const title = new Text({
    text: '🏢 Claude Office',
    style: {
      fontSize: 28,
      fill: 0xFFFFFF,
      fontWeight: 'bold',
      stroke: { color: 0x4169E1, width: 4 },
      dropShadow: {
        color: 0x000000,
        blur: 3,
        distance: 3
      }
    }
  });
  
  title.x = CONFIG.width / 2;
  title.y = 30;
  title.anchor.set(0.5, 0);
  scene.addChild(title);
  
  // 提示文字
  const hint = new Text({
    text: '🎮 日系原神風格辦公室 - Demo',
    style: {
      fontSize: 14,
      fill: 0xFFFFFF,
      stroke: { color: 0x000000, width: 2 }
    }
  });
  
  hint.x = CONFIG.width / 2;
  hint.y = CONFIG.height - 20;
  hint.anchor.set(0.5, 1);
  scene.addChild(hint);
}

function update(deltaTime) {
  const time = Date.now();
  
  // 更新雲朵動畫
  for (let i = 0; i < 5; i++) {
    const cloud = gameObjects.get(`cloud_${i}`);
    if (cloud) {
      cloud.x += cloud.speed * deltaTime;
      if (cloud.x > CONFIG.width + 100) {
        cloud.x = -100;
      }
    }
  }
  
  // 更新植物搖曳
  for (let i = 0; i < 4; i++) {
    const plant = gameObjects.get(`plant_${i}`);
    if (plant) {
      plant.rotation = Math.sin(time * 0.001 + i) * 0.05;
    }
  }
  
  // 更新角色動畫
  ['sakura', 'homura', 'ryo'].forEach(id => {
    const char = gameObjects.get(id);
    if (char) {
      char.animationTime += deltaTime;
      drawGenshinCharacter(char.graphics, char.config);
    }
  });
}

// ============ 啟動遊戲 ============
init().catch(err => {
  console.error('[Game] 初始化失敗:', err);
  document.getElementById('error-message').textContent = `錯誤: ${err.message}`;
});
