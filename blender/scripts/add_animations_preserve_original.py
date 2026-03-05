import bpy
import math

# 載入原始模型（不刪除任何動畫！）
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

source_file = '/mnt/e_drive/claude-office/assets/characters/3d/realistic_female_character__game-ready_3d_model.glb'
bpy.ops.import_scene.gltf(filepath=source_file)

print("✅ 載入原始模型（保留所有動畫）")

# 找到骨骼
armature = None
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE':
        armature = obj
        break

print(f"✅ 找到骨骼: {armature.name}")
print(f"原始動畫數量: {len(bpy.data.actions)}")

# 找到主要骨骼
bone_map = {}
for bone in armature.pose.bones:
    name_lower = bone.name.lower()
    if 'hip' in name_lower and 'pelvis' not in name_lower:
        bone_map['hip'] = bone
    elif 'spine01' in name_lower:
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

print(f"找到 {len(bone_map)} 個控制骨骼")

# 切換到姿勢模式
bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode='POSE')

# 確保有 animation_data
if not armature.animation_data:
    armature.animation_data_create()

# 添加新的自定義動畫（不覆蓋原有的！）

# === 新增 Idle 動畫 ===
print("\n=== 新增 Idle 動畫 ===")
action_idle = bpy.data.actions.new(name="Idle")

total_frames = 120
for frame in range(0, total_frames + 1, 4):
    bpy.context.scene.frame_set(frame)
    
    # 輕微呼吸
    if 'spine2' in bone_map:
        breath = 0.05 * math.sin(frame * 2 * math.pi / total_frames)
        bone_map['spine2'].rotation_euler = (breath, 0, 0)
        bone_map['spine2'].keyframe_insert(data_path="rotation_euler", frame=frame, action=action_idle)
    
    # 輕微上下晃動
    if 'hip' in bone_map:
        offset = 0.02 * math.sin(frame * 2 * math.pi / total_frames)
        bone_map['hip'].location = (0, offset, 0)
        bone_map['hip'].keyframe_insert(data_path="location", frame=frame, action=action_idle)

print("✅ Idle 完成")

# === 新增 Walk 動畫 ===
print("\n=== 新增 Walk 動畫 ===")
action_walk = bpy.data.actions.new(name="Walk")

total_frames = 48
for frame in range(0, total_frames + 1, 2):
    bpy.context.scene.frame_set(frame)
    t = frame * 2 * math.pi / total_frames
    
    if 'hip' in bone_map:
        hip_y = 0.03 * abs(math.sin(t))
        hip_rot = 0.1 * math.sin(t)
        bone_map['hip'].location = (0, hip_y, 0)
        bone_map['hip'].rotation_euler = (0, 0, hip_rot)
        bone_map['hip'].keyframe_insert(data_path="location", frame=frame, action=action_walk)
        bone_map['hip'].keyframe_insert(data_path="rotation_euler", frame=frame, action=action_walk)
    
    if 'l_thigh' in bone_map:
        bone_map['l_thigh'].rotation_euler = (0.4 * math.sin(t), 0, 0)
        bone_map['l_thigh'].keyframe_insert(data_path="rotation_euler", frame=frame, action=action_walk)
    
    if 'l_calf' in bone_map:
        bone_map['l_calf'].rotation_euler = (max(0, -0.5 * math.sin(t + 0.5)), 0, 0)
        bone_map['l_calf'].keyframe_insert(data_path="rotation_euler", frame=frame, action=action_walk)
    
    if 'r_thigh' in bone_map:
        bone_map['r_thigh'].rotation_euler = (0.4 * math.sin(t + math.pi), 0, 0)
        bone_map['r_thigh'].keyframe_insert(data_path="rotation_euler", frame=frame, action=action_walk)
    
    if 'r_calf' in bone_map:
        bone_map['r_calf'].rotation_euler = (max(0, -0.5 * math.sin(t + math.pi + 0.5)), 0, 0)
        bone_map['r_calf'].keyframe_insert(data_path="rotation_euler", frame=frame, action=action_walk)
    
    if 'l_upperarm' in bone_map:
        bone_map['l_upperarm'].rotation_euler = (0.3 * math.sin(t + math.pi), 0, 0)
        bone_map['l_upperarm'].keyframe_insert(data_path="rotation_euler", frame=frame, action=action_walk)
    
    if 'r_upperarm' in bone_map:
        bone_map['r_upperarm'].rotation_euler = (0.3 * math.sin(t), 0, 0)
        bone_map['r_upperarm'].keyframe_insert(data_path="rotation_euler", frame=frame, action=action_walk)

print("✅ Walk 完成")

# === 新增 Type 動畫 ===
print("\n=== 新增 Type 動畫 ===")
action_type = bpy.data.actions.new(name="Type")

total_frames = 60
for frame in range(0, total_frames + 1, 3):
    bpy.context.scene.frame_set(frame)
    t = frame * 2 * math.pi / total_frames
    
    if 'spine' in bone_map:
        bone_map['spine'].rotation_euler = (0.2, 0, 0)
        bone_map['spine'].keyframe_insert(data_path="rotation_euler", frame=frame, action=action_type)
    
    if 'l_upperarm' in bone_map:
        bone_map['l_upperarm'].rotation_euler = (-0.8, 0.3, 0)
        bone_map['l_upperarm'].keyframe_insert(data_path="rotation_euler", frame=frame, action=action_type)
    
    if 'l_forearm' in bone_map:
        bone_map['l_forearm'].rotation_euler = (-0.5 + 0.1 * math.sin(t * 3), 0, 0)
        bone_map['l_forearm'].keyframe_insert(data_path="rotation_euler", frame=frame, action=action_type)
    
    if 'r_upperarm' in bone_map:
        bone_map['r_upperarm'].rotation_euler = (-0.8, -0.3, 0)
        bone_map['r_upperarm'].keyframe_insert(data_path="rotation_euler", frame=frame, action=action_type)
    
    if 'r_forearm' in bone_map:
        bone_map['r_forearm'].rotation_euler = (-0.5 + 0.1 * math.sin(t * 3 + math.pi), 0, 0)
        bone_map['r_forearm'].keyframe_insert(data_path="rotation_euler", frame=frame, action=action_type)

print("✅ Type 完成")

# 回到物件模式
bpy.ops.object.mode_set(mode='OBJECT')

print(f"\n總動畫數量: {len(bpy.data.actions)}")

# 導出
output_glb = '/mnt/e_drive/claude-office/blender/exports/character_with_custom_animations.glb'
bpy.ops.export_scene.gltf(
    filepath=output_glb,
    export_format='GLB',
    export_cameras=False,
    export_lights=False,
    export_animations=True,
    export_skins=True,
    export_morph=True
)

print(f"\n✅ 導出完成: {output_glb}")
print("包含動畫:")
for action in bpy.data.actions:
    print(f"  - {action.name}")
