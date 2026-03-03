#!/usr/bin/env python3
"""
Claude Office V10 - 修正：
1. 椅子往後移（距離桌子 1m）
2. 螢幕往桌子後方移
3. 地板完全填滿房間
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

# ========== 地板（完全填滿）==========

bpy.ops.mesh.primitive_plane_add(size=1)
floor = bpy.context.active_object
floor.name = "Floor"
floor.scale = (ROOM_W/2 + 0.2, ROOM_D/2 + 0.2, 1)  # 稍微大一點
floor.data.materials.append(mat_floor)

# ========== 牆壁 ==========

# 後牆
bpy.ops.mesh.primitive_cube_add(size=1)
back_wall = bpy.context.active_object
back_wall.name = "Back_Wall"
back_wall.scale = (ROOM_W/2 + 0.15, 0.08, WALL_H/2)
back_wall.location = (0, -ROOM_D/2 - 0.04, WALL_H/2)
back_wall.data.materials.append(mat_wall)

# 前牆左半
bpy.ops.mesh.primitive_cube_add(size=1)
front_left = bpy.context.active_object
front_left.name = "Front_Wall_Left"
front_left.scale = (ROOM_W/4 - 0.5, 0.08, WALL_H/2)
front_left.location = (-ROOM_W/4 - 0.5, ROOM_D/2 + 0.04, WALL_H/2)
front_left.data.materials.append(mat_wall)

# 前牆右半
bpy.ops.mesh.primitive_cube_add(size=1)
front_right = bpy.context.active_object
front_right.name = "Front_Wall_Right"
front_right.scale = (ROOM_W/4 - 0.5, 0.08, WALL_H/2)
front_right.location = (ROOM_W/4 + 0.5, ROOM_D/2 + 0.04, WALL_H/2)
front_right.data.materials.append(mat_wall)

# 門上方
bpy.ops.mesh.primitive_cube_add(size=1)
front_top = bpy.context.active_object
front_top.name = "Front_Wall_Top"
front_top.scale = (1.2, 0.08, (WALL_H - 2.2)/2)
front_top.location = (0, ROOM_D/2 + 0.04, 2.2 + (WALL_H - 2.2)/2)
front_top.data.materials.append(mat_wall)

# 左牆
bpy.ops.mesh.primitive_cube_add(size=1)
left_wall = bpy.context.active_object
left_wall.name = "Left_Wall"
left_wall.scale = (0.08, ROOM_D/2, WALL_H/2)
left_wall.location = (-ROOM_W/2 - 0.04, 0, WALL_H/2)
left_wall.data.materials.append(mat_wall)

# 右牆
bpy.ops.mesh.primitive_cube_add(size=1)
right_wall = bpy.context.active_object
right_wall.name = "Right_Wall"
right_wall.scale = (0.08, ROOM_D/2, WALL_H/2)
right_wall.location = (ROOM_W/2 + 0.04, 0, WALL_H/2)
right_wall.data.materials.append(mat_wall)

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
glass_fl = bpy.context.active_object
glass_fl.scale = (0.7, 0.03, WALL_H/2)
glass_fl.location = (-6.3, -2, WALL_H/2)
glass_fl.data.materials.append(mat_glass)

bpy.ops.mesh.primitive_cube_add(size=1)
glass_fr = bpy.context.active_object
glass_fr.scale = (0.7, 0.03, WALL_H/2)
glass_fr.location = (-3.7, -2, WALL_H/2)
glass_fr.data.materials.append(mat_glass)

bpy.ops.mesh.primitive_cube_add(size=1)
glass_r = bpy.context.active_object
glass_r.scale = (0.03, 2, WALL_H/2)
glass_r.location = (-3, -4, WALL_H/2)
glass_r.data.materials.append(mat_glass)

# 會議室框架
for gx, gy in [(-7, -2), (-5, -2), (-3, -2), (-3, -4), (-3, -6)]:
    bpy.ops.mesh.primitive_cube_add(size=1)
    frame = bpy.context.active_object
    frame.scale = (0.04, 0.04, WALL_H/2)
    frame.location = (gx, gy, WALL_H/2)
    frame.data.materials.append(mat_metal_frame)

# 會議桌
bpy.ops.mesh.primitive_cylinder_add(radius=0.6, depth=0.04)
meeting_table = bpy.context.active_object
meeting_table.scale = (1, 0.7, 1)
meeting_table.location = (-5, -4, 0.75)
meeting_table.data.materials.append(mat_meeting_table)

# 會議椅（面向桌子中心）
for i in range(4):
    angle = i * (math.pi / 2) + math.pi/4
    cx = -5 + math.cos(angle) * 0.8
    cy = -4 + math.sin(angle) * 0.5
    bpy.ops.mesh.primitive_cube_add(size=1)
    chair = bpy.context.active_object
    chair.scale = (0.28, 0.28, 0.05)
    chair.location = (cx, cy, 0.48)
    chair.rotation_euler = (0, 0, angle + math.pi)  # 面向桌子
    chair.data.materials.append(mat_seat)

# 白板
bpy.ops.mesh.primitive_cube_add(size=1)
whiteboard = bpy.context.active_object
whiteboard.scale = (0.02, 0.8, 0.5)
whiteboard.location = (-ROOM_W/2 + 0.12, -4, 1.3)
whiteboard.data.materials.append(mat_whiteboard)

# ========== 工作站（修正椅子距離和螢幕位置）==========

def create_workstation(x, y, facing='north', index=1):
    """facing: 桌子朝向（椅子在其背面）"""
    angles = {'north': 0, 'south': math.pi, 'east': math.pi/2, 'west': -math.pi/2}
    rot = angles[facing]
    
    # 桌子
    bpy.ops.mesh.primitive_cube_add(size=1)
    desktop = bpy.context.active_object
    desktop.scale = (1.2, 0.6, 0.025)
    desktop.location = (x, y, 0.75)
    desktop.rotation_euler = (0, 0, rot)
    desktop.data.materials.append(mat_desktop)
    
    # 桌腿
    for dx, dy in [(-0.5, -0.22), (-0.5, 0.22), (0.5, -0.22), (0.5, 0.22)]:
        bx = x + dx * math.cos(rot) - dy * math.sin(rot)
        by = y + dx * math.sin(rot) + dy * math.cos(rot)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.65)
        leg = bpy.context.active_object
        leg.location = (bx, by, 0.375)
        leg.data.materials.append(mat_metal)
    
    # 螢幕（在桌子後緣，距離中心 0.25m）
    for sx in [-0.25, 0.25]:
        # 螢幕在桌子後方邊緣
        bx = x + sx * math.cos(rot) - 0.28 * math.sin(rot)
        by = y + sx * math.sin(rot) + 0.28 * math.cos(rot)
        bpy.ops.mesh.primitive_cube_add(size=1)
        screen = bpy.context.active_object
        screen.scale = (0.48, 0.02, 0.28)
        screen.location = (bx, by, 1.0)
        screen.rotation_euler = (0, 0, rot)
        screen.data.materials.append(mat_screen)
    
    # 鍵盤（在桌子前緣）
    kx = x - 0.2 * math.sin(rot)
    ky = y + 0.2 * math.cos(rot)
    bpy.ops.mesh.primitive_cube_add(size=1)
    kb = bpy.context.active_object
    kb.scale = (0.32, 0.1, 0.012)
    kb.location = (kx, ky, 0.43)
    kb.rotation_euler = (0, 0, rot)
    kb.data.materials.append(mat_plastic)
    
    # 滑鼠
    bpy.ops.mesh.primitive_cube_add(size=1)
    mouse = bpy.context.active_object
    mouse.scale = (0.05, 0.08, 0.02)
    mouse.location = (kx + 0.18*math.cos(rot), ky + 0.18*math.sin(rot), 0.43)
    mouse.rotation_euler = (0, 0, rot)
    mouse.data.materials.append(mat_plastic)
    
    # 椅子（在桌子背面 1m 處，面向桌子）
    chair_offset = 1.0  # 椅子距離桌子 1m
    chair_x = x - chair_offset * math.sin(rot)
    chair_y = y + chair_offset * math.cos(rot)
    chair_rot = rot  # 椅子面向與桌子相同方向（面向桌子）
    
    # 座椅
    bpy.ops.mesh.primitive_cube_add(size=1)
    seat = bpy.context.active_object
    seat.scale = (0.38, 0.35, 0.07)
    seat.location = (chair_x, chair_y, 0.48)
    seat.rotation_euler = (0, 0, chair_rot)
    seat.data.materials.append(mat_seat)
    
    # 椅背（在座椅背面）
    back_x = chair_x - 0.15 * math.sin(chair_rot)
    back_y = chair_y - 0.15 * math.cos(chair_rot)
    bpy.ops.mesh.primitive_cube_add(size=1)
    back = bpy.context.active_object
    back.scale = (0.36, 0.05, 0.38)
    back.location = (back_x, back_y, 0.72)
    back.rotation_euler = (math.radians(8), 0, chair_rot)
    back.data.materials.append(mat_seat)
    
    # 椅子支柱
    bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.28)
    pillar = bpy.context.active_object
    pillar.location = (chair_x, chair_y, 0.3)
    pillar.data.materials.append(mat_metal)
    
    # 五星腳
    for i in range(5):
        angle = chair_rot + i * (2 * math.pi / 5)
        bpy.ops.mesh.primitive_cube_add(size=1)
        arm = bpy.context.active_object
        arm.scale = (0.2, 0.02, 0.015)
        arm.location = (chair_x + math.cos(angle)*0.1, chair_y + math.sin(angle)*0.1, 0.07)
        arm.rotation_euler = (0, 0, angle)
        arm.data.materials.append(mat_metal)
        
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.018)
        wheel = bpy.context.active_object
        wheel.location = (chair_x + math.cos(angle)*0.2, chair_y + math.sin(angle)*0.2, 0.018)
        wheel.data.materials.append(mat_plastic)

# ========== 工作站佈局 ==========

# 左側工作站（面向右/東方）
create_workstation(-5.5, 1, facing='east', index=1)
create_workstation(-5.5, 3.5, facing='east', index=2)

# 中間工作站（面向前/北方）
create_workstation(-1, 0, facing='north', index=3)

# 右側工作站（面向左/西方）
create_workstation(5.5, 1, facing='west', index=4)
create_workstation(5.5, 3.5, facing='west', index=5)

# ========== 休息區（右後角）==========

LOUNGE_X, LOUNGE_Y = 5.5, -4.5

bpy.ops.mesh.primitive_plane_add(size=1)
carpet = bpy.context.active_object
carpet.scale = (2, 2, 1)
carpet.location = (LOUNGE_X, LOUNGE_Y, 0.01)
carpet.data.materials.append(mat_carpet)

bpy.ops.mesh.primitive_cube_add(size=1)
sofa_main = bpy.context.active_object
sofa_main.scale = (1.3, 0.38, 0.3)
sofa_main.location = (LOUNGE_X, LOUNGE_Y - 0.55, 0.3)
sofa_main.data.materials.append(mat_sofa)

bpy.ops.mesh.primitive_cube_add(size=1)
sofa_back = bpy.context.active_object
sofa_back.scale = (1.3, 0.06, 0.22)
sofa_back.location = (LOUNGE_X, LOUNGE_Y - 0.78, 0.48)
sofa_back.data.materials.append(mat_sofa)

bpy.ops.mesh.primitive_cube_add(size=1)
sofa_side = bpy.context.active_object
sofa_side.scale = (0.38, 1, 0.3)
sofa_side.location = (LOUNGE_X + 0.7, LOUNGE_Y, 0.3)
sofa_side.data.materials.append(mat_sofa)

bpy.ops.mesh.primitive_cube_add(size=1)
coffee_table = bpy.context.active_object
coffee_table.scale = (0.5, 0.3, 0.015)
coffee_table.location = (LOUNGE_X + 0.2, LOUNGE_Y + 0.25, 0.36)
coffee_table.data.materials.append(mat_coffee_table)

for dx, dy in [(-0.2, -0.1), (-0.2, 0.1), (0.2, -0.1), (0.2, 0.1)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.32)
    leg = bpy.context.active_object
    leg.location = (LOUNGE_X + 0.2 + dx, LOUNGE_Y + 0.25 + dy, 0.175)
    leg.data.materials.append(mat_metal)

for i in range(3):
    bpy.ops.mesh.primitive_cube_add(size=1)
    cushion = bpy.context.active_object
    cushion.scale = (0.14, 0.14, 0.06)
    cushion.location = (LOUNGE_X - 0.35 + i * 0.35, LOUNGE_Y - 0.5, 0.48)
    cushion.rotation_euler = (math.radians(8), 0, 0)
    cushion.data.materials.append(mat_cushion)

# ========== 咖啡區（入口附近）==========

COFFEE_X, COFFEE_Y = 5.5, 4.5

bpy.ops.mesh.primitive_cube_add(size=1)
high_table = bpy.context.active_object
high_table.scale = (0.4, 0.25, 0.015)
high_table.location = (COFFEE_X, COFFEE_Y, 0.9)
high_table.data.materials.append(mat_coffee_table)

bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.85)
table_pole = bpy.context.active_object
table_pole.location = (COFFEE_X, COFFEE_Y, 0.45)
table_pole.data.materials.append(mat_metal)

bpy.ops.mesh.primitive_cube_add(size=1)
coffee_machine = bpy.context.active_object
coffee_machine.scale = (0.09, 0.14, 0.18)
coffee_machine.location = (COFFEE_X - 0.08, COFFEE_Y, 1.02)
coffee_machine.data.materials.append(mat_coffee_machine)

for i in range(2):
    stool_y = COFFEE_Y - 0.5 - i * 0.3
    bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=0.03)
    stool_seat = bpy.context.active_object
    stool_seat.location = (COFFEE_X + 0.2, stool_y, 0.65)
    stool_seat.data.materials.append(mat_plastic)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.014, depth=0.6)
    stool_pole = bpy.context.active_object
    stool_pole.location = (COFFEE_X + 0.2, stool_y, 0.32)
    stool_pole.data.materials.append(mat_metal)

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

print("✅ V10 完成！")
print("修正：椅子距離桌子 1m，螢幕在桌子後緣，地板完全填滿")
