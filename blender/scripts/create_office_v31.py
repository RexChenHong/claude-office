#!/usr/bin/env python3
"""V32 - 修正牆壁尺寸
- 牆壁 scale 使用完整尺寸（不是一半）
- cube size=1 → scale 直接等於實際尺寸
"""
import bpy
import math
import sys

sys.path.insert(0, '/home/rex/.local/lib/python3.10/site-packages')

# ========== 材質定義 ==========
def create_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat

mat_floor = create_material("Floor", (0.15, 0.10, 0.08, 1), roughness=0.9)
mat_wall = create_material("Wall", (0.92, 0.92, 0.90, 1), roughness=0.95)
mat_desktop = create_material("Desktop", (0.95, 0.95, 0.93, 1), roughness=0.6)
mat_metal = create_material("Metal", (0.2, 0.2, 0.2, 1), roughness=0.3, metallic=0.8)
mat_screen = create_material("Screen", (0.05, 0.05, 0.05, 1), roughness=0.1, metallic=0.5)
mat_plastic = create_material("Plastic", (0.3, 0.3, 0.3, 1), roughness=0.4)
mat_seat = create_material("Seat", (0.25, 0.25, 0.28, 1), roughness=0.8)
mat_coffee_cup = create_material("CoffeeCup", (1.0, 1.0, 1.0, 1), roughness=0.3)
mat_coffee = create_material("Coffee", (0.15, 0.08, 0.05, 1), roughness=0.2)
mat_book_blue = create_material("BookBlue", (0.1, 0.2, 0.6, 1), roughness=0.7)
mat_book_red = create_material("BookRed", (0.7, 0.15, 0.1, 1), roughness=0.7)
mat_pen_holder = create_material("PenHolder", (0.2, 0.15, 0.1, 1), roughness=0.5)
mat_pen = create_material("Pen", (0.1, 0.1, 0.1, 1), roughness=0.3, metallic=0.3)
mat_paper = create_material("Paper", (0.95, 0.95, 0.92, 1), roughness=0.9)
mat_plant = create_material("Plant", (0.15, 0.4, 0.15, 1), roughness=0.8)
mat_pot = create_material("Pot", (0.6, 0.4, 0.3, 1), roughness=0.7)
mat_frame = create_material("Frame", (0.3, 0.25, 0.2, 1), roughness=0.4)
mat_art = create_material("Art", (0.8, 0.7, 0.5, 1), roughness=0.5)

def add_bevel(obj, segments=3, width=0.02):
    bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel.segments = segments
    bevel.width = width
    bevel.limit_method = 'ANGLE'

# ========== 尺寸定義（1.2倍微幅放大）==========
DESK_WIDTH = 1.4
DESK_DEPTH = 0.75
DESK_THICK = 0.03
DESK_HEIGHT = 0.75
MONITOR_WIDTH = 0.55
MONITOR_DEPTH = 0.03
MONITOR_HEIGHT = 0.32
MONITOR_STAND_HEIGHT = 0.12
KEYBOARD_WIDTH = 0.54
KEYBOARD_DEPTH = 0.18
KEYBOARD_HEIGHT = 0.024
MOUSE_WIDTH = 0.072
MOUSE_DEPTH = 0.144
MOUSE_HEIGHT = 0.042
CUP_RADIUS = 0.042
CUP_HEIGHT = 0.108
BOOK_WIDTH = 0.252
BOOK_DEPTH = 0.18
BOOK_HEIGHT = 0.03
PENHOLDER_RADIUS = 0.042
PENHOLDER_HEIGHT = 0.12

# ========== 創建桌面物件函數 ==========
def create_keyboard(x, y, z, rot=0):
    bpy.ops.mesh.primitive_cube_add(size=1)
    kb = bpy.context.active_object
    kb.scale = (KEYBOARD_WIDTH, KEYBOARD_DEPTH, KEYBOARD_HEIGHT)
    kb.location = (x, y, z)
    kb.rotation_euler = (0, 0, rot)
    kb.data.materials.append(mat_plastic)
    add_bevel(kb, segments=3, width=0.006)
    kb.name = "Keyboard"
    
    for row in range(4):
        for col in range(12):
            kx = x + (col - 5.5) * 0.038
            ky = y + (row - 1.5) * 0.03
            kz = z + KEYBOARD_HEIGHT + 0.008
            rx = x + (kx - x) * math.cos(rot) - (ky - y) * math.sin(rot)
            ry = y + (kx - x) * math.sin(rot) + (ky - y) * math.cos(rot)
            bpy.ops.mesh.primitive_cube_add(size=1)
            key = bpy.context.active_object
            key.scale = (0.016, 0.016, 0.007)
            key.location = (rx, ry, kz)
            key.rotation_euler = (0, 0, rot)
            key.data.materials.append(mat_metal)

def create_mouse(x, y, z, rot=0):
    bpy.ops.mesh.primitive_cube_add(size=1)
    mouse = bpy.context.active_object
    mouse.scale = (MOUSE_WIDTH, MOUSE_DEPTH, MOUSE_HEIGHT)
    mouse.location = (x, y, z)
    mouse.rotation_euler = (0, 0, rot)
    mouse.data.materials.append(mat_metal)
    add_bevel(mouse, segments=4, width=0.01)
    mouse.name = "Mouse"
    
    mx = x - 0.02 * math.sin(rot)
    my = y + 0.02 * math.cos(rot)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.006, depth=0.018)
    wheel = bpy.context.active_object
    wheel.location = (mx, my, z + MOUSE_HEIGHT)
    wheel.rotation_euler = (math.pi/2, 0, rot)
    wheel.data.materials.append(mat_metal)

def create_coffee_cup(x, y, z):
    bpy.ops.mesh.primitive_cylinder_add(radius=CUP_RADIUS, depth=CUP_HEIGHT)
    cup = bpy.context.active_object
    cup.location = (x, y, z + CUP_HEIGHT/2)
    cup.data.materials.append(mat_coffee_cup)
    add_bevel(cup, segments=3, width=0.003)
    cup.name = "CoffeeCup"
    
    bpy.ops.mesh.primitive_cylinder_add(radius=CUP_RADIUS * 0.9, depth=0.012)
    coffee = bpy.context.active_object
    coffee.location = (x, y, z + CUP_HEIGHT * 0.85)
    coffee.data.materials.append(mat_coffee)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.005, depth=CUP_HEIGHT * 0.6)
    handle = bpy.context.active_object
    handle.location = (x + CUP_RADIUS + 0.012, y, z + CUP_HEIGHT * 0.5)
    handle.rotation_euler = (0, 0, math.pi/2)
    handle.data.materials.append(mat_coffee_cup)

def create_book_stack(x, y, z, count=3):
    colors = [mat_book_blue, mat_book_red, mat_book_blue]
    for i in range(count):
        angle = (i * 0.08) - 0.08
        bpy.ops.mesh.primitive_cube_add(size=1)
        book = bpy.context.active_object
        book.scale = (BOOK_WIDTH, BOOK_DEPTH, BOOK_HEIGHT)
        book.location = (x, y, z + BOOK_HEIGHT/2 + i * BOOK_HEIGHT)
        book.rotation_euler = (0, 0, angle)
        book.data.materials.append(colors[i % len(colors)])
        add_bevel(book, segments=2, width=0.0025)
        book.name = f"Book_{i}"

def create_pen_holder(x, y, z):
    bpy.ops.mesh.primitive_cylinder_add(radius=PENHOLDER_RADIUS, depth=PENHOLDER_HEIGHT)
    holder = bpy.context.active_object
    holder.location = (x, y, z + PENHOLDER_HEIGHT/2)
    holder.data.materials.append(mat_pen_holder)
    add_bevel(holder, segments=3, width=0.003)
    holder.name = "PenHolder"
    
    for i in range(4):
        angle = i * math.pi / 2 + 0.3
        bpy.ops.mesh.primitive_cylinder_add(radius=0.005, depth=0.168)
        pen = bpy.context.active_object
        px = x + math.cos(angle) * 0.018
        py = y + math.sin(angle) * 0.018
        pen.location = (px, py, z + PENHOLDER_HEIGHT + 0.036)
        pen.rotation_euler = (0.15 + i * 0.05, 0, angle)
        pen.data.materials.append(mat_pen)

def create_papers(x, y, z, count=5):
    for i in range(count):
        bpy.ops.mesh.primitive_cube_add(size=1)
        paper = bpy.context.active_object
        paper.scale = (0.252, 0.356, 0.0024)
        offset_x = i * 0.0036
        offset_y = i * 0.0024
        offset_rot = i * 0.03
        paper.location = (x + offset_x, y + offset_y, z + 0.003 + i * 0.003)
        paper.rotation_euler = (0, 0, offset_rot)
        paper.data.materials.append(mat_paper)
        paper.name = f"Paper_{i}"

def create_plant(x, y, z):
    """盆栽 - z 是地面高度"""
    bpy.ops.mesh.primitive_cylinder_add(radius=0.096, depth=0.144)
    pot = bpy.context.active_object
    pot.location = (x, y, z + 0.072)
    pot.data.materials.append(mat_pot)
    add_bevel(pot, segments=3, width=0.006)
    pot.name = "PlantPot"
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.144)
    plant = bpy.context.active_object
    plant.location = (x, y, z + 0.216)
    plant.data.materials.append(mat_plant)
    plant.name = "Plant"

def create_wall_art(x, y, z, width=0.6, height=0.4):
    w = width * 1.2
    h = height * 1.2
    bpy.ops.mesh.primitive_cube_add(size=1)
    frame = bpy.context.active_object
    frame.scale = (w + 0.036, 0.024, h + 0.036)
    frame.location = (x, y, z)
    frame.data.materials.append(mat_frame)
    frame.name = "ArtFrame"
    
    bpy.ops.mesh.primitive_cube_add(size=1)
    art = bpy.context.active_object
    art.scale = (w, 0.018, h)
    art.location = (x, y - 0.012, z)
    art.data.materials.append(mat_art)
    art.name = "ArtCanvas"

def create_clock(x, y, z, radius=0.12):
    r = radius * 1.2
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=0.024)
    clock = bpy.context.active_object
    clock.location = (x, y, z)
    clock.rotation_euler = (math.pi/2, 0, 0)
    clock.data.materials.append(mat_metal)
    clock.name = "Clock"
    
    for angle, length in [(0, r * 0.67), (math.pi/2, r * 0.42)]:
        bpy.ops.mesh.primitive_cube_add(size=1)
        hand = bpy.context.active_object
        hand.scale = (length, 0.01, 0.006)
        hx = x + length/2 * math.cos(angle)
        hz = z + length/2 * math.sin(angle)
        hand.location = (hx, y - 0.018, hz)
        hand.rotation_euler = (0, 0, -angle)
        hand.data.materials.append(mat_screen)

# ========== 創建工作站 ==========
def create_workstation(x, y, facing='north', index=1):
    rotations = {'north': 0, 'east': math.pi/2, 'south': math.pi, 'west': -math.pi/2}
    rot = rotations.get(facing, 0)
    
    # 桌面
    bpy.ops.mesh.primitive_cube_add(size=1)
    desk = bpy.context.active_object
    desk.scale = (DESK_WIDTH, DESK_DEPTH, DESK_THICK)
    desk.location = (x, y, DESK_HEIGHT)
    desk.rotation_euler = (0, 0, rot)
    desk.data.materials.append(mat_desktop)
    add_bevel(desk, segments=5, width=0.025)
    desk.name = f"Desk_{index}"
    
    desktop_top = DESK_HEIGHT + DESK_THICK/2
    
    # 桌腳
    for dx, dy in [(-0.55, -0.25), (-0.55, 0.25), (0.55, -0.25), (0.55, 0.25)]:
        bx = x + dx * math.cos(rot) - dy * math.sin(rot)
        by = y + dx * math.sin(rot) + dy * math.cos(rot)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.72)
        leg = bpy.context.active_object
        leg.location = (bx, by, 0.36)
        leg.data.materials.append(mat_metal)
    
    # 螢幕
    monitor_offset = DESK_DEPTH/2 - 0.15
    for sx in [-0.35, 0.35]:
        mx = x + sx * math.cos(rot) + monitor_offset * math.sin(rot)
        my = y + sx * math.sin(rot) - monitor_offset * math.cos(rot)
        
        bpy.ops.mesh.primitive_cube_add(size=1)
        monitor = bpy.context.active_object
        monitor.scale = (MONITOR_WIDTH, MONITOR_DEPTH, MONITOR_HEIGHT)
        monitor.location = (mx, my, desktop_top + MONITOR_STAND_HEIGHT + MONITOR_HEIGHT/2)
        monitor.rotation_euler = (0, 0, rot + math.pi)
        monitor.data.materials.append(mat_screen)
        add_bevel(monitor, segments=2, width=0.005)
        monitor.name = f"Monitor_{index}_{sx}"
        
        bpy.ops.mesh.primitive_cube_add(size=1)
        stand = bpy.context.active_object
        stand.scale = (0.03, 0.08, MONITOR_STAND_HEIGHT)
        stand.location = (mx, my, desktop_top + MONITOR_STAND_HEIGHT/2)
        stand.rotation_euler = (0, 0, rot)
        stand.data.materials.append(mat_metal)
    
    # 鍵盤
    kb_offset = -DESK_DEPTH/2 + 0.15
    kx = x + kb_offset * math.sin(rot)
    ky = y - kb_offset * math.cos(rot)
    kb_z = desktop_top + KEYBOARD_HEIGHT/2
    create_keyboard(kx, ky, kb_z, rot)
    
    # 滑鼠
    mouse_offset_x = 0.18 * math.cos(rot)
    mouse_offset_y = 0.18 * math.sin(rot)
    mx_pos = kx + mouse_offset_x
    my_pos = ky + mouse_offset_y
    mouse_z = desktop_top + MOUSE_HEIGHT/2
    create_mouse(mx_pos, my_pos, mouse_z, rot)
    
    # 咖啡杯
    cup_dx = DESK_WIDTH/2 - 0.25
    cup_dy = -DESK_DEPTH/2 + 0.15
    cup_x = x + cup_dx * math.cos(rot) - cup_dy * math.sin(rot)
    cup_y = y + cup_dx * math.sin(rot) + cup_dy * math.cos(rot)
    create_coffee_cup(cup_x, cup_y, desktop_top)
    
    # 筆筒
    pen_dx = DESK_WIDTH/2 - 0.20
    pen_dy = DESK_DEPTH/2 - 0.15
    pen_x = x + pen_dx * math.cos(rot) - pen_dy * math.sin(rot)
    pen_y = y + pen_dx * math.sin(rot) + pen_dy * math.cos(rot)
    create_pen_holder(pen_x, pen_y, desktop_top)
    
    # 書本（偶數工作站）
    if index % 2 == 0:
        book_dx = -DESK_WIDTH/2 + 0.20
        book_dy = DESK_DEPTH/2 - 0.15
        book_x = x + book_dx * math.cos(rot) - book_dy * math.sin(rot)
        book_y = y + book_dx * math.sin(rot) + book_dy * math.cos(rot)
        create_book_stack(book_x, book_y, desktop_top, 2)
    
    # 文件堆（3的倍數工作站）
    if index % 3 == 0:
        paper_dx = -DESK_WIDTH/2 + 0.25
        paper_dy = -DESK_DEPTH/2 + 0.20
        paper_x = x + paper_dx * math.cos(rot) - paper_dy * math.sin(rot)
        paper_y = y + paper_dx * math.sin(rot) + paper_dy * math.cos(rot)
        create_papers(paper_x, paper_y, desktop_top, 3)
    
    # 椅子
    chair_offset = -DESK_DEPTH/2 - 0.35
    chair_x = x + chair_offset * math.sin(rot)
    chair_y = y - chair_offset * math.cos(rot)
    
    bpy.ops.mesh.primitive_cube_add(size=1)
    seat = bpy.context.active_object
    seat.scale = (0.45, 0.4, 0.06)
    seat.location = (chair_x, chair_y, 0.48)
    seat.rotation_euler = (0, 0, rot)
    seat.data.materials.append(mat_seat)
    add_bevel(seat, segments=5, width=0.03)
    seat.name = f"Seat_{index}"
    
    back_x = chair_x - 0.18 * math.sin(rot)
    back_y = chair_y - 0.18 * math.cos(rot)
    bpy.ops.mesh.primitive_cube_add(size=1)
    back = bpy.context.active_object
    back.scale = (0.42, 0.06, 0.45)
    back.location = (back_x, back_y, 0.78)
    back.rotation_euler = (0, 0, rot)
    back.data.materials.append(mat_seat)
    add_bevel(back, segments=3, width=0.02)

# ========== 場景佈局 ==========
ROOM_W = 16
ROOM_D = 14
WALL_H = 2.8

# 地板
bpy.ops.mesh.primitive_plane_add(size=1)
floor = bpy.context.active_object
floor.scale = (ROOM_W + 2, ROOM_D + 2, 1)
floor.data.materials.append(mat_floor)
floor.name = "Floor"

# ========== 牆壁（完整四面牆）==========
WALL_THICK = 0.08

# 南牆（入口牆，完整）
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (ROOM_W, WALL_THICK, WALL_H)
w.location = (0, -ROOM_D/2 - WALL_THICK/2, WALL_H/2)
w.data.materials.append(mat_wall)
add_bevel(w, segments=3, width=0.01)
w.name = "Wall_South"

# 北牆（完整，無缺口）
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (ROOM_W, WALL_THICK, WALL_H)
w.location = (0, ROOM_D/2 + WALL_THICK/2, WALL_H/2)
w.data.materials.append(mat_wall)
add_bevel(w, segments=3, width=0.01)
w.name = "Wall_North"

# 西牆（完整）
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (WALL_THICK, ROOM_D, WALL_H)
w.location = (-ROOM_W/2 - WALL_THICK/2, 0, WALL_H/2)
w.data.materials.append(mat_wall)
add_bevel(w, segments=3, width=0.01)
w.name = "Wall_West"

# 東牆（完整）
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (WALL_THICK, ROOM_D, WALL_H)
w.location = (ROOM_W/2 + WALL_THICK/2, 0, WALL_H/2)
w.data.materials.append(mat_wall)
add_bevel(w, segments=3, width=0.01)
w.name = "Wall_East"

# ========== 5 個工作站（調整位置，確保在牆內）==========
# 安全距離：桌子邊緣距離牆壁至少 0.5m
SAFE_MARGIN = 0.5
DESK_HALF_W = DESK_WIDTH / 2  # 0.7m
DESK_HALF_D = DESK_DEPTH / 2  # 0.375m

# 左側工作站（面向東）
left_x = -ROOM_W/2 + SAFE_MARGIN + DESK_HALF_D  # -8 + 0.5 + 0.375 = -7.125
create_workstation(-5.5, 2, facing='east', index=1)
create_workstation(-5.5, 4.5, facing='east', index=2)

# 中間工作站（面向北）
create_workstation(0, 0, facing='north', index=3)

# 右側工作站（面向西）
right_x = ROOM_W/2 - SAFE_MARGIN - DESK_HALF_D  # 8 - 0.5 - 0.375 = 7.125
create_workstation(5.5, 2, facing='west', index=4)
create_workstation(5.5, 4.5, facing='west', index=5)

# ========== 會議室 ==========
MEETING_X = 3
MEETING_Y = -4

bpy.ops.mesh.primitive_cylinder_add(radius=1.2, depth=0.03)
t = bpy.context.active_object
t.scale = (1.0, 0.65, 1)
t.location = (MEETING_X, MEETING_Y, 0.77)
t.data.materials.append(mat_desktop)
add_bevel(t, segments=8, width=0.02)

for i in range(6):
    angle = i * math.pi / 3
    cx = MEETING_X + 1.5 * math.cos(angle)
    cy = MEETING_Y + 1.0 * math.sin(angle)
    bpy.ops.mesh.primitive_cube_add(size=1)
    seat = bpy.context.active_object
    seat.scale = (0.4, 0.35, 0.06)
    seat.location = (cx, cy, 0.48)
    seat.rotation_euler = (0, 0, angle + math.pi)
    seat.data.materials.append(mat_seat)

wb_x = MEETING_X + 2.0
bpy.ops.mesh.primitive_cube_add(size=1)
wb = bpy.context.active_object
wb.scale = (0.02, 0.8, 0.5)
wb.location = (wb_x, MEETING_Y, 1.5)
wb.data.materials.append(mat_screen)

# ========== 休息區 ==========
LOUNGE_X = -4
LOUNGE_Y = -4

bpy.ops.mesh.primitive_cube_add(size=1)
sofa1 = bpy.context.active_object
sofa1.scale = (0.6, 1.8, 0.35)
sofa1.location = (LOUNGE_X, LOUNGE_Y, 0.25)
sofa1.data.materials.append(mat_seat)
add_bevel(sofa1, segments=3, width=0.03)

bpy.ops.mesh.primitive_cube_add(size=1)
sofa2 = bpy.context.active_object
sofa2.scale = (1.6, 0.6, 0.35)
sofa2.location = (LOUNGE_X + 0.5, LOUNGE_Y - 1.2, 0.25)
sofa2.data.materials.append(mat_seat)
add_bevel(sofa2, segments=3, width=0.03)

bpy.ops.mesh.primitive_cube_add(size=1)
table = bpy.context.active_object
table.scale = (0.8, 0.4, 0.03)
table.location = (LOUNGE_X + 0.5, LOUNGE_Y - 0.3, 0.35)
table.data.materials.append(mat_desktop)
add_bevel(table, segments=3, width=0.015)

create_coffee_cup(LOUNGE_X + 0.3, LOUNGE_Y - 0.3, 0.38)

# ========== 咖啡區 ==========
COFFEE_X = -2
COFFEE_Y = -5

bpy.ops.mesh.primitive_cube_add(size=1)
ct = bpy.context.active_object
ct.scale = (0.8, 0.4, 0.03)
ct.location = (COFFEE_X, COFFEE_Y, 0.9)
ct.data.materials.append(mat_desktop)
add_bevel(ct, segments=3, width=0.015)

bpy.ops.mesh.primitive_cube_add(size=1)
cm = bpy.context.active_object
cm.scale = (0.15, 0.2, 0.3)
cm.location = (COFFEE_X + 0.2, COFFEE_Y, 1.05)
cm.data.materials.append(mat_metal)
add_bevel(cm, segments=2, width=0.005)

for dx in [-0.35, 0.35]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.75)
    stool = bpy.context.active_object
    stool.location = (COFFEE_X + dx, COFFEE_Y - 0.4, 0.45)
    stool.data.materials.append(mat_metal)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.03)
    top = bpy.context.active_object
    top.location = (COFFEE_X + dx, COFFEE_Y - 0.4, 0.85)
    top.data.materials.append(mat_seat)

# ========== 盆栽（確保在地面）==========
create_plant(-7, -5, 0)
create_plant(7, -5, 0)
create_plant(-7, 6, 0)
create_plant(7, 6, 0)

# ========== 牆上掛畫 ==========
create_wall_art(MEETING_X + 2.5, MEETING_Y, 1.6, width=0.8, height=0.5)

# ========== 時鐘 ==========
create_clock(0, -ROOM_D/2 - 0.04, 2.2, radius=0.15)

# ========== 額外掛畫 ==========
create_wall_art(-ROOM_W/2 - 0.04, 2, 1.8, width=0.6, height=0.4)
create_wall_art(ROOM_W/2 + 0.04, 2, 1.8, width=0.6, height=0.4)

print("V32 場景創建完成！")

# 導出
export_path = '/mnt/e_drive/claude-office/blender/exports/office_v32.glb'
bpy.ops.export_scene.gltf(filepath=export_path, export_format='GLB')
print(f'已導出: {export_path}')
