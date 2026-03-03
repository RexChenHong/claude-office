/**
 * Claude Office - Sprite Animation System
 * 
 * 處理角色 sprite sheet 動畫播放與狀態切換
 */

import { AnimatedSprite, Spritesheet, Assets, Texture, TextureSource } from 'pixi.js';

export class CharacterAnimator {
  constructor() {
    this.spritesheets = new Map();
    this.currentSprite = null;
    this.currentAction = null;
    this.isPlaying = false;
    this.animationSpeed = 0.15; // 調整動畫速度（越小越慢）
  }

  /**
   * 載入角色的所有動畫 sprite sheets
   */
  async loadCharacterSprites(characterId) {
    const actions = ['idle', 'walk_left', 'walk_right', 'working', 'waiting'];
    const loadedSpritesheets = {};

    for (const action of actions) {
      try {
        const jsonPath = `/assets/sprites/${characterId}/${action}.json`;
        
        // 1. 使用 fetch 載入 JSON
        const response = await fetch(jsonPath);
        const jsonData = await response.json();
        
        // 2. 載入對應的 PNG 圖片
        const pngPath = `/assets/sprites/${characterId}/${action}.png`;
        const texture = await Assets.load(pngPath);
        
        // 3. 創建 Spritesheet
        const spritesheet = new Spritesheet(texture, jsonData);
        await spritesheet.parse();
        
        loadedSpritesheets[action] = spritesheet;
        console.log(`[Animator] 載入 ${characterId} - ${action} 成功`);
      } catch (err) {
        console.warn(`[Animator] 載入 ${characterId} - ${action} 失敗:`, err);
      }
    }

    this.spritesheets.set(characterId, loadedSpritesheets);
    return loadedSpritesheets;
  }

  /**
   * 建立動畫精靈
   */
  createAnimatedSprite(characterId, action) {
    const charSprites = this.spritesheets.get(characterId);
    if (!charSprites || !charSprites[action]) {
      console.warn(`[Animator] 找不到 ${characterId} - ${action}`);
      return null;
    }

    const spritesheet = charSprites[action];
    const textures = Object.values(spritesheet.textures);

    if (textures.length === 0) {
      console.warn(`[Animator] ${characterId} - ${action} 沒有幀`);
      return null;
    }

    // 對 textures 排序以確保動畫順序正確
    textures.sort((a, b) => {
      const frameA = parseInt(a.textureCache.textureCacheIds?.frameId || 0);
      const frameB = parseInt(b.textureCache.textureCacheIds?.frameId || 0);
      return frameA - frameB;
    });

    console.log(`[Animator] ${characterId} - ${action} 共 ${textures.length} 幀`);

    const animatedSprite = new AnimatedSprite(textures);
    animatedSprite.animationSpeed = this.animationSpeed;
    animatedSprite.anchor.set(0.5, 1); // 底部中心
    animatedSprite.loop = true;
    animatedSprite.play();

    this.currentSprite = animatedSprite;
    this.currentAction = action;

    return animatedSprite;
  }

  /**
   * 切換動作
   */
  switchAction(characterId, newAction, container) {
    if (this.currentAction === newAction) return;

    const oldSprite = this.currentSprite;
    const newSprite = this.createAnimatedSprite(characterId, newAction);

    if (!newSprite) return;

    // 保持位置
    if (oldSprite) {
      newSprite.x = oldSprite.x;
      newSprite.y = oldSprite.y;
      newSprite.scale = oldSprite.scale.clone();
      container.removeChild(oldSprite);
    }

    container.addChild(newSprite);
    
    console.log(`[Animator] 切換動作: ${this.currentAction} → ${newAction}`);
  }

  /**
   * 播放走路動畫（移動中）
   */
  playWalk(direction, container) {
    const action = direction === 'left' ? 'walk_left' : 'walk_right';
    this.switchAction(this.currentCharacterId, action, container);
  }

  /**
   * 播放閒置動畫
   */
  playIdle(container) {
    this.switchAction(this.currentCharacterId, 'idle', container);
  }

  /**
   * 播放工作動畫
   */
  playWorking(container) {
    this.switchAction(this.currentCharacterId, 'working', container);
  }

  /**
   * 播放等待動畫
   */
  playWaiting(container) {
    this.switchAction(this.currentCharacterId, 'waiting', container);
  }

  /**
   * 停止動畫
   */
  stop() {
    if (this.currentSprite) {
      this.currentSprite.stop();
      this.isPlaying = false;
    }
  }

  /**
   * 繼續動畫
   */
  play() {
    if (this.currentSprite) {
      this.currentSprite.play();
      this.isPlaying = true;
    }
  }

  /**
   * 設定動畫速度
   */
  setSpeed(speed) {
    this.animationSpeed = speed;
    if (this.currentSprite) {
      this.currentSprite.animationSpeed = speed;
    }
  }
}

/**
 * 角色狀態機
 */
export class CharacterStateMachine {
  constructor(animator, characterId, container) {
    this.animator = animator;
    this.characterId = characterId;
    this.container = container;
    this.state = 'idle';
    this.position = { x: 0, y: 0 };
    this.targetPosition = null;
    this.isMoving = false;
    this.moveSpeed = 3; // 移動速度（像素/幀）
  }

  /**
   * 設定角色位置
   */
  setPosition(x, y) {
    this.position = { x, y };
    if (this.animator.currentSprite) {
      this.animator.currentSprite.x = x;
      this.animator.currentSprite.y = y;
    }
  }

  /**
   * 移動到目標位置
   */
  moveTo(targetX, targetY, onComplete) {
    this.targetPosition = { x: targetX, y: targetY };
    this.isMoving = true;

    // 判斷方向
    const direction = targetX > this.position.x ? 'right' : 'left';
    this.animator.playWalk(direction, this.container);

    // 移動循環
    const moveLoop = () => {
      if (!this.isMoving) return;

      const dx = this.targetPosition.x - this.position.x;
      const dy = this.targetPosition.y - this.position.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance < this.moveSpeed) {
        // 到達目標
        this.setPosition(this.targetPosition.x, this.targetPosition.y);
        this.isMoving = false;
        
        if (onComplete) onComplete();
        return;
      }

      // 移動
      const ratio = this.moveSpeed / distance;
      this.position.x += dx * ratio;
      this.position.y += dy * ratio;
      
      if (this.animator.currentSprite) {
        this.animator.currentSprite.x = this.position.x;
        this.animator.currentSprite.y = this.position.y;
      }

      requestAnimationFrame(moveLoop);
    };

    moveLoop();
  }

  /**
   * 設定狀態
   */
  setState(newState) {
    switch (newState) {
      case 'idle':
        this.animator.playIdle(this.container);
        break;
      case 'working':
        this.animator.playWorking(this.container);
        break;
      case 'waiting':
        this.animator.playWaiting(this.container);
        break;
      default:
        console.warn(`[StateMachine] 未知狀態: ${newState}`);
    }
    this.state = newState;
  }

  /**
   * 取得當前狀態
   */
  getState() {
    return this.state;
  }
}
