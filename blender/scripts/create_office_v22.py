#!/usr/bin/env python3
"""
Claude Office V23 - 加強圓角版（更明顯的 Bevel）
加大圓角寬度，讓效果更明顯
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

def create_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    return mat

# 材質定義（保持 V19 的顏色，但調整 roughness）
mat_floor = create_material("DarkWoodFloor", (0.25, 0.18, 0.12, 1), roughness=0.85)
mat_wall = create_material("Wall", (0.92, 0.92, 0.9, 1), roughness=0.95)
mat_glass = create_material("Glass", (0.85, 0.92, 0.98, 0.15), roughness=0.1)
mat_metal_frame = create_material("Metal_Frame", (0.08, 0.08, 0.08, 1), roughness=0.5, metallic=0.4)
mat_desktop = create_material("Desktop", (0.95, 0.95, 0.93, 1), roughness=0.6)
mat_seat = create_material("Seat", (0.06, 0.06, 0.06, 1), roughness=0.9)
mat_metal = create_material("Metal", (0.35, 0.35, 0.37, 1), roughness=0.4, metallic=0.5)
mat_plastic = create_material("Plastic", (0.04, 0.04, 0.04, 1), roughness=0.7)
mat_screen = create_material("Screen", (0.1, 0.13, 0.16, 1), roughness=0.4)
mat_meeting_table = create_material("Meeting_Table", (0.55, 0.45, 0.38, 1), roughness=0.6)
mat_whiteboard = create_material("Whiteboard", (0.98, 0.98, 0.98, 1), roughness=0.5)
mat_sofa = create_material("Sofa", (0.22, 0.22, 0.24, 1), roughness=0.95)
mat_plant_pot = create_material("Pot", (0.65, 0.45, 0.32, 1), roughness=0.8)
mat_plant = create_material("Plant", (0.18, 0.38, 0.15, 1), roughness=0.8)
mat_printer = create_material("Printer", (0.18, 0.18, 0.18, 1), roughness=0.6)
mat_water_dispenser = create_material("WaterDispenser", (0.88, 0.88, 0.88, 1), roughness=0.5)
mat_cabinet = create_material("Cabinet", (0.55, 0.55, 0.57, 1), roughness=0.6, metallic=0.2)
mat_trash_bin = create_material("TrashBin", (0.22, 0.22, 0.22, 1), roughness=0.7)
mat_carpet = create_material("Carpet", (0.5, 0.43, 0.38, 1), roughness=0.98)
mat_lamp = create_material("Lamp", (0.12, 0.12, 0.12, 1), roughness=0.5, metallic=0.3)

# ========== 圓角函數 ==========

def add_bevel(obj, segments=3, width=0.008):
    """為物件添加 Bevel modifier"""
    bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel.segments = segments
    bevel.width = width
    bevel.limit_method = 'ANGLE'
    bevel.angle_limit = math.radians(30)
    bevel.use_clamp_overlap = True
    return bevel

# ========== 房間尺寸 ==========

ROOM_W = 16
ROOM_D = 14
WALL_H = 2.8

# ========== 地板（深色木地板）==========

bpy.ops.mesh.primitive_plane_add(size=1)
floor = bpy.context.active_object
floor.scale = (ROOM_W + 2, ROOM_D + 2, 1)
floor.data.materials.append(mat_floor)
# 地板不需要圓角

# ========== 牆壁 ==========

# 後牆
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (ROOM_W/2 + 0.15, 0.08, WALL_H/2)
w.location = (0, -ROOM_D/2 - 0.04, WALL_H/2)
w.data.materials.append(mat_wall)
add_bevel(w, segments=2, width=0.005)

# 前牆（完整）
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (ROOM_W/2 - 1.2, 0.08, WALL_H/2)
w.location = (-ROOM_W/4 - 0.6, ROOM_D/2 + 0.04, WALL_H/2)
w.data.materials.append(mat_wall)
add_bevel(w, segments=2, width=0.005)

bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (ROOM_W/2 - 1.2, 0.08, WALL_H/2)
w.location = (ROOM_W/4 + 0.6, ROOM_D/2 + 0.04, WALL_H/2)
w.data.materials.append(mat_wall)
add_bevel(w, segments=2, width=0.005)

bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (1.2, 0.08, (WALL_H - 2.2)/2)
w.location = (0, ROOM_D/2 + 0.04, 2.2 + (WALL_H - 2.2)/2)
w.data.materials.append(mat_wall)
add_bevel(w, segments=2, width=0.005)

# 左牆
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.08, ROOM_D/2, WALL_H/2)
w.location = (-ROOM_W/2 - 0.04, 0, WALL_H/2)
w.data.materials.append(mat_wall)
add_bevel(w, segments=2, width=0.005)

# 右牆
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.08, ROOM_D/2, WALL_H/2)
w.location = (ROOM_W/2 + 0.04, 0, WALL_H/2)
w.data.materials.append(mat_wall)
add_bevel(w, segments=2, width=0.005)

# 落地窗
bpy.ops.mesh.primitive_cube_add(size=1)
window = bpy.context.active_object
window.scale = (0.02, 5, WALL_H/2 - 0.15)
window.location = (ROOM_W/2 + 0.07, 0, WALL_H/2)
window.data.materials.append(mat_glass)
add_bevel(window, segments=2, width=0.003)

# ========== 主官辦公室隔間 ==========

for fx, fy in [(-2.5, -1.5), (-2.5, 1.5), (0.5, -1.5), (0.5, 1.5)]:
    bpy.ops.mesh.primitive_cube_add(size=1)
    f = bpy.context.active_object
    f.scale = (0.035, 0.035, WALL_H/2)
    f.location = (fx, fy, WALL_H/2)
    f.data.materials.append(mat_metal_frame)
    add_bevel(f, segments=2, width=0.005)

# 左面玻璃
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.015, 1.5, WALL_H/2)
w.location = (-2.5, 0, WALL_H/2)
w.data.materials.append(mat_glass)
add_bevel(w, segments=2, width=0.003)

# 右面玻璃
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.015, 1.5, WALL_H/2)
w.location = (0.5, 0, WALL_H/2)
w.data.materials.append(mat_glass)
add_bevel(w, segments=2, width=0.003)

# ========== L 型玻璃隔間 ==========

# 短邊
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.015, 2.5, WALL_H/2)
w.location = (-4, -4.5, WALL_H/2)
w.data.materials.append(mat_glass)
add_bevel(w, segments=2, width=0.003)

# 長邊
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (4.5, 0.015, WALL_H/2)
w.location = (0.5, -7, WALL_H/2)
w.data.materials.append(mat_glass)
add_bevel(w, segments=2, width=0.003)

# 金屬框架
frame_positions = [(-4, -7), (-4, -2), (-1, -7), (2, -7), (5, -7)]
for fx, fy in frame_positions:
    bpy.ops.mesh.primitive_cube_add(size=1)
    f = bpy.context.active_object
    f.scale = (0.035, 0.035, WALL_H/2)
    f.location = (fx, fy, WALL_H/2)
    f.data.materials.append(mat_metal_frame)
    add_bevel(f, segments=2, width=0.005)

# ========== 會議室 ==========

MEETING_X, MEETING_Y = -2, -5

bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=0.035)
t = bpy.context.active_object
t.scale = (1, 0.6, 1)
t.location = (MEETING_X, MEETING_Y, 0.75)
t.data.materials.append(mat_meeting_table)
# 圓柱體不需要額外圓角

for i in range(4):
    angle = i * (math.pi / 2) + math.pi/4
    cx = MEETING_X + math.cos(angle) * 0.75
    cy = MEETING_Y + math.sin(angle) * 0.45
    bpy.ops.mesh.primitive_cube_add(size=1)
    c = bpy.context.active_object
    c.scale = (0.26, 0.26, 0.045)
    c.location = (cx, cy, 0.48)
    c.rotation_euler = (0, 0, angle + math.pi)
    c.data.materials.append(mat_seat)
    add_bevel(c, segments=3, width=0.01)

bpy.ops.mesh.primitive_cube_add(size=1)
wb = bpy.context.active_object
wb.scale = (0.015, 0.75, 0.45)
wb.location = (-ROOM_W/2 + 0.12, MEETING_Y, 1.3)
wb.data.materials.append(mat_whiteboard)
add_bevel(wb, segments=2, width=0.003)

# ========== 休息區 ==========

LOUNGE_X, LOUNGE_Y = 3, -5

# 地毯
bpy.ops.mesh.primitive_plane_add(size=1)
c = bpy.context.active_object
c.scale = (1.8, 1.8, 1)
c.location = (LOUNGE_X, LOUNGE_Y, 0.01)
c.data.materials.append(mat_carpet)

# L 型沙發（坐墊）
bpy.ops.mesh.primitive_cube_add(size=1)
s = bpy.context.active_object
s.scale = (1.0, 0.3, 0.25)
s.location = (LOUNGE_X, LOUNGE_Y - 0.4, 0.25)
s.data.materials.append(mat_sofa)
add_bevel(s, segments=4, width=0.03)  # 沙發用更大圓角

# 沙發靠背
bpy.ops.mesh.primitive_cube_add(size=1)
s = bpy.context.active_object
s.scale = (1.0, 0.05, 0.18)
s.location = (LOUNGE_X, LOUNGE_Y - 0.6, 0.4)
s.data.materials.append(mat_sofa)
add_bevel(s, segments=3, width=0.015)

# L 型側邊
bpy.ops.mesh.primitive_cube_add(size=1)
s = bpy.context.active_object
s.scale = (0.3, 0.8, 0.25)
s.location = (LOUNGE_X + 0.55, LOUNGE_Y, 0.25)
s.data.materials.append(mat_sofa)
add_bevel(s, segments=4, width=0.03)

# 茶几
bpy.ops.mesh.primitive_cube_add(size=1)
ct = bpy.context.active_object
ct.scale = (0.4, 0.24, 0.012)
ct.location = (LOUNGE_X + 0.1, LOUNGE_Y + 0.18, 0.32)
ct.data.materials.append(mat_meeting_table)
add_bevel(ct, segments=3, width=0.01)

for dx, dy in [(-0.15, -0.06), (-0.15, 0.06), (0.15, -0.06), (0.15, 0.06)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.01, depth=0.25)
    l = bpy.context.active_object
    l.location = (LOUNGE_X + 0.1 + dx, LOUNGE_Y + 0.18 + dy, 0.14)
    l.data.materials.append(mat_metal)

# ========== 工作站 ==========

def create_workstation(x, y, facing='north', index=1):
    angles = {'north': 0, 'south': math.pi, 'east': math.pi/2, 'west': -math.pi/2}
    rot = angles[facing]

    # 桌面（大圓角）
    bpy.ops.mesh.primitive_cube_add(size=1)
    d = bpy.context.active_object
    d.scale = (1.3, 0.65, 0.022)
    d.location = (x, y, 0.75)
    d.rotation_euler = (0, 0, rot)
    d.data.materials.append(mat_desktop)
    add_bevel(d, segments=4, width=0.015)

    # 桌腳（圓柱不需要圓角）
    for dx, dy in [(-0.55, -0.25), (-0.55, 0.25), (0.55, -0.25), (0.55, 0.25)]:
        bx = x + dx * math.cos(rot) - dy * math.sin(rot)
        by = y + dx * math.sin(rot) + dy * math.cos(rot)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.65)
        leg = bpy.context.active_object
        leg.location = (bx, by, 0.375)
        leg.data.materials.append(mat_metal)

    # 螢幕
    for sx in [-0.3, 0.3]:
        bx = x + sx * math.cos(rot) + 0.35 * math.sin(rot)
        by = y + sx * math.sin(rot) + 0.35 * math.cos(rot)
        bpy.ops.mesh.primitive_cube_add(size=1)
        s = bpy.context.active_object
        s.scale = (0.5, 0.02, 0.28)
        s.location = (bx, by, 1.0)
        s.rotation_euler = (0, 0, rot + math.pi)
        s.data.materials.append(mat_screen)
        add_bevel(s, segments=2, width=0.005)

    # 鍵盤
    kx = x - 0.3 * math.sin(rot)
    ky = y + 0.3 * math.cos(rot)
    bpy.ops.mesh.primitive_cube_add(size=1)
    kb = bpy.context.active_object
    kb.scale = (0.32, 0.1, 0.012)
    kb.location = (kx, ky, 0.43)
    kb.rotation_euler = (0, 0, rot)
    kb.data.materials.append(mat_plastic)
    add_bevel(kb, segments=2, width=0.005)

    # 滑鼠
    bpy.ops.mesh.primitive_cube_add(size=1)
    m = bpy.context.active_object
    m.scale = (0.05, 0.08, 0.02)
    m.location = (kx + 0.2*math.cos(rot), ky + 0.2*math.sin(rot), 0.43)
    m.rotation_euler = (0, 0, rot)
    m.data.materials.append(mat_plastic)
    add_bevel(m, segments=2, width=0.005)

    # 椅子
    chair_offset = -0.75
    chair_x = x + chair_offset * math.sin(rot)
    chair_y = y + chair_offset * math.cos(rot)
    chair_rot = rot

    # 椅座（大圓角）
    bpy.ops.mesh.primitive_cube_add(size=1)
    seat = bpy.context.active_object
    seat.scale = (0.4, 0.36, 0.07)
    seat.location = (chair_x, chair_y, 0.48)
    seat.rotation_euler = (0, 0, chair_rot)
    seat.data.materials.append(mat_seat)
    add_bevel(seat, segments=4, width=0.02)

    # 椅背
    back_x = chair_x - 0.16 * math.sin(chair_rot)
    back_y = chair_y - 0.16 * math.cos(chair_rot)
    bpy.ops.mesh.primitive_cube_add(size=1)
    back = bpy.context.active_object
    back.scale = (0.38, 0.05, 0.4)
    back.location = (back_x, back_y, 0.72)
    back.rotation_euler = (math.radians(8), 0, chair_rot)
    back.data.materials.append(mat_seat)
    add_bevel(back, segments=3, width=0.015)

    # 椅子支柱
    bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.3)
    p = bpy.context.active_object
    p.location = (chair_x, chair_y, 0.32)
    p.data.materials.append(mat_metal)

    # 輪子
    for i in range(5):
        angle = chair_rot + i * (2 * math.pi / 5)
        bpy.ops.mesh.primitive_cube_add(size=1)
        arm = bpy.context.active_object
        arm.scale = (0.2, 0.02, 0.015)
        arm.location = (chair_x + math.cos(angle)*0.1, chair_y + math.sin(angle)*0.1, 0.07)
        arm.rotation_euler = (0, 0, angle)
        arm.data.materials.append(mat_metal)
        add_bevel(arm, segments=2, width=0.003)

        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.018)
        wh = bpy.context.active_object
        wh.location = (chair_x + math.cos(angle)*0.2, chair_y + math.sin(angle)*0.2, 0.018)
        wh.data.materials.append(mat_plastic)

# ========== 工作站佈局 ==========

create_workstation(-5.5, 2, facing='east', index=1)
create_workstation(-5.5, 4.5, facing='east', index=2)
create_workstation(-1, 0, facing='north', index=3)
create_workstation(5.5, 2, facing='west', index=4)
create_workstation(5.5, 4.5, facing='west', index=5)

# ========== 設備 ==========

# 印表機
bpy.ops.mesh.primitive_cube_add(size=1)
printer = bpy.context.active_object
printer.scale = (0.28, 0.25, 0.18)
printer.location = (-ROOM_W/2 + 0.3, 3.5, 0.5)
printer.data.materials.append(mat_printer)
add_bevel(printer, segments=3, width=0.01)

# 飲水機
bpy.ops.mesh.primitive_cube_add(size=1)
water = bpy.context.active_object
water.scale = (0.25, 0.25, 0.85)
water.location = (6.5, 5.5, 0.45)
water.data.materials.append(mat_water_dispenser)
add_bevel(water, segments=3, width=0.01)

# 文件櫃
for i in range(3):
    bpy.ops.mesh.primitive_cube_add(size=1)
    cab = bpy.context.active_object
    cab.scale = (0.32, 0.38, 0.65)
    cab.location = (-ROOM_W/2 + 0.28, -1 + i * 0.45, 0.35)
    cab.data.materials.append(mat_cabinet)
    add_bevel(cab, segments=3, width=0.01)

# 垃圾桶
for bx, by in [(-6.5, 2), (-0.5, -1), (6.5, 2)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.25)
    trash = bpy.context.active_object
    trash.location = (bx, by, 0.15)
    trash.data.materials.append(mat_trash_bin)

# 檯燈
for lx, ly in [(-5, 1.5), (5, 1.5)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.4)
    lamp_pole = bpy.context.active_object
    lamp_pole.location = (lx, ly, 0.55)
    lamp_pole.data.materials.append(mat_metal)

    bpy.ops.mesh.primitive_cone_add(radius1=0.08, depth=0.06)
    lamp_shade = bpy.context.active_object
    lamp_shade.location = (lx, ly, 0.8)
    lamp_shade.data.materials.append(mat_lamp)

# 大型綠植
for px, py in [(6, -6), (-6, 5.5), (6, 5.5)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.12)
    pot = bpy.context.active_object
    pot.location = (px, py, 0.56)
    pot.data.materials.append(mat_plant_pot)

    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.14)
    plant = bpy.context.active_object
    plant.location = (px, py, 0.8)
    plant.scale = (1, 1, 1.2)
    plant.data.materials.append(mat_plant)

# 小型桌面盆栽
for dx, dy in [(-5.5, 2.5), (5.5, 2.5)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.04)
    dp = bpy.context.active_object
    dp.location = (dx + 0.5, dy - 0.25, 0.79)
    dp.data.materials.append(mat_plant_pot)

    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.04)
    pl = bpy.context.active_object
    pl.location = (dx + 0.5, dy - 0.25, 0.85)
    pl.data.materials.append(mat_plant)

# 時鐘
bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.015)
clock = bpy.context.active_object
clock.location = (0, -6.8, 2.3)
clock.rotation_euler = (math.pi/2, 0, 0)
clock.data.materials.append(mat_metal_frame)

print("✅ V22 完成！")
print("已為所有物件添加 Bevel modifier（圓角）")
print("圓角設定：segments=2-4, width=0.005-0.03")

# ========== 應用所有 Modifiers（關鍵步驟！）==========

print("正在應用所有 modifiers...")
for obj in bpy.data.objects:
    if obj.type == 'MESH' and obj.modifiers:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        for modifier in obj.modifiers:
            try:
                bpy.ops.object.modifier_apply(modifier=modifier.name)
                print(f"  ✓ 已應用 {obj.name} 的 {modifier.name}")
            except Exception as e:
                print(f"  ✗ 應用失敗 {obj.name}: {e}")

print("✅ 所有 modifiers 已應用！")
