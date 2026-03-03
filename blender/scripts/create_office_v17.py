#!/usr/bin/env python3
"""
Claude Office V17 - 程序化 PBR 材質
提升畫質到寫實風格
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
for block in bpy.data.textures:
    if block.users == 0:
        bpy.data.textures.remove(block)

# ========== 程序化 PBR 材質 ==========

def create_wood_floor_material():
    """寫實木地板 PBR"""
    mat = bpy.data.materials.new(name="WoodFloor_PBR")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # 清除默認節點
    nodes.clear()
    
    # 創建節點
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (300, 0)
    
    # 木紋顏色
    color_ramp = nodes.new('ShaderNodeValToRGB')
    color_ramp.location = (0, 100)
    color_ramp.color_ramp.elements[0].color = (0.45, 0.32, 0.22, 1)  # 深木色
    color_ramp.color_ramp.elements[1].color = (0.65, 0.48, 0.32, 1)  # 淺木色
    
    # 紋理坐標
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-600, 0)
    
    # 木紋方向（沿 X 軸）
    separate_xyz = nodes.new('ShaderNodeSeparateXYZ')
    separate_xyz.location = (-400, 0)
    
    # 木紋條紋
    wave = nodes.new('ShaderNodeTexWave')
    wave.location = (-200, 0)
    wave.inputs['Scale'].default_value = 15.0
    wave.inputs['Distortion'].default_value = 2.0
    wave.inputs['Detail'].default_value = 5.0
    
    # 細微噪點
    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-200, -150)
    noise.inputs['Scale'].default_value = 50.0
    noise.inputs['Detail'].default_value = 10.0
    
    mix_rgb = nodes.new('ShaderNodeMixRGB')
    mix_rgb.location = (0, 0)
    mix_rgb.inputs['Fac'].default_value = 0.3
    
    # 凹凸貼圖
    bump = nodes.new('ShaderNodeBump')
    bump.location = (-100, -200)
    bump.inputs['Strength'].default_value = 0.05
    
    # 連接節點
    links.new(tex_coord.outputs['Generated'], separate_xyz.inputs['Vector'])
    links.new(separate_xyz.outputs['X'], wave.inputs['Vector'])
    links.new(tex_coord.outputs['Generated'], noise.inputs['Vector'])
    links.new(wave.outputs['Fac'], mix_rgb.inputs['Color1'])
    links.new(noise.outputs['Fac'], mix_rgb.inputs['Color2'])
    links.new(mix_rgb.outputs['Color'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], principled.inputs['Normal'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    # 設置參數
    principled.inputs['Roughness'].default_value = 0.35
    principled.inputs['Specular'].default_value = 0.4
    
    return mat

def create_glass_material():
    """寫實玻璃 PBR"""
    mat = bpy.data.materials.new(name="Glass_PBR")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    glass = nodes.new('ShaderNodeBsdfGlass')
    glass.location = (300, 0)
    glass.inputs['Color'].default_value = (0.85, 0.92, 0.98, 1)
    glass.inputs['Roughness'].default_value = 0.02
    glass.inputs['IOR'].default_value = 1.45
    
    # 混合透明（降低不透明度）
    transparent = nodes.new('ShaderNodeBsdfTransparent')
    transparent.location = (300, -200)
    
    mix_shader = nodes.new('ShaderNodeMixShader')
    mix_shader.location = (450, 0)
    mix_shader.inputs['Fac'].default_value = 0.15  # 15% 玻璃，85% 透明
    
    links.new(transparent.outputs['BSDF'], mix_shader.inputs[1])
    links.new(glass.outputs['BSDF'], mix_shader.inputs[2])
    links.new(mix_shader.outputs['Shader'], output.inputs['Surface'])
    
    mat.blend_method = 'BLEND'
    mat.shadow_method = 'CLIP'
    
    return mat

def create_metal_material():
    """寫實金屬 PBR"""
    mat = bpy.data.materials.new(name="Metal_PBR")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (300, 0)
    principled.inputs['Base Color'].default_value = (0.4, 0.4, 0.42, 1)
    principled.inputs['Metallic'].default_value = 0.9
    principled.inputs['Roughness'].default_value = 0.15
    
    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (0, -100)
    noise.inputs['Scale'].default_value = 100.0
    
    links.new(noise.outputs['Fac'], principled.inputs['Roughness'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

def create_fabric_material(color=(0.08, 0.08, 0.08, 1)):
    """寫實布料 PBR"""
    mat = bpy.data.materials.new(name="Fabric_PBR")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (300, 0)
    principled.inputs['Base Color'].default_value = color
    principled.inputs['Roughness'].default_value = 0.85
    
    # 布料紋理
    voronoi = nodes.new('ShaderNodeTexVoronoi')
    voronoi.location = (0, -100)
    voronoi.inputs['Scale'].default_value = 80.0
    
    bump = nodes.new('ShaderNodeBump')
    bump.location = (150, -200)
    bump.inputs['Strength'].default_value = 0.02
    
    links.new(voronoi.outputs['Distance'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], principled.inputs['Normal'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

def create_screen_material():
    """寫實螢幕 PBR（發光）"""
    mat = bpy.data.materials.new(name="Screen_PBR")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (300, 0)
    principled.inputs['Base Color'].default_value = (0.12, 0.15, 0.18, 1)
    principled.inputs['Emission'].default_value = (0.22, 0.27, 0.32, 1)
    principled.inputs['Roughness'].default_value = 0.08
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

def create_simple_material(name, color, roughness=0.5, metallic=0.0):
    """簡單材質（非關鍵物體用）"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    return mat

# 創建所有材質
mat_floor = create_wood_floor_material()
mat_wall = create_simple_material("Wall", (0.95, 0.95, 0.93, 1), roughness=0.9)
mat_glass = create_glass_material()
mat_metal_frame = create_metal_material()
mat_desktop = create_simple_material("Desktop", (0.98, 0.98, 0.96, 1), roughness=0.25)
mat_seat = create_fabric_material((0.08, 0.08, 0.08, 1))
mat_metal = create_metal_material()
mat_plastic = create_simple_material("Plastic", (0.05, 0.05, 0.05, 1), roughness=0.35)
mat_screen = create_screen_material()
mat_meeting_table = create_simple_material("Meeting_Table", (0.65, 0.55, 0.45, 1), roughness=0.35)
mat_whiteboard = create_simple_material("Whiteboard", (0.99, 0.99, 0.99, 1), roughness=0.25)
mat_sofa = create_fabric_material((0.28, 0.28, 0.3, 1))
mat_plant_pot = create_simple_material("Pot", (0.7, 0.5, 0.35, 1), roughness=0.6)
mat_plant = create_simple_material("Plant", (0.2, 0.4, 0.18, 1), roughness=0.5)
mat_printer = create_simple_material("Printer", (0.2, 0.2, 0.2, 1), roughness=0.3)
mat_water_dispenser = create_simple_material("WaterDispenser", (0.9, 0.9, 0.9, 1), roughness=0.2)
mat_cabinet = create_simple_material("Cabinet", (0.6, 0.6, 0.62, 1), roughness=0.3, metallic=0.4)
mat_trash_bin = create_simple_material("TrashBin", (0.25, 0.25, 0.25, 1), roughness=0.5)
mat_carpet = create_simple_material("Carpet", (0.55, 0.48, 0.42, 1), roughness=0.95)
mat_lamp = create_simple_material("Lamp", (0.15, 0.15, 0.15, 1), roughness=0.2, metallic=0.7)

# ========== 房間尺寸 ==========

ROOM_W = 16
ROOM_D = 14
WALL_H = 2.8

# ========== 地板（木質紋 PBR）==========

bpy.ops.mesh.primitive_plane_add(size=1)
floor = bpy.context.active_object
floor.scale = (ROOM_W + 2, ROOM_D + 2, 1)
floor.data.materials.append(mat_floor)

# ========== 牆壁（完全連接）==========

# 後牆
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (ROOM_W/2 + 0.15, 0.08, WALL_H/2)
w.location = (0, -ROOM_D/2 - 0.04, WALL_H/2)
w.data.materials.append(mat_wall)

# 前牆（完整，無空隙）
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (ROOM_W/2 - 1.2, 0.08, WALL_H/2)
w.location = (-ROOM_W/4 - 0.6, ROOM_D/2 + 0.04, WALL_H/2)
w.data.materials.append(mat_wall)

bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (ROOM_W/2 - 1.2, 0.08, WALL_H/2)
w.location = (ROOM_W/4 + 0.6, ROOM_D/2 + 0.04, WALL_H/2)
w.data.materials.append(mat_wall)

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

# ========== 主官辦公室隔間（中間工作站）==========

# 左面玻璃
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.015, 1.5, WALL_H/2)
w.location = (-2.5, 0, WALL_H/2)
w.data.materials.append(mat_glass)

# 右面玻璃
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.015, 1.5, WALL_H/2)
w.location = (0.5, 0, WALL_H/2)
w.data.materials.append(mat_glass)

# 黑色金屬框架
for fx, fy in [(-2.5, -1.5), (-2.5, 1.5), (0.5, -1.5), (0.5, 1.5)]:
    bpy.ops.mesh.primitive_cube_add(size=1)
    f = bpy.context.active_object
    f.scale = (0.035, 0.035, WALL_H/2)
    f.location = (fx, fy, WALL_H/2)
    f.data.materials.append(mat_metal_frame)

# ========== L 型玻璃隔間（後方）==========

# 短邊（左側）
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (0.015, 2.5, WALL_H/2)
w.location = (-4, -4.5, WALL_H/2)
w.data.materials.append(mat_glass)

# 長邊（後方）
bpy.ops.mesh.primitive_cube_add(size=1)
w = bpy.context.active_object
w.scale = (4.5, 0.015, WALL_H/2)
w.location = (0.5, -7, WALL_H/2)
w.data.materials.append(mat_glass)

# 黑色金屬框架
frame_positions = [
    (-4, -7), (-4, -2), (-4, -7),
    (-1, -7), (2, -7), (5, -7),
]
for fx, fy in frame_positions:
    bpy.ops.mesh.primitive_cube_add(size=1)
    f = bpy.context.active_object
    f.scale = (0.035, 0.035, WALL_H/2)
    f.location = (fx, fy, WALL_H/2)
    f.data.materials.append(mat_metal_frame)

# ========== 會議室（左後方）==========

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

bpy.ops.mesh.primitive_cube_add(size=1)
wb = bpy.context.active_object
wb.scale = (0.015, 0.75, 0.45)
wb.location = (-ROOM_W/2 + 0.12, MEETING_Y, 1.3)
wb.data.materials.append(mat_whiteboard)

# ========== 休息區（右後方）==========

LOUNGE_X, LOUNGE_Y = 3, -5

# 地毯
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

bpy.ops.mesh.primitive_cube_add(size=1)
s = bpy.context.active_object
s.scale = (1.0, 0.05, 0.18)
s.location = (LOUNGE_X, LOUNGE_Y - 0.6, 0.4)
s.data.materials.append(mat_sofa)

bpy.ops.mesh.primitive_cube_add(size=1)
s = bpy.context.active_object
s.scale = (0.3, 0.8, 0.25)
s.location = (LOUNGE_X + 0.55, LOUNGE_Y, 0.25)
s.data.materials.append(mat_sofa)

# 茶几
bpy.ops.mesh.primitive_cube_add(size=1)
ct = bpy.context.active_object
ct.scale = (0.4, 0.24, 0.012)
ct.location = (LOUNGE_X + 0.1, LOUNGE_Y + 0.18, 0.32)
ct.data.materials.append(mat_meeting_table)

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
    
    kx = x - 0.3 * math.sin(rot)
    ky = y + 0.3 * math.cos(rot)
    bpy.ops.mesh.primitive_cube_add(size=1)
    kb = bpy.context.active_object
    kb.scale = (0.32, 0.1, 0.012)
    kb.location = (kx, ky, 0.43)
    kb.rotation_euler = (0, 0, rot)
    kb.data.materials.append(mat_plastic)
    
    bpy.ops.mesh.primitive_cube_add(size=1)
    m = bpy.context.active_object
    m.scale = (0.05, 0.08, 0.02)
    m.location = (kx + 0.2*math.cos(rot), ky + 0.2*math.sin(rot), 0.43)
    m.rotation_euler = (0, 0, rot)
    m.data.materials.append(mat_plastic)
    
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
    
    back_x = chair_x - 0.16 * math.sin(chair_rot)
    back_y = chair_y - 0.16 * math.cos(chair_rot)
    bpy.ops.mesh.primitive_cube_add(size=1)
    back = bpy.context.active_object
    back.scale = (0.38, 0.05, 0.4)
    back.location = (back_x, back_y, 0.72)
    back.rotation_euler = (math.radians(8), 0, chair_rot)
    back.data.materials.append(mat_seat)
    
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
        
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.018)
        wh = bpy.context.active_object
        wh.location = (chair_x + math.cos(angle)*0.2, chair_y + math.sin(angle)*0.2, 0.018)
        wh.data.materials.append(mat_plastic)

# ========== 工作站佈局 ==========

create_workstation(-5.5, 2, facing='east', index=1)
create_workstation(-5.5, 4.5, facing='east', index=2)
create_workstation(-1, 0, facing='north', index=3)  # 主官辦公室
create_workstation(5.5, 2, facing='west', index=4)
create_workstation(5.5, 4.5, facing='west', index=5)

# ========== 印表機（左牆）==========

bpy.ops.mesh.primitive_cube_add(size=1)
printer = bpy.context.active_object
printer.scale = (0.28, 0.25, 0.18)
printer.location = (-ROOM_W/2 + 0.3, 3.5, 0.5)
printer.data.materials.append(mat_printer)

# ========== 飲水機（入口附近）==========

bpy.ops.mesh.primitive_cube_add(size=1)
water = bpy.context.active_object
water.scale = (0.25, 0.25, 0.85)
water.location = (6.5, 5.5, 0.45)
water.data.materials.append(mat_water_dispenser)

# ========== 文件櫃（左牆）==========

for i in range(3):
    bpy.ops.mesh.primitive_cube_add(size=1)
    cab = bpy.context.active_object
    cab.scale = (0.32, 0.38, 0.65)
    cab.location = (-ROOM_W/2 + 0.28, -1 + i * 0.45, 0.35)
    cab.data.materials.append(mat_cabinet)

# ========== 垃圾桶（工作站旁）==========

for bx, by in [(-6.5, 2), (-0.5, -1), (6.5, 2)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.25)
    trash = bpy.context.active_object
    trash.location = (bx, by, 0.15)
    trash.data.materials.append(mat_trash_bin)

# ========== 檯燈（桌子旁）==========

for lx, ly in [(-5, 1.5), (5, 1.5)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.4)
    lamp_pole = bpy.context.active_object
    lamp_pole.location = (lx, ly, 0.55)
    lamp_pole.data.materials.append(mat_metal)
    
    bpy.ops.mesh.primitive_cone_add(radius1=0.08, depth=0.06)
    lamp_shade = bpy.context.active_object
    lamp_shade.location = (lx, ly, 0.8)
    lamp_shade.data.materials.append(mat_lamp)

# ========== 大型綠植（角落）==========

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

# ========== 小型桌面盆栽 ==========

for dx, dy in [(-5.5, 2.5), (5.5, 2.5)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.04)
    dp = bpy.context.active_object
    dp.location = (dx + 0.5, dy - 0.25, 0.79)
    dp.data.materials.append(mat_plant_pot)
    
    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.04)
    pl = bpy.context.active_object
    pl.location = (dx + 0.5, dy - 0.25, 0.85)
    pl.data.materials.append(mat_plant)

# ========== 簡約時鐘 ==========

bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.015)
clock = bpy.context.active_object
clock.location = (0, -6.8, 2.3)
clock.rotation_euler = (math.pi/2, 0, 0)
clock.data.materials.append(mat_metal_frame)

# ========== 改進光照（模擬環境光）==========

# 啟用環境光遮蔽
bpy.context.scene.eevee.use_gtao = True
bpy.context.scene.eevee.gtao_distance = 10.0
bpy.context.scene.eevee.gtao_factor = 1.0

# 啟用泛光
bpy.context.scene.eevee.use_bloom = True
bpy.context.scene.eevee.bloom_intensity = 0.3

# 啟用屏幕空間反射
bpy.context.scene.eevee.use_ssr = True
bpy.context.scene.eevee.ssr_quality = 0.8

print("✅ V17 完成！")
print("程序化 PBR 材質：木地板、玻璃、金屬、布料、螢幕發光")
print("改進光照：環境光遮蔽、泛光、屏幕空間反射")
