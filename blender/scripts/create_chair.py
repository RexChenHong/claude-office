#!/usr/bin/env python3
"""
創建精緻辦公椅模型
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
def create_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    return mat

# 材質定義
mat_seat = create_material("Seat_Fabric", (0.2, 0.2, 0.25, 1), roughness=0.8)  # 深灰布料
mat_metal = create_material("Chair_Metal", (0.3, 0.3, 0.35, 1), roughness=0.3, metallic=0.8)  # 金屬
mat_plastic = create_material("Plastic_Black", (0.1, 0.1, 0.1, 1), roughness=0.4)  # 黑色塑料

# 創建群組
bpy.ops.object.empty_add(type='PLAIN_AXES')
chair_group = bpy.context.active_object
chair_group.name = "Office_Chair"
chair_group.location = (0, 0, 0)

# ===== 1. 座椅（帶弧度）=====
bpy.ops.mesh.primitive_cube_add(size=1)
seat = bpy.context.active_object
seat.name = "Seat"
seat.scale = (0.45, 0.4, 0.08)
seat.location = (0, 0, 0.48)
seat.data.materials.append(mat_seat)
seat.parent = chair_group

# 座椅邊緣修飾
bpy.ops.mesh.primitive_cube_add(size=1)
seat_edge = bpy.context.active_object
seat_edge.name = "Seat_Edge"
seat_edge.scale = (0.48, 0.43, 0.03)
seat_edge.location = (0, 0, 0.44)
seat_edge.data.materials.append(mat_plastic)
seat_edge.parent = chair_group

# ===== 2. 椅背（帶弧度）=====
bpy.ops.mesh.primitive_cube_add(size=1)
back = bpy.context.active_object
back.name = "Backrest"
back.scale = (0.42, 0.06, 0.5)
back.location = (0, -0.22, 0.78)
back.rotation_euler = (math.radians(10), 0, 0)  # 微微後傾
back.data.materials.append(mat_seat)
back.parent = chair_group

# 椅背框架
bpy.ops.mesh.primitive_cube_add(size=1)
back_frame = bpy.context.active_object
back_frame.name = "Backrest_Frame"
back_frame.scale = (0.46, 0.03, 0.54)
back_frame.location = (0, -0.26, 0.78)
back_frame.rotation_euler = (math.radians(10), 0, 0)
back_frame.data.materials.append(mat_plastic)
back_frame.parent = chair_group

# ===== 3. 扶手（左右）=====
def create_armrest(x_pos):
    # 扶手支柱
    bpy.ops.mesh.primitive_cube_add(size=1)
    support = bpy.context.active_object
    support.name = f"Armrest_Support_{'L' if x_pos < 0 else 'R'}"
    support.scale = (0.03, 0.03, 0.2)
    support.location = (x_pos, -0.15, 0.55)
    support.data.materials.append(mat_metal)
    support.parent = chair_group

    # 扶手墊
    bpy.ops.mesh.primitive_cube_add(size=1)
    pad = bpy.context.active_object
    pad.name = f"Armrest_Pad_{'L' if x_pos < 0 else 'R'}"
    pad.scale = (0.06, 0.15, 0.02)
    pad.location = (x_pos, -0.05, 0.66)
    pad.data.materials.append(mat_seat)
    pad.parent = chair_group

create_armrest(-0.28)  # 左扶手
create_armrest(0.28)   # 右扶手

# ===== 4. 座椅支柱 =====
bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.25)
pillar = bpy.context.active_object
pillar.name = "Seat_Pillar"
pillar.location = (0, 0, 0.32)
pillar.data.materials.append(mat_metal)
pillar.parent = chair_group

# 氣壓缸外殼
bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.1)
gas_cylinder = bpy.context.active_object
gas_cylinder.name = "Gas_Cylinder"
gas_cylinder.location = (0, 0, 0.18)
gas_cylinder.data.materials.append(mat_metal)
gas_cylinder.parent = chair_group

# ===== 5. 五星腳底座 =====
bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.04)
center_hub = bpy.context.active_object
center_hub.name = "Base_Hub"
center_hub.location = (0, 0, 0.1)
center_hub.data.materials.append(mat_metal)
center_hub.parent = chair_group

# 五個腳
for i in range(5):
    angle = i * (2 * math.pi / 5)
    x = math.cos(angle) * 0.25
    y = math.sin(angle) * 0.25

    # 腳臂
    bpy.ops.mesh.primitive_cube_add(size=1)
    arm = bpy.context.active_object
    arm.name = f"Leg_Arm_{i+1}"
    arm.scale = (0.28, 0.03, 0.02)
    arm.location = (x/2, y/2, 0.09)
    arm.rotation_euler = (0, 0, angle)
    arm.data.materials.append(mat_metal)
    arm.parent = chair_group

    # 輪子
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.025)
    wheel = bpy.context.active_object
    wheel.name = f"Wheel_{i+1}"
    wheel.location = (x, y, 0.025)
    wheel.data.materials.append(mat_plastic)
    wheel.parent = chair_group

# ===== 6. 設置原點 =====
bpy.context.view_layer.objects.active = chair_group
bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

print("✅ 辦公椅模型創建完成！")
print("包含：座椅、椅背、扶手、五星腳、輪子")
