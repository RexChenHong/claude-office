import bpy
import math
from mathutils import Quaternion, Vector, Euler

print("\n=== 基於原始動畫的正確方法 ===")

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

# 設置原始動畫為基準，並保存所有骨骼的基準狀態
if bpy.data.actions:
    armature.animation_data.action = bpy.data.actions[0]
    bpy.context.scene.frame_set(0)

# 找所有主要骨骼
bones_list = [
    'CC_Base_Hip_03', 'CC_Base_Spine01', 'CC_Base_Spine02',
    'CC_Base_L_Thigh_05', 'CC_Base_L_Calf_06', 
    'CC_Base_R_Thigh_05', 'CC_Base_R_Calf_06',
    'CC_Base_L_Upperarm_01', 'CC_Base_L_Forearm_01',
    'CC_Base_R_Upperarm_01', 'CC_Base_R_Forearm_01'
]

# 保存所有骨骼的基準
bone_bases = {}
for bone_name in bones_list:
    bone = armature.pose.bones.get(bone_name)
    if bone:
        bone_bases[bone_name] = {
            'bone': bone,
            'base_quat': Quaternion(bone.rotation_quaternion),
            'base_loc': Vector(bone.location)
        }

print(f"✅ 保存了 {len(bone_bases)} 個骨骼的基準")

# ============================================
# Idle 動畫（完全複製原始動畫的行為）
# ============================================
print("\n【1/5】Idle 動畫...")

action_idle = bpy.data.actions.new(name="Idle")
armature.animation_data.action = action_idle

bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = 120

for frame in range(0, 121, 10):
    bpy.context.scene.frame_set(frame)
    t = frame / 120

    # Hip 上下移動（基於基準）
    if 'CC_Base_Hip_03' in bone_bases:
        bone_data = bone_bases['CC_Base_Hip_03']
        bone = bone_data['bone']
        base_loc = bone_data['base_loc']
        base_quat = bone_data['base_quat']
        
        # 位置增量（在基準上增加）
        new_loc = base_loc + Vector((0, 0.1 * math.sin(t * 2 * math.pi), 0))
        bone.location = new_loc
        bone.keyframe_insert(data_path="location", frame=frame)
        
        # 四元數保持基準（原始動畫四元數變化很小）
        bone.rotation_quaternion = base_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    # Spine2 輕微旋轉
    if 'CC_Base_Spine02' in bone_bases:
        bone_data = bone_bases['CC_Base_Spine02']
        bone = bone_data['bone']
        base_quat = bone_data['base_quat']
        
        # 小幅度增量（y, z 變化，保持 w, x）
        delta_y = 0.02 * math.sin(t * 2 * math.pi)
        delta_z = -0.02 * math.sin(t * 2 * math.pi)
        
        # 直接修改四元數分量
        new_quat = Quaternion((base_quat.w, base_quat.x, base_quat.y + delta_y, base_quat.z + delta_z))
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

print("✅ Idle 完成")

# ============================================
# Walk 動畫
# ============================================
print("\n【2/5】Walk 動畫...")

action_walk = bpy.data.actions.new(name="Walk")
armature.animation_data.action = action_walk

bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = 48

for frame in range(0, 49, 4):
    bpy.context.scene.frame_set(frame)
    t = frame / 48 * 2 * math.pi

    # Hip 上下
    if 'CC_Base_Hip_03' in bone_bases:
        bone_data = bone_bases['CC_Base_Hip_03']
        bone = bone_data['bone']
        base_loc = bone_data['base_loc']
        base_quat = bone_data['base_quat']
        
        new_loc = base_loc + Vector((0, 0.15 * abs(math.sin(t)), 0))
        bone.location = new_loc
        bone.keyframe_insert(data_path="location", frame=frame)
        
        bone.rotation_quaternion = base_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    # 大腿（左）
    if 'CC_Base_L_Thigh_05' in bone_bases:
        bone_data = bone_bases['CC_Base_L_Thigh_05']
        bone = bone_data['bone']
        base_quat = bone_data['base_quat']
        
        # 直接修改 x 分量（X 軸旋轉）
        delta_x = 0.05 * math.sin(t)
        new_quat = Quaternion((base_quat.w, base_quat.x + delta_x, base_quat.y, base_quat.z))
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    # 大腿（右）
    if 'CC_Base_R_Thigh_05' in bone_bases:
        bone_data = bone_bases['CC_Base_R_Thigh_05']
        bone = bone_data['bone']
        base_quat = bone_data['base_quat']
        
        delta_x = 0.05 * math.sin(t + math.pi)
        new_quat = Quaternion((base_quat.w, base_quat.x + delta_x, base_quat.y, base_quat.z))
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    # 小腿（左）
    if 'CC_Base_L_Calf_06' in bone_bases:
        bone_data = bone_bases['CC_Base_L_Calf_06']
        bone = bone_data['bone']
        base_quat = bone_data['base_quat']
        
        delta_x = max(0, 0.05 * math.sin(t + 0.5))
        new_quat = Quaternion((base_quat.w, base_quat.x + delta_x, base_quat.y, base_quat.z))
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    # 小腿（右）
    if 'CC_Base_R_Calf_06' in bone_bases:
        bone_data = bone_bases['CC_Base_R_Calf_06']
        bone = bone_data['bone']
        base_quat = bone_data['base_quat']
        
        delta_x = max(0, 0.05 * math.sin(t + math.pi + 0.5))
        new_quat = Quaternion((base_quat.w, base_quat.x + delta_x, base_quat.y, base_quat.z))
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    # 手臂擺動（左）
    if 'CC_Base_L_Upperarm_01' in bone_bases:
        bone_data = bone_bases['CC_Base_L_Upperarm_01']
        bone = bone_data['bone']
        base_quat = bone_data['base_quat']
        
        delta_x = 0.05 * math.sin(t + math.pi)
        new_quat = Quaternion((base_quat.w, base_quat.x + delta_x, base_quat.y, base_quat.z))
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    # 手臂擺動（右）
    if 'CC_Base_R_Upperarm_01' in bone_bases:
        bone_data = bone_bases['CC_Base_R_Upperarm_01']
        bone = bone_data['bone']
        base_quat = bone_data['base_quat']
        
        delta_x = 0.05 * math.sin(t)
        new_quat = Quaternion((base_quat.w, base_quat.x + delta_x, base_quat.y, base_quat.z))
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

print("✅ Walk 完成")

# 回到物件模式
bpy.ops.object.mode_set(mode='OBJECT')

print(f"\n總動畫: {len(bpy.data.actions)} 個")

# 導出
output = '/mnt/e_drive/claude-office/blender/exports/character_final_animation.glb'
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
print("\n✅ 關鍵修正：基於原始基準的直接四元數分量修改")
