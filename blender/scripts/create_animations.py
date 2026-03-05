import bpy
import math
from mathutils import Euler

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
print(f"骨骼數量: {len(armature.data.bones)}")

# 切換到姿勢模式
bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode='POSE')

# 清除所有舊動畫
for action in bpy.data.actions:
    bpy.data.actions.remove(action)

# 定義主要骨骼名稱（根據 Character Creator 命名規則）
bone_names = {
    'hip': 'CC_Base_Hip',
    'spine': 'CC_Base_Spine',
    'spine1': 'CC_Base_Spine01',
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
            print(f"  找到 {key}: {bone.name}")
            break

# === 動畫 1: 待機（Idle）===
print("\n=== 製作待機動畫 ===")
action_idle = bpy.data.actions.new(name="Idle")
action_idle.use_fake_user = True

# 設定幀率 24 FPS，總共 120 幀（5 秒循環）
fps = 24
total_frames = 120

for frame in range(0, total_frames + 1, 10):
    bpy.context.scene.frame_set(frame)
    
    # 輕微上下晃動
    if 'hip' in bones:
        offset_y = 0.02 * math.sin(frame * 2 * math.pi / total_frames)
        bones['hip'].location = (0, offset_y, 0)
        bones['hip'].keyframe_insert(data_path="location", frame=frame)
    
    # 輕微呼吸
    if 'spine2' in bones:
        breath = 0.03 * math.sin(frame * 2 * math.pi / total_frames)
        bones['spine2'].rotation_euler = (breath, 0, 0)
        bones['spine2'].keyframe_insert(data_path="rotation_euler", frame=frame)

print("✅ 待機動畫完成")

# === 動畫 2: 走路（Walk）===
print("\n=== 製作走路動畫 ===")
action_walk = bpy.data.actions.new(name="Walk")
action_walk.use_fake_user = True

total_frames = 48  # 2 秒循環

for frame in range(0, total_frames + 1, 2):
    bpy.context.scene.frame_set(frame)
    
    t = frame * 2 * math.pi / total_frames
    
    # 髖部上下移動
    if 'hip' in bones:
        hip_y = 0.03 * abs(math.sin(t))
        bones['hip'].location = (0, hip_y, 0)
        bones['hip'].keyframe_insert(data_path="location", frame=frame)
        
        # 髖部左右旋轉
        hip_rot = 0.1 * math.sin(t)
        bones['hip'].rotation_euler = (0, 0, hip_rot)
        bones['hip'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    # 左腿
    if 'l_thigh' in bones:
        l_thigh_rot = 0.4 * math.sin(t)
        bones['l_thigh'].rotation_euler = (l_thigh_rot, 0, 0)
        bones['l_thigh'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'l_calf' in bones:
        l_calf_rot = max(0, -0.5 * math.sin(t + 0.5))
        bones['l_calf'].rotation_euler = (l_calf_rot, 0, 0)
        bones['l_calf'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    # 右腿（相反）
    if 'r_thigh' in bones:
        r_thigh_rot = 0.4 * math.sin(t + math.pi)
        bones['r_thigh'].rotation_euler = (r_thigh_rot, 0, 0)
        bones['r_thigh'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'r_calf' in bones:
        r_calf_rot = max(0, -0.5 * math.sin(t + math.pi + 0.5))
        bones['r_calf'].rotation_euler = (r_calf_rot, 0, 0)
        bones['r_calf'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    # 手臂擺動
    if 'l_upperarm' in bones:
        l_arm_rot = 0.3 * math.sin(t + math.pi)
        bones['l_upperarm'].rotation_euler = (l_arm_rot, 0, 0)
        bones['l_upperarm'].keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if 'r_upperarm' in bones:
        r_arm_rot = 0.3 * math.sin(t)
        bones['r_upperarm'].rotation_euler = (r_arm_rot, 0, 0)
        bones['r_upperarm'].keyframe_insert(data_path="rotation_euler", frame=frame)

print("✅ 走路動畫完成")

# === 動畫 3: 坐下（Sit Down）===
print("\n=== 製作坐下動畫 ===")
action_sit = bpy.data.actions.new(name="SitDown")
action_sit.use_fake_user = True

total_frames = 60  # 2.5 秒

keyframes = [
    (0, 0, 0, 0, 0),      # 站立
    (20, -0.3, 0.2, 0.8, 0.1),  # 彎腰
    (40, -0.8, 0.6, 1.2, 0.2),  # 下蹲
    (60, -1.0, 0.8, 1.4, 0.3),  # 坐下
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

print("✅ 坐下動畫完成")

# === 動畫 4: 起立（Stand Up）===
print("\n=== 製作起立動畫 ===")
action_stand = bpy.data.actions.new(name="StandUp")
action_stand.use_fake_user = True

total_frames = 60  # 2.5 秒

# 反向關鍵幀
keyframes = [
    (0, -1.0, 0.8, 1.4, 0.3),   # 坐著
    (20, -0.8, 0.6, 1.2, 0.2),  # 準備起身
    (40, -0.3, 0.2, 0.8, 0.1),  # 起身
    (60, 0, 0, 0, 0),           # 站立
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

print("✅ 起立動畫完成")

# 回到物件模式
bpy.ops.object.mode_set(mode='OBJECT')

# 保存
output_file = '/mnt/e_drive/claude-office/blender/exports/character_with_animations.glb'
bpy.ops.export_scene.gltf(
    filepath=output_file,
    export_format='GLB',
    export_cameras=False,
    export_lights=False,
    export_draco_mesh_compression_enable=False
)

print(f"\n✅ 導出完成: {output_file}")
print("包含動畫:")
print("  - Idle（待機）")
print("  - Walk（走路）")
print("  - SitDown（坐下）")
print("  - StandUp（起立）")
