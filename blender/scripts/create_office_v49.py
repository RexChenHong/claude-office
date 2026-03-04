#!/usr/bin/env python3
"""V49 - 恢復原本格局
- 5 張工作站：原本位置和朝向
- 椅子在桌子後方，面向桌子
"""
import bpy
import math
import sys
import bmesh

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

# ========== 一體成型椅子 ==========
def create_chair(x, y, rot=0, index=""):
    """椅子面向 rot 方向"""
    # 5 腳底座
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.02)
    base = bpy.context.active_object
    base.location = (x, y, 0.05)
    base.data.materials.append(mat_metal)
    
    # 椅桿
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.35)
    pole = bpy.context.active_object
    pole.location = (x, y, 0.225)
    pole.data.materials.append(mat_metal)
    
    # 一體成型 L 型座墊+椅背
    mesh = bpy.data.meshes.new(f"ChairMesh{index}")
    obj = bpy.data.objects.new(f"Chair{index}", mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    seat_w, seat_d, seat_h = 0.4, 0.38, 0.08
    seat_z = 0.47
    back_w, back_d, back_h = 0.36, 0.06, 0.5
    
    sv = [
        (-seat_w/2, -seat_d/2, seat_z - seat_h/2), (seat_w/2, -seat_d/2, seat_z - seat_h/2),
        (seat_w/2, seat_d/2, seat_z - seat_h/2), (-seat_w/2, seat_d/2, seat_z - seat_h/2),
        (-seat_w/2, -seat_d/2, seat_z + seat_h/2), (seat_w/2, -seat_d/2, seat_z + seat_h/2),
        (seat_w/2, seat_d/2, seat_z + seat_h/2), (-seat_w/2, seat_d/2, seat_z + seat_h/2),
    ]
    
    back_bottom_z = seat_z + seat_h/2
    back_center_y = -seat_d/2 - back_d/2
    bv = [
        (-back_w/2, back_center_y - back_d/2, back_bottom_z), (back_w/2, back_center_y - back_d/2, back_bottom_z),
        (back_w/2, back_center_y + back_d/2, back_bottom_z), (-back_w/2, back_center_y + back_d/2, back_bottom_z),
        (-back_w/2, back_center_y - back_d/2, back_bottom_z + back_h), (back_w/2, back_center_y - back_d/2, back_bottom_z + back_h),
        (back_w/2, back_center_y + back_d/2, back_bottom_z + back_h), (-back_w/2, back_center_y + back_d/2, back_bottom_z + back_h),
    ]
    
    all_v = sv + bv
    verts = [bm.verts.new(v) for v in all_v]
    bm.verts.ensure_lookup_table()
    
    for f in [(0,1,2,3), (4,5,6,7), (0,1,5,4), (3,2,6,7), (0,3,7,4), (1,2,6,5)]:
        bm.faces.new([verts[i] for i in f])
    for f in [(8,9,10,11), (12,13,14,15), (8,9,13,12), (11,10,14,15), (8,11,15,12), (9,10,14,13)]:
        bm.faces.new([verts[i] for i in f])
    
    bm.to_mesh(mesh)
    bm.free()
    
    obj.location = (x, y, 0)
    obj.rotation_euler = (0, 0, rot)
    obj.data.materials.append(mat_seat)

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

# ========== 5 張工作站（原本格局）==========
# 工作站 1: (-5.5, 4), 面向東 (rot=π/2) → 椅子在 X- 方向，面向東
create_desk(-5.5, 4, rot=math.pi/2, index=1)
create_chair(-5.5 - 0.875, 4, rot=math.pi/2, index="_WS1")

# 工作站 2: (-5.5, 6), 面向東 (rot=π/2) → 椅子在 X- 方向，面向東
create_desk(-5.5, 6, rot=math.pi/2, index=2)
create_chair(-5.5 - 0.875, 6, rot=math.pi/2, index="_WS2")

# 工作站 3: (0, 5), 面向北 (rot=0) → 椅子在 Y- 方向，面向北
create_desk(0, 5, rot=0, index=3)
create_chair(0, 5 - 0.875, rot=0, index="_WS3")

# 工作站 4: (5.5, 4), 面向西 (rot=-π/2) → 椅子在 X+ 方向，面向西
create_desk(5.5, 4, rot=-math.pi/2, index=4)
create_chair(5.5 + 0.875, 4, rot=-math.pi/2, index="_WS4")

# 工作站 5: (5.5, 6), 面向西 (rot=-π/2) → 椅子在 X+ 方向，面向西
create_desk(5.5, 6, rot=-math.pi/2, index=5)
create_chair(5.5 + 0.875, 6, rot=-math.pi/2, index="_WS5")

# ========== 導出 ==========
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(
    filepath='/mnt/e_drive/claude-office/blender/exports/office_v49.glb',
    export_format='GLB',
    use_selection=True
)

print("已導出 V49")
