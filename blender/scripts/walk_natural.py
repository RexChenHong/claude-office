import bpy
import math
from mathutils import Quaternion, Vector

print("\n=== 正確的自然走路動畫 ===")

# 載入原始模型
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.import_scene.gltf(filepath='/mnt/e_drive/claude-office/assets/characters/3d/realistic_female_character__game-ready_3d_model.glb')

armature = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
print(f"✅ 骨骼: {armature.name}")

# 切換到姿勢模式
bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode='POSE')

if not armature.animation_data:
    armature.animation_data.create()

# 設置原始動畫為基準，保存每個骨骼的基準
if bpy.data.actions:
    armature.animation_data.action = bpy.data.actions[0]
    bpy.context.scene.frame_set(0)

# 找所有主要骨骼
bones_list = [
    'CC_Base_Hip_03',
    'CC_Base_Spine01', 'CC_Base_Spine02',
    'CC_Base_L_Thigh_05', 'CC_Base_L_Calf_06',
    'CC_Base_R_Thigh_05', 'CC_Base_R_Calf_06',
    'CC_Base_L_Upperarm_01', 'CC_Base_L_Forearm_01',
    'CC_Base_R_Upperarm_01', 'CC_Base_R_Forearm_01'
]

# 保存每個骨骼的基準四元數
bone_bases = {}
for bone_name in bones_list:
    bone = armature.pose.bones.get(bone_name)
    if bone:
        bone_bases[bone_name] = {
            'bone': bone,
            'base_quat': Quaternion(bone.rotation_quaternion),
            'base_loc': Vector(bone.location)
        }
        print(f"{bone_name}: base_quat=({bone.rotation_quaternion.w:.5f}, {bone.rotation_quaternion.x:.5f}, {bone.rotation_quaternion.y:.5f}, {bone.rotation_quaternion.z:.5f})")

print(f"\n✅ 保存了 {len(bone_bases)} 個骨骼的基準")

# ============================================
# Walk 動畫（自然走路，基於每個骨骼的基準）
# ============================================
print("\n【1/1】Walk 動畫（自然走路）...")

action_walk = bpy.data.actions.new(name="Walk")
armature.animation_data.action = action_walk

bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = 48

for frame in range(0, 49, 2):
    bpy.context.scene.frame_set(frame)
    t = frame / 48 * 2 * math.pi  # 一個完整的走路循環

    # Hip 上下移動（走路時身體會起伏）
    if 'CC_Base_Hip_03' in bone_bases:
        bone_data = bone_bases['CC_Base_Hip_03']
        bone = bone_data['bone']
        base_loc = bone_data['base_loc']
        base_quat = bone_data['base_quat']
        
        # 身體起伏（最高點在單腳站立時）
        hip_bob = 0.05 * abs(math.sin(t * 2))
        
        # 身體左右搖擺
        hip_sway = 0.03 * math.sin(t)
        
        new_loc = base_loc + Vector((hip_sway, hip_bob, 0))
        bone.location = new_loc
        bone.keyframe_insert(data_path="location", frame=frame)
        
        # Hip 輕微旋轉（y, z 分量）
        delta_y = 0.02 * math.sin(t)
        delta_z = 0.02 * math.cos(t)
        new_quat = Quaternion((base_quat.w, base_quat.x, base_quat.y + delta_y, base_quat.z + delta_z))
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    # 左大腿（向前向後擺動）
    if 'CC_Base_L_Thigh_05' in bone_bases:
        bone_data = bone_bases['CC_Base_L_Thigh_05']
        bone = bone_data['bone']
        base_quat = bone_data['base_quat']
        
        # 走路時大腿向前向後旋轉
        # 使用基準四元數 + 增量
        delta_y = 0.3 * math.sin(t)
        delta_z = 0.2 * math.cos(t)
        
        new_quat = Quaternion((base_quat.w, base_quat.x, base_quat.y + delta_y, base_quat.z + delta_z))
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    # 右大腿（與左大腿相反）
    if 'CC_Base_R_Thigh_05' in bone_bases:
        bone_data = bone_bases['CC_Base_R_Thigh_05']
        bone = bone_data['bone']
        base_quat = bone_data['base_quat']
        
        delta_y = 0.3 * math.sin(t + math.pi)
        delta_z = 0.2 * math.cos(t + math.pi)
        
        new_quat = Quaternion((base_quat.w, base_quat.x, base_quat.y + delta_y, base_quat.z + delta_z))
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    # 左小腿（膝蓋彎曲）
    if 'CC_Base_L_Calf_06' in bone_bases:
        bone_data = bone_bases['CC_Base_L_Calf_06']
        bone = bone_data['bone']
        base_quat = bone_data['base_quat']
        
        # 膝蓋彎曲（大腿向後時彎曲）
        knee_bend = max(0, 0.5 * math.sin(t + 0.5))
        
        new_quat = Quaternion((base_quat.w - knee_bend, base_quat.x + knee_bend * 0.5, base_quat.y, base_quat.z))
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    # 右小腿（與左小腿相反）
    if 'CC_Base_R_Calf_06' in bone_bases:
        bone_data = bone_bases['CC_Base_R_Calf_06']
        bone = bone_data['bone']
        base_quat = bone_data['base_quat']
        
        knee_bend = max(0, 0.5 * math.sin(t + math.pi + 0.5))
        
        new_quat = Quaternion((base_quat.w - knee_bend, base_quat.x + knee_bend * 0.5, base_quat.y, base_quat.z))
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    # 左手臂（與右腿同步，自然擺動）
    if 'CC_Base_L_Upperarm_01' in bone_bases:
        bone_data = bone_bases['CC_Base_L_Upperarm_01']
        bone = bone_data['bone']
        base_quat = bone_data['base_quat']
        
        # 手臂前後擺動（與右腿同步）
        arm_swing = 0.2 * math.sin(t + math.pi)
        
        new_quat = Quaternion((base_quat.w, base_quat.x, base_quat.y + arm_swing, base_quat.z))
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    # 右手臂（與左腿同步）
    if 'CC_Base_R_Upperarm_01' in bone_bases:
        bone_data = bone_bases['CC_Base_R_Upperarm_01']
        bone = bone_data['bone']
        base_quat = bone_data['base_quat']
        
        arm_swing = 0.2 * math.sin(t)
        
        new_quat = Quaternion((base_quat.w, base_quat.x, base_quat.y + arm_swing, base_quat.z))
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    # 脊椎輕微旋轉（身體轉動）
    if 'CC_Base_Spine02' in bone_bases:
        bone_data = bone_bases['CC_Base_Spine02']
        bone = bone_data['bone']
        base_quat = bone_data['base_quat']
        
        # 身體隨走路轉動
        spine_twist = 0.03 * math.sin(t)
        
        new_quat = Quaternion((base_quat.w, base_quat.x, base_quat.y + spine_twist, base_quat.z))
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

print("✅ Walk 完成")

# 回到物件模式
bpy.ops.object.mode_set(mode='OBJECT')

print(f"\n總動畫: {len(bpy.data.actions)} 個")

# 導出
output = '/mnt/e_drive/claude-office/blender/exports/character_walk_natural.glb'
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
print("\n✅ 關鍵修正：基於每個骨骼的實際基準四元數，所有分量都變化")
