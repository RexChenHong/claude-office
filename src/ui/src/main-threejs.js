/**
 * Claude Office - Three.js 3D Scene (修正版)
 * 專注於顯示 3D 模型，移除簡單幾何體
 */

import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// ============ 全局變量 ============

let scene, camera, renderer, controls;
let mixer, clock;
let characters = [];
const mixers = [];

// ============ 初始化場景 ============

function init() {
  console.log('[Three.js] 初始化場景...');

  // 創建場景
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x1a1a2e); // 深色背景

  // 創建相機（調整位置）
  camera = new THREE.PerspectiveCamera(
    60,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
  );
  camera.position.set(0, 1.5, 3); // 更近的距離

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
  controls.target.set(0, 1, 0); // 看向模型中心

  // 添加燈光
  createLights();

  // 創建簡單地面
  createGround();

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
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
  scene.add(ambientLight);

  // 主光源
  const directionalLight = new THREE.DirectionalLight(0xffffff, 1.0);
  directionalLight.position.set(5, 10, 7);
  directionalLight.castShadow = true;
  directionalLight.shadow.mapSize.width = 2048;
  directionalLight.shadow.mapSize.height = 2048;
  scene.add(directionalLight);

  // 背光
  const backLight = new THREE.DirectionalLight(0xffffff, 0.5);
  backLight.position.set(-5, 5, -5);
  scene.add(backLight);

  // 頂光
  const topLight = new THREE.DirectionalLight(0xffffff, 0.3);
  topLight.position.set(0, 10, 0);
  scene.add(topLight);

  console.log('[Three.js] 燈光系統設置完成');
}

// ============ 地面 ============

function createGround() {
  // 圓形地面
  const groundGeometry = new THREE.CircleGeometry(5, 64);
  const groundMaterial = new THREE.MeshStandardMaterial({
    color: 0x2d2d44,
    roughness: 0.8,
    metalness: 0.2,
  });
  const ground = new THREE.Mesh(groundGeometry, groundMaterial);
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  scene.add(ground);

  console.log('[Three.js] 地面創建完成');
}

// ============ 加載 3D 模型 ============

function loadCharacters() {
  const loader = new GLTFLoader();

  // 顯示加載訊息
  const loadingDiv = document.createElement('div');
  loadingDiv.id = 'loading-info';
  loadingDiv.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);color:#00ff88;font-size:24px;font-family:monospace;z-index:1000;';
  loadingDiv.textContent = '正在加載 3D 模型...';
  document.body.appendChild(loadingDiv);

  // 加載 Xbot 模型
  loader.load(
    '/models/Xbot.glb',
    (gltf) => {
      console.log('[Three.js] ✅ Xbot 模型加載成功！');
      console.log('[Three.js] 模型信息：', {
        animations: gltf.animations.length,
        scene: gltf.scene.children.length,
        position: gltf.scene.position,
        scale: gltf.scene.scale,
      });

      const model = gltf.scene;
      
      // 調整模型位置和縮放
      model.position.set(0, 0, 0);
      model.scale.set(1, 1, 1);

      // 啟用陰影
      model.traverse((child) => {
        if (child.isMesh) {
          child.castShadow = true;
          child.receiveShadow = true;
          console.log('[Three.js] 網格：', child.name, child.geometry?.boundingBox);
        }
      });

      scene.add(model);
      characters.push(model);

      // 創建動畫混合器
      if (gltf.animations.length > 0) {
        mixer = new THREE.AnimationMixer(model);
        const action = mixer.clipAction(gltf.animations[0]);
        action.play();
        console.log('[Three.js] 🎬 播放動畫：', gltf.animations[0].name);
      }

      // 移除加載訊息
      loadingDiv.textContent = '✅ 模型加載完成！';
      setTimeout(() => loadingDiv.remove(), 2000);

      // 更新控制器目標
      controls.target.set(0, 1, 0);
      controls.update();
    },
    (progress) => {
      if (progress.total > 0) {
        const percent = (progress.loaded / progress.total * 100).toFixed(1);
        loadingDiv.textContent = `加載進度：${percent}%`;
        console.log(`[Three.js] 加載進度：${percent}%`);
      }
    },
    (error) => {
      console.error('[Three.js] ❌ 模型加載失敗：', error);
      loadingDiv.textContent = '❌ 模型加載失敗！';
      loadingDiv.style.color = '#ff4444';
      
      // 顯示錯誤訊息
      document.getElementById('error-message').textContent = 
        `模型加載失敗：${error.message || '未知錯誤'}。請檢查控制台。`;
    }
  );
}

// ============ 動畫循環 ============

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
console.log('[Three.js] 使用滑鼠拖曳旋轉視角');
console.log('[Three.js] 使用滾輪縮放');
