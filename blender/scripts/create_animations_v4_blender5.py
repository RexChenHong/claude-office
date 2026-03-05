import bpy
import math

# 清除場景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 載入來源模型
source_file = '/mnt/e_drive/claude-office/assets/characters/3d/realistic_female_character__game-ready_3d_model.glb'
bpy.ops.import_scene.gltf(filepath=source_file)

print("✅ 模型載入成功")

# 找到骨骼
armature = None
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE':
        armature = obj
        break

if not armature:
    print("❌ 找不到骨骼")
    exit(1)

print(f"✅ 找到骨骼: {armature.name}")

# 清除所有舊動畫
for action in bpy.data.actions:
    bpy.data.actions.remove(action)

# 定義骨骼
bone_map = {}
for bone in armature.pose.bones:
    name_lower = bone.name.lower()
    if 'hip' in name_lower:
        bone_map['hip'] = bone
    elif 'spine' in name_lower and 'spine01' in name_lower:
        bone_map['spine'] = bone
    elif 'spine02' in name_lower:
        bone_map['spine2'] = bone
    elif 'head' in name_lower:
        bone_map['head'] = bone
    elif 'l_thigh' in name_lower:
        bone_map['l_thigh'] = bone
    elif 'l_calf' in name_lower:
        bone_map['l_calf'] = bone
    elif 'r_thigh' in name_lower:
        bone_map['r_thigh'] = bone
    elif 'r_calf' in name_lower:
        bone_map['r_calf'] = bone
    elif 'l_upperarm' in name_lower:
        bone_map['l_upperarm'] = bone
    elif 'l_forearm' in name_lower:
        bone_map['l_forearm'] = bone
    elif 'r_upperarm' in name_lower:
        bone_map['r_upperarm'] = bone
    elif 'r_forearm' in name_lower:
        bone_map['r_forearm'] = bone

print(f"找到 {len(bone_map)} 個骨骼")

# 切換到姿勢模式
bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode='POSE')

# === 動畫 1: Idle（待機）===
print("\n=== 製作 Idle 動畫 ===")
action_idle = bpy.data.actions.new(name="Idle")
armature.animation_data_create()
armature.animation_data.action = action_idle

total_frames = 120
for frame in range(0, total_frames + 1, 4):
    bpy.context.scene.frame_set(frame)
    
    if 'hip' in bone_map:
        offset_y = 0.02 * math.sin(frame * 2 * math.pi / total_frames)
        bone_map['hip'].location = (0, offset_y, 0)
        bone_map['hip'].keyframe_insert(data_path="location", frame=frame)
    
    if 'spine2' in bone_map:
        breath = 0.03 * math.sin(frame * 2 * math.pi / total_frames)
        bone_map['spine2'].rotation_euler = (breath, 0, 0)
        bone_map['spine2'].keyframe_insert(data_path="rotation_euler", frame=frame)

print("✅ Idle 完成")

# === 動畫 2: Walk（走路）===
print("\n=== 製作 Walk 動畫 ===")
action_walk = bpy.data.actions.new(name="Walk")
armature.animation_data.action = action_walk

total_frames = 48
for frame in range(0, total_frames + 1, 2):
    bpy.context.scene.frame_set(frame)
    t = frame * 2 * math.pi / total_frames
    
    if 'hip' in bone_map:
        hip_y = 0.03 * abs(math.sin(t))
        hip_rot = 0.1 * math.sin(t)
        bone_map['hip'].location = (0, hip_y, 0)
        bone_map['hip'].rotation_euler = (0, 0, hip_rot)
        bone_map['hip'].keyframe_insert(data_path="location", frame=frame)
        bone_map['hip'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'l_thigh' in bone_map:
        bone_map['l_thigh'].rotation_euler = (0.4 * math.sin(t), 0, 0)
        bone_map['l_thigh'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'l_calf' in bone_map:
        bone_map['l_calf'].rotation_euler = (max(0, -0.5 * math.sin(t + 0.5)), 0, 0)
        bone_map['l_calf'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'r_thigh' in bone_map:
        bone_map['r_thigh'].rotation_euler = (0.4 * math.sin(t + math.pi), 0, 0)
        bone_map['r_thigh'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'r_calf' in bone_map:
        bone_map['r_calf'].rotation_euler = (max(0, -0.5 * math.sin(t + math.pi + 0.5)), 0, 0)
        bone_map['r_calf'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'l_upperarm' in bone_map:
        bone_map['l_upperarm'].rotation_euler = (0.3 * math.sin(t + math.pi), 0, 0)
        bone_map['l_upperarm'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'r_upperarm' in bone_map:
        bone_map['r_upperarm'].rotation_euler = (0.3 * math.sin(t), 0, 0)
        bone_map['r_upperarm'].keyframe_insert(data_path="rotation_euler", frame=frame)

print("✅ Walk 完成")

# === 動畫 3: Type（打字）===
print("\n=== 製作 Type 動畫 ===")
action_type = bpy.data.actions.new(name="Type")
armature.animation_data.action = action_type

total_frames = 60
for frame in range(0, total_frames + 1, 3):
    bpy.context.scene.frame_set(frame)
    t = frame * 2 * math.pi / total_frames
    
    if 'spine' in bone_map:
        bone_map['spine'].rotation_euler = (0.2, 0, 0)
        bone_map['spine'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'l_upperarm' in bone_map:
        bone_map['l_upperarm'].rotation_euler = (-0.8, 0.3, 0)
        bone_map['l_upperarm'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'l_forearm' in bone_map:
        bone_map['l_forearm'].rotation_euler = (-0.5 + 0.1 * math.sin(t * 3), 0, 0)
        bone_map['l_forearm'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'r_upperarm' in bone_map:
        bone_map['r_upperarm'].rotation_euler = (-0.8, -0.3, 0)
        bone_map['r_upperarm'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'r_forearm' in bone_map:
        bone_map['r_forearm'].rotation_euler = (-0.5 + 0.1 * math.sin(t * 3 + math.pi), 0, 0)
        bone_map['r_forearm'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'head' in bone_map:
        bone_map['head'].rotation_euler = (0.05 * math.sin(t * 2), 0, 0)
        bone_map['head'].keyframe_insert(data_path="rotation_euler", frame=frame)

print("✅ Type 完成")

# === 動畫 4: SitDown（坐下）===
print("\n=== 製作 SitDown 動畫 ===")
action_sit = bpy.data.actions.new(name="SitDown")
armature.animation_data.action = action_sit

keyframes = [(0, 0, 0, 0), (20, 0.2, 0.8, 0.1), (40, 0.6, 1.2, 0.2), (60, 0.8, 1.4, 0.3)]
for frame, hip_y, knee_rot, spine_rot in keyframes:
    bpy.context.scene.frame_set(frame)
    
    if 'hip' in bone_map:
        bone_map['hip'].location = (-frame * 0.016, hip_y, 0)
        bone_map['hip'].keyframe_insert(data_path="location", frame=frame)
    
    if 'l_thigh' in bone_map:
        bone_map['l_thigh'].rotation_euler = (-knee_rot, 0, 0)
        bone_map['l_thigh'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'r_thigh' in bone_map:
        bone_map['r_thigh'].rotation_euler = (-knee_rot, 0, 0)
        bone_map['r_thigh'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'l_calf' in bone_map:
        bone_map['l_calf'].rotation_euler = (knee_rot * 1.5, 0, 0)
        bone_map['l_calf'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'r_calf' in bone_map:
        bone_map['r_calf'].rotation_euler = (knee_rot * 1.5, 0, 0)
        bone_map['r_calf'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'spine' in bone_map:
        bone_map['spine'].rotation_euler = (spine_rot, 0, 0)
        bone_map['spine'].keyframe_insert(data_path="rotation_euler", frame=frame)

print("✅ SitDown 完成")

# === 動畫 5: StandUp（起立）===
print("\n=== 製作 StandUp 動畫 ===")
action_stand = bpy.data.actions.new(name="StandUp")
armature.animation_data.action = action_stand

keyframes = [(0, 0.8, 1.4, 0.3), (20, 0.6, 1.2, 0.2), (40, 0.2, 0.8, 0.1), (60, 0, 0, 0)]
for frame, hip_y, knee_rot, spine_rot in keyframes:
    bpy.context.scene.frame_set(frame)
    
    if 'hip' in bone_map:
        bone_map['hip'].location = (-(60 - frame) * 0.016, hip_y, 0)
        bone_map['hip'].keyframe_insert(data_path="location", frame=frame)
    
    if 'l_thigh' in bone_map:
        bone_map['l_thigh'].rotation_euler = (-knee_rot, 0, 0)
        bone_map['l_thigh'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'r_thigh' in bone_map:
        bone_map['r_thigh'].rotation_euler = (-knee_rot, 0, 0)
        bone_map['r_thigh'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'l_calf' in bone_map:
        bone_map['l_calf'].rotation_euler = (knee_rot * 1.5, 0, 0)
        bone_map['l_calf'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'r_calf' in bone_map:
        bone_map['r_calf'].rotation_euler = (knee_rot * 1.5, 0, 0)
        bone_map['r_calf'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'spine' in bone_map:
        bone_map['spine'].rotation_euler = (spine_rot, 0, 0)
        bone_map['spine'].keyframe_insert(data_path="rotation_euler", frame=frame)

print("✅ StandUp 完成")

# 回到物件模式
bpy.ops.object.mode_set(mode='OBJECT')

# 導出（使用 Blender 5.0 的最新參數）
output_file = '/mnt/e_drive/claude-office/blender/exports/character_animations_v4.blend'
bpy.ops.wm.save_as_mainfile(filepath=output_file)

# 導出 GLB
output_glb = '/mnt/e_drive/claude-office/blender/exports/character_animations_v4.glb'
bpy.ops.export_scene.gltf(
    filepath=output_glb,
    export_format='GLB',
    export_cameras=False,
    export_lights=False,
    export_animations=True,
    export_nla_strips=False,  # 改為 False，導出當前動作
    export_skins=True,
    export_morph=True
)

print(f"\n✅ 導出完成: {output_glb}")
print("包含動畫:")
for action in bpy.data.actions:
    print(f"  - {action.name}")
