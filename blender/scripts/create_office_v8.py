#!/usr/bin/env python3
"""
Claude Office V8 - 修正版
1. 無天花板
2. 牆壁連續不斷開
3. 椅子方向正確（面向桌子）
4. 添加隔間
5. 簡化模型先確認佈局，之後再優化
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

mat_floor = create_material("Floor", (0.55, 0.42, 0.32, 1), roughness=0.7)
mat_wall = create_material("Wall", (0.92, 0.92, 0.9, 1), roughness=0.9)
mat_glass = create_material("Glass", (0.7, 0.85, 0.95, 0.15), roughness=0.1)
mat_partition = create_material("Partition", (0.85, 0.85, 0.83, 1), roughness=0.8)
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

ROOM_W = 14  # 寬（X軸）
ROOM_D = 12  # 深（Y軸）
WALL_H = 2.8  # 牆高
WALL_T = 0.15  # 牆厚

# ========== 地板 ==========

bpy.ops.mesh.primitive_plane_add(size=1)
floor = bpy.context.active_object
floor.name = "Floor"
floor.scale = (ROOM_W/2, ROOM_D/2, 1)
floor.location = (0, 0, 0)
floor.data.materials.append(mat_floor)

# ========== 連續牆壁（用一個 mesh）==========

# 創建牆壁 mesh
wall_verts = [
    # 後牆（Y = -ROOM_D/2）
    (-ROOM_W/2, -ROOM_D/2, 0), (ROOM_W/2, -ROOM_D/2, 0),
    (ROOM_W/2, -ROOM_D/2, WALL_H), (-ROOM_W/2, -ROOM_D/2, WALL_H),
    # 右牆
    (ROOM_W/2, -ROOM_D/2, 0), (ROOM_W/2, ROOM_D/2, 0),
    (ROOM_W/2, ROOM_D/2, WALL_H), (ROOM_W/2, -ROOM_D/2, WALL_H),
    # 前牆（Y = ROOM_D/2，有窗戶開口）
    (ROOM_W/2, ROOM_D/2, 0), (-ROOM_W/2, ROOM_D/2, 0),
    (-ROOM_W/2, ROOM_D/2, WALL_H), (ROOM_W/2, ROOM_D/2, WALL_H),
    # 左牆
    (-ROOM_W/2, ROOM_D/2, 0), (-ROOM_W/2, -ROOM_D/2, 0),
    (-ROOM_W/2, -ROOM_D/2, WALL_H), (-ROOM_W/2, ROOM_D/2, WALL_H),
]

# 簡化：用 4 面牆分別創建但緊密相連
# 後牆
bpy.ops.mesh.primitive_cube_add(size=1)
back_wall = bpy.context.active_object
back_wall.name = "Back_Wall"
back_wall.scale = (ROOM_W/2 + WALL_T, WALL_T/2, WALL_H/2)
back_wall.location = (0, -ROOM_D/2 - WALL_T/2, WALL_H/2)
back_wall.data.materials.append(mat_wall)

# 前牆（左半）
bpy.ops.mesh.primitive_cube_add(size=1)
front_wall_left = bpy.context.active_object
front_wall_left.name = "Front_Wall_Left"
front_wall_left.scale = (ROOM_W/4, WALL_T/2, WALL_H/2)
front_wall_left.location = (-ROOM_W/4, ROOM_D/2 + WALL_T/2, WALL_H/2)
front_wall_left.data.materials.append(mat_wall)

# 前牆（右半）
bpy.ops.mesh.primitive_cube_add(size=1)
front_wall_right = bpy.context.active_object
front_wall_right.name = "Front_Wall_Right"
front_wall_right.scale = (ROOM_W/4, WALL_T/2, WALL_H/2)
front_wall_right.location = (ROOM_W/4, ROOM_D/2 + WALL_T/2, WALL_H/2)
front_wall_right.data.materials.append(mat_wall)

# 前牆（上方，門上面）
bpy.ops.mesh.primitive_cube_add(size=1)
front_wall_top = bpy.context.active_object
front_wall_top.name = "Front_Wall_Top"
front_wall_top.scale = (ROOM_W/2 - 2, WALL_T/2, (WALL_H - 2.2)/2)
front_wall_top.location = (0, ROOM_D/2 + WALL_T/2, 2.2 + (WALL_H - 2.2)/2)
front_wall_top.data.materials.append(mat_wall)

# 左牆
bpy.ops.mesh.primitive_cube_add(size=1)
left_wall = bpy.context.active_object
left_wall.name = "Left_Wall"
left_wall.scale = (WALL_T/2, ROOM_D/2, WALL_H/2)
left_wall.location = (-ROOM_W/2 - WALL_T/2, 0, WALL_H/2)
left_wall.data.materials.append(mat_wall)

# 右牆（有落地窗）
bpy.ops.mesh.primitive_cube_add(size=1)
right_wall = bpy.context.active_object
right_wall.name = "Right_Wall"
right_wall.scale = (WALL_T/2, ROOM_D/2, WALL_H/2)
right_wall.location = (ROOM_W/2 + WALL_T/2, 0, WALL_H/2)
right_wall.data.materials.append(mat_wall)

# 落地窗（玻璃）
bpy.ops.mesh.primitive_cube_add(size=1)
window = bpy.context.active_object
window.name = "Window"
window.scale = (0.02, 4, WALL_H/2 - 0.2)
window.location = (ROOM_W/2 + 0.05, 0, WALL_H/2)
window.data.materials.append(mat_glass)

# 窗框
for i in range(4):
    bpy.ops.mesh.primitive_cube_add(size=1)
    frame = bpy.context.active_object
    frame.name = f"Window_Frame_{i}"
    frame.scale = (0.05, 0.05, WALL_H/2 - 0.2)
    frame.location = (ROOM_W/2 + 0.05, -3 + i * 2, WALL_H/2)
    frame.data.materials.append(mat_metal_frame)

# ========== 隔間 ==========

# 辦公區與休息區隔間（矮牆，1.2m 高）
bpy.ops.mesh.primitive_cube_add(size=1)
partition1 = bpy.context.active_object
partition1.name = "Partition_Office_Lounge"
partition1.scale = (0.08, 4, 0.6)
partition1.location = (0, -2, 0.6)
partition1.data.materials.append(mat_partition)

# 會議室玻璃隔間（三面）
MEETING_X, MEETING_Y = -4.5, -3.5
MEETING_W, MEETING_D = 3.5, 3

# 會議室前牆（有門）
bpy.ops.mesh.primitive_cube_add(size=1)
meeting_front = bpy.context.active_object
meeting_front.name = "Meeting_Glass_Front"
meeting_front.scale = (MEETING_W/2 - 0.5, 0.03, WALL_H/2)
meeting_front.location = (MEETING_X, MEETING_Y - MEETING_D/2, WALL_H/2)
meeting_front.data.materials.append(mat_glass)

# 會議室右牆
bpy.ops.mesh.primitive_cube_add(size=1)
meeting_right = bpy.context.active_object
meeting_right.name = "Meeting_Glass_Right"
meeting_right.scale = (0.03, MEETING_D/2, WALL_H/2)
meeting_right.location = (MEETING_X + MEETING_W/2, MEETING_Y, WALL_H/2)
meeting_right.data.materials.append(mat_glass)

# 會議室框架
for corner in [(MEETING_X - MEETING_W/2, MEETING_Y - MEETING_D/2), 
               (MEETING_X + MEETING_W/2, MEETING_Y - MEETING_D/2),
               (MEETING_X + MEETING_W/2, MEETING_Y + MEETING_D/2)]:
    bpy.ops.mesh.primitive_cube_add(size=1)
    corner_frame = bpy.context.active_object
    corner_frame.scale = (0.04, 0.04, WALL_H/2)
    corner_frame.location = (corner[0], corner[1], WALL_H/2)
    corner_frame.data.materials.append(mat_metal_frame)

# ========== 工作站（椅子正確面向桌子）==========

def create_workstation(x, y, facing='north', index=1):
    """創建工作站，facing: 'north'(面向Y+), 'south'(面向Y-), 'east'(面向X+), 'west'(面向X-)"""
    
    # 計算旋轉角度
    angles = {'north': 0, 'south': math.pi, 'east': math.pi/2, 'west': -math.pi/2}
    rot = angles[facing]
    
    # 桌子
    bpy.ops.mesh.primitive_cube_add(size=1)
    desktop = bpy.context.active_object
    desktop.name = f"Desktop_{index}"
    desktop.scale = (1.3, 0.65, 0.025)
    desktop.location = (x, y, 0.75)
    desktop.rotation_euler = (0, 0, rot)
    desktop.data.materials.append(mat_desktop)
    
    # 桌腿
    for dx, dy in [(-0.55, -0.25), (-0.55, 0.25), (0.55, -0.25), (0.55, 0.25)]:
        bx = x + dx * math.cos(rot) - dy * math.sin(rot)
        by = y + dx * math.sin(rot) + dy * math.cos(rot)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.7)
        leg = bpy.context.active_object
        leg.location = (bx, by, 0.375)
        leg.data.materials.append(mat_metal)
    
    # 雙螢幕
    for sx in [-0.3, 0.3]:
        bx = x + sx * math.cos(rot) - 0.35 * math.sin(rot)
        by = y + sx * math.sin(rot) + 0.35 * math.cos(rot)
        bpy.ops.mesh.primitive_cube_add(size=1)
        screen = bpy.context.active_object
        screen.name = f"Screen_{index}"
        screen.scale = (0.52, 0.025, 0.3)
        screen.location = (bx, by, 1.0)
        screen.rotation_euler = (0, 0, rot)
        screen.data.materials.append(mat_screen)
    
    # 鍵盤
    kx = x - 0.3 * math.sin(rot)
    ky = y + 0.3 * math.cos(rot)
    bpy.ops.mesh.primitive_cube_add(size=1)
    kb = bpy.context.active_object
    kb.name = f"Keyboard_{index}"
    kb.scale = (0.35, 0.12, 0.015)
    kb.location = (kx, ky, 0.43)
    kb.rotation_euler = (0, 0, rot)
    kb.data.materials.append(mat_plastic)
    
    # 滑鼠
    bpy.ops.mesh.primitive_cube_add(size=1)
    mouse = bpy.context.active_object
    mouse.name = f"Mouse_{index}"
    mouse.scale = (0.055, 0.09, 0.025)
    mouse.location = (kx + 0.22*math.cos(rot), ky + 0.22*math.sin(rot), 0.43)
    mouse.rotation_euler = (0, 0, rot)
    mouse.data.materials.append(mat_plastic)
    
    # 椅子（在桌子背面，面向桌子）
    # 椅子位置：桌子背面 + 0.7m
    chair_offset = -0.75  # 背面方向
    chair_x = x + chair_offset * math.sin(rot)
    chair_y = y + chair_offset * math.cos(rot)
    chair_rot = rot  # 椅子面向桌子（同方向）
    
    # 座椅
    bpy.ops.mesh.primitive_cube_add(size=1)
    seat = bpy.context.active_object
    seat.name = f"Seat_{index}"
    seat.scale = (0.42, 0.38, 0.08)
    seat.location = (chair_x, chair_y, 0.48)
    seat.rotation_euler = (0, 0, chair_rot)
    seat.data.materials.append(mat_seat)
    
    # 椅背（在座椅背面）
    back_x = chair_x - 0.17 * math.sin(chair_rot)
    back_y = chair_y - 0.17 * math.cos(chair_rot)
    bpy.ops.mesh.primitive_cube_add(size=1)
    back = bpy.context.active_object
    back.name = f"Backrest_{index}"
    back.scale = (0.4, 0.055, 0.42)
    back.location = (back_x, back_y, 0.73)
    back.rotation_euler = (math.radians(8), 0, chair_rot)
    back.data.materials.append(mat_seat)
    
    # 椅子支柱
    bpy.ops.mesh.primitive_cylinder_add(radius=0.028, depth=0.3)
    pillar = bpy.context.active_object
    pillar.name = f"Chair_Pillar_{index}"
    pillar.location = (chair_x, chair_y, 0.3)
    pillar.data.materials.append(mat_metal)
    
    # 五星腳
    for i in range(5):
        angle = chair_rot + i * (2 * math.pi / 5)
        lx = chair_x + math.cos(angle) * 0.22
        ly = chair_y + math.sin(angle) * 0.22
        
        bpy.ops.mesh.primitive_cube_add(size=1)
        arm = bpy.context.active_object
        arm.scale = (0.24, 0.025, 0.018)
        arm.location = (chair_x + math.cos(angle)*0.11, chair_y + math.sin(angle)*0.11, 0.08)
        arm.rotation_euler = (0, 0, angle)
        arm.data.materials.append(mat_metal)
        
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.02)
        wheel = bpy.context.active_object
        wheel.location = (lx, ly, 0.02)
        wheel.data.materials.append(mat_plastic)

# ========== 辦公區佈局 ==========

# 左側工作站區（3 個，面向右/窗戶）
create_workstation(-4.5, -1.5, facing='east', index=1)
create_workstation(-4.5, 1.5, facing='east', index=2)

# 右側工作站區（2 個，面向左）
create_workstation(4.5, 0, facing='west', index=3)

# 中間工作站（面向前）
create_workstation(0, 1.5, facing='north', index=4)
create_workstation(0, -1.5, facing='south', index=5)

# ========== 會議室 ==========

# 會議桌
bpy.ops.mesh.primitive_cylinder_add(radius=0.65, depth=0.04)
meeting_table = bpy.context.active_object
meeting_table.name = "Meeting_Table"
meeting_table.scale = (1, 0.7, 1)  # 橢圓形
meeting_table.location = (MEETING_X, MEETING_Y, 0.75)
meeting_table.data.materials.append(mat_meeting_table)

# 會議椅（4 張，面向桌子中心）
for i in range(4):
    angle = i * (math.pi / 2) + math.pi/4
    cx = MEETING_X + math.cos(angle) * 0.85
    cy = MEETING_Y + math.sin(angle) * 0.55
    
    bpy.ops.mesh.primitive_cube_add(size=1)
    chair = bpy.context.active_object
    chair.name = f"Meeting_Chair_{i+1}"
    chair.scale = (0.3, 0.3, 0.055)
    chair.location = (cx, cy, 0.48)
    chair.rotation_euler = (0, 0, angle + math.pi)  # 面向桌子
    chair.data.materials.append(mat_seat)

# 白板
bpy.ops.mesh.primitive_cube_add(size=1)
whiteboard = bpy.context.active_object
whiteboard.name = "Whiteboard"
whiteboard.scale = (0.02, 0.85, 0.55)
whiteboard.location = (-ROOM_W/2 + 0.1, MEETING_Y, 1.35)
whiteboard.data.materials.append(mat_whiteboard)

# ========== 休息區（右後角）==========

LOUNGE_X, LOUNGE_Y = 4.5, -4

# 地毯
bpy.ops.mesh.primitive_plane_add(size=1)
carpet = bpy.context.active_object
carpet.name = "Carpet"
carpet.scale = (2.2, 2.2, 1)
carpet.location = (LOUNGE_X, LOUNGE_Y, 0.01)
carpet.data.materials.append(mat_carpet)

# L 型沙發
bpy.ops.mesh.primitive_cube_add(size=1)
sofa_main = bpy.context.active_object
sofa_main.name = "Sofa_Main"
sofa_main.scale = (1.4, 0.42, 0.32)
sofa_main.location = (LOUNGE_X, LOUNGE_Y - 0.6, 0.32)
sofa_main.data.materials.append(mat_sofa)

bpy.ops.mesh.primitive_cube_add(size=1)
sofa_back = bpy.context.active_object
sofa_back.name = "Sofa_Back"
sofa_back.scale = (1.4, 0.07, 0.25)
sofa_back.location = (LOUNGE_X, LOUNGE_Y - 0.85, 0.52)
sofa_back.data.materials.append(mat_sofa)

bpy.ops.mesh.primitive_cube_add(size=1)
sofa_side = bpy.context.active_object
sofa_side.name = "Sofa_Side"
sofa_side.scale = (0.42, 1.1, 0.32)
sofa_side.location = (LOUNGE_X + 0.75, LOUNGE_Y, 0.32)
sofa_side.data.materials.append(mat_sofa)

# 茶几
bpy.ops.mesh.primitive_cube_add(size=1)
coffee_table = bpy.context.active_object
coffee_table.name = "Coffee_Table"
coffee_table.scale = (0.55, 0.32, 0.018)
coffee_table.location = (LOUNGE_X + 0.25, LOUNGE_Y + 0.3, 0.38)
coffee_table.data.materials.append(mat_coffee_table)

# 茶几腿
for dx, dy in [(-0.22, -0.11), (-0.22, 0.11), (0.22, -0.11), (0.22, 0.11)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.35)
    leg = bpy.context.active_object
    leg.location = (LOUNGE_X + 0.25 + dx, LOUNGE_Y + 0.3 + dy, 0.195)
    leg.data.materials.append(mat_metal)

# 靠墊
for i in range(3):
    bpy.ops.mesh.primitive_cube_add(size=1)
    cushion = bpy.context.active_object
    cushion.name = f"Cushion_{i+1}"
    cushion.scale = (0.16, 0.16, 0.07)
    cushion.location = (LOUNGE_X - 0.4 + i * 0.4, LOUNGE_Y - 0.55, 0.52)
    cushion.rotation_euler = (math.radians(10), 0, 0)
    cushion.data.materials.append(mat_cushion)

# ========== 咖啡區（入口附近）==========

COFFEE_X, COFFEE_Y = 4.5, 4

# 高桌
bpy.ops.mesh.primitive_cube_add(size=1)
high_table = bpy.context.active_object
high_table.name = "High_Table"
high_table.scale = (0.45, 0.28, 0.018)
high_table.location = (COFFEE_X, COFFEE_Y, 0.95)
high_table.data.materials.append(mat_coffee_table)

bpy.ops.mesh.primitive_cylinder_add(radius=0.022, depth=0.9)
table_pole = bpy.context.active_object
table_pole.location = (COFFEE_X, COFFEE_Y, 0.48)
table_pole.data.materials.append(mat_metal)

# 咖啡機
bpy.ops.mesh.primitive_cube_add(size=1)
coffee_machine = bpy.context.active_object
coffee_machine.name = "Coffee_Machine"
coffee_machine.scale = (0.1, 0.16, 0.2)
coffee_machine.location = (COFFEE_X - 0.1, COFFEE_Y, 1.08)
coffee_machine.data.materials.append(mat_coffee_machine)

# 高腳椅
for i in range(2):
    stool_y = COFFEE_Y - 0.55 - i * 0.32
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.035)
    stool_seat = bpy.context.active_object
    stool_seat.name = f"Stool_{i+1}"
    stool_seat.location = (COFFEE_X + 0.22, stool_y, 0.7)
    stool_seat.data.materials.append(mat_plastic)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.65)
    stool_pole = bpy.context.active_object
    stool_pole.location = (COFFEE_X + 0.22, stool_y, 0.35)
    stool_pole.data.materials.append(mat_metal)

# ========== 盆栽 ==========

for px, py in [(-5.5, 4.5), (5.5, -5), (-5.5, -5.5)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.12)
    pot = bpy.context.active_object
    pot.location = (px, py, 0.52)
    pot.data.materials.append(mat_plant_pot)
    
    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.12)
    plant = bpy.context.active_object
    plant.location = (px, py, 0.68)
    plant.scale = (1, 1, 1.2)
    plant.data.materials.append(mat_plant)

print("✅ V8 創建完成！")
print("修正：無天花板、牆壁連續、椅子方向正確、隔間分明")
