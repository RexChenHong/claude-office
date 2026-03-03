#!/usr/bin/env python3
"""
Claude Office V11 - 修正：
1. 椅子距離不動（保持 V8 的 -0.75）
2. 螢幕朝向使用者（rot + π，不是 rot）
3. 地板加大
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

# ========== 材質 ==========

def create_material(name, color, roughness=0.5, metallic=0.0, emission=None):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    if emission:
        bsdf.inputs['Emission'].default_value = emission
        bsdf.inputs['Emission Strength'].default_value = 0.5
    return mat

mat_floor = create_material("Floor", (0.58, 0.45, 0.35, 1), roughness=0.7)
mat_wall = create_material("Wall", (0.92, 0.92, 0.9, 1), roughness=0.9)
mat_glass = create_material("Glass", (0.7, 0.85, 0.95, 0.15), roughness=0.1)
mat_metal_frame = create_material("Metal_Frame", (0.3, 0.3, 0.32, 1), roughness=0.3, metallic=0.7)
mat_partition = create_material("Partition", (0.88, 0.88, 0.86, 1), roughness=0.8)
mat_desktop = create_material("Desktop", (0.95, 0.95, 0.93, 1), roughness=0.3)
mat_seat = create_material("Seat", (0.22, 0.22, 0.25, 1), roughness=0.8)
mat_metal = create_material("Metal", (0.5, 0.5, 0.52, 1), roughness=0.2, metallic=0.9)
mat_plastic = create_material("Plastic", (0.1, 0.1, 0.1, 1), roughness=0.4)
mat_screen = create_material("Screen", (0.15, 0.18, 0.22, 1), roughness=0.1, emission=(0.25, 0.3, 0.35, 1))
mat_meeting_table = create_material("Meeting_Table", (0.35, 0.28, 0.22, 1), roughness=0.4)
mat_whiteboard = create_material("Whiteboard", (0.98, 0.98, 0.98, 1), roughness=0.3)
mat_sofa = create_material("Sofa", (0.35, 0.35, 0.38, 1), roughness=0.85)
mat_coffee_table = create_material("Coffee_Table", (0.38, 0.28, 0.22, 1), roughness=0.5)
mat_cushion = create_material("Cushion", (0.2, 0.35, 0.5, 1), roughness=0.8)
mat_carpet = create_material("Carpet", (0.45, 0.45, 0.47, 1), roughness=0.95)
mat_coffee_machine = create_material("Coffee_Machine", (0.12, 0.12, 0.12, 1), roughness=0.3, metallic=0.7)
mat_plant_pot = create_material("Pot", (0.55, 0.38, 0.28, 1), roughness=0.7)
mat_plant = create_material("Plant", (0.22, 0.45, 0.22, 1), roughness=0.6)

# ========== 房間尺寸 ==========

ROOM_W = 16
ROOM_D = 14
WALL_H = 2.8

# ========== 地板（完全覆蓋）==========

bpy.ops.mesh.primitive_plane_add(size=1)
floor = bpy.context.active_object
floor.name = "Floor"
# plane size=1，scale 後的實際尺寸是 scale * 1
# 房間是 16x14m，地板應該是 scale=(16, 14, 1) 或更大
floor.scale = (ROOM_W + 2, ROOM_D + 2, 1)  # 18x16m，確保完全覆蓋
floor.data.materials.append(mat_floor)

# ========== 牆壁 ==========

# 後牆
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.name = "Back_Wall"
w.scale = (ROOM_W/2 + 0.15, 0.08, WALL_H/2)
w.location = (0, -ROOM_D/2 - 0.04, WALL_H/2)
w.data.materials.append(mat_wall)

# 前牆左半
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.name = "Front_Wall_Left"
w.scale = (ROOM_W/4 - 0.5, 0.08, WALL_H/2)
w.location = (-ROOM_W/4 - 0.5, ROOM_D/2 + 0.04, WALL_H/2)
w.data.materials.append(mat_wall)

# 前牆右半
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.name = "Front_Wall_Right"
w.scale = (ROOM_W/4 - 0.5, 0.08, WALL_H/2)
w.location = (ROOM_W/4 + 0.5, ROOM_D/2 + 0.04, WALL_H/2)
w.data.materials.append(mat_wall)

# 門上方
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.name = "Front_Wall_Top"
w.scale = (1.2, 0.08, (WALL_H - 2.2)/2)
w.location = (0, ROOM_D/2 + 0.04, 2.2 + (WALL_H - 2.2)/2)
w.data.materials.append(mat_wall)

# 左牆
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.name = "Left_Wall"
w.scale = (0.08, ROOM_D/2, WALL_H/2)
w.location = (-ROOM_W/2 - 0.04, 0, WALL_H/2)
w.data.materials.append(mat_wall)

# 右牆
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.name = "Right_Wall"
w.scale = (0.08, ROOM_D/2, WALL_H/2)
w.location = (ROOM_W/2 + 0.04, 0, WALL_H/2)
w.data.materials.append(mat_wall)

# 落地窗
bpy.ops.mesh.primitive_cube_add(size=1)
window = bpy.context.active_object
window.name = "Window"
window.scale = (0.02, 5, WALL_H/2 - 0.15)
window.location = (ROOM_W/2 + 0.07, 0, WALL_H/2)
window.data.materials.append(mat_glass)

# ========== 會議室（左後角）==========

# 玻璃隔間
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.7, 0.03, WALL_H/2)
w.location = (-6.3, -2, WALL_H/2)
w.data.materials.append(mat_glass)

bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.7, 0.03, WALL_H/2)
w.location = (-3.7, -2, WALL_H/2)
w.data.materials.append(mat_glass)

bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.03, 2, WALL_H/2)
w.location = (-3, -4, WALL_H/2)
w.data.materials.append(mat_glass)

# 會議室框架
for gx, gy in [(-7, -2), (-5, -2), (-3, -2), (-3, -4), (-3, -6)]:
    bpy.ops.mesh.primitive_cube_add(size=1)
    frame = bpy.context.active_object
    frame.scale = (0.04, 0.04, WALL_H/2)
    frame.location = (gx, gy, WALL_H/2)
    frame.data.materials.append(mat_metal_frame)

# 會議桌
bpy.ops.mesh.primitive_cylinder_add(radius=0.6, depth=0.04)
t = bpy.context.active_object
t.scale = (1, 0.7, 1)
t.location = (-5, -4, 0.75)
t.data.materials.append(mat_meeting_table)

# 會議椅
for i in range(4):
    angle = i * (math.pi / 2) + math.pi/4
    cx = -5 + math.cos(angle) * 0.8
    cy = -4 + math.sin(angle) * 0.5
    bpy.ops.mesh.primitive_cube_add(size=1)
    c = bpy.context.active_object
    c.scale = (0.28, 0.28, 0.05)
    c.location = (cx, cy, 0.48)
    c.rotation_euler = (0, 0, angle + math.pi)
    c.data.materials.append(mat_seat)

# 白板
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.02, 0.8, 0.5)
w.location = (-ROOM_W/2 + 0.12, -4, 1.3)
w.data.materials.append(mat_whiteboard)

# ========== 工作站 ==========

def create_workstation(x, y, facing='north', index=1):
    """創建工作站，facing: 使用者面向的方向"""
    
    angles = {'north': 0, 'south': math.pi, 'east': math.pi/2, 'west': -math.pi/2}
    rot = angles[facing]
    
    # 桌子
    bpy.ops.mesh.primitive_cube_add(size=1)
    d = bpy.context.active_object
    d.scale = (1.3, 0.65, 0.025)
    d.location = (x, y, 0.75)
    d.rotation_euler = (0, 0, rot)
    d.data.materials.append(mat_desktop)
    
    # 桌腿
    for dx, dy in [(-0.55, -0.25), (-0.55, 0.25), (0.55, -0.25), (0.55, 0.25)]:
        bx = x + dx * math.cos(rot) - dy * math.sin(rot)
        by = y + dx * math.sin(rot) + dy * math.cos(rot)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.7)
        leg = bpy.context.active_object
        leg.location = (bx, by, 0.375)
        leg.data.materials.append(mat_metal)
    
    # 雙螢幕（在桌子前方，朝向使用者）
    # 使用者面向 rot，螢幕應該在使用者前方，朝向使用者（rot + π）
    for sx in [-0.3, 0.3]:
        bx = x + sx * math.cos(rot) - 0.35 * math.sin(rot)
        by = y + sx * math.sin(rot) + 0.35 * math.cos(rot)
        bpy.ops.mesh.primitive_cube_add(size=1)
        s = bpy.context.active_object
        s.scale = (0.52, 0.025, 0.3)
        s.location = (bx, by, 1.0)
        s.rotation_euler = (0, 0, rot + math.pi)  # 螢幕朝向使用者
        s.data.materials.append(mat_screen)
    
    # 鍵盤
    kx = x - 0.3 * math.sin(rot)
    ky = y + 0.3 * math.cos(rot)
    bpy.ops.mesh.primitive_cube_add(size=1)
    kb = bpy.context.active_object
    kb.scale = (0.35, 0.12, 0.015)
    kb.location = (kx, ky, 0.43)
    kb.rotation_euler = (0, 0, rot)
    kb.data.materials.append(mat_plastic)
    
    # 滑鼠
    bpy.ops.mesh.primitive_cube_add(size=1)
    m = bpy.context.active_object
    m.scale = (0.055, 0.09, 0.025)
    m.location = (kx + 0.22*math.cos(rot), ky + 0.22*math.sin(rot), 0.43)
    m.rotation_euler = (0, 0, rot)
    m.data.materials.append(mat_plastic)
    
    # 椅子（在桌子背面，面向桌子）
    chair_offset = -0.75  # V8 原始值，不動
    chair_x = x + chair_offset * math.sin(rot)
    chair_y = y + chair_offset * math.cos(rot)
    chair_rot = rot  # 面向桌子
    
    # 座椅
    bpy.ops.mesh.primitive_cube_add(size=1)
    seat = bpy.context.active_object
    seat.scale = (0.42, 0.38, 0.08)
    seat.location = (chair_x, chair_y, 0.48)
    seat.rotation_euler = (0, 0, chair_rot)
    seat.data.materials.append(mat_seat)
    
    # 椅背
    back_x = chair_x - 0.17 * math.sin(chair_rot)
    back_y = chair_y - 0.17 * math.cos(chair_rot)
    bpy.ops.mesh.primitive_cube_add(size=1)
    back = bpy.context.active_object
    back.scale = (0.4, 0.055, 0.42)
    back.location = (back_x, back_y, 0.72)
    back.rotation_euler = (math.radians(8), 0, chair_rot)
    back.data.materials.append(mat_seat)
    
    # 椅子支柱
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.32)
    p = bpy.context.active_object
    p.location = (chair_x, chair_y, 0.32)
    p.data.materials.append(mat_metal)
    
    # 五星腳
    for i in range(5):
        angle = chair_rot + i * (2 * math.pi / 5)
        bpy.ops.mesh.primitive_cube_add(size=1)
        arm = bpy.context.active_object
        arm.scale = (0.22, 0.025, 0.02)
        arm.location = (chair_x + math.cos(angle)*0.11, chair_y + math.sin(angle)*0.11, 0.08)
        arm.rotation_euler = (0, 0, angle)
        arm.data.materials.append(mat_metal)
        
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.02)
        wh = bpy.context.active_object
        wh.location = (chair_x + math.cos(angle)*0.22, chair_y + math.sin(angle)*0.22, 0.02)
        wh.data.materials.append(mat_plastic)

# ========== 工作站佈局 ==========

# 左側工作站（面向右/東方，使用者面向窗戶）
create_workstation(-5.5, 1, facing='east', index=1)
create_workstation(-5.5, 3.5, facing='east', index=2)

# 中間工作站（面向前/北方）
create_workstation(-1, 0, facing='north', index=3)

# 右側工作站（面向左/西方，使用者面向窗戶）
create_workstation(5.5, 1, facing='west', index=4)
create_workstation(5.5, 3.5, facing='west', index=5)

# ========== 休息區（右後角）==========

LOUNGE_X, LOUNGE_Y = 5.5, -4.5

bpy.ops.mesh.primitive_plane_add(size=1)
c = bpy.context.active_object
c.scale = (2, 2, 1)
c.location = (LOUNGE_X, LOUNGE_Y, 0.01)
c.data.materials.append(mat_carpet)

bpy.ops.mesh.primitive_cube_add(size=1)
s = bpy.context.active_object
s.scale = (1.3, 0.38, 0.3)
s.location = (LOUNGE_X, LOUNGE_Y - 0.55, 0.3)
s.data.materials.append(mat_sofa)

bpy.ops.mesh.primitive_cube_add(size=1)
s = bpy.context.active_object
s.scale = (1.3, 0.06, 0.22)
s.location = (LOUNGE_X, LOUNGE_Y - 0.78, 0.48)
s.data.materials.append(mat_sofa)

bpy.ops.mesh.primitive_cube_add(size=1)
s = bpy.context.active_object
s.scale = (0.38, 1, 0.3)
s.location = (LOUNGE_X + 0.7, LOUNGE_Y, 0.3)
s.data.materials.append(mat_sofa)

bpy.ops.mesh.primitive_cube_add(size=1)
ct = bpy.context.active_object
ct.scale = (0.5, 0.3, 0.015)
ct.location = (LOUNGE_X + 0.2, LOUNGE_Y + 0.25, 0.36)
ct.data.materials.append(mat_coffee_table)

for dx, dy in [(-0.2, -0.1), (-0.2, 0.1), (0.2, -0.1), (0.2, 0.1)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.32)
    l = bpy.context.active_object
    l.location = (LOUNGE_X + 0.2 + dx, LOUNGE_Y + 0.25 + dy, 0.175)
    l.data.materials.append(mat_metal)

for i in range(3):
    bpy.ops.mesh.primitive_cube_add(size=1)
    c = bpy.context.active_object
    c.scale = (0.14, 0.14, 0.06)
    c.location = (LOUNGE_X - 0.35 + i * 0.35, LOUNGE_Y - 0.5, 0.48)
    c.rotation_euler = (math.radians(8), 0, 0)
    c.data.materials.append(mat_cushion)

# ========== 咖啡區（入口附近）==========

COFFEE_X, COFFEE_Y = 5.5, 4.5

bpy.ops.mesh.primitive_cube_add(size=1)
ht = bpy.context.active_object
ht.scale = (0.4, 0.25, 0.015)
ht.location = (COFFEE_X, COFFEE_Y, 0.9)
ht.data.materials.append(mat_coffee_table)

bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.85)
tp = bpy.context.active_object
tp.location = (COFFEE_X, COFFEE_Y, 0.45)
tp.data.materials.append(mat_metal)

bpy.ops.mesh.primitive_cube_add(size=1)
cm = bpy.context.active_object
cm.scale = (0.09, 0.14, 0.18)
cm.location = (COFFEE_X - 0.08, COFFEE_Y, 1.02)
cm.data.materials.append(mat_coffee_machine)

for i in range(2):
    stool_y = COFFEE_Y - 0.5 - i * 0.3
    bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=0.03)
    ss = bpy.context.active_object
    ss.location = (COFFEE_X + 0.2, stool_y, 0.65)
    ss.data.materials.append(mat_plastic)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.014, depth=0.6)
    sp = bpy.context.active_object
    sp.location = (COFFEE_X + 0.2, stool_y, 0.32)
    sp.data.materials.append(mat_metal)

# ========== 盆栽 ==========

for px, py in [(-6, 5.5), (6, -6), (-6, -6)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.1)
    pot = bpy.context.active_object
    pot.location = (px, py, 0.5)
    pot.data.materials.append(mat_plant_pot)
    
    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.1)
    plant = bpy.context.active_object
    plant.location = (px, py, 0.65)
    plant.scale = (1, 1, 1.15)
    plant.data.materials.append(mat_plant)

print("✅ V11 完成！")
print("修正：螢幕朝向使用者（rot + π），椅子距離保持 V8 原值")
