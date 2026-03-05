import bpy
import math

print("\n=== 修正版：使用正確的旋轉模式 ===")

# 載入原始模型
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

source = '/mnt/e_drive/claude-office/assets/characters/3d/realistic_female_character__game-ready_3d_model.glb'
bpy.ops.import_scene.gltf(filepath=source)

# 找骨骼
armature = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
print(f"骨骼: {armature.name}")

# 找主要骨骼並設置為 Euler 模式
bones = {}
for b in armature.pose.bones:
    n = b.name.lower()
    if 'hip' in n and 'pelvis' not in n and 'bone' not in n:
        bones['hip'] = b
        b.rotation_mode = 'XYZ'  # 關鍵：設置為 Euler 模式
    elif 'spine01' in n:
        bones['spine'] = b
        b.rotation_mode = 'XYZ'
    elif 'spine02' in n:
        bones['spine2'] = b
        b.rotation_mode = 'XYZ'
    elif 'head' in n:
        bones['head'] = b
        b.rotation_mode = 'XYZ'
    elif 'l_thigh' in n:
        bones['l_thigh'] = b
        b.rotation_mode = 'XYZ'
    elif 'l_calf' in n:
        bones['l_calf'] = b
        b.rotation_mode = 'XYZ'
    elif 'r_thigh' in n:
        bones['r_thigh'] = b
        b.rotation_mode = 'XYZ'
    elif 'r_calf' in n:
        bones['r_calf'] = b
        b.rotation_mode = 'XYZ'
    elif 'l_upperarm' in n:
        bones['l_upperarm'] = b
        b.rotation_mode = 'XYZ'
    elif 'l_forearm' in n:
        bones['l_forearm'] = b
        b.rotation_mode = 'XYZ'
    elif 'r_upperarm' in n:
        bones['r_upperarm'] = b
        b.rotation_mode = 'XYZ'
    elif 'r_forearm' in n:
        bones['r_forearm'] = b
        b.rotation_mode = 'XYZ'

print(f"✅ 找到 {len(bones)} 個控制骨骼，已設置為 XYZ 模式")

# 切換到姿勢模式
bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode='POSE')

if not armature.animation_data:
    armature.animation_data_create()

# ============================================
# 製作 Idle 動畫
# ============================================
print("\n【1/5】製作 Idle 動畫...")

action_idle = bpy.data.actions.new(name="Idle")
armature.animation_data.action = action_idle

bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = 120

for frame in range(0, 121, 10):
    bpy.context.scene.frame_set(frame)
    t = frame / 120

    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.transforms_clear()

    # 應用動畫
    if 'spine2' in bones:
        bones['spine2'].rotation_euler = (0.03 * math.sin(t * 2 * math.pi), 0, 0)

    if 'hip' in bones:
        bones['hip'].location = (0, 0.02 * math.sin(t * 2 * math.pi), 0)

    # 插入關鍵幀
    for bone_name, bone in bones.items():
        bone.keyframe_insert(data_path="location", frame=frame)
        bone.keyframe_insert(data_path="rotation_euler", frame=frame)

print("✅ Idle 完成")

# ============================================
# 製作 Walk 動畫
# ============================================
print("\n【2/5】製作 Walk 動畫...")

action_walk = bpy.data.actions.new(name="Walk")
armature.animation_data.action = action_walk

bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = 48

for frame in range(0, 49, 4):
    bpy.context.scene.frame_set(frame)
    t = frame / 48 * 2 * math.pi

    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.transforms_clear()

    if 'hip' in bones:
        bones['hip'].location = (0, 0.03 * abs(math.sin(t)), 0)

    if 'l_thigh' in bones:
        bones['l_thigh'].rotation_euler = (0.4 * math.sin(t), 0, 0)

    if 'r_thigh' in bones:
        bones['r_thigh'].rotation_euler = (0.4 * math.sin(t + math.pi), 0, 0)

    if 'l_calf' in bones:
        bones['l_calf'].rotation_euler = (max(0, -0.5 * math.sin(t + 0.5)), 0, 0)

    if 'r_calf' in bones:
        bones['r_calf'].rotation_euler = (max(0, -0.5 * math.sin(t + math.pi + 0.5)), 0, 0)

    for bone_name, bone in bones.items():
        bone.keyframe_insert(data_path="location", frame=frame)
        bone.keyframe_insert(data_path="rotation_euler", frame=frame)

print("✅ Walk 完成")

# ============================================
# 製作 Type 動畫
# ============================================
print("\n【3/5】製作 Type 動畫...")

action_type = bpy.data.actions.new(name="Type")
armature.animation_data.action = action_type

bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = 60

for frame in range(0, 61, 6):
    bpy.context.scene.frame_set(frame)
    t = frame / 60 * 2 * math.pi

    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.transforms_clear()

    if 'spine' in bones:
        bones['spine'].rotation_euler = (0.2, 0, 0)

    if 'l_upperarm' in bones:
        bones['l_upperarm'].rotation_euler = (-0.8, 0.3, 0)

    if 'l_forearm' in bones:
        bones['l_forearm'].rotation_euler = (-0.5 + 0.1 * math.sin(t * 3), 0, 0)

    if 'r_upperarm' in bones:
        bones['r_upperarm'].rotation_euler = (-0.8, -0.3, 0)

    if 'r_forearm' in bones:
        bones['r_forearm'].rotation_euler = (-0.5 + 0.1 * math.sin(t * 3 + math.pi), 0, 0)

    for bone_name, bone in bones.items():
        bone.keyframe_insert(data_path="location", frame=frame)
        bone.keyframe_insert(data_path="rotation_euler", frame=frame)

print("✅ Type 完成")

# ============================================
# 製作 SitDown 動畫
# ============================================
print("\n【4/5】製作 SitDown 動畫...")

action_sit = bpy.data.actions.new(name="SitDown")
armature.animation_data.action = action_sit

bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = 60

keyframes = [(0, 0, 0, 0), (30, -0.5, 1.0, 0.15), (60, -0.8, 1.3, 0.25)]

for frame, hip_x, knee_rot, spine_rot in keyframes:
    bpy.context.scene.frame_set(frame)
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.transforms_clear()

    if 'hip' in bones:
        bones['hip'].location = (hip_x, 0.7, 0)

    if 'l_thigh' in bones:
        bones['l_thigh'].rotation_euler = (-knee_rot, 0, 0)

    if 'r_thigh' in bones:
        bones['r_thigh'].rotation_euler = (-knee_rot, 0, 0)

    if 'l_calf' in bones:
        bones['l_calf'].rotation_euler = (knee_rot * 1.5, 0, 0)

    if 'r_calf' in bones:
        bones['r_calf'].rotation_euler = (knee_rot * 1.5, 0, 0)

    if 'spine' in bones:
        bones['spine'].rotation_euler = (spine_rot, 0, 0)

    for bone_name, bone in bones.items():
        bone.keyframe_insert(data_path="location", frame=frame)
        bone.keyframe_insert(data_path="rotation_euler", frame=frame)

print("✅ SitDown 完成")

# ============================================
# 製作 StandUp 動畫
# ============================================
print("\n【5/5】製作 StandUp 動畫...")

action_stand = bpy.data.actions.new(name="StandUp")
armature.animation_data.action = action_stand

bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = 60

keyframes = [(0, -0.8, 1.3, 0.25), (30, -0.5, 1.0, 0.15), (60, 0, 0, 0)]

for frame, hip_x, knee_rot, spine_rot in keyframes:
    bpy.context.scene.frame_set(frame)
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.transforms_clear()

    if 'hip' in bones:
        bones['hip'].location = (hip_x, 0.7, 0)

    if 'l_thigh' in bones:
        bones['l_thigh'].rotation_euler = (-knee_rot, 0, 0)

    if 'r_thigh' in bones:
        bones['r_thigh'].rotation_euler = (-knee_rot, 0, 0)

    if 'l_calf' in bones:
        bones['l_calf'].rotation_euler = (knee_rot * 1.5, 0, 0)

    if 'r_calf' in bones:
        bones['r_calf'].rotation_euler = (knee_rot * 1.5, 0, 0)

    if 'spine' in bones:
        bones['spine'].rotation_euler = (spine_rot, 0, 0)

    for bone_name, bone in bones.items():
        bone.keyframe_insert(data_path="location", frame=frame)
        bone.keyframe_insert(data_path="rotation_euler", frame=frame)

print("✅ StandUp 完成")

# 回到物件模式
bpy.ops.object.mode_set(mode='OBJECT')

print(f"\n總動畫: {len(bpy.data.actions)} 個")

# 導出
output = '/mnt/e_drive/claude-office/blender/exports/character_euler_animations.glb'
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
    print(f"  - {a.name} (幀: {a.frame_range.x:.0f} - {a.frame_range.y:.0f})")

print("\n✅ 關鍵修正：所有骨骼都已設置為 XYZ Euler 模式！")
