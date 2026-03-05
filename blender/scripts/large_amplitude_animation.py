import bpy
import math
from mathutils import Quaternion, Vector, Euler

print("\n=== 大幅度動畫 + 正確四元數 ===")

# 載入原始模型
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

source = '/mnt/e_drive/claude-office/assets/characters/3d/realistic_female_character__game-ready_3d_model.glb'
bpy.ops.import_scene.gltf(filepath=source)

# 找骨骼
armature = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
print(f"✅ 骨骼: {armature.name}")

# 找主要骨骼
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
# Idle 動畫（大幅度）
# ============================================
print("\n【1/5】Idle 動畫（大幅度）...")

action_idle = bpy.data.actions.new(name="Idle")
armature.animation_data.action = action_idle

bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = 120

for frame in range(0, 121, 10):
    bpy.context.scene.frame_set(frame)
    t = frame / 120

    # 清除變換
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.transforms_clear()

    # 大幅度呼吸（X軸旋轉 15 度）
    if 'spine2' in bones:
        angle_deg = 15 * math.sin(t * 2 * math.pi)
        euler = Euler((math.radians(angle_deg), 0, 0), 'XYZ')
        bones['spine2'].rotation_quaternion = euler.to_quaternion()
        bones['spine2'].keyframe_insert(data_path="rotation_quaternion", frame=frame, group="Idle")

    # 大幅度上下移動（0.1 米）
    if 'hip' in bones:
        bones['hip'].location = Vector((0, 0.1 * math.sin(t * 2 * math.pi), 0))
        bones['hip'].keyframe_insert(data_path="location", frame=frame, group="Idle")

    # 輕微搖擺（Z軸旋轉 10 度）
    if 'hip' in bones:
        angle_deg = 10 * math.sin(t * 2 * math.pi)
        euler = Euler((0, 0, math.radians(angle_deg)), 'XYZ')
        bones['hip'].rotation_quaternion = euler.to_quaternion()
        bones['hip'].keyframe_insert(data_path="rotation_quaternion", frame=frame, group="Idle")

print("✅ Idle 完成")

# ============================================
# Walk 動畫（大幅度）
# ============================================
print("\n【2/5】Walk 動畫（大幅度）...")

action_walk = bpy.data.actions.new(name="Walk")
armature.animation_data.action = action_walk

bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = 48

for frame in range(0, 49, 4):
    bpy.context.scene.frame_set(frame)
    t = frame / 48 * 2 * math.pi

    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.transforms_clear()

    # 髖部上下（0.15 米）
    if 'hip' in bones:
        bones['hip'].location = Vector((0, 0.15 * abs(math.sin(t)), 0))
        bones['hip'].keyframe_insert(data_path="location", frame=frame, group="Walk")

    # 大腿旋轉（45 度）
    if 'l_thigh' in bones:
        angle_deg = 45 * math.sin(t)
        euler = Euler((math.radians(angle_deg), 0, 0), 'XYZ')
        bones['l_thigh'].rotation_quaternion = euler.to_quaternion()
        bones['l_thigh'].keyframe_insert(data_path="rotation_quaternion", frame=frame, group="Walk")

    if 'r_thigh' in bones:
        angle_deg = 45 * math.sin(t + math.pi)
        euler = Euler((math.radians(angle_deg), 0, 0), 'XYZ')
        bones['r_thigh'].rotation_quaternion = euler.to_quaternion()
        bones['r_thigh'].keyframe_insert(data_path="rotation_quaternion", frame=frame, group="Walk")

    # 小腿旋轉（60 度）
    if 'l_calf' in bones:
        angle_deg = max(0, 60 * math.sin(t + 0.5))
        euler = Euler((math.radians(angle_deg), 0, 0), 'XYZ')
        bones['l_calf'].rotation_quaternion = euler.to_quaternion()
        bones['l_calf'].keyframe_insert(data_path="rotation_quaternion", frame=frame, group="Walk")

    if 'r_calf' in bones:
        angle_deg = max(0, 60 * math.sin(t + math.pi + 0.5))
        euler = Euler((math.radians(angle_deg), 0, 0), 'XYZ')
        bones['r_calf'].rotation_quaternion = euler.to_quaternion()
        bones['r_calf'].keyframe_insert(data_path="rotation_quaternion", frame=frame, group="Walk")

    # 手臂擺動（30 度）
    if 'l_upperarm' in bones:
        angle_deg = 30 * math.sin(t + math.pi)
        euler = Euler((math.radians(angle_deg), 0, 0), 'XYZ')
        bones['l_upperarm'].rotation_quaternion = euler.to_quaternion()
        bones['l_upperarm'].keyframe_insert(data_path="rotation_quaternion", frame=frame, group="Walk")

    if 'r_upperarm' in bones:
        angle_deg = 30 * math.sin(t)
        euler = Euler((math.radians(angle_deg), 0, 0), 'XYZ')
        bones['r_upperarm'].rotation_quaternion = euler.to_quaternion()
        bones['r_upperarm'].keyframe_insert(data_path="rotation_quaternion", frame=frame, group="Walk")

print("✅ Walk 完成")

# ============================================
# Type 動畫（大幅度）
# ============================================
print("\n【3/5】Type 動畫（大幅度）...")

action_type = bpy.data.actions.new(name="Type")
armature.animation_data.action = action_type

bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = 60

for frame in range(0, 61, 6):
    bpy.context.scene.frame_set(frame)
    t = frame / 60 * 2 * math.pi

    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.transforms_clear()

    # 身體前傾（20 度）
    if 'spine' in bones:
        euler = Euler((math.radians(20), 0, 0), 'XYZ')
        bones['spine'].rotation_quaternion = euler.to_quaternion()
        bones['spine'].keyframe_insert(data_path="rotation_quaternion", frame=frame, group="Type")

    # 手臂前伸（60 度）
    if 'l_upperarm' in bones:
        euler = Euler((math.radians(-60), math.radians(20), 0), 'XYZ')
        bones['l_upperarm'].rotation_quaternion = euler.to_quaternion()
        bones['l_upperarm'].keyframe_insert(data_path="rotation_quaternion", frame=frame, group="Type")

    if 'l_forearm' in bones:
        angle_deg = -90 + 15 * math.sin(t * 3)
        euler = Euler((math.radians(angle_deg), 0, 0), 'XYZ')
        bones['l_forearm'].rotation_quaternion = euler.to_quaternion()
        bones['l_forearm'].keyframe_insert(data_path="rotation_quaternion", frame=frame, group="Type")

    if 'r_upperarm' in bones:
        euler = Euler((math.radians(-60), math.radians(-20), 0), 'XYZ')
        bones['r_upperarm'].rotation_quaternion = euler.to_quaternion()
        bones['r_upperarm'].keyframe_insert(data_path="rotation_quaternion", frame=frame, group="Type")

    if 'r_forearm' in bones:
        angle_deg = -90 + 15 * math.sin(t * 3 + math.pi)
        euler = Euler((math.radians(angle_deg), 0, 0), 'XYZ')
        bones['r_forearm'].rotation_quaternion = euler.to_quaternion()
        bones['r_forearm'].keyframe_insert(data_path="rotation_quaternion", frame=frame, group="Type")

print("✅ Type 完成")

# ============================================
# SitDown 動畫（大幅度）
# ============================================
print("\n【4/5】SitDown 動畫（大幅度）...")

action_sit = bpy.data.actions.new(name="SitDown")
armature.animation_data.action = action_sit

bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = 60

keyframes = [
    (0, 0, 0, 0, 0),
    (30, -0.3, 0.6, 70, 15),
    (60, -0.4, 0.8, 90, 25),
]

for frame, hip_x, hip_y, knee_deg, spine_deg in keyframes:
    bpy.context.scene.frame_set(frame)
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.transforms_clear()

    if 'hip' in bones:
        bones['hip'].location = Vector((hip_x, hip_y, 0))
        bones['hip'].keyframe_insert(data_path="location", frame=frame, group="SitDown")

    if 'l_thigh' in bones:
        euler = Euler((math.radians(-knee_deg), 0, 0), 'XYZ')
        bones['l_thigh'].rotation_quaternion = euler.to_quaternion()
        bones['l_thigh'].keyframe_insert(data_path="rotation_quaternion", frame=frame, group="SitDown")

    if 'r_thigh' in bones:
        euler = Euler((math.radians(-knee_deg), 0, 0), 'XYZ')
        bones['r_thigh'].rotation_quaternion = euler.to_quaternion()
        bones['r_thigh'].keyframe_insert(data_path="rotation_quaternion", frame=frame, group="SitDown")

    if 'l_calf' in bones:
        euler = Euler((math.radians(knee_deg * 1.5), 0, 0), 'XYZ')
        bones['l_calf'].rotation_quaternion = euler.to_quaternion()
        bones['l_calf'].keyframe_insert(data_path="rotation_quaternion", frame=frame, group="SitDown")

    if 'r_calf' in bones:
        euler = Euler((math.radians(knee_deg * 1.5), 0, 0), 'XYZ')
        bones['r_calf'].rotation_quaternion = euler.to_quaternion()
        bones['r_calf'].keyframe_insert(data_path="rotation_quaternion", frame=frame, group="SitDown")

    if 'spine' in bones:
        euler = Euler((math.radians(spine_deg), 0, 0), 'XYZ')
        bones['spine'].rotation_quaternion = euler.to_quaternion()
        bones['spine'].keyframe_insert(data_path="rotation_quaternion", frame=frame, group="SitDown")

print("✅ SitDown 完成")

# ============================================
# StandUp 動畫（大幅度）
# ============================================
print("\n【5/5】StandUp 動畫（大幅度）...")

action_stand = bpy.data.actions.new(name="StandUp")
armature.animation_data.action = action_stand

bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = 60

keyframes = [
    (0, -0.4, 0.8, 90, 25),
    (30, -0.3, 0.6, 70, 15),
    (60, 0, 0, 0, 0),
]

for frame, hip_x, hip_y, knee_deg, spine_deg in keyframes:
    bpy.context.scene.frame_set(frame)
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.transforms_clear()

    if 'hip' in bones:
        bones['hip'].location = Vector((hip_x, hip_y, 0))
        bones['hip'].keyframe_insert(data_path="location", frame=frame, group="StandUp")

    if 'l_thigh' in bones:
        euler = Euler((math.radians(-knee_deg), 0, 0), 'XYZ')
        bones['l_thigh'].rotation_quaternion = euler.to_quaternion()
        bones['l_thigh'].keyframe_insert(data_path="rotation_quaternion", frame=frame, group="StandUp")

    if 'r_thigh' in bones:
        euler = Euler((math.radians(-knee_deg), 0, 0), 'XYZ')
        bones['r_thigh'].rotation_quaternion = euler.to_quaternion()
        bones['r_thigh'].keyframe_insert(data_path="rotation_quaternion", frame=frame, group="StandUp")

    if 'l_calf' in bones:
        euler = Euler((math.radians(knee_deg * 1.5), 0, 0), 'XYZ')
        bones['l_calf'].rotation_quaternion = euler.to_quaternion()
        bones['l_calf'].keyframe_insert(data_path="rotation_quaternion", frame=frame, group="StandUp")

    if 'r_calf' in bones:
        euler = Euler((math.radians(knee_deg * 1.5), 0, 0), 'XYZ')
        bones['r_calf'].rotation_quaternion = euler.to_quaternion()
        bones['r_calf'].keyframe_insert(data_path="rotation_quaternion", frame=frame, group="StandUp")

    if 'spine' in bones:
        euler = Euler((math.radians(spine_deg), 0, 0), 'XYZ')
        bones['spine'].rotation_quaternion = euler.to_quaternion()
        bones['spine'].keyframe_insert(data_path="rotation_quaternion", frame=frame, group="StandUp")

print("✅ StandUp 完成")

# 回到物件模式
bpy.ops.object.mode_set(mode='OBJECT')

print(f"\n總動畫: {len(bpy.data.actions)} 個")

# 導出
output = '/mnt/e_drive/claude-office/blender/exports/character_large_amplitude.glb'
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

print("\n✅ 關鍵修正：大幅度動作 + 正確四元數（使用 Euler.to_quaternion()）")
