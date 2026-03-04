#!/usr/bin/env python3
"""V50 - 修正椅子朝向 + 合併椅子部件
1. 椅子面向桌子（椅背在桌子反方向）
2. 椅子所有部件合併成一個物件（簡化版）
"""
import bpy
import math
import sys

sys.path.insert(0, '/home/rex/.local/lib/python3.10/site-packages')

# 清空場景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# ========== 材質定義 ==========
def create_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat

mat_desktop = create_material("Desktop", (0.95, 0.95, 0.93, 1), roughness=0.6)
mat_metal = create_material("Metal", (0.2, 0.2, 0.2, 1), roughness=0.3, metallic=0.8)
mat_seat = create_material("Seat", (0.25, 0.25, 0.28, 1), roughness=0.8)
mat_floor = create_material("Floor", (0.15, 0.10, 0.08, 1), roughness=0.9)

# ========== 一體成型椅子（簡化版）==========
def create_chair(x, y, rot=0, index=""):
    """創建完整椅子，所有部件合併成一個物件
    椅子面向 rot 方向，椅背在 -rot 方向
    """
    # 創建空物件作為椅子父物件
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(x, y, 0))
    chair_parent = bpy.context.active_object
    chair_parent.name = f"Chair{index}"
    chair_parent.rotation_euler = (0, 0, rot)
    
    # 5 腳底座
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.02)
    base = bpy.context.active_object
    base.location = (0, 0, 0.05)
    base.data.materials.append(mat_metal)
    base.parent = chair_parent
    
    # 5 個椅腳 + 輪子
    for i in range(5):
        angle = i * 2 * math.pi / 5
        lx = 0.22 * math.cos(angle)
        ly = 0.22 * math.sin(angle)
        
        # 椅腳
        bpy.ops.mesh.primitive_cube_add(size=1)
        leg = bpy.context.active_object
        leg.scale = (0.22, 0.02, 0.02)
        leg.location = (0.11 * math.cos(angle), 0.11 * math.sin(angle), 0.05)
        leg.rotation_euler = (0, 0, angle)
        leg.data.materials.append(mat_metal)
        leg.parent = chair_parent
        
        # 輪子
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05)
        wheel = bpy.context.active_object
        wheel.location = (lx, ly, 0.05)
        wheel.data.materials.append(mat_metal)
        wheel.parent = chair_parent
    
    # 椅桿
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.35)
    pole = bpy.context.active_object
    pole.location = (0, 0, 0.225)
    pole.data.materials.append(mat_metal)
    pole.parent = chair_parent
    
    # 座墊
    bpy.ops.mesh.primitive_cube_add(size=1)
    seat = bpy.context.active_object
    seat.scale = (0.4, 0.38, 0.08)
    seat.location = (0, 0, 0.47)
    seat.data.materials.append(mat_seat)
    seat.parent = chair_parent
    
    # 椅背（在座墊後方 Y-，椅子面向 Y+）
    bpy.ops.mesh.primitive_cube_add(size=1)
    back = bpy.context.active_object
    back.scale = (0.36, 0.06, 0.5)
    back.location = (0, -0.25, 0.76)  # Y- 方向
    back.data.materials.append(mat_seat)
    back.parent = chair_parent
    
    # 合併所有椅子部件
    bpy.ops.object.select_all(action='DESELECT')
    for child in chair_parent.children:
        child.select_set(True)
    bpy.context.view_layer.objects.active = chair_parent.children[0]
    bpy.ops.object.join()
    
    # 刪除空父物件，重命名合併後的 mesh
    merged = bpy.context.active_object
    merged.name = f"Chair{index}"
    merged.location = (x, y, 0)
    merged.rotation_euler = (0, 0, rot)
    bpy.data.objects.remove(chair_parent)

# ========== 桌子 ==========
def create_desk(x, y, rot=0, index=1):
    bpy.ops.mesh.primitive_cube_add(size=1)
    desk = bpy.context.active_object
    desk.scale = (1.4, 0.75, 0.03)
    desk.location = (x, y, 0.765)
    desk.rotation_euler = (0, 0, rot)
    desk.data.materials.append(mat_desktop)
    desk.name = f"Desk_{index}"
    
    for dx, dy in [(-0.6, -0.3), (0.6, -0.3), (-0.6, 0.3), (0.6, 0.3)]:
        bx = x + dx * math.cos(rot) - dy * math.sin(rot)
        by = y + dx * math.sin(rot) + dy * math.cos(rot)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.75)
        leg = bpy.context.active_object
        leg.location = (bx, by, 0.375)
        leg.data.materials.append(mat_metal)

# ========== 地板 ==========
bpy.ops.mesh.primitive_plane_add(size=1)
floor = bpy.context.active_object
floor.scale = (16, 14, 1)
floor.data.materials.append(mat_floor)

# ========== 5 張工作站 ==========
# 椅子位置和朝向：
# - 椅子在桌子「後方」（使用者坐的位置）
# - 椅子面向桌子
# - 椅背遠離桌子

# 位置計算：
# - 面向北(0): 椅子在 Y- 方向 → (x, y-offset)
# - 面向東(π/2): 椅子在 X- 方向 → (x-offset, y)
# - 面向西(-π/2): 椅子在 X+ 方向 → (x+offset, y)
# 公式: chair_x = x - offset*sin(rot), chair_y = y - offset*cos(rot)

chair_offset = 0.875

# 工作站 1: (-5.5, 4), 面向東 (desk_rot=π/2)
# 椅子位置: (-5.5-0.875, 4) = (-6.375, 4)
# 椅子面向東 (rot=-π/2)，椅背向西（遠離桌子）
create_desk(-5.5, 4, rot=math.pi/2, index=1)
create_chair(-5.5 - chair_offset, 4, rot=-math.pi/2, index="_WS1")

# 工作站 2: (-5.5, 6), 面向東
create_desk(-5.5, 6, rot=math.pi/2, index=2)
create_chair(-5.5 - chair_offset, 6, rot=-math.pi/2, index="_WS2")

# 工作站 3: (0, 5), 面向北 (desk_rot=0)
# 椅子位置: (0, 5+0.875) = (0, 5.875) - 在桌子北邊
# 椅子面向南 (rot=π)，椅背向北（遠離桌子）
create_desk(0, 5, rot=0, index=3)
create_chair(0, 5 + chair_offset, rot=math.pi, index="_WS3")

# 工作站 4: (5.5, 4), 面向西 (desk_rot=-π/2)
# 椅子位置: (5.5+0.875, 4) = (6.375, 4)
# 椅子面向西 (rot=π/2)，椅背向東（遠離桌子）
create_desk(5.5, 4, rot=-math.pi/2, index=4)
create_chair(5.5 + chair_offset, 4, rot=math.pi/2, index="_WS4")

# 工作站 5: (5.5, 6), 面向西
create_desk(5.5, 6, rot=-math.pi/2, index=5)
create_chair(5.5 + chair_offset, 6, rot=math.pi/2, index="_WS5")

# ========== 導出 ==========
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(
    filepath='/mnt/e_drive/claude-office/blender/exports/office_v50.glb',
    export_format='GLB',
    use_selection=True
)

print("已導出 V50")
