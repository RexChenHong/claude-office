# Blender + Three.js 學習路徑

## 🎯 目標
**創建專業遊戲級視覺效果**（日系原神風格）

---

## 📋 專案規格

### 辦公室場景
**參考模型**：https://sketchfab.com/3d-models/office-ea1d5422c80141aa8ec2478cc359fe41
**詳細規格**：`OFFICE_SPEC.md`

**核心要素**：
- 開放式辦公區域（多個工作站）
- 休息/討論區域（沙發 + 茶几）
- 會議室
- 現代極簡風格（白 + 灰色調）
- 專業燈光系統

---

## 📚 學習計劃（更新版）

### Phase 1：快速原型 ✅（已完成）
**目標**：使用現成素材建立第一個 3D 場景

**完成內容**：
- ✅ 下載 Xbot.glb 模型（2.8 MB）
- ✅ 創建 Three.js 場景
- ✅ 實現 GLTF 模型加載
- ✅ 添加燈光和陰影
- ✅ OrbitControls 相機控制

**問題**：
- ❌ Xbot 不是日系風格
- ❌ 缺少辦公室場景

---

### Phase 1.5：辦公室建模（本週，10-12 小時）
**目標**：根據規格書創建辦公室場景

**學習內容**：
1. **Blender 基礎**（3-4 小時）
   - 介面與導航
   - 基礎建模工具
   - 材質系統
   - UV 展開

2. **辦公室建模**（5-6 小時）
   - 地板與牆面
   - 辦公桌椅
   - 電腦設備
   - 燈光系統

3. **導出與整合**（2-3 小時）
   - GLTF 導出
   - Three.js 整合
   - 燈光調整
   - 測試優化

**參考規格**：`OFFICE_SPEC.md`

---

### Phase 2：動畫系統（下週，3-4 小時）
**目標**：實現複雜動畫系統

**學習內容**：
- Three.js AnimationMixer
- 多動畫切換（idle、working、walking）
- 動畫混合（blending）

---

### Phase 3：角色建模（下下週，15-20 小時）
**目標**：創建專屬角色（櫻、焰、涼、琴、宵）

**學習內容**：
- 角色建模（基礎人體）
- 骨骼綁定（Rigging）
- 權重繪製（Weight Painting）
- 簡單動畫製作

**參考**：
- 日系角色比例（6 頭身）
- 原神風格參考

---

## 🛠️ 技術棧

### 前端渲染
- **Three.js**：3D 渲染引擎
- **GLTFLoader**：加載 GLTF 模型
- **OrbitControls**：相機控制

### 3D 建模
- **Blender**：免費開源 3D 套件
- **Python API**：程序化生成（進階）

### 素材來源
- **Sketchfab**：參考模型（不下載，只參考）
- **自己建模**：學習 Blender 創建

---

## 📋 學習筆記

### GLTF 格式優勢
- ✅ 開放標準（Khronos Group）
- ✅ 檔案小（二進制壓縮）
- ✅ 包含動畫、材質、骨骼
- ✅ Three.js 原生支持
- ✅ 瀏覽器直接加載

### Blender 建模原則
- **模組化設計**：重複使用組件
- **低多邊形**：保持性能
- **PBR 材質**：真實感渲染
- **清晰的命名**：便於管理

---

## 🎯 里程碑（更新）

### Week 1（本週）
- [x] Phase 1 完成：第一個 3D 場景 ✅
- [x] 創建辦公室規格書 ✅
- [x] Phase 1.5 進行中：辦公室建模
  - [x] Blender 安裝完成（3.0.1）✅
  - [x] Blender 基礎學習（1 小時）✅
  - [x] 創建 Python 腳本生成場景 ✅
  - [x] 生成 .blend 檔案 ✅
  - [ ] 學習 Blender GUI 操作（明天）
  - [ ] 手動導出 GLTF（明天）
  - [ ] Three.js 整合（後天）

### Week 2（下週）
- [ ] Phase 2 完成：動畫系統
- [ ] 添加角色模型（使用 Mixamo 免費模型）

### Week 3（下下週）
- [ ] Phase 3 啟動：角色建模
- [ ] 創建第一個專屬角色

---

## 📚 參考資源

### 官方文檔
- Three.js：https://threejs.org/docs/
- Blender Python API：https://docs.blender.org/api/current/
- GLTF 規格：https://www.khronos.org/gltf/

### Blender 教程
- Blender Guru（甜甜圈教程）：https://www.blenderguru.com/
- CG Cookie：https://cgcookie.com/
- Blender 官方教程：https://www.blender.org/support/tutorials/

### 免費素材（參考用）
- Sketchfab：https://sketchfab.com
- Mixamo（動畫）：https://www.mixamo.com

---

## 💡 學習心得

### 為什麼不用 PixiJS Graphics？
- ❌ 簡單幾何圖形（小學生畫風）
- ❌ 無法達到專業遊戲品質
- ❌ 不適合複雜場景和角色

### 為什麼選擇自己建模？
- ✅ 完全控制品質和風格
- ✅ 學習寶貴的 3D 技能
- ✅ 長期來看更靈活
- ✅ 節省尋找素材的時間

---

**建立日期**：2026-03-03
**最後更新**：2026-03-03
**預計完成**：2026-03-17（2 週）

### Phase 1: 快速原型（今天，2-3 小時）
**目標**：使用現成素材建立第一個 3D 場景

**資源**：
- **Sketchfab**：https://sketchfab.com/tags/gltf
- **Mixamo**：https://www.mixamo.com/
- **Three.js GLTFLoader**：官方教程

**步驟**：
1. ✅ 從 Sketchfab 下載免費 GLTF 角色模型
2. ✅ 使用 Three.js 加載 GLTF 模型
3. ✅ 播放模型內建動畫
4. ✅ 添加辦公室場景

**預期結果**：
- 真正的 3D 角色在辦公室中移動
- 專業遊戲品質視覺效果

---

### Phase 2: 動畫系統（明天，3-4 小時）
**目標**：實現複雜動畫系統

**學習內容**：
- Three.js AnimationMixer
- 多動畫切換（idle、working、walking）
- 動畫混合（blending）

**資源**：
- https://sbcode.net/threejs/gltf-animation/
- https://tympanus.net/codrops/2019/10/14/how-to-create-an-interactive-3d-character-with-three-js/

---

### Phase 3: Blender 基礎（本週，5-7 小時）
**目標**：學習 Blender Python API

**學習內容**：
- Blender 介面和基本操作
- Python API 基礎
- 程序化建模

**資源**：
- https://docs.blender.org/api/current/index.html
- https://docs.blender.org/api/current/info_quickstart.html
- https://demando.io/blog/dev-generating-a-procedural-solar-system-with-blenders-python-api

**練習**：
- 創建簡單的辦公室場景
- 創建基礎角色模型

---

### Phase 4: 高級角色創建（下週，10+ 小時）
**目標**：創建專屬角色（櫻、焰、涼、琴、宵）

**學習內容**：
- 角色建模
- 骨骼綁定（Rigging）
- 權重繪製（Weight Painting）
- 動畫製作

**工具**：
- Blender（建模、綁定、動畫）
- Mixamo（動畫庫）
- Substance Painter（紋理，可選）

---

## 🛠️ 技術棧

### 前端渲染
- **Three.js**：3D 渲染引擎
- **GLTFLoader**：加載 GLTF 模型
- **OrbitControls**：相機控制

### 3D 建模
- **Blender**：免費開源 3D 套件
- **Python API**：程序化生成

### 素材來源
- **Sketchfab**：免費 GLTF 模型
- **Mixamo**：免費動畫庫
- **BlenderKit**：免費 Blender 資源

---

## 📋 學習筆記

### GLTF 格式優勢
- ✅ 開放標準（Khronos Group）
- ✅ 檔案小（二進制壓縮）
- ✅ 包含動畫、材質、骨骼
- ✅ Three.js 原生支持
- ✅ 瀏覽器直接加載

### Mixamo 動畫庫
- **免費**：Adobe 帳號即可使用
- **角色**：預製角色（可下載 FBX）
- **動畫**：數千種動畫（走路、跑步、打字等）
- **格式**：FBX（需轉換為 GLTF）

---

## 🎯 里程碑

### Week 1（本週）
- [x] 學習計劃制定
- [x] Phase 1 完成：第一個 3D 場景
  - [x] 下載 Xbot.glb 模型（2.8 MB）
  - [x] 創建 Three.js 場景
  - [x] 實現 GLTF 模型加載
  - [x] 添加燈光和陰影
  - [x] 添加 OrbitControls
  - [x] 安裝 Three.js 套件（0.160.0）
- [ ] Phase 2 進行中：動畫系統

### Week 2（下週）
- [ ] Phase 3 完成：Blender 基礎
- [ ] 創建簡單辦公室場景

### Week 3（下下週）
- [ ] Phase 4 啟動：角色建模
- [ ] 創建第一個專屬角色

---

## 📚 參考資源

### 官方文檔
- Three.js：https://threejs.org/docs/
- Blender Python API：https://docs.blender.org/api/current/
- GLTF 規格：https://www.khronos.org/gltf/

### 教程網站
- Three.js Tutorials：https://sbcode.net/threejs/
- Codrops：https://tympanus.net/codrops/
- Blender Guru：https://www.blenderguru.com/

### 免費素材
- Sketchfab：https://sketchfab.com
- Mixamo：https://www.mixamo.com
- BlenderKit：https://www.blenderkit.com/

---

## 💡 學習心得

### 為什麼不用 PixiJS Graphics？
- ❌ 簡單幾何圖形（小學生畫風）
- ❌ 無法達到專業遊戲品質
- ❌ 不適合複雜角色動畫

### 為什麼選擇 GLTF + Three.js？
- ✅ 專業遊戲標準格式
- ✅ 豐富的免費素材
- ✅ 學習曲線較平緩
- ✅ 即時渲染性能優異

---

**建立日期**：2026-03-03
**預計完成**：2026-03-17（2 週）
