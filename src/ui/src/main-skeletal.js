/**
 * Claude Office - 2D 骨骼動畫系統（遊戲級）
 * 即時渲染，不是預渲染圖片輪播
 */

import { Application, Container, Graphics, Text } from 'pixi.js';

// ============ 骨骼動畫系統 ============

class Bone {
  constructor(length, angle = 0) {
    this.length = length;
    this.angle = angle; // 弧度
    this.children = [];
    this.x = 0;
    this.y = 0;
    this.globalAngle = 0;
  }

  addChild(bone) {
    this.children.push(bone);
    return bone;
  }

  update(parentX = 0, parentY = 0, parentAngle = 0) {
    this.globalAngle = parentAngle + this.angle;
    this.x = parentX + Math.cos(this.globalAngle) * this.length;
    this.y = parentY + Math.sin(this.globalAngle) * this.length;

    this.children.forEach(child => {
      child.update(this.x, this.y, this.globalAngle);
    });
  }

  setAngle(angle) {
    this.angle = angle;
  }
}

// ============ 角色類（日系原神風格） ============

class GenshinCharacter {
  constructor(config) {
    this.config = config;
    this.container = new Container();

    // 創建骨骼結構
    this.skeleton = this.createSkeleton();

    // 動畫參數
    this.animationTime = 0;
    this.state = 'idle';

    // 繪製角色
    this.graphics = new Graphics();
    this.container.addChild(this.graphics);
    this.draw();
  }

  createSkeleton() {
    // 根骨骼（臀部）
    const root = new Bone(0, 0);

    // 軀幹
    const torso = new Bone(40, -Math.PI / 2); // 向上
    root.addChild(torso);

    // 頭部
    const head = new Bone(25, 0);
    torso.addChild(head);

    // 左臂
    const leftUpperArm = new Bone(20, -Math.PI / 4);
    const leftLowerArm = new Bone(18, -Math.PI / 6);
    leftUpperArm.addChild(leftLowerArm);
    torso.addChild(leftUpperArm);

    // 右臂
    const rightUpperArm = new Bone(20, Math.PI / 4);
    const rightLowerArm = new Bone(18, Math.PI / 6);
    rightUpperArm.addChild(rightLowerArm);
    torso.addChild(rightUpperArm);

    // 左腿
    const leftUpperLeg = new Bone(25, Math.PI / 2 + 0.1);
    const leftLowerLeg = new Bone(22, 0.1);
    leftUpperLeg.addChild(leftLowerLeg);
    root.addChild(leftUpperLeg);

    // 右腿
    const rightUpperLeg = new Bone(25, Math.PI / 2 - 0.1);
    const rightLowerLeg = new Bone(22, -0.1);
    rightUpperLeg.addChild(rightLowerLeg);
    root.addChild(rightUpperLeg);

    return {
      root,
      torso,
      head,
      leftUpperArm,
      leftLowerArm,
      rightUpperArm,
      rightLowerArm,
      leftUpperLeg,
      leftLowerLeg,
      rightUpperLeg,
      rightLowerLeg
    };
  }

  update(deltaTime) {
    this.animationTime += deltaTime * 0.05;

    // 根據狀態更新骨骼角度
    switch (this.state) {
      case 'idle':
        this.animateIdle();
        break;
      case 'working':
        this.animateWorking();
        break;
      case 'walking':
        this.animateWalking();
        break;
    }

    // 更新骨骼
    this.skeleton.root.update(this.container.x, this.container.y, 0);

    // 重新繪製
    this.draw();
  }

  animateIdle() {
    const t = this.animationTime;

    // 輕微晃動
    this.skeleton.torso.setAngle(-Math.PI / 2 + Math.sin(t) * 0.02);
    this.skeleton.head.setAngle(Math.sin(t * 0.8) * 0.05);

    // 手臂自然下垂
    this.skeleton.leftUpperArm.setAngle(Math.PI / 2 + Math.sin(t * 0.7) * 0.1);
    this.skeleton.rightUpperArm.setAngle(Math.PI / 2 - Math.sin(t * 0.9) * 0.1);

    // 腿部微調
    this.skeleton.leftUpperLeg.setAngle(Math.PI / 2 + Math.sin(t * 0.5) * 0.02);
    this.skeleton.rightUpperLeg.setAngle(Math.PI / 2 - Math.sin(t * 0.5) * 0.02);
  }

  animateWorking() {
    const t = this.animationTime;

    // 前傾
    this.skeleton.torso.setAngle(-Math.PI / 2 + 0.2);

    // 手臂打字動作
    this.skeleton.leftUpperArm.setAngle(Math.PI / 3 + Math.sin(t * 5) * 0.2);
    this.skeleton.rightUpperArm.setAngle(Math.PI / 3 - Math.sin(t * 5 + 0.5) * 0.2);
    this.skeleton.leftLowerArm.setAngle(Math.sin(t * 8) * 0.3);
    this.skeleton.rightLowerArm.setAngle(-Math.sin(t * 8 + 0.3) * 0.3);
  }

  animateWalking() {
    const t = this.animationTime;

    // 軀幹輕微搖擺
    this.skeleton.torso.setAngle(-Math.PI / 2 + Math.sin(t * 2) * 0.05);

    // 手臂擺動
    this.skeleton.leftUpperArm.setAngle(Math.PI / 2 + Math.sin(t * 4) * 0.5);
    this.skeleton.rightUpperArm.setAngle(Math.PI / 2 - Math.sin(t * 4) * 0.5);

    // 腿部交替
    this.skeleton.leftUpperLeg.setAngle(Math.PI / 2 + Math.sin(t * 4) * 0.5);
    this.skeleton.rightUpperLeg.setAngle(Math.PI / 2 - Math.sin(t * 4) * 0.5);
    this.skeleton.leftLowerLeg.setAngle(Math.sin(t * 4 + 1) * 0.4);
    this.skeleton.rightLowerLeg.setAngle(-Math.sin(t * 4 + 1) * 0.4);
  }

  draw() {
    const g = this.graphics;
    g.clear();

    const config = this.config;

    // 繪製角色（基於骨骼位置）
    const headPos = this.skeleton.head;
    const torsoPos = this.skeleton.torso;

    // 頭髮（後層）
    g.circle(headPos.x, headPos.y - 5, 22);
    g.fill({ color: config.hairColor });

    // 雙馬尾
    if (config.hairstyle === 'twin-tail') {
      const leftTail = this.skeleton.leftUpperArm;
      const rightTail = this.skeleton.rightUpperArm;

      g.ellipse(headPos.x - 30, headPos.y, 10, 25);
      g.fill({ color: config.hairColor });
      g.ellipse(headPos.x + 30, headPos.y, 10, 25);
      g.fill({ color: config.hairColor });
    }

    // 臉部
    g.circle(headPos.x, headPos.y, 18);
    g.fill({ color: 0xFFE4C4 });

    // 眼睛（日系大眼睛）
    const blinkPhase = Math.sin(this.animationTime * 3);
    const eyeOpen = blinkPhase > 0.95 ? 0.3 : 1;

    g.circle(headPos.x - 6, headPos.y - 2, 4 * eyeOpen);
    g.fill({ color: config.eyeColor });
    g.circle(headPos.x + 6, headPos.y - 2, 4 * eyeOpen);
    g.fill({ color: config.eyeColor });

    // 眼睛高光
    if (eyeOpen > 0.5) {
      g.circle(headPos.x - 5, headPos.y - 3, 1.5);
      g.fill({ color: 0xFFFFFF });
      g.circle(headPos.x + 7, headPos.y - 3, 1.5);
      g.fill({ color: 0xFFFFFF });
    }

    // 微笑
    g.arc(headPos.x, headPos.y + 3, 4, 0.2, Math.PI - 0.2);
    g.stroke({ color: 0xFF9999, width: 1.5 });

    // 身體
    g.roundRect(torsoPos.x - 12, torsoPos.y - 20, 24, 45, 5);
    g.fill({ color: config.outfitColor });

    // 蝴蝶結/領帶
    g.circle(torsoPos.x, torsoPos.y - 15, 4);
    g.fill({ color: config.accentColor });

    // 手臂
    const leftArm = this.skeleton.leftLowerArm;
    const rightArm = this.skeleton.rightLowerArm;
    g.roundRect(leftArm.x - 4, leftArm.y - 4, 8, 18, 3);
    g.fill({ color: 0xFFE4C4 });
    g.roundRect(rightArm.x - 4, rightArm.y - 4, 8, 18, 3);
    g.fill({ color: 0xFFE4C4 });

    // 腿部
    const leftLeg = this.skeleton.leftLowerLeg;
    const rightLeg = this.skeleton.rightLowerLeg;
    g.roundRect(leftLeg.x - 5, leftLeg.y - 5, 10, 22, 3);
    g.fill({ color: 0x4169E1 });
    g.roundRect(rightLeg.x - 5, rightLeg.y - 5, 10, 22, 3);
    g.fill({ color: 0x4169E1 });

    // 鞋子
    g.roundRect(leftLeg.x - 6, leftLeg.y + 15, 12, 6, 2);
    g.fill({ color: 0x8B4513 });
    g.roundRect(rightLeg.x - 6, rightLeg.y + 15, 12, 6, 2);
    g.fill({ color: 0x8B4513 });

    // 名字標籤
    if (!this.nameTag) {
      this.nameTag = new Text({
        text: config.name,
        style: {
          fontSize: 12,
          fill: 0xFFFFFF,
          fontWeight: 'bold',
          stroke: { color: 0x000000, width: 2 }
        }
      });
      this.nameTag.anchor.set(0.5, 1);
      this.container.addChild(this.nameTag);
    }
    this.nameTag.x = headPos.x;
    this.nameTag.y = headPos.y - 35;
  }

  setState(state) {
    this.state = state;
  }

  setPosition(x, y) {
    this.container.x = x;
    this.container.y = y;
  }
}

// ============ 遊戲場景 ============

class GameScene {
  constructor(app) {
    this.app = app;
    this.scene = new Container();
    this.characters = new Map();
    this.decorations = [];

    app.stage.addChild(this.scene);
    this.createScene();
  }

  createScene() {
    // 背景層
    this.createBackground();

    // 動態裝飾
    this.createDecorations();

    // 角色
    this.createCharacters();
  }

  createBackground() {
    const bg = new Graphics();

    // 天空漸層
    for (let y = 0; y < 300; y++) {
      const ratio = y / 300;
      const r = Math.floor(135 + (200 - 135) * ratio);
      const g = Math.floor(206 + (220 - 206) * ratio);
      const b = Math.floor(235 + (240 - 235) * ratio);
      const color = (r << 16) + (g << 8) + b;

      bg.rect(0, y, this.app.screen.width, 1);
      bg.fill({ color });
    }

    // 牆壁
    bg.rect(0, 300, this.app.screen.width, 400);
    bg.fill({ color: 0xFFF8DC });

    // 地板
    bg.rect(0, 500, this.app.screen.width, 200);
    bg.fill({ color: 0xD2691E });

    // 地板紋理
    for (let x = 0; x < this.app.screen.width; x += 80) {
      bg.rect(x, 500, 2, 200);
      bg.fill({ color: 0xA0522D });
    }

    this.scene.addChild(bg);
  }

  createDecorations() {
    // 雲朵
    for (let i = 0; i < 5; i++) {
      const cloud = new Graphics();
      cloud.circle(0, 0, 30);
      cloud.fill({ color: 0xFFFFFF, alpha: 0.9 });
      cloud.circle(25, -5, 25);
      cloud.fill({ color: 0xFFFFFF, alpha: 0.9 });
      cloud.circle(50, 0, 30);
      cloud.fill({ color: 0xFFFFFF, alpha: 0.9 });

      cloud.x = Math.random() * this.app.screen.width;
      cloud.y = 50 + Math.random() * 150;
      cloud.speed = 0.2 + Math.random() * 0.3;

      this.scene.addChild(cloud);
      this.decorations.push(cloud);
    }

    // 植物搖曳
    for (let i = 0; i < 4; i++) {
      const plant = new Graphics();
      plant.moveTo(0, 0);
      plant.lineTo(-15, -30);
      plant.lineTo(0, -20);
      plant.lineTo(15, -35);
      plant.lineTo(0, 0);
      plant.fill({ color: 0x228B22 });

      plant.x = 50 + i * 350;
      plant.y = 550;
      plant.rotationSpeed = 0.001 + Math.random() * 0.002;
      plant.rotationPhase = Math.random() * Math.PI * 2;

      this.scene.addChild(plant);
      this.decorations.push(plant);
    }
  }

  createCharacters() {
    const configs = {
      sakura: {
        name: '櫻',
        hairColor: 0xFFB6C1,
        eyeColor: 0x4169E1,
        outfitColor: 0xFFFFFF,
        accentColor: 0x4169E1,
        hairstyle: 'twin-tail'
      },
      homura: {
        name: '焰',
        hairColor: 0xDC143C,
        eyeColor: 0xDC143C,
        outfitColor: 0x2F4F4F,
        accentColor: 0xDC143C,
        hairstyle: 'short'
      },
      ryo: {
        name: '涼',
        hairColor: 0x4169E1,
        eyeColor: 0x4169E1,
        outfitColor: 0x4169E1,
        accentColor: 0xFFFFFF,
        hairstyle: 'short'
      }
    };

    // 創建角色
    const positions = [
      { x: 200, y: 600 },
      { x: 350, y: 600 },
      { x: 750, y: 600 }
    ];

    Object.keys(configs).forEach((id, index) => {
      const char = new GenshinCharacter(configs[id]);
      char.setPosition(positions[index].x, positions[index].y);
      this.scene.addChild(char.container);
      this.characters.set(id, char);
    });
  }

  update(deltaTime) {
    // 更新角色
    this.characters.forEach(char => {
      char.update(deltaTime);
    });

    // 更新裝飾
    this.decorations.forEach(deco => {
      if (deco.speed) {
        // 雲朵移動
        deco.x += deco.speed * deltaTime;
        if (deco.x > this.app.screen.width + 100) {
          deco.x = -100;
        }
      } else if (deco.rotationSpeed) {
        // 植物搖曳
        deco.rotation = Math.sin(Date.now() * deco.rotationSpeed + deco.rotationPhase) * 0.1;
      }
    });
  }
}

// ============ 主程序 ============

async function init() {
  console.log('[Game] 初始化遊戲...');

  const app = new Application();
  await app.init({
    width: 1200,
    height: 700,
    backgroundColor: 0x87CEEB,
    antialias: true,
    resolution: window.devicePixelRatio || 1,
    autoDensity: true,
  });

  document.getElementById('game-container').appendChild(app.canvas);

  // 創建遊戲場景
  const gameScene = new GameScene(app);

  // 遊戲循環
  app.ticker.add((ticker) => {
    gameScene.update(ticker.deltaTime);
  });

  console.log('[Game] 遊戲啟動完成！');

  // 測試狀態切換
  setTimeout(() => {
    const sakura = gameScene.characters.get('sakura');
    if (sakura) {
      sakura.setState('working');
      console.log('[Game] 櫻切換到工作狀態');
    }
  }, 3000);
}

init().catch(err => {
  console.error('[Game] 初始化失敗:', err);
  document.getElementById('error-message').textContent = `錯誤: ${err.message}`;
});
