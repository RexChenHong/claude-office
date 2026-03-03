#!/usr/bin/env python3
"""
創建真實辦公室場景（V7 - 修正佈局）
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

# ========== 材質定義 ==========

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

# 材質
mat_floor = create_material("Floor", (0.55, 0.4, 0.28, 1), roughness=0.7)
mat_wall = create_material("Wall", (0.92, 0.92, 0.9, 1), roughness=0.9)
mat_ceiling = create_material("Ceiling", (0.98, 0.98, 0.98, 1), roughness=0.95)
mat_glass = create_material("Glass", (0.7, 0.85, 0.95, 0.2), roughness=0.1)
mat_metal_frame = create_material("Metal_Frame", (0.25, 0.25, 0.28, 1), roughness=0.3, metallic=0.8)
mat_desktop = create_material("Desktop", (0.95, 0.95, 0.93, 1), roughness=0.3)
mat_seat = create_material("Seat_Grey", (0.25, 0.25, 0.28, 1), roughness=0.8)
mat_metal = create_material("Metal", (0.55, 0.55, 0.58, 1), roughness=0.2, metallic=0.9)
mat_plastic = create_material("Plastic", (0.08, 0.08, 0.08, 1), roughness=0.4)
mat_screen = create_material("Screen", (0.1, 0.1, 0.12, 1), roughness=0.1, emission=(0.2, 0.25, 0.3, 1))
mat_lamp = create_material("Lamp", (0.95, 0.95, 0.95, 1), roughness=0.5)
mat_light = create_material("Light", (1.0, 0.98, 0.92, 1), roughness=0.1, emission=(1, 0.98, 0.92, 1))
mat_plant_pot = create_material("Pot", (0.6, 0.4, 0.3, 1), roughness=0.7)
mat_plant = create_material("Plant", (0.2, 0.45, 0.2, 1), roughness=0.6)
mat_meeting_table = create_material("Meeting_Table", (0.35, 0.28, 0.22, 1), roughness=0.4)
mat_whiteboard = create_material("Whiteboard", (0.98, 0.98, 0.98, 1), roughness=0.3)
mat_sofa = create_material("Sofa", (0.4, 0.4, 0.42, 1), roughness=0.85)
mat_coffee_table = create_material("Coffee_Table", (0.38, 0.28, 0.22, 1), roughness=0.5)
mat_cushion = create_material("Cushion", (0.2, 0.35, 0.55, 1), roughness=0.8)
mat_carpet = create_material("Carpet", (0.45, 0.45, 0.47, 1), roughness=0.95)
mat_coffee_machine = create_material("Coffee_Machine", (0.12, 0.12, 0.12, 1), roughness=0.3, metallic=0.7)

# ========== 較小的辦公室（12m x 10m）==========

ROOM_W = 12  # 寬（X軸）
ROOM_D = 10  # 深（Y軸）
ROOM_H = 2.8  # 高

# 地板
bpy.ops.mesh.primitive_plane_add(size=1)
floor = bpy.context.active_object
floor.name = "Floor"
floor.scale = (ROOM_W/2, ROOM_D/2, 1)
floor.location = (0, 0, 0)
floor.data.materials.append(mat_floor)

# 天花板
bpy.ops.mesh.primitive_plane_add(size=1)
ceiling = bpy.context.active_object
ceiling.name = "Ceiling"
ceiling.scale = (ROOM_W/2, ROOM_D/2, 1)
ceiling.location = (0, 0, ROOM_H)
ceiling.rotation_euler = (math.pi, 0, 0)
ceiling.data.materials.append(mat_ceiling)

# 牆面（四面）
# 後牆（Y = -ROOM_D/2）
bpy.ops.mesh.primitive_cube_add(size=1)
back_wall = bpy.context.active_object
back_wall.name = "Back_Wall"
back_wall.scale = (ROOM_W/2, 0.1, ROOM_H/2)
back_wall.location = (0, -ROOM_D/2, ROOM_H/2)
back_wall.data.materials.append(mat_wall)

# 前牆（Y = ROOM_D/2，有窗）
bpy.ops.mesh.primitive_cube_add(size=1)
front_wall = bpy.context.active_object
front_wall.name = "Front_Wall"
front_wall.scale = (ROOM_W/2, 0.1, ROOM_H/2)
front_wall.location = (0, ROOM_D/2, ROOM_H/2)
front_wall.data.materials.append(mat_wall)

# 左牆
bpy.ops.mesh.primitive_cube_add(size=1)
left_wall = bpy.context.active_object
left_wall.name = "Left_Wall"
left_wall.scale = (0.1, ROOM_D/2, ROOM_H/2)
left_wall.location = (-ROOM_W/2, 0, ROOM_H/2)
left_wall.data.materials.append(mat_wall)

# 右牆（有落地窗）
bpy.ops.mesh.primitive_cube_add(size=1)
right_wall = bpy.context.active_object
right_wall.name = "Right_Wall"
right_wall.scale = (0.1, ROOM_D/2, ROOM_H/2)
right_wall.location = (ROOM_W/2, 0, ROOM_H/2)
right_wall.data.materials.append(mat_wall)

# 落地窗（右牆）
bpy.ops.mesh.primitive_cube_add(size=1)
window = bpy.context.active_object
window.name = "Window"
window.scale = (0.02, 3, ROOM_H/2 - 0.2)
window.location = (ROOM_W/2 - 0.05, 0, ROOM_H/2)
window.data.materials.append(mat_glass)

# 窗框
for i in range(3):
    bpy.ops.mesh.primitive_cube_add(size=1)
    frame = bpy.context.active_object
    frame.name = f"Window_Frame_{i}"
    frame.scale = (0.04, 0.04, ROOM_H/2 - 0.2)
    frame.location = (ROOM_W/2 - 0.05, -2.5 + i * 2.5, ROOM_H/2)
    frame.data.materials.append(mat_metal_frame)

# ========== 天花板燈具 ==========

for i in range(6):
    lx = -3.5 + (i % 3) * 3.5
    ly = -2 + (i // 3) * 4
    
    bpy.ops.mesh.primitive_cube_add(size=1)
    light_box = bpy.context.active_object
    light_box.name = f"Light_{i+1}"
    light_box.scale = (0.6, 0.6, 0.03)
    light_box.location = (lx, ly, ROOM_H - 0.03)
    light_box.data.materials.append(mat_lamp)

# ========== 工作站函數 ==========

def create_workstation(x, y, rotation=0, index=1):
    """創建工作站（面向桌子的方向）"""
    
    # 桌面
    bpy.ops.mesh.primitive_cube_add(size=1)
    desktop = bpy.context.active_object
    desktop.name = f"Desktop_{index}"
    desktop.scale = (1.4, 0.7, 0.025)
    desktop.location = (x, y, 0.75)
    desktop.rotation_euler = (0, 0, rotation)
    desktop.data.materials.append(mat_desktop)
    
    # 桌腿（4 個）
    for i, (dx, dy) in enumerate([(-0.6, -0.28), (-0.6, 0.28), (0.6, -0.28), (0.6, 0.28)]):
        bx = x + dx * math.cos(rotation) - dy * math.sin(rotation)
        by = y + dx * math.sin(rotation) + dy * math.cos(rotation)
        
        bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.7)
        leg = bpy.context.active_object
        leg.name = f"Leg_{index}_{i+1}"
        leg.location = (bx, by, 0.375)
        leg.data.materials.append(mat_metal)
    
    # 雙螢幕
    for j, sx in enumerate([-0.35, 0.35]):
        bx = x + sx * math.cos(rotation)
        by = y + sx * math.sin(rotation) - 0.4 * math.cos(rotation + math.pi/2)
        
        bpy.ops.mesh.primitive_cube_add(size=1)
        screen = bpy.context.active_object
        screen.name = f"Screen_{index}_{j+1}"
        screen.scale = (0.55, 0.03, 0.32)
        screen.location = (bx, by, 1.05)
        screen.rotation_euler = (0, 0, rotation)
        screen.data.materials.append(mat_screen)
    
    # 鍵盤
    kx = x - 0.35 * math.sin(rotation)
    ky = y - 0.35 * math.cos(rotation)
    bpy.ops.mesh.primitive_cube_add(size=1)
    kb = bpy.context.active_object
    kb.name = f"Keyboard_{index}"
    kb.scale = (0.4, 0.14, 0.015)
    kb.location = (kx, ky, 0.43)
    kb.rotation_euler = (0, 0, rotation)
    kb.data.materials.append(mat_plastic)
    
    # 滑鼠
    mx = kx + 0.28 * math.cos(rotation)
    my = ky + 0.28 * math.sin(rotation)
    bpy.ops.mesh.primitive_cube_add(size=1)
    mouse = bpy.context.active_object
    mouse.name = f"Mouse_{index}"
    mouse.scale = (0.06, 0.1, 0.025)
    mouse.location = (mx, my, 0.43)
    mouse.rotation_euler = (0, 0, rotation)
    mouse.data.materials.append(mat_plastic)
    
    # 辦公椅（桌子對面）
    chair_x = x + 0.8 * math.sin(rotation)
    chair_y = y + 0.8 * math.cos(rotation)
    
    # 座椅
    bpy.ops.mesh.primitive_cube_add(size=1)
    seat = bpy.context.active_object
    seat.name = f"Seat_{index}"
    seat.scale = (0.45, 0.4, 0.08)
    seat.location = (chair_x, chair_y, 0.48)
    seat.rotation_euler = (0, 0, rotation + math.pi)
    seat.data.materials.append(mat_seat)
    
    # 椅背
    bpy.ops.mesh.primitive_cube_add(size=1)
    back = bpy.context.active_object
    back.name = f"Backrest_{index}"
    back.scale = (0.42, 0.06, 0.45)
    back.location = (chair_x + 0.18*math.sin(rotation+math.pi), chair_y + 0.18*math.cos(rotation+math.pi), 0.75)
    back.rotation_euler = (math.radians(8), 0, rotation + math.pi)
    back.data.materials.append(mat_seat)
    
    # 椅子支柱
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.3)
    pillar = bpy.context.active_object
    pillar.name = f"Chair_Pillar_{index}"
    pillar.location = (chair_x, chair_y, 0.3)
    pillar.data.materials.append(mat_metal)
    
    # 五星腳
    for i in range(5):
        angle = rotation + math.pi + i * (2 * math.pi / 5)
        lx = chair_x + math.cos(angle) * 0.22
        ly = chair_y + math.sin(angle) * 0.22
        
        bpy.ops.mesh.primitive_cube_add(size=1)
        arm = bpy.context.active_object
        arm.name = f"Chair_Arm_{index}_{i+1}"
        arm.scale = (0.24, 0.03, 0.02)
        arm.location = (chair_x + math.cos(angle) * 0.11, chair_y + math.sin(angle) * 0.11, 0.08)
        arm.rotation_euler = (0, 0, angle)
        arm.data.materials.append(mat_metal)
        
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.02)
        wheel = bpy.context.active_object
        wheel.name = f"Wheel_{index}_{i+1}"
        wheel.location = (lx, ly, 0.02)
        wheel.data.materials.append(mat_plastic)

# ========== 真實佈局 ==========

# 左側工作區（3 個工作站，面向右牆窗戶）
create_workstation(-4, -3, rotation=0, index=1)
create_workstation(-4, 0, rotation=0, index=2)
create_workstation(-4, 3, rotation=0, index=3)

# 右側工作區（2 個工作站，面向左）
create_workstation(4, -1.5, rotation=math.pi, index=4)
create_workstation(4, 1.5, rotation=math.pi, index=5)

# ========== 會議室（左後角，玻璃隔間）==========

MEETING_X, MEETING_Y = -3.5, -3.5
MEETING_W, MEETING_D = 3, 3

# 玻璃隔間（三面）
# 前牆（有入口）
bpy.ops.mesh.primitive_cube_add(size=1)
glass_front = bpy.context.active_object
glass_front.name = "Glass_Front"
glass_front.scale = (MEETING_W/2 - 0.4, 0.02, ROOM_H/2)
glass_front.location = (MEETING_X, MEETING_Y - MEETING_D/2, ROOM_H/2)
glass_front.data.materials.append(mat_glass)

# 右牆
bpy.ops.mesh.primitive_cube_add(size=1)
glass_right = bpy.context.active_object
glass_right.name = "Glass_Right"
glass_right.scale = (0.02, MEETING_D/2, ROOM_H/2)
glass_right.location = (MEETING_X + MEETING_W/2, MEETING_Y, ROOM_H/2)
glass_right.data.materials.append(mat_glass)

# 會議桌（橢圓形）
bpy.ops.mesh.primitive_cylinder_add(radius=0.7, depth=0.04)
meeting_table = bpy.context.active_object
meeting_table.name = "Meeting_Table"
meeting_table.scale = (1, 0.65, 1)
meeting_table.location = (MEETING_X, MEETING_Y, 0.75)
meeting_table.data.materials.append(mat_meeting_table)

# 會議椅（4 張）
for i in range(4):
    angle = i * (math.pi / 2) + math.pi/4
    cx = MEETING_X + math.cos(angle) * 0.9
    cy = MEETING_Y + math.sin(angle) * 0.6
    
    bpy.ops.mesh.primitive_cube_add(size=1)
    chair = bpy.context.active_object
    chair.name = f"Meeting_Chair_{i+1}"
    chair.scale = (0.32, 0.32, 0.06)
    chair.location = (cx, cy, 0.48)
    chair.rotation_euler = (0, 0, angle + math.pi)
    chair.data.materials.append(mat_seat)

# 白板
bpy.ops.mesh.primitive_cube_add(size=1)
whiteboard = bpy.context.active_object
whiteboard.name = "Whiteboard"
whiteboard.scale = (0.02, 0.9, 0.6)
whiteboard.location = (-ROOM_W/2 + 0.1, MEETING_Y, 1.3)
whiteboard.data.materials.append(mat_whiteboard)

# ========== 休息區（右後角）==========

LOUNGE_X, LOUNGE_Y = 4, -3.5

# 地毯
bpy.ops.mesh.primitive_plane_add(size=1)
carpet = bpy.context.active_object
carpet.name = "Carpet"
carpet.scale = (2, 2, 1)
carpet.location = (LOUNGE_X, LOUNGE_Y, 0.01)
carpet.data.materials.append(mat_carpet)

# L 型沙發
# 主沙發
bpy.ops.mesh.primitive_cube_add(size=1)
sofa_main = bpy.context.active_object
sofa_main.name = "Sofa_Main"
sofa_main.scale = (1.5, 0.45, 0.35)
sofa_main.location = (LOUNGE_X, LOUNGE_Y - 0.6, 0.35)
sofa_main.data.materials.append(mat_sofa)

# 沙發靠背
bpy.ops.mesh.primitive_cube_add(size=1)
sofa_back = bpy.context.active_object
sofa_back.name = "Sofa_Back"
sofa_back.scale = (1.5, 0.08, 0.28)
sofa_back.location = (LOUNGE_X, LOUNGE_Y - 0.85, 0.55)
sofa_back.data.materials.append(mat_sofa)

# 側邊沙發
bpy.ops.mesh.primitive_cube_add(size=1)
sofa_side = bpy.context.active_object
sofa_side.name = "Sofa_Side"
sofa_side.scale = (0.45, 1.2, 0.35)
sofa_side.location = (LOUNGE_X + 0.85, LOUNGE_Y, 0.35)
sofa_side.data.materials.append(mat_sofa)

# 茶几
bpy.ops.mesh.primitive_cube_add(size=1)
coffee_table = bpy.context.active_object
coffee_table.name = "Coffee_Table"
coffee_table.scale = (0.6, 0.35, 0.02)
coffee_table.location = (LOUNGE_X + 0.3, LOUNGE_Y + 0.3, 0.4)
coffee_table.data.materials.append(mat_coffee_table)

# 茶几腿
for dx, dy in [(-0.25, -0.12), (-0.25, 0.12), (0.25, -0.12), (0.25, 0.12)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.36)
    leg = bpy.context.active_object
    leg.name = "Table_Leg"
    leg.location = (LOUNGE_X + 0.3 + dx, LOUNGE_Y + 0.3 + dy, 0.2)
    leg.data.materials.append(mat_metal)

# 靠墊
for i in range(3):
    bpy.ops.mesh.primitive_cube_add(size=1)
    cushion = bpy.context.active_object
    cushion.name = f"Cushion_{i+1}"
    cushion.scale = (0.18, 0.18, 0.08)
    cushion.location = (LOUNGE_X - 0.4 + i * 0.4, LOUNGE_Y - 0.55, 0.55)
    cushion.rotation_euler = (math.radians(12), 0, 0)
    cushion.data.materials.append(mat_cushion)

# ========== 咖啡區（入口附近）==========

COFFEE_X, COFFEE_Y = 4, 3.5

# 高桌
bpy.ops.mesh.primitive_cube_add(size=1)
high_table = bpy.context.active_object
high_table.name = "High_Table"
high_table.scale = (0.5, 0.3, 0.02)
high_table.location = (COFFEE_X, COFFEE_Y, 1.0)
high_table.data.materials.append(mat_coffee_table)

# 桌子支柱
bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.95)
table_pole = bpy.context.active_object
table_pole.name = "Table_Pole"
table_pole.location = (COFFEE_X, COFFEE_Y, 0.5)
table_pole.data.materials.append(mat_metal)

# 咖啡機
bpy.ops.mesh.primitive_cube_add(size=1)
coffee_machine = bpy.context.active_object
coffee_machine.name = "Coffee_Machine"
coffee_machine.scale = (0.12, 0.18, 0.22)
coffee_machine.location = (COFFEE_X - 0.12, COFFEE_Y, 1.13)
coffee_machine.data.materials.append(mat_coffee_machine)

# 高腳椅（2 張）
for i in range(2):
    stool_y = COFFEE_Y - 0.6 - i * 0.35
    
    # 座椅
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.04)
    stool_seat = bpy.context.active_object
    stool_seat.name = f"Stool_{i+1}"
    stool_seat.location = (COFFEE_X + 0.25, stool_y, 0.72)
    stool_seat.data.materials.append(mat_plastic)
    
    # 支柱
    bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=0.66)
    stool_pole = bpy.context.active_object
    stool_pole.name = f"Stool_Pole_{i+1}"
    stool_pole.location = (COFFEE_X + 0.25, stool_y, 0.35)
    stool_pole.data.materials.append(mat_metal)

# ========== 盆栽裝飾 ==========

plant_positions = [(-5, 4), (5, -4.5), (0, 4.5)]
for i, (px, py) in enumerate(plant_positions):
    # 花盆
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.15)
    pot = bpy.context.active_object
    pot.name = f"Pot_{i+1}"
    pot.location = (px, py, 0.525)
    pot.data.materials.append(mat_plant_pot)
    
    # 植物
    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.15)
    plant = bpy.context.active_object
    plant.name = f"Plant_{i+1}"
    plant.location = (px, py, 0.7)
    plant.scale = (1, 1, 1.2)
    plant.data.materials.append(mat_plant)

print("✅ 真實辦公室場景 V7 創建完成！")
print(f"空間：{ROOM_W}m x {ROOM_D}m x {ROOM_H}m")
print("佈局：左側 3 工作站 + 右側 2 工作站 + 會議室 + 休息區 + 咖啡區")
