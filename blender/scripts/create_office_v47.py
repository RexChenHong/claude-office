#!/usr/bin/env python3
"""V47 - 一體成型椅子 + 修正位置
1. 椅子用單一 mesh 做 L 型（不再分座墊和椅背）
2. 椅子位置修正：在桌子後方，不是前方
3. 移除玻璃隔間
"""
import bpy
import math
import sys
import bmesh

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
mat_seat = create_material("Seat", (0.25, 0.25, 0.28, 1), roughness=0.8)
mat_plant = create_material("Plant", (0.15, 0.45, 0.15, 1), roughness=0.8)
mat_pot = create_material("Pot", (0.6, 0.4, 0.3, 1), roughness=0.7)
mat_water_cooler = create_material("WaterCooler", (0.95, 0.95, 0.95, 1), roughness=0.3)
mat_water_blue = create_material("WaterBlue", (0.3, 0.6, 0.9, 0.8), roughness=0.1)
mat_printer = create_material("Printer", (0.2, 0.2, 0.2, 1), roughness=0.4)
mat_whiteboard = create_material("Whiteboard", (0.98, 0.98, 0.98, 1), roughness=0.2)
mat_sofa = create_material("Sofa", (0.4, 0.35, 0.3, 1), roughness=0.9)

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

# ========== 一體成型辦公椅（L 型）==========
def create_office_chair(x, y, rot=0, index=""):
    """創建一體成型 L 型辦公椅
    座墊 + 椅背用單一 mesh，確保 L 型結構
    
    座標系：
    - 椅子面向 rot 方向
    - rot=0 時面向 Y+ 方向
    - 椅背在 Y- 方向（後方）
    """
    # 5 腳輪底座
    base_z = 0.05
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.02)
    base = bpy.context.active_object
    base.location = (x, y, base_z)
    base.rotation_euler = (0, 0, rot)
    base.data.materials.append(mat_metal)
    base.name = f"ChairBase{index}"
    
    # 5 個支撐腳 + 輪子
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
    
    # 椅桿
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.35)
    pole = bpy.context.active_object
    pole.location = (x, y, 0.225)
    pole.data.materials.append(mat_metal)
    
    # ========== 一體成型 L 型座墊+椅背 ==========
    # 使用 bmesh 創建 L 型 mesh
    # 座墊：寬 0.4，深 0.38，高 0.08
    # 椅背：寬 0.36，深 0.06，高 0.5
    # L 型結構：椅背在座墊後方
    
    mesh = bpy.data.meshes.new(f"ChairMesh{index}")
    obj = bpy.data.objects.new(f"Chair{index}", mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    # 座墊尺寸
    seat_w = 0.4   # X 軸寬度
    seat_d = 0.38  # Y 軸深度
    seat_h = 0.08  # Z 軸高度
    seat_z = 0.47  # 座墊中心高度
    
    # 椅背尺寸
    back_w = 0.36  # X 軸寬度
    back_d = 0.06  # Y 軸厚度
    back_h = 0.5   # Z 軸高度
    back_offset = seat_d / 2  # 椅背在座墊後方
    
    # 座墊頂點（8 個）
    # 座墊中心在 (0, 0, seat_z)
    seat_vertices = [
        # 底部 4 點
        (-seat_w/2, -seat_d/2, seat_z - seat_h/2),
        (seat_w/2, -seat_d/2, seat_z - seat_h/2),
        (seat_w/2, seat_d/2, seat_z - seat_h/2),
        (-seat_w/2, seat_d/2, seat_z - seat_h/2),
        # 頂部 4 點
        (-seat_w/2, -seat_d/2, seat_z + seat_h/2),
        (seat_w/2, -seat_d/2, seat_z + seat_h/2),
        (seat_w/2, seat_d/2, seat_z + seat_h/2),
        (-seat_w/2, seat_d/2, seat_z + seat_h/2),
    ]
    
    # 椅背頂點（8 個）
    # 椅背底部緊貼座墊後方頂部
    back_bottom_z = seat_z + seat_h/2
    back_center_y = -seat_d/2 - back_d/2  # 椅背中心在座墊後方
    back_vertices = [
        # 底部 4 點
        (-back_w/2, back_center_y - back_d/2, back_bottom_z),
        (back_w/2, back_center_y - back_d/2, back_bottom_z),
        (back_w/2, back_center_y + back_d/2, back_bottom_z),
        (-back_w/2, back_center_y + back_d/2, back_bottom_z),
        # 頂部 4 點
        (-back_w/2, back_center_y - back_d/2, back_bottom_z + back_h),
        (back_w/2, back_center_y - back_d/2, back_bottom_z + back_h),
        (back_w/2, back_center_y + back_d/2, back_bottom_z + back_h),
        (-back_w/2, back_center_y + back_d/2, back_bottom_z + back_h),
    ]
    
    # 合併頂點
    all_vertices = seat_vertices + back_vertices
    
    # 創建頂點
    verts = [bm.verts.new(v) for v in all_vertices]
    bm.verts.ensure_lookup_table()
    
    # 座墊面（6 面）
    seat_faces = [
        # 底部
        (0, 1, 2, 3),
        # 頂部
        (4, 5, 6, 7),
        # 前面
        (0, 1, 5, 4),
        # 後面
        (3, 2, 6, 7),
        # 左面
        (0, 3, 7, 4),
        # 右面
        (1, 2, 6, 5),
    ]
    
    # 椅背面（6 面，但前面與座墊後面相鄰）
    back_faces = [
        # 底部
        (8, 9, 10, 11),
        # 頂部
        (12, 13, 14, 15),
        # 前面
        (8, 9, 13, 12),
        # 後面
        (11, 10, 14, 15),
        # 左面
        (8, 11, 15, 12),
        # 右面
        (9, 10, 14, 13),
    ]
    
    all_faces = seat_faces + back_faces
    
    for f in all_faces:
        bm.faces.new([verts[i] for i in f])
    
    bm.to_mesh(mesh)
    bm.free()
    
    # 設置位置和旋轉
    obj.location = (x, y, 0)
    obj.rotation_euler = (0, 0, rot)
    obj.data.materials.append(mat_seat)
    
    # 添加 bevel 修飾器
    add_bevel(obj, segments=3, width=0.02)

# ========== 盆栽 ==========
def create_plant_v2(x, y, z):
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

# ========== 飲水機 ==========
def create_water_cooler(x, y, z):
    bpy.ops.mesh.primitive_cube_add(size=1)
    body = bpy.context.active_object
    body.scale = (0.4, 0.4, 1.0)
    body.location = (x, y, z + 0.5)
    body.data.materials.append(mat_water_cooler)
    add_bevel(body, segments=3, width=0.01)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.4)
    tank = bpy.context.active_object
    tank.location = (x, y, z + 1.2)
    tank.data.materials.append(mat_water_blue)
    
    bpy.ops.mesh.primitive_cube_add(size=1)
    tap = bpy.context.active_object
    tap.scale = (0.1, 0.15, 0.1)
    tap.location = (x, y - 0.25, z + 0.3)
    tap.data.materials.append(mat_metal)

# ========== 影印機 ==========
def create_printer(x, y, z, rot=0):
    bpy.ops.mesh.primitive_cube_add(size=1)
    body = bpy.context.active_object
    body.scale = (0.5, 0.4, 0.35)
    body.location = (x, y, z + 0.35)
    body.rotation_euler = (0, 0, rot)
    body.data.materials.append(mat_printer)
    add_bevel(body, segments=3, width=0.01)
    
    bpy.ops.mesh.primitive_cube_add(size=1)
    tray = bpy.context.active_object
    tray.scale = (0.45, 0.35, 0.02)
    tray.location = (x, y, z + 0.55)
    tray.rotation_euler = (0, 0, rot)
    tray.data.materials.append(mat_printer)

# ========== 工作站 ==========
def create_workstation(x, y, facing='north', index=1):
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
    
    # V47 修正：椅子位置計算
    # rot=0（面向 Y+）：椅子在 Y- 方向
    # rot=π/2（面向 X+）：椅子在 X- 方向
    # 公式：chair_x = x - offset * sin(rot), chair_y = y - offset * cos(rot)
    chair_offset = DESK_DEPTH/2 + 0.5  # 正數！椅子在桌子後方
    chair_x = x - chair_offset * math.sin(rot)
    chair_y = y - chair_offset * math.cos(rot)
    
    # 椅子面向桌子（rot + π）
    create_office_chair(chair_x, chair_y, rot=rot + math.pi, index=f"_WS{index}")

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

# 會議椅（面向桌子中心）
chairs = [
    (0, "會議椅1"),
    (60, "會議椅2"),
    (120, "會議椅3"),
    (180, "會議椅4"),
    (240, "會議椅5"),
    (300, "會議椅6"),
]

for deg, name in chairs:
    angle = math.radians(deg)
    cx = MEETING_X + 1.8 * math.cos(angle)
    cy = MEETING_Y + 1.4 * math.sin(angle)
    # 計算椅子面向桌子中心的角度
    chair_rot = math.atan2(MEETING_Y - cy, MEETING_X - cx)
    create_office_chair(cx, cy, rot=chair_rot, index=f"_{name}")

# 白板（貼在西牆上）
bpy.ops.mesh.primitive_cube_add(size=1)
wb = bpy.context.active_object
wb.scale = (0.02, 1.2, 0.8)
wb.location = (-7.9, MEETING_Y, 1.5)
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
sofa1.data.materials.append(mat_sofa)
add_bevel(sofa1, segments=3, width=0.03)
sofa1.name = "Sofa1"

bpy.ops.mesh.primitive_cube_add(size=1)
sofa2 = bpy.context.active_object
sofa2.scale = (2.0, 0.6, 0.4)
sofa2.location = (LOUNGE_X, LOUNGE_Y - 1.2, 0.3)
sofa2.data.materials.append(mat_sofa)
add_bevel(sofa2, segments=3, width=0.03)
sofa2.name = "Sofa2"

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
art.name = "Art"

# ========== 導出 GLB ==========
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(
    filepath='/mnt/e_drive/claude-office/blender/exports/office_v47.glb',
    export_format='GLB',
    use_selection=True
)

print("已導出: /mnt/e_drive/claude-office/blender/exports/office_v47.glb")
