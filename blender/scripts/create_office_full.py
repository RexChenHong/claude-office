#!/usr/bin/env python3
"""
創建完整 5 人辦公室場景
"""

import sys

# 修復 numpy 路徑問題
user_site = '/home/rex/.local/lib/python3.10/site-packages'
if user_site not in sys.path:
    sys.path.insert(0, user_site)

import bpy
import math

# 清除場景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 清除孤立數據
for block in bpy.data.meshes:
    if block.users == 0:
        bpy.data.meshes.remove(block)
for block in bpy.data.materials:
    if block.users == 0:
        bpy.data.materials.remove(block)

# ========== 材質定義 ==========

def create_material(name, color, roughness=0.5, metallic=0.0, emission=None):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    if emission:
        bsdf.inputs['Emission'].default_value = emission
        bsdf.inputs['Emission Strength'].default_value = 0.5
    return mat

# 辦公室材質
mat_floor = create_material("Floor_Wood", (0.6, 0.45, 0.3, 1), roughness=0.6)
mat_wall = create_material("Wall_White", (0.95, 0.95, 0.95, 1), roughness=0.9)
mat_ceiling = create_material("Ceiling", (0.98, 0.98, 0.98, 1), roughness=0.95)
mat_glass = create_material("Glass", (0.7, 0.85, 0.95, 0.3), roughness=0.1, metallic=0.0)
mat_metal_frame = create_material("Metal_Frame", (0.3, 0.3, 0.35, 1), roughness=0.3, metallic=0.8)

# 家具材質
mat_desktop = create_material("Desktop_White", (0.92, 0.92, 0.9, 1), roughness=0.3)
mat_seat = create_material("Seat_Fabric", (0.2, 0.2, 0.25, 1), roughness=0.8)
mat_metal = create_material("Metal_Silver", (0.5, 0.5, 0.55, 1), roughness=0.2, metallic=0.9)
mat_plastic = create_material("Plastic_Black", (0.1, 0.1, 0.1, 1), roughness=0.4)
mat_screen = create_material("Screen_LCD", (0.1, 0.1, 0.12, 1), roughness=0.1, emission=(0.2, 0.25, 0.3, 1))
mat_bezel = create_material("Bezel_Black", (0.05, 0.05, 0.05, 1), roughness=0.3)
mat_keycap = create_material("Keycap_Dark", (0.15, 0.15, 0.15, 1), roughness=0.4)
mat_led = create_material("LED_Strip", (0.2, 0.5, 0.8, 1), roughness=0.2)
mat_lamp = create_material("Lamp_White", (0.95, 0.95, 0.95, 1), roughness=0.5)
mat_lamp_light = create_material("Lamp_Light", (1.0, 0.98, 0.9, 1), roughness=0.1, emission=(1, 0.98, 0.9, 1))
mat_plant_pot = create_material("Plant_Pot", (0.6, 0.4, 0.3, 1), roughness=0.7)
mat_plant_leaf = create_material("Plant_Leaf", (0.2, 0.5, 0.2, 1), roughness=0.6)

# ========== 辦公室主體 ==========

# 地板（20m x 20m）
bpy.ops.mesh.primitive_plane_add(size=20)
floor = bpy.context.active_object
floor.name = "Floor"
floor.location = (0, 0, 0)
floor.data.materials.append(mat_floor)

# 天花板
bpy.ops.mesh.primitive_plane_add(size=20)
ceiling = bpy.context.active_object
ceiling.name = "Ceiling"
ceiling.location = (0, 0, 2.8)
ceiling.rotation_euler = (math.pi, 0, 0)
ceiling.data.materials.append(mat_ceiling)

# 牆面
# 後牆
bpy.ops.mesh.primitive_plane_add(size=20)
back_wall = bpy.context.active_object
back_wall.name = "Back_Wall"
back_wall.scale = (1, 1, 2.8/10)
back_wall.location = (0, -10, 1.4)
back_wall.rotation_euler = (math.pi/2, 0, 0)
back_wall.data.materials.append(mat_wall)

# 左牆
bpy.ops.mesh.primitive_plane_add(size=20)
left_wall = bpy.context.active_object
left_wall.name = "Left_Wall"
left_wall.scale = (1, 1, 2.8/10)
left_wall.location = (-10, 0, 1.4)
left_wall.rotation_euler = (math.pi/2, 0, math.pi/2)
left_wall.data.materials.append(mat_wall)

# 右牆（帶落地窗）
bpy.ops.mesh.primitive_plane_add(size=20)
right_wall = bpy.context.active_object
right_wall.name = "Right_Wall"
right_wall.scale = (1, 1, 2.8/10)
right_wall.location = (10, 0, 1.4)
right_wall.rotation_euler = (math.pi/2, 0, -math.pi/2)
right_wall.data.materials.append(mat_wall)

# 落地窗（右牆中央）
bpy.ops.mesh.primitive_plane_add(size=8)
window = bpy.context.active_object
window.name = "Window_Glass"
window.scale = (1, 1, 2.5/8)
window.location = (9.95, 0, 1.3)
window.rotation_euler = (math.pi/2, 0, -math.pi/2)
window.data.materials.append(mat_glass)

# 窗框
for i in range(4):
    bpy.ops.mesh.primitive_cube_add(size=1)
    frame = bpy.context.active_object
    frame.name = f"Window_Frame_{i}"
    frame.scale = (0.05, 2, 2.5/2)
    frame.location = (9.97, -3 + i*2, 1.3)
    frame.data.materials.append(mat_metal_frame)

# ========== 工作站創建函數 ==========

def create_workstation(x, y, index):
    """創建單個工作站"""

    # 創建群組
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    ws_group = bpy.context.active_object
    ws_group.name = f"Workstation_{index}"
    ws_group.location = (x, y, 0)

    # ===== 1. 桌子 =====
    # 桌面
    bpy.ops.mesh.primitive_cube_add(size=1)
    desktop = bpy.context.active_object
    desktop.name = f"Desktop_{index}"
    desktop.scale = (1.2, 0.6, 0.025)
    desktop.location = (x, y, 0.75)
    desktop.data.materials.append(mat_desktop)
    desktop.parent = ws_group

    # 桌腿
    leg_positions = [(-0.55, -0.25), (-0.55, 0.25), (0.55, -0.25), (0.55, 0.25)]
    for i, (lx, ly) in enumerate(leg_positions):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.725)
        leg = bpy.context.active_object
        leg.name = f"Leg_{index}_{i+1}"
        leg.location = (x + lx, y + ly, 0.3625)
        leg.data.materials.append(mat_metal)
        leg.parent = ws_group

    # ===== 2. 雙螢幕 =====
    SCREEN_WIDTH = 0.6
    SCREEN_HEIGHT = 0.34

    # 主螢幕
    bpy.ops.mesh.primitive_cube_add(size=1)
    panel1 = bpy.context.active_object
    panel1.name = f"Screen_1_{index}"
    panel1.scale = (SCREEN_WIDTH, 0.03, SCREEN_HEIGHT)
    panel1.location = (x - 0.32, y - 0.55, 1.1)
    panel1.data.materials.append(mat_screen)
    panel1.parent = ws_group

    # 副螢幕
    bpy.ops.mesh.primitive_cube_add(size=1)
    panel2 = bpy.context.active_object
    panel2.name = f"Screen_2_{index}"
    panel2.scale = (SCREEN_WIDTH, 0.03, SCREEN_HEIGHT)
    panel2.location = (x + 0.32, y - 0.55, 1.1)
    panel2.rotation_euler = (0, 0, math.radians(10))
    panel2.data.materials.append(mat_screen)
    panel2.parent = ws_group

    # 支架
    bpy.ops.mesh.primitive_cube_add(size=1)
    stand = bpy.context.active_object
    stand.name = f"Monitor_Stand_{index}"
    stand.scale = (0.04, 0.04, 0.35)
    stand.location = (x, y - 0.55, 0.78)
    stand.data.materials.append(mat_metal)
    stand.parent = ws_group

    # 底座
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.01)
    base = bpy.context.active_object
    base.name = f"Monitor_Base_{index}"
    base.scale = (1, 0.8, 1)
    base.location = (x, y - 0.55, 0.52)
    base.data.materials.append(mat_metal)
    base.parent = ws_group

    # ===== 3. 鍵盤 =====
    bpy.ops.mesh.primitive_cube_add(size=1)
    kb = bpy.context.active_object
    kb.name = f"Keyboard_{index}"
    kb.scale = (0.35, 0.12, 0.015)
    kb.location = (x, y - 0.25, 0.43)
    kb.data.materials.append(mat_plastic)
    kb.parent = ws_group

    # ===== 4. 滑鼠 =====
    bpy.ops.mesh.primitive_cube_add(size=1)
    mouse = bpy.context.active_object
    mouse.name = f"Mouse_{index}"
    mouse.scale = (0.06, 0.11, 0.03)
    mouse.location = (x + 0.25, y - 0.25, 0.43)
    mouse.data.materials.append(mat_plastic)
    mouse.parent = ws_group

    # ===== 5. 辦公椅 =====
    # 座椅
    bpy.ops.mesh.primitive_cube_add(size=1)
    seat = bpy.context.active_object
    seat.name = f"Seat_{index}"
    seat.scale = (0.45, 0.4, 0.08)
    seat.location = (x, y + 0.6, 0.48)
    seat.data.materials.append(mat_seat)
    seat.parent = ws_group

    # 椅背
    bpy.ops.mesh.primitive_cube_add(size=1)
    back = bpy.context.active_object
    back.name = f"Backrest_{index}"
    back.scale = (0.42, 0.06, 0.5)
    back.location = (x, y + 0.82, 0.78)
    back.rotation_euler = (math.radians(10), 0, 0)
    back.data.materials.append(mat_seat)
    back.parent = ws_group

    # 椅子支柱
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.25)
    pillar = bpy.context.active_object
    pillar.name = f"Chair_Pillar_{index}"
    pillar.location = (x, y + 0.6, 0.32)
    pillar.data.materials.append(mat_metal)
    pillar.parent = ws_group

    # 五星腳
    for i in range(5):
        angle = i * (2 * math.pi / 5)
        lx = math.cos(angle) * 0.25
        ly = math.sin(angle) * 0.25

        bpy.ops.mesh.primitive_cube_add(size=1)
        arm = bpy.context.active_object
        arm.name = f"Chair_Arm_{index}_{i+1}"
        arm.scale = (0.28, 0.03, 0.02)
        arm.location = (x + lx/2, y + 0.6 + ly/2, 0.09)
        arm.rotation_euler = (0, 0, angle)
        arm.data.materials.append(mat_metal)
        arm.parent = ws_group

        # 輪子
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.025)
        wheel = bpy.context.active_object
        wheel.name = f"Wheel_{index}_{i+1}"
        wheel.location = (x + lx, y + 0.6 + ly, 0.025)
        wheel.data.materials.append(mat_plastic)
        wheel.parent = ws_group

    # ===== 6. 檯燈 =====
    # 燈座
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.02)
    lamp_base = bpy.context.active_object
    lamp_base.name = f"Lamp_Base_{index}"
    lamp_base.location = (x + 0.5, y - 0.2, 0.52)
    lamp_base.data.materials.append(mat_lamp)
    lamp_base.parent = ws_group

    # 燈臂
    bpy.ops.mesh.primitive_cylinder_add(radius=0.01, depth=0.35)
    lamp_arm = bpy.context.active_object
    lamp_arm.name = f"Lamp_Arm_{index}"
    lamp_arm.location = (x + 0.5, y - 0.2, 0.7)
    lamp_arm.data.materials.append(mat_metal)
    lamp_arm.parent = ws_group

    # 燈罩
    bpy.ops.mesh.primitive_cone_add(radius1=0.08, radius2=0.05, depth=0.1)
    lamp_shade = bpy.context.active_object
    lamp_shade.name = f"Lamp_Shade_{index}"
    lamp_shade.location = (x + 0.5, y - 0.2, 0.92)
    lamp_shade.rotation_euler = (math.pi, 0, 0)
    lamp_shade.data.materials.append(mat_lamp)
    lamp_shade.parent = ws_group

    # ===== 7. 盆栽 =====
    # 花盆
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.1)
    pot = bpy.context.active_object
    pot.name = f"Pot_{index}"
    pot.location = (x - 0.5, y - 0.2, 0.52)
    pot.data.materials.append(mat_plant_pot)
    pot.parent = ws_group

    # 植物葉片（簡化）
    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.12)
    plant = bpy.context.active_object
    plant.name = f"Plant_{index}"
    plant.location = (x - 0.5, y - 0.2, 0.65)
    plant.scale = (1, 1, 1.3)
    plant.data.materials.append(mat_plant_leaf)
    plant.parent = ws_group

    return ws_group

# ========== 創建 5 個工作站 ==========

for i in range(5):
    x = -6 + i * 3  # 間距 3m
    y = 0
    create_workstation(x, y, i + 1)

print("✅ 5 人辦公室場景創建完成！")
print("包含：地板、牆面、天花板、落地窗、5 個工作站（桌子、椅子、螢幕、鍵盤、檯燈、盆栽）")
