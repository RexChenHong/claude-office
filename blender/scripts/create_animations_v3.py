import bpy
import math

# 載入模型
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

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

# 定義主要骨骼
bone_names = {
    'hip': 'CC_Base_Hip',
    'spine': 'CC_Base_Spine01',
    'spine2': 'CC_Base_Spine02',
    'neck': 'CC_Base_Neck',
    'head': 'CC_Base_Head',
    'l_thigh': 'CC_Base_L_Thigh',
    'l_calf': 'CC_Base_L_Calf',
    'l_foot': 'CC_Base_L_Foot',
    'r_thigh': 'CC_Base_R_Thigh',
    'r_calf': 'CC_Base_R_Calf',
    'r_foot': 'CC_Base_R_Foot',
    'l_clavicle': 'CC_Base_L_Clavicle',
    'l_upperarm': 'CC_Base_L_Upperarm',
    'l_forearm': 'CC_Base_L_Forearm',
    'l_hand': 'CC_Base_L_Hand',
    'r_clavicle': 'CC_Base_R_Clavicle',
    'r_upperarm': 'CC_Base_R_Upperarm',
    'r_forearm': 'CC_Base_R_Forearm',
    'r_hand': 'CC_Base_R_Hand',
}

# 找到對應的骨骼
bones = {}
for key, name in bone_names.items():
    for bone in armature.pose.bones:
        if name in bone.name:
            bones[key] = bone
            break

print(f"找到 {len(bones)} 個骨骼")

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
    
    if 'hip' in bones:
        offset_y = 0.02 * math.sin(frame * 2 * math.pi / total_frames)
        bones['hip'].location = (0, offset_y, 0)
        bones['hip'].keyframe_insert(data_path="location", frame=frame)
    
    if 'spine2' in bones:
        breath = 0.03 * math.sin(frame * 2 * math.pi / total_frames)
        bones['spine2'].rotation_euler = (breath, 0, 0)
        bones['spine2'].keyframe_insert(data_path="rotation_euler", frame=frame)

# 將動畫推送到 NLA
track = armature.animation_data.nla_tracks.new()
track.name = "Idle"
strip = track.strips.new("Idle", 1, action_idle)
strip.name = "Idle"

print("✅ Idle 完成")

# === 動畫 2: Walk（走路）===
print("\n=== 製作 Walk 動畫 ===")
action_walk = bpy.data.actions.new(name="Walk")
armature.animation_data.action = action_walk

total_frames = 48

for frame in range(0, total_frames + 1, 2):
    bpy.context.scene.frame_set(frame)
    t = frame * 2 * math.pi / total_frames
    
    if 'hip' in bones:
        hip_y = 0.03 * abs(math.sin(t))
        hip_rot = 0.1 * math.sin(t)
        bones['hip'].location = (0, hip_y, 0)
        bones['hip'].rotation_euler = (0, 0, hip_rot)
        bones['hip'].keyframe_insert(data_path="location", frame=frame)
        bones['hip'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'l_thigh' in bones:
        l_thigh_rot = 0.4 * math.sin(t)
        bones['l_thigh'].rotation_euler = (l_thigh_rot, 0, 0)
        bones['l_thigh'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'l_calf' in bones:
        l_calf_rot = max(0, -0.5 * math.sin(t + 0.5))
        bones['l_calf'].rotation_euler = (l_calf_rot, 0, 0)
        bones['l_calf'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'r_thigh' in bones:
        r_thigh_rot = 0.4 * math.sin(t + math.pi)
        bones['r_thigh'].rotation_euler = (r_thigh_rot, 0, 0)
        bones['r_thigh'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'r_calf' in bones:
        r_calf_rot = max(0, -0.5 * math.sin(t + math.pi + 0.5))
        bones['r_calf'].rotation_euler = (r_calf_rot, 0, 0)
        bones['r_calf'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'l_upperarm' in bones:
        l_arm_rot = 0.3 * math.sin(t + math.pi)
        bones['l_upperarm'].rotation_euler = (l_arm_rot, 0, 0)
        bones['l_upperarm'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'r_upperarm' in bones:
        r_arm_rot = 0.3 * math.sin(t)
        bones['r_upperarm'].rotation_euler = (r_arm_rot, 0, 0)
        bones['r_upperarm'].keyframe_insert(data_path="rotation_euler", frame=frame)

# 推送到 NLA
track = armature.animation_data.nla_tracks.new()
track.name = "Walk"
strip = track.strips.new("Walk", 50, action_walk)
strip.name = "Walk"

print("✅ Walk 完成")

# === 動畫 3: Type（打字）===
print("\n=== 製作 Type 動畫 ===")
action_type = bpy.data.actions.new(name="Type")
armature.animation_data.action = action_type

total_frames = 60

for frame in range(0, total_frames + 1, 3):
    bpy.context.scene.frame_set(frame)
    t = frame * 2 * math.pi / total_frames
    
    if 'spine' in bones:
        lean = 0.2
        bones['spine'].rotation_euler = (lean, 0, 0)
        bones['spine'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'l_upperarm' in bones:
        l_upper = -0.8
        bones['l_upperarm'].rotation_euler = (l_upper, 0.3, 0)
        bones['l_upperarm'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'l_forearm' in bones:
        l_fore = -0.5 + 0.1 * math.sin(t * 3)
        bones['l_forearm'].rotation_euler = (l_fore, 0, 0)
        bones['l_forearm'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'r_upperarm' in bones:
        r_upper = -0.8
        bones['r_upperarm'].rotation_euler = (r_upper, -0.3, 0)
        bones['r_upperarm'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'r_forearm' in bones:
        r_fore = -0.5 + 0.1 * math.sin(t * 3 + math.pi)
        bones['r_forearm'].rotation_euler = (r_fore, 0, 0)
        bones['r_forearm'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'head' in bones:
        head_nod = 0.05 * math.sin(t * 2)
        bones['head'].rotation_euler = (head_nod, 0, 0)
        bones['head'].keyframe_insert(data_path="rotation_euler", frame=frame)

# 推送到 NLA
track = armature.animation_data.nla_tracks.new()
track.name = "Type"
strip = track.strips.new("Type", 100, action_type)
strip.name = "Type"

print("✅ Type 完成")

# === 動畫 4: SitDown（坐下）===
print("\n=== 製作 SitDown 動畫 ===")
action_sit = bpy.data.actions.new(name="SitDown")
armature.animation_data.action = action_sit

keyframes = [
    (0, 0, 0, 0, 0),
    (20, -0.3, 0.2, 0.8, 0.1),
    (40, -0.8, 0.6, 1.2, 0.2),
    (60, -1.0, 0.8, 1.4, 0.3),
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

# 推送到 NLA
track = armature.animation_data.nla_tracks.new()
track.name = "SitDown"
strip = track.strips.new("SitDown", 150, action_sit)
strip.name = "SitDown"

print("✅ SitDown 完成")

# === 動畫 5: StandUp（起立）===
print("\n=== 製作 StandUp 動畫 ===")
action_stand = bpy.data.actions.new(name="StandUp")
armature.animation_data.action = action_stand

keyframes = [
    (0, -1.0, 0.8, 1.4, 0.3),
    (20, -0.8, 0.6, 1.2, 0.2),
    (40, -0.3, 0.2, 0.8, 0.1),
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

# 推送到 NLA
track = armature.animation_data.nla_tracks.new()
track.name = "StandUp"
strip = track.strips.new("StandUp", 220, action_stand)
strip.name = "StandUp"

print("✅ StandUp 完成")

# 回到物件模式
bpy.ops.object.mode_set(mode='OBJECT')

# 設置幀範圍包含所有動畫
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 300

# 導出
output_file = '/mnt/e_drive/claude-office/blender/exports/character_animations_v3.glb'

bpy.ops.export_scene.gltf(
    filepath=output_file,
    export_format='GLB',
    export_cameras=False,
    export_lights=False,
    export_draco_mesh_compression_enable=False,
    export_animations=True,
    export_nla_strips=True,
    export_frame_range=False,  # 導出所有幀，不限於場景範圍
    export_all_influences=True,
    export_skins=True,
    export_morph=True
)

print(f"\n✅ 導出完成: {output_file}")
print("包含動畫:")
for action in bpy.data.actions:
    print(f"  - {action.name}")
