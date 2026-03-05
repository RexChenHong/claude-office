import bpy
import math
from mathutils import Quaternion, Vector

print("\n=== 修正後的自然走路動畫 ===")

# 載入原始模型
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.import_scene.gltf(filepath='/mnt/e_drive/claude-office/assets/characters/3d/realistic_female_character__game-ready_3d_model.glb')

armature = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
print(f"✅ 骨骼: {armature.name}")

# 列出所有相關骨骼
print(f"\n查找骨骼:")
thigh_bones = [b for b in armature.pose.bones if 'Thigh' in b.name and 'L_' in b.name or 'R_' in b.name]
calf_bones = [b for b in armature.pose.bones if 'Calf' in b.name and 'L_' in b.name or 'R_' in b.name]
arm_bones = [b for b in armature.pose.bones if 'Upperarm' in b.name and 'L_' in b.name or 'R_' in b.name]

print(f"大腿骨骼: {[b.name for b in thigh_bones[:4]]}")
print(f"小腿骨骼: {[b.name for b in calf_bones[:4]]}")
print(f"手臂骨骼: {[b.name for b in arm_bones[:4]]}")

# 切換到姿勢模式
bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode='POSE')

if not armature.animation_data:
    armature.animation_data.create()

# 設置原始動畫為基準，保存每個骨骼的基準
if bpy.data.actions:
    armature.animation_data.action = bpy.data.actions[0]
    bpy.context.scene.frame_set(0)

# 找所有主要骨骼（使用實際名稱）
bone_bases = {}

# Hip
hip = armature.pose.bones.get('CC_Base_Hip_03')
if hip:
    bone_bases['hip'] = {'bone': hip, 'base_quat': Quaternion(hip.rotation_quaternion), 'base_loc': Vector(hip.location)}

# Spine
spine = armature.pose.bones.get('CC_Base_Spine02')
if spine:
    bone_bases['spine'] = {'bone': spine, 'base_quat': Quaternion(spine.rotation_quaternion), 'base_loc': Vector(spine.location)}

# 左右大腿（注意：右側骨骼名稱後綴不同！）
l_thigh = armature.pose.bones.get('CC_Base_L_Thigh_05')
if l_thigh:
    bone_bases['l_thigh'] = {'bone': l_thigh, 'base_quat': Quaternion(l_thigh.rotation_quaternion), 'base_loc': Vector(l_thigh.location)}

r_thigh = armature.pose.bones.get('CC_Base_R_Thigh_020')  # 修正：_020 不是 _05
if r_thigh:
    bone_bases['r_thigh'] = {'bone': r_thigh, 'base_quat': Quaternion(r_thigh.rotation_quaternion), 'base_loc': Vector(r_thigh.location)}

# 左右小腿（注意：右側骨骼名稱後綴不同！）
l_calf = armature.pose.bones.get('CC_Base_L_Calf_06')
if l_calf:
    bone_bases['l_calf'] = {'bone': l_calf, 'base_quat': Quaternion(l_calf.rotation_quaternion), 'base_loc': Vector(l_calf.location)}

r_calf = armature.pose.bones.get('CC_Base_R_Calf_021')  # 修正：_021 不是 _06
if r_calf:
    bone_bases['r_calf'] = {'bone': r_calf, 'base_quat': Quaternion(r_calf.rotation_quaternion), 'base_loc': Vector(r_calf.location)}

# 左右手臂（注意：右側骨骼名稱後綴不同！）
l_arm = armature.pose.bones.get('CC_Base_L_Upperarm_052')
if l_arm:
    bone_bases['l_arm'] = {'bone': l_arm, 'base_quat': Quaternion(l_arm.rotation_quaternion), 'base_loc': Vector(l_arm.location)}

r_arm = armature.pose.bones.get('CC_Base_R_Upperarm_080')  # 修正：_080 不是 _01
if r_arm:
    bone_bases['r_arm'] = {'bone': r_arm, 'base_quat': Quaternion(r_arm.rotation_quaternion), 'base_loc': Vector(r_arm.location)}

# 左右前臂（新增）
l_forearm = armature.pose.bones.get('CC_Base_L_Forearm_053')
if l_forearm:
    bone_bases['l_forearm'] = {'bone': l_forearm, 'base_quat': Quaternion(l_forearm.rotation_quaternion), 'base_loc': Vector(l_forearm.location)}

r_forearm = armature.pose.bones.get('CC_Base_R_Forearm_081')  # 修正：_081 不是 _01
if r_forearm:
    bone_bases['r_forearm'] = {'bone': r_forearm, 'base_quat': Quaternion(r_forearm.rotation_quaternion), 'base_loc': Vector(r_forearm.location)}

print(f"\n✅ 保存了 {len(bone_bases)} 個骨骼的基準")

# ============================================
# Walk 動畫（修正版）
# ============================================
print("\n【1/1】Walk 動畫（修正版）...")

action_walk = bpy.data.actions.new(name="Walk")
armature.animation_data.action = action_walk

bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = 48

for frame in range(0, 49, 2):
    bpy.context.scene.frame_set(frame)
    t = frame / 48 * 2 * math.pi

    # Hip 上下移動
    if 'hip' in bone_bases:
        bone_data = bone_bases['hip']
        bone = bone_data['bone']
        base_loc = bone_data['base_loc']
        base_quat = bone_data['base_quat']
        
        hip_bob = 0.05 * abs(math.sin(t * 2))
        new_loc = base_loc + Vector((0, hip_bob, 0))
        bone.location = new_loc
        bone.keyframe_insert(data_path="location", frame=frame)
        
        bone.rotation_quaternion = base_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    # 左大腿（向前向後擺動）
    if 'l_thigh' in bone_bases:
        bone_data = bone_bases['l_thigh']
        bone = bone_data['bone']
        base_quat = bone_data['base_quat']
        
        # 使用原始四元數的變化
        # 根據原始動畫，大腿的 w, x, y, z 都在變化
        delta_w = 0.1 * math.sin(t)
        delta_x = 0.1 * math.cos(t)
        delta_y = 0.2 * math.sin(t)
        delta_z = 0.15 * math.cos(t)
        
        new_quat = Quaternion((
            base_quat.w + delta_w,
            base_quat.x + delta_x,
            base_quat.y + delta_y,
            base_quat.z + delta_z
        ))
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    # 右大腿（與左大腿相反）
    if 'r_thigh' in bone_bases:
        bone_data = bone_bases['r_thigh']
        bone = bone_data['bone']
        base_quat = bone_data['base_quat']
        
        delta_w = 0.1 * math.sin(t + math.pi)
        delta_x = 0.1 * math.cos(t + math.pi)
        delta_y = 0.2 * math.sin(t + math.pi)
        delta_z = 0.15 * math.cos(t + math.pi)
        
        new_quat = Quaternion((
            base_quat.w + delta_w,
            base_quat.x + delta_x,
            base_quat.y + delta_y,
            base_quat.z + delta_z
        ))
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    # 左小腿（膝蓋彎曲）
    if 'l_calf' in bone_bases:
        bone_data = bone_bases['l_calf']
        bone = bone_data['bone']
        base_quat = bone_data['base_quat']
        
        # 膝蓋彎曲（根據原始動畫，w 從 1 變到 0.4，x 從 0 變到 -0.9）
        knee_bend = max(0, 0.3 * math.sin(t + 0.5))
        
        new_quat = Quaternion((
            base_quat.w - knee_bend,
            base_quat.x + knee_bend * 0.8,
            base_quat.y,
            base_quat.z
        ))
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    # 右小腿（與左小腿相反）
    if 'r_calf' in bone_bases:
        bone_data = bone_bases['r_calf']
        bone = bone_data['bone']
        base_quat = bone_data['base_quat']
        
        knee_bend = max(0, 0.3 * math.sin(t + math.pi + 0.5))
        
        new_quat = Quaternion((
            base_quat.w - knee_bend,
            base_quat.x + knee_bend * 0.8,
            base_quat.y,
            base_quat.z
        ))
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    # 左手臂（與右腿同步）
    if 'l_arm' in bone_bases:
        bone_data = bone_bases['l_arm']
        bone = bone_data['bone']
        base_quat = bone_data['base_quat']
        
        # 手臂擺動
        delta_y = 0.2 * math.sin(t + math.pi)
        delta_z = 0.1 * math.cos(t + math.pi)
        
        new_quat = Quaternion((
            base_quat.w,
            base_quat.x,
            base_quat.y + delta_y,
            base_quat.z + delta_z
        ))
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    # 右手臂（與左腿同步）
    if 'r_arm' in bone_bases:
        bone_data = bone_bases['r_arm']
        bone = bone_data['bone']
        base_quat = bone_data['base_quat']
        
        delta_y = 0.2 * math.sin(t)
        delta_z = 0.1 * math.cos(t)
        
        new_quat = Quaternion((
            base_quat.w,
            base_quat.x,
            base_quat.y + delta_y,
            base_quat.z + delta_z
        ))
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    # Spine 轉動
    if 'spine' in bone_bases:
        bone_data = bone_bases['spine']
        bone = bone_data['bone']
        base_quat = bone_data['base_quat']
        
        delta_y = 0.03 * math.sin(t)
        
        new_quat = Quaternion((base_quat.w, base_quat.x, base_quat.y + delta_y, base_quat.z))
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

print("✅ Walk 完成")

# 回到物件模式
bpy.ops.object.mode_set(mode='OBJECT')

print(f"\n總動畫: {len(bpy.data.actions)} 個")

# 導出
output = '/mnt/e_drive/claude-office/blender/exports/character_walk_fixed.glb'
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
print("\n✅ 關鍵修正：檢查骨骼名稱，確保左右都存在")
