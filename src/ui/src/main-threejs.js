/**
 * Claude Office - Three.js 3D Scene
 * 使用真正的 3D 模型（非幾何圖形）
 */

import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// ============ 全局變量 ============

let scene, camera, renderer, controls;
let mixer, clock;
let characters = [];

// ============ 初始化場景 ============

function init() {
  console.log('[Three.js] 初始化場景...');

  // 創建場景
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x87CEEB); // 天空藍

  // 創建相機
  camera = new THREE.PerspectiveCamera(
    45,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
  );
  camera.position.set(0, 2, 5);

  // 創建渲染器
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  document.getElementById('game-container').appendChild(renderer.domElement);

  // 添加控制器
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;

  // 添加燈光
  createLights();

  // 創建地板
  createFloor();

  // 創建辦公室場景
  createOffice();

  // 加載 3D 模型
  loadCharacters();

  // 時鐘（用於動畫）
  clock = new THREE.Clock();

  // 監聽視窗大小變化
  window.addEventListener('resize', onWindowResize, false);

  console.log('[Three.js] 場景初始化完成！');
}

// ============ 燈光系統 ============

function createLights() {
  // 環境光
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
  scene.add(ambientLight);

  // 主光源
  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
  directionalLight.position.set(5, 10, 7);
  directionalLight.castShadow = true;
  directionalLight.shadow.mapSize.width = 2048;
  directionalLight.shadow.mapSize.height = 2048;
  scene.add(directionalLight);

  // 補光
  const fillLight = new THREE.DirectionalLight(0xffffff, 0.3);
  fillLight.position.set(-5, 5, -5);
  scene.add(fillLight);
}

// ============ 場景物體 ============

function createFloor() {
  // 地板
  const floorGeometry = new THREE.PlaneGeometry(20, 20);
  const floorMaterial = new THREE.MeshStandardMaterial({
    color: 0xD2691E,
    roughness: 0.8,
  });
  const floor = new THREE.Mesh(floorGeometry, floorMaterial);
  floor.rotation.x = -Math.PI / 2;
  floor.receiveShadow = true;
  scene.add(floor);

  // 地板紋理（條紋）
  for (let i = -10; i <= 10; i++) {
    const stripeGeometry = new THREE.PlaneGeometry(0.05, 20);
    const stripeMaterial = new THREE.MeshStandardMaterial({
      color: 0xA0522D,
    });
    const stripe = new THREE.Mesh(stripeGeometry, stripeMaterial);
    stripe.rotation.x = -Math.PI / 2;
    stripe.position.set(i, 0.001, 0);
    scene.add(stripe);
  }
}

function createOffice() {
  // 辦公桌（簡單幾何形狀，之後替換為真實模型）
  const deskGeometry = new THREE.BoxGeometry(2, 0.8, 1);
  const deskMaterial = new THREE.MeshStandardMaterial({
    color: 0x8B4513,
    roughness: 0.6,
  });
  const desk = new THREE.Mesh(deskGeometry, deskMaterial);
  desk.position.set(-3, 0.4, 0);
  desk.castShadow = true;
  desk.receiveShadow = true;
  scene.add(desk);

  // 椅子
  const chairSeatGeometry = new THREE.BoxGeometry(0.5, 0.1, 0.5);
  const chairMaterial = new THREE.MeshStandardMaterial({
    color: 0x2F4F4F,
  });
  const chairSeat = new THREE.Mesh(chairSeatGeometry, chairMaterial);
  chairSeat.position.set(-3, 0.5, 0.6);
  chairSeat.castShadow = true;
  scene.add(chairSeat);

  // 椅背
  const chairBackGeometry = new THREE.BoxGeometry(0.5, 0.6, 0.1);
  const chairBack = new THREE.Mesh(chairBackGeometry, chairMaterial);
  chairBack.position.set(-3, 0.8, 0.85);
  chairBack.castShadow = true;
  scene.add(chairBack);

  // 電腦螢幕（簡單方塊）
  const screenGeometry = new THREE.BoxGeometry(0.8, 0.6, 0.05);
  const screenMaterial = new THREE.MeshStandardMaterial({
    color: 0x1a1a1a,
    emissive: 0x0077ff,
    emissiveIntensity: 0.3,
  });
  const screen = new THREE.Mesh(screenGeometry, screenMaterial);
  screen.position.set(-3, 1.2, -0.3);
  scene.add(screen);
}

// ============ 加載 3D 模型 ============

function loadCharacters() {
  const loader = new GLTFLoader();

  // 加載 Xbot 模型
  loader.load(
    '/models/Xbot.glb',
    (gltf) => {
      console.log('[Three.js] Xbot 模型加載成功！', gltf);

      const model = gltf.scene;
      model.position.set(0, 0, 0);
      model.scale.set(1, 1, 1);

      // 啟用陰影
      model.traverse((child) => {
        if (child.isMesh) {
          child.castShadow = true;
          child.receiveShadow = true;
        }
      });

      scene.add(model);

      // 創建動畫混合器
      if (gltf.animations.length > 0) {
        mixer = new THREE.AnimationMixer(model);
        const action = mixer.clipAction(gltf.animations[0]);
        action.play();
        console.log('[Three.js] 播放動畫：', gltf.animations[0].name);
      }

      characters.push(model);
    },
    (progress) => {
      console.log('[Three.js] 加載進度：', (progress.loaded / progress.total * 100) + '%');
    },
    (error) => {
      console.error('[Three.js] 模型加載失敗：', error);
      document.getElementById('error-message').textContent = '模型加載失敗！';
    }
  );

  // 加載第二個模型（複製）
  loader.load(
    '/models/Xbot.glb',
    (gltf) => {
      const model = gltf.scene;
      model.position.set(2, 0, 0);
      model.scale.set(1, 1, 1);

      model.traverse((child) => {
        if (child.isMesh) {
          child.castShadow = true;
          child.receiveShadow = true;
        }
      });

      scene.add(model);

      if (gltf.animations.length > 0) {
        const mixer2 = new THREE.AnimationMixer(model);
        const action = mixer2.clipAction(gltf.animations[0]);
        action.play();
        mixers.push(mixer2);
      }

      characters.push(model);
    }
  );
}

// ============ 動畫循環 ============

let mixers = [];

function animate() {
  requestAnimationFrame(animate);

  const delta = clock.getDelta();

  // 更新動畫混合器
  if (mixer) mixer.update(delta);
  mixers.forEach(m => m.update(delta));

  // 更新控制器
  controls.update();

  // 渲染場景
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

console.log('[Three.js] 3D 場景啟動完成！');
console.log('[Three.js] 使用真正的 3D 模型（GLTF）');
