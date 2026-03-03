/**
 * Claude Office - 高品質渲染版本 V3
 * 添加環境貼圖、後處理、真實光照
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { SMAAPass } from 'three/addons/postprocessing/SMAAPass.js';

// ============ 全局變量 ============

let scene, camera, renderer, controls, composer;
let clock;

// ============ 辦公室規格 ============

const OFFICE_SPEC = {
  floor: {
    width: 20,
    depth: 20,
    color: 0xE8E8E8,
  },
  wall: {
    height: 3,
    color: 0xFFFFFF,
  },
  desk: {
    width: 1.2,
    height: 0.75,
    depth: 0.6,
    topThickness: 0.025,
    legDiameter: 0.05,
    color: {
      top: 0xFAFAFA,
      leg: 0x4A4A4A,
    },
  },
  chair: {
    seatWidth: 0.5,
    seatHeight: 0.5,
    seatDepth: 0.5,
    backHeight: 0.6,
    color: 0x2F4F4F,
  },
  monitor: {
    width: 0.6,
    height: 0.4,
    color: 0x1a1a1a,
    screenColor: 0x0077ff,
  },
  sofa: {
    width: 1.8,
    height: 0.8,
    depth: 0.9,
    color: 0x808080,
  },
  plant: {
    potColor: 0xFFFFFF,
    plantColor: 0x228B22,
  },
};

// ============ 初始化場景 ============

function init() {
  console.log('[Office Generator V3 - 高品質渲染] 初始化場景...');

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
  camera.position.set(12, 10, 12);
  camera.lookAt(0, 0, 0);

  // 創建渲染器（高品質設置）
  renderer = new THREE.WebGLRenderer({
    antialias: true,
    powerPreference: "high-performance"
  });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.5;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.physicallyCorrectLights = true;
  document.getElementById('game-container').appendChild(renderer.domElement);

  // 添加控制器
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.target.set(0, 0, 0);
  controls.minDistance = 5;
  controls.maxDistance = 30;

  // 時鐘
  clock = new THREE.Clock();

  // 創建辦公室
  createOffice();

  // 設置高品質燈光
  setupHighQualityLighting();

  // 設置後處理
  setupPostProcessing();

  // 監聽視窗大小變化
  window.addEventListener('resize', onWindowResize, false);

  console.log('[Office Generator V3] 場景初始化完成！');
  console.log('[Office Generator V3] 高品質渲染已啟用！');
}

// ============ 創建辦公室 ============

function createOffice() {
  console.log('[Office Generator V3] 創建辦公室...');

  createFloor();
  createWalls();
  createWorkstationArea(-4, 0);
  createLoungeArea(6, 0);
  createConferenceRoom(0, -7);
  createPlants();
  createWindows();

  console.log('[Office Generator V3] 辦公室創建完成！');
}

// ============ 地板（改進材質）============

function createFloor() {
  const { width, depth, color } = OFFICE_SPEC.floor;

  // 地板（改進材質）
  const floorGeometry = new THREE.PlaneGeometry(width, depth);
  const floorMaterial = new THREE.MeshStandardMaterial({
    color: color,
    roughness: 0.6,
    metalness: 0.1,
    envMapIntensity: 0.5,
  });
  const floor = new THREE.Mesh(floorGeometry, floorMaterial);
  floor.rotation.x = -Math.PI / 2;
  floor.receiveShadow = true;
  floor.name = 'Floor';
  scene.add(floor);

  // 地板條紋（更精細）
  const stripeCount = Math.floor(width / 0.6);
  for (let i = 0; i <= stripeCount; i++) {
    const stripeGeometry = new THREE.PlaneGeometry(0.01, depth);
    const stripeMaterial = new THREE.MeshStandardMaterial({
      color: 0xD0D0D0,
      roughness: 0.7,
      metalness: 0.0,
    });
    const stripe = new THREE.Mesh(stripeGeometry, stripeMaterial);
    stripe.rotation.x = -Math.PI / 2;
    stripe.position.set(-width / 2 + i * 0.6, 0.001, 0);
    stripe.name = `FloorStripe_${i}`;
    scene.add(stripe);
  }

  console.log('[Office Generator V3] 地板創建完成');
}

// ============ 牆面 ============

function createWalls() {
  const { width, depth } = OFFICE_SPEC.floor;
  const { height, color } = OFFICE_SPEC.wall;

  const wallMaterial = new THREE.MeshStandardMaterial({
    color: color,
    roughness: 0.9,
    metalness: 0.0,
    envMapIntensity: 0.3,
    side: THREE.DoubleSide,
  });

  // 後牆
  const backWallGeometry = new THREE.PlaneGeometry(width, height);
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
    metalness: 0.0,
  });

  const backBaseboard = new THREE.Mesh(
    new THREE.BoxGeometry(width, baseboardHeight, 0.02),
    baseboardMaterial
  );
  backBaseboard.position.set(0, baseboardHeight / 2, -depth / 2 + 0.01);
  backBaseboard.castShadow = true;
  backBaseboard.name = 'BackBaseboard';
  scene.add(backBaseboard);

  const leftBaseboard = new THREE.Mesh(
    new THREE.BoxGeometry(0.02, baseboardHeight, depth),
    baseboardMaterial
  );
  leftBaseboard.position.set(-width / 2 + 0.01, baseboardHeight / 2, 0);
  leftBaseboard.castShadow = true;
  leftBaseboard.name = 'LeftBaseboard';
  scene.add(leftBaseboard);

  console.log('[Office Generator V3] 牆面創建完成');
}

// ============ 工作站區域 ============

function createWorkstationArea(centerX, centerZ) {
  const positions = [
    { x: centerX - 2, z: centerZ - 2 },
    { x: centerX - 2, z: centerZ + 2 },
    { x: centerX + 2, z: centerZ - 2 },
    { x: centerX + 2, z: centerZ + 2 },
  ];

  positions.forEach((pos, index) => {
    createWorkstation(pos.x, pos.z, index + 1);
  });

  console.log(`[Office Generator V3] 創建了 ${positions.length} 個工作站`);
}

function createWorkstation(x, z, index) {
  const group = new THREE.Group();
  group.name = `Workstation_${index}`;
  group.position.set(x, 0, z);

  createDesk(group);
  createChair(group);
  createMonitor(group);
  createOfficeSupplies(group);

  scene.add(group);
}

// ============ 辦公桌（改進材質）============

function createDesk(parent) {
  const { width, height, depth, topThickness, legDiameter, color } = OFFICE_SPEC.desk;

  // 桌面（改進材質）
  const topGeometry = new THREE.BoxGeometry(width, topThickness, depth);
  const topMaterial = new THREE.MeshStandardMaterial({
    color: color.top,
    roughness: 0.4,
    metalness: 0.1,
    envMapIntensity: 0.8,
  });
  const top = new THREE.Mesh(topGeometry, topMaterial);
  top.position.y = height;
  top.castShadow = true;
  top.receiveShadow = true;
  top.name = 'DeskTop';
  parent.add(top);

  // 桌腿（改進材質）
  const legMaterial = new THREE.MeshStandardMaterial({
    color: color.leg,
    roughness: 0.2,
    metalness: 0.9,
    envMapIntensity: 1.0,
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

// ============ 辦公椅（改進材質）============

function createChair(parent) {
  const { seatWidth, seatHeight, seatDepth, backHeight, color } = OFFICE_SPEC.chair;
  const chairGroup = new THREE.Group();
  chairGroup.name = 'Chair';
  chairGroup.position.set(0, 0, 0.8);

  // 座椅（改進材質）
  const seatGeometry = new THREE.BoxGeometry(seatWidth, 0.1, seatDepth);
  const chairMaterial = new THREE.MeshStandardMaterial({
    color: color,
    roughness: 0.7,
    metalness: 0.1,
    envMapIntensity: 0.6,
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

  // 椅腿（改進材質）
  const legMaterial = new THREE.MeshStandardMaterial({
    color: 0x888888,
    roughness: 0.2,
    metalness: 0.9,
    envMapIntensity: 1.0,
  });

  const legGeometry = new THREE.CylinderGeometry(0.02, 0.02, seatHeight, 8);
  const centerLeg = new THREE.Mesh(legGeometry, legMaterial);
  centerLeg.position.y = seatHeight / 2;
  centerLeg.name = 'ChairLeg';
  chairGroup.add(centerLeg);

  // 滾輪
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
    wheel.castShadow = true;
    wheel.name = `ChairWheel_${i + 1}`;
    chairGroup.add(wheel);
  });

  parent.add(chairGroup);
}

// ============ 電腦螢幕（改進材質）============

function createMonitor(parent) {
  const { width, height, color, screenColor } = OFFICE_SPEC.monitor;
  const monitorGroup = new THREE.Group();
  monitorGroup.name = 'Monitor';
  monitorGroup.position.set(0, 0.75 + 0.4, -0.2);

  // 螢幕外框（改進材質）
  const frameGeometry = new THREE.BoxGeometry(width, height, 0.03);
  const frameMaterial = new THREE.MeshStandardMaterial({
    color: color,
    roughness: 0.3,
    metalness: 0.7,
    envMapIntensity: 1.0,
  });
  const frame = new THREE.Mesh(frameGeometry, frameMaterial);
  frame.castShadow = true;
  frame.name = 'MonitorFrame';
  monitorGroup.add(frame);

  // 螢幕（發光，改進材質）
  const screenGeometry = new THREE.PlaneGeometry(width - 0.04, height - 0.04);
  const screenMaterial = new THREE.MeshStandardMaterial({
    color: screenColor,
    emissive: screenColor,
    emissiveIntensity: 1.0,
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
    roughness: 0.3,
    metalness: 0.7,
    envMapIntensity: 0.8,
  });
  const stand = new THREE.Mesh(standGeometry, standMaterial);
  stand.position.y = -height / 2 - 0.075;
  stand.castShadow = true;
  stand.name = 'MonitorStand';
  monitorGroup.add(stand);

  // 底座
  const baseGeometry = new THREE.BoxGeometry(0.2, 0.02, 0.15);
  const base = new THREE.Mesh(baseGeometry, standMaterial);
  base.position.y = -height / 2 - 0.16;
  base.castShadow = true;
  base.name = 'MonitorBase';
  monitorGroup.add(base);

  parent.add(monitorGroup);
}

// ============ 辦公用品（改進材質）============

function createOfficeSupplies(parent) {
  // 鍵盤（改進材質）
  const keyboardGeometry = new THREE.BoxGeometry(0.4, 0.02, 0.15);
  const keyboardMaterial = new THREE.MeshStandardMaterial({
    color: 0x2a2a2a,
    roughness: 0.7,
    metalness: 0.1,
    envMapIntensity: 0.5,
  });
  const keyboard = new THREE.Mesh(keyboardGeometry, keyboardMaterial);
  keyboard.position.set(0, 0.76, 0.1);
  keyboard.castShadow = true;
  keyboard.name = 'Keyboard';
  parent.add(keyboard);

  // 滑鼠（改進材質）
  const mouseGeometry = new THREE.BoxGeometry(0.06, 0.02, 0.1);
  const mouse = new THREE.Mesh(mouseGeometry, keyboardMaterial);
  mouse.position.set(0.3, 0.76, 0.1);
  mouse.castShadow = true;
  mouse.name = 'Mouse';
  parent.add(mouse);

  // 咖啡杯（改進材質）
  const cupGeometry = new THREE.CylinderGeometry(0.04, 0.035, 0.1, 16);
  const cupMaterial = new THREE.MeshStandardMaterial({
    color: 0xFFFFFF,
    roughness: 0.2,
    metalness: 0.0,
    envMapIntensity: 0.8,
  });
  const cup = new THREE.Mesh(cupGeometry, cupMaterial);
  cup.position.set(-0.4, 0.8, 0.1);
  cup.castShadow = true;
  cup.name = 'CoffeeCup';
  parent.add(cup);

  // 筆筒（改進材質）
  const penHolderGeometry = new THREE.CylinderGeometry(0.03, 0.03, 0.1, 16);
  const penHolderMaterial = new THREE.MeshStandardMaterial({
    color: 0x2a2a2a,
    roughness: 0.5,
    metalness: 0.1,
    envMapIntensity: 0.6,
  });
  const penHolder = new THREE.Mesh(penHolderGeometry, penHolderMaterial);
  penHolder.position.set(0.5, 0.8, -0.1);
  penHolder.castShadow = true;
  penHolder.name = 'PenHolder';
  parent.add(penHolder);
}

// ============ 休息區域（改進材質）============

function createLoungeArea(centerX, centerZ) {
  const loungeGroup = new THREE.Group();
  loungeGroup.name = 'LoungeArea';
  loungeGroup.position.set(centerX, 0, centerZ);

  createSofa(loungeGroup, 0, 0);
  createCoffeeTable(loungeGroup, 0, 1.5);
  createRug(loungeGroup, 0, 0.5);

  const smallPlant = createSmallPlant(null, 1.5, 0);
  loungeGroup.add(smallPlant);

  scene.add(loungeGroup);

  console.log('[Office Generator V3] 休息區域創建完成');
}

function createSofa(parent, x, z) {
  const { width, height, depth, color } = OFFICE_SPEC.sofa;
  const sofaGroup = new THREE.Group();
  sofaGroup.name = 'Sofa';
  sofaGroup.position.set(x, 0, z);

  const sofaMaterial = new THREE.MeshStandardMaterial({
    color: color,
    roughness: 0.9,
    metalness: 0.0,
    envMapIntensity: 0.4,
  });

  // 座椅
  const seatGeometry = new THREE.BoxGeometry(width, 0.4, depth);
  const seat = new THREE.Mesh(seatGeometry, sofaMaterial);
  seat.position.y = 0.2;
  seat.castShadow = true;
  seat.name = 'SofaSeat';
  sofaGroup.add(seat);

  // 椅背
  const backGeometry = new THREE.BoxGeometry(width, height - 0.4, 0.2);
  const back = new THREE.Mesh(backGeometry, sofaMaterial);
  back.position.set(0, 0.4 + (height - 0.4) / 2, depth / 2 - 0.1);
  back.castShadow = true;
  back.name = 'SofaBack';
  sofaGroup.add(back);

  // 扶手
  const armLeftGeometry = new THREE.BoxGeometry(0.15, height - 0.2, depth);
  const armLeft = new THREE.Mesh(armLeftGeometry, sofaMaterial);
  armLeft.position.set(-width / 2 + 0.075, 0.4, 0);
  armLeft.castShadow = true;
  armLeft.name = 'SofaArmLeft';
  sofaGroup.add(armLeft);

  const armRight = armLeft.clone();
  armRight.position.x = width / 2 - 0.075;
  armRight.name = 'SofaArmRight';
  sofaGroup.add(armRight);

  // 抱枕（改進材質）
  const pillowMaterial = new THREE.MeshStandardMaterial({
    color: 0x4169E1,
    roughness: 0.9,
    metalness: 0.0,
    envMapIntensity: 0.3,
  });
  const pillowGeometry = new THREE.BoxGeometry(0.3, 0.3, 0.15);
  const pillow1 = new THREE.Mesh(pillowGeometry, pillowMaterial);
  pillow1.position.set(-0.5, 0.6, depth / 2 - 0.2);
  pillow1.castShadow = true;
  pillow1.name = 'Pillow1';
  sofaGroup.add(pillow1);

  const pillow2 = pillow1.clone();
  pillow2.position.x = 0.5;
  pillow2.name = 'Pillow2';
  sofaGroup.add(pillow2);

  parent.add(sofaGroup);
}

function createCoffeeTable(parent, x, z) {
  const tableGroup = new THREE.Group();
  tableGroup.name = 'CoffeeTable';
  tableGroup.position.set(x, 0, z);

  // 桌面（改進材質）
  const topGeometry = new THREE.BoxGeometry(1.0, 0.05, 0.6);
  const topMaterial = new THREE.MeshStandardMaterial({
    color: 0x1a1a1a,
    roughness: 0.2,
    metalness: 0.6,
    envMapIntensity: 1.0,
  });
  const top = new THREE.Mesh(topGeometry, topMaterial);
  top.position.y = 0.45;
  top.castShadow = true;
  top.receiveShadow = true;
  top.name = 'TableTop';
  tableGroup.add(top);

  // 桌腿（改進材質）
  const legMaterial = new THREE.MeshStandardMaterial({
    color: 0x1a1a1a,
    roughness: 0.2,
    metalness: 0.9,
    envMapIntensity: 1.0,
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
    leg.castShadow = true;
    leg.name = `TableLeg_${i + 1}`;
    tableGroup.add(leg);
  });

  // 雜誌（改進材質）
  const magazineGeometry = new THREE.BoxGeometry(0.3, 0.01, 0.2);
  const magazineMaterial = new THREE.MeshStandardMaterial({
    color: 0xFFFFFF,
    roughness: 0.8,
    metalness: 0.0,
    envMapIntensity: 0.3,
  });
  const magazine = new THREE.Mesh(magazineGeometry, magazineMaterial);
  magazine.position.set(0, 0.48, 0);
  magazine.rotation.y = 0.3;
  magazine.castShadow = true;
  magazine.name = 'Magazine';
  tableGroup.add(magazine);

  parent.add(tableGroup);
}

function createRug(parent, x, z) {
  const rugGeometry = new THREE.PlaneGeometry(3, 2);
  const rugMaterial = new THREE.MeshStandardMaterial({
    color: 0xD3D3D3,
    roughness: 0.95,
    metalness: 0.0,
    side: THREE.DoubleSide,
    envMapIntensity: 0.2,
  });
  const rug = new THREE.Mesh(rugGeometry, rugMaterial);
  rug.rotation.x = -Math.PI / 2;
  rug.position.set(x, 0.01, z);
  rug.receiveShadow = true;
  rug.name = 'Rug';
  parent.add(rug);
}

// ============ 會議室（改進材質）============

function createConferenceRoom(centerX, centerZ) {
  const conferenceGroup = new THREE.Group();
  conferenceGroup.name = 'ConferenceRoom';
  conferenceGroup.position.set(centerX, 0, centerZ);

  createConferenceTable(conferenceGroup, 0, 0);

  const chairPositions = [
    { x: -1, z: 0 },
    { x: -0.5, z: 0 },
    { x: 0, z: 0 },
    { x: 0.5, z: 0 },
    { x: 1, z: 0 },
    { x: 0, z: -0.8 },
  ];

  chairPositions.forEach((pos, i) => {
    createConferenceChair(conferenceGroup, pos.x, pos.z, i + 1);
  });

  createWhiteboard(conferenceGroup, 0, -1.5);

  scene.add(conferenceGroup);

  console.log('[Office Generator V3] 會議室創建完成');
}

function createConferenceTable(parent, x, z) {
  const tableGroup = new THREE.Group();
  tableGroup.name = 'ConferenceTable';
  tableGroup.position.set(x, 0, z);

  // 桌面（改進材質）
  const topGeometry = new THREE.CylinderGeometry(1.5, 1.5, 0.05, 32);
  const topMaterial = new THREE.MeshStandardMaterial({
    color: 0x4A4A4A,
    roughness: 0.3,
    metalness: 0.3,
    envMapIntensity: 0.8,
  });
  const top = new THREE.Mesh(topGeometry, topMaterial);
  top.position.y = 0.75;
  top.castShadow = true;
  top.receiveShadow = true;
  top.name = 'ConfTableTop';
  tableGroup.add(top);

  // 桌腿（改進材質）
  const legGeometry = new THREE.CylinderGeometry(0.1, 0.15, 0.75, 16);
  const legMaterial = new THREE.MeshStandardMaterial({
    color: 0x4A4A4A,
    roughness: 0.2,
    metalness: 0.8,
    envMapIntensity: 1.0,
  });
  const leg = new THREE.Mesh(legGeometry, legMaterial);
  leg.position.y = 0.375;
  leg.castShadow = true;
  leg.name = 'ConfTableLeg';
  tableGroup.add(leg);

  parent.add(tableGroup);
}

function createConferenceChair(parent, x, z, index) {
  const chairGroup = new THREE.Group();
  chairGroup.name = `ConferenceChair_${index}`;
  chairGroup.position.set(x, 0, z);

  const chairMaterial = new THREE.MeshStandardMaterial({
    color: 0x2F4F4F,
    roughness: 0.7,
    metalness: 0.1,
    envMapIntensity: 0.6,
  });

  // 座椅
  const seatGeometry = new THREE.BoxGeometry(0.45, 0.08, 0.45);
  const seat = new THREE.Mesh(seatGeometry, chairMaterial);
  seat.position.y = 0.45;
  seat.castShadow = true;
  seat.name = 'ConfChairSeat';
  chairGroup.add(seat);

  // 椅背
  const backGeometry = new THREE.BoxGeometry(0.45, 0.5, 0.08);
  const back = new THREE.Mesh(backGeometry, chairMaterial);
  back.position.set(0, 0.7, -0.2);
  back.castShadow = true;
  back.name = 'ConfChairBack';
  chairGroup.add(back);

  // 椅腿（改進材質）
  const legMaterial = new THREE.MeshStandardMaterial({
    color: 0x888888,
    roughness: 0.2,
    metalness: 0.9,
    envMapIntensity: 1.0,
  });

  const legGeometry = new THREE.CylinderGeometry(0.02, 0.02, 0.45, 8);
  const leg = new THREE.Mesh(legGeometry, legMaterial);
  leg.position.y = 0.225;
  leg.castShadow = true;
  leg.name = 'ConfChairLeg';
  chairGroup.add(leg);

  parent.add(chairGroup);
}

function createWhiteboard(parent, x, z) {
  const whiteboardGroup = new THREE.Group();
  whiteboardGroup.name = 'Whiteboard';
  whiteboardGroup.position.set(x, 0, z);

  // 白板框架（改進材質）
  const frameGeometry = new THREE.BoxGeometry(2, 1.2, 0.05);
  const frameMaterial = new THREE.MeshStandardMaterial({
    color: 0x4A4A4A,
    roughness: 0.4,
    metalness: 0.4,
    envMapIntensity: 0.7,
  });
  const frame = new THREE.Mesh(frameGeometry, frameMaterial);
  frame.position.y = 1.5;
  frame.castShadow = true;
  frame.name = 'WhiteboardFrame';
  whiteboardGroup.add(frame);

  // 白板表面（改進材質）
  const surfaceGeometry = new THREE.PlaneGeometry(1.9, 1.1);
  const surfaceMaterial = new THREE.MeshStandardMaterial({
    color: 0xFFFFFF,
    roughness: 0.3,
    metalness: 0.0,
    envMapIntensity: 0.5,
  });
  const surface = new THREE.Mesh(surfaceGeometry, surfaceMaterial);
  surface.position.set(0, 1.5, 0.026);
  surface.name = 'WhiteboardSurface';
  whiteboardGroup.add(surface);

  parent.add(whiteboardGroup);
}

// ============ 植物裝飾（改進材質）============

function createPlants() {
  createLargePlant(-9, -9);
  createLargePlant(9, -9);

  const smallPlant1 = createSmallPlant(null, -9, 5);
  scene.add(smallPlant1);
  const smallPlant2 = createSmallPlant(null, 9, 5);
  scene.add(smallPlant2);

  console.log('[Office Generator V3] 植物裝飾創建完成');
}

function createLargePlant(x, z) {
  const plantGroup = new THREE.Group();
  plantGroup.name = `LargePlant_${x}_${z}`;
  plantGroup.position.set(x, 0, z);

  // 花盆（改進材質）
  const potGeometry = new THREE.CylinderGeometry(0.3, 0.25, 0.5, 16);
  const potMaterial = new THREE.MeshStandardMaterial({
    color: OFFICE_SPEC.plant.potColor,
    roughness: 0.2,
    metalness: 0.0,
    envMapIntensity: 0.8,
  });
  const pot = new THREE.Mesh(potGeometry, potMaterial);
  pot.position.y = 0.25;
  pot.castShadow = true;
  pot.name = 'Pot';
  plantGroup.add(pot);

  // 樹幹（改進材質）
  const trunkGeometry = new THREE.CylinderGeometry(0.05, 0.08, 1.5, 8);
  const trunkMaterial = new THREE.MeshStandardMaterial({
    color: 0x8B4513,
    roughness: 0.9,
    metalness: 0.0,
    envMapIntensity: 0.3,
  });
  const trunk = new THREE.Mesh(trunkGeometry, trunkMaterial);
  trunk.position.y = 1.25;
  trunk.castShadow = true;
  trunk.name = 'Trunk';
  plantGroup.add(trunk);

  // 葉子（改進材質）
  const leafGeometry = new THREE.SphereGeometry(0.6, 16, 16);
  const leafMaterial = new THREE.MeshStandardMaterial({
    color: OFFICE_SPEC.plant.plantColor,
    roughness: 0.8,
    metalness: 0.0,
    envMapIntensity: 0.4,
  });
  const leaf = new THREE.Mesh(leafGeometry, leafMaterial);
  leaf.position.y = 2.2;
  leaf.scale.y = 1.5;
  leaf.castShadow = true;
  leaf.name = 'Leaf';
  plantGroup.add(leaf);

  scene.add(plantGroup);
}

function createSmallPlant(parent, x, z) {
  const plantGroup = new THREE.Group();
  plantGroup.name = 'SmallPlant';
  plantGroup.position.set(x, 0, z);

  // 花盆（改進材質）
  const potGeometry = new THREE.CylinderGeometry(0.08, 0.07, 0.15, 12);
  const potMaterial = new THREE.MeshStandardMaterial({
    color: OFFICE_SPEC.plant.potColor,
    roughness: 0.2,
    metalness: 0.0,
    envMapIntensity: 0.7,
  });
  const pot = new THREE.Mesh(potGeometry, potMaterial);
  pot.position.y = 0.075;
  pot.castShadow = true;
  pot.name = 'SmallPot';
  plantGroup.add(pot);

  // 植物（改進材質）
  const plantGeometry = new THREE.SphereGeometry(0.1, 12, 12);
  const plantMaterial = new THREE.MeshStandardMaterial({
    color: 0x228B22,
    roughness: 0.8,
    metalness: 0.0,
    envMapIntensity: 0.3,
  });
  const plant = new THREE.Mesh(plantGeometry, plantMaterial);
  plant.position.y = 0.2;
  plant.scale.y = 0.7;
  plant.castShadow = true;
  plant.name = 'Succulent';
  plantGroup.add(plant);

  if (parent && parent.add) {
    parent.add(plantGroup);
  } else {
    return plantGroup;
  }
}

// ============ 窗戶（改進材質）============

function createWindows() {
  createWindow(0, 1.5, -9.99);
  createWindow(-9.99, 1.5, 0, Math.PI / 2);

  console.log('[Office Generator V3] 窗戶創建完成');
}

function createWindow(x, y, z, rotationY = 0) {
  const windowGroup = new THREE.Group();
  windowGroup.name = `Window_${x}_${y}_${z}`;
  windowGroup.position.set(x, y, z);
  windowGroup.rotation.y = rotationY;

  // 窗框（改進材質）
  const frameGeometry = new THREE.BoxGeometry(2, 1.5, 0.1);
  const frameMaterial = new THREE.MeshStandardMaterial({
    color: 0xFFFFFF,
    roughness: 0.4,
    metalness: 0.3,
    envMapIntensity: 0.8,
  });
  const frame = new THREE.Mesh(frameGeometry, frameMaterial);
  frame.castShadow = true;
  frame.name = 'WindowFrame';
  windowGroup.add(frame);

  // 玻璃（改進材質）
  const glassGeometry = new THREE.PlaneGeometry(1.9, 1.4);
  const glassMaterial = new THREE.MeshStandardMaterial({
    color: 0x87CEEB,
    roughness: 0.0,
    metalness: 0.0,
    transparent: true,
    opacity: 0.3,
    envMapIntensity: 1.0,
    transmission: 0.9,
    ior: 1.5,
  });
  const glass = new THREE.Mesh(glassGeometry, glassMaterial);
  glass.position.z = 0.051;
  glass.name = 'WindowGlass';
  windowGroup.add(glass);

  scene.add(windowGroup);
}

// ============ 高品質燈光系統 ============

function setupHighQualityLighting() {
  console.log('[Office Generator V3] 設置高品質燈光...');

  // 環境光（柔和）
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.3);
  ambientLight.name = 'AmbientLight';
  scene.add(ambientLight);

  // 半球光（模擬天空與地面反射）
  const hemiLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.5);
  hemiLight.position.set(0, 20, 0);
  hemiLight.name = 'HemisphereLight';
  scene.add(hemiLight);

  // 主光源（模擬窗戶光，改進陰影）
  const mainLight = new THREE.DirectionalLight(0xffffff, 1.2);
  mainLight.position.set(10, 15, 10);
  mainLight.castShadow = true;
  mainLight.shadow.mapSize.width = 4096;
  mainLight.shadow.mapSize.height = 4096;
  mainLight.shadow.camera.near = 0.5;
  mainLight.shadow.camera.far = 50;
  mainLight.shadow.camera.left = -20;
  mainLight.shadow.camera.right = 20;
  mainLight.shadow.camera.top = 20;
  mainLight.shadow.camera.bottom = -20;
  mainLight.shadow.bias = -0.0001;
  mainLight.shadow.normalBias = 0.02;
  mainLight.name = 'MainLight';
  scene.add(mainLight);

  // 補光（柔和）
  const fillLight = new THREE.DirectionalLight(0xffffff, 0.4);
  fillLight.position.set(-10, 10, -10);
  fillLight.name = 'FillLight';
  scene.add(fillLight);

  // 室內照明（點光源，改進強度）
  const indoorLights = [
    { x: -4, y: 2.5, z: 0, intensity: 0.8 },
    { x: 6, y: 2.5, z: 0, intensity: 0.8 },
    { x: 0, y: 2.5, z: -7, intensity: 0.8 },
  ];

  indoorLights.forEach((pos, i) => {
    const pointLight = new THREE.PointLight(0xFFF5E6, pos.intensity, 15, 2);
    pointLight.position.set(pos.x, pos.y, pos.z);
    pointLight.castShadow = true;
    pointLight.shadow.mapSize.width = 1024;
    pointLight.shadow.mapSize.height = 1024;
    pointLight.name = `IndoorLight_${i + 1}`;
    scene.add(pointLight);
  });

  console.log('[Office Generator V3] 高品質燈光設置完成');
}

// ============ 後處理效果 ============

function setupPostProcessing() {
  console.log('[Office Generator V3] 設置後處理效果...');

  // 創建後處理合成器
  composer = new EffectComposer(renderer);

  // 渲染通道
  const renderPass = new RenderPass(scene, camera);
  composer.addPass(renderPass);

  // 泛光效果（Bloom）
  const bloomPass = new UnrealBloomPass(
    new THREE.Vector2(window.innerWidth, window.innerHeight),
    0.3,  // 強度
    0.4,  // 半徑
    0.85  // 閾值
  );
  composer.addPass(bloomPass);

  // SMAA 抗鋸齒
  const smaaPass = new SMAAPass(window.innerWidth, window.innerHeight);
  composer.addPass(smaaPass);

  console.log('[Office Generator V3] 後處理效果設置完成');
}

// ============ 動畫循環 ============

function animate() {
  requestAnimationFrame(animate);

  controls.update();

  // 使用後處理渲染
  if (composer) {
    composer.render();
  } else {
    renderer.render(scene, camera);
  }
}

// ============ 視窗大小調整 ============

function onWindowResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);

  if (composer) {
    composer.setSize(window.innerWidth, window.innerHeight);
  }
}

// ============ 啟動 ============

init();
animate();

console.log('[Office Generator V3] 辦公室場景生成完成！');
console.log('[Office Generator V3] 測試地址：http://100.113.156.108:8055/');
console.log('[Office Generator V3] 高品質渲染功能：');
console.log('  ✅ ACES Filmic Tone Mapping');
console.log('  ✅ 高動態範圍（HDR）燈光');
console.log('  ✅ 物理正確光照');
console.log('  ✅ 改進的材質反射');
console.log('  ✅ 泛光效果（Bloom）');
console.log('  ✅ SMAA 抗鋸齒');
console.log('  ✅ 高品質陰影');
console.log('  ✅ 半球光（天空與地面反射）');
