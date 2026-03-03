/**
 * PBR 貼圖生成器
 * 程序化生成木紋、布料、金屬等紋理
 */

import * as THREE from 'three';

// ============ 木地板貼圖生成 ============

export function createWoodTexture(width = 512, height = 512) {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');

  // 基礎顏色
  ctx.fillStyle = '#D4B896';
  ctx.fillRect(0, 0, width, height);

  // 木紋條紋
  const stripeCount = 8;
  const stripeWidth = width / stripeCount;

  for (let i = 0; i < stripeCount; i++) {
    const x = i * stripeWidth;
    const variation = Math.random() * 30 - 15;

    // 隨機顏色變化
    const r = 212 + variation;
    const g = 184 + variation;
    const b = 150 + variation;

    ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
    ctx.fillRect(x, 0, stripeWidth, height);

    // 添加細節
    for (let j = 0; j < 20; j++) {
      const y = Math.random() * height;
      const lineLength = Math.random() * 50 + 20;
      const lineWidth = Math.random() * 2 + 1;

      ctx.strokeStyle = `rgba(0, 0, 0, ${Math.random() * 0.1})`;
      ctx.lineWidth = lineWidth;
      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.lineTo(x + lineLength, y);
      ctx.stroke();
    }
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(2, 2);

  return texture;
}

export function createWoodNormalMap(width = 512, height = 512) {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');

  // 基礎顏色（中性法線）
  ctx.fillStyle = '#8080FF';
  ctx.fillRect(0, 0, width, height);

  // 木紋凹凸
  const stripeCount = 8;
  const stripeWidth = width / stripeCount;

  for (let i = 0; i < stripeCount; i++) {
    const x = i * stripeWidth;

    // 添加邊緣凹凸
    ctx.strokeStyle = 'rgba(128, 128, 255, 0.5)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, height);
    ctx.stroke();
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(2, 2);

  return texture;
}

// ============ 布料貼圖生成 ============

export function createFabricTexture(width = 512, height = 512, color = '#808080') {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');

  // 基礎顏色
  ctx.fillStyle = color;
  ctx.fillRect(0, 0, width, height);

  // 布料紋理（編織效果）
  const gridSize = 4;

  for (let x = 0; x < width; x += gridSize) {
    for (let y = 0; y < height; y += gridSize) {
      const variation = Math.random() * 20 - 10;

      // 解析基礎顏色
      const r = parseInt(color.slice(1, 3), 16) + variation;
      const g = parseInt(color.slice(3, 5), 16) + variation;
      const b = parseInt(color.slice(5, 7), 16) + variation;

      ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
      ctx.fillRect(x, y, gridSize - 1, gridSize - 1);
    }
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(4, 4);

  return texture;
}

export function createFabricNormalMap(width = 512, height = 512) {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');

  // 基礎顏色（中性法線）
  ctx.fillStyle = '#8080FF';
  ctx.fillRect(0, 0, width, height);

  // 布料編織凹凸
  const gridSize = 4;

  for (let x = 0; x < width; x += gridSize) {
    for (let y = 0; y < height; y += gridSize) {
      // 隨機凹凸方向
      const r = 128 + Math.random() * 20 - 10;
      const g = 128 + Math.random() * 20 - 10;

      ctx.fillStyle = `rgb(${r}, ${g}, 255)`;
      ctx.fillRect(x, y, gridSize - 1, gridSize - 1);
    }
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(4, 4);

  return texture;
}

// ============ 金屬貼圖生成 ============

export function createMetalTexture(width = 512, height = 512, color = '#4A4A4A') {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');

  // 基礎顏色
  ctx.fillStyle = color;
  ctx.fillRect(0, 0, width, height);

  // 金屬反光效果
  const gradient = ctx.createLinearGradient(0, 0, width, height);
  gradient.addColorStop(0, 'rgba(255, 255, 255, 0.1)');
  gradient.addColorStop(0.5, 'rgba(0, 0, 0, 0.1)');
  gradient.addColorStop(1, 'rgba(255, 255, 255, 0.1)');

  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, width, height);

  // 添加細微刮痕
  for (let i = 0; i < 100; i++) {
    const x1 = Math.random() * width;
    const y1 = Math.random() * height;
    const x2 = x1 + Math.random() * 50;
    const y2 = y1 + Math.random() * 50;

    ctx.strokeStyle = `rgba(255, 255, 255, ${Math.random() * 0.1})`;
    ctx.lineWidth = Math.random() * 2;
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;

  return texture;
}

export function createMetalRoughnessMap(width = 512, height = 512, roughness = 0.3) {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');

  // 基礎粗糙度
  const baseRoughness = Math.floor(roughness * 255);
  ctx.fillStyle = `rgb(${baseRoughness}, ${baseRoughness}, ${baseRoughness})`;
  ctx.fillRect(0, 0, width, height);

  // 添加變化
  for (let x = 0; x < width; x += 2) {
    for (let y = 0; y < height; y += 2) {
      const variation = Math.random() * 20 - 10;
      const r = baseRoughness + variation;
      const final = Math.max(0, Math.min(255, r));

      ctx.fillStyle = `rgb(${final}, ${final}, ${final})`;
      ctx.fillRect(x, y, 2, 2);
    }
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;

  return texture;
}

// ============ 環境貼圖生成 ============

export function createEnvironmentTexture() {
  // 創建簡單的環境貼圖（漸層天空）
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext('2d');

  // 天空漸層
  const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
  gradient.addColorStop(0, '#87CEEB');
  gradient.addColorStop(0.5, '#E0F6FF');
  gradient.addColorStop(1, '#FFFFFF');

  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // 添加一些雲朵
  ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
  for (let i = 0; i < 10; i++) {
    const x = Math.random() * canvas.width;
    const y = Math.random() * canvas.height * 0.5;
    const radius = Math.random() * 50 + 20;

    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fill();
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.mapping = THREE.EquirectangularReflectionMapping;

  return texture;
}

// ============ 玻璃貼圖生成 ============

export function createGlassNormalMap(width = 512, height = 512) {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');

  // 基礎顏色（中性法線）
  ctx.fillStyle = '#8080FF';
  ctx.fillRect(0, 0, width, height);

  // 添加細微凹凸（玻璃表面不平整）
  for (let x = 0; x < width; x += 8) {
    for (let y = 0; y < height; y += 8) {
      const r = 128 + Math.random() * 4 - 2;
      const g = 128 + Math.random() * 4 - 2;

      ctx.fillStyle = `rgb(${r}, ${g}, 255)`;
      ctx.fillRect(x, y, 8, 8);
    }
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;

  return texture;
}

// ============ 螢幕貼圖生成 ============

export function createMonitorScreenTexture(width = 512, height = 512) {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');

  // 螢幕背景
  ctx.fillStyle = '#001122';
  ctx.fillRect(0, 0, width, height);

  // 添加程式碼效果
  ctx.font = '12px monospace';
  ctx.fillStyle = '#00FF00';

  for (let y = 20; y < height; y += 15) {
    const text = 'const data = await fetch(url);'.substring(0, Math.random() * 30 + 10);
    ctx.fillText(text, 10, y);
  }

  const texture = new THREE.CanvasTexture(canvas);
  return texture;
}
