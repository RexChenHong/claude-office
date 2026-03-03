# Blender 學習筆記 - Day 1

## 📚 今日學習內容（2026-03-03）

### ✅ 完成項目

1. **Blender 安裝**（5 分鐘）
   - 版本：Blender 3.0.1
   - 位置：`/usr/bin/blender`
   - 大小：837 MB（包含依賴庫）

2. **Python API 基礎**（30 分鐘）
   - 學習 `bpy` 模組
   - 基礎操作：創建、縮放、定位
   - 物件命名與管理

3. **創建第一個場景**（1 小時）
   - 辦公桌（桌面 + 桌腿）
   - 辦公椅（座椅 + 椅背）
   - 地板、燈光、相機
   - 保存 .blend 檔案

---

## 🎯 學習成果

### 創建的檔案
1. **OFFICE_SPEC.md**：詳細的辦公室規格書
2. **create_office.py**：Blender Python 腳本
3. **office_scene.blend**：Blender 場景檔案

### 代碼示例

#### 創建立方體
```python
import bpy

# 創建立方體
bpy.ops.mesh.primitive_cube_add()
obj = bpy.context.active_object

# 設置名稱、縮放、位置
obj.name = "My_Cube"
obj.scale = (1, 1, 1)
obj.location = (0, 0, 0)
```

#### 創建平面
```python
bpy.ops.mesh.primitive_plane_add()
floor = bpy.context.active_object
floor.scale = (10, 10, 1)
```

#### 創建燈光
```python
# 太陽光
bpy.ops.object.light_add(type='SUN')
sun = bpy.context.active_object
sun.location = (5, 5, 10)
sun.data.energy = 5

# 區域光
bpy.ops.object.light_add(type='AREA')
area = bpy.context.active_object
area.data.energy = 100
```

---

## 🚧 遇到的問題

### 問題 1：GLTF 導出失敗
**錯誤訊息**：
```
'/usr/bin/3.0/python/lib/python3.10/site-packages/libextern_draco.so' does not exist
```

**原因**：
- Blender 3.0 的 GLTF 導出需要 draco 壓縮庫
- Ubuntu 版本的 Blender 缺少此庫

**解決方案**：
1. 短期：保存 .blend 檔案，手動在 GUI 導出
2. 長期：安裝 draco 庫或升級 Blender

### 問題 2：API 參數錯誤
**錯誤代碼**：
```python
bpy.ops.mesh.primitive_plane_add(scale=(10, 10))  # ❌ 錯誤
```

**正確代碼**：
```python
bpy.ops.mesh.primitive_cube_add()  # ✅ 正確
obj = bpy.context.active_object
obj.scale = (10, 10, 1)
```

**原因**：Blender 3.0 的 `primitive_*_add()` 不接受 `scale` 參數

---

## 💡 學習心得

### 1. Blender Python API 的特點
- **優點**：
  - 程序化建模（適合重複性工作）
  - 可批量創建物件
  - 可精確控制參數
- **缺點**：
  - 需要 GUI 操作的功能無法自動化（如部分導出）
  - 文檔不夠詳細
  - 版本差異大（2.8 vs 3.0）

### 2. 建模思維
- **模組化設計**：將場景拆分為獨立組件
- **參數化建模**：使用變數控制尺寸
- **層級結構**：合理的命名規範

### 3. 工作流程
```
1. 規格設計（OFFICE_SPEC.md）
2. Python 腳本（create_office.py）
3. 生成 .blend 檔案
4. 手動導出 GLTF
5. Three.js 整合
```

---

## 📋 明日計劃（2026-03-04）

### Phase 1.5 繼續（預計 2-3 小時）

1. **學習 Blender GUI 操作**（1 小時）
   - 開啟 office_scene.blend
   - 學習導航（旋轉、縮放、平移）
   - 學習選取、移動、縮放工具
   - 學習材質設置

2. **手動導出 GLTF**（30 分鐘）
   - File → Export → glTF 2.0
   - 選擇導出選項
   - 測試導出結果

3. **Three.js 整合**（1 小時）
   - 更新 main-threejs.js
   - 加載新模型
   - 調整相機和燈光
   - 測試渲染效果

---

## 🎯 里程碑

### Week 1 Day 1（今天）✅
- [x] Blender 安裝
- [x] Python API 基礎
- [x] 創建第一個場景
- [x] 保存 .blend 檔案

### Week 1 Day 2（明天）
- [ ] Blender GUI 基礎
- [ ] 手動導出 GLTF
- [ ] Three.js 整合測試

### Week 1 Day 3（後天）
- [ ] 添加更多細節（電腦、書本、植物）
- [ ] 材質和紋理
- [ ] 優化模型

---

## 📚 學習資源

### 官方文檔
- Blender Python API：https://docs.blender.org/api/3.0/
- Blender 手冊：https://docs.blender.org/manual/en/3.0/

### 教程
- Blender Guru（甜甜圈教程）：https://www.blenderguru.com/
- CG Cookie：https://cgcookie.com/

---

## 🔄 下一步行動

### 立即行動（現在）
1. 提交 Git 變更 ✅
2. 向溫水報告進度
3. 休息，準備明天的學習

### 明天行動（2026-03-04）
1. 早上：學習 Blender GUI（1 小時）
2. 下午：導出 GLTF + Three.js 整合（2 小時）
3. 晚上：測試和優化（1 小時）

---

**學習時間**：今天 1.5 小時
**累計時間**：1.5 小時 / 40 小時（3.75%）
**學習進度**：Phase 1.5 進行中（30% 完成）
