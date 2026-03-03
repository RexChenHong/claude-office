# Blender 學習筆記

## 📅 學習日期：2026-03-03

---

## 🎯 學習目標
掌握 Blender 建模技能，創建 Sketchfab 等級的 5 人辦公室場景。

---

## Phase 1：Blender 基礎

### 1.1 Blender 安裝與啟動

#### 檢查 Blender 版本
```bash
blender --version
```

#### 啟動 Blender（無 GUI）
```bash
blender -b  # 背景模式
blender -P script.py  # 執行 Python 腳本
```

### 1.2 基礎操作

#### 介面佈局
- **3D Viewport**：主要建模區域
- **Outliner**：場景物件列表
- **Properties**：材質、燈光設置
- **Timeline**：動畫時間軸

#### 快捷鍵
- **導航**：
  - `中鍵拖曳`：旋轉視角
  - `Shift + 中鍵`：平移視角
  - `滾輪`：縮放
  - `Numpad 1/3/7`：前/右/上視角

- **物件操作**：
  - `G`：移動（Grab）
  - `R`：旋轉（Rotate）
  - `S`：縮放（Scale）
  - `X/Y/Z`：限制軸向
  - `Shift + G/R/S`：精細調整

- **編輯模式**：
  - `Tab`：切換編輯模式
  - `1/2/3`：點/線/面選擇
  - `E`：擠出（Extrude）
  - `I`：內插（Inset）
  - `Ctrl + B`：倒角（Bevel）
  - `Ctrl + R`：環切（Loop Cut）

- **其他**：
  - `Z`：著色模式（Wireframe/Solid/Material/Rendered）
  - `Shift + A`：添加物件
  - `X` 或 `Delete`：刪除
  - `Ctrl + S`：保存
  - `Ctrl + Z`：復原
  - `Shift + Ctrl + Z`：重做

### 1.3 基礎建模練習

#### 練習 1：簡單桌子
```python
import bpy

# 清除場景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 創建桌面
bpy.ops.mesh.primitive_cube_add(size=1)
desktop = bpy.context.active_object
desktop.name = "Desktop"
desktop.scale = (1.2, 0.6, 0.025)  # 1.2m x 0.6m x 0.025m
desktop.location = (0, 0, 0.75)

# 創建桌腿（4 個）
leg_positions = [(-0.55, -0.25), (-0.55, 0.25), (0.55, -0.25), (0.55, 0.25)]
for i, (x, y) in enumerate(leg_positions):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.725)
    leg = bpy.context.active_object
    leg.name = f"Leg_{i+1}"
    leg.location = (x, y, 0.3625)
```

#### 練習 2：辦公椅
```python
# 座椅
bpy.ops.mesh.primitive_cube_add(size=1)
seat = bpy.context.active_object
seat.name = "Seat"
seat.scale = (0.5, 0.5, 0.1)
seat.location = (0, 0, 0.5)

# 椅背
bpy.ops.mesh.primitive_cube_add(size=1)
back = bpy.context.active_object
back.name = "Back"
back.scale = (0.5, 0.1, 0.6)
back.location = (0, 0.2, 0.8)
```

---

## Phase 2：辦公室建模

### 2.1 建築結構

#### 地板（20m x 20m）
```python
bpy.ops.mesh.primitive_plane_add(size=20)
floor = bpy.context.active_object
floor.name = "Floor"
```

#### 牆面
```python
# 後牆
bpy.ops.mesh.primitive_plane_add(size=20)
back_wall = bpy.context.active_object
back_wall.name = "BackWall"
back_wall.scale = (1, 1, 2.8)  # 2.8m 高
back_wall.location = (0, 1.4, -10)
back_wall.rotation_euler = (math.pi/2, 0, 0)

# 左牆
bpy.ops.mesh.primitive_plane_add(size=20)
left_wall = bpy.context.active_object
left_wall.name = "LeftWall"
left_wall.scale = (1, 1, 2.8)
left_wall.location = (-10, 1.4, 0)
left_wall.rotation_euler = (math.pi/2, 0, math.pi/2)
```

### 2.2 5 個工作站

按照 `LAYOUT_V4.md` 佈局：

```python
# 創建 5 個工作站（一字排開）
for i in range(5):
    x = -6 + i * 3
    z = 0
    create_workstation(x, z, i+1)

def create_workstation(x, z, index):
    # 創建群組
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    workstation = bpy.context.active_object
    workstation.name = f"Workstation_{index}"
    workstation.location = (x, 0, z)
    
    # 創建桌子（相對位置）
    create_desk(x, z)
    create_chair(x, z)
    create_monitors(x, z)
```

### 2.3 材質設置

#### PBR 材質（Principled BSDF）
```python
# 木地板材質
mat_wood = bpy.data.materials.new(name="Wood_Floor")
mat_wood.use_nodes = True
nodes = mat_wood.node_tree.nodes

# Principled BSDF
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.6, 0.4, 0.2, 1)  # 木色
bsdf.inputs['Roughness'].default_value = 0.4
bsdf.inputs['Metallic'].default_value = 0.0

# 應用到地板
floor.data.materials.append(mat_wood)
```

---

## Phase 3：導出與整合

### 3.1 導出 GLTF

#### Blender 操作
```
File → Export → glTF 2.0 (.glb/.gltf)

設置：
- Format: glTF Separate (.gltf + .bin + textures)
- Include: ✅ Custom Properties, ✅ Cameras, ✅ Lights
- Transform: +Y Up
- Mesh: ✅ Apply Modifiers
- Material: ✅ Export Materials
```

#### Python 腳本
```python
import bpy

# 導出 GLTF
bpy.ops.export_scene.gltf(
    filepath='/mnt/e_drive/claude-office/blender/exports/office.glb',
    export_format='GLB',
    export_cameras=True,
    export_lights=True,
    export_extras=True
)
```

### 3.2 Three.js 整合

```javascript
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

const loader = new GLTFLoader();

loader.load(
  '/blender/exports/office.glb',
  (gltf) => {
    scene.add(gltf.scene);
    console.log('辦公室模型載入完成！');
    
    // 調整相機位置
    camera.position.set(15, 12, 15);
    camera.lookAt(0, 0, 0);
  },
  (progress) => {
    console.log('載入進度：', (progress.loaded / progress.total * 100) + '%');
  },
  (error) => {
    console.error('載入錯誤：', error);
  }
);
```

---

## 📝 學習筆記

### 2026-03-03 18:30
- ✅ 遠端桌面已修復（chrome-remote-desktop --enable-and-start）
- ⏳ 開始 Phase 1 學習
- 📚 參考資料：
  - Blender 官方文檔：https://docs.blender.org/
  - Blender Guru：https://www.blenderguru.com/
  - Poly Haven（免費貼圖）：https://polyhaven.com/

---

## 🎯 下一步

1. **立即執行**：
   - [ ] 檢查 Blender 版本
   - [ ] 創建第一個簡單模型（桌子）
   - [ ] 學習基礎操作

2. **今日目標**：
   - [ ] 完成 Phase 1（基礎）
   - [ ] 建立第一個工作站模型

3. **明日目標**：
   - [ ] 完成 Phase 2（辦公室建模）
   - [ ] 應用材質與貼圖

---

**最後更新**：2026-03-03 18:30 (Asia/Taipei)
