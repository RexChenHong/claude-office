#!/usr/bin/env python3
"""
創建雙螢幕工作站
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

# 創建材質
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

# 材質定義
mat_screen = create_material("Screen_LCD", (0.1, 0.1, 0.12, 1), roughness=0.1, emission=(0.2, 0.25, 0.3, 1))
mat_bezel = create_material("Bezel_Black", (0.05, 0.05, 0.05, 1), roughness=0.3)
mat_stand = create_material("Stand_Silver", (0.7, 0.7, 0.72, 1), roughness=0.2, metallic=0.8)
mat_base = create_material("Base_Heavy", (0.6, 0.6, 0.62, 1), roughness=0.3, metallic=0.6)

# 創建群組
bpy.ops.object.empty_add(type='PLAIN_AXES')
monitor_group = bpy.context.active_object
monitor_group.name = "Dual_Monitors"
monitor_group.location = (0, 0, 0)

# 螢幕尺寸（27 吋 = 約 60cm x 34cm）
SCREEN_WIDTH = 0.6
SCREEN_HEIGHT = 0.34
SCREEN_DEPTH = 0.03
BEZEL_WIDTH = 0.008  # 薄邊框

def create_single_monitor(x_offset, rotation_y=0):
    """創建單個螢幕"""

    # 螢幕面板
    bpy.ops.mesh.primitive_cube_add(size=1)
    panel = bpy.context.active_object
    panel.name = f"Screen_Panel_{x_offset:.1f}"
    panel.scale = (SCREEN_WIDTH, SCREEN_DEPTH, SCREEN_HEIGHT)
    panel.location = (x_offset, -0.55, 0.6)
    panel.rotation_euler = (0, rotation_y, 0)
    panel.data.materials.append(mat_screen)
    panel.parent = monitor_group

    # 邊框（上）
    bpy.ops.mesh.primitive_cube_add(size=1)
    bezel_top = bpy.context.active_object
    bezel_top.name = "Bezel_Top"
    bezel_top.scale = (SCREEN_WIDTH + BEZEL_WIDTH*2, SCREEN_DEPTH + 0.01, BEZEL_WIDTH)
    bezel_top.location = (x_offset, -0.55, 0.6 + SCREEN_HEIGHT + BEZEL_WIDTH/2)
    bezel_top.rotation_euler = (0, rotation_y, 0)
    bezel_top.data.materials.append(mat_bezel)
    bezel_top.parent = monitor_group

    # 邊框（下）
    bpy.ops.mesh.primitive_cube_add(size=1)
    bezel_bottom = bpy.context.active_object
    bezel_bottom.name = "Bezel_Bottom"
    bezel_bottom.scale = (SCREEN_WIDTH + BEZEL_WIDTH*2, SCREEN_DEPTH + 0.01, BEZEL_WIDTH)
    bezel_bottom.location = (x_offset, -0.55, 0.6 - SCREEN_HEIGHT - BEZEL_WIDTH/2)
    bezel_bottom.rotation_euler = (0, rotation_y, 0)
    bezel_bottom.data.materials.append(mat_bezel)
    bezel_bottom.parent = monitor_group

    # 邊框（左）
    bpy.ops.mesh.primitive_cube_add(size=1)
    bezel_left = bpy.context.active_object
    bezel_left.name = "Bezel_Left"
    bezel_left.scale = (BEZEL_WIDTH, SCREEN_DEPTH + 0.01, SCREEN_HEIGHT*2 + BEZEL_WIDTH*2)
    bezel_left.location = (x_offset - SCREEN_WIDTH - BEZEL_WIDTH/2, -0.55, 0.6)
    bezel_left.rotation_euler = (0, rotation_y, 0)
    bezel_left.data.materials.append(mat_bezel)
    bezel_left.parent = monitor_group

    # 邊框（右）
    bpy.ops.mesh.primitive_cube_add(size=1)
    bezel_right = bpy.context.active_object
    bezel_right.name = "Bezel_Right"
    bezel_right.scale = (BEZEL_WIDTH, SCREEN_DEPTH + 0.01, SCREEN_HEIGHT*2 + BEZEL_WIDTH*2)
    bezel_right.location = (x_offset + SCREEN_WIDTH + BEZEL_WIDTH/2, -0.55, 0.6)
    bezel_right.rotation_euler = (0, rotation_y, 0)
    bezel_right.data.materials.append(mat_bezel)
    bezel_right.parent = monitor_group

    return panel

# 創建主螢幕（中間偏左）
create_single_monitor(-0.32, 0)

# 創建副螢幕（中間偏右，微微旋轉）
create_single_monitor(0.32, math.radians(10))

# ===== 支架系統 =====

# 垂直支架
bpy.ops.mesh.primitive_cube_add(size=1)
stand_vertical = bpy.context.active_object
stand_vertical.name = "Stand_Vertical"
stand_vertical.scale = (0.04, 0.04, 0.35)
stand_vertical.location = (0, -0.55, 0.28)
stand_vertical.data.materials.append(mat_stand)
stand_vertical.parent = monitor_group

# 水平支架（連接兩個螢幕）
bpy.ops.mesh.primitive_cube_add(size=1)
stand_horizontal = bpy.context.active_object
stand_horizontal.name = "Stand_Horizontal"
stand_horizontal.scale = (0.7, 0.02, 0.02)
stand_horizontal.location = (0, -0.57, 0.45)
stand_horizontal.data.materials.append(mat_stand)
stand_horizontal.parent = monitor_group

# ===== 底座 =====

# 底座柱
bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.08)
base_pillar = bpy.context.active_object
base_pillar.name = "Base_Pillar"
base_pillar.location = (0, -0.55, 0.08)
base_pillar.data.materials.append(mat_stand)
base_pillar.parent = monitor_group

# 底座盤（橢圓形）
bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.01)
base_plate = bpy.context.active_object
base_plate.name = "Base_Plate"
base_plate.scale = (1, 0.8, 1)  # 橢圓形
base_plate.location = (0, -0.55, 0.02)
base_plate.data.materials.append(mat_base)
base_plate.parent = monitor_group

print("✅ 雙螢幕模型創建完成！")
print("包含：2 個螢幕 + 薄邊框 + 支架 + 底座")
