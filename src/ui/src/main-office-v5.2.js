/**
 * Claude Office - V5.2（完整細節 + 低曝光）
 * 保留 V5 所有細節 + V5.1 低光照
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';

// 導入貼圖生成器
import {
  createWoodTexture,
  createWoodNormalMap,
  createFabricTexture,
  createFabricNormalMap,
  createMetalTexture,
  createMetalRoughnessMap,
  createEnvironmentTexture,
} from './texture-generator.js';

// ============ 全局變量 ============

let scene, camera, renderer, controls, composer;
let clock;
let textures = {};

// ============ 初始化場景 ============

function init() {
  console.log('[Office Generator V5.2] 初始化場景（完整細節 + 低曝光）...');

  // 創建場景
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xF5F5F5);

  // 創建相機
  camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.set(15, 12, 15);
  camera.lookAt(0, 0, 0);

  // 創建渲染器（低曝光）
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.5;  // V5.1 低曝光
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.physicallyCorrectLights = true;
  document.getElementById('game-container').appendChild(renderer.domElement);

  // 添加控制器
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;

  // 時鐘
  clock = new THREE.Clock();

  // 生成貼圖
  generateTextures();

  // 創建辦公室
  createOffice();

  // 設置燈光（V5.1 低光照）
  setupLighting();

  // 設置後處理（移除 Bloom）
  // setupPostProcessing();

  // 監聽視窗大小變化
  window.addEventListener('resize', onWindowResize, false);

  console.log('[Office Generator V5.2] 場景初始化完成！');
}

// ============ 生成貼圖 ============

function generateTextures() {
  console.log('[Texture Generator] 生成高品質貼圖...');

  textures = {
    wood: {
      diffuse: createWoodTexture(1024, 1024),
      normal: createWoodNormalMap(1024, 1024),
    },
    fabric: {
      grey: createFabricTexture(512, 512, '#808080'),
      blue: createFabricTexture(512, 512, '#4169E1'),
      red: createFabricTexture(512, 512, '#DC143C'),
      green: createFabricTexture(512, 512, '#228B22'),
      normal: createFabricNormalMap(512, 512),
    },
    metal: {
      diffuse: createMetalTexture(512, 512, '#4A4A4A'),
      roughness: createMetalRoughnessMap(512, 512, 0.3),
    },
    environment: createEnvironmentTexture(),
  };
}

// ============ 創建辦公室 ============

function createOffice() {
  console.log('[Office Generator V5.2] 創建辦公室...');

  createFloor();
  createWalls();
  createCeiling();
  createWorkstations();
  createConferenceRoom(-7, -6);
  createLoungeArea(6, 5);
  createDecorations();

  console.log('[Office Generator V5.2] 辦公室創建完成！');
}

// ============ 地板（陰影接收）============

function createFloor() {
  const floorGeometry = new THREE.PlaneGeometry(20, 20);
  const floorMaterial = new THREE.MeshStandardMaterial({
    map: textures.wood.diffuse,
    normalMap: textures.wood.normal,
    roughness: 0.6,
    metalness: 0.1,
  });

  const floor = new THREE.Mesh(floorGeometry, floorMaterial);
  floor.rotation.x = -Math.PI / 2;
  floor.receiveShadow = true;
  scene.add(floor);
}

// ============ 牆面 ============

function createWalls() {
  const wallMaterial = new THREE.MeshStandardMaterial({
    color: 0xFFFFFF,
    roughness: 0.9,
    metalness: 0.0,
  });

  // 後牆
  const backWall = new THREE.Mesh(new THREE.PlaneGeometry(20, 2.8), wallMaterial);
  backWall.position.set(0, 1.4, -10);
  backWall.receiveShadow = true;
  scene.add(backWall);

  // 左牆
  const leftWall = new THREE.Mesh(new THREE.PlaneGeometry(20, 2.8), wallMaterial);
  leftWall.rotation.y = Math.PI / 2;
  leftWall.position.set(-10, 1.4, 0);
  leftWall.receiveShadow = true;
  scene.add(leftWall);
}

// ============ 天花板 ============

function createCeiling() {
  const ceiling = new THREE.Mesh(
    new THREE.PlaneGeometry(20, 20),
    new THREE.MeshStandardMaterial({ color: 0xFFFFFF, roughness: 0.9 })
  );
  ceiling.rotation.x = Math.PI / 2;
  ceiling.position.y = 2.8;
  scene.add(ceiling);
}

// ============ 5 個工作站（更多細節）============

function createWorkstations() {
  for (let i = 0; i < 5; i++) {
    createWorkstation(-6 + i * 3, 0, i + 1);
  }
}

function createWorkstation(x, z, index) {
  const group = new THREE.Group();
  group.position.set(x, 0, z);

  createDesk(group);
  createChair(group);
  createDualMonitors(group);
  createOfficeSupplies(group, index);
  createPersonalItems(group, index);

  scene.add(group);
}

// ============ 辦公桌（陰影投射）============

function createDesk(parent) {
  const topGeometry = new THREE.BoxGeometry(1.2, 0.025, 0.6);
  const topMaterial = new THREE.MeshStandardMaterial({
    map: textures.wood.diffuse,
    normalMap: textures.wood.normal,
    roughness: 0.4,
    metalness: 0.1,
  });

  const top = new THREE.Mesh(topGeometry, topMaterial);
  top.position.y = 0.75;
  top.castShadow = true;
  top.receiveShadow = true;
  parent.add(top);

  // 桌腿
  const legMaterial = new THREE.MeshStandardMaterial({
    map: textures.metal.diffuse,
    roughnessMap: textures.metal.roughness,
    metalness: 0.9,
  });

  const legPositions = [
    { x: -0.55, z: -0.25 },
    { x: -0.55, z: 0.25 },
    { x: 0.55, z: -0.25 },
    { x: 0.55, z: 0.25 },
  ];

  legPositions.forEach((pos, i) => {
    const leg = new THREE.Mesh(
      new THREE.CylinderGeometry(0.025, 0.025, 0.725, 8),
      legMaterial
    );
    leg.position.set(pos.x, 0.3625, pos.z);
    leg.castShadow = true;
    parent.add(leg);
  });
}

// ============ 辦公椅（布料紋理）============

function createChair(parent) {
  const chairGroup = new THREE.Group();
  chairGroup.position.set(0, 0, 0.8);

  const chairMaterial = new THREE.MeshStandardMaterial({
    map: textures.fabric.grey,
    normalMap: textures.fabric.normal,
    roughness: 0.7,
    metalness: 0.1,
  });

  // 座椅
  const seat = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.1, 0.5), chairMaterial);
  seat.position.y = 0.5;
  seat.castShadow = true;
  chairGroup.add(seat);

  // 椅背
  const back = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.6, 0.1), chairMaterial);
  back.position.set(0, 0.8, 0.2);
  back.castShadow = true;
  chairGroup.add(back);

  // 扶手
  const armMaterial = new THREE.MeshStandardMaterial({
    map: textures.metal.diffuse,
    metalness: 0.9,
  });

  const leftArm = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.2, 0.4), armMaterial);
  leftArm.position.set(-0.275, 0.6, 0);
  leftArm.castShadow = true;
  chairGroup.add(leftArm);

  const rightArm = leftArm.clone();
  rightArm.position.x = 0.275;
  chairGroup.add(rightArm);

  parent.add(chairGroup);
}

// ============ 雙螢幕（發光）============

function createDualMonitors(parent) {
  createMonitor(parent, -0.35, 0, -0.15);
  createMonitor(parent, 0.35, 0, -0.15);
}

function createMonitor(parent, offsetX, offsetY, offsetZ) {
  const monitorGroup = new THREE.Group();
  monitorGroup.position.set(offsetX, 1.15 + offsetY, -0.2 + offsetZ);
  monitorGroup.rotation.y = offsetX > 0 ? -0.2 : 0.2;

  // 外框
  const frame = new THREE.Mesh(
    new THREE.BoxGeometry(0.6, 0.4, 0.03),
    new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.3, metalness: 0.7 })
  );
  frame.castShadow = true;
  monitorGroup.add(frame);

  // 螢幕（發光）
  const screen = new THREE.Mesh(
    new THREE.PlaneGeometry(0.56, 0.36),
    new THREE.MeshStandardMaterial({
      color: 0x0077ff,
      emissive: 0x0077ff,
      emissiveIntensity: 0.3,  // 降低發光強度
    })
  );
  screen.position.z = 0.016;
  monitorGroup.add(screen);

  parent.add(monitorGroup);
}

// ============ 辦公用品 ============

function createOfficeSupplies(parent, index) {
  // 鍵盤
  const keyboard = new THREE.Mesh(
    new THREE.BoxGeometry(0.4, 0.02, 0.15),
    new THREE.MeshStandardMaterial({ color: 0x2a2a2a, roughness: 0.7 })
  );
  keyboard.position.set(0, 0.76, 0.1);
  keyboard.castShadow = true;
  parent.add(keyboard);

  // 滑鼠
  const mouse = new THREE.Mesh(
    new THREE.BoxGeometry(0.06, 0.02, 0.1),
    new THREE.MeshStandardMaterial({ color: 0x2a2a2a })
  );
  mouse.position.set(0.3, 0.76, 0.1);
  mouse.castShadow = true;
  parent.add(mouse);

  // 咖啡杯
  const cup = new THREE.Mesh(
    new THREE.CylinderGeometry(0.04, 0.035, 0.1, 16),
    new THREE.MeshStandardMaterial({ color: 0xFFFFFF, roughness: 0.2 })
  );
  cup.position.set(-0.4, 0.8, 0.1);
  cup.castShadow = true;
  parent.add(cup);

  // 咖啡（深色）
  const coffee = new THREE.Mesh(
    new THREE.CylinderGeometry(0.035, 0.035, 0.08, 16),
    new THREE.MeshStandardMaterial({ color: 0x3E2723, roughness: 0.1 })
  );
  coffee.position.set(-0.4, 0.81, 0.1);
  parent.add(coffee);
}

// ============ 個人物品（增加生活感）============

function createPersonalItems(parent, index) {
  // 檔案夾（不同顏色）
  const folderColors = [0xFFFFFF, 0x4169E1, 0xDC143C, 0x228B22, 0xFFD700];
  const folder = new THREE.Mesh(
    new THREE.BoxGeometry(0.05, 0.3, 0.2),
    new THREE.MeshStandardMaterial({
      map: textures.fabric[Object.keys(textures.fabric)[index % 5]],
      roughness: 0.8,
    })
  );
  folder.position.set(0.5, 0.9, -0.1);
  folder.rotation.z = 0.1;
  folder.castShadow = true;
  parent.add(folder);

  // 筆筒
  const penHolder = new THREE.Mesh(
    new THREE.CylinderGeometry(0.03, 0.03, 0.1, 12),
    new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.5 })
  );
  penHolder.position.set(0.45, 0.8, -0.15);
  penHolder.castShadow = true;
  parent.add(penHolder);

  // 筆（3支）
  const penColors = [0x0000FF, 0xFF0000, 0x000000];
  penColors.forEach((color, i) => {
    const pen = new THREE.Mesh(
      new THREE.CylinderGeometry(0.005, 0.005, 0.12, 8),
      new THREE.MeshStandardMaterial({ color })
    );
    pen.position.set(0.45 + i * 0.01, 0.87, -0.15);
    pen.rotation.x = 0.1;
    parent.add(pen);
  });

  // 書籍（1-2本）
  if (index % 2 === 0) {
    const book = new THREE.Mesh(
      new THREE.BoxGeometry(0.15, 0.02, 0.1),
      new THREE.MeshStandardMaterial({
        map: textures.fabric.blue,
        roughness: 0.8,
      })
    );
    book.position.set(-0.3, 0.77, -0.2);
    book.rotation.y = 0.3;
    book.castShadow = true;
    parent.add(book);
  }
}

// ============ 會議室（改進）============

function createConferenceRoom(centerX, centerZ) {
  const conferenceGroup = new THREE.Group();
  conferenceGroup.position.set(centerX, 0, centerZ);

  // 會議桌
  const table = new THREE.Mesh(
    new THREE.BoxGeometry(3, 0.05, 1.2),
    new THREE.MeshStandardMaterial({
      map: textures.wood.diffuse,
      normalMap: textures.wood.normal,
      roughness: 0.4,
    })
  );
  table.position.y = 0.75;
  table.castShadow = true;
  table.receiveShadow = true;
  conferenceGroup.add(table);

  // 桌腿
  const legMaterial = new THREE.MeshStandardMaterial({
    map: textures.metal.diffuse,
    roughnessMap: textures.metal.roughness,
    metalness: 0.9,
  });

  const legPositions = [
    { x: -1.3, z: -0.5 },
    { x: -1.3, z: 0.5 },
    { x: 1.3, z: -0.5 },
    { x: 1.3, z: 0.5 },
  ];

  legPositions.forEach((pos, i) => {
    const leg = new THREE.Mesh(
      new THREE.BoxGeometry(0.05, 0.75, 0.05),
      legMaterial
    );
    leg.position.set(pos.x, 0.375, pos.z);
    leg.castShadow = true;
    conferenceGroup.add(leg);
  });

  // 會議椅（6張）
  const chairPositions = [
    { x: -1, z: 0.8 },
    { x: 0, z: 0.8 },
    { x: 1, z: 0.8 },
    { x: -1, z: -0.8 },
    { x: 0, z: -0.8 },
    { x: 1, z: -0.8 },
  ];

  chairPositions.forEach((pos, i) => {
    createConferenceChair(conferenceGroup, pos.x, pos.z, i + 1);
  });

  // 白板
  const whiteboard = new THREE.Mesh(
    new THREE.BoxGeometry(2, 1.2, 0.05),
    new THREE.MeshStandardMaterial({
      map: textures.metal.diffuse,
      roughnessMap: textures.metal.roughness,
      metalness: 0.9,
    })
  );
  whiteboard.position.set(0, 1.5, -1.5);
  whiteboard.castShadow = true;
  conferenceGroup.add(whiteboard);

  // 白板表面
  const surface = new THREE.Mesh(
    new THREE.PlaneGeometry(1.9, 1.1),
    new THREE.MeshStandardMaterial({ color: 0xFFFFFF, roughness: 0.3 })
  );
  surface.position.set(0, 1.5, -1.474);
  conferenceGroup.add(surface);

  scene.add(conferenceGroup);
}

function createConferenceChair(parent, x, z, index) {
  const chairGroup = new THREE.Group();
  chairGroup.position.set(x, 0, z);

  const chairMaterial = new THREE.MeshStandardMaterial({
    map: textures.fabric.grey,
    normalMap: textures.fabric.normal,
    roughness: 0.7,
  });

  // 座椅
  const seat = new THREE.Mesh(new THREE.BoxGeometry(0.45, 0.08, 0.45), chairMaterial);
  seat.position.y = 0.45;
  seat.castShadow = true;
  chairGroup.add(seat);

  // 椅背
  const back = new THREE.Mesh(new THREE.BoxGeometry(0.45, 0.5, 0.08), chairMaterial);
  back.position.set(0, 0.7, -0.2);
  back.castShadow = true;
  chairGroup.add(back);

  parent.add(chairGroup);
}

// ============ 休息區（改進）============

function createLoungeArea(centerX, centerZ) {
  const loungeGroup = new THREE.Group();
  loungeGroup.position.set(centerX, 0, centerZ);

  // 沙發
  createSofa(loungeGroup, 0, 0);

  // 茶几
  createCoffeeTable(loungeGroup, 0, 1.5);

  // 地毯
  const rug = new THREE.Mesh(
    new THREE.PlaneGeometry(3, 2),
    new THREE.MeshStandardMaterial({ color: 0xD3D3D3, roughness: 0.95 })
  );
  rug.rotation.x = -Math.PI / 2;
  rug.position.set(0, 0.01, 0.5);
  rug.receiveShadow = true;
  loungeGroup.add(rug);

  // 植物裝飾
  createPlant(loungeGroup, 2, 0);
  createPlant(loungeGroup, -2, 0);

  scene.add(loungeGroup);
}

function createSofa(parent, x, z) {
  const sofaGroup = new THREE.Group();
  sofaGroup.position.set(x, 0, z);

  const sofaMaterial = new THREE.MeshStandardMaterial({
    map: textures.fabric.grey,
    normalMap: textures.fabric.normal,
    roughness: 0.9,
  });

  // 座椅
  const seat = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.4, 0.9), sofaMaterial);
  seat.position.y = 0.2;
  seat.castShadow = true;
  sofaGroup.add(seat);

  // 椅背
  const back = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.4, 0.2), sofaMaterial);
  back.position.set(0, 0.6, 0.35);
  back.castShadow = true;
  sofaGroup.add(back);

  // 扶手
  const leftArm = new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.6, 0.9), sofaMaterial);
  leftArm.position.set(-0.825, 0.4, 0);
  leftArm.castShadow = true;
  sofaGroup.add(leftArm);

  const rightArm = leftArm.clone();
  rightArm.position.x = 0.825;
  sofaGroup.add(rightArm);

  // 抱枕（藍色）
  const pillowMaterial = new THREE.MeshStandardMaterial({
    map: textures.fabric.blue,
    normalMap: textures.fabric.normal,
  });

  const pillow1 = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.3, 0.15), pillowMaterial);
  pillow1.position.set(-0.5, 0.6, 0.25);
  pillow1.castShadow = true;
  sofaGroup.add(pillow1);

  const pillow2 = pillow1.clone();
  pillow2.position.x = 0.5;
  sofaGroup.add(pillow2);

  parent.add(sofaGroup);
}

function createCoffeeTable(parent, x, z) {
  const tableGroup = new THREE.Group();
  tableGroup.position.set(x, 0, z);

  // 桌面
  const top = new THREE.Mesh(
    new THREE.BoxGeometry(1.0, 0.05, 0.6),
    new THREE.MeshStandardMaterial({
      map: textures.wood.diffuse,
      normalMap: textures.wood.normal,
      roughness: 0.4,
    })
  );
  top.position.y = 0.45;
  top.castShadow = true;
  top.receiveShadow = true;
  tableGroup.add(top);

  // 桌腿
  const legMaterial = new THREE.MeshStandardMaterial({
    map: textures.metal.diffuse,
    metalness: 0.9,
  });

  const legPositions = [
    { x: -0.4, z: -0.25 },
    { x: -0.4, z: 0.25 },
    { x: 0.4, z: -0.25 },
    { x: 0.4, z: 0.25 },
  ];

  legPositions.forEach((pos, i) => {
    const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.45, 8), legMaterial);
    leg.position.set(pos.x, 0.225, pos.z);
    leg.castShadow = true;
    tableGroup.add(leg);
  });

  // 茶杯（茶几上）
  const teaCup = new THREE.Mesh(
    new THREE.CylinderGeometry(0.03, 0.025, 0.08, 12),
    new THREE.MeshStandardMaterial({ color: 0xFFFFFF, roughness: 0.2 })
  );
  teaCup.position.set(0, 0.49, 0);
  teaCup.castShadow = true;
  tableGroup.add(teaCup);

  // 雜誌
  const magazine = new THREE.Mesh(
    new THREE.BoxGeometry(0.3, 0.01, 0.2),
    new THREE.MeshStandardMaterial({ color: 0xFFFFFF, roughness: 0.8 })
  );
  magazine.position.set(0.2, 0.48, 0.1);
  magazine.rotation.y = 0.3;
  magazine.castShadow = true;
  tableGroup.add(magazine);

  parent.add(tableGroup);
}

function createPlant(parent, x, z) {
  const plantGroup = new THREE.Group();
  plantGroup.position.set(x, 0, z);

  // 花盆
  const pot = new THREE.Mesh(
    new THREE.CylinderGeometry(0.15, 0.12, 0.3, 12),
    new THREE.MeshStandardMaterial({ color: 0xFFFFFF, roughness: 0.2 })
  );
  pot.position.y = 0.15;
  pot.castShadow = true;
  plantGroup.add(pot);

  // 植物
  const plant = new THREE.Mesh(
    new THREE.SphereGeometry(0.2, 12, 12),
    new THREE.MeshStandardMaterial({ color: 0x228B22, roughness: 0.8 })
  );
  plant.position.y = 0.5;
  plant.scale.y = 1.2;
  plant.castShadow = true;
  plantGroup.add(plant);

  parent.add(plantGroup);
}

// ============ 裝飾品（增加細節）============

function createDecorations() {
  // 牆面掛畫
  createPainting(-5, 1.5, -9.95);
  createPainting(5, 1.5, -9.95);

  // 角落植物
  createLargePlant(-9, -9);
  createLargePlant(9, -9);

  // 時鐘
  createClock(0, 2.0, -9.95);
}

function createPainting(x, y, z) {
  const frame = new THREE.Mesh(
    new THREE.BoxGeometry(1.0, 0.8, 0.05),
    new THREE.MeshStandardMaterial({
      map: textures.metal.diffuse,
      roughnessMap: textures.metal.roughness,
      metalness: 0.9,
    })
  );
  frame.position.set(x, y, z);
  frame.castShadow = true;
  scene.add(frame);

  const canvas = new THREE.Mesh(
    new THREE.PlaneGeometry(0.9, 0.7),
    new THREE.MeshStandardMaterial({ color: 0x87CEEB, roughness: 0.5 })
  );
  canvas.position.set(x, y, z + 0.026);
  scene.add(canvas);
}

function createLargePlant(x, z) {
  const plantGroup = new THREE.Group();
  plantGroup.position.set(x, 0, z);

  // 花盆
  const pot = new THREE.Mesh(
    new THREE.CylinderGeometry(0.3, 0.25, 0.5, 16),
    new THREE.MeshStandardMaterial({ color: 0xFFFFFF, roughness: 0.2 })
  );
  pot.position.y = 0.25;
  pot.castShadow = true;
  plantGroup.add(pot);

  // 樹幹
  const trunk = new THREE.Mesh(
    new THREE.CylinderGeometry(0.05, 0.08, 1.5, 8),
    new THREE.MeshStandardMaterial({ color: 0x8B4513, roughness: 0.9 })
  );
  trunk.position.y = 1.25;
  trunk.castShadow = true;
  plantGroup.add(trunk);

  // 葉子
  const leaf = new THREE.Mesh(
    new THREE.SphereGeometry(0.6, 16, 16),
    new THREE.MeshStandardMaterial({ color: 0x228B22, roughness: 0.8 })
  );
  leaf.position.y = 2.2;
  leaf.scale.y = 1.5;
  leaf.castShadow = true;
  plantGroup.add(leaf);

  scene.add(plantGroup);
}

function createClock(x, y, z) {
  const clockGroup = new THREE.Group();
  clockGroup.position.set(x, y, z);

  // 外框
  const frame = new THREE.Mesh(
    new THREE.CylinderGeometry(0.3, 0.3, 0.05, 24),
    new THREE.MeshStandardMaterial({
      map: textures.metal.diffuse,
      metalness: 0.9,
    })
  );
  frame.rotation.x = Math.PI / 2;
  frame.castShadow = true;
  clockGroup.add(frame);

  // 鐘面
  const face = new THREE.Mesh(
    new THREE.CircleGeometry(0.28, 24),
    new THREE.MeshStandardMaterial({ color: 0xFFFFFF, roughness: 0.3 })
  );
  face.position.z = 0.026;
  clockGroup.add(face);

  scene.add(clockGroup);
}

// ============ 燈光系統（V5.1 低光照）============

function setupLighting() {
  // 環境光（降低）
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.2);  // 0.3 → 0.2
  scene.add(ambientLight);

  // 半球光（降低）
  const hemiLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.15);  // 0.5 → 0.15
  hemiLight.position.set(0, 20, 0);
  scene.add(hemiLight);

  // 主光源（降低）
  const mainLight = new THREE.DirectionalLight(0xffffff, 0.3);  // 1.2 → 0.3
  mainLight.position.set(10, 15, 10);
  mainLight.castShadow = true;
  mainLight.shadow.mapSize.width = 2048;
  mainLight.shadow.mapSize.height = 2048;
  mainLight.shadow.camera.near = 0.5;
  mainLight.shadow.camera.far = 50;
  mainLight.shadow.camera.left = -20;
  mainLight.shadow.camera.right = 20;
  mainLight.shadow.camera.top = 20;
  mainLight.shadow.camera.bottom = -20;
  mainLight.shadow.bias = -0.0001;
  scene.add(mainLight);

  // 補光（降低）
  const fillLight = new THREE.DirectionalLight(0xffffff, 0.1);  // 0.4 → 0.1
  fillLight.position.set(-10, 10, -10);
  scene.add(fillLight);

  // 應用環境貼圖
  scene.environment = textures.environment;

  console.log('[Office Generator V5.2] 燈光設置完成（低曝光）');
}

// ============ 後處理（移除）============

// function setupPostProcessing() {
//   composer = new EffectComposer(renderer);
//   const renderPass = new RenderPass(scene, camera);
//   composer.addPass(renderPass);
//   const bloomPass = new UnrealBloomPass(
//     new THREE.Vector2(window.innerWidth, window.innerHeight),
//     0.4,
//     0.4,
//     0.85
//   );
//   composer.addPass(bloomPass);
// }

// ============ 動畫循環 ============

function animate() {
  requestAnimationFrame(animate);

  controls.update();
  renderer.render(scene, camera);  // 直接渲染，不使用 composer
}

// ============ 視窗大小調整 ============

function onWindowResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}

// ============ 啟動 ============

init();
animate();

console.log('[Office Generator V5.2] 辦公室場景生成完成！');
console.log('[Office Generator V5.2] 改進項目：');
console.log('  ✅ 保留 V5 所有細節');
console.log('  ✅ V5.1 低曝光設定');
console.log('  ✅ 移除 Bloom 後處理');
console.log('  ✅ 降低所有光源強度');
