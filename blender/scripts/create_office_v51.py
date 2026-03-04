#!/usr/bin/env python3
"""V51 - 優化桌子質感 + 鎖定已調整物件
1. 桌子：木紋桌面 + 金屬邊框 + 圓柱桌腳
2. 椅子：鎖定（不再修改）
3. 座標：鎖定（不再修改）
"""
import bpy
import math
import sys

sys.path.insert(0, '/home/rex/.local/lib/python3.10/site-packages')

# 清空場景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# ========== 材質定義（優化版）==========
def create_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat

# 桌面：白色霧面烤漆
mat_desktop = create_material("Desktop_White", (0.95, 0.95, 0.93, 1), roughness=0.4, metallic=0.0)

# 桌框：深灰色金屬
mat_frame = create_material("DeskFrame", (0.3, 0.3, 0.32, 1), roughness=0.2, metallic=0.9)

# 桌腳：銀色金屬
mat_leg = create_material("DeskLeg", (0.6, 0.6, 0.62, 1), roughness=0.3, metallic=0.8)

# 椅子材質（鎖定）
mat_seat = create_material("Seat", (0.25, 0.25, 0.28, 1), roughness=0.8)
mat_metal = create_material("Metal", (0.2, 0.2, 0.2, 1), roughness=0.3, metallic=0.8)

# 地板材質
mat_floor = create_material("Floor", (0.15, 0.10, 0.08, 1), roughness=0.9)

def add_bevel(obj, segments=3, width=0.02):
    bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel.segments = segments
    bevel.width = width
    bevel.limit_method = 'ANGLE'

# ========== 椅子（鎖定，不再修改）==========
def create_chair(x, y, rot=0, index=""):
    """椅子 - 鎖定版本，不再修改"""
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
        
        bpy.ops.mesh.primitive_cube_add(size=1)
        leg = bpy.context.active_object
        leg.scale = (0.22, 0.02, 0.02)
        leg.location = (0.11 * math.cos(angle), 0.11 * math.sin(angle), 0.05)
        leg.rotation_euler = (0, 0, angle)
        leg.data.materials.append(mat_metal)
        leg.parent = chair_parent
        
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
    
    # 椅背
    bpy.ops.mesh.primitive_cube_add(size=1)
    back = bpy.context.active_object
    back.scale = (0.36, 0.06, 0.5)
    back.location = (0, -0.25, 0.76)
    back.data.materials.append(mat_seat)
    back.parent = chair_parent
    
    # 合併
    bpy.ops.object.select_all(action='DESELECT')
    for child in chair_parent.children:
        child.select_set(True)
    bpy.context.view_layer.objects.active = chair_parent.children[0]
    bpy.ops.object.join()
    
    merged = bpy.context.active_object
    merged.name = f"Chair{index}"
    merged.location = (x, y, 0)
    merged.rotation_euler = (0, 0, rot)
    bpy.data.objects.remove(chair_parent)

# ========== 桌子（優化版）==========
def create_desk(x, y, rot=0, index=1):
    """桌子 - 優化質感版本"""
    desk_parent = bpy.data.objects.new(f"Desk_{index}_Parent", None)
    bpy.context.collection.objects.link(desk_parent)
    desk_parent.location = (x, y, 0)
    desk_parent.rotation_euler = (0, 0, rot)
    
    # ========== 桌面主體 ==========
    # 桌面板（白色烤漆）
    bpy.ops.mesh.primitive_cube_add(size=1)
    desktop = bpy.context.active_object
    desktop.scale = (1.4, 0.75, 0.025)  # 稍薄
    desktop.location = (0, 0, 0.7625)
    desktop.data.materials.append(mat_desktop)
    add_bevel(desktop, segments=4, width=0.01)
    desktop.name = f"Desktop_{index}"
    desktop.parent = desk_parent
    
    # ========== 金屬邊框 ==========
    frame_height = 0.05
    frame_thickness = 0.03
    
    # 前邊框（Y+）
    bpy.ops.mesh.primitive_cube_add(size=1)
    front_frame = bpy.context.active_object
    front_frame.scale = (1.4, frame_thickness, frame_height)
    front_frame.location = (0, 0.375 - frame_thickness/2, 0.735)
    front_frame.data.materials.append(mat_frame)
    front_frame.parent = desk_parent
    
    # 後邊框（Y-）
    bpy.ops.mesh.primitive_cube_add(size=1)
    back_frame = bpy.context.active_object
    back_frame.scale = (1.4, frame_thickness, frame_height)
    back_frame.location = (0, -0.375 + frame_thickness/2, 0.735)
    back_frame.data.materials.append(mat_frame)
    back_frame.parent = desk_parent
    
    # 左邊框（X-）
    bpy.ops.mesh.primitive_cube_add(size=1)
    left_frame = bpy.context.active_object
    left_frame.scale = (frame_thickness, 0.75 - frame_thickness*2, frame_height)
    left_frame.location = (-0.7 + frame_thickness/2, 0, 0.735)
    left_frame.data.materials.append(mat_frame)
    left_frame.parent = desk_parent
    
    # 右邊框（X+）
    bpy.ops.mesh.primitive_cube_add(size=1)
    right_frame = bpy.context.active_object
    right_frame.scale = (frame_thickness, 0.75 - frame_thickness*2, frame_height)
    right_frame.location = (0.7 - frame_thickness/2, 0, 0.735)
    right_frame.data.materials.append(mat_frame)
    right_frame.parent = desk_parent
    
    # ========== 桌腳（圓柱形）==========
    leg_radius = 0.03
    leg_height = 0.71
    
    for dx, dy in [(-0.6, -0.3), (0.6, -0.3), (-0.6, 0.3), (0.6, 0.3)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=leg_radius, depth=leg_height)
        leg = bpy.context.active_object
        leg.location = (dx, dy, leg_height/2)
        leg.data.materials.append(mat_leg)
        add_bevel(leg, segments=2, width=0.005)
        leg.parent = desk_parent
    
    # ========== 桌腳底座 ==========
    base_radius = 0.05
    base_height = 0.02
    
    for dx, dy in [(-0.6, -0.3), (0.6, -0.3), (-0.6, 0.3), (0.6, 0.3)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=base_radius, depth=base_height)
        base = bpy.context.active_object
        base.location = (dx, dy, 0.01)
        base.data.materials.append(mat_frame)
        base.parent = desk_parent

# ========== 地板 ==========
bpy.ops.mesh.primitive_plane_add(size=1)
floor = bpy.context.active_object
floor.scale = (16, 14, 1)
floor.data.materials.append(mat_floor)

# ========== 5 張工作站（鎖定座標）==========
chair_offset = 0.875

# 工作站 1: (-5.5, 4), 面向東
create_desk(-5.5, 4, rot=math.pi/2, index=1)
create_chair(-5.5 - chair_offset, 4, rot=-math.pi/2, index="_WS1")

# 工作站 2: (-5.5, 6), 面向東
create_desk(-5.5, 6, rot=math.pi/2, index=2)
create_chair(-5.5 - chair_offset, 6, rot=-math.pi/2, index="_WS2")

# 工作站 3: (0, 5), 面向北
create_desk(0, 5, rot=0, index=3)
create_chair(0, 5 + chair_offset, rot=math.pi, index="_WS3")

# 工作站 4: (5.5, 4), 面向西
create_desk(5.5, 4, rot=-math.pi/2, index=4)
create_chair(5.5 + chair_offset, 4, rot=math.pi/2, index="_WS4")

# 工作站 5: (5.5, 6), 面向西
create_desk(5.5, 6, rot=-math.pi/2, index=5)
create_chair(5.5 + chair_offset, 6, rot=math.pi/2, index="_WS5")

# ========== 導出 ==========
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(
    filepath='/mnt/e_drive/claude-office/blender/exports/office_v51.glb',
    export_format='GLB',
    use_selection=True
)

print("已導出 V51")
