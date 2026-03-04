#!/usr/bin/env python3
"""V37 - 修正溫水提出的 5 個問題
1. 移除圖中間的四方形方塊（休息區茶几改為圓形）
2. 修正會議椅分佈不均（改用統一半徑）
3. 修正玻璃貫穿會議區（移到左側外圍）
4. 白板貼到西牆上
5. 全面檢查所有物件位置
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
mat_glass = create_material("Glass", (0.85, 0.92, 0.95, 0.3), roughness=0.1, metallic=0.0)
mat_glass_frame = create_material("GlassFrame", (0.3, 0.3, 0.3, 1), roughness=0.3, metallic=0.7)
mat_desktop = create_material("Desktop", (0.95, 0.95, 0.93, 1), roughness=0.6)
mat_metal = create_material("Metal", (0.2, 0.2, 0.2, 1), roughness=0.3, metallic=0.8)
mat_screen = create_material("Screen", (0.05, 0.05, 0.05, 1), roughness=0.1, metallic=0.5)
mat_plastic = create_material("Plastic", (0.3, 0.3, 0.3, 1), roughness=0.4)
mat_seat = create_material("Seat", (0.25, 0.25, 0.28, 1), roughness=0.8)
mat_plant = create_material("Plant", (0.15, 0.45, 0.15, 1), roughness=0.8)
mat_pot = create_material("Pot", (0.6, 0.4, 0.3, 1), roughness=0.7)
mat_water_cooler = create_material("WaterCooler", (0.95, 0.95, 0.95, 1), roughness=0.3)
mat_water_blue = create_material("WaterBlue", (0.3, 0.6, 0.9, 0.8), roughness=0.1)
mat_printer = create_material("Printer", (0.2, 0.2, 0.2, 1), roughness=0.4)
mat_whiteboard = create_material("Whiteboard", (0.98, 0.98, 0.98, 1), roughness=0.2)

def add_bevel(obj, segments=3, width=0.02):
    bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel.segments = segments
    bevel.width = width
    bevel.limit_method = 'ANGLE'

# ========== 尺寸定義 ==========
DESK_WIDTH = 1.4
DESK_DEPTH = 0.75
DESK_THICK = 0.03
DESK_HEIGHT = 0.75

# ========== 辦公椅元件組 ==========
def create_office_chair(x, y, target_x=None, target_y=None, rot=None):
    """創建辦公椅元件組"""
    if rot is None and target_x is not None and target_y is not None:
        dx = target_x - x
        dy = target_y - y
        rot = math.atan2(dx, dy)
    elif rot is None:
        rot = 0
    
    base_z = 0.05
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.02)
    base = bpy.context.active_object
    base.location = (x, y, base_z)
    base.rotation_euler = (0, 0, rot)
    base.data.materials.append(mat_metal)
    base.name = "ChairBase"
    
    for i in range(5):
        angle = i * 2 * math.pi / 5 + rot
        wx = x + 0.22 * math.cos(angle)
        wy = y + 0.22 * math.sin(angle)
        
        bpy.ops.mesh.primitive_cube_add(size=1)
        leg = bpy.context.active_object
        leg.scale = (0.22, 0.02, 0.02)
        leg.location = (x + 0.11 * math.cos(angle), y + 0.11 * math.sin(angle), base_z)
        leg.rotation_euler = (0, 0, angle)
        leg.data.materials.append(mat_metal)
        
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05)
        wheel = bpy.context.active_object
        wheel.location = (wx, wy, 0.05)
        wheel.data.materials.append(mat_metal)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.35)
    pole = bpy.context.active_object
    pole.location = (x, y, 0.225)
    pole.data.materials.append(mat_metal)
    
    bpy.ops.mesh.primitive_cube_add(size=1)
    seat = bpy.context.active_object
    seat.scale = (0.45, 0.4, 0.06)
    seat.location = (x, y, 0.45)
    seat.rotation_euler = (0, 0, rot)
    seat.data.materials.append(mat_seat)
    add_bevel(seat, segments=5, width=0.03)
    seat.name = "Seat"
    
    back_dist = 0.18
    back_x = x - back_dist * math.sin(rot)
    back_y = y - back_dist * math.cos(rot)
    bpy.ops.mesh.primitive_cube_add(size=1)
    back = bpy.context.active_object
    back.scale = (0.42, 0.06, 0.45)
    back.location = (back_x, back_y, 0.72)
    back.rotation_euler = (0, 0, rot)
    back.data.materials.append(mat_seat)
    add_bevel(back, segments=5, width=0.03)
    back.name = "ChairBack"

# ========== 改進盆栽 ==========
def create_plant_v2(x, y, z):
    """改進版盆栽 - 多層葉子"""
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.25)
    pot = bpy.context.active_object
    pot.location = (x, y, z + 0.125)
    pot.data.materials.append(mat_pot)
    pot.name = "PlantPot"
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.16, depth=0.05)
    soil = bpy.context.active_object
    soil.location = (x, y, z + 0.275)
    soil.data.materials.append(mat_pot)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.4)
    trunk = bpy.context.active_object
    trunk.location = (x, y, z + 0.5)
    trunk.data.materials.append(mat_pot)
    
    for i, (dy, dz, r) in enumerate([(0, 0.35, 0.25), (0.08, 0.45, 0.22), (-0.08, 0.5, 0.2), (0, 0.6, 0.15)]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r)
        leaf = bpy.context.active_object
        leaf.location = (x + dy, y, z + dz)
        leaf.data.materials.append(mat_plant)
        leaf.name = f"Leaf_{i}"

# ========== 飲水機 ==========
def create_water_cooler(x, y, z):
    """飲水機"""
    bpy.ops.mesh.primitive_cube_add(size=1)
    body = bpy.context.active_object
    body.scale = (0.4, 0.4, 1.0)
    body.location = (x, y, z + 0.5)
    body.data.materials.append(mat_water_cooler)
    add_bevel(body, segments=3, width=0.01)
    body.name = "WaterCooler"
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.4)
    tank = bpy.context.active_object
    tank.location = (x, y, z + 1.2)
    tank.data.materials.append(mat_water_blue)
    tank.name = "WaterTank"
    
    bpy.ops.mesh.primitive_cube_add(size=1)
    tap = bpy.context.active_object
    tap.scale = (0.1, 0.15, 0.1)
    tap.location = (x, y - 0.25, z + 0.3)
    tap.data.materials.append(mat_metal)

# ========== 影印機 ==========
def create_printer(x, y, z, rot=0):
    """影印機/列表機"""
    bpy.ops.mesh.primitive_cube_add(size=1)
    body = bpy.context.active_object
    body.scale = (0.5, 0.4, 0.35)
    body.location = (x, y, z + 0.35)
    body.rotation_euler = (0, 0, rot)
    body.data.materials.append(mat_printer)
    add_bevel(body, segments=3, width=0.01)
    body.name = "Printer"
    
    bpy.ops.mesh.primitive_cube_add(size=1)
    tray = bpy.context.active_object
    tray.scale = (0.45, 0.35, 0.02)
    tray.location = (x, y, z + 0.55)
    tray.rotation_euler = (0, 0, rot)
    tray.data.materials.append(mat_printer)

# ========== 玻璃隔間牆（含門）==========
def create_glass_partition_with_door(x, y, w, d, h, door_pos='center', door_w=1.0, name="GlassPartition"):
    """創建玻璃隔間牆（含門洞）"""
    door_h = 2.0
    is_horizontal = w > d
    
    if is_horizontal:
        left_w = (w - door_w) / 2 - 0.05
        if left_w > 0:
            bpy.ops.mesh.primitive_cube_add(size=1)
            glass = bpy.context.active_object
            glass.scale = (left_w, d, h)
            glass.location = (x - door_w/2 - left_w/2 - 0.05, y, h/2)
            glass.data.materials.append(mat_glass)
            glass.name = f"{name}_Left"
        
        right_w = (w - door_w) / 2 - 0.05
        if right_w > 0:
            bpy.ops.mesh.primitive_cube_add(size=1)
            glass = bpy.context.active_object
            glass.scale = (right_w, d, h)
            glass.location = (x + door_w/2 + right_w/2 + 0.05, y, h/2)
            glass.data.materials.append(mat_glass)
            glass.name = f"{name}_Right"
        
        if h > door_h:
            bpy.ops.mesh.primitive_cube_add(size=1)
            top = bpy.context.active_object
            top.scale = (door_w, d, h - door_h)
            top.location = (x, y, door_h + (h - door_h)/2)
            top.data.materials.append(mat_glass)
            top.name = f"{name}_Top"
        
        bpy.ops.mesh.primitive_cube_add(size=1)
        frame = bpy.context.active_object
        frame.scale = (door_w + 0.1, 0.08, 0.05)
        frame.location = (x, y, h)
        frame.data.materials.append(mat_glass_frame)
        frame.name = f"{name}_DoorFrame"
        
    else:
        top_d = (d - door_w) / 2 - 0.05
        if top_d > 0:
            bpy.ops.mesh.primitive_cube_add(size=1)
            glass = bpy.context.active_object
            glass.scale = (w, top_d, h)
            glass.location = (x, y + door_w/2 + top_d/2 + 0.05, h/2)
            glass.data.materials.append(mat_glass)
            glass.name = f"{name}_Top"
        
        bot_d = (d - door_w) / 2 - 0.05
        if bot_d > 0:
            bpy.ops.mesh.primitive_cube_add(size=1)
            glass = bpy.context.active_object
            glass.scale = (w, bot_d, h)
            glass.location = (x, y - door_w/2 - bot_d/2 - 0.05, h/2)
            glass.data.materials.append(mat_glass)
            glass.name = f"{name}_Bot"
        
        if h > door_h:
            bpy.ops.mesh.primitive_cube_add(size=1)
            top = bpy.context.active_object
            top.scale = (w, door_w, h - door_h)
            top.location = (x, y, door_h + (h - door_h)/2)
            top.data.materials.append(mat_glass)
            top.name = f"{name}_TopGlass"
        
        bpy.ops.mesh.primitive_cube_add(size=1)
        frame = bpy.context.active_object
        frame.scale = (0.08, door_w + 0.1, 0.05)
        frame.location = (x, y, h)
        frame.data.materials.append(mat_glass_frame)

# ========== 工作站 ==========
def create_workstation(x, y, facing='north', index=1):
    """創建工作站"""
    facing_map = {'north': 0, 'east': math.pi/2, 'west': -math.pi/2, 'south': math.pi}
    rot = facing_map.get(facing, 0)
    
    desktop_top = DESK_HEIGHT + DESK_THICK/2
    bpy.ops.mesh.primitive_cube_add(size=1)
    desk = bpy.context.active_object
    desk.scale = (DESK_WIDTH, DESK_DEPTH, DESK_THICK)
    desk.location = (x, y, desktop_top)
    desk.rotation_euler = (0, 0, rot)
    desk.data.materials.append(mat_desktop)
    add_bevel(desk, segments=3, width=0.01)
    desk.name = f"Desk_{index}"
    
    for dx, dy in [(-DESK_WIDTH/2 + 0.1, -DESK_DEPTH/2 + 0.1), 
                   (DESK_WIDTH/2 - 0.1, -DESK_DEPTH/2 + 0.1),
                   (-DESK_WIDTH/2 + 0.1, DESK_DEPTH/2 - 0.1),
                   (DESK_WIDTH/2 - 0.1, DESK_DEPTH/2 - 0.1)]:
        bx = x + dx * math.cos(rot) - dy * math.sin(rot)
        by = y + dx * math.sin(rot) + dy * math.cos(rot)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=DESK_HEIGHT)
        leg = bpy.context.active_object
        leg.location = (bx, by, DESK_HEIGHT/2)
        leg.data.materials.append(mat_metal)
    
    monitor_offset = DESK_DEPTH/2 - 0.15
    for sx in [-0.35, 0.35]:
        mx = x + sx * math.cos(rot) + monitor_offset * math.sin(rot)
        my = y + sx * math.sin(rot) - monitor_offset * math.cos(rot)
        
        bpy.ops.mesh.primitive_cube_add(size=1)
        monitor = bpy.context.active_object
        monitor.scale = (0.55, 0.03, 0.32)
        monitor.location = (mx, my, desktop_top + 0.12 + 0.16)
        monitor.rotation_euler = (0, 0, rot + math.pi)
        monitor.data.materials.append(mat_screen)
        add_bevel(monitor, segments=2, width=0.005)
        
        bpy.ops.mesh.primitive_cube_add(size=1)
        stand = bpy.context.active_object
        stand.scale = (0.03, 0.08, 0.12)
        stand.location = (mx, my, desktop_top + 0.06)
        stand.rotation_euler = (0, 0, rot)
        stand.data.materials.append(mat_metal)
    
    chair_offset = -DESK_DEPTH/2 - 0.4
    chair_x = x + chair_offset * math.sin(rot)
    chair_y = y - chair_offset * math.cos(rot)
    create_office_chair(chair_x, chair_y, rot=rot)

# ========== 場景佈局 ==========
ROOM_W = 16
ROOM_D = 14
WALL_H = 2.8

# 地板
bpy.ops.mesh.primitive_plane_add(size=1)
floor = bpy.context.active_object
floor.scale = (ROOM_W, ROOM_D, 1)
floor.data.materials.append(mat_floor)
floor.name = "Floor"

# 四周實心牆
WALL_THICK = 0.15

bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (ROOM_W, WALL_THICK, 0.3)
w.location = (0, -ROOM_D/2, 0.15)
w.data.materials.append(mat_wall)
w.name = "Wall_South_Low"

bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (ROOM_W, WALL_THICK, WALL_H)
w.location = (0, ROOM_D/2, WALL_H/2)
w.data.materials.append(mat_wall)
w.name = "Wall_North"

bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (WALL_THICK, ROOM_D, WALL_H)
w.location = (-ROOM_W/2, 0, WALL_H/2)
w.data.materials.append(mat_wall)
w.name = "Wall_West"

bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (WALL_THICK, ROOM_D, WALL_H)
w.location = (ROOM_W/2, 0, WALL_H/2)
w.data.materials.append(mat_wall)
w.name = "Wall_East"

# ========== 內部玻璃隔間（修正位置）==========
# 橫向玻璃隔間（分隔工作區和其他區域，門在中央）
create_glass_partition_with_door(0, 1.5, ROOM_W - 2, 0.02, 1.8, 'center', 1.2, "GlassPartition_Main")

# 會議區玻璃隔間（移到左側，不穿過會議桌）
# 原本：x=-3.5 會穿過會議桌中心(-4, -4)
# 修正：移到 x=-6.5（會議桌左側外圍）
create_glass_partition_with_door(-6.5, -4, 0.02, 5, 1.8, 'center', 1.0, "GlassPartition_Meeting")

# ========== 工作區（北區）==========
create_workstation(-5.5, 4, facing='east', index=1)
create_workstation(-5.5, 6, facing='east', index=2)
create_workstation(0, 5, facing='north', index=3)
create_workstation(5.5, 4, facing='west', index=4)
create_workstation(5.5, 6, facing='west', index=5)

# ========== 會議區（南區左側）==========
MEETING_X = -4
MEETING_Y = -4

# 橢圓會議桌
bpy.ops.mesh.primitive_cylinder_add(radius=1.2, depth=0.03)
t = bpy.context.active_object
t.scale = (1.0, 0.65, 1)
t.location = (MEETING_X, MEETING_Y, 0.77)
t.data.materials.append(mat_desktop)
add_bevel(t, segments=8, width=0.02)
t.name = "MeetingTable"

# 會議椅（修正：統一半徑，均勻分佈）
# 原本：X用1.6，Y用1.1（不均勻）
# 修正：改用橢圓分佈，配合桌子形狀
for i in range(6):
    angle = i * math.pi / 3
    # 配合橢圓桌子：長軸1.2，短軸0.78
    # 椅子距離：長軸方向1.8，短軸方向1.4
    cx = MEETING_X + 1.8 * math.cos(angle)
    cy = MEETING_Y + 1.4 * math.sin(angle)
    create_office_chair(cx, cy, target_x=MEETING_X, target_y=MEETING_Y)

# 白板（修正：貼到西牆上）
# 原本：x = -6.5（離牆太遠）
# 修正：x = -7.9（緊貼西牆 x=-8）
bpy.ops.mesh.primitive_cube_add(size=1)
wb = bpy.context.active_object
wb.scale = (0.02, 1.2, 0.8)
wb.location = (-7.9, MEETING_Y, 1.5)  # 緊貼西牆
wb.data.materials.append(mat_whiteboard)
add_bevel(wb, segments=2, width=0.005)
wb.name = "Whiteboard"

# ========== 休息區（南區右側）==========
LOUNGE_X = 4
LOUNGE_Y = -4

# L 型沙發
bpy.ops.mesh.primitive_cube_add(size=1)
sofa1 = bpy.context.active_object
sofa1.scale = (0.6, 2.0, 0.4)
sofa1.location = (LOUNGE_X + 1.2, LOUNGE_Y, 0.3)
sofa1.data.materials.append(mat_seat)
add_bevel(sofa1, segments=3, width=0.03)

bpy.ops.mesh.primitive_cube_add(size=1)
sofa2 = bpy.context.active_object
sofa2.scale = (2.0, 0.6, 0.4)
sofa2.location = (LOUNGE_X, LOUNGE_Y - 1.2, 0.3)
sofa2.data.materials.append(mat_seat)
add_bevel(sofa2, segments=3, width=0.03)

# 茶几（改為圓形，不再突兀）
bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=0.03)
table = bpy.context.active_object
table.location = (LOUNGE_X, LOUNGE_Y, 0.4)
table.data.materials.append(mat_desktop)
add_bevel(table, segments=8, width=0.015)
table.name = "CoffeeTable"

# ========== 辦公用品區（角落）==========
create_water_cooler(6, -2, 0)
create_printer(6.5, -4, 0, rot=math.pi/4)

# ========== 盆栽（角落裝飾）==========
create_plant_v2(-7, 6, 0)
create_plant_v2(7, 6, 0)
create_plant_v2(-7, -6, 0)
create_plant_v2(7, -6, 0)

# 時鐘（北牆）
bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.02)
clock = bpy.context.active_object
clock.location = (0, ROOM_D/2 - 0.1, 2.2)
clock.rotation_euler = (math.pi/2, 0, 0)
clock.data.materials.append(mat_metal)
clock.name = "Clock"

# 掛畫（北牆）
bpy.ops.mesh.primitive_cube_add(size=1)
art = bpy.context.active_object
art.scale = (0.8, 0.02, 0.5)
art.location = (-3, ROOM_D/2 - 0.1, 1.8)
art.data.materials.append(mat_seat)

# ========== 導出 GLB ==========
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(
    filepath='/mnt/e_drive/claude-office/blender/exports/office_v37.glb',
    export_format='GLB',
    use_selection=True
)

print("已導出: /mnt/e_drive/claude-office/blender/exports/office_v37.glb")
