# Blender 學習路徑

## 📅 建立日期：2026-03-03

---

## 🎯 學習目標

掌握 Blender 建模技能，創建 Sketchfab 等級的 5 人辦公室場景。

**預期效果**：85% → 98%

---

## 📚 學習階段

### Phase 1：Blender 基礎（1-2 小時）

#### 1.1 介面與操作
- [ ] Blender 介面佈局
- [ ] 視窗導航（旋轉、縮放、平移）
- [ ] 基礎快捷鍵
  - `G`：移動
  - `R`：旋轉
  - `S`：縮放
  - `Tab`：切換編輯模式
  - `Z`：著色模式
  - `Ctrl+S`：保存

#### 1.2 基礎建模
- [ ] 基礎形狀（Cube、Cylinder、Plane）
- [ ] 編輯模式（Vertex、Edge、Face）
- [ ] Extrude（擠出）
- [ ] Inset（內插）
- [ ] Bevel（倒角）
- [ ] Loop Cut（環切）

#### 1.3 材質與貼圖
- [ ] 材質系統（Principled BSDF）
- [ ] 貼圖映射（UV Mapping）
- [ ] PBR 材質設置
  - Base Color（基礎色）
  - Roughness（粗糙度）
  - Metallic（金屬度）
  - Normal Map（法線貼圖）

#### 1.4 燈光設置
- [ ] 點光源（Point Light）
- [ ] 方向光（Sun Light）
- [ ] 區域光（Area Light）
- [ ] 環境光（World Settings）

---

### Phase 2：辦公室建模（1-2 小時）

#### 2.1 建築結構
- [ ] 地板（Plane → Extrude）
- [ ] 牆面（Plane → Extrude）
- [ ] 天花板
- [ ] 窗戶（落地窗設計）
- [ ] 玻璃隔間（Transparent Material）

#### 2.2 辦公家具
按照 `LAYOUT_V4.md` 佈局：

**工作站（5 個）**
- [ ] 辦公桌（1.2m x 0.6m）
  - 桌面（Box + Bevel）
  - 桌腿（Cylinder）
- [ ] 辦公椅
  - 座椅（Box + Subdivision）
  - 椅背（Box）
  - 扶手（Cylinder）
- [ ] 電腦螢幕（雙螢幕）
  - 外框（Box）
  - 螢幕（Plane + Emission）

**會議室（左上角）**
- [ ] 會議桌（橢圓形，3m x 1.2m）
- [ ] 會議椅（6 張）
- [ ] 白板（2m x 1.2m）

**公共區域（右下角）**
- [ ] L 型沙發
- [ ] 茶几
- [ ] 咖啡桌
- [ ] 高腳椅（2 張）

#### 2.3 裝飾品
- [ ] 植物（大型 + 小型）
- [ ] 掛畫（牆面裝飾）
- [ ] 時鐘
- [ ] 天花板燈具（LED 平板燈）
- [ ] 檔案櫃（靠牆）

#### 2.4 材質應用
- [ ] 木地板（真實木紋貼圖）
- [ ] 白色牆面（粗糙度設置）
- [ ] 布料材質（沙發、椅子）
- [ ] 金屬材質（框架、桌腿）
- [ ] 玻璃材質（窗戶、隔間）

---

### Phase 3：導出與整合（30 分鐘）

#### 3.1 導出 GLTF
- [ ] 檢查模型尺寸（公制）
- [ ] 應用所有變換（Ctrl+A）
- [ ] 導出 GLTF 格式
  - Format: glTF Separate (.gltf + .bin + textures)
  - Include: Custom Properties, Cameras, Lights
  - Transform: +Y Up
  - Mesh: Apply Modifiers

#### 3.2 Three.js 整合
- [ ] 安裝 GLTFLoader
  ```bash
  npm install three/examples/jsm/loaders/GLTFLoader
  ```
- [ ] 加載 GLTF 模型
  ```javascript
  import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
  
  const loader = new GLTFLoader();
  loader.load('/models/office.glb', (gltf) => {
    scene.add(gltf.scene);
  });
  ```
- [ ] 調整相機位置
- [ ] 測試渲染效果

#### 3.3 優化
- [ ] 降低多邊形數量（Decimate Modifier）
- [ ] 壓縮貼圖（1024x1024）
- [ ] 合併網格（Join）
- [ ] 檢查效能（Frame Rate）

---

## 🎨 技術規格

### 建模標準
- **單位**：公制（米）
- **比例**：1:1 真實比例
- **原點**：地板中心 (0, 0, 0)
- **朝向**：+Y 向上，+Z 向前

### 貼圖規格
- **解析度**：1024x1024 或 2048x2048
- **格式**：PNG 或 JPEG
- **類型**：
  - Base Color（Albedo）
  - Roughness
  - Metallic
  - Normal Map
  - Ambient Occlusion（可選）

### 材質標準
- **木地板**：
  - Base Color: 木紋貼圖
  - Roughness: 0.4-0.6
  - Metallic: 0.0
- **布料**：
  - Base Color: 單色或花紋
  - Roughness: 0.7-0.9
  - Metallic: 0.0
- **金屬**：
  - Base Color: 金屬色
  - Roughness: 0.2-0.4
  - Metallic: 0.9-1.0
- **玻璃**：
  - Base Color: 白色或淡藍色
  - Roughness: 0.0
  - Metallic: 0.0
  - Alpha: 0.3-0.5

---

## 📖 學習資源

### 官方文檔
- **Blender 官方文檔**：https://docs.blender.org/
- **Blender 手冊**：https://docs.blender.org/manual/en/latest/

### 教學影片
- **Blender Guru**：https://www.blenderguru.com/
  - Blender 2.8 Beginner Tutorial Series
  - Donut Tutorial（甜甜圈教學）
- **CG Cookie**：https://cgcookie.com/
- **Blender Cloud**：https://cloud.blender.org/

### 免費資源
- **Poly Haven**（貼圖）：https://polyhaven.com/
  - HDRI 環境貼圖
  - PBR 材質
  - 3D 模型
- **Texture Haven**（貼圖）：https://texturehaven.com/
- **Sketchfab**（參考）：https://sketchfab.com/features/gltf

### Python API
- **Blender Python API**：https://docs.blender.org/api/current/
- **Blender Python 範例**：https://docs.blender.org/api/current/info_quickstart.html

---

## 🛠️ 實作計劃

### Day 1（2026-03-03）
- [ ] 完成 Phase 1（基礎）
- [ ] 熟悉介面與操作
- [ ] 建立第一個簡單模型（Cube → 桌子）

### Day 2（2026-03-04）
- [ ] 完成 Phase 2（建模）
- [ ] 建立完整辦公室場景
- [ ] 應用材質與貼圖

### Day 3（2026-03-05）
- [ ] 完成 Phase 3（導出）
- [ ] 整合到 Three.js
- [ ] 測試與優化

---

## 📊 進度追蹤

| 階段 | 預計時間 | 實際時間 | 狀態 |
|------|---------|---------|------|
| Phase 1：基礎 | 1-2 小時 | - | ⏳ 待開始 |
| Phase 2：建模 | 1-2 小時 | - | ⏳ 待開始 |
| Phase 3：導出 | 30 分鐘 | - | ⏳ 待開始 |

---

## 🎯 成功標準

### 技術標準
- ✅ 模型能成功導出 GLTF
- ✅ Three.js 能正確加載
- ✅ 貼圖正確顯示
- ✅ 材質效果符合預期

### 視覺標準
- ✅ 達到 Sketchfab 參考模型的 95% 以上
- ✅ 材質真實感明顯提升
- ✅ 光照效果自然
- ✅ 陰影柔和

### 效能標準
- ✅ Frame Rate ≥ 30 FPS（筆電）
- ✅ 載入時間 < 5 秒
- ✅ 記憶體使用 < 500MB

---

## 📝 學習筆記

### 2026-03-03
- 決策：選擇 Blender 建模作為長期技術投資
- 原因：效果最好（98%），免費，可複用
- 下一步：開始 Phase 1 學習

---

**最後更新**：2026-03-03 18:25 (Asia/Taipei)
