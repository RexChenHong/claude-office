import bpy
import math
from mathutils import Quaternion

print("\n=== 正確方法：使用四元數（不改變 rotation_mode）===")

# 載入原始模型
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

source = '/mnt/e_drive/claude-office/assets/characters/3d/realistic_female_character__game-ready_3d_model.glb'
bpy.ops.import_scene.gltf(filepath=source)

# 找骨骼
armature = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
print(f"骨骼: {armature.name}")

# 找主要骨骼（不改變 rotation_mode！）
bones = {}
for b in armature.pose.bones:
    n = b.name.lower()
    if 'hip' in n and 'pelvis' not in n and 'bone' not in n:
        bones['hip'] = b
    elif 'spine01' in n:
        bones['spine'] = b
    elif 'spine02' in n:
        bones['spine2'] = b
    elif 'head' in n:
        bones['head'] = b
    elif 'l_thigh' in n:
        bones['l_thigh'] = b
    elif 'l_calf' in n:
        bones['l_calf'] = b
    elif 'r_thigh' in n:
        bones['r_thigh'] = b
    elif 'r_calf' in n:
        bones['r_calf'] = b
    elif 'l_upperarm' in n:
        bones['l_upperarm'] = b
    elif 'l_forearm' in n:
        bones['l_forearm'] = b
    elif 'r_upperarm' in n:
        bones['r_upperarm'] = b
    elif 'r_forearm' in n:
        bones['r_forearm'] = b

print(f"✅ 找到 {len(bones)} 個控制骨骼")

# 切換到姿勢模式
bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode='POSE')

if not armature.animation_data:
    armature.animation_data_create()

# ============================================
# 製作 Idle 動畫（使用四元數）
# ============================================
print("\n【1/5】製作 Idle 動畫...")

action_idle = bpy.data.actions.new(name="Custom_Idle")
armature.animation_data.action = action_idle

bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = 120

for frame in range(0, 121, 10):
    bpy.context.scene.frame_set(frame)
    t = frame / 120

    # 輕微呼吸（使用四元數）
    if 'spine2' in bones:
        # 創建一個輕微的 X 軸旋轉
        q = Quaternion((1, 0.03 * math.sin(t * 2 * math.pi), 0, 0))
        bones['spine2'].rotation_quaternion = q
        bones['spine2'].keyframe_insert(data_path="rotation_quaternion", frame=frame)

    # 輕微上下移動（位置是通用的）
    if 'hip' in bones:
        bones['hip'].location = (0, 0.02 * math.sin(t * 2 * math.pi), 0)
        bones['hip'].keyframe_insert(data_path="location", frame=frame)

print("✅ Idle 完成")

# ============================================
# 製作 Walk 動畫（使用四元數）
# ============================================
print("\n【2/5】製作 Walk 動畫...")

action_walk = bpy.data.actions.new(name="Custom_Walk")
armature.animation_data.action = action_walk

bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = 48

for frame in range(0, 49, 4):
    bpy.context.scene.frame_set(frame)
    t = frame / 48 * 2 * math.pi

    if 'hip' in bones:
        bones['hip'].location = (0, 0.03 * abs(math.sin(t)), 0)
        bones['hip'].keyframe_insert(data_path="location", frame=frame)

    # 大腿旋轉（使用四元數）
    if 'l_thigh' in bones:
        q = Quaternion((1, 0.4 * math.sin(t), 0, 0))
        bones['l_thigh'].rotation_quaternion = q
        bones['l_thigh'].keyframe_insert(data_path="rotation_quaternion", frame=frame)

    if 'r_thigh' in bones:
        q = Quaternion((1, 0.4 * math.sin(t + math.pi), 0, 0))
        bones['r_thigh'].rotation_quaternion = q
        bones['r_thigh'].keyframe_insert(data_path="rotation_quaternion", frame=frame)

    # 小腿旋轉
    if 'l_calf' in bones:
        angle = max(0, -0.5 * math.sin(t + 0.5))
        q = Quaternion((1, angle, 0, 0))
        bones['l_calf'].rotation_quaternion = q
        bones['l_calf'].keyframe_insert(data_path="rotation_quaternion", frame=frame)

    if 'r_calf' in bones:
        angle = max(0, -0.5 * math.sin(t + math.pi + 0.5))
        q = Quaternion((1, angle, 0, 0))
        bones['r_calf'].rotation_quaternion = q
        bones['r_calf'].keyframe_insert(data_path="rotation_quaternion", frame=frame)

print("✅ Walk 完成")

# ============================================
# 製作 Type 動畫（使用四元數）
# ============================================
print("\n【3/5】製作 Type 動畫...")

action_type = bpy.data.actions.new(name="Custom_Type")
armature.animation_data.action = action_type

bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = 60

for frame in range(0, 61, 6):
    bpy.context.scene.frame_set(frame)
    t = frame / 60 * 2 * math.pi

    if 'spine' in bones:
        q = Quaternion((1, 0.2, 0, 0))
        bones['spine'].rotation_quaternion = q
        bones['spine'].keyframe_insert(data_path="rotation_quaternion", frame=frame)

    if 'l_upperarm' in bones:
        q = Quaternion((1, -0.8, 0.3, 0))
        bones['l_upperarm'].rotation_quaternion = q
        bones['l_upperarm'].keyframe_insert(data_path="rotation_quaternion", frame=frame)

    if 'l_forearm' in bones:
        angle = -0.5 + 0.1 * math.sin(t * 3)
        q = Quaternion((1, angle, 0, 0))
        bones['l_forearm'].rotation_quaternion = q
        bones['l_forearm'].keyframe_insert(data_path="rotation_quaternion", frame=frame)

    if 'r_upperarm' in bones:
        q = Quaternion((1, -0.8, -0.3, 0))
        bones['r_upperarm'].rotation_quaternion = q
        bones['r_upperarm'].keyframe_insert(data_path="rotation_quaternion", frame=frame)

    if 'r_forearm' in bones:
        angle = -0.5 + 0.1 * math.sin(t * 3 + math.pi)
        q = Quaternion((1, angle, 0, 0))
        bones['r_forearm'].rotation_quaternion = q
        bones['r_forearm'].keyframe_insert(data_path="rotation_quaternion", frame=frame)

print("✅ Type 完成")

# 回到物件模式
bpy.ops.object.mode_set(mode='OBJECT')

print(f"\n總動畫: {len(bpy.data.actions)} 個")

# 導出（保留原始動畫！）
output = '/mnt/e_drive/claude-office/blender/exports/character_with_custom_quaternion.glb'
print(f"\n開始導出到: {output}")

bpy.ops.export_scene.gltf(
    filepath=output,
    export_format='GLB',
    export_cameras=False,
    export_lights=False,
    export_animations=True,
    export_skins=True,
    export_morph=False
)

import os
size = os.path.getsize(output) / 1024 / 1024
print(f"\n✅ 導出成功！大小: {size:.1f} MB")
print("\n包含動畫:")
for a in bpy.data.actions:
    print(f"  - {a.name}")

print("\n✅ 關鍵：使用四元數，保留原始動畫！")
