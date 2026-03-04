#!/usr/bin/env python3
"""V63 - 最終整合版
- V53 桌椅：鎖定版（椅子面向桌子）
- V60 牆壁位置：長牆 y=3，短牆從 y=3 到 y=7
- V61 鐵柱門框：從地板到牆頂，U字形
"""
import bpy
import math
import sys

sys.path.insert(0, '/home/rex/.local/lib/python3.10/site-packages')

# 清空場景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# ========== 材質定義 ==========
def create_material(name, color, roughness=0.5, metallic=0.0, emission=None):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission:
        bsdf.inputs["Emission"].default_value = emission
        bsdf.inputs["Emission Strength"].default_value = 0.5
    return mat

# 桌子材質
mat_desktop = create_material("Desktop_White", (0.95, 0.95, 0.93, 1), roughness=0.4)
mat_frame = create_material("DeskFrame", (0.3, 0.3, 0.32, 1), roughness=0.2, metallic=0.9)
mat_leg = create_material("DeskLeg", (0.6, 0.6, 0.62, 1), roughness=0.3, metallic=0.8)

# 椅子材質
mat_seat_mesh = create_material("SeatMesh", (0.15, 0.15, 0.17, 1), roughness=0.7, metallic=0.0)
mat_seat_cushion = create_material("SeatCushion", (0.2, 0.2, 0.22, 1), roughness=0.85, metallic=0.0)
mat_chrome = create_material("Chrome", (0.8, 0.8, 0.82, 1), roughness=0.05, metallic=0.95)
mat_plastic = create_material("ChairPlastic", (0.1, 0.1, 0.1, 1), roughness=0.4, metallic=0.0)
mat_back_black = create_material("BackBlack", (0.08, 0.08, 0.08, 1), roughness=0.6, metallic=0.0)
mat_armrest = create_material("Armrest", (0.1, 0.1, 0.1, 1), roughness=0.5, metallic=0.0)

# 地板材質
mat_floor = create_material("Floor", (0.15, 0.10, 0.08, 1), roughness=0.9)

# 螢幕材質
mat_screen_frame = create_material("ScreenFrame", (0.08, 0.08, 0.08, 1), roughness=0.15, metallic=0.7)
mat_screen_display = create_material("ScreenDisplay", (0.02, 0.02, 0.03, 1), roughness=0.05, emission=(0.15, 0.18, 0.22, 1))
mat_screen_stand = create_material("ScreenStand", (0.15, 0.15, 0.15, 1), roughness=0.2, metallic=0.85)

# 鍵盤材質
mat_keyboard = create_material("Keyboard", (0.12, 0.12, 0.12, 1), roughness=0.35, metallic=0.0)
mat_keys = create_material("Keys", (0.2, 0.2, 0.2, 1), roughness=0.25, metallic=0.0)

# 杯子材質
mat_cup = create_material("Cup", (0.95, 0.93, 0.90, 1), roughness=0.1, metallic=0.0)
mat_coffee = create_material("Coffee", (0.02, 0.015, 0.01, 1), roughness=0.08, metallic=0.1)

# 牆壁材質 - 玻璃
mat_glass = create_material("Glass", (0.7, 0.85, 0.9, 1.0), roughness=0.05, metallic=0.0)

# 鐵柱材質 - 深灰色金屬
mat_iron = create_material("Iron", (0.25, 0.25, 0.27, 1.0), roughness=0.3, metallic=0.9)

# 門框材質 - 棕色木紋
mat_door_frame = create_material("DoorFrame", (0.4, 0.25, 0.15, 1.0), roughness=0.6, metallic=0.0)

def add_bevel(obj, segments=3, width=0.02):
    bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel.segments = segments
    bevel.width = width
    bevel.limit_method = 'ANGLE'

# ========== 椅子（V53 鎖定版）==========
def create_chair(x, y, rot=0, index=""):
    parts = []
    for i in range(5):
        angle = i * 2 * math.pi / 5
        dx = math.cos(angle)
        dy = math.sin(angle)
        for j in range(5):
            t = j / 4.0
            px = 0.04 + t * 0.18
            py = 0
            bpy.ops.mesh.primitive_cube_add(size=1)
            leg_seg = bpy.context.active_object
            leg_seg.scale = (0.04, 0.02, 0.025)
            leg_seg.location = (px * dx, px * dy, 0.025)
            leg_seg.data.materials.append(mat_chrome)
            parts.append(leg_seg)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.022)
        wheel = bpy.context.active_object
        wheel.location = (0.22 * dx, 0.22 * dy, 0.022)
        wheel.data.materials.append(mat_plastic)
        parts.append(wheel)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.015)
    base_disc = bpy.context.active_object
    base_disc.location = (0, 0, 0.022)
    base_disc.data.materials.append(mat_chrome)
    parts.append(base_disc)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.022, depth=0.28)
    gas_lift = bpy.context.active_object
    gas_lift.location = (0, 0, 0.16)
    gas_lift.data.materials.append(mat_chrome)
    parts.append(gas_lift)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.02)
    seat_plate = bpy.context.active_object
    seat_plate.location = (0, 0, 0.31)
    seat_plate.data.materials.append(mat_plastic)
    parts.append(seat_plate)

    bpy.ops.mesh.primitive_cube_add(size=1)
    seat = bpy.context.active_object
    seat.scale = (0.38, 0.36, 0.07)
    seat.location = (0, 0.02, 0.37)
    seat.data.materials.append(mat_seat_cushion)
    add_bevel(seat, segments=4, width=0.04)
    parts.append(seat)

    for sx in [-0.15, 0.15]:
        bpy.ops.mesh.primitive_cube_add(size=1)
        back_frame = bpy.context.active_object
        back_frame.scale = (0.015, 0.015, 0.42)
        back_frame.location = (sx, -0.20, 0.62)
        back_frame.data.materials.append(mat_chrome)
        parts.append(back_frame)

    bpy.ops.mesh.primitive_cube_add(size=1)
    top_bar = bpy.context.active_object
    top_bar.scale = (0.32, 0.015, 0.015)
    top_bar.location = (0, -0.20, 0.84)
    top_bar.data.materials.append(mat_chrome)
    parts.append(top_bar)

    bpy.ops.mesh.primitive_cube_add(size=1)
    back = bpy.context.active_object
    back.scale = (0.30, 0.035, 0.38)
    back.location = (0, -0.21, 0.63)
    back.data.materials.append(mat_back_black)
    add_bevel(back, segments=3, width=0.02)
    parts.append(back)

    bpy.ops.mesh.primitive_cube_add(size=1)
    lumbar = bpy.context.active_object
    lumbar.scale = (0.24, 0.04, 0.07)
    lumbar.location = (0, -0.18, 0.47)
    lumbar.data.materials.append(mat_back_black)
    add_bevel(lumbar, segments=3, width=0.02)
    parts.append(lumbar)

    for sx in [-0.24, 0.24]:
        bpy.ops.mesh.primitive_cube_add(size=1)
        arm_post = bpy.context.active_object
        arm_post.scale = (0.015, 0.015, 0.12)
        arm_post.location = (sx, 0.05, 0.42)
        arm_post.data.materials.append(mat_chrome)
        parts.append(arm_post)
        bpy.ops.mesh.primitive_cube_add(size=1)
        arm_pad = bpy.context.active_object
        arm_pad.scale = (0.04, 0.14, 0.018)
        arm_pad.location = (sx, 0.05, 0.50)
        arm_pad.data.materials.append(mat_armrest)
        add_bevel(arm_pad, segments=2, width=0.01)
        parts.append(arm_pad)

    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    merged = bpy.context.active_object
    merged.location = (x, y, 0.025)
    merged.rotation_euler = (0, 0, rot)

# ========== 螢幕 ==========
DESKTOP_Z = 0.775

def create_monitor(parent, local_x, local_y):
    bpy.ops.mesh.primitive_cube_add(size=1)
    frame = bpy.context.active_object
    frame.scale = (0.55, 0.02, 0.45)
    frame.location = (local_x, local_y, DESKTOP_Z + 0.25)
    frame.data.materials.append(mat_screen_frame)
    add_bevel(frame, segments=2, width=0.003)
    frame.parent = parent

    bpy.ops.mesh.primitive_cube_add(size=1)
    display = bpy.context.active_object
    display.scale = (0.52, 0.01, 0.42)
    display.location = (local_x, local_y + 0.015, DESKTOP_Z + 0.25)
    display.data.materials.append(mat_screen_display)
    display.parent = parent

    bpy.ops.mesh.primitive_cube_add(size=1)
    stand_pole = bpy.context.active_object
    stand_pole.scale = (0.03, 0.02, 0.08)
    stand_pole.location = (local_x, local_y, DESKTOP_Z + 0.045)
    stand_pole.data.materials.append(mat_screen_stand)
    stand_pole.parent = parent

    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.01)
    stand_base = bpy.context.active_object
    stand_base.location = (local_x, local_y, DESKTOP_Z + 0.005)
    stand_base.data.materials.append(mat_screen_stand)
    stand_base.parent = parent

# ========== 鍵盤 ==========
def create_keyboard(parent, local_x, local_y):
    bpy.ops.mesh.primitive_cube_add(size=1)
    kb_body = bpy.context.active_object
    kb_body.scale = (0.45, 0.18, 0.025)
    kb_body.location = (local_x, local_y, DESKTOP_Z + 0.0125)
    kb_body.data.materials.append(mat_keyboard)
    add_bevel(kb_body, segments=2, width=0.005)
    kb_body.parent = parent

    for row in range(5):
        row_y = local_y - 0.065 + row * 0.032
        for col in range(14):
            key_x = local_x - 0.185 + col * 0.0285
            bpy.ops.mesh.primitive_cube_add(size=1)
            key = bpy.context.active_object
            key.scale = (0.016, 0.013, 0.012)
            key.location = (key_x, row_y, DESKTOP_Z + 0.031)
            key.data.materials.append(mat_keys)
            add_bevel(key, segments=1, width=0.002)
            key.parent = parent

# ========== 杯子 ==========
def create_cup(parent, local_x, local_y):
    outer_r = 0.05
    cup_h = 0.10
    bpy.ops.mesh.primitive_cylinder_add(radius=outer_r, depth=cup_h)
    cup_body = bpy.context.active_object
    cup_body.location = (local_x, local_y, DESKTOP_Z + cup_h/2)
    cup_body.data.materials.append(mat_cup)
    cup_body.parent = parent

    coffee_r = outer_r - 0.004
    coffee_h = 0.004
    coffee_z = DESKTOP_Z + cup_h + coffee_h/2
    bpy.ops.mesh.primitive_cylinder_add(radius=coffee_r, depth=coffee_h)
    coffee = bpy.context.active_object
    coffee.location = (local_x, local_y, coffee_z)
    coffee.data.materials.append(mat_coffee)
    coffee.parent = parent

    bpy.ops.mesh.primitive_torus_add(major_radius=0.035, minor_radius=0.012)
    handle = bpy.context.active_object
    handle.location = (local_x + 0.06, local_y, DESKTOP_Z + 0.055)
    handle.rotation_euler = (0, math.pi/2, 0)
    handle.data.materials.append(mat_cup)
    handle.parent = parent

# ========== 桌子 ==========
def create_desk(x, y, rot=0, index=1):
    desk_parent = bpy.data.objects.new(f"Desk_{index}_Parent", None)
    bpy.context.collection.objects.link(desk_parent)
    desk_parent.location = (x, y, 0)
    desk_parent.rotation_euler = (0, 0, rot)
    
    bpy.ops.mesh.primitive_cube_add(size=1)
    desktop = bpy.context.active_object
    desktop.scale = (1.4, 0.75, 0.025)
    desktop.location = (0, 0, 0.7625)
    desktop.data.materials.append(mat_desktop)
    add_bevel(desktop, segments=4, width=0.01)
    desktop.parent = desk_parent
    
    frame_h, frame_t = 0.05, 0.03
    for side, (sx, sy, sw, sd) in [
        ('front', (0, 0.375 - frame_t/2, 1.4, frame_t)),
        ('back', (0, -0.375 + frame_t/2, 1.4, frame_t)),
        ('left', (-0.7 + frame_t/2, 0, frame_t, 0.75 - frame_t*2)),
        ('right', (0.7 - frame_t/2, 0, frame_t, 0.75 - frame_t*2)),
    ]:
        bpy.ops.mesh.primitive_cube_add(size=1)
        frame = bpy.context.active_object
        frame.scale = (sw, sd, frame_h)
        frame.location = (sx, sy, 0.735)
        frame.data.materials.append(mat_frame)
        frame.parent = desk_parent
    
    for dx, dy in [(-0.6, -0.3), (0.6, -0.3), (-0.6, 0.3), (0.6, 0.3)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.71)
        leg = bpy.context.active_object
        leg.location = (dx, dy, 0.355)
        leg.data.materials.append(mat_leg)
        add_bevel(leg, segments=2, width=0.005)
        leg.parent = desk_parent
        
        bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.02)
        base = bpy.context.active_object
        base.location = (dx, dy, 0.01)
        base.data.materials.append(mat_frame)
        base.parent = desk_parent
    
    create_monitor(desk_parent, -0.25, -0.28)
    create_monitor(desk_parent, 0.25, -0.28)
    create_keyboard(desk_parent, 0, 0.25)
    create_cup(desk_parent, 0.55, 0.15)

# ========== 地板 ==========
bpy.ops.mesh.primitive_plane_add(size=1)
floor = bpy.context.active_object
floor.scale = (16, 14, 1)
floor.data.materials.append(mat_floor)

# ========== 玻璃牆壁（長牆 y=3，短牆 y=3 到 y=7）==========
wall_height = 3.0
wall_thick = 0.3
door_height = 2.2
door_width = 1.2
long_wall_y = 3.0
doors = [-5.5, 0, 5.5]

# 長牆（y=3，避開門洞）
long_wall_segments = [
    (-8.0, -6.1),   # 西段左
    (-4.9, -0.6),   # 西段右 + 中段左
    (0.6, 4.9),     # 中段右 + 東段左
    (6.1, 8.0),     # 東段右
]

for x1, x2 in long_wall_segments:
    bpy.ops.mesh.primitive_cube_add(size=2)
    w = bpy.context.active_object
    # size=2 意味著邊長為 2（從 -1 到 1），scale 需要除以 2
    w.scale = ((x2-x1)/2, wall_thick/2, wall_height/2)
    w.location = ((x1+x2)/2, long_wall_y, wall_height/2)
    w.data.materials.append(mat_glass)

# 門洞上方的牆
for door_x in doors:
    bpy.ops.mesh.primitive_cube_add(size=2)
    w = bpy.context.active_object
    w.scale = (door_width/2, wall_thick/2, (wall_height-door_height)/2)
    w.location = (door_x, long_wall_y, door_height + (wall_height-door_height)/2)
    w.data.materials.append(mat_glass)

# 短牆（從 y=3 到 y=7，與長牆連接）
for x_pos in [-2.5, 2.5]:
    bpy.ops.mesh.primitive_cube_add(size=2)
    sw = bpy.context.active_object
    # 短牆從長牆北邊開始（y = 3 + wall_thick/2）到 y=7
    # 長度 = 7 - (3 + wall_thick/2) = 4 - wall_thick/2 = 3.85
    sw.scale = (wall_thick/2, 1.925, wall_height/2)  # 長度 3.85 米
    sw.location = (x_pos, 5.075, wall_height/2)  # y = (3.15 + 7) / 2 = 5.075
    sw.data.materials.append(mat_glass)

# ========== 鐵柱（從地板到牆頂）==========
pillar_radius = 0.05

# 交接處鐵柱
pillar_positions = [
    (-2.5, 3.0),   # 西短牆與長牆
    (2.5, 3.0),    # 東短牆與長牆
    (-2.5, 7.0),   # 西短牆頂端
    (2.5, 7.0),    # 東短牆頂端
    (-8.0, 3.0),   # 長牆西端
    (8.0, 3.0),    # 長牆東端
]

for px, py in pillar_positions:
    bpy.ops.mesh.primitive_cylinder_add(radius=pillar_radius, depth=wall_height)
    pillar = bpy.context.active_object
    pillar.location = (px, py, wall_height/2)  # 從地板 z=0 到牆頂 z=3
    pillar.data.materials.append(mat_iron)

# ========== 門框（U 字形相連，包覆牆壁）==========
frame_thick = 0.06

for door_x in doors:
    # 左邊框（從地板到門頂，包含上框厚度）
    bpy.ops.mesh.primitive_cube_add(size=2)
    left_frame = bpy.context.active_object
    left_frame.scale = (frame_thick/2, wall_thick/2 + frame_thick/2, (door_height + frame_thick)/2)
    left_frame.location = (door_x - door_width/2 - frame_thick/2, long_wall_y, (door_height + frame_thick)/2)
    left_frame.data.materials.append(mat_door_frame)

    # 右邊框（從地板到門頂，包含上框厚度）
    bpy.ops.mesh.primitive_cube_add(size=2)
    right_frame = bpy.context.active_object
    right_frame.scale = (frame_thick/2, wall_thick/2 + frame_thick/2, (door_height + frame_thick)/2)
    right_frame.location = (door_x + door_width/2 + frame_thick/2, long_wall_y, (door_height + frame_thick)/2)
    right_frame.data.materials.append(mat_door_frame)

    # 上框（連接左右，在門頂位置）
    bpy.ops.mesh.primitive_cube_add(size=2)
    top_frame = bpy.context.active_object
    top_frame.scale = ((door_width + frame_thick*2)/2, wall_thick/2 + frame_thick/2, frame_thick/2)
    top_frame.location = (door_x, long_wall_y, door_height + frame_thick/2)
    top_frame.data.materials.append(mat_door_frame)

# ========== 5 張工作站（左右排列，避開門）==========
chair_offset = 0.875

# 西區：兩個工作站左右排列（避開門 x=-5.5）
create_desk(-6.5, 5.5, rot=0, index=1)
create_chair(-6.5, 5.5 + chair_offset, rot=math.pi, index="_WS1")

create_desk(-4.5, 5.5, rot=0, index=2)
create_chair(-4.5, 5.5 + chair_offset, rot=math.pi, index="_WS2")

# 中區：一個工作站
create_desk(0, 5.5, rot=0, index=3)
create_chair(0, 5.5 + chair_offset, rot=math.pi, index="_WS3")

# 東區：兩個工作站左右排列（避開門 x=5.5）
create_desk(4.5, 5.5, rot=0, index=4)
create_chair(4.5, 5.5 + chair_offset, rot=math.pi, index="_WS4")

create_desk(6.5, 5.5, rot=0, index=5)
create_chair(6.5, 5.5 + chair_offset, rot=math.pi, index="_WS5")

# ========== 會議室牆壁（寬敞版，西面和南面貼齊地毯邊緣）==========
# 地板範圍：x: -8~8, y: -7~7
# 牆壁厚度：0.3m
# 會議室尺寸（更寬敞）
meeting_room_width = 6.0 - wall_thick   # 扣除牆壁厚度
meeting_room_depth = 6.0 - wall_thick   # 扣除牆壁厚度
meeting_room_x = -5.0      # 中心 x
meeting_room_y = -4.0      # 中心 y

# 西牆（x=-8 + wall_thick/2，在地板邊緣內側）
west_wall_x = -8.0 + wall_thick/2
bpy.ops.mesh.primitive_cube_add(size=2)
west_wall = bpy.context.active_object
west_wall.name = "MeetingRoom_West"
west_wall.scale = (wall_thick/2, meeting_room_depth/2, wall_height/2)
west_wall.location = (west_wall_x, meeting_room_y, wall_height/2)
west_wall.data.materials.append(mat_glass)

# 西牆上的液晶電視
tv_width = 2.0   # 2 米寬（大型電視）
tv_height = 1.2  # 1.2 米高
tv_depth = 0.05  # 5cm 厚度
tv_z = 1.5       # 電視中心高度 1.5m

# 電視邊框（黑色，完全不透明）
mat_tv_frame = create_material("TVFrame", (0.02, 0.02, 0.02, 1.0), roughness=0.15, metallic=0.7)
# 電視屏幕（深黑色發光，完全不透明）
mat_tv_screen = create_material("TVScreen", (0.01, 0.01, 0.01, 1.0), roughness=0.02, emission=(0.08, 0.1, 0.12, 1.0))

# 電視主體（邊框）
bpy.ops.mesh.primitive_cube_add(size=2)
tv_body = bpy.context.active_object
tv_body.name = "MeetingRoom_TV_Body"
tv_body.scale = (tv_depth/2, tv_width/2, tv_height/2)
tv_body.location = (west_wall_x - tv_depth/2 - 0.01, meeting_room_y, tv_z)
tv_body.data.materials.append(mat_tv_frame)
add_bevel(tv_body, segments=2, width=0.005)

# 電視屏幕（發光）
bpy.ops.mesh.primitive_cube_add(size=2)
tv_screen = bpy.context.active_object
tv_screen.name = "MeetingRoom_TV_Screen"
tv_screen.scale = (0.01, tv_width/2 - 0.04, tv_height/2 - 0.04)  # 比邊框小一點
tv_screen.location = (west_wall_x - tv_depth - 0.02, meeting_room_y, tv_z)
tv_screen.data.materials.append(mat_tv_screen)

# 電視支架（掛牆架）
mat_tv_bracket = create_material("TVBracket", (0.3, 0.3, 0.32, 1), roughness=0.2, metallic=0.9)
bracket_width = 0.15
bracket_height = 0.3

# 左支架
bpy.ops.mesh.primitive_cube_add(size=2)
bracket_left = bpy.context.active_object
bracket_left.name = "MeetingRoom_TV_Bracket_Left"
bracket_left.scale = (0.1, bracket_width/2, bracket_height/2)
bracket_left.location = (west_wall_x + 0.05, meeting_room_y - tv_width/4, tv_z)
bracket_left.data.materials.append(mat_tv_bracket)

# 右支架
bpy.ops.mesh.primitive_cube_add(size=2)
bracket_right = bpy.context.active_object
bracket_right.name = "MeetingRoom_TV_Bracket_Right"
bracket_right.scale = (0.1, bracket_width/2, bracket_height/2)
bracket_right.location = (west_wall_x + 0.05, meeting_room_y + tv_width/4, tv_z)
bracket_right.data.materials.append(mat_tv_bracket)

# 南牆（y=-7 + wall_thick/2，在地板邊緣內側）
south_wall_y = -7.0 + wall_thick/2
bpy.ops.mesh.primitive_cube_add(size=2)
south_wall = bpy.context.active_object
south_wall.name = "MeetingRoom_South"
south_wall.scale = (meeting_room_width/2, wall_thick/2, wall_height/2)
south_wall.location = (meeting_room_x, south_wall_y, wall_height/2)
south_wall.data.materials.append(mat_glass)

# 北牆（y=-1，延伸連接西面和東面）
north_wall_y = -1.0
bpy.ops.mesh.primitive_cube_add(size=2)
north_wall = bpy.context.active_object
north_wall.name = "MeetingRoom_North"
north_wall.scale = (meeting_room_width/2, wall_thick/2, wall_height/2)
north_wall.location = (meeting_room_x, north_wall_y, wall_height/2)
north_wall.data.materials.append(mat_glass)

# 東牆（x=-2，有門，延伸連接北面和南面）
east_wall_x = -2.0
door_width_room = 1.2  # 會議室門寬度 1.2 米

# 東牆北段（門北邊）
bpy.ops.mesh.primitive_cube_add(size=2)
east_wall_north = bpy.context.active_object
east_wall_north.name = "MeetingRoom_East_North"
east_wall_north.scale = (wall_thick/2, (meeting_room_depth/2 - door_width_room/2)/2, wall_height/2)
east_wall_north.location = (east_wall_x, meeting_room_y + meeting_room_depth/4 + door_width_room/4, wall_height/2)
east_wall_north.data.materials.append(mat_glass)

# 東牆南段（門南邊）
bpy.ops.mesh.primitive_cube_add(size=2)
east_wall_south = bpy.context.active_object
east_wall_south.name = "MeetingRoom_East_South"
east_wall_south.scale = (wall_thick/2, (meeting_room_depth/2 - door_width_room/2)/2, wall_height/2)
east_wall_south.location = (east_wall_x, meeting_room_y - meeting_room_depth/4 - door_width_room/4, wall_height/2)
east_wall_south.data.materials.append(mat_glass)

# 東牆門框上方
bpy.ops.mesh.primitive_cube_add(size=2)
east_wall_top = bpy.context.active_object
east_wall_top.name = "MeetingRoom_East_Top"
east_wall_top.scale = (wall_thick/2, door_width_room/2, (wall_height - door_height)/2)
east_wall_top.location = (east_wall_x, meeting_room_y, door_height + (wall_height - door_height)/2)
east_wall_top.data.materials.append(mat_glass)

# 會議室鐵柱（四個角落）
meeting_pillar_positions = [
    (west_wall_x, south_wall_y),   # 西南角（貼齊地毯角落）
    (west_wall_x, north_wall_y),   # 西北角
    (east_wall_x, south_wall_y),   # 東南角
    (east_wall_x, north_wall_y),   # 東北角
]

for px, py in meeting_pillar_positions:
    bpy.ops.mesh.primitive_cylinder_add(radius=pillar_radius, depth=wall_height)
    pillar = bpy.context.active_object
    pillar.name = f"MeetingRoom_Pillar_{px}_{py}"
    pillar.location = (px, py, wall_height/2)
    pillar.data.materials.append(mat_iron)

# 會議室門框（東牆，朝東）
# 左框
bpy.ops.mesh.primitive_cube_add(size=2)
left_frame_meeting = bpy.context.active_object
left_frame_meeting.name = "MeetingRoom_DoorFrame_Left"
left_frame_meeting.scale = (frame_thick/2, wall_thick/2 + frame_thick/2, (door_height + frame_thick)/2)
left_frame_meeting.location = (east_wall_x, meeting_room_y - door_width_room/2 - frame_thick/2, (door_height + frame_thick)/2)
left_frame_meeting.data.materials.append(mat_door_frame)

# 右框
bpy.ops.mesh.primitive_cube_add(size=2)
right_frame_meeting = bpy.context.active_object
right_frame_meeting.name = "MeetingRoom_DoorFrame_Right"
right_frame_meeting.scale = (frame_thick/2, wall_thick/2 + frame_thick/2, (door_height + frame_thick)/2)
right_frame_meeting.location = (east_wall_x, meeting_room_y + door_width_room/2 + frame_thick/2, (door_height + frame_thick)/2)
right_frame_meeting.data.materials.append(mat_door_frame)

# 上框
bpy.ops.mesh.primitive_cube_add(size=2)
top_frame_meeting = bpy.context.active_object
top_frame_meeting.name = "MeetingRoom_DoorFrame_Top"
top_frame_meeting.scale = (frame_thick/2, (door_width_room + frame_thick*2)/2, frame_thick/2)
top_frame_meeting.location = (east_wall_x, meeting_room_y, door_height + frame_thick/2)
top_frame_meeting.data.materials.append(mat_door_frame)

# ========== 會議桌（西南區域，橢圓桌）==========
# 材質：深色木紋桌面，高品質反光
mat_meeting_table = create_material("MeetingTable", (0.25, 0.15, 0.1, 1), roughness=0.4, metallic=0.0)
# 桌腳材質：深色金屬
mat_meeting_leg = create_material("MeetingLeg", (0.2, 0.2, 0.22, 1), roughness=0.3, metallic=0.8)

# 會議桌位置：西南區域，在地毯內部
meeting_table_x = -5.0
meeting_table_y = -4.0
meeting_table_width = 1.8  # 1.8 米長（橢圓長軸）
meeting_table_depth = 1.0  # 1 米寬（橢圓短軸）
meeting_table_height = 0.75  # 0.75 米高
meeting_table_thick = 0.08  # 桌面厚度 8cm

# 橢圓形桌面
bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=meeting_table_thick)
table_top = bpy.context.active_object
table_top.name = "MeetingTable_Top"
table_top.scale = (meeting_table_width/2, meeting_table_depth/2, 1)
table_top.location = (meeting_table_x, meeting_table_y, meeting_table_height)
table_top.data.materials.append(mat_meeting_table)

# 中心支撐柱（橢圓桌用中央支撐）
bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=meeting_table_height - meeting_table_thick/2)
center_leg = bpy.context.active_object
center_leg.name = "MeetingTable_CenterLeg"
center_leg.location = (meeting_table_x, meeting_table_y, (meeting_table_height - meeting_table_thick/2)/2)
center_leg.data.materials.append(mat_meeting_leg)

# 底座（五角星形）
bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=0.03, vertices=5)
base = bpy.context.active_object
base.name = "MeetingTable_Base"
base.location = (meeting_table_x, meeting_table_y, 0.015)
base.data.materials.append(mat_meeting_leg)

# 會議椅材質：深灰色布料，有質感
mat_meeting_seat = create_material("MeetingSeat", (0.15, 0.15, 0.17, 1), roughness=0.85, metallic=0.0)
mat_meeting_back = create_material("MeetingBack", (0.12, 0.12, 0.14, 1), roughness=0.9, metallic=0.0)
mat_meeting_frame = create_material("MeetingChairFrame", (0.7, 0.7, 0.72, 1), roughness=0.1, metallic=0.9)

chair_offset_side = 0.55  # 椅子距離桌子邊緣的距離

# 創建擬真化會議椅的函數
def create_meeting_chair(x, y, direction, index):
    """創建擬真化會議椅（椅背往後傾斜）"""
    # 座墊（有厚度和曲線）
    bpy.ops.mesh.primitive_cube_add(size=2)
    seat = bpy.context.active_object
    seat.name = f"MeetingChair_Seat_{index}"
    seat.scale = (0.36, 0.36, 0.06)
    seat.location = (x, y, 0.44)
    seat.data.materials.append(mat_meeting_seat)
    add_bevel(seat, segments=3, width=0.02)

    # 椅背（往後傾斜，不是往前）
    bpy.ops.mesh.primitive_cube_add(size=2)
    back = bpy.context.active_object
    back.name = f"MeetingChair_Back_{index}"
    back.scale = (0.34, 0.04, 0.42)
    # 往後傾斜：rotation_euler 的 x 軸旋轉為負值（往後）
    back.location = (x, y + direction * 0.36, 0.67)
    back.rotation_euler = (-0.15 * direction, 0, 0)  # 往後傾斜
    back.data.materials.append(mat_meeting_back)
    add_bevel(back, segments=3, width=0.02)

    # 椅腳框架（金屬）
    # 四個椅腳
    for dx, dy in [(-0.14, -0.14), (0.14, -0.14), (-0.14, 0.14), (0.14, 0.14)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.38)
        chair_leg = bpy.context.active_object
        chair_leg.name = f"MeetingChair_Leg_{index}_{dx}_{dy}"
        chair_leg.location = (x + dx, y + dy, 0.19)
        chair_leg.data.materials.append(mat_meeting_frame)

# 北側椅子（3 把）
for i in range(3):
    chair_x = meeting_table_x - meeting_table_width/2 + 0.5 + i * 0.65
    chair_y = meeting_table_y + meeting_table_depth/2 + chair_offset_side
    create_meeting_chair(chair_x, chair_y, 1, f"North_{i}")

# 南側椅子（3 把）
for i in range(3):
    chair_x = meeting_table_x - meeting_table_width/2 + 0.5 + i * 0.65
    chair_y = meeting_table_y - meeting_table_depth/2 - chair_offset_side
    create_meeting_chair(chair_x, chair_y, -1, f"South_{i}")

# ========== 導出 ==========
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(
    filepath='/mnt/e_drive/claude-office/blender/exports/office_v64.glb',
    export_format='GLB',
    use_selection=True
)

print("✅ V64 已導出")
print("   V63 鎖定版 + 會議桌（左邊角落）")
