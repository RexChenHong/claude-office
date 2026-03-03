#!/usr/bin/env python3
"""
Claude Office V13 - 專業室內設計風格
基於 Sketchfab 參考模型的設計原則：
1. 全高玻璃隔間（透明，保持視覺連接）
2. 模塊化工作站（對稱排列）
3. 統一材質（白桌、黑椅、淺灰地板）
4. 極簡裝飾（功能性優先）
5. 材質對比（玻璃 vs 金屬 vs 木材）
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

# ========== 材質（統一風格）==========

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

# 淺灰色地板（參考風格）
mat_floor = create_material("Floor", (0.75, 0.75, 0.75, 1), roughness=0.6)
mat_wall = create_material("Wall", (0.95, 0.95, 0.93, 1), roughness=0.9)
# 透明玻璃（隔間）
mat_glass = create_material("Glass", (0.85, 0.92, 0.98, 0.12), roughness=0.05)
# 黑色金屬框
mat_metal_frame = create_material("Metal_Frame", (0.12, 0.12, 0.12, 1), roughness=0.2, metallic=0.85)
# 白色桌面
mat_desktop = create_material("Desktop", (0.98, 0.98, 0.96, 1), roughness=0.25)
# 黑色座椅
mat_seat = create_material("Seat", (0.08, 0.08, 0.08, 1), roughness=0.7)
# 金屬（桌腿、椅子腳）
mat_metal = create_material("Metal", (0.4, 0.4, 0.42, 1), roughness=0.15, metallic=0.9)
mat_plastic = create_material("Plastic", (0.05, 0.05, 0.05, 1), roughness=0.35)
mat_screen = create_material("Screen", (0.12, 0.15, 0.18, 1), roughness=0.08, emission=(0.22, 0.27, 0.32, 1))
# 會議桌（淺木色）
mat_meeting_table = create_material("Meeting_Table", (0.65, 0.55, 0.45, 1), roughness=0.35)
# 白板（功能性）
mat_whiteboard = create_material("Whiteboard", (0.99, 0.99, 0.99, 1), roughness=0.25)
# 沙發（深灰色）
mat_sofa = create_material("Sofa", (0.28, 0.28, 0.3, 1), roughness=0.9)
# 綠植
mat_plant_pot = create_material("Pot", (0.7, 0.5, 0.35, 1), roughness=0.6)
mat_plant = create_material("Plant", (0.2, 0.4, 0.18, 1), roughness=0.5)

# ========== 房間尺寸 ==========

ROOM_W = 16
ROOM_D = 14
WALL_H = 2.8

# ========== 地板（淺灰色）==========

bpy.ops.mesh.primitive_plane_add(size=1)
floor = bpy.context.active_object
floor.name = "Floor"
floor.scale = (ROOM_W + 2, ROOM_D + 2, 1)
floor.data.materials.append(mat_floor)

# ========== 外牆 ==========

# 後牆
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (ROOM_W/2 + 0.15, 0.08, WALL_H/2)
w.location = (0, -ROOM_D/2 - 0.04, WALL_H/2)
w.data.materials.append(mat_wall)

# 前牆（左半）
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (ROOM_W/4 - 0.5, 0.08, WALL_H/2)
w.location = (-ROOM_W/4 - 0.5, ROOM_D/2 + 0.04, WALL_H/2)
w.data.materials.append(mat_wall)

# 前牆（右半）
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (ROOM_W/4 - 0.5, 0.08, WALL_H/2)
w.location = (ROOM_W/4 + 0.5, ROOM_D/2 + 0.04, WALL_H/2)
w.data.materials.append(mat_wall)

# 門上方
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (1.2, 0.08, (WALL_H - 2.2)/2)
w.location = (0, ROOM_D/2 + 0.04, 2.2 + (WALL_H - 2.2)/2)
w.data.materials.append(mat_wall)

# 左牆
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.08, ROOM_D/2, WALL_H/2)
w.location = (-ROOM_W/2 - 0.04, 0, WALL_H/2)
w.data.materials.append(mat_wall)

# 右牆
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.08, ROOM_D/2, WALL_H/2)
w.location = (ROOM_W/2 + 0.04, 0, WALL_H/2)
w.data.materials.append(mat_wall)

# 落地窗
bpy.ops.mesh.primitive_cube_add(size=1)
window = bpy.context.active_object
window.scale = (0.02, 5, WALL_H/2 - 0.15)
window.location = (ROOM_W/2 + 0.07, 0, WALL_H/2)
window.data.materials.append(mat_glass)

# ========== 全高玻璃隔間（會議室）==========

# 會議室位置：左後角
MEETING_X, MEETING_Y = -5, -4

# 前面玻璃（有入口）
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.65, 0.015, WALL_H/2)
w.location = (MEETING_X - 1.3, MEETING_Y + 2, WALL_H/2)
w.data.materials.append(mat_glass)

bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.65, 0.015, WALL_H/2)
w.location = (MEETING_X + 1.3, MEETING_Y + 2, WALL_H/2)
w.data.materials.append(mat_glass)

# 右面玻璃
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.015, 2, WALL_H/2)
w.location = (MEETING_X + 2, MEETING_Y, WALL_H/2)
w.data.materials.append(mat_glass)

# 黑色金屬框架
frame_positions = [
    (MEETING_X - 2, MEETING_Y + 2),
    (MEETING_X - 0.8, MEETING_Y + 2),
    (MEETING_X + 0.8, MEETING_Y + 2),
    (MEETING_X + 2, MEETING_Y + 2),
    (MEETING_X + 2, MEETING_Y),
    (MEETING_X + 2, MEETING_Y - 2),
]
for fx, fy in frame_positions:
    bpy.ops.mesh.primitive_cube_add(size=1)
    f = bpy.context.active_object
    f.scale = (0.035, 0.035, WALL_H/2)
    f.location = (fx, fy, WALL_H/2)
    f.data.materials.append(mat_metal_frame)

# 會議桌（橢圓形）
bpy.ops.mesh.primitive_cylinder_add(radius=0.65, depth=0.035)
t = bpy.context.active_object
t.scale = (1, 0.6, 1)
t.location = (MEETING_X, MEETING_Y, 0.75)
t.data.materials.append(mat_meeting_table)

# 會議椅（4 把，面向桌子）
for i in range(4):
    angle = i * (math.pi / 2) + math.pi/4
    cx = MEETING_X + math.cos(angle) * 0.85
    cy = MEETING_Y + math.sin(angle) * 0.5
    bpy.ops.mesh.primitive_cube_add(size=1)
    c = bpy.context.active_object
    c.scale = (0.26, 0.26, 0.045)
    c.location = (cx, cy, 0.48)
    c.rotation_euler = (0, 0, angle + math.pi)
    c.data.materials.append(mat_seat)

# 白板（功能性裝飾）
bpy.ops.mesh.primitive_cube_add(size=1)
wb = bpy.context.active_object
wb.scale = (0.015, 0.85, 0.5)
wb.location = (-ROOM_W/2 + 0.12, MEETING_Y, 1.35)
wb.data.materials.append(mat_whiteboard)

# ========== 全高玻璃隔間（休息區）==========

# 休息區位置：右後角
LOUNGE_X, LOUNGE_Y = 5.5, -4.5

# 左面玻璃（有入口）
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.015, 1.5, WALL_H/2)
w.location = (LOUNGE_X - 1.5, LOUNGE_Y - 1, WALL_H/2)
w.data.materials.append(mat_glass)

bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.015, 1.5, WALL_H/2)
w.location = (LOUNGE_X - 1.5, LOUNGE_Y + 1, WALL_H/2)
w.data.materials.append(mat_glass)

# 黑色金屬框架
lounge_frames = [
    (LOUNGE_X - 1.5, LOUNGE_Y - 2),
    (LOUNGE_X - 1.5, LOUNGE_Y - 0.5),
    (LOUNGE_X - 1.5, LOUNGE_Y + 0.5),
    (LOUNGE_X - 1.5, LOUNGE_Y + 2),
]
for fx, fy in lounge_frames:
    bpy.ops.mesh.primitive_cube_add(size=1)
    f = bpy.context.active_object
    f.scale = (0.035, 0.035, WALL_H/2)
    f.location = (fx, fy, WALL_H/2)
    f.data.materials.append(mat_metal_frame)

# L 型沙發
bpy.ops.mesh.primitive_cube_add(size=1)
s = bpy.context.active_object
s.scale = (1.2, 0.35, 0.28)
s.location = (LOUNGE_X, LOUNGE_Y - 0.5, 0.28)
s.data.materials.append(mat_sofa)

bpy.ops.mesh.primitive_cube_add(size=1)
s = bpy.context.active_object
s.scale = (1.2, 0.055, 0.2)
s.location = (LOUNGE_X, LOUNGE_Y - 0.72, 0.45)
s.data.materials.append(mat_sofa)

bpy.ops.mesh.primitive_cube_add(size=1)
s = bpy.context.active_object
s.scale = (0.35, 0.9, 0.28)
s.location = (LOUNGE_X + 0.65, LOUNGE_Y, 0.28)
s.data.materials.append(mat_sofa)

# 茶几
bpy.ops.mesh.primitive_cube_add(size=1)
ct = bpy.context.active_object
ct.scale = (0.45, 0.28, 0.012)
ct.location = (LOUNGE_X + 0.15, LOUNGE_Y + 0.22, 0.35)
ct.data.materials.append(mat_meeting_table)

for dx, dy in [(-0.18, -0.08), (-0.18, 0.08), (0.18, -0.08), (0.18, 0.08)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.01, depth=0.28)
    l = bpy.context.active_object
    l.location = (LOUNGE_X + 0.15 + dx, LOUNGE_Y + 0.22 + dy, 0.16)
    l.data.materials.append(mat_metal)

# ========== 工作站（模塊化佈局）==========

def create_workstation(x, y, facing='north', index=1):
    """工作站：facing 是使用者面向的方向"""
    
    angles = {'north': 0, 'south': math.pi, 'east': math.pi/2, 'west': -math.pi/2}
    rot = angles[facing]
    
    # 白色桌子
    bpy.ops.mesh.primitive_cube_add(size=1)
    d = bpy.context.active_object
    d.scale = (1.3, 0.65, 0.022)
    d.location = (x, y, 0.75)
    d.rotation_euler = (0, 0, rot)
    d.data.materials.append(mat_desktop)
    
    # 金屬桌腿
    for dx, dy in [(-0.55, -0.25), (-0.55, 0.25), (0.55, -0.25), (0.55, 0.25)]:
        bx = x + dx * math.cos(rot) - dy * math.sin(rot)
        by = y + dx * math.sin(rot) + dy * math.cos(rot)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.65)
        leg = bpy.context.active_object
        leg.location = (bx, by, 0.375)
        leg.data.materials.append(mat_metal)
    
    # 雙螢幕（黑色）
    for sx in [-0.3, 0.3]:
        bx = x + sx * math.cos(rot) + 0.35 * math.sin(rot)
        by = y + sx * math.sin(rot) + 0.35 * math.cos(rot)
        bpy.ops.mesh.primitive_cube_add(size=1)
        s = bpy.context.active_object
        s.scale = (0.5, 0.02, 0.28)
        s.location = (bx, by, 1.0)
        s.rotation_euler = (0, 0, rot + math.pi)
        s.data.materials.append(mat_screen)
    
    # 鍵盤
    kx = x - 0.3 * math.sin(rot)
    ky = y + 0.3 * math.cos(rot)
    bpy.ops.mesh.primitive_cube_add(size=1)
    kb = bpy.context.active_object
    kb.scale = (0.32, 0.1, 0.012)
    kb.location = (kx, ky, 0.43)
    kb.rotation_euler = (0, 0, rot)
    kb.data.materials.append(mat_plastic)
    
    # 滑鼠
    bpy.ops.mesh.primitive_cube_add(size=1)
    m = bpy.context.active_object
    m.scale = (0.05, 0.08, 0.02)
    m.location = (kx + 0.2*math.cos(rot), ky + 0.2*math.sin(rot), 0.43)
    m.rotation_euler = (0, 0, rot)
    m.data.materials.append(mat_plastic)
    
    # 黑色椅子（在桌子背面，面向桌子）
    chair_offset = -0.75
    chair_x = x + chair_offset * math.sin(rot)
    chair_y = y + chair_offset * math.cos(rot)
    chair_rot = rot
    
    # 座椅
    bpy.ops.mesh.primitive_cube_add(size=1)
    seat = bpy.context.active_object
    seat.scale = (0.4, 0.36, 0.07)
    seat.location = (chair_x, chair_y, 0.48)
    seat.rotation_euler = (0, 0, chair_rot)
    seat.data.materials.append(mat_seat)
    
    # 椅背
    back_x = chair_x - 0.16 * math.sin(chair_rot)
    back_y = chair_y - 0.16 * math.cos(chair_rot)
    bpy.ops.mesh.primitive_cube_add(size=1)
    back = bpy.context.active_object
    back.scale = (0.38, 0.05, 0.4)
    back.location = (back_x, back_y, 0.72)
    back.rotation_euler = (math.radians(8), 0, chair_rot)
    back.data.materials.append(mat_seat)
    
    # 椅子支柱
    bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.3)
    p = bpy.context.active_object
    p.location = (chair_x, chair_y, 0.32)
    p.data.materials.append(mat_metal)
    
    # 五星腳
    for i in range(5):
        angle = chair_rot + i * (2 * math.pi / 5)
        bpy.ops.mesh.primitive_cube_add(size=1)
        arm = bpy.context.active_object
        arm.scale = (0.2, 0.02, 0.015)
        arm.location = (chair_x + math.cos(angle)*0.1, chair_y + math.sin(angle)*0.1, 0.07)
        arm.rotation_euler = (0, 0, angle)
        arm.data.materials.append(mat_metal)
        
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.018)
        wh = bpy.context.active_object
        wh.location = (chair_x + math.cos(angle)*0.2, chair_y + math.sin(angle)*0.2, 0.018)
        wh.data.materials.append(mat_plastic)

# ========== 模塊化工作站佈局（對稱）==========

# 左側模塊（2 個工作站，面向窗戶）
create_workstation(-5.5, 1.2, facing='east', index=1)
create_workstation(-5.5, 3.8, facing='east', index=2)

# 中間工作站（單獨，面向門）
create_workstation(-1, 0, facing='north', index=3)

# 右側模塊（2 個工作站，面向窗戶）
create_workstation(5.5, 1.2, facing='west', index=4)
create_workstation(5.5, 3.8, facing='west', index=5)

# ========== 功能性裝飾（極簡）==========

# 大型綠植（角落）
for px, py in [(6, -6), (-6, 5.5)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.12)
    pot = bpy.context.active_object
    pot.location = (px, py, 0.56)
    pot.data.materials.append(mat_plant_pot)
    
    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.14)
    plant = bpy.context.active_object
    plant.location = (px, py, 0.8)
    plant.scale = (1, 1, 1.2)
    plant.data.materials.append(mat_plant)

# 簡約時鐘（後牆）
bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.015)
clock = bpy.context.active_object
clock.location = (0, -6.8, 2.3)
clock.rotation_euler = (math.pi/2, 0, 0)
clock.data.materials.append(mat_metal_frame)

print("✅ V13 完成！")
print("設計風格：專業室內設計（參考 Sketchfab 模型）")
print("特點：全高玻璃隔間、模塊化工作站、統一材質、極簡裝飾")
