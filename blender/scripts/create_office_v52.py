#!/usr/bin/env python3
"""V52 - 桌上物品（螢幕、鍵盤、杯子）
1. 螢幕：黑色邊框、屏幕發光
2. 鍵盤：黑色、按鍵細節
3. 杯子：馬克杯
4. 方向：配合桌子朝向
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

# 椅子材質 - 擬真化
mat_seat_mesh = create_material("SeatMesh", (0.15, 0.15, 0.17, 1), roughness=0.7, metallic=0.0)  # 網布
mat_seat_cushion = create_material("SeatCushion", (0.2, 0.2, 0.22, 1), roughness=0.85, metallic=0.0)  # 海綿
mat_chrome = create_material("Chrome", (0.8, 0.8, 0.82, 1), roughness=0.05, metallic=0.95)  # 鉻合金
mat_plastic = create_material("ChairPlastic", (0.1, 0.1, 0.1, 1), roughness=0.4, metallic=0.0)  # 黑色塑料
mat_back_black = create_material("BackBlack", (0.08, 0.08, 0.08, 1), roughness=0.6, metallic=0.0)  # 椅背黑色
mat_armrest = create_material("Armrest", (0.1, 0.1, 0.1, 1), roughness=0.5, metallic=0.0)  # 扶手黑色

# 地板材質
mat_floor = create_material("Floor", (0.15, 0.10, 0.08, 1), roughness=0.9)

# 螢幕材質 - 優化
mat_screen_frame = create_material("ScreenFrame", (0.08, 0.08, 0.08, 1), roughness=0.15, metallic=0.7)
mat_screen_display = create_material("ScreenDisplay", (0.02, 0.02, 0.03, 1), roughness=0.05, emission=(0.15, 0.18, 0.22, 1))
mat_screen_stand = create_material("ScreenStand", (0.15, 0.15, 0.15, 1), roughness=0.2, metallic=0.85)

# 鍵盤材質 - 優化（深黑色塑料質感）
mat_keyboard = create_material("Keyboard", (0.12, 0.12, 0.12, 1), roughness=0.35, metallic=0.0)
mat_keys = create_material("Keys", (0.2, 0.2, 0.2, 1), roughness=0.25, metallic=0.0)

# 杯子材質 - 優化（陶瓷光澤）
mat_cup = create_material("Cup", (0.95, 0.93, 0.90, 1), roughness=0.1, metallic=0.0)
# 咖啡材質 - 深黑色液體
mat_coffee = create_material("Coffee", (0.02, 0.015, 0.01, 1), roughness=0.08, metallic=0.1)

def add_bevel(obj, segments=3, width=0.02):
    bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel.segments = segments
    bevel.width = width
    bevel.limit_method = 'ANGLE'

# ========== 椅子（擬真化 - 無旋轉版）==========
def create_chair(x, y, rot=0, index=""):
    """椅子所有部件都基於中心點 (0,0,0)，不使用旋轉，最後再移動+旋轉"""
    parts = []

    # ===== 五星腳架 =====
    for i in range(5):
        angle = i * 2 * math.pi / 5
        dx = math.cos(angle)
        dy = math.sin(angle)

        # 腳管（用多個小方塊組成，不用旋轉）
        for j in range(5):
            t = j / 4.0  # 0 到 1
            px = 0.04 + t * 0.18  # 從中心到末端
            py = 0
            bpy.ops.mesh.primitive_cube_add(size=1)
            leg_seg = bpy.context.active_object
            leg_seg.scale = (0.04, 0.02, 0.025)
            # 位置：沿著 angle 方向
            leg_seg.location = (px * dx, px * dy, 0.025)
            leg_seg.data.materials.append(mat_chrome)
            parts.append(leg_seg)

        # 輪子（在腳末端，接觸地面）
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.022)
        wheel = bpy.context.active_object
        wheel.location = (0.22 * dx, 0.22 * dy, 0.022)
        wheel.data.materials.append(mat_plastic)
        parts.append(wheel)

    # ===== 中央支柱 =====
    # 底座圓盤
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.015)
    base_disc = bpy.context.active_object
    base_disc.location = (0, 0, 0.022)
    base_disc.data.materials.append(mat_chrome)
    parts.append(base_disc)

    # 氣壓棒
    bpy.ops.mesh.primitive_cylinder_add(radius=0.022, depth=0.28)
    gas_lift = bpy.context.active_object
    gas_lift.location = (0, 0, 0.16)
    gas_lift.data.materials.append(mat_chrome)
    parts.append(gas_lift)

    # 座椅底盤
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.02)
    seat_plate = bpy.context.active_object
    seat_plate.location = (0, 0, 0.31)
    seat_plate.data.materials.append(mat_plastic)
    parts.append(seat_plate)

    # ===== 座墊 =====
    bpy.ops.mesh.primitive_cube_add(size=1)
    seat = bpy.context.active_object
    seat.scale = (0.38, 0.36, 0.07)
    seat.location = (0, 0.02, 0.37)
    seat.data.materials.append(mat_seat_cushion)
    add_bevel(seat, segments=4, width=0.04)
    parts.append(seat)

    # ===== 椅背 =====
    # 椅背支柱（左右兩根）
    for sx in [-0.15, 0.15]:
        bpy.ops.mesh.primitive_cube_add(size=1)
        back_frame = bpy.context.active_object
        back_frame.scale = (0.015, 0.015, 0.42)
        back_frame.location = (sx, -0.20, 0.62)
        back_frame.data.materials.append(mat_chrome)
        parts.append(back_frame)

    # 椅背頂部橫桿
    bpy.ops.mesh.primitive_cube_add(size=1)
    top_bar = bpy.context.active_object
    top_bar.scale = (0.32, 0.015, 0.015)
    top_bar.location = (0, -0.20, 0.84)
    top_bar.data.materials.append(mat_chrome)
    parts.append(top_bar)

    # 椅背主體
    bpy.ops.mesh.primitive_cube_add(size=1)
    back = bpy.context.active_object
    back.scale = (0.30, 0.035, 0.38)
    back.location = (0, -0.21, 0.63)
    back.data.materials.append(mat_back_black)
    add_bevel(back, segments=3, width=0.02)
    parts.append(back)

    # 腰靠
    bpy.ops.mesh.primitive_cube_add(size=1)
    lumbar = bpy.context.active_object
    lumbar.scale = (0.24, 0.04, 0.07)
    lumbar.location = (0, -0.18, 0.47)
    lumbar.data.materials.append(mat_back_black)
    add_bevel(lumbar, segments=3, width=0.02)
    parts.append(lumbar)

    # ===== 扶手 =====
    for sx in [-0.24, 0.24]:
        # 扶手支柱
        bpy.ops.mesh.primitive_cube_add(size=1)
        arm_post = bpy.context.active_object
        arm_post.scale = (0.015, 0.015, 0.12)
        arm_post.location = (sx, 0.05, 0.42)
        arm_post.data.materials.append(mat_chrome)
        parts.append(arm_post)

        # 扶手墊
        bpy.ops.mesh.primitive_cube_add(size=1)
        arm_pad = bpy.context.active_object
        arm_pad.scale = (0.04, 0.14, 0.018)
        arm_pad.location = (sx, 0.05, 0.50)
        arm_pad.data.materials.append(mat_armrest)
        add_bevel(arm_pad, segments=2, width=0.01)
        parts.append(arm_pad)

    # ===== 合併所有部件 =====
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()

    # 最後一次性設置位置和旋轉（z=0.025 讓輪子完全在地面之上）
    merged = bpy.context.active_object
    merged.location = (x, y, 0.025)
    merged.rotation_euler = (0, 0, rot)

# ========== 螢幕 ==========
# 桌面頂部在 z=0.775，所有物品要加上這個高度
DESKTOP_Z = 0.775

def create_monitor(parent, local_x, local_y):
    """創建螢幕（面向 Y-，即面向坐在椅子上的人）"""
    # 螢幕外框 - 加寬（增加高度）
    bpy.ops.mesh.primitive_cube_add(size=1)
    frame = bpy.context.active_object
    frame.scale = (0.55, 0.02, 0.45)
    frame.location = (local_x, local_y, DESKTOP_Z + 0.25)
    frame.data.materials.append(mat_screen_frame)
    add_bevel(frame, segments=2, width=0.003)
    frame.parent = parent

    # 螢幕顯示區（在框的椅子側 - 亮面面向椅子）
    bpy.ops.mesh.primitive_cube_add(size=1)
    display = bpy.context.active_object
    display.scale = (0.52, 0.01, 0.42)
    display.location = (local_x, local_y + 0.015, DESKTOP_Z + 0.25)
    display.data.materials.append(mat_screen_display)
    display.parent = parent

    # 底座支柱
    bpy.ops.mesh.primitive_cube_add(size=1)
    stand_pole = bpy.context.active_object
    stand_pole.scale = (0.03, 0.02, 0.08)
    stand_pole.location = (local_x, local_y, DESKTOP_Z + 0.045)
    stand_pole.data.materials.append(mat_screen_stand)
    stand_pole.parent = parent

    # 底座
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.01)
    stand_base = bpy.context.active_object
    stand_base.location = (local_x, local_y, DESKTOP_Z + 0.005)
    stand_base.data.materials.append(mat_screen_stand)
    stand_base.parent = parent

# ========== 鍵盤 ==========
def create_keyboard(parent, local_x, local_y):
    """創建鍵盤（在桌面靠近椅子側）"""
    # 鍵盤主體 - 加大 + 凹槽效果
    bpy.ops.mesh.primitive_cube_add(size=1)
    kb_body = bpy.context.active_object
    kb_body.scale = (0.45, 0.18, 0.025)
    kb_body.location = (local_x, local_y, DESKTOP_Z + 0.0125)
    kb_body.data.materials.append(mat_keyboard)
    add_bevel(kb_body, segments=2, width=0.005)
    kb_body.parent = parent

    # 按鍵（加深凹凸感）
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
    """創建馬克杯（在桌面角落）"""
    outer_r = 0.05
    cup_h = 0.10

    # 杯身（外殼）
    bpy.ops.mesh.primitive_cylinder_add(radius=outer_r, depth=cup_h)
    cup_body = bpy.context.active_object
    cup_body.location = (local_x, local_y, DESKTOP_Z + cup_h/2)
    cup_body.data.materials.append(mat_cup)
    cup_body.parent = parent

    # 咖啡液面（在杯口位置，從上方可見）
    # 放在杯子頂部，略小於杯口
    coffee_r = outer_r - 0.004
    coffee_h = 0.004  # 薄薄一層
    coffee_z = DESKTOP_Z + cup_h + coffee_h/2  # 在杯口之上
    bpy.ops.mesh.primitive_cylinder_add(radius=coffee_r, depth=coffee_h)
    coffee = bpy.context.active_object
    coffee.location = (local_x, local_y, coffee_z)
    coffee.data.materials.append(mat_coffee)
    coffee.parent = parent

    # 杯把
    bpy.ops.mesh.primitive_torus_add(major_radius=0.035, minor_radius=0.012)
    handle = bpy.context.active_object
    handle.location = (local_x + 0.06, local_y, DESKTOP_Z + 0.055)
    handle.rotation_euler = (0, math.pi/2, 0)
    handle.data.materials.append(mat_cup)
    handle.parent = parent

# ========== 桌子 ==========
def create_desk(x, y, rot=0, index=1):
    """桌子 + 桌上物品"""
    desk_parent = bpy.data.objects.new(f"Desk_{index}_Parent", None)
    bpy.context.collection.objects.link(desk_parent)
    desk_parent.location = (x, y, 0)
    desk_parent.rotation_euler = (0, 0, rot)
    
    # 桌面板
    bpy.ops.mesh.primitive_cube_add(size=1)
    desktop = bpy.context.active_object
    desktop.scale = (1.4, 0.75, 0.025)
    desktop.location = (0, 0, 0.7625)
    desktop.data.materials.append(mat_desktop)
    add_bevel(desktop, segments=4, width=0.01)
    desktop.parent = desk_parent
    
    # 金屬邊框
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
    
    # 桌腳
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
    
    # ========== 桌上物品 ==========
    # 螢幕在桌子遠端（local_y < 0），面向椅子
    # 雙螢幕
    create_monitor(desk_parent, -0.25, -0.28)
    create_monitor(desk_parent, 0.25, -0.28)

    # 鍵盤（在靠近椅子側）
    create_keyboard(desk_parent, 0, 0.25)

    # 杯子（放在右側靠近椅子，避開螢幕）
    create_cup(desk_parent, 0.55, 0.15)

# ========== 地板 ==========
bpy.ops.mesh.primitive_plane_add(size=1)
floor = bpy.context.active_object
floor.scale = (16, 14, 1)
floor.data.materials.append(mat_floor)

# ========== 5 張工作站 ==========
chair_offset = 0.875

# 工作站 1: (-5.5, 4), 面向東
create_desk(-5.5, 4, rot=math.pi/2, index=1)
create_chair(-5.5 - chair_offset, 4, rot=-math.pi/2, index="_WS1")

# 工作站 2: (-5.5, 6), 面向東
create_desk(-5.5, 6, rot=math.pi/2, index=2)
create_chair(-5.5 - chair_offset, 6, rot=-math.pi/2, index="_WS2")

# 工作站 3: (0, 5), 面向北
create_desk(0, 5, rot=0, index=3)
create_chair(0, 5 + chair_offset, rot=math.pi, index="_WS3")

# 工作站 4: (5.5, 4), 面向西
create_desk(5.5, 4, rot=-math.pi/2, index=4)
create_chair(5.5 + chair_offset, 4, rot=math.pi/2, index="_WS4")

# 工作站 5: (5.5, 6), 面向西
create_desk(5.5, 6, rot=-math.pi/2, index=5)
create_chair(5.5 + chair_offset, 6, rot=math.pi/2, index="_WS5")

# ========== 導出 ==========
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(
    filepath='/mnt/e_drive/claude-office/blender/exports/office_v52.glb',
    export_format='GLB',
    use_selection=True
)

print("已導出 V52")
