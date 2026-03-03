#!/usr/bin/env python3
"""
創建鍵盤與滑鼠
"""

import sys

# 修復 numpy 路徑問題
user_site = '/home/rex/.local/lib/python3.10/site-packages'
if user_site not in sys.path:
    sys.path.insert(0, user_site)

import bpy
import math

# 清除場景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 清除孤立數據
for block in bpy.data.meshes:
    if block.users == 0:
        bpy.data.meshes.remove(block)
for block in bpy.data.materials:
    if block.users == 0:
        bpy.data.materials.remove(block)

# 創建材質
def create_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    return mat

# 材質定義
mat_keycap = create_material("Keycap_Dark", (0.15, 0.15, 0.15, 1), roughness=0.4)
mat_body = create_material("Keyboard_Body", (0.2, 0.2, 0.2, 1), roughness=0.3)
mat_mouse = create_material("Mouse_Dark", (0.12, 0.12, 0.12, 1), roughness=0.35, metallic=0.1)
mat_led = create_material("LED_Strip", (0.2, 0.5, 0.8, 1), roughness=0.2)

# ===== 鍵盤 =====

# 鍵盤主體
bpy.ops.mesh.primitive_cube_add(size=1)
kb_body = bpy.context.active_object
kb_body.name = "Keyboard_Body"
kb_body.scale = (0.35, 0.12, 0.015)
kb_body.location = (0, -0.25, 0.43)
kb_body.data.materials.append(mat_body)

# 鍵盤上蓋（帶傾斜）
bpy.ops.mesh.primitive_cube_add(size=1)
kb_top = bpy.context.active_object
kb_top.name = "Keyboard_Top"
kb_top.scale = (0.34, 0.11, 0.008)
kb_top.location = (0, -0.25, 0.44)
kb_top.rotation_euler = (math.radians(-5), 0, 0)  # 微微傾斜
kb_top.data.materials.append(mat_body)

# LED 燈條（底部）
bpy.ops.mesh.primitive_cube_add(size=1)
led_strip = bpy.context.active_object
led_strip.name = "LED_Strip"
led_strip.scale = (0.35, 0.005, 0.003)
led_strip.location = (0, -0.195, 0.425)
led_strip.data.materials.append(mat_led)

# 模擬按鍵（簡化版 - 4 排）
key_rows = [
    (0.14, -0.22, 0.448),   # 第一排（數字鍵）
    (0.14, -0.25, 0.447),   # 第二排（QWERTY）
    (0.14, -0.28, 0.446),   # 第三排（ASDF）
    (0.14, -0.31, 0.445),   # 第四排（ZXCV）
]

for row_idx, (x_scale, y_pos, z_pos) in enumerate(key_rows):
    # 創建一排按鍵（用一個長方體代替多個按鍵）
    bpy.ops.mesh.primitive_cube_add(size=1)
    key_row = bpy.context.active_object
    key_row.name = f"Key_Row_{row_idx+1}"
    key_row.scale = (x_scale, 0.02, 0.006)
    key_row.location = (0, y_pos, z_pos)
    key_row.data.materials.append(mat_keycap)

# 空白鍵（較大）
bpy.ops.mesh.primitive_cube_add(size=1)
spacebar = bpy.context.active_object
spacebar.name = "Spacebar"
spacebar.scale = (0.12, 0.02, 0.006)
spacebar.location = (0, -0.34, 0.444)
spacebar.data.materials.append(mat_keycap)

# ===== 滑鼠 =====

# 滑鼠主體（使用擠出建模會更真實，但這裡用簡化版）
bpy.ops.mesh.primitive_cube_add(size=1)
mouse_body = bpy.context.active_object
mouse_body.name = "Mouse_Body"
mouse_body.scale = (0.06, 0.11, 0.03)
mouse_body.location = (0.25, -0.25, 0.425)

# 應用縮放後調整形狀
bpy.context.view_layer.objects.active = mouse_body
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# 進入編輯模式調整形狀
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.transform.shrink_fatten(value=0.01)  # 讓滑鼠更圓滑
bpy.ops.object.mode_set(mode='OBJECT')

mouse_body.data.materials.append(mat_mouse)

# 滑鼠滾輪
bpy.ops.mesh.primitive_cylinder_add(radius=0.008, depth=0.015)
scroll_wheel = bpy.context.active_object
scroll_wheel.name = "Scroll_Wheel"
scroll_wheel.location = (0.25, -0.29, 0.45)
scroll_wheel.rotation_euler = (math.pi/2, 0, 0)
scroll_wheel.data.materials.append(mat_keycap)

# 滑鼠左右鍵（左鍵）
bpy.ops.mesh.primitive_cube_add(size=1)
lmb = bpy.context.active_object
lmb.name = "Left_Mouse_Button"
lmb.scale = (0.025, 0.03, 0.015)
lmb.location = (0.235, -0.31, 0.445)
lmb.data.materials.append(mat_keycap)

# 右鍵
bpy.ops.mesh.primitive_cube_add(size=1)
rmb = bpy.context.active_object
rmb.name = "Right_Mouse_Button"
rmb.scale = (0.025, 0.03, 0.015)
rmb.location = (0.265, -0.31, 0.445)
rmb.data.materials.append(mat_keycap)

print("✅ 鍵盤與滑鼠模型創建完成！")
