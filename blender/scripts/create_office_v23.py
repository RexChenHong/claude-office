#!/usr/bin/env python3
"""
Claude Office V23 - 極低反光材質（接近 Sketchfab）
所有材質 roughness >= 0.85
"""

import sys
user_site = '/home/rex/.local/lib/python3.10/site-packages'
if user_site not in sys.path:
    sys.path.insert(0, user_site)

import bpy
import math

# 清除場景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

for block in bpy.data.meshes:
    if block.users == 0:
        bpy.data.meshes.remove(block)
for block in bpy.data.materials:
    if block.users == 0:
        bpy.data.materials.remove(block)

# ========== 材質（極低反光）==========

def create_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    return mat

# 所有材質 roughness >= 0.85（接近無反光）
mat_floor = create_material("DarkWoodFloor", (0.25, 0.18, 0.12, 1), roughness=0.95)
mat_wall = create_material("Wall", (0.92, 0.92, 0.9, 1), roughness=0.98)
mat_glass = create_material("Glass", (0.85, 0.92, 0.98, 0.15), roughness=0.2)
mat_metal_frame = create_material("Metal_Frame", (0.08, 0.08, 0.08, 1), roughness=0.7, metallic=0.2)
mat_desktop = create_material("Desktop", (0.95, 0.95, 0.93, 1), roughness=0.9)
mat_seat = create_material("Seat", (0.06, 0.06, 0.06, 1), roughness=0.95)
mat_metal = create_material("Metal", (0.35, 0.35, 0.37, 1), roughness=0.6, metallic=0.3)
mat_plastic = create_material("Plastic", (0.04, 0.04, 0.04, 1), roughness=0.9)
mat_screen = create_material("Screen", (0.1, 0.13, 0.16, 1), roughness=0.5)
mat_meeting_table = create_material("Meeting_Table", (0.55, 0.45, 0.38, 1), roughness=0.85)
mat_whiteboard = create_material("Whiteboard", (0.98, 0.98, 0.98, 1), roughness=0.7)
mat_sofa = create_material("Sofa", (0.22, 0.22, 0.24, 1), roughness=0.98)
mat_plant_pot = create_material("Pot", (0.65, 0.45, 0.32, 1), roughness=0.9)
mat_plant = create_material("Plant", (0.18, 0.38, 0.15, 1), roughness=0.9)
mat_printer = create_material("Printer", (0.18, 0.18, 0.18, 1), roughness=0.85)
mat_water_dispenser = create_material("WaterDispenser", (0.88, 0.88, 0.88, 1), roughness=0.7)
mat_cabinet = create_material("Cabinet", (0.55, 0.55, 0.57, 1), roughness=0.85, metallic=0.1)
mat_trash_bin = create_material("TrashBin", (0.22, 0.22, 0.22, 1), roughness=0.85)
mat_carpet = create_material("Carpet", (0.5, 0.43, 0.38, 1), roughness=0.99)
mat_lamp = create_material("Lamp", (0.12, 0.12, 0.12, 1), roughness=0.7, metallic=0.2)

# ========== 房間尺寸 ==========

ROOM_W = 16
ROOM_D = 14
WALL_H = 2.8

# ========== 地板 ==========

bpy.ops.mesh.primitive_plane_add(size=1)
floor = bpy.context.active_object
floor.scale = (ROOM_W + 2, ROOM_D + 2, 1)
floor.data.materials.append(mat_floor)

# ========== 牆壁 ==========

# 後牆
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (ROOM_W/2 + 0.15, 0.08, WALL_H/2)
w.location = (0, -ROOM_D/2 - 0.04, WALL_H/2)
w.data.materials.append(mat_wall)

# 前牆
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (ROOM_W/2 - 1.2, 0.08, WALL_H/2)
w.location = (-ROOM_W/4 - 0.6, ROOM_D/2 + 0.04, WALL_H/2)
w.data.materials.append(mat_wall)

bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (ROOM_W/2 - 1.2, 0.08, WALL_H/2)
w.location = (ROOM_W/4 + 0.6, ROOM_D/2 + 0.04, WALL_H/2)
w.data.materials.append(mat_wall)

bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (1.2, 0.08, (WALL_H - 2.2)/2)
w.location = (0, ROOM_D/2 + 0.04, 2.2 + (WALL_H - 2.2)/2)
w.data.materials.append(mat_wall)

# 左牆
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.08, ROOM_D/2, WALL_H/2)
w.location = (-ROOM_W/2 - 0.04, 0, WALL_H/2)
w.data.materials.append(mat_wall)

# 右牆
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.08, ROOM_D/2, WALL_H/2)
w.location = (ROOM_W/2 + 0.04, 0, WALL_H/2)
w.data.materials.append(mat_wall)

# 落地窗
bpy.ops.mesh.primitive_cube_add(size=1)
window = bpy.context.active_object
window.scale = (0.02, 5, WALL_H/2 - 0.15)
window.location = (ROOM_W/2 + 0.07, 0, WALL_H/2)
window.data.materials.append(mat_glass)

# ========== 主官辦公室隔間 ==========

for fx, fy in [(-2.5, -1.5), (-2.5, 1.5), (0.5, -1.5), (0.5, 1.5)]:
    bpy.ops.mesh.primitive_cube_add(size=1)
    f = bpy.context.active_object
    f.scale = (0.035, 0.035, WALL_H/2)
    f.location = (fx, fy, WALL_H/2)
    f.data.materials.append(mat_metal_frame)

bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.015, 1.5, WALL_H/2)
w.location = (-2.5, 0, WALL_H/2)
w.data.materials.append(mat_glass)

bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.015, 1.5, WALL_H/2)
w.location = (0.5, 0, WALL_H/2)
w.data.materials.append(mat_glass)

# ========== L 型玻璃隔間 ==========

bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.015, 2.5, WALL_H/2)
w.location = (-4, -4.5, WALL_H/2)
w.data.materials.append(mat_glass)

bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (4.5, 0.015, WALL_H/2)
w.location = (0.5, -7, WALL_H/2)
w.data.materials.append(mat_glass)

frame_positions = [(-4, -7), (-4, -2), (-1, -7), (2, -7), (5, -7)]
for fx, fy in frame_positions:
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

bpy.ops.mesh.primitive_cube_add(size=1)
wb = bpy.context.active_object
wb.scale = (0.015, 0.75, 0.45)
wb.location = (-ROOM_W/2 + 0.12, MEETING_Y, 1.3)
wb.data.materials.append(mat_whiteboard)

# ========== 休息區 ==========

LOUNGE_X, LOUNGE_Y = 3, -5

bpy.ops.mesh.primitive_cube_add(size=1)
carpet = bpy.context.active_object
carpet.scale = (2.5, 1.8, 0.02)
carpet.location = (LOUNGE_X, LOUNGE_Y, 0.01)
carpet.data.materials.append(mat_carpet)

# L 型沙發（兩個長沙發）
for dx, dy, sx, sy in [(-0.6, 0, 1.2, 0.35), (0.6, -0.5, 0.35, 1)]:
    bpy.ops.mesh.primitive_cube_add(size=1)
    s = bpy.context.active_object
    s.scale = (sx/2, sy/2, 0.22)
    s.location = (LOUNGE_X + dx, LOUNGE_Y + dy, 0.22)
    s.data.materials.append(mat_sofa)

bpy.ops.mesh.primitive_cube_add(size=1)
ct = bpy.context.active_object
ct.scale = (0.35, 0.35, 0.18)
ct.location = (LOUNGE_X + 0.6, LOUNGE_Y + 0.4, 0.18)
ct.data.materials.append(mat_meeting_table)

# ========== 5 個工作站 ==========

DESK_W, DESK_D = 1.4, 0.75
positions = [
    (-5, 2, 0),
    (-2.5, 2, 0),
    (0, 2, 0),
    (2.5, 2, 0),
    (5, 2, 0),
]
rotations = [math.pi, math.pi, math.pi, math.pi, math.pi]

for idx, (x, y, z) in enumerate(positions):
    rot = rotations[idx]

    # 桌子
    bpy.ops.mesh.primitive_cube_add(size=1)
    desk = bpy.context.active_object
    desk.scale = (DESK_W/2, DESK_D/2, 0.025)
    desk.location = (x, y, 0.75)
    desk.rotation_euler = (0, 0, rot)
    desk.data.materials.append(mat_desktop)

    # 椅子
    offset = 0.55
    cx = x + offset * math.sin(rot)
    cy = y + offset * math.cos(rot)
    bpy.ops.mesh.primitive_cube_add(size=1)
    chair = bpy.context.active_object
    chair.scale = (0.26, 0.26, 0.045)
    chair.location = (cx, cy, 0.48)
    chair.rotation_euler = (0, 0, rot + math.pi)
    chair.data.materials.append(mat_seat)

    # 雙螢幕
    for screen_dx in [-0.3, 0.3]:
        bpy.ops.mesh.primitive_cube_add(size=1)
        screen = bpy.context.active_object
        screen.scale = (0.26, 0.02, 0.19)
        sx = x - 0.15 * math.sin(rot) + screen_dx * math.cos(rot)
        sy = y - 0.15 * math.cos(rot) - screen_dx * math.sin(rot)
        screen.location = (sx, sy, 1.05)
        screen.rotation_euler = (0, 0, rot)
        screen.data.materials.append(mat_screen)

    # 鍵盤
    bpy.ops.mesh.primitive_cube_add(size=1)
    kb = bpy.context.active_object
    kb.scale = (0.22, 0.08, 0.012)
    kb.location = (x, y, 0.78)
    kb.rotation_euler = (0, 0, rot)
    kb.data.materials.append(mat_plastic)

    # 滑鼠
    mx = x + 0.28 * math.cos(rot)
    my = y - 0.28 * math.sin(rot)
    bpy.ops.mesh.primitive_cube_add(size=1)
    mouse = bpy.context.active_object
    mouse.scale = (0.04, 0.06, 0.012)
    mouse.location = (mx, my, 0.78)
    mouse.rotation_euler = (0, 0, rot)
    mouse.data.materials.append(mat_plastic)

    # 檯燈
    lamp_x = x - 0.45 * math.sin(rot)
    lamp_y = y - 0.45 * math.cos(rot)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.22)
    lp = bpy.context.active_object
    lp.location = (lamp_x, lamp_y, 0.86)
    lp.data.materials.append(mat_lamp)

    # 盆栽
    plant_x = x + 0.45 * math.sin(rot)
    plant_y = y + 0.45 * math.cos(rot)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.12)
    pot = bpy.context.active_object
    pot.location = (plant_x, plant_y, 0.81)
    pot.data.materials.append(mat_plant_pot)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1)
    plant = bpy.context.active_object
    plant.location = (plant_x, plant_y, 0.95)
    plant.data.materials.append(mat_plant)

# ========== 設備區 ==========

# 印表機
bpy.ops.mesh.primitive_cube_add(size=1)
printer = bpy.context.active_object
printer.scale = (0.25, 0.2, 0.12)
printer.location = (-6, -2, 0.86)
printer.data.materials.append(mat_printer)

# 飲水機
bpy.ops.mesh.primitive_cube_add(size=1)
wd = bpy.context.active_object
wd.scale = (0.18, 0.18, 0.5)
wd.location = (-6.5, -4, 0.5)
wd.data.materials.append(mat_water_dispenser)

# 文件櫃
bpy.ops.mesh.primitive_cube_add(size=1)
cab = bpy.context.active_object
cab.scale = (0.5, 0.25, 0.7)
cab.location = (-6.5, 4, 0.7)
cab.data.materials.append(mat_cabinet)

# 垃圾桶
for gx, gy in [(-5, 1), (-2.5, 1), (0, 1), (2.5, 1), (5, 1)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.3)
    tb = bpy.context.active_object
    tb.location = (gx, gy - 0.5, 0.15)
    tb.data.materials.append(mat_trash_bin)

# ========== 天花板燈光 ==========

for lx, ly in [(-4, 2), (0, 2), (4, 2), (-2, -5), (2, -5)]:
    bpy.ops.mesh.primitive_cube_add(size=1)
    lamp_panel = bpy.context.active_object
    lamp_panel.scale = (0.4, 0.15, 0.015)
    lamp_panel.location = (lx, ly, WALL_H - 0.02)
    lamp_panel.data.materials.append(mat_lamp)

print("MODEL_CREATED: office_v23")
