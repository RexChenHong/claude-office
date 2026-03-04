"""
Claude Office V28 - 修正尺寸比例與座標關聯性
- 使用真實尺寸（公尺單位）
- 物件相對於桌面的正確位置
- 添加更多細節布景
"""
import bpy
import math

# 清除場景
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

# 基礎材質
mat_floor = create_material("Floor", (0.15, 0.10, 0.08, 1), roughness=0.9)
mat_wall = create_material("Wall", (0.92, 0.92, 0.90, 1), roughness=0.95)
mat_desktop = create_material("Desktop", (0.95, 0.95, 0.93, 1), roughness=0.6)
mat_metal = create_material("Metal", (0.2, 0.2, 0.2, 1), roughness=0.3, metallic=0.8)
mat_screen = create_material("Screen", (0.05, 0.05, 0.05, 1), roughness=0.1, metallic=0.5)
mat_plastic = create_material("Plastic", (0.3, 0.3, 0.3, 1), roughness=0.4)
mat_seat = create_material("Seat", (0.25, 0.25, 0.28, 1), roughness=0.8)

# 桌面物件材質
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

# ========== Bevel 函數 ==========
def add_bevel(obj, segments=3, width=0.02):
    bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel.segments = segments
    bevel.width = width
    bevel.limit_method = 'ANGLE'

# ========== 尺寸定義（3倍放大，保持相對比例）==========
# 桌子
DESK_WIDTH = 1.4    # 桌寬
DESK_DEPTH = 0.75   # 桌深
DESK_THICK = 0.03   # 桌面厚度
DESK_HEIGHT = 0.75  # 桌高（桌面中心）

# 螢幕
MONITOR_WIDTH = 0.55
MONITOR_DEPTH = 0.03
MONITOR_HEIGHT = 0.32
MONITOR_STAND_HEIGHT = 0.12

# 鍵盤（3倍放大）
KEYBOARD_WIDTH = 1.35    # 0.45 * 3
KEYBOARD_DEPTH = 0.45    # 0.15 * 3
KEYBOARD_HEIGHT = 0.06   # 0.02 * 3

# 滑鼠（3倍放大）
MOUSE_WIDTH = 0.18       # 0.06 * 3
MOUSE_DEPTH = 0.36       # 0.12 * 3
MOUSE_HEIGHT = 0.105     # 0.035 * 3

# 咖啡杯（3倍放大）
CUP_RADIUS = 0.105       # 0.035 * 3
CUP_HEIGHT = 0.27        # 0.09 * 3

# 書本（3倍放大）
BOOK_WIDTH = 0.63        # 0.21 * 3
BOOK_DEPTH = 0.45        # 0.15 * 3
BOOK_HEIGHT = 0.075      # 0.025 * 3

# 筆筒（3倍放大）
PENHOLDER_RADIUS = 0.105  # 0.035 * 3
PENHOLDER_HEIGHT = 0.30   # 0.10 * 3

# ========== 創建桌面物件函數 ==========

def create_keyboard(x, y, z, rot=0):
    """創建鍵盤（3倍放大）"""
    # 底座
    bpy.ops.mesh.primitive_cube_add(size=1)
    kb = bpy.context.active_object
    kb.scale = (KEYBOARD_WIDTH, KEYBOARD_DEPTH, KEYBOARD_HEIGHT)
    kb.location = (x, y, z)
    kb.rotation_euler = (0, 0, rot)
    kb.data.materials.append(mat_plastic)
    add_bevel(kb, segments=3, width=0.015)
    kb.name = "Keyboard"
    
    # 按鍵（簡化版，只做外框）
    for row in range(4):
        for col in range(12):
            kx = x + (col - 5.5) * 0.10
            ky = y + (row - 1.5) * 0.08
            kz = z + KEYBOARD_HEIGHT + 0.02
            
            rx = x + (kx - x) * math.cos(rot) - (ky - y) * math.sin(rot)
            ry = y + (kx - x) * math.sin(rot) + (ky - y) * math.cos(rot)
            
            bpy.ops.mesh.primitive_cube_add(size=1)
            key = bpy.context.active_object
            key.scale = (0.04, 0.04, 0.018)
            key.location = (rx, ry, kz)
            key.rotation_euler = (0, 0, rot)
            key.data.materials.append(mat_metal)

def create_mouse(x, y, z, rot=0):
    """創建滑鼠（3倍放大）"""
    bpy.ops.mesh.primitive_cube_add(size=1)
    mouse = bpy.context.active_object
    mouse.scale = (MOUSE_WIDTH, MOUSE_DEPTH, MOUSE_HEIGHT)
    mouse.location = (x, y, z)
    mouse.rotation_euler = (0, 0, rot)
    mouse.data.materials.append(mat_metal)
    add_bevel(mouse, segments=4, width=0.025)
    mouse.name = "Mouse"
    
    # 滾輪
    mx = x - 0.05 * math.sin(rot)
    my = y + 0.05 * math.cos(rot)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.045)
    wheel = bpy.context.active_object
    wheel.location = (mx, my, z + MOUSE_HEIGHT)
    wheel.rotation_euler = (math.pi/2, 0, rot)
    wheel.data.materials.append(mat_metal)

def create_coffee_cup(x, y, z):
    """創建咖啡杯（3倍放大）"""
    # 杯身
    bpy.ops.mesh.primitive_cylinder_add(radius=CUP_RADIUS, depth=CUP_HEIGHT)
    cup = bpy.context.active_object
    cup.location = (x, y, z + CUP_HEIGHT/2)
    cup.data.materials.append(mat_coffee_cup)
    add_bevel(cup, segments=3, width=0.008)
    cup.name = "CoffeeCup"
    
    # 咖啡液面
    bpy.ops.mesh.primitive_cylinder_add(radius=CUP_RADIUS * 0.9, depth=0.03)
    coffee = bpy.context.active_object
    coffee.location = (x, y, z + CUP_HEIGHT * 0.85)
    coffee.data.materials.append(mat_coffee)
    
    # 杯柄
    bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=CUP_HEIGHT * 0.6)
    handle = bpy.context.active_object
    handle.location = (x + CUP_RADIUS + 0.03, y, z + CUP_HEIGHT * 0.5)
    handle.rotation_euler = (0, 0, math.pi/2)
    handle.data.materials.append(mat_coffee_cup)

def create_book_stack(x, y, z, count=3):
    """創建書本堆疊（3倍放大）"""
    colors = [mat_book_blue, mat_book_red, mat_book_blue]
    for i in range(count):
        angle = (i * 0.08) - 0.08
        bpy.ops.mesh.primitive_cube_add(size=1)
        book = bpy.context.active_object
        book.scale = (BOOK_WIDTH, BOOK_DEPTH, BOOK_HEIGHT)
        book.location = (x, y, z + BOOK_HEIGHT/2 + i * BOOK_HEIGHT)
        book.rotation_euler = (0, 0, angle)
        book.data.materials.append(colors[i % len(colors)])
        add_bevel(book, segments=2, width=0.006)
        book.name = f"Book_{i}"

def create_pen_holder(x, y, z):
    """創建筆筒（3倍放大）"""
    # 筒身
    bpy.ops.mesh.primitive_cylinder_add(radius=PENHOLDER_RADIUS, depth=PENHOLDER_HEIGHT)
    holder = bpy.context.active_object
    holder.location = (x, y, z + PENHOLDER_HEIGHT/2)
    holder.data.materials.append(mat_pen_holder)
    add_bevel(holder, segments=3, width=0.008)
    holder.name = "PenHolder"
    
    # 筆
    for i in range(4):
        angle = i * math.pi / 2 + 0.3
        bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.42)
        pen = bpy.context.active_object
        px = x + math.cos(angle) * 0.045
        py = y + math.sin(angle) * 0.045
        pen.location = (px, py, z + PENHOLDER_HEIGHT + 0.09)
        pen.rotation_euler = (0.15 + i * 0.05, 0, angle)
        pen.data.materials.append(mat_pen)

def create_papers(x, y, z, count=5):
    """創建文件堆（3倍放大）"""
    for i in range(count):
        bpy.ops.mesh.primitive_cube_add(size=1)
        paper = bpy.context.active_object
        paper.scale = (0.63, 0.89, 0.006)  # A4 * 3
        offset_x = i * 0.009
        offset_y = i * 0.006
        offset_rot = i * 0.03
        paper.location = (x + offset_x, y + offset_y, z + 0.003 + i * 0.0075)
        paper.rotation_euler = (0, 0, offset_rot)
        paper.data.materials.append(mat_paper)
        paper.name = f"Paper_{i}"

def create_plant(x, y, z):
    """創建盆栽（3倍放大）"""
    # 花盆
    bpy.ops.mesh.primitive_cylinder_add(radius=0.24, depth=0.36)
    pot = bpy.context.active_object
    pot.location = (x, y, z + 0.18)
    pot.data.materials.append(mat_pot)
    add_bevel(pot, segments=3, width=0.015)
    pot.name = "PlantPot"
    
    # 植物（用 UV Sphere 代替）
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.36)
    plant = bpy.context.active_object
    plant.location = (x, y, z + 0.54)
    plant.data.materials.append(mat_plant)
    plant.name = "Plant"

def create_wall_art(x, y, z, width=0.6, height=0.4):
    """創建牆上掛畫（3倍放大）"""
    w = width * 3
    h = height * 3
    # 畫框
    bpy.ops.mesh.primitive_cube_add(size=1)
    frame = bpy.context.active_object
    frame.scale = (w + 0.09, 0.06, h + 0.09)
    frame.location = (x, y, z)
    frame.data.materials.append(mat_frame)
    frame.name = "ArtFrame"
    
    # 畫布
    bpy.ops.mesh.primitive_cube_add(size=1)
    art = bpy.context.active_object
    art.scale = (w, 0.045, h)
    art.location = (x, y - 0.03, z)
    art.data.materials.append(mat_art)
    art.name = "ArtCanvas"

def create_clock(x, y, z, radius=0.12):
    """創建時鐘（3倍放大）"""
    r = radius * 3
    # 鐘面
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=0.06)
    clock = bpy.context.active_object
    clock.location = (x, y, z)
    clock.rotation_euler = (math.pi/2, 0, 0)
    clock.data.materials.append(mat_metal)
    clock.name = "Clock"
    
    # 指針（簡化）
    for angle, length in [(0, r * 0.67), (math.pi/2, r * 0.42)]:
        bpy.ops.mesh.primitive_cube_add(size=1)
        hand = bpy.context.active_object
        hand.scale = (length, 0.024, 0.015)
        hx = x + length/2 * math.cos(angle)
        hz = z + length/2 * math.sin(angle)
        hand.location = (hx, y - 0.045, hz)
        hand.rotation_euler = (0, 0, -angle)
        hand.data.materials.append(mat_screen)

# ========== 創建工作站（修正座標關聯性）==========

def create_workstation(x, y, facing='north', index=1):
    """創建工作站 - 所有物件座標相對於桌子中心"""
    
    # 計算旋轉角度
    rotations = {'north': 0, 'east': math.pi/2, 'south': math.pi, 'west': -math.pi/2}
    rot = rotations.get(facing, 0)
    
    # ========== 桌面 ==========
    bpy.ops.mesh.primitive_cube_add(size=1)
    desk = bpy.context.active_object
    desk.scale = (DESK_WIDTH, DESK_DEPTH, DESK_THICK)
    desk.location = (x, y, DESK_HEIGHT)
    desk.rotation_euler = (0, 0, rot)
    desk.data.materials.append(mat_desktop)
    add_bevel(desk, segments=5, width=0.025)
    desk.name = f"Desk_{index}"
    
    # 桌面頂面高度
    desktop_top = DESK_HEIGHT + DESK_THICK/2
    
    # 桌腳
    for dx, dy in [(-0.55, -0.25), (-0.55, 0.25), (0.55, -0.25), (0.55, 0.25)]:
        bx = x + dx * math.cos(rot) - dy * math.sin(rot)
        by = y + dx * math.sin(rot) + dy * math.cos(rot)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=DESK_HEIGHT * 2 - DESK_THICK)
        leg = bpy.context.active_object
        leg.location = (bx, by, (DESK_HEIGHT - DESK_THICK/2)/2)
        leg.data.materials.append(mat_metal)
    
    # ========== 螢幕（雙螢幕）==========
    # 螢幕位置：桌子後方 0.2m
    monitor_offset = DESK_DEPTH/2 - 0.15
    
    for sx in [-0.35, 0.35]:  # 雙螢幕間距
        mx = x + sx * math.cos(rot) + monitor_offset * math.sin(rot)
        my = y + sx * math.sin(rot) - monitor_offset * math.cos(rot)
        
        # 螢幕
        bpy.ops.mesh.primitive_cube_add(size=1)
        monitor = bpy.context.active_object
        monitor.scale = (MONITOR_WIDTH, MONITOR_DEPTH, MONITOR_HEIGHT)
        monitor.location = (mx, my, desktop_top + MONITOR_STAND_HEIGHT + MONITOR_HEIGHT/2)
        monitor.rotation_euler = (0, 0, rot + math.pi)
        monitor.data.materials.append(mat_screen)
        add_bevel(monitor, segments=2, width=0.005)
        monitor.name = f"Monitor_{index}_{sx}"
        
        # 螢幕支架
        bpy.ops.mesh.primitive_cube_add(size=1)
        stand = bpy.context.active_object
        stand.scale = (0.03, 0.08, MONITOR_STAND_HEIGHT)
        stand.location = (mx, my, desktop_top + MONITOR_STAND_HEIGHT/2)
        stand.rotation_euler = (0, 0, rot)
        stand.data.materials.append(mat_metal)
    
    # ========== 鍵盤位置 ==========
    # 鍵盤在螢幕前方，距離 0.3m
    kb_offset = -0.3  # 相對於桌子中心向使用者方向
    kx = x + kb_offset * math.sin(rot)
    ky = y - kb_offset * math.cos(rot)
    kb_z = desktop_top + KEYBOARD_HEIGHT/2
    create_keyboard(kx, ky, kb_z, rot)
    
    # ========== 滑鼠位置 ==========
    # 滑鼠在鍵盤右側 0.18m
    mouse_offset_x = 0.18 * math.cos(rot)
    mouse_offset_y = 0.18 * math.sin(rot)
    mx = kx + mouse_offset_x
    my = ky + mouse_offset_y
    mouse_z = desktop_top + MOUSE_HEIGHT/2
    create_mouse(mx, my, mouse_z, rot)
    
    # ========== 桌面物件（角落位置）==========
    # 咖啡杯：右前方角落
    cup_dx = 0.45
    cup_dy = -0.25
    cup_x = x + cup_dx * math.cos(rot) - cup_dy * math.sin(rot)
    cup_y = y + cup_dx * math.sin(rot) + cup_dy * math.cos(rot)
    create_coffee_cup(cup_x, cup_y, desktop_top)
    
    # 筆筒：右後方角落
    pen_dx = 0.50
    pen_dy = 0.25
    pen_x = x + pen_dx * math.cos(rot) - pen_dy * math.sin(rot)
    pen_y = y + pen_dx * math.sin(rot) + pen_dy * math.cos(rot)
    create_pen_holder(pen_x, pen_y, desktop_top)
    
    # 書本：左後方角落（部分桌面）
    if index % 2 == 0:
        book_dx = -0.50
        book_dy = 0.25
        book_x = x + book_dx * math.cos(rot) - book_dy * math.sin(rot)
        book_y = y + book_dx * math.sin(rot) + book_dy * math.cos(rot)
        create_book_stack(book_x, book_y, desktop_top, 2)
    
    # 文件堆：左前方（部分桌面）
    if index % 3 == 0:
        paper_dx = -0.45
        paper_dy = -0.20
        paper_x = x + paper_dx * math.cos(rot) - paper_dy * math.sin(rot)
        paper_y = y + paper_dx * math.sin(rot) + paper_dy * math.cos(rot)
        create_papers(paper_x, paper_y, desktop_top, 3)
    
    # ========== 椅子 ==========
    chair_offset = -0.7  # 椅子距離桌子
    chair_x = x + chair_offset * math.sin(rot)
    chair_y = y - chair_offset * math.cos(rot)
    
    # 椅座
    bpy.ops.mesh.primitive_cube_add(size=1)
    seat = bpy.context.active_object
    seat.scale = (0.45, 0.4, 0.06)
    seat.location = (chair_x, chair_y, 0.48)
    seat.rotation_euler = (0, 0, rot)
    seat.data.materials.append(mat_seat)
    add_bevel(seat, segments=5, width=0.03)
    seat.name = f"Seat_{index}"
    
    # 椅背
    back_x = chair_x - 0.18 * math.sin(rot)
    back_y = chair_y - 0.18 * math.cos(rot)
    bpy.ops.mesh.primitive_cube_add(size=1)
    back = bpy.context.active_object
    back.scale = (0.42, 0.06, 0.45)
    back.location = (back_x, back_y, 0.78)
    back.rotation_euler = (0, 0, rot)
    back.data.materials.append(mat_seat)
    add_bevel(back, segments=3, width=0.02)

# ========== 房間尺寸 ==========
ROOM_W = 16
ROOM_D = 14
WALL_H = 2.8

# ========== 創建場景 ==========

# 地板
bpy.ops.mesh.primitive_plane_add(size=1)
floor = bpy.context.active_object
floor.scale = (ROOM_W + 2, ROOM_D + 2, 1)
floor.data.materials.append(mat_floor)
floor.name = "Floor"

# 牆壁
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (ROOM_W/2 + 0.15, 0.08, WALL_H/2)
w.location = (0, -ROOM_D/2 - 0.04, WALL_H/2)
w.data.materials.append(mat_wall)
add_bevel(w, segments=3, width=0.01)

bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (ROOM_W/2 - 1.2, 0.08, WALL_H/2)
w.location = (-ROOM_W/4 - 0.6, ROOM_D/2 + 0.04, WALL_H/2)
w.data.materials.append(mat_wall)
add_bevel(w, segments=3, width=0.01)

bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.08, ROOM_D/2, WALL_H/2)
w.location = (-ROOM_W/2 - 0.04, 0, WALL_H/2)
w.data.materials.append(mat_wall)
add_bevel(w, segments=3, width=0.01)

bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.08, ROOM_D/2, WALL_H/2)
w.location = (ROOM_W/2 + 0.04, 0, WALL_H/2)
w.data.materials.append(mat_wall)
add_bevel(w, segments=3, width=0.01)

# ========== 5 個工作站 ==========
create_workstation(-5.5, 2, facing='east', index=1)
create_workstation(-5.5, 4.5, facing='east', index=2)
create_workstation(-1, 0, facing='north', index=3)
create_workstation(5.5, 2, facing='west', index=4)
create_workstation(5.5, 4.5, facing='west', index=5)

# ========== 會議室 ==========
MEETING_X = 3
MEETING_Y = -3.5

# 橢圓桌
bpy.ops.mesh.primitive_cylinder_add(radius=1.2, depth=0.03)
t = bpy.context.active_object
t.scale = (1.0, 0.65, 1)
t.location = (MEETING_X, MEETING_Y, 0.77)
t.data.materials.append(mat_desktop)
add_bevel(t, segments=8, width=0.02)

# 會議椅
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

# 白板
wb_x = MEETING_X + 2.0
bpy.ops.mesh.primitive_cube_add(size=1)
wb = bpy.context.active_object
wb.scale = (0.02, 0.8, 0.5)
wb.location = (wb_x, MEETING_Y, 1.5)
wb.data.materials.append(mat_screen)

# ========== 休息區 ==========
LOUNGE_X = -4
LOUNGE_Y = -4

# L型沙發
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

# 茶几
bpy.ops.mesh.primitive_cube_add(size=1)
table = bpy.context.active_object
table.scale = (0.8, 0.4, 0.03)
table.location = (LOUNGE_X + 0.5, LOUNGE_Y - 0.3, 0.35)
table.data.materials.append(mat_desktop)
add_bevel(table, segments=3, width=0.015)

# 休息區咖啡杯
create_coffee_cup(LOUNGE_X + 0.3, LOUNGE_Y - 0.3, 0.38)

# ========== 咖啡區 ==========
COFFEE_X = -2
COFFEE_Y = -5

# 高桌
bpy.ops.mesh.primitive_cube_add(size=1)
ct = bpy.context.active_object
ct.scale = (0.8, 0.4, 0.03)
ct.location = (COFFEE_X, COFFEE_Y, 0.9)
ct.data.materials.append(mat_desktop)
add_bevel(ct, segments=3, width=0.015)

# 咖啡機
bpy.ops.mesh.primitive_cube_add(size=1)
cm = bpy.context.active_object
cm.scale = (0.15, 0.2, 0.3)
cm.location = (COFFEE_X + 0.2, COFFEE_Y, 1.05)
cm.data.materials.append(mat_metal)
add_bevel(cm, segments=2, width=0.005)

# 高腳椅
for dx in [-0.35, 0.35]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.75)
    stool = bpy.context.active_object
    stool.location = (COFFEE_X + dx, COFFEE_Y - 0.4, 0.45)
    stool.data.materials.append(mat_metal)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.03)
    top = bpy.context.active_object
    top.location = (COFFEE_X + dx, COFFEE_Y - 0.4, 0.85)
    top.data.materials.append(mat_seat)

# ========== 新增細節布景 ==========

# 盆栽（角落裝飾）
create_plant(-7, -5, 0)
create_plant(7, -5, 0)
create_plant(-7, 6, 0)
create_plant(7, 6, 0)

# 牆上掛畫（會議室）
create_wall_art(MEETING_X + 2.5, MEETING_Y, 1.6, width=0.8, height=0.5)

# 時鐘（入口處）
create_clock(0, -6.9, 2.2, radius=0.15)

# 額外掛畫
create_wall_art(-7.9, 2, 1.8, width=0.6, height=0.4)
create_wall_art(7.9, 2, 1.8, width=0.6, height=0.4)

print("V28 場景創建完成！")
