/**
 * Claude Office - 遊戲角色系統
 * 使用 PixiJS Graphics 繪製角色（臨時方案）
 * 確保角色特徵一致，展示遊戲概念
 */

import { Graphics, AnimatedSprite, Application, Container, Text, Assets, Spritesheet, Texture } from 'pixi.js';

export class GameCharacter {
  constructor(characterConfig) {
    this.config = characterConfig;
    this.container = new Container();
    this.graphics = new Graphics();
    this.state = 'idle';
    this.animationTime = 0;
    
    this.container.addChild(this.graphics);
    this.drawCharacter();
  }

  /**
   * 繪製角色（使用 PixiJS Graphics）
   * 確保所有幀的角色特徵完全一致
   */
  drawCharacter() {
    const g = this.graphics;
    g.clear();
    
    // 動畫偏移（基於時間）
    const breathe = Math.sin(this.animationTime * 0.05) * 2; // 呼吸效果
    const blink = Math.sin(this.animationTime * 0.2) > 0.95 ? 0.5 : 1; // 眨眼
    
    // 角色特徵（固定不變）
    const hairColor = this.config.hairColor;
    const eyeColor = this.config.eyeColor;
    const outfitColor = this.config.outfitColor;
    
    // 身體（6頭身比例）
    const bodyHeight = 60;
    const headSize = 20;
    
    // 頭髮
    g.circle(0, -bodyHeight + breathe, headSize + 5);
    g.fill({ color: hairColor });
    
    // 臉部
    g.circle(0, -bodyHeight + 5, headSize);
    g.fill({ color: 0xFFE4C4 }); // 膚色
    
    // 眼睛
    g.circle(-7, -bodyHeight + 5, 3 * blink);
    g.fill({ color: eyeColor });
    g.circle(7, -bodyHeight + 5, 3 * blink);
    g.fill({ color: eyeColor });
    
    // 身體（服裝）
    g.roundRect(-15, -bodyHeight + 25, 30, 40, 5);
    g.fill({ color: outfitColor });
    
    // 手臂
    g.roundRect(-25, -bodyHeight + 30, 10, 25, 3);
    g.fill({ color: 0xFFE4C4 });
    g.roundRect(15, -bodyHeight + 30, 10, 25, 3);
    g.fill({ color: 0xFFE4C4 });
    
    // 腿部
    g.roundRect(-12, -bodyHeight + 65, 10, 30, 3);
    g.fill({ color: 0x4169E1 }); // 褲子顏色
    g.roundRect(2, -bodyHeight + 65, 10, 30, 3);
    g.fill({ color: 0x4169E1 });
    
    // 腳部
    g.roundRect(-14, -bodyHeight + 95, 14, 8, 2);
    g.fill({ color: 0x8B4513 }); // 鞋子顏色
    g.roundRect(0, -bodyHeight + 95, 14, 8, 2);
    g.fill({ color: 0x8B4513 });
    
    // 名字標籤
    this.nameText = new Text({
      text: this.config.name,
      style: {
        fontSize: 12,
        fill: 0xFFFFFF,
        fontWeight: 'bold',
        stroke: { color: 0x000000, width: 2 }
      }
    });
    this.nameText.anchor.set(0.5, 1);
    this.nameText.y = -bodyHeight - 30;
    this.container.addChild(this.nameText);
  }

  /**
   * 更新動畫
   */
  update(deltaTime) {
    this.animationTime += deltaTime;
    this.drawCharacter(); // 重新繪製（實現動畫效果）
  }

  /**
   * 切換狀態
   */
  setState(newState) {
    this.state = newState;
    // 可以根據狀態改變動畫
  }

  /**
   * 設置位置
   */
  setPosition(x, y) {
    this.container.x = x;
    this.container.y = y;
  }
}

/**
 * 角色配置（日系原神風格）
 */
export const CHARACTER_CONFIGS = {
  sakura: {
    id: 'sakura',
    name: '櫻',
    hairColor: 0xFFB6C1, // 粉色
    eyeColor: 0x4169E1,  // 藍色
    outfitColor: 0xFFFFFF, // 白色
    accentColor: 0x4169E1  // 藍色蝴蝶結
  },
  homura: {
    id: 'homura',
    name: '焰',
    hairColor: 0xDC143C, // 紅色
    eyeColor: 0xDC143C,  // 紅色
    outfitColor: 0x2F4F4F, // 黑色
    accentColor: 0xDC143C  // 紅色領帶
  },
  ryo: {
    id: 'ryo',
    name: '涼',
    hairColor: 0x4169E1, // 藍色
    eyeColor: 0x4169E1,  // 藍色
    outfitColor: 0x4169E1, // 藍色
    accentColor: 0xFFFFFF  // 白色領帶
  },
  koto: {
    id: 'koto',
    name: '琴',
    hairColor: 0x32CD32, // 綠色
    eyeColor: 0x32CD32,  // 綠色
    outfitColor: 0x32CD32, // 綠色
    accentColor: 0xFFFFFF  // 白色
  },
  yoi: {
    id: 'yoi',
    name: '宵',
    hairColor: 0x9370DB, // 紫色
    eyeColor: 0x9370DB,  // 紫色
    outfitColor: 0x9370DB, // 紴色
    accentColor: 0xFFD700  // 金色
  }
};
