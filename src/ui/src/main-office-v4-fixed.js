/**
 * Claude Office - V4 修復版（WebGL 檢測 + 降級方案）
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { SMAAPass } from 'three/addons/postprocessing/SMAAPass.js';

// 導入貼圖生成器
import {
  createWoodTexture,
  createWoodNormalMap,
  createFabricTexture,
  createFabricNormalMap,
  createMetalTexture,
  createMetalRoughnessMap,
  createEnvironmentTexture,
  createGlassNormalMap,
  createMonitorScreenTexture,
} from './texture-generator.js';

// ============ 全局變量 ============

let scene, camera, renderer, controls, composer;
let clock;
let webglSupported = false;

// 貼圖快取
let textures = {};

// ============ WebGL 支援檢測 ============

function checkWebGLSupport() {
  try {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    return !!gl;
  } catch (e) {
    return false;
  }
}

// ============ 初始化場景 ============

function init() {
  console.log('[Office Generator V4] 檢測 WebGL 支援...');

  // 檢測 WebGL 支援
  webglSupported = checkWebGLSupport();

  if (!webglSupported) {
    showError('您的瀏覽器不支援 WebGL，無法顯示 3D 場景。<br>請嘗試：<br>1. 更新瀏覽器<br>2. 更新顯卡驅動<br>3. 使用其他瀏覽器（Chrome、Firefox）');
    return;
  }

  console.log('[Office Generator V4 - 5人辦公室] 初始化場景...');

  try {
    // 創建場景
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xF5F5F5);

    // 創建相機
    camera = new THREE.PerspectiveCamera(
      60,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    camera.position.set(15, 12, 15);
    camera.lookAt(0, 0, 0);

    // 創建渲染器（降低性能需求）
    renderer = new THREE.WebGLRenderer({
      antialias: false,  // 關閉抗鋸齒
      powerPreference: "high-performance",
      failIfMajorPerformanceCaveat: false  // 允許軟體渲染
    });

    if (!renderer) {
      throw new Error('無法創建 WebGL 渲染器');
    }

    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(1);  // 降低像素比
    renderer.shadowMap.enabled = false;  // 關閉陰影
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.5;
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    document.getElementById('game-container').appendChild(renderer.domElement);

    // 添加控制器
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.target.set(0, 0, 0);

    // 時鐘
    clock = new THREE.Clock();

    // 生成貼圖
    generateTextures();

    // 創建辦公室
    createOffice();

    // 設置燈光
    setupLighting();

    // 設置後處理（簡化版）
    setupPostProcessing();

    // 監聽視窗大小變化
    window.addEventListener('resize', onWindowResize, false);

    console.log('[Office Generator V4] 場景初始化完成！');

  } catch (error) {
    console.error('[Office Generator V4] 初始化失敗:', error);
    showError('3D 場景初始化失敗：<br>' + error.message);
    return;
  }
}

// ============ 顯示錯誤訊息 ============

function showError(message) {
  const container = document.getElementById('game-container');
  container.innerHTML = `
    <div style="
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100vh;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      text-align: center;
      padding: 20px;
    ">
      <div>
        <h1 style="font-size: 48px; margin-bottom: 20px;">⚠️</h1>
        <h2 style="font-size: 24px; margin-bottom: 20px;">無法載入 3D 場景</h2>
        <p style="font-size: 16px; line-height: 1.6;">${message}</p>
      </div>
    </div>
  `;
}

// ============ 生成貼圖（簡化版）============

function generateTextures() {
  console.log('[Texture Generator] 生成 PBR 貼圖...');

  try {
    textures = {
      wood: {
        diffuse: createWoodTexture(512, 512),  // 降低解析度
        normal: createWoodNormalMap(512, 512),
      },
      fabric: {
        grey: createFabricTexture(256, 256, '#808080'),
        blue: createFabricTexture(256, 256, '#4169E1'),
        normal: createFabricNormalMap(256, 256),
      },
      metal: {
        diffuse: createMetalTexture(256, 256, '#4A4A4A'),
        roughness: createMetalRoughnessMap(256, 256, 0.3),
      },
      environment: createEnvironmentTexture(),
      glass: {
        normal: createGlassNormalMap(256, 256),
      },
      monitor: createMonitorScreenTexture(256, 256),
    };

    console.log('[Texture Generator] PBR 貼圖生成完成！');
  } catch (error) {
    console.warn('[Texture Generator] 貼圖生成失敗，使用純色:', error);
    // 降級方案：不使用貼圖
    textures = {};
  }
}

// ============ 創建辦公室（簡化版）============

function createOffice() {
  console.log('[Office Generator V4] 創建 5 人辦公室...');

  createFloor();
  createWalls();
  createWorkstations();
  createLoungeArea(6, 5);

  console.log('[Office Generator V4] 5 人辦公室創建完成！');
}

// ============ 地板（簡化版）============

function createFloor() {
  const floorGeometry = new THREE.PlaneGeometry(20, 20);
  const floorMaterial = new THREE.MeshStandardMaterial({
    color: 0xE8E8E8,
    roughness: 0.6,
    metalness: 0.1,
  });

  if (textures.wood) {
    floorMaterial.map = textures.wood.diffuse;
    floorMaterial.normalMap = textures.wood.normal;
  }

  const floor = new THREE.Mesh(floorGeometry, floorMaterial);
  floor.rotation.x = -Math.PI / 2;
  floor.name = 'Floor';
  scene.add(floor);
}

// ============ 牆面 ============

function createWalls() {
  const wallMaterial = new THREE.MeshStandardMaterial({
    color: 0xFFFFFF,
    roughness: 0.9,
    metalness: 0.0,
    side: THREE.DoubleSide,
  });

  // 後牆
  const backWallGeometry = new THREE.PlaneGeometry(20, 2.8);
  const backWall = new THREE.Mesh(backWallGeometry, wallMaterial);
  backWall.position.set(0, 1.4, -10);
  backWall.name = 'BackWall';
  scene.add(backWall);

  // 左牆
  const leftWallGeometry = new THREE.PlaneGeometry(20, 2.8);
  const leftWall = new THREE.Mesh(leftWallGeometry, wallMaterial);
  leftWall.rotation.y = Math.PI / 2;
  leftWall.position.set(-10, 1.4, 0);
  leftWall.name = 'LeftWall';
  scene.add(leftWall);
}

// ============ 5 個工作站（簡化版）============

function createWorkstations() {
  const startX = -6;
  const spacing = 3;

  for (let i = 0; i < 5; i++) {
    const x = startX + i * spacing;
    createWorkstation(x, 0, i + 1);
  }

  console.log('[Office Generator V4] 創建了 5 個工作站');
}

function createWorkstation(x, z, index) {
  const group = new THREE.Group();
  group.name = `Workstation_${index}`;
  group.position.set(x, 0, z);

  createDesk(group);
  createChair(group);
  createMonitor(group);

  scene.add(group);
}

// ============ 辦公桌 ============

function createDesk(parent) {
  const topGeometry = new THREE.BoxGeometry(1.2, 0.025, 0.6);
  const topMaterial = new THREE.MeshStandardMaterial({
    color: 0xFAFAFA,
    roughness: 0.4,
    metalness: 0.1,
  });

  if (textures.wood) {
    topMaterial.map = textures.wood.diffuse;
  }

  const top = new THREE.Mesh(topGeometry, topMaterial);
  top.position.y = 0.75;
  top.name = 'DeskTop';
  parent.add(top);

  // 桌腿
  const legMaterial = new THREE.MeshStandardMaterial({
    color: 0x4A4A4A,
    roughness: 0.3,
    metalness: 0.9,
  });

  if (textures.metal) {
    legMaterial.map = textures.metal.diffuse;
  }

  const legPositions = [
    { x: -0.55, z: -0.25 },
    { x: -0.55, z: 0.25 },
    { x: 0.55, z: -0.25 },
    { x: 0.55, z: 0.25 },
  ];

  legPositions.forEach((pos, i) => {
    const legGeometry = new THREE.CylinderGeometry(0.025, 0.025, 0.725, 8);
    const leg = new THREE.Mesh(legGeometry, legMaterial);
    leg.position.set(pos.x, 0.3625, pos.z);
    leg.name = `DeskLeg_${i + 1}`;
    parent.add(leg);
  });
}

// ============ 辦公椅 ============

function createChair(parent) {
  const chairGroup = new THREE.Group();
  chairGroup.name = 'Chair';
  chairGroup.position.set(0, 0, 0.8);

  const chairMaterial = new THREE.MeshStandardMaterial({
    color: 0x2F4F4F,
    roughness: 0.7,
    metalness: 0.1,
  });

  if (textures.fabric) {
    chairMaterial.map = textures.fabric.grey;
  }

  // 座椅
  const seatGeometry = new THREE.BoxGeometry(0.5, 0.1, 0.5);
  const seat = new THREE.Mesh(seatGeometry, chairMaterial);
  seat.position.y = 0.5;
  seat.name = 'ChairSeat';
  chairGroup.add(seat);

  // 椅背
  const backGeometry = new THREE.BoxGeometry(0.5, 0.6, 0.1);
  const back = new THREE.Mesh(backGeometry, chairMaterial);
  back.position.set(0, 0.8, 0.2);
  back.name = 'ChairBack';
  chairGroup.add(back);

  // 椅腿
  const legMaterial = new THREE.MeshStandardMaterial({
    color: 0x888888,
    roughness: 0.2,
    metalness: 0.9,
  });

  const legGeometry = new THREE.CylinderGeometry(0.02, 0.02, 0.5, 8);
  const centerLeg = new THREE.Mesh(legGeometry, legMaterial);
  centerLeg.position.y = 0.25;
  centerLeg.name = 'ChairLeg';
  chairGroup.add(centerLeg);

  parent.add(chairGroup);
}

// ============ 螢幕 ============

function createMonitor(parent) {
  const monitorGroup = new THREE.Group();
  monitorGroup.name = 'Monitor';
  monitorGroup.position.set(0, 1.15, -0.2);

  // 螢幕外框
  const frameGeometry = new THREE.BoxGeometry(0.6, 0.4, 0.03);
  const frameMaterial = new THREE.MeshStandardMaterial({
    color: 0x1a1a1a,
    roughness: 0.3,
    metalness: 0.7,
  });
  const frame = new THREE.Mesh(frameGeometry, frameMaterial);
  frame.name = 'MonitorFrame';
  monitorGroup.add(frame);

  // 螢幕（發光）
  const screenGeometry = new THREE.PlaneGeometry(0.56, 0.36);
  const screenMaterial = new THREE.MeshStandardMaterial({
    map: textures.monitor || null,
    emissive: 0x0077ff,
    emissiveIntensity: 1.0,
  });
  const screen = new THREE.Mesh(screenGeometry, screenMaterial);
  screen.position.z = 0.016;
  screen.name = 'MonitorScreen';
  monitorGroup.add(screen);

  parent.add(monitorGroup);
}

// ============ 公共區域（簡化版）============

function createLoungeArea(centerX, centerZ) {
  const loungeGroup = new THREE.Group();
  loungeGroup.name = 'LoungeArea';
  loungeGroup.position.set(centerX, 0, centerZ);

  createSofa(loungeGroup, 0, 0);
  createCoffeeTable(loungeGroup, 0, 1.5);

  scene.add(loungeGroup);
}

function createSofa(parent, x, z) {
  const sofaGroup = new THREE.Group();
  sofaGroup.name = 'Sofa';
  sofaGroup.position.set(x, 0, z);

  const sofaMaterial = new THREE.MeshStandardMaterial({
    color: 0x808080,
    roughness: 0.9,
    metalness: 0.0,
  });

  if (textures.fabric) {
    sofaMaterial.map = textures.fabric.grey;
  }

  // 座椅
  const seatGeometry = new THREE.BoxGeometry(1.8, 0.4, 0.9);
  const seat = new THREE.Mesh(seatGeometry, sofaMaterial);
  seat.position.y = 0.2;
  seat.name = 'SofaSeat';
  sofaGroup.add(seat);

  // 椅背
  const backGeometry = new THREE.BoxGeometry(1.8, 0.4, 0.2);
  const back = new THREE.Mesh(backGeometry, sofaMaterial);
  back.position.set(0, 0.6, 0.35);
  back.name = 'SofaBack';
  sofaGroup.add(back);

  parent.add(sofaGroup);
}

function createCoffeeTable(parent, x, z) {
  const tableGroup = new THREE.Group();
  tableGroup.name = 'CoffeeTable';
  tableGroup.position.set(x, 0, z);

  // 桌面
  const topGeometry = new THREE.BoxGeometry(1.0, 0.05, 0.6);
  const topMaterial = new THREE.MeshStandardMaterial({
    color: 0x1a1a1a,
    roughness: 0.2,
    metalness: 0.6,
  });

  if (textures.wood) {
    topMaterial.map = textures.wood.diffuse;
  }

  const top = new THREE.Mesh(topGeometry, topMaterial);
  top.position.y = 0.45;
  top.name = 'TableTop';
  tableGroup.add(top);

  // 桌腿
  const legMaterial = new THREE.MeshStandardMaterial({
    color: 0x1a1a1a,
    roughness: 0.2,
    metalness: 0.9,
  });

  const legPositions = [
    { x: -0.4, z: -0.25 },
    { x: -0.4, z: 0.25 },
    { x: 0.4, z: -0.25 },
    { x: 0.4, z: 0.25 },
  ];

  legPositions.forEach((pos, i) => {
    const legGeometry = new THREE.CylinderGeometry(0.02, 0.02, 0.45, 8);
    const leg = new THREE.Mesh(legGeometry, legMaterial);
    leg.position.set(pos.x, 0.225, pos.z);
    leg.name = `TableLeg_${i + 1}`;
    tableGroup.add(leg);
  });

  parent.add(tableGroup);
}

// ============ 燈光系統（簡化版）============

function setupLighting() {
  // 環境光
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
  scene.add(ambientLight);

  // 主光源
  const mainLight = new THREE.DirectionalLight(0xffffff, 0.8);
  mainLight.position.set(10, 15, 10);
  scene.add(mainLight);

  // 應用環境貼圖
  if (textures.environment) {
    scene.environment = textures.environment;
  }

  console.log('[Office Generator V4] 燈光設置完成');
}

// ============ 後處理（簡化版）============

function setupPostProcessing() {
  try {
    composer = new EffectComposer(renderer);

    const renderPass = new RenderPass(scene, camera);
    composer.addPass(renderPass);

    const bloomPass = new UnrealBloomPass(
      new THREE.Vector2(window.innerWidth, window.innerHeight),
      0.3,
      0.4,
      0.85
    );
    composer.addPass(bloomPass);

    console.log('[Office Generator V4] 後處理設置完成');
  } catch (error) {
    console.warn('[Office Generator V4] 後處理設置失敗，使用基礎渲染:', error);
    composer = null;
  }
}

// ============ 動畫循環 ============

function animate() {
  requestAnimationFrame(animate);

  if (controls) {
    controls.update();
  }

  if (composer) {
    composer.render();
  } else if (renderer && scene && camera) {
    renderer.render(scene, camera);
  }
}

// ============ 視窗大小調整 ============

function onWindowResize() {
  if (!camera || !renderer) return;

  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);

  if (composer) {
    composer.setSize(window.innerWidth, window.innerHeight);
  }
}

// ============ 啟動 ============

init();

if (webglSupported && renderer) {
  animate();
  console.log('[Office Generator V4] 5 人辦公室場景生成完成！');
  console.log('[Office Generator V4] 測試地址：http://100.113.156.108:8055/');
} else {
  console.error('[Office Generator V4] 啟動失敗：WebGL 不支援');
}
