#!/usr/bin/env python3
"""
Claude Office V25 - PBR 紋理版（修正導出）
使用 GLTF 兼容的材質節點設置
"""

import sys
user_site = '/home/rex/.local/lib/python3.10/site-packages'
if user_site not in sys.path:
    sys.path.insert(0, user_site)

import bpy
import math
import os

# 清除場景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

for block in bpy.data.meshes:
    if block.users == 0:
        bpy.data.meshes.remove(block)
for block in bpy.data.materials:
    if block.users == 0:
        bpy.data.materials.remove(block)
for block in bpy.data.images:
    if block.users == 0:
        bpy.data.images.remove(block)

# ========== 紋理路徑 ==========

TEXTURE_DIR = "/mnt/e_drive/claude-office/blender/textures"

# ========== GLTF 兼容的 PBR 材質 ==========

def create_gltf_pbr_material(name, color_image=None, normal_image=None, roughness_image=None,
                              base_color=(0.5, 0.5, 0.5, 1), roughness=0.5, metallic=0.0):
    """
    創建 GLTF 兼容的 PBR 材質
    關鍵：紋理節點必須使用特定的命名和連接方式
    """
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.blend_method = 'OPAQUE'
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # 清除默認節點
    nodes.clear()
    
    # 創建輸出節點
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    # 創建 Principled BSDF
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # 設置基礎顏色
    if color_image and os.path.exists(color_image):
        # 創建顏色紋理
        tex_color = nodes.new('ShaderNodeTexImage')
        tex_color.location = (-600, 200)
        tex_color.image = bpy.data.images.load(color_image)
        tex_color.label = "Base Color"
        links.new(tex_color.outputs['Color'], bsdf.inputs['Base Color'])
    else:
        bsdf.inputs['Base Color'].default_value = base_color
    
    # 設置法線
    if normal_image and os.path.exists(normal_image):
        tex_normal = nodes.new('ShaderNodeTexImage')
        tex_normal.location = (-600, -100)
        tex_normal.image = bpy.data.images.load(normal_image)
        tex_normal.label = "Normal"
        
        normal_map = nodes.new('ShaderNodeNormalMap')
        normal_map.location = (-300, -100)
        normal_map.inputs['Strength'].default_value = 1.0
        links.new(tex_normal.outputs['Color'], normal_map.inputs['Color'])
        links.new(normal_map.outputs['Normal'], bsdf.inputs['Normal'])
    
    # 設置粗糙度
    if roughness_image and os.path.exists(roughness_image):
        tex_roughness = nodes.new('ShaderNodeTexImage')
        tex_roughness.location = (-600, -300)
        tex_roughness.image = bpy.data.images.load(roughness_image)
        tex_roughness.label = "Roughness"
        # 粗糙度通常是灰度圖，需要從 Color 提取
        links.new(tex_roughness.outputs['Color'], bsdf.inputs['Roughness'])
    else:
        bsdf.inputs['Roughness'].default_value = roughness
    
    bsdf.inputs['Metallic'].default_value = metallic
    
    return mat

def create_simple_material(name, color, roughness=0.5, metallic=0.0):
    """簡單純色材質"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    return mat

# ========== 材質定義 ==========

print("正在創建 PBR 材質...")

# 地板 - 木地板 PBR
mat_floor = create_gltf_pbr_material(
    "WoodFloor_PBR",
    color_image=f"{TEXTURE_DIR}/wood_diffuse.jpg",
    normal_image=f"{TEXTURE_DIR}/wood_normal.jpg",
    roughness_image=f"{TEXTURE_DIR}/wood_roughness.jpg"
)
print("  ✓ 木地板 PBR")

# 椅座/沙發 - 布料 PBR（深色）
mat_seat = create_gltf_pbr_material(
    "Seat_Fabric_PBR",
    color_image=f"{TEXTURE_DIR}/fabric_diffuse.jpg",
    normal_image=f"{TEXTURE_DIR}/fabric_normal.jpg",
    roughness_image=f"{TEXTURE_DIR}/fabric_roughness.jpg"
)
print("  ✓ 椅座布料 PBR")

# 沙發 - 同樣的布料
mat_sofa = mat_seat  # 複用椅座材質
print("  ✓ 沙發布料 PBR（複用）")

# 其他材質（純色）
mat_wall = create_simple_material("Wall", (0.92, 0.92, 0.9, 1), roughness=0.95)
mat_glass = create_simple_material("Glass", (0.85, 0.92, 0.98, 0.15), roughness=0.1)
mat_metal_frame = create_simple_material("Metal_Frame", (0.08, 0.08, 0.08, 1), roughness=0.5, metallic=0.4)
mat_desktop = create_simple_material("Desktop", (0.95, 0.95, 0.93, 1), roughness=0.6)
mat_metal = create_simple_material("Metal", (0.35, 0.35, 0.37, 1), roughness=0.4, metallic=0.5)
mat_plastic = create_simple_material("Plastic", (0.04, 0.04, 0.04, 1), roughness=0.7)
mat_screen = create_simple_material("Screen", (0.1, 0.13, 0.16, 1), roughness=0.4)
mat_meeting_table = create_simple_material("Meeting_Table", (0.55, 0.45, 0.38, 1), roughness=0.6)
mat_whiteboard = create_simple_material("Whiteboard", (0.98, 0.98, 0.98, 1), roughness=0.5)
mat_plant_pot = create_simple_material("Pot", (0.65, 0.45, 0.32, 1), roughness=0.8)
mat_plant = create_simple_material("Plant", (0.18, 0.38, 0.15, 1), roughness=0.8)
mat_printer = create_simple_material("Printer", (0.18, 0.18, 0.18, 1), roughness=0.6)
mat_water_dispenser = create_simple_material("WaterDispenser", (0.88, 0.88, 0.88, 1), roughness=0.5)
mat_cabinet = create_simple_material("Cabinet", (0.55, 0.55, 0.57, 1), roughness=0.6, metallic=0.2)
mat_trash_bin = create_simple_material("TrashBin", (0.22, 0.22, 0.22, 1), roughness=0.7)
mat_carpet = create_simple_material("Carpet", (0.5, 0.43, 0.38, 1), roughness=0.98)
mat_lamp = create_simple_material("Lamp", (0.12, 0.12, 0.12, 1), roughness=0.5, metallic=0.3)

print("✅ 材質創建完成！")

# ========== 圓角函數 ==========

def add_bevel(obj, segments=4, width=0.02):
    bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel.segments = segments
    bevel.width = width
    bevel.limit_method = 'ANGLE'
    bevel.angle_limit = math.radians(35)
    bevel.use_clamp_overlap = True
    return bevel

# ========== 房間尺寸 ==========

ROOM_W = 16
ROOM_D = 14
WALL_H = 2.8

# ========== 地板 ==========

bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False)
floor = bpy.context.active_object
floor.scale = (ROOM_W + 2, ROOM_D + 2, 1)
floor.data.materials.append(mat_floor)

# 為地板設置 UV 縮放（讓紋理重複）
bpy.context.view_layer.objects.active = floor
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
# 縮放 UV 讓紋理重複更多次
bpy.ops.transform.resize(value=(8.0, 8.0, 1.0))
bpy.ops.object.mode_set(mode='OBJECT')

# ========== 牆壁 ==========

# 後牆
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (ROOM_W/2 + 0.15, 0.08, WALL_H/2)
w.location = (0, -ROOM_D/2 - 0.04, WALL_H/2)
w.data.materials.append(mat_wall)
add_bevel(w, segments=3, width=0.01)

# 前牆
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (ROOM_W/2 - 1.2, 0.08, WALL_H/2)
w.location = (-ROOM_W/4 - 0.6, ROOM_D/2 + 0.04, WALL_H/2)
w.data.materials.append(mat_wall)
add_bevel(w, segments=3, width=0.01)

bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (ROOM_W/2 - 1.2, 0.08, WALL_H/2)
w.location = (ROOM_W/4 + 0.6, ROOM_D/2 + 0.04, WALL_H/2)
w.data.materials.append(mat_wall)
add_bevel(w, segments=3, width=0.01)

bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (1.2, 0.08, (WALL_H - 2.2)/2)
w.location = (0, ROOM_D/2 + 0.04, 2.2 + (WALL_H - 2.2)/2)
w.data.materials.append(mat_wall)
add_bevel(w, segments=3, width=0.01)

# 左牆
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.08, ROOM_D/2, WALL_H/2)
w.location = (-ROOM_W/2 - 0.04, 0, WALL_H/2)
w.data.materials.append(mat_wall)
add_bevel(w, segments=3, width=0.01)

# 右牆
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.08, ROOM_D/2, WALL_H/2)
w.location = (ROOM_W/2 + 0.04, 0, WALL_H/2)
w.data.materials.append(mat_wall)
add_bevel(w, segments=3, width=0.01)

# 落地窗
bpy.ops.mesh.primitive_cube_add(size=1)
window = bpy.context.active_object
window.scale = (0.02, 5, WALL_H/2 - 0.15)
window.location = (ROOM_W/2 + 0.07, 0, WALL_H/2)
window.data.materials.append(mat_glass)
add_bevel(window, segments=3, width=0.008)

# ========== 主官辦公室隔間 ==========

for fx, fy in [(-2.5, -1.5), (-2.5, 1.5), (0.5, -1.5), (0.5, 1.5)]:
    bpy.ops.mesh.primitive_cube_add(size=1)
    f = bpy.context.active_object
    f.scale = (0.035, 0.035, WALL_H/2)
    f.location = (fx, fy, WALL_H/2)
    f.data.materials.append(mat_metal_frame)
    add_bevel(f, segments=3, width=0.01)

bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.015, 1.5, WALL_H/2)
w.location = (-2.5, 0, WALL_H/2)
w.data.materials.append(mat_glass)
add_bevel(w, segments=3, width=0.008)

bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.015, 1.5, WALL_H/2)
w.location = (0.5, 0, WALL_H/2)
w.data.materials.append(mat_glass)
add_bevel(w, segments=3, width=0.008)

# ========== L 型玻璃隔間 ==========

bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.015, 2.5, WALL_H/2)
w.location = (-4, -4.5, WALL_H/2)
w.data.materials.append(mat_glass)
add_bevel(w, segments=3, width=0.008)

bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (4.5, 0.015, WALL_H/2)
w.location = (0.5, -7, WALL_H/2)
w.data.materials.append(mat_glass)
add_bevel(w, segments=3, width=0.008)

frame_positions = [(-4, -7), (-4, -2), (-1, -7), (2, -7), (5, -7)]
for fx, fy in frame_positions:
    bpy.ops.mesh.primitive_cube_add(size=1)
    f = bpy.context.active_object
    f.scale = (0.035, 0.035, WALL_H/2)
    f.location = (fx, fy, WALL_H/2)
    f.data.materials.append(mat_metal_frame)
    add_bevel(f, segments=3, width=0.01)

# ========== 會議室 ==========

MEETING_X, MEETING_Y = -2, -5

bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=0.035)
t = bpy.context.active_object
t.scale = (1, 0.6, 1)
t.location = (MEETING_X, MEETING_Y, 0.75)
t.data.materials.append(mat_meeting_table)

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
    add_bevel(c, segments=4, width=0.02)

bpy.ops.mesh.primitive_cube_add(size=1)
wb = bpy.context.active_object
wb.scale = (0.015, 0.75, 0.45)
wb.location = (-ROOM_W/2 + 0.12, MEETING_Y, 1.3)
wb.data.materials.append(mat_whiteboard)
add_bevel(wb, segments=2, width=0.003)

# ========== 休息區 ==========

LOUNGE_X, LOUNGE_Y = 3, -5

bpy.ops.mesh.primitive_plane_add(size=1)
c = bpy.context.active_object
c.scale = (1.8, 1.8, 1)
c.location = (LOUNGE_X, LOUNGE_Y, 0.01)
c.data.materials.append(mat_carpet)

# L 型沙發
bpy.ops.mesh.primitive_cube_add(size=1)
s = bpy.context.active_object
s.scale = (1.0, 0.3, 0.25)
s.location = (LOUNGE_X, LOUNGE_Y - 0.4, 0.25)
s.data.materials.append(mat_sofa)
add_bevel(s, segments=5, width=0.05)

bpy.ops.mesh.primitive_cube_add(size=1)
s = bpy.context.active_object
s.scale = (1.0, 0.05, 0.18)
s.location = (LOUNGE_X, LOUNGE_Y - 0.6, 0.4)
s.data.materials.append(mat_sofa)
add_bevel(s, segments=4, width=0.025)

bpy.ops.mesh.primitive_cube_add(size=1)
s = bpy.context.active_object
s.scale = (0.3, 0.8, 0.25)
s.location = (LOUNGE_X + 0.55, LOUNGE_Y, 0.25)
s.data.materials.append(mat_sofa)
add_bevel(s, segments=5, width=0.05)

bpy.ops.mesh.primitive_cube_add(size=1)
ct = bpy.context.active_object
ct.scale = (0.4, 0.24, 0.012)
ct.location = (LOUNGE_X + 0.1, LOUNGE_Y + 0.18, 0.32)
ct.data.materials.append(mat_meeting_table)
add_bevel(ct, segments=4, width=0.02)

for dx, dy in [(-0.15, -0.06), (-0.15, 0.06), (0.15, -0.06), (0.15, 0.06)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.01, depth=0.25)
    l = bpy.context.active_object
    l.location = (LOUNGE_X + 0.1 + dx, LOUNGE_Y + 0.18 + dy, 0.14)
    l.data.materials.append(mat_metal)

# ========== 工作站 ==========

def create_workstation(x, y, facing='north', index=1):
    angles = {'north': 0, 'south': math.pi, 'east': math.pi/2, 'west': -math.pi/2}
    rot = angles[facing]

    bpy.ops.mesh.primitive_cube_add(size=1)
    d = bpy.context.active_object
    d.scale = (1.3, 0.65, 0.022)
    d.location = (x, y, 0.75)
    d.rotation_euler = (0, 0, rot)
    d.data.materials.append(mat_desktop)
    add_bevel(d, segments=5, width=0.025)

    for dx, dy in [(-0.55, -0.25), (-0.55, 0.25), (0.55, -0.25), (0.55, 0.25)]:
        bx = x + dx * math.cos(rot) - dy * math.sin(rot)
        by = y + dx * math.sin(rot) + dy * math.cos(rot)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.65)
        leg = bpy.context.active_object
        leg.location = (bx, by, 0.375)
        leg.data.materials.append(mat_metal)

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

    kx = x - 0.3 * math.sin(rot)
    ky = y + 0.3 * math.cos(rot)
    bpy.ops.mesh.primitive_cube_add(size=1)
    kb = bpy.context.active_object
    kb.scale = (0.32, 0.1, 0.012)
    kb.location = (kx, ky, 0.43)
    kb.rotation_euler = (0, 0, rot)
    kb.data.materials.append(mat_plastic)
    add_bevel(kb, segments=3, width=0.01)

    bpy.ops.mesh.primitive_cube_add(size=1)
    m = bpy.context.active_object
    m.scale = (0.05, 0.08, 0.02)
    m.location = (kx + 0.2*math.cos(rot), ky + 0.2*math.sin(rot), 0.43)
    m.rotation_euler = (0, 0, rot)
    m.data.materials.append(mat_plastic)
    add_bevel(m, segments=3, width=0.01)

    chair_offset = -0.75
    chair_x = x + chair_offset * math.sin(rot)
    chair_y = y + chair_offset * math.cos(rot)
    chair_rot = rot

    bpy.ops.mesh.primitive_cube_add(size=1)
    seat = bpy.context.active_object
    seat.scale = (0.4, 0.36, 0.07)
    seat.location = (chair_x, chair_y, 0.48)
    seat.rotation_euler = (0, 0, chair_rot)
    seat.data.materials.append(mat_seat)
    add_bevel(seat, segments=5, width=0.03)

    back_x = chair_x - 0.16 * math.sin(chair_rot)
    back_y = chair_y - 0.16 * math.cos(chair_rot)
    bpy.ops.mesh.primitive_cube_add(size=1)
    back = bpy.context.active_object
    back.scale = (0.38, 0.05, 0.4)
    back.location = (back_x, back_y, 0.72)
    back.rotation_euler = (math.radians(8), 0, chair_rot)
    back.data.materials.append(mat_seat)
    add_bevel(back, segments=4, width=0.02)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.3)
    p = bpy.context.active_object
    p.location = (chair_x, chair_y, 0.32)
    p.data.materials.append(mat_metal)

    for i in range(5):
        angle = chair_rot + i * (2 * math.pi / 5)
        bpy.ops.mesh.primitive_cube_add(size=1)
        arm = bpy.context.active_object
        arm.scale = (0.2, 0.02, 0.015)
        arm.location = (chair_x + math.cos(angle)*0.1, chair_y + math.sin(angle)*0.1, 0.07)
        arm.rotation_euler = (0, 0, angle)
        arm.data.materials.append(mat_metal)
        add_bevel(arm, segments=3, width=0.008)

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

bpy.ops.mesh.primitive_cube_add(size=1)
printer = bpy.context.active_object
printer.scale = (0.28, 0.25, 0.18)
printer.location = (-ROOM_W/2 + 0.3, 3.5, 0.5)
printer.data.materials.append(mat_printer)
add_bevel(printer, segments=4, width=0.02)

bpy.ops.mesh.primitive_cube_add(size=1)
water = bpy.context.active_object
water.scale = (0.25, 0.25, 0.85)
water.location = (6.5, 5.5, 0.45)
water.data.materials.append(mat_water_dispenser)
add_bevel(water, segments=4, width=0.02)

for i in range(3):
    bpy.ops.mesh.primitive_cube_add(size=1)
    cab = bpy.context.active_object
    cab.scale = (0.32, 0.38, 0.65)
    cab.location = (-ROOM_W/2 + 0.28, -1 + i * 0.45, 0.35)
    cab.data.materials.append(mat_cabinet)
    add_bevel(cab, segments=4, width=0.02)

for bx, by in [(-6.5, 2), (-0.5, -1), (6.5, 2)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.25)
    trash = bpy.context.active_object
    trash.location = (bx, by, 0.15)
    trash.data.materials.append(mat_trash_bin)

for lx, ly in [(-5, 1.5), (5, 1.5)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.4)
    lamp_pole = bpy.context.active_object
    lamp_pole.location = (lx, ly, 0.55)
    lamp_pole.data.materials.append(mat_metal)

    bpy.ops.mesh.primitive_cone_add(radius1=0.08, depth=0.06)
    lamp_shade = bpy.context.active_object
    lamp_shade.location = (lx, ly, 0.8)
    lamp_shade.data.materials.append(mat_lamp)

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

for dx, dy in [(-5.5, 2.5), (5.5, 2.5)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.04)
    dp = bpy.context.active_object
    dp.location = (dx + 0.5, dy - 0.25, 0.79)
    dp.data.materials.append(mat_plant_pot)

    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.04)
    pl = bpy.context.active_object
    pl.location = (dx + 0.5, dy - 0.25, 0.85)
    pl.data.materials.append(mat_plant)

bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.015)
clock = bpy.context.active_object
clock.location = (0, -6.8, 2.3)
clock.rotation_euler = (math.pi/2, 0, 0)
clock.data.materials.append(mat_metal_frame)

print("✅ V25 場景完成！")

# ========== 應用所有 Modifiers ==========

print("正在應用所有 modifiers...")
for obj in bpy.data.objects:
    if obj.type == 'MESH' and obj.modifiers:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        for modifier in obj.modifiers:
            try:
                bpy.ops.object.modifier_apply(modifier=modifier.name)
            except Exception as e:
                pass

print("✅ V25 完成！")
print("已應用 PBR 紋理到地板、椅座、沙發")
print("紋理來源：AmbientCG (WoodFloor054, Fabric045)")
