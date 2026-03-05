import bpy
import math

print("\n" + "="*60)
print("正確製作動畫 - 使用 Blender 正確 API")
print("="*60)

# 載入原始模型
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

source_file = '/mnt/e_drive/claude-office/assets/characters/3d/realistic_female_character__game-ready_3d_model.glb'
bpy.ops.import_scene.gltf(filepath=source_file)

print("\n✅ 原始模型載入成功")

# 找到骨骼
armature = None
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE':
        armature = obj
        break

print(f"✅ 骨骼系統: {armature.name}")

# 找到主要骨骼
bones = {}
for bone in armature.pose.bones:
    name = bone.name.lower()
    if 'hip' in name and 'pelvis' not in name:
        bones['hip'] = bone
    elif 'spine01' in name:
        bones['spine'] = bone
    elif 'spine02' in name:
        bones['spine2'] = bone
    elif 'head' in name:
        bones['head'] = bone
    elif 'l_thigh' in name:
        bones['l_thigh'] = bone
    elif 'l_calf' in name:
        bones['l_calf'] = bone
    elif 'r_thigh' in name:
        bones['r_thigh'] = bone
    elif 'r_calf' in name:
        bones['r_calf'] = bone
    elif 'l_upperarm' in name:
        bones['l_upperarm'] = bone
    elif 'l_forearm' in name:
        bones['l_forearm'] = bone
    elif 'r_upperarm' in name:
        bones['r_upperarm'] = bone
    elif 'r_forearm' in name:
        bones['r_forearm'] = bone

print(f"✅ 找到 {len(bones)} 個控制骨骼")

# 切換到姿勢模式
bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode='POSE')

# 確保有 animation_data
if not armature.animation_data:
    armature.animation_data_create()

print("\n" + "="*60)
print("開始製作 5 個動畫")
print("="*60)

# ============================================
# 動畫 1: Idle（閒置）
# ============================================
print("\n【1/5】製作 Idle 動畫...")
action_idle = bpy.data.actions.new(name="Idle")
armature.animation_data.action = action_idle  # 設置為當前動作

total_frames = 120
for frame in range(0, total_frames + 1, 4):
    bpy.context.scene.frame_set(frame)
    t = frame / total_frames

    if 'spine2' in bones:
        breath = 0.03 * math.sin(t * 2 * math.pi)
        bones['spine2'].rotation_euler = (breath, 0, 0)
        bones['spine2'].keyframe_insert(data_path="rotation_euler", frame=frame)

    if 'hip' in bones:
        offset = 0.02 * math.sin(t * 2 * math.pi)
        bones['hip'].location = (0, offset, 0)
        bones['hip'].keyframe_insert(data_path="location", frame=frame)

print("  ✅ Idle 完成")

# ============================================
# 動畫 2: Walk（走路）
# ============================================
print("\n【2/5】製作 Walk 動畫...")
action_walk = bpy.data.actions.new(name="Walk")
armature.animation_data.action = action_walk

total_frames = 48
for frame in range(0, total_frames + 1, 2):
    bpy.context.scene.frame_set(frame)
    t = frame / total_frames * 2 * math.pi

    if 'hip' in bones:
        bones['hip'].location = (0, 0.03 * abs(math.sin(t)), 0)
        bones['hip'].rotation_euler = (0, 0, 0.1 * math.sin(t))
        bones['hip'].keyframe_insert(data_path="location", frame=frame)
        bones['hip'].keyframe_insert(data_path="rotation_euler", frame=frame)

    if 'l_thigh' in bones:
        bones['l_thigh'].rotation_euler = (0.4 * math.sin(t), 0, 0)
        bones['l_thigh'].keyframe_insert(data_path="rotation_euler", frame=frame)

    if 'l_calf' in bones:
        bones['l_calf'].rotation_euler = (max(0, -0.5 * math.sin(t + 0.5)), 0, 0)
        bones['l_calf'].keyframe_insert(data_path="rotation_euler", frame=frame)

    if 'r_thigh' in bones:
        bones['r_thigh'].rotation_euler = (0.4 * math.sin(t + math.pi), 0, 0)
        bones['r_thigh'].keyframe_insert(data_path="rotation_euler", frame=frame)

    if 'r_calf' in bones:
        bones['r_calf'].rotation_euler = (max(0, -0.5 * math.sin(t + math.pi + 0.5)), 0, 0)
        bones['r_calf'].keyframe_insert(data_path="rotation_euler", frame=frame)

    if 'l_upperarm' in bones:
        bones['l_upperarm'].rotation_euler = (0.3 * math.sin(t + math.pi), 0, 0)
        bones['l_upperarm'].keyframe_insert(data_path="rotation_euler", frame=frame)

    if 'r_upperarm' in bones:
        bones['r_upperarm'].rotation_euler = (0.3 * math.sin(t), 0, 0)
        bones['r_upperarm'].keyframe_insert(data_path="rotation_euler", frame=frame)

print("  ✅ Walk 完成")

# ============================================
# 動畫 3: Type（打字）
# ============================================
print("\n【3/5】製作 Type 動畫...")
action_type = bpy.data.actions.new(name="Type")
armature.animation_data.action = action_type

total_frames = 60
for frame in range(0, total_frames + 1, 3):
    bpy.context.scene.frame_set(frame)
    t = frame / total_frames * 2 * math.pi

    if 'spine' in bones:
        bones['spine'].rotation_euler = (0.2, 0, 0)
        bones['spine'].keyframe_insert(data_path="rotation_euler", frame=frame)

    if 'l_upperarm' in bones:
        bones['l_upperarm'].rotation_euler = (-0.8, 0.3, 0)
        bones['l_upperarm'].keyframe_insert(data_path="rotation_euler", frame=frame)

    if 'l_forearm' in bones:
        bones['l_forearm'].rotation_euler = (-0.5 + 0.1 * math.sin(t * 3), 0, 0)
        bones['l_forearm'].keyframe_insert(data_path="rotation_euler", frame=frame)

    if 'r_upperarm' in bones:
        bones['r_upperarm'].rotation_euler = (-0.8, -0.3, 0)
        bones['r_upperarm'].keyframe_insert(data_path="rotation_euler", frame=frame)

    if 'r_forearm' in bones:
        bones['r_forearm'].rotation_euler = (-0.5 + 0.1 * math.sin(t * 3 + math.pi), 0, 0)
        bones['r_forearm'].keyframe_insert(data_path="rotation_euler", frame=frame)

    if 'head' in bones:
        bones['head'].rotation_euler = (0.05 * math.sin(t * 2), 0, 0)
        bones['head'].keyframe_insert(data_path="rotation_euler", frame=frame)

print("  ✅ Type 完成")

# ============================================
# 動畫 4: SitDown（坐下）
# ============================================
print("\n【4/5】製作 SitDown 動畫...")
action_sit = bpy.data.actions.new(name="SitDown")
armature.animation_data.action = action_sit

keyframes = [
    (0, 0, 0, 0, 0),
    (15, -0.2, 0.15, 0.6, 0.08),
    (30, -0.5, 0.4, 1.0, 0.15),
    (45, -0.7, 0.6, 1.2, 0.2),
    (60, -0.8, 0.7, 1.3, 0.25),
]

for frame, hip_x, hip_y, knee_rot, spine_rot in keyframes:
    bpy.context.scene.frame_set(frame)

    if 'hip' in bones:
        bones['hip'].location = (hip_x, hip_y, 0)
        bones['hip'].keyframe_insert(data_path="location", frame=frame)

    if 'l_thigh' in bones:
        bones['l_thigh'].rotation_euler = (-knee_rot, 0, 0)
        bones['l_thigh'].keyframe_insert(data_path="rotation_euler", frame=frame)

    if 'r_thigh' in bones:
        bones['r_thigh'].rotation_euler = (-knee_rot, 0, 0)
        bones['r_thigh'].keyframe_insert(data_path="rotation_euler", frame=frame)

    if 'l_calf' in bones:
        bones['l_calf'].rotation_euler = (knee_rot * 1.5, 0, 0)
        bones['l_calf'].keyframe_insert(data_path="rotation_euler", frame=frame)

    if 'r_calf' in bones:
        bones['r_calf'].rotation_euler = (knee_rot * 1.5, 0, 0)
        bones['r_calf'].keyframe_insert(data_path="rotation_euler", frame=frame)

    if 'spine' in bones:
        bones['spine'].rotation_euler = (spine_rot, 0, 0)
        bones['spine'].keyframe_insert(data_path="rotation_euler", frame=frame)

print("  ✅ SitDown 完成")

# ============================================
# 動畫 5: StandUp（起立）
# ============================================
print("\n【5/5】製作 StandUp 動畫...")
action_stand = bpy.data.actions.new(name="StandUp")
armature.animation_data.action = action_stand

keyframes = [
    (0, -0.8, 0.7, 1.3, 0.25),
    (15, -0.7, 0.6, 1.2, 0.2),
    (30, -0.5, 0.4, 1.0, 0.15),
    (45, -0.2, 0.15, 0.6, 0.08),
    (60, 0, 0, 0, 0),
]

for frame, hip_x, hip_y, knee_rot, spine_rot in keyframes:
    bpy.context.scene.frame_set(frame)

    if 'hip' in bones:
        bones['hip'].location = (hip_x, hip_y, 0)
        bones['hip'].keyframe_insert(data_path="location", frame=frame)

    if 'l_thigh' in bones:
        bones['l_thigh'].rotation_euler = (-knee_rot, 0, 0)
        bones['l_thigh'].keyframe_insert(data_path="rotation_euler", frame=frame)

    if 'r_thigh' in bones:
        bones['r_thigh'].rotation_euler = (-knee_rot, 0, 0)
        bones['r_thigh'].keyframe_insert(data_path="rotation_euler", frame=frame)

    if 'l_calf' in bones:
        bones['l_calf'].rotation_euler = (knee_rot * 1.5, 0, 0)
        bones['l_calf'].keyframe_insert(data_path="rotation_euler", frame=frame)

    if 'r_calf' in bones:
        bones['r_calf'].rotation_euler = (knee_rot * 1.5, 0, 0)
        bones['r_calf'].keyframe_insert(data_path="rotation_euler", frame=frame)

    if 'spine' in bones:
        bones['spine'].rotation_euler = (spine_rot, 0, 0)
        bones['spine'].keyframe_insert(data_path="rotation_euler", frame=frame)

print("  ✅ StandUp 完成")

# 回到物件模式
bpy.ops.object.mode_set(mode='OBJECT')

print("\n" + "="*60)
print(f"動畫製作完成！總動畫數: {len(bpy.data.actions)}")
print("="*60)

# 導出
output_glb = '/mnt/e_drive/claude-office/blender/exports/character_final_animations.glb'
bpy.ops.export_scene.gltf(
    filepath=output_glb,
    export_format='GLB',
    export_cameras=False,
    export_lights=False,
    export_animations=True,
    export_skins=True,
    export_morph=True
)

print(f"\n✅ 導出成功: {output_glb}")

import os
file_size = os.path.getsize(output_glb) / 1024 / 1024
print(f"✅ 檔案大小: {file_size:.1f} MB")

print("\n包含的動畫:")
for action in bpy.data.actions:
    if action.name in ['Idle', 'Walk', 'Type', 'SitDown', 'StandUp']:
        print(f"  ✅ {action.name}")
