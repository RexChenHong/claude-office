#!/usr/bin/env python3
"""
創建完整 5 人辦公室場景（含會議室 + 休息區）
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

# 辦公室材質
mat_floor = create_material("Floor_Wood", (0.6, 0.45, 0.3, 1), roughness=0.6)
mat_wall = create_material("Wall_White", (0.95, 0.95, 0.95, 1), roughness=0.9)
mat_ceiling = create_material("Ceiling", (0.98, 0.98, 0.98, 1), roughness=0.95)
mat_glass = create_material("Glass", (0.7, 0.85, 0.95, 0.3), roughness=0.1, metallic=0.0)
mat_metal_frame = create_material("Metal_Frame", (0.3, 0.3, 0.35, 1), roughness=0.3, metallic=0.8)

# 家具材質
mat_desktop = create_material("Desktop_White", (0.92, 0.92, 0.9, 1), roughness=0.3)
mat_seat = create_material("Seat_Fabric", (0.2, 0.2, 0.25, 1), roughness=0.8)
mat_metal = create_material("Metal_Silver", (0.5, 0.5, 0.55, 1), roughness=0.2, metallic=0.9)
mat_plastic = create_material("Plastic_Black", (0.1, 0.1, 0.1, 1), roughness=0.4)
mat_screen = create_material("Screen_LCD", (0.1, 0.1, 0.12, 1), roughness=0.1, emission=(0.2, 0.25, 0.3, 1))
mat_bezel = create_material("Bezel_Black", (0.05, 0.05, 0.05, 1), roughness=0.3)
mat_keycap = create_material("Keycap_Dark", (0.15, 0.15, 0.15, 1), roughness=0.4)
mat_lamp = create_material("Lamp_White", (0.95, 0.95, 0.95, 1), roughness=0.5)
mat_lamp_light = create_material("Lamp_Light", (1.0, 0.98, 0.9, 1), roughness=0.1, emission=(1, 0.98, 0.9, 1))
mat_plant_pot = create_material("Plant_Pot", (0.6, 0.4, 0.3, 1), roughness=0.7)
mat_plant_leaf = create_material("Plant_Leaf", (0.2, 0.5, 0.2, 1), roughness=0.6)

# 會議室材質
mat_meeting_table = create_material("Meeting_Table", (0.3, 0.25, 0.2, 1), roughness=0.4)
mat_whiteboard = create_material("Whiteboard", (0.98, 0.98, 0.98, 1), roughness=0.3)
mat_chair_fabric_blue = create_material("Chair_Blue", (0.2, 0.3, 0.5, 1), roughness=0.7)

# 休息區材質
mat_sofa = create_material("Sofa_Grey", (0.4, 0.4, 0.42, 1), roughness=0.85)
mat_coffee_table = create_material("Coffee_Table", (0.35, 0.25, 0.2, 1), roughness=0.5)
mat_cushion = create_material("Cushion_Blue", (0.25, 0.35, 0.55, 1), roughness=0.8)
mat_carpet = create_material("Carpet_Grey", (0.5, 0.5, 0.52, 1), roughness=0.95)
mat_coffee_machine = create_material("Coffee_Machine", (0.15, 0.15, 0.15, 1), roughness=0.3, metallic=0.7)

# 天花板燈具
mat_ceiling_light = create_material("Ceiling_Light", (0.95, 0.95, 0.95, 1), roughness=0.5)
mat_ceiling_light_panel = create_material("Light_Panel", (0.98, 0.98, 0.95, 1), roughness=0.1, emission=(1.0, 1.0, 0.95, 1))

# ========== 辦公室主體 ==========

# 地板（20m x 20m）
bpy.ops.mesh.primitive_plane_add(size=20)
floor = bpy.context.active_object
floor.name = "Floor"
floor.location = (0, 0, 0)
floor.data.materials.append(mat_floor)

# 天花板
bpy.ops.mesh.primitive_plane_add(size=20)
ceiling = bpy.context.active_object
ceiling.name = "Ceiling"
ceiling.location = (0, 0, 2.8)
ceiling.rotation_euler = (math.pi, 0, 0)
ceiling.data.materials.append(mat_ceiling)

# 牆面
# 後牆
bpy.ops.mesh.primitive_plane_add(size=20)
back_wall = bpy.context.active_object
back_wall.name = "Back_Wall"
back_wall.scale = (1, 1, 2.8/10)
back_wall.location = (0, -10, 1.4)
back_wall.rotation_euler = (math.pi/2, 0, 0)
back_wall.data.materials.append(mat_wall)

# 左牆
bpy.ops.mesh.primitive_plane_add(size=20)
left_wall = bpy.context.active_object
left_wall.name = "Left_Wall"
left_wall.scale = (1, 1, 2.8/10)
left_wall.location = (-10, 0, 1.4)
left_wall.rotation_euler = (math.pi/2, 0, math.pi/2)
left_wall.data.materials.append(mat_wall)

# 右牆（帶落地窗）
bpy.ops.mesh.primitive_plane_add(size=20)
right_wall = bpy.context.active_object
right_wall.name = "Right_Wall"
right_wall.scale = (1, 1, 2.8/10)
right_wall.location = (10, 0, 1.4)
right_wall.rotation_euler = (math.pi/2, 0, -math.pi/2)
right_wall.data.materials.append(mat_wall)

# 落地窗（右牆中央）
bpy.ops.mesh.primitive_plane_add(size=8)
window = bpy.context.active_object
window.name = "Window_Glass"
window.scale = (1, 1, 2.5/8)
window.location = (9.95, 0, 1.3)
window.rotation_euler = (math.pi/2, 0, -math.pi/2)
window.data.materials.append(mat_glass)

# 窗框
for i in range(4):
    bpy.ops.mesh.primitive_cube_add(size=1)
    frame = bpy.context.active_object
    frame.name = f"Window_Frame_{i}"
    frame.scale = (0.05, 2, 2.5/2)
    frame.location = (9.97, -3 + i*2, 1.3)
    frame.data.materials.append(mat_metal_frame)

# ========== 天花板燈具 ==========

def create_ceiling_light(x, y, name):
    """創建天花板 LED 平板燈"""
    # 燈具外殼
    bpy.ops.mesh.primitive_cube_add(size=1)
    light_box = bpy.context.active_object
    light_box.name = f"Light_Box_{name}"
    light_box.scale = (0.6, 0.6, 0.02)
    light_box.location = (x, y, 2.75)
    light_box.data.materials.append(mat_ceiling_light)

    # 發光面板
    bpy.ops.mesh.primitive_plane_add(size=0.55)
    panel = bpy.context.active_object
    panel.name = f"Light_Panel_{name}"
    panel.location = (x, y, 2.74)
    panel.rotation_euler = (math.pi, 0, 0)
    panel.data.materials.append(mat_ceiling_light_panel)

# 燈具佈局
light_positions = [
    (-4, -4), (-4, 0), (-4, 4),
    (0, -4), (0, 0), (0, 4),
    (4, -4), (4, 0), (4, 4),
]
for i, (lx, ly) in enumerate(light_positions):
    create_ceiling_light(lx, ly, f"{i+1}")

# ========== 工作站創建函數 ==========

def create_workstation(x, y, index):
    """創建單個工作站"""

    # 創建群組
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    ws_group = bpy.context.active_object
    ws_group.name = f"Workstation_{index}"
    ws_group.location = (x, y, 0)

    # 桌面
    bpy.ops.mesh.primitive_cube_add(size=1)
    desktop = bpy.context.active_object
    desktop.name = f"Desktop_{index}"
    desktop.scale = (1.2, 0.6, 0.025)
    desktop.location = (x, y, 0.75)
    desktop.data.materials.append(mat_desktop)
    desktop.parent = ws_group

    # 桌腿
    leg_positions = [(-0.55, -0.25), (-0.55, 0.25), (0.55, -0.25), (0.55, 0.25)]
    for i, (lx, ly) in enumerate(leg_positions):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.725)
        leg = bpy.context.active_object
        leg.name = f"Leg_{index}_{i+1}"
        leg.location = (x + lx, y + ly, 0.3625)
        leg.data.materials.append(mat_metal)
        leg.parent = ws_group

    # 雙螢幕
    SCREEN_WIDTH = 0.6
    SCREEN_HEIGHT = 0.34

    for j, sx in enumerate([-0.32, 0.32]):
        bpy.ops.mesh.primitive_cube_add(size=1)
        panel = bpy.context.active_object
        panel.name = f"Screen_{index}_{j+1}"
        panel.scale = (SCREEN_WIDTH, 0.03, SCREEN_HEIGHT)
        panel.location = (x + sx, y - 0.55, 1.1)
        if j == 1:
            panel.rotation_euler = (0, 0, math.radians(10))
        panel.data.materials.append(mat_screen)
        panel.parent = ws_group

    # 支架
    bpy.ops.mesh.primitive_cube_add(size=1)
    stand = bpy.context.active_object
    stand.name = f"Monitor_Stand_{index}"
    stand.scale = (0.04, 0.04, 0.35)
    stand.location = (x, y - 0.55, 0.78)
    stand.data.materials.append(mat_metal)
    stand.parent = ws_group

    # 底座
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.01)
    base = bpy.context.active_object
    base.name = f"Monitor_Base_{index}"
    base.scale = (1, 0.8, 1)
    base.location = (x, y - 0.55, 0.52)
    base.data.materials.append(mat_metal)
    base.parent = ws_group

    # 鍵盤
    bpy.ops.mesh.primitive_cube_add(size=1)
    kb = bpy.context.active_object
    kb.name = f"Keyboard_{index}"
    kb.scale = (0.35, 0.12, 0.015)
    kb.location = (x, y - 0.25, 0.43)
    kb.data.materials.append(mat_plastic)
    kb.parent = ws_group

    # 滑鼠
    bpy.ops.mesh.primitive_cube_add(size=1)
    mouse = bpy.context.active_object
    mouse.name = f"Mouse_{index}"
    mouse.scale = (0.06, 0.11, 0.03)
    mouse.location = (x + 0.25, y - 0.25, 0.43)
    mouse.data.materials.append(mat_plastic)
    mouse.parent = ws_group

    # 辦公椅
    bpy.ops.mesh.primitive_cube_add(size=1)
    seat = bpy.context.active_object
    seat.name = f"Seat_{index}"
    seat.scale = (0.45, 0.4, 0.08)
    seat.location = (x, y + 0.6, 0.48)
    seat.data.materials.append(mat_seat)
    seat.parent = ws_group

    bpy.ops.mesh.primitive_cube_add(size=1)
    back = bpy.context.active_object
    back.name = f"Backrest_{index}"
    back.scale = (0.42, 0.06, 0.5)
    back.location = (x, y + 0.82, 0.78)
    back.rotation_euler = (math.radians(10), 0, 0)
    back.data.materials.append(mat_seat)
    back.parent = ws_group

    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.25)
    pillar = bpy.context.active_object
    pillar.name = f"Chair_Pillar_{index}"
    pillar.location = (x, y + 0.6, 0.32)
    pillar.data.materials.append(mat_metal)
    pillar.parent = ws_group

    # 五星腳
    for i in range(5):
        angle = i * (2 * math.pi / 5)
        lx = math.cos(angle) * 0.25
        ly = math.sin(angle) * 0.25

        bpy.ops.mesh.primitive_cube_add(size=1)
        arm = bpy.context.active_object
        arm.name = f"Chair_Arm_{index}_{i+1}"
        arm.scale = (0.28, 0.03, 0.02)
        arm.location = (x + lx/2, y + 0.6 + ly/2, 0.09)
        arm.rotation_euler = (0, 0, angle)
        arm.data.materials.append(mat_metal)
        arm.parent = ws_group

        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.025)
        wheel = bpy.context.active_object
        wheel.name = f"Wheel_{index}_{i+1}"
        wheel.location = (x + lx, y + 0.6 + ly, 0.025)
        wheel.data.materials.append(mat_plastic)
        wheel.parent = ws_group

    # 檯燈
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.02)
    lamp_base = bpy.context.active_object
    lamp_base.name = f"Lamp_Base_{index}"
    lamp_base.location = (x + 0.5, y - 0.2, 0.52)
    lamp_base.data.materials.append(mat_lamp)
    lamp_base.parent = ws_group

    bpy.ops.mesh.primitive_cylinder_add(radius=0.01, depth=0.35)
    lamp_arm = bpy.context.active_object
    lamp_arm.name = f"Lamp_Arm_{index}"
    lamp_arm.location = (x + 0.5, y - 0.2, 0.7)
    lamp_arm.data.materials.append(mat_metal)
    lamp_arm.parent = ws_group

    bpy.ops.mesh.primitive_cone_add(radius1=0.08, radius2=0.05, depth=0.1)
    lamp_shade = bpy.context.active_object
    lamp_shade.name = f"Lamp_Shade_{index}"
    lamp_shade.location = (x + 0.5, y - 0.2, 0.92)
    lamp_shade.rotation_euler = (math.pi, 0, 0)
    lamp_shade.data.materials.append(mat_lamp)
    lamp_shade.parent = ws_group

    # 盆栽
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.1)
    pot = bpy.context.active_object
    pot.name = f"Pot_{index}"
    pot.location = (x - 0.5, y - 0.2, 0.52)
    pot.data.materials.append(mat_plant_pot)
    pot.parent = ws_group

    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.12)
    plant = bpy.context.active_object
    plant.name = f"Plant_{index}"
    plant.location = (x - 0.5, y - 0.2, 0.65)
    plant.scale = (1, 1, 1.3)
    plant.data.materials.append(mat_plant_leaf)
    plant.parent = ws_group

    return ws_group

# ========== 會議室 ==========

def create_meeting_room():
    """創建會議室（左上角）"""
    
    # 會議室玻璃隔間
    room_x, room_y = -7, 7  # 左上角
    room_w, room_d = 4, 3   # 4m x 3m
    
    # 創建群組
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    room_group = bpy.context.active_object
    room_group.name = "Meeting_Room"
    room_group.location = (room_x, room_y, 0)
    
    # 玻璃牆（三面，第四面是建築牆）
    # 前牆（有門）
    bpy.ops.mesh.primitive_cube_add(size=1)
    glass_front = bpy.context.active_object
    glass_front.name = "Glass_Front"
    glass_front.scale = (room_w/2 - 0.5, 0.02, 2.8/2)
    glass_front.location = (room_x, room_y - room_d/2, 1.4)
    glass_front.data.materials.append(mat_glass)
    glass_front.parent = room_group
    
    # 門口部分（不封閉）
    bpy.ops.mesh.primitive_cube_add(size=1)
    glass_door_left = bpy.context.active_object
    glass_door_left.name = "Glass_Door_Left"
    glass_door_left.scale = (0.5, 0.02, 2.8/2)
    glass_door_left.location = (room_x + room_w/2 - 0.25, room_y - room_d/2, 1.4)
    glass_door_left.data.materials.append(mat_glass)
    glass_door_left.parent = room_group
    
    # 右牆
    bpy.ops.mesh.primitive_cube_add(size=1)
    glass_right = bpy.context.active_object
    glass_right.name = "Glass_Right"
    glass_right.scale = (0.02, room_d/2, 2.8/2)
    glass_right.location = (room_x + room_w/2, room_y, 1.4)
    glass_right.data.materials.append(mat_glass)
    glass_right.parent = room_group
    
    # 金屬框架
    # 垂直框架
    for fx in [room_x - room_w/2, room_x + room_w/2]:
        bpy.ops.mesh.primitive_cube_add(size=1)
        vframe = bpy.context.active_object
        vframe.name = f"Frame_V_{fx:.0f}"
        vframe.scale = (0.04, 0.04, 2.8/2)
        vframe.location = (fx, room_y - room_d/2, 1.4)
        vframe.data.materials.append(mat_metal_frame)
        vframe.parent = room_group
    
    # 水平框架（頂部）
    bpy.ops.mesh.primitive_cube_add(size=1)
    hframe = bpy.context.active_object
    hframe.name = "Frame_Top"
    hframe.scale = (room_w/2, 0.04, 0.04)
    hframe.location = (room_x, room_y - room_d/2, 2.8)
    hframe.data.materials.append(mat_metal_frame)
    hframe.parent = room_group
    
    # 橢圓形會議桌
    bpy.ops.mesh.primitive_cylinder_add(radius=0.75, depth=0.05)
    table = bpy.context.active_object
    table.name = "Meeting_Table"
    table.scale = (1, 0.7, 1)  # 橢圓形
    table.location = (room_x, room_y, 0.75)
    table.data.materials.append(mat_meeting_table)
    table.parent = room_group
    
    # 會議椅（6 張）
    for i in range(6):
        angle = i * (2 * math.pi / 6)
        cx = room_x + math.cos(angle) * 1.0
        cy = room_y + math.sin(angle) * 0.7
        
        # 座椅
        bpy.ops.mesh.primitive_cube_add(size=1)
        chair_seat = bpy.context.active_object
        chair_seat.name = f"Meeting_Chair_Seat_{i+1}"
        chair_seat.scale = (0.35, 0.35, 0.06)
        chair_seat.location = (cx, cy, 0.48)
        chair_seat.data.materials.append(mat_chair_fabric_blue)
        chair_seat.parent = room_group
        
        # 椅背
        bpy.ops.mesh.primitive_cube_add(size=1)
        chair_back = bpy.context.active_object
        chair_back.name = f"Meeting_Chair_Back_{i+1}"
        chair_back.scale = (0.35, 0.05, 0.4)
        chair_back.location = (cx, cy - 0.15, 0.72)
        chair_back.rotation_euler = (math.radians(5), 0, 0)
        chair_back.data.materials.append(mat_chair_fabric_blue)
        chair_back.parent = room_group
    
    # 白板
    bpy.ops.mesh.primitive_cube_add(size=1)
    whiteboard = bpy.context.active_object
    whiteboard.name = "Whiteboard"
    whiteboard.scale = (0.02, 1.0, 0.75)
    whiteboard.location = (room_x - room_w/2 + 0.02, room_y, 1.3)
    whiteboard.data.materials.append(mat_whiteboard)
    whiteboard.parent = room_group
    
    # 白板框架
    bpy.ops.mesh.primitive_cube_add(size=1)
    wb_frame = bpy.context.active_object
    wb_frame.name = "Whiteboard_Frame"
    wb_frame.scale = (0.03, 1.05, 0.8)
    wb_frame.location = (room_x - room_w/2 + 0.01, room_y, 1.3)
    wb_frame.data.materials.append(mat_metal_frame)
    wb_frame.parent = room_group

# ========== 休息區 ==========

def create_lounge_area():
    """創建休息區（右下角）"""
    
    lounge_x, lounge_y = 6, -6  # 右下角
    
    # 創建群組
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    lounge_group = bpy.context.active_object
    lounge_group.name = "Lounge_Area"
    lounge_group.location = (lounge_x, lounge_y, 0)
    
    # 地毯
    bpy.ops.mesh.primitive_plane_add(size=4)
    carpet = bpy.context.active_object
    carpet.name = "Carpet"
    carpet.location = (lounge_x, lounge_y, 0.01)
    carpet.data.materials.append(mat_carpet)
    carpet.parent = lounge_group
    
    # L型沙發
    # 主沙發（長邊）
    bpy.ops.mesh.primitive_cube_add(size=1)
    sofa_main = bpy.context.active_object
    sofa_main.name = "Sofa_Main"
    sofa_main.scale = (0.8, 0.4, 0.35)
    sofa_main.location = (lounge_x, lounge_y - 0.8, 0.35)
    sofa_main.data.materials.append(mat_sofa)
    sofa_main.parent = lounge_group
    
    # 沙發靠背
    bpy.ops.mesh.primitive_cube_add(size=1)
    sofa_back = bpy.context.active_object
    sofa_back.name = "Sofa_Back"
    sofa_back.scale = (0.8, 0.08, 0.3)
    sofa_back.location = (lounge_x, lounge_y - 1.0, 0.55)
    sofa_back.data.materials.append(mat_sofa)
    sofa_back.parent = lounge_group
    
    # 沙發短邊（L型）
    bpy.ops.mesh.primitive_cube_add(size=1)
    sofa_side = bpy.context.active_object
    sofa_side.name = "Sofa_Side"
    sofa_side.scale = (0.4, 0.8, 0.35)
    sofa_side.location = (lounge_x - 0.6, lounge_y, 0.35)
    sofa_side.data.materials.append(mat_sofa)
    sofa_side.parent = lounge_group
    
    # 沙發短邊靠背
    bpy.ops.mesh.primitive_cube_add(size=1)
    sofa_side_back = bpy.context.active_object
    sofa_side_back.name = "Sofa_Side_Back"
    sofa_side_back.scale = (0.08, 0.8, 0.3)
    sofa_side_back.location = (lounge_x - 0.82, lounge_y, 0.55)
    sofa_side_back.data.materials.append(mat_sofa)
    sofa_side_back.parent = lounge_group
    
    # 靠墊
    for i in range(3):
        bpy.ops.mesh.primitive_cube_add(size=1)
        cushion = bpy.context.active_object
        cushion.name = f"Cushion_{i+1}"
        cushion.scale = (0.2, 0.2, 0.08)
        cushion.location = (lounge_x - 0.3 + i * 0.3, lounge_y - 0.7, 0.55)
        cushion.rotation_euler = (math.radians(15), 0, 0)
        cushion.data.materials.append(mat_cushion)
        cushion.parent = lounge_group
    
    # 茶几
    bpy.ops.mesh.primitive_cube_add(size=1)
    coffee_table = bpy.context.active_object
    coffee_table.name = "Coffee_Table"
    coffee_table.scale = (0.5, 0.35, 0.02)
    coffee_table.location = (lounge_x, lounge_y + 0.2, 0.4)
    coffee_table.data.materials.append(mat_coffee_table)
    coffee_table.parent = lounge_group
    
    # 茶几腿
    for lx, ly in [(-0.2, -0.12), (-0.2, 0.12), (0.2, -0.12), (0.2, 0.12)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.38)
        table_leg = bpy.context.active_object
        table_leg.name = f"Table_Leg_{lx:.0f}_{ly:.0f}"
        table_leg.location = (lounge_x + lx, lounge_y + 0.2 + ly, 0.2)
        table_leg.data.materials.append(mat_metal)
        table_leg.parent = lounge_group

# ========== 咖啡區 ==========

def create_coffee_area():
    """創建咖啡區（右下角，休息區旁）"""
    
    coffee_x, coffee_y = 6, -3  # 休息區上方
    
    # 創建群組
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    coffee_group = bpy.context.active_object
    coffee_group.name = "Coffee_Area"
    coffee_group.location = (coffee_x, coffee_y, 0)
    
    # 咖啡桌
    bpy.ops.mesh.primitive_cube_add(size=1)
    coffee_table = bpy.context.active_object
    coffee_table.name = "Coffee_Table"
    coffee_table.scale = (0.6, 0.3, 0.03)
    coffee_table.location = (coffee_x, coffee_y, 1.0)
    coffee_table.data.materials.append(mat_coffee_table)
    coffee_table.parent = coffee_group
    
    # 桌子支架
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.95)
    table_support = bpy.context.active_object
    table_support.name = "Coffee_Table_Support"
    table_support.location = (coffee_x, coffee_y, 0.5)
    table_support.data.materials.append(mat_metal)
    table_support.parent = coffee_group
    
    # 底座
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.02)
    table_base = bpy.context.active_object
    table_base.name = "Coffee_Table_Base"
    table_base.location = (coffee_x, coffee_y, 0.02)
    table_base.data.materials.append(mat_metal)
    table_base.parent = coffee_group
    
    # 咖啡機
    bpy.ops.mesh.primitive_cube_add(size=1)
    machine = bpy.context.active_object
    machine.name = "Coffee_Machine"
    machine.scale = (0.15, 0.2, 0.25)
    machine.location = (coffee_x - 0.15, coffee_y, 1.15)
    machine.data.materials.append(mat_coffee_machine)
    machine.parent = coffee_group
    
    # 高腳椅（2 張）
    for i in range(2):
        cy = coffee_y - 0.6 - i * 0.4
        
        # 座椅
        bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.05)
        stool_seat = bpy.context.active_object
        stool_seat.name = f"Stool_Seat_{i+1}"
        stool_seat.location = (coffee_x + 0.3, cy, 0.75)
        stool_seat.data.materials.append(mat_plastic)
        stool_seat.parent = coffee_group
        
        # 椅子支柱
        bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.7)
        stool_pillar = bpy.context.active_object
        stool_pillar.name = f"Stool_Pillar_{i+1}"
        stool_pillar.location = (coffee_x + 0.3, cy, 0.37)
        stool_pillar.data.materials.append(mat_metal)
        stool_pillar.parent = coffee_group
        
        # 底座
        bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.02)
        stool_base = bpy.context.active_object
        stool_base.name = f"Stool_Base_{i+1}"
        stool_base.location = (coffee_x + 0.3, cy, 0.02)
        stool_base.data.materials.append(mat_metal)
        stool_base.parent = coffee_group

# ========== 創建所有元素 ==========

# 創建 5 個工作站
for i in range(5):
    x = -6 + i * 3  # 間距 3m
    y = 0
    create_workstation(x, y, i + 1)

# 創建會議室
create_meeting_room()

# 創建休息區
create_lounge_area()

# 創建咖啡區
create_coffee_area()

print("✅ 完整辦公室場景創建完成！")
print("包含：")
print("  - 地板、牆面、天花板、落地窗")
print("  - 9 個天花板 LED 燈")
print("  - 5 個工作站（桌子、椅子、雙螢幕、鍵盤、檯燈、盆栽）")
print("  - 會議室（玻璃隔間、橢圓桌、6 椅、白板）")
print("  - 休息區（L 型沙發、茶几、地毯、靠墊）")
print("  - 咖啡區（高桌、咖啡機、2 高腳椅）")
