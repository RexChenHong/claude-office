#!/usr/bin/env python3
"""
Claude Office V20.1 - 最簡單的紋理設置
只用 Image Texture → Principled BSDF（無中間節點）
"""

import sys
user_site = '/home/rex/.local/lib/python3.10/site-packages'
if user_site not in sys.path:
    sys.path.insert(0, user_site)

import bpy
import math
import os

# 清除場景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

for block in bpy.data.meshes:
    if block.users == 0:
        bpy.data.meshes.remove(block)
for block in bpy.data.materials:
    if block.users == 0:
        bpy.data.materials.remove(block)
for block in bpy.data.images:
    if block.users == 0:
        bpy.data.images.remove(block)

TEX_PATH = "/mnt/e_drive/claude-office/blender/textures/"

# ========== 載入紋理 ==========

def load_texture(name, path):
    if not os.path.exists(path):
        print(f"✗ {name}: 不存在")
        return None
    try:
        img = bpy.data.images.load(path, check_existing=True)
        img.name = name
        print(f"✓ {name}")
        return img
    except Exception as e:
        print(f"✗ {name}: {e}")
        return None

wood_diff = load_texture("Wood_Diff", TEX_PATH + "wood_diffuse.jpg")
wood_norm = load_texture("Wood_Norm", TEX_PATH + "wood_normal.jpg")
fabric_diff = load_texture("Fabric_Diff", TEX_PATH + "fabric_diffuse.jpg")

# ========== 材質 ==========

def create_simple_textured_material(name, diffuse_img=None, normal_img=None):
    """最簡單的紋理材質（GLTF 兼容）"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    principled = nodes.get("Principled BSDF")

    # Diffuse
    if diffuse_img:
        tex = nodes.new('ShaderNodeTexImage')
        tex.image = diffuse_img
        tex.label = "Diffuse"
        links.new(tex.outputs['Color'], principled.inputs['Base Color'])

    # Normal
    if normal_img:
        normal_tex = nodes.new('ShaderNodeTexImage')
        normal_tex.image = normal_img
        normal_tex.label = "Normal"
        normal_tex.image.colorspace_settings.name = 'Linear'

        normal_map = nodes.new('ShaderNodeNormalMap')
        links.new(normal_tex.outputs['Color'], normal_map.inputs['Color'])
        links.new(normal_map.outputs['Normal'], principled.inputs['Normal'])

    return mat

def create_color_material(name, color, roughness=0.5, metallic=0.0):
    """純色材質"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    return mat

# 創建材質
mat_floor = create_simple_textured_material("Floor", wood_diff, wood_norm)
mat_wall = create_color_material("Wall", (0.92, 0.92, 0.9, 1), roughness=0.85)
mat_glass = create_color_material("Glass", (0.85, 0.92, 0.98, 0.15), roughness=0.05)
mat_metal_frame = create_color_material("Metal", (0.08, 0.08, 0.08, 1), roughness=0.2, metallic=0.85)
mat_desktop = create_color_material("Desktop", (0.95, 0.95, 0.93, 1), roughness=0.25)
mat_seat = create_simple_textured_material("Seat", fabric_diff)
mat_metal = create_color_material("Metal", (0.35, 0.35, 0.37, 1), roughness=0.15, metallic=0.9)
mat_plastic = create_color_material("Plastic", (0.04, 0.04, 0.04, 1), roughness=0.35)
mat_screen = create_color_material("Screen", (0.1, 0.13, 0.16, 1), roughness=0.08)
mat_meeting_table = create_color_material("Table", (0.55, 0.45, 0.38, 1), roughness=0.35)
mat_whiteboard = create_color_material("Whiteboard", (0.98, 0.98, 0.98, 1), roughness=0.25)
mat_sofa = create_simple_textured_material("Sofa", fabric_diff)
mat_pot = create_color_material("Pot", (0.65, 0.45, 0.32, 1), roughness=0.6)
mat_plant = create_color_material("Plant", (0.18, 0.38, 0.15, 1), roughness=0.5)
mat_printer = create_color_material("Printer", (0.18, 0.18, 0.18, 1), roughness=0.3)
mat_water = create_color_material("Water", (0.88, 0.88, 0.88, 1), roughness=0.2)
mat_cabinet = create_color_material("Cabinet", (0.55, 0.55, 0.57, 1), roughness=0.3, metallic=0.4)
mat_trash = create_color_material("Trash", (0.22, 0.22, 0.22, 1), roughness=0.5)
mat_carpet = create_color_material("Carpet", (0.5, 0.43, 0.38, 1), roughness=0.95)
mat_lamp = create_color_material("Lamp", (0.12, 0.12, 0.12, 1), roughness=0.2, metallic=0.7)

# ========== 房間 ==========

ROOM_W, ROOM_D, WALL_H = 16, 14, 2.8

# 地板
bpy.ops.mesh.primitive_plane_add(size=1)
floor = bpy.context.active_object
floor.scale = (ROOM_W + 2, ROOM_D + 2, 1)
floor.data.materials.append(mat_floor)

# 牆壁
for wx, wy, wz, sx, sy in [
    (0, -ROOM_D/2 - 0.04, WALL_H/2, ROOM_W/2 + 0.15, 0.08),  # 後
    (-ROOM_W/4 - 0.6, ROOM_D/2 + 0.04, WALL_H/2, ROOM_W/2 - 1.2, 0.08),  # 前左
    (ROOM_W/4 + 0.6, ROOM_D/2 + 0.04, WALL_H/2, ROOM_W/2 - 1.2, 0.08),  # 前右
    (0, ROOM_D/2 + 0.04, 2.2 + (WALL_H - 2.2)/2, 1.2, (WALL_H - 2.2)/2),  # 門上
    (-ROOM_W/2 - 0.04, 0, WALL_H/2, 0.08, ROOM_D/2),  # 左
    (ROOM_W/2 + 0.04, 0, WALL_H/2, 0.08, ROOM_D/2),  # 右
]:
    bpy.ops.mesh.primitive_cube_add(size=1)
    w = bpy.context.active_object
    w.scale = (sx, sy, wz if sy < 0.1 else WALL_H/2)
    w.location = (wx, wy, wz)
    w.data.materials.append(mat_wall)

# 落地窗
bpy.ops.mesh.primitive_cube_add(size=1)
window = bpy.context.active_object
window.scale = (0.02, 5, WALL_H/2 - 0.15)
window.location = (ROOM_W/2 + 0.07, 0, WALL_H/2)
window.data.materials.append(mat_glass)

# ========== 隔間 ==========

# 主官辦公室
for fx, fy in [(-2.5, -1.5), (-2.5, 1.5), (0.5, -1.5), (0.5, 1.5)]:
    bpy.ops.mesh.primitive_cube_add(size=1)
    f = bpy.context.active_object
    f.scale = (0.035, 0.035, WALL_H/2)
    f.location = (fx, fy, WALL_H/2)
    f.data.materials.append(mat_metal_frame)

for gx, gy in [(-2.5, 0), (0.5, 0)]:
    bpy.ops.mesh.primitive_cube_add(size=1)
    g = bpy.context.active_object
    g.scale = (0.015, 1.5, WALL_H/2)
    g.location = (gx, gy, WALL_H/2)
    g.data.materials.append(mat_glass)

# L 型隔間
for lx, ly, lr in [(-4, -4.5, 0), (0.5, -7, math.pi/2)]:
    bpy.ops.mesh.primitive_cube_add(size=1)
    lg = bpy.context.active_object
    if lr == 0:
        lg.scale = (0.015, 2.5, WALL_H/2)
    else:
        lg.scale = (4.5, 0.015, WALL_H/2)
        lg.rotation_euler = (0, 0, lr)
    lg.location = (lx, ly, WALL_H/2)
    lg.data.materials.append(mat_glass)

for fx, fy in [(-4, -7), (-4, -2), (-1, -7), (2, -7), (5, -7)]:
    bpy.ops.mesh.primitive_cube_add(size=1)
    f = bpy.context.active_object
    f.scale = (0.035, 0.035, WALL_H/2)
    f.location = (fx, fy, WALL_H/2)
    f.data.materials.append(mat_metal_frame)

# ========== 會議室 ==========

MEETING_X, MEETING_Y = -2, -5

bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=0.035)
t = bpy.context.active_object
t.scale = (1, 0.6, 1)
t.location = (MEETING_X, MEETING_Y, 0.75)
t.data.materials.append(mat_meeting_table)

for i in range(4):
    angle = i * (math.pi / 2) + math.pi/4
    cx = MEETING_X + math.cos(angle) * 0.75
    cy = MEETING_Y + math.sin(angle) * 0.45
    bpy.ops.mesh.primitive_cube_add(size=1)
    c = bpy.context.active_object
    c.scale = (0.26, 0.26, 0.045)
    c.location = (cx, cy, 0.48)
    c.rotation_euler = (0, 0, angle + math.pi)
    c.data.materials.append(mat_seat)

# ========== 休息區 ==========

LOUNGE_X, LOUNGE_Y = 3, -5

bpy.ops.mesh.primitive_plane_add(size=1)
c = bpy.context.active_object
c.scale = (1.8, 1.8, 1)
c.location = (LOUNGE_X, LOUNGE_Y, 0.01)
c.data.materials.append(mat_carpet)

# 沙發
for sx, sy, sz, rx in [
    (LOUNGE_X, LOUNGE_Y - 0.4, 0.25, 0),
    (LOUNGE_X, LOUNGE_Y - 0.6, 0.4, 0),
    (LOUNGE_X + 0.55, LOUNGE_Y, 0.25, math.pi/2)
]:
    bpy.ops.mesh.primitive_cube_add(size=1)
    s = bpy.context.active_object
    if rx == 0:
        s.scale = (1.0, 0.3 if sz == 0.25 else 0.05, 0.25)
    else:
        s.scale = (0.3, 0.8, 0.25)
    s.location = (sx, sy, sz)
    s.data.materials.append(mat_sofa)

# 茶几
bpy.ops.mesh.primitive_cube_add(size=1)
ct = bpy.context.active_object
ct.scale = (0.4, 0.24, 0.012)
ct.location = (LOUNGE_X + 0.1, LOUNGE_Y + 0.18, 0.32)
ct.data.materials.append(mat_meeting_table)

# ========== 工作站 ==========

def create_workstation(x, y, facing='north'):
    angles = {'north': 0, 'south': math.pi, 'east': math.pi/2, 'west': -math.pi/2}
    rot = angles[facing]

    # 桌子
    bpy.ops.mesh.primitive_cube_add(size=1)
    d = bpy.context.active_object
    d.scale = (1.3, 0.65, 0.022)
    d.location = (x, y, 0.75)
    d.rotation_euler = (0, 0, rot)
    d.data.materials.append(mat_desktop)

    # 腿
    for dx, dy in [(-0.55, -0.25), (-0.55, 0.25), (0.55, -0.25), (0.55, 0.25)]:
        bx = x + dx * math.cos(rot) - dy * math.sin(rot)
        by = y + dx * math.sin(rot) + dy * math.cos(rot)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.65)
        leg = bpy.context.active_object
        leg.location = (bx, by, 0.375)
        leg.data.materials.append(mat_metal)

    # 螢幕
    for sx in [-0.3, 0.3]:
        bx = x + sx * math.cos(rot) + 0.35 * math.sin(rot)
        by = y + sx * math.sin(rot) + 0.35 * math.cos(rot)
        bpy.ops.mesh.primitive_cube_add(size=1)
        s = bpy.context.active_object
        s.scale = (0.5, 0.02, 0.28)
        s.location = (bx, by, 1.0)
        s.rotation_euler = (0, 0, rot + math.pi)
        s.data.materials.append(mat_screen)

    # 椅子
    chair_offset = -0.75
    chair_x = x + chair_offset * math.sin(rot)
    chair_y = y + chair_offset * math.cos(rot)

    bpy.ops.mesh.primitive_cube_add(size=1)
    seat = bpy.context.active_object
    seat.scale = (0.4, 0.36, 0.07)
    seat.location = (chair_x, chair_y, 0.48)
    seat.rotation_euler = (0, 0, rot)
    seat.data.materials.append(mat_seat)

# 工作站佈局
create_workstation(-5.5, 2, 'east')
create_workstation(-5.5, 4.5, 'east')
create_workstation(-1, 0, 'north')
create_workstation(5.5, 2, 'west')
create_workstation(5.5, 4.5, 'west')

# ========== 設備 ==========

# 印表機
bpy.ops.mesh.primitive_cube_add(size=1)
p = bpy.context.active_object
p.scale = (0.28, 0.25, 0.18)
p.location = (-ROOM_W/2 + 0.3, 3.5, 0.5)
p.data.materials.append(mat_printer)

# 飲水機
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.25, 0.25, 0.85)
w.location = (6.5, 5.5, 0.45)
w.data.materials.append(mat_water)

# 文件櫃
for i in range(3):
    bpy.ops.mesh.primitive_cube_add(size=1)
    cab = bpy.context.active_object
    cab.scale = (0.32, 0.38, 0.65)
    cab.location = (-ROOM_W/2 + 0.28, -1 + i * 0.45, 0.35)
    cab.data.materials.append(mat_cabinet)

# 垃圾桶
for bx, by in [(-6.5, 2), (-0.5, -1), (6.5, 2)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.25)
    trash = bpy.context.active_object
    trash.location = (bx, by, 0.15)
    trash.data.materials.append(mat_trash)

# 植物
for px, py in [(6, -6), (-6, 5.5), (6, 5.5)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.12)
    pot = bpy.context.active_object
    pot.location = (px, py, 0.56)
    pot.data.materials.append(mat_pot)

    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.14)
    plant = bpy.context.active_object
    plant.location = (px, py, 0.8)
    plant.scale = (1, 1, 1.2)
    plant.data.materials.append(mat_plant)

print("✅ V20.1 完成！")
print("最簡單的紋理設置（Image Texture → BSDF）")
