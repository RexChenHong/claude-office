/**
 * Claude Office - V5.1（修復曝光問題）
 * 大幅降低光照強度
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
  console.log('[Office Generator V5.1] 初始化場景（降低曝光）...');

  // 創建場景
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xD0D0D0);  // 降低背景亮度

  // 創建相機
  camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.set(15, 12, 15);
  camera.lookAt(0, 0, 0);

  // 創建渲染器（大幅降低曝光）
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.5;  // 大幅降低（0.8 → 0.5）
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.physicallyCorrectLights = false;  // 關閉物理正確光照
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

  // 設置燈光（大幅降低）
  setupLighting();

  // 設置後處理（移除 Bloom）
  // setupPostProcessing();

  // 監聽視窗大小變化
  window.addEventListener('resize', onWindowResize, false);

  console.log('[Office Generator V5.1] 場景初始化完成！');
}

// ============ 生成貼圖 ============

function generateTextures() {
  console.log('[Texture Generator] 生成貼圖...');

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
  };
}

// ============ 創建辦公室（簡化版）============

function createOffice() {
  console.log('[Office Generator V5.1] 創建辦公室...');

  createFloor();
  createWalls();
  createWorkstations();
  createLoungeArea(6, 5);

  console.log('[Office Generator V5.1] 辦公室創建完成！');
}

// ============ 地板 ============

function createFloor() {
  const floor = new THREE.Mesh(
    new THREE.PlaneGeometry(20, 20),
    new THREE.MeshStandardMaterial({
      map: textures.wood.diffuse,
      normalMap: textures.wood.normal,
      roughness: 0.6,
      metalness: 0.1,
    })
  );
  floor.rotation.x = -Math.PI / 2;
  floor.receiveShadow = true;
  scene.add(floor);
}

// ============ 牆面 ============

function createWalls() {
  const wallMaterial = new THREE.MeshStandardMaterial({
    color: 0xF5F5F5,  // 降低亮度
    roughness: 0.9,
    metalness: 0.0,
  });

  const backWall = new THREE.Mesh(new THREE.PlaneGeometry(20, 2.8), wallMaterial);
  backWall.position.set(0, 1.4, -10);
  backWall.receiveShadow = true;
  scene.add(backWall);

  const leftWall = new THREE.Mesh(new THREE.PlaneGeometry(20, 2.8), wallMaterial);
  leftWall.rotation.y = Math.PI / 2;
  leftWall.position.set(-10, 1.4, 0);
  leftWall.receiveShadow = true;
  scene.add(leftWall);
}

// ============ 5 個工作站 ============

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
  createMonitor(group);

  scene.add(group);
}

// ============ 辦公桌 ============

function createDesk(parent) {
  const top = new THREE.Mesh(
    new THREE.BoxGeometry(1.2, 0.025, 0.6),
    new THREE.MeshStandardMaterial({
      map: textures.wood.diffuse,
      normalMap: textures.wood.normal,
      roughness: 0.4,
      metalness: 0.1,
    })
  );
  top.position.y = 0.75;
  top.castShadow = true;
  top.receiveShadow = true;
  parent.add(top);

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

// ============ 辦公椅 ============

function createChair(parent) {
  const chairGroup = new THREE.Group();
  chairGroup.position.set(0, 0, 0.8);

  const chairMaterial = new THREE.MeshStandardMaterial({
    map: textures.fabric.grey,
    normalMap: textures.fabric.normal,
    roughness: 0.7,
    metalness: 0.1,
  });

  const seat = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.1, 0.5), chairMaterial);
  seat.position.y = 0.5;
  seat.castShadow = true;
  chairGroup.add(seat);

  const back = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.6, 0.1), chairMaterial);
  back.position.set(0, 0.8, 0.2);
  back.castShadow = true;
  chairGroup.add(back);

  parent.add(chairGroup);
}

// ============ 螢幕 ============

function createMonitor(parent) {
  const monitorGroup = new THREE.Group();
  monitorGroup.position.set(0, 1.15, -0.2);

  const frame = new THREE.Mesh(
    new THREE.BoxGeometry(0.6, 0.4, 0.03),
    new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.3, metalness: 0.7 })
  );
  frame.castShadow = true;
  monitorGroup.add(frame);

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

// ============ 休息區 ============

function createLoungeArea(centerX, centerZ) {
  const loungeGroup = new THREE.Group();
  loungeGroup.position.set(centerX, 0, centerZ);

  createSofa(loungeGroup, 0, 0);
  createCoffeeTable(loungeGroup, 0, 1.5);

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

  const seat = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.4, 0.9), sofaMaterial);
  seat.position.y = 0.2;
  seat.castShadow = true;
  sofaGroup.add(seat);

  const back = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.4, 0.2), sofaMaterial);
  back.position.set(0, 0.6, 0.35);
  back.castShadow = true;
  sofaGroup.add(back);

  parent.add(sofaGroup);
}

function createCoffeeTable(parent, x, z) {
  const tableGroup = new THREE.Group();
  tableGroup.position.set(x, 0, z);

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

  parent.add(tableGroup);
}

// ============ 燈光系統（大幅降低）============

function setupLighting() {
  // 環境光（大幅降低）
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.2);  // 0.3 → 0.2
  scene.add(ambientLight);

  // 半球光（大幅降低）
  const hemiLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.15);  // 0.5 → 0.15
  hemiLight.position.set(0, 20, 0);
  scene.add(hemiLight);

  // 主光源（大幅降低）
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

  // 補光（大幅降低）
  const fillLight = new THREE.DirectionalLight(0xffffff, 0.1);  // 0.4 → 0.1
  fillLight.position.set(-10, 10, -10);
  scene.add(fillLight);

  // 應用環境貼圖
  scene.environment = textures.environment;

  console.log('[Office Generator V5.1] 燈光設置完成（大幅降低）');
}

// ============ 動畫循環 ============

function animate() {
  requestAnimationFrame(animate);

  controls.update();
  renderer.render(scene, camera);
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

console.log('[Office Generator V5.1] 辦公室場景生成完成！');
console.log('[Office Generator V5.1] 改進：大幅降低曝光');
