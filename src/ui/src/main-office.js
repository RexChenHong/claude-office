/**
 * Claude Office - 程序化辦公室場景生成器
 * 根據 OFFICE_SPEC.md 規格書生成
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// ============ 全局變量 ============

let scene, camera, renderer, controls;
let clock;

// ============ 辦公室規格（基於 OFFICE_SPEC.md）============

const OFFICE_SPEC = {
  floor: {
    width: 20,
    depth: 20,
    color: 0xD2691E, // 淺木色
  },
  wall: {
    height: 3,
    color: 0xF5F5F5, // 淺灰色
  },
  desk: {
    width: 1.2,
    height: 0.75,
    depth: 0.6,
    topThickness: 0.025,
    legDiameter: 0.05,
    color: {
      top: 0xFAFAFA, // 白色
      leg: 0x4A4A4A, // 深灰色
    },
  },
  chair: {
    seatWidth: 0.5,
    seatHeight: 0.5,
    seatDepth: 0.5,
    backHeight: 0.6,
    color: 0x2F4F4F, // 深灰色
  },
  monitor: {
    width: 0.6,
    height: 0.4,
    color: 0x1a1a1a,
    screenColor: 0x0077ff,
  },
};

// ============ 初始化場景 ============

function init() {
  console.log('[Office Generator] 初始化場景...');

  // 創建場景
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x87CEEB); // 天空藍

  // 創建相機
  camera = new THREE.PerspectiveCamera(
    60,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
  );
  camera.position.set(10, 8, 10);
  camera.lookAt(0, 0, 0);

  // 創建渲染器
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;
  document.getElementById('game-container').appendChild(renderer.domElement);

  // 添加控制器
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.target.set(0, 0, 0);

  // 時鐘
  clock = new THREE.Clock();

  // 創建辦公室
  createOffice();

  // 設置燈光
  setupLighting();

  // 監聽視窗大小變化
  window.addEventListener('resize', onWindowResize, false);

  console.log('[Office Generator] 場景初始化完成！');
}

// ============ 創建辦公室 ============

function createOffice() {
  console.log('[Office Generator] 創建辦公室...');

  // 創建地板
  createFloor();

  // 創建牆面
  createWalls();

  // 創建工作站（多個）
  createWorkstations();

  console.log('[Office Generator] 辦公室創建完成！');
}

// ============ 地板 ============

function createFloor() {
  const { width, depth, color } = OFFICE_SPEC.floor;

  // 地板
  const floorGeometry = new THREE.PlaneGeometry(width, depth);
  const floorMaterial = new THREE.MeshStandardMaterial({
    color: color,
    roughness: 0.8,
    metalness: 0.0,
  });
  const floor = new THREE.Mesh(floorGeometry, floorMaterial);
  floor.rotation.x = -Math.PI / 2;
  floor.receiveShadow = true;
  floor.name = 'Floor';
  scene.add(floor);

  // 地板條紋
  const stripeCount = Math.floor(width / 0.8);
  for (let i = 0; i <= stripeCount; i++) {
    const stripeGeometry = new THREE.PlaneGeometry(0.02, depth);
    const stripeMaterial = new THREE.MeshStandardMaterial({
      color: 0xA0522D,
      roughness: 0.8,
    });
    const stripe = new THREE.Mesh(stripeGeometry, stripeMaterial);
    stripe.rotation.x = -Math.PI / 2;
    stripe.position.set(-width / 2 + i * 0.8, 0.001, 0);
    stripe.name = `FloorStripe_${i}`;
    scene.add(stripe);
  }

  console.log('[Office Generator] 地板創建完成');
}

// ============ 牆面 ============

function createWalls() {
  const { width, depth } = OFFICE_SPEC.floor;
  const { height, color } = OFFICE_SPEC.wall;

  // 後牆
  const backWallGeometry = new THREE.PlaneGeometry(width, height);
  const wallMaterial = new THREE.MeshStandardMaterial({
    color: color,
    roughness: 0.9,
    metalness: 0.0,
    side: THREE.DoubleSide,
  });
  const backWall = new THREE.Mesh(backWallGeometry, wallMaterial);
  backWall.position.set(0, height / 2, -depth / 2);
  backWall.receiveShadow = true;
  backWall.name = 'BackWall';
  scene.add(backWall);

  // 左牆
  const leftWallGeometry = new THREE.PlaneGeometry(depth, height);
  const leftWall = new THREE.Mesh(leftWallGeometry, wallMaterial);
  leftWall.rotation.y = Math.PI / 2;
  leftWall.position.set(-width / 2, height / 2, 0);
  leftWall.receiveShadow = true;
  leftWall.name = 'LeftWall';
  scene.add(leftWall);

  // 踢腳板
  const baseboardHeight = 0.1;
  const baseboardMaterial = new THREE.MeshStandardMaterial({
    color: 0xFFFFFF,
    roughness: 0.5,
  });

  // 後牆踢腳板
  const backBaseboard = new THREE.Mesh(
    new THREE.BoxGeometry(width, baseboardHeight, 0.02),
    baseboardMaterial
  );
  backBaseboard.position.set(0, baseboardHeight / 2, -depth / 2 + 0.01);
  backBaseboard.name = 'BackBaseboard';
  scene.add(backBaseboard);

  // 左牆踢腳板
  const leftBaseboard = new THREE.Mesh(
    new THREE.BoxGeometry(0.02, baseboardHeight, depth),
    baseboardMaterial
  );
  leftBaseboard.position.set(-width / 2 + 0.01, baseboardHeight / 2, 0);
  leftBaseboard.name = 'LeftBaseboard';
  scene.add(leftBaseboard);

  console.log('[Office Generator] 牆面創建完成');
}

// ============ 工作站 ============

function createWorkstations() {
  const positions = [
    { x: -4, z: -2 },
    { x: -4, z: 2 },
    { x: 0, z: -2 },
    { x: 0, z: 2 },
    { x: 4, z: -2 },
    { x: 4, z: 2 },
  ];

  positions.forEach((pos, index) => {
    createWorkstation(pos.x, pos.z, index + 1);
  });

  console.log(`[Office Generator] 創建了 ${positions.length} 個工作站`);
}

function createWorkstation(x, z, index) {
  const group = new THREE.Group();
  group.name = `Workstation_${index}`;
  group.position.set(x, 0, z);

  // 辦公桌
  createDesk(group);

  // 辦公椅
  createChair(group);

  // 電腦螢幕
  createMonitor(group);

  scene.add(group);
}

// ============ 辦公桌 ============

function createDesk(parent) {
  const { width, height, depth, topThickness, legDiameter, color } = OFFICE_SPEC.desk;

  // 桌面
  const topGeometry = new THREE.BoxGeometry(width, topThickness, depth);
  const topMaterial = new THREE.MeshStandardMaterial({
    color: color.top,
    roughness: 0.6,
    metalness: 0.1,
  });
  const top = new THREE.Mesh(topGeometry, topMaterial);
  top.position.y = height;
  top.castShadow = true;
  top.receiveShadow = true;
  top.name = 'DeskTop';
  parent.add(top);

  // 桌腿
  const legMaterial = new THREE.MeshStandardMaterial({
    color: color.leg,
    roughness: 0.3,
    metalness: 0.8,
  });

  const legPositions = [
    { x: -width / 2 + legDiameter, z: -depth / 2 + legDiameter },
    { x: -width / 2 + legDiameter, z: depth / 2 - legDiameter },
    { x: width / 2 - legDiameter, z: -depth / 2 + legDiameter },
    { x: width / 2 - legDiameter, z: depth / 2 - legDiameter },
  ];

  legPositions.forEach((pos, i) => {
    const legGeometry = new THREE.CylinderGeometry(
      legDiameter / 2,
      legDiameter / 2,
      height - topThickness,
      16
    );
    const leg = new THREE.Mesh(legGeometry, legMaterial);
    leg.position.set(pos.x, (height - topThickness) / 2, pos.z);
    leg.castShadow = true;
    leg.name = `DeskLeg_${i + 1}`;
    parent.add(leg);
  });
}

// ============ 辦公椅 ============

function createChair(parent) {
  const { seatWidth, seatHeight, seatDepth, backHeight, color } = OFFICE_SPEC.chair;
  const chairGroup = new THREE.Group();
  chairGroup.name = 'Chair';
  chairGroup.position.set(0, 0, 0.8);

  // 座椅
  const seatGeometry = new THREE.BoxGeometry(seatWidth, 0.1, seatDepth);
  const chairMaterial = new THREE.MeshStandardMaterial({
    color: color,
    roughness: 0.8,
    metalness: 0.1,
  });
  const seat = new THREE.Mesh(seatGeometry, chairMaterial);
  seat.position.y = seatHeight;
  seat.castShadow = true;
  seat.name = 'ChairSeat';
  chairGroup.add(seat);

  // 椅背
  const backGeometry = new THREE.BoxGeometry(seatWidth, backHeight, 0.1);
  const back = new THREE.Mesh(backGeometry, chairMaterial);
  back.position.set(0, seatHeight + backHeight / 2, seatDepth / 2 - 0.05);
  back.castShadow = true;
  back.name = 'ChairBack';
  chairGroup.add(back);

  // 椅腿（簡化版）
  const legMaterial = new THREE.MeshStandardMaterial({
    color: 0x888888,
    roughness: 0.3,
    metalness: 0.8,
  });

  const legGeometry = new THREE.CylinderGeometry(0.02, 0.02, seatHeight, 8);
  const centerLeg = new THREE.Mesh(legGeometry, legMaterial);
  centerLeg.position.y = seatHeight / 2;
  centerLeg.name = 'ChairLeg';
  chairGroup.add(centerLeg);

  // 滾輪（簡化版）
  const wheelGeometry = new THREE.SphereGeometry(0.03, 8, 8);
  const wheelPositions = [
    { x: 0.15, z: 0.15 },
    { x: -0.15, z: 0.15 },
    { x: 0.15, z: -0.15 },
    { x: -0.15, z: -0.15 },
  ];

  wheelPositions.forEach((pos, i) => {
    const wheel = new THREE.Mesh(wheelGeometry, legMaterial);
    wheel.position.set(pos.x, 0.03, pos.z);
    wheel.name = `ChairWheel_${i + 1}`;
    chairGroup.add(wheel);
  });

  parent.add(chairGroup);
}

// ============ 電腦螢幕 ============

function createMonitor(parent) {
  const { width, height, color, screenColor } = OFFICE_SPEC.monitor;
  const monitorGroup = new THREE.Group();
  monitorGroup.name = 'Monitor';
  monitorGroup.position.set(0, 0.75 + 0.4, -0.2);

  // 螢幕外框
  const frameGeometry = new THREE.BoxGeometry(width, height, 0.03);
  const frameMaterial = new THREE.MeshStandardMaterial({
    color: color,
    roughness: 0.5,
    metalness: 0.5,
  });
  const frame = new THREE.Mesh(frameGeometry, frameMaterial);
  frame.castShadow = true;
  frame.name = 'MonitorFrame';
  monitorGroup.add(frame);

  // 螢幕（發光）
  const screenGeometry = new THREE.PlaneGeometry(width - 0.04, height - 0.04);
  const screenMaterial = new THREE.MeshStandardMaterial({
    color: screenColor,
    emissive: screenColor,
    emissiveIntensity: 0.5,
    roughness: 0.1,
    metalness: 0.0,
  });
  const screen = new THREE.Mesh(screenGeometry, screenMaterial);
  screen.position.z = 0.016;
  screen.name = 'MonitorScreen';
  monitorGroup.add(screen);

  // 支架
  const standGeometry = new THREE.BoxGeometry(0.05, 0.15, 0.05);
  const standMaterial = new THREE.MeshStandardMaterial({
    color: color,
    roughness: 0.5,
    metalness: 0.5,
  });
  const stand = new THREE.Mesh(standGeometry, standMaterial);
  stand.position.y = -height / 2 - 0.075;
  stand.name = 'MonitorStand';
  monitorGroup.add(stand);

  // 底座
  const baseGeometry = new THREE.BoxGeometry(0.2, 0.02, 0.15);
  const base = new THREE.Mesh(baseGeometry, standMaterial);
  base.position.y = -height / 2 - 0.16;
  base.name = 'MonitorBase';
  monitorGroup.add(base);

  parent.add(monitorGroup);
}

// ============ 燈光系統 ============

function setupLighting() {
  // 環境光
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
  ambientLight.name = 'AmbientLight';
  scene.add(ambientLight);

  // 主光源（模擬窗戶光）
  const mainLight = new THREE.DirectionalLight(0xffffff, 0.8);
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
  mainLight.name = 'MainLight';
  scene.add(mainLight);

  // 補光
  const fillLight = new THREE.DirectionalLight(0xffffff, 0.3);
  fillLight.position.set(-10, 10, -10);
  fillLight.name = 'FillLight';
  scene.add(fillLight);

  console.log('[Office Generator] 燈光系統設置完成');
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

console.log('[Office Generator] 辦公室場景生成完成！');
console.log('[Office Generator] 測試地址：http://100.113.156.108:8055/');
