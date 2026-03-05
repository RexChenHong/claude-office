import bpy
import math
from mathutils import Quaternion, Vector, Euler

print("\n=== 全身性動畫 + 正確的四元數增量 ===")

# 載入原始模型
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

source = '/mnt/e_drive/claude-office/assets/characters/3d/realistic_female_character__game-ready_3d_model.glb'
bpy.ops.import_scene.gltf(filepath=source)

# 找骨骼
armature = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
print(f"✅ 骨骼: {armature.name}")

# 切換到姿勢模式
bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode='POSE')

if not armature.animation_data:
    armature.animation_data_create()

# 設置原始動畫為基準
if bpy.data.actions:
    armature.animation_data.action = bpy.data.actions[0]
    bpy.context.scene.frame_set(0)

# 獲取所有主要骨骼的基準
bones_base = {}
for b in armature.pose.bones:
    n = b.name.lower()
    if 'hip' in n and 'pelvis' not in n and 'bone' not in n:
        bones_base['hip'] = b
    elif 'spine01' in n:
        bones_base['spine'] = b
    elif 'spine02' in n:
        bones_base['spine2'] = b
    elif 'head' in n:
        bones_base['head'] = b
    elif 'l_thigh' in n:
        bones_base['l_thigh'] = b
    elif 'l_calf' in n:
        bones_base['l_calf'] = b
    elif 'r_thigh' in n:
        bones_base['r_thigh'] = b
    elif 'r_calf' in n:
        bones_base['r_calf'] = b
    elif 'l_upperarm' in n:
        bones_base['l_upperarm'] = b
    elif 'l_forearm' in n:
        bones_base['l_forearm'] = b
    elif 'r_upperarm' in n:
        bones_base['r_upperarm'] = b
    elif 'r_forearm' in n:
        bones_base['r_forearm'] = b

print(f"✅ 找到 {len(bones_base)} 個控制骨骼（全身）")

# ============================================
# Idle 動畫（全身性）
# ============================================
print("\n【1/5】Idle 動畫（全身性）...")

action_idle = bpy.data.actions.new(name="Idle")
armature.animation_data.action = action_idle

bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = 120

for frame in range(0, 121, 10):
    bpy.context.scene.frame_set(frame)
    t = frame / 120

    # Hip 上下移動
    if 'hip' in bones_base:
        bone = bones_base['hip']
        # 獲取基準位置
        bpy.context.scene.frame_set(0)
        base_loc = bone.location.copy()
        bpy.context.scene.frame_set(frame)
        
        # 增量位置
        new_loc = base_loc + Vector((0, 0.1 * math.sin(t * 2 * math.pi), 0))
        bone.location = new_loc
        bone.keyframe_insert(data_path="location", frame=frame)

    # Spine2 輕微旋轉
    if 'spine2' in bones_base:
        bone = bones_base['spine2']
        # 獲取基準四元數
        bpy.context.scene.frame_set(0)
        base_quat = bone.rotation_quaternion.copy()
        bpy.context.scene.frame_set(frame)
        
        # 增量旋轉
        angle_rad = math.radians(15 * math.sin(t * 2 * math.pi))
        delta_euler = Euler((angle_rad, 0, 0), 'XYZ')
        delta_quat = delta_euler.to_quaternion()
        
        # 應用增量（四元數乘法）
        new_quat = delta_quat @ base_quat
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

print("✅ Idle 完成（上半身）")

# ============================================
# Walk 動畫（全身性）
# ============================================
print("\n【2/5】Walk 動畫（全身性）...")

action_walk = bpy.data.actions.new(name="Walk")
armature.animation_data.action = action_walk

bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = 48

for frame in range(0, 49, 4):
    bpy.context.scene.frame_set(frame)
    t = frame / 48 * 2 * math.pi

    # 獲取基準
    bpy.context.scene.frame_set(0)
    if 'hip' in bones_base:
        hip_base_loc = bones_base['hip'].location.copy()
        hip_base_quat = bones_base['hip'].rotation_quaternion.copy()
    if 'l_thigh' in bones_base:
        l_thigh_base_quat = bones_base['l_thigh'].rotation_quaternion.copy()
    if 'r_thigh' in bones_base:
        r_thigh_base_quat = bones_base['r_thigh'].rotation_quaternion.copy()
    if 'l_calf' in bones_base:
        l_calf_base_quat = bones_base['l_calf'].rotation_quaternion.copy()
    if 'r_calf' in bones_base:
        r_calf_base_quat = bones_base['r_calf'].rotation_quaternion.copy()
    
    bpy.context.scene.frame_set(frame)

    # Hip 上下移動
    if 'hip' in bones_base:
        bone = bones_base['hip']
        new_loc = hip_base_loc + Vector((0, 0.15 * abs(math.sin(t)), 0))
        bone.location = new_loc
        bone.keyframe_insert(data_path="location", frame=frame)

    # 大腿旋轉（左）
    if 'l_thigh' in bones_base:
        bone = bones_base['l_thigh']
        angle_deg = 45 * math.sin(t)
        delta_euler = Euler((math.radians(angle_deg), 0, 0), 'XYZ')
        delta_quat = delta_euler.to_quaternion()
        new_quat = delta_quat @ l_thigh_base_quat
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    # 大腿旋轉（右）
    if 'r_thigh' in bones_base:
        bone = bones_base['r_thigh']
        angle_deg = 45 * math.sin(t + math.pi)
        delta_euler = Euler((math.radians(angle_deg), 0, 0), 'XYZ')
        delta_quat = delta_euler.to_quaternion()
        new_quat = delta_quat @ r_thigh_base_quat
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    # 小腿旋轉（左）
    if 'l_calf' in bones_base:
        bone = bones_base['l_calf']
        angle_deg = max(0, 60 * math.sin(t + 0.5))
        delta_euler = Euler((math.radians(angle_deg), 0, 0), 'XYZ')
        delta_quat = delta_euler.to_quaternion()
        new_quat = delta_quat @ l_calf_base_quat
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    # 小腿旋轉（右）
    if 'r_calf' in bones_base:
        bone = bones_base['r_calf']
        angle_deg = max(0, 60 * math.sin(t + math.pi + 0.5))
        delta_euler = Euler((math.radians(angle_deg), 0, 0), 'XYZ')
        delta_quat = delta_euler.to_quaternion()
        new_quat = delta_quat @ r_calf_base_quat
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    # 手臂擺動（左）
    if 'l_upperarm' in bones_base:
        bpy.context.scene.frame_set(0)
        l_upperarm_base_quat = bones_base['l_upperarm'].rotation_quaternion.copy()
        bpy.context.scene.frame_set(frame)
        
        bone = bones_base['l_upperarm']
        angle_deg = 30 * math.sin(t + math.pi)
        delta_euler = Euler((math.radians(angle_deg), 0, 0), 'XYZ')
        delta_quat = delta_euler.to_quaternion()
        new_quat = delta_quat @ l_upperarm_base_quat
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    # 手臂擺動（右）
    if 'r_upperarm' in bones_base:
        bpy.context.scene.frame_set(0)
        r_upperarm_base_quat = bones_base['r_upperarm'].rotation_quaternion.copy()
        bpy.context.scene.frame_set(frame)
        
        bone = bones_base['r_upperarm']
        angle_deg = 30 * math.sin(t)
        delta_euler = Euler((math.radians(angle_deg), 0, 0), 'XYZ')
        delta_quat = delta_euler.to_quaternion()
        new_quat = delta_quat @ r_upperarm_base_quat
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

print("✅ Walk 完成（全身性）")

# 回到物件模式
bpy.ops.object.mode_set(mode='OBJECT')

print(f"\n總動畫: {len(bpy.data.actions)} 個")

# 導出
output = '/mnt/e_drive/claude-office/blender/exports/character_fullbody_animation.glb'
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
print("\n✅ 關鍵修正：全身性動畫（上下半身都有）")
