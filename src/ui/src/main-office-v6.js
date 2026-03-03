/**
 * Claude Office - V6（Blender 建模版本）
 * 載入 Blender 導出的 GLB 模型
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { SSAOPass } from 'three/addons/postprocessing/SSAOPass.js';

// ============ 全局變量 ============

let scene, camera, renderer, controls, composer;
let clock;
let mixer;
let officeModel = null;

// ============ 初始化場景 ============

function init() {
  console.log('[Office V6] 初始化場景（Blender 建模版本）...');

  // 創建場景
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xE8E8E8);

  // 創建相機
  camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.set(15, 10, 15);
  camera.lookAt(0, 0, 0);

  // 創建渲染器
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  document.getElementById('game-container').appendChild(renderer.domElement);

  // 添加控制器
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.target.set(0, 0.5, 0);

  // 時鐘
  clock = new THREE.Clock();

  // 載入 Blender 模型
  loadOfficeModel();

  // 設置燈光（備用，如果模型沒有燈光）
  setupLighting();

  // 設置後處理
  setupPostProcessing();

  // 監聽視窗大小變化
  window.addEventListener('resize', onWindowResize, false);

  console.log('[Office V6] 場景初始化完成！');
}

// ============ 載入 Blender 模型 ============

function loadOfficeModel() {
  console.log('[Office V6] 載入 Blender 模型...');

  const loader = new GLTFLoader();

  // 設置加載管理器
  const manager = THREE.DefaultLoadingManager;
  manager.onProgress = (url, loaded, total) => {
    console.log(`[Loader] 載入進度: ${loaded}/${total} - ${url}`);
  };

  loader.load(
    '/blender/exports/office_5person.glb',
    (gltf) => {
      officeModel = gltf.scene;
      console.log('[Office V6] 模型載入成功！', officeModel);

      // 設置陰影
      officeModel.traverse((child) => {
        if (child.isMesh) {
          child.castShadow = true;
          child.receiveShadow = true;

          // 增強材質
          if (child.material) {
            // 確保材質正確渲染
            if (child.material.isMeshStandardMaterial || child.material.isMeshPhysicalMaterial) {
              // Blender 材質已經有正確的 PBR 設置
              child.material.needsUpdate = true;
            }
          }
        }
      });

      // 計算邊界盒並調整相機
      const box = new THREE.Box3().setFromObject(officeModel);
      const center = box.getCenter(new THREE.Vector3());
      const size = box.getSize(new THREE.Vector3());

      console.log('[Office V6] 模型尺寸:', size);
      console.log('[Office V6] 模型中心:', center);

      // 添加到場景
      scene.add(officeModel);

      // 調整相機位置
      const maxDim = Math.max(size.x, size.y, size.z);
      camera.position.set(center.x + maxDim * 0.8, center.y + maxDim * 0.5, center.z + maxDim * 0.8);
      controls.target.copy(center);
      controls.update();

      console.log('[Office V6] Blender 模型整合完成！');
    },
    (progress) => {
      const percent = (progress.loaded / progress.total * 100).toFixed(1);
      console.log(`[Office V6] 載入進度: ${percent}%`);
    },
    (error) => {
      console.error('[Office V6] 模型載入失敗:', error);

      // 備用方案：創建簡單場景
      console.log('[Office V6] 使用備用場景...');
      createFallbackScene();
    }
  );
}

// ============ 備用場景 ============

function createFallbackScene() {
  // 地板
  const floorGeometry = new THREE.PlaneGeometry(20, 20);
  const floorMaterial = new THREE.MeshStandardMaterial({
    color: 0x8B7355,
    roughness: 0.8,
    metalness: 0.1,
  });
  const floor = new THREE.Mesh(floorGeometry, floorMaterial);
  floor.rotation.x = -Math.PI / 2;
  floor.receiveShadow = true;
  scene.add(floor);

  // 簡單工作站標記
  for (let i = 0; i < 5; i++) {
    const markerGeometry = new THREE.BoxGeometry(1.2, 0.1, 0.6);
    const markerMaterial = new THREE.MeshStandardMaterial({ color: 0xffffff });
    const marker = new THREE.Mesh(markerGeometry, markerMaterial);
    marker.position.set(-6 + i * 3, 0.75, 0);
    marker.castShadow = true;
    marker.receiveShadow = true;
    scene.add(marker);
  }

  console.log('[Office V6] 備用場景創建完成');
}

// ============ 設置燈光 ============

function setupLighting() {
  console.log('[Office V6] 設置燈光...');

  // 環境光
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
  scene.add(ambientLight);

  // 半球光（模擬天空和地面反射）
  const hemisphereLight = new THREE.HemisphereLight(0x87CEEB, 0x8B7355, 0.6);
  hemisphereLight.position.set(0, 10, 0);
  scene.add(hemisphereLight);

  // 主光源（模擬窗戶光）
  const mainLight = new THREE.DirectionalLight(0xfff5e6, 1.2);
  mainLight.position.set(10, 15, 5);
  mainLight.castShadow = true;
  mainLight.shadow.mapSize.width = 2048;
  mainLight.shadow.mapSize.height = 2048;
  mainLight.shadow.camera.near = 0.5;
  mainLight.shadow.camera.far = 50;
  mainLight.shadow.camera.left = -15;
  mainLight.shadow.camera.right = 15;
  mainLight.shadow.camera.top = 15;
  mainLight.shadow.camera.bottom = -15;
  mainLight.shadow.bias = -0.0001;
  scene.add(mainLight);

  // 填充光
  const fillLight = new THREE.DirectionalLight(0xe6f0ff, 0.5);
  fillLight.position.set(-10, 10, -5);
  scene.add(fillLight);

  console.log('[Office V6] 燈光設置完成');
}

// ============ 設置後處理 ============

function setupPostProcessing() {
  console.log('[Office V6] 設置後處理...');

  composer = new EffectComposer(renderer);

  // 渲染通道
  const renderPass = new RenderPass(scene, camera);
  composer.addPass(renderPass);

  // SSAO（環境光遮蔽）
  const ssaoPass = new SSAOPass(scene, camera, window.innerWidth, window.innerHeight);
  ssaoPass.kernelRadius = 16;
  ssaoPass.minDistance = 0.005;
  ssaoPass.maxDistance = 0.1;
  composer.addPass(ssaoPass);

  // Bloom（泛光）
  const bloomPass = new UnrealBloomPass(
    new THREE.Vector2(window.innerWidth, window.innerHeight),
    0.3,  // 強度
    0.4,  // 半徑
    0.85  // 閾值
  );
  composer.addPass(bloomPass);

  console.log('[Office V6] 後處理設置完成');
}

// ============ 視窗大小變化 ============

function onWindowResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);

  if (composer) {
    composer.setSize(window.innerWidth, window.innerHeight);
  }
}

// ============ 動畫循環 ============

function animate() {
  requestAnimationFrame(animate);

  const delta = clock.getDelta();

  // 更新控制器
  controls.update();

  // 更新動畫混合器
  if (mixer) {
    mixer.update(delta);
  }

  // 渲染
  if (composer) {
    composer.render();
  } else {
    renderer.render(scene, camera);
  }
}

// ============ 啟動 ============

init();
animate();

console.log('[Office V6] Claude Office 啟動完成！');
