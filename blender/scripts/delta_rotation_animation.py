import bpy
import math
from mathutils import Quaternion, Vector, Euler

print("\n=== 基於原始四元數的增量動畫 ===")

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

# 獲取 Hip 骨骼的原始四元數作為基準
hip = armature.pose.bones.get('CC_Base_Hip_03')
if hip:
    base_quat = hip.rotation_quaternion.copy()
    base_loc = hip.location.copy()
    print(f"\nHip 基準四元數: w={base_quat.w:.4f}, x={base_quat.x:.4f}, y={base_quat.y:.4f}, z={base_quat.z:.4f}")
    print(f"Hip 基準位置: {base_loc}")

# 找主要骨骼並獲取基準四元數
bones_base = {}
for b in armature.pose.bones:
    n = b.name.lower()
    if 'hip' in n and 'pelvis' not in n and 'bone' not in n:
        bones_base['hip'] = {'bone': b, 'base_quat': b.rotation_quaternion.copy(), 'base_loc': b.location.copy()}
    elif 'spine01' in n:
        bones_base['spine'] = {'bone': b, 'base_quat': b.rotation_quaternion.copy(), 'base_loc': b.location.copy()}
    elif 'spine02' in n:
        bones_base['spine2'] = {'bone': b, 'base_quat': b.rotation_quaternion.copy(), 'base_loc': b.location.copy()}

print(f"\n✅ 獲取了 {len(bones_base)} 個骨骼的基準四元數")

# ============================================
# Idle 動畫（使用增量旋轉）
# ============================================
print("\n【1/5】Idle 動畫（增量旋轉）...")

action_idle = bpy.data.actions.new(name="Idle_Delta")
armature.animation_data.action = action_idle

bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = 120

for frame in range(0, 121, 10):
    bpy.context.scene.frame_set(frame)
    t = frame / 120

    # Hip 上下移動（在基準位置上增量）
    if 'hip' in bones_base:
        bone_data = bones_base['hip']
        bone = bone_data['bone']
        base_loc = bone_data['base_loc']

        # 增量位置
        new_loc = base_loc + Vector((0, 0.1 * math.sin(t * 2 * math.pi), 0))
        bone.location = new_loc
        bone.keyframe_insert(data_path="location", frame=frame, group="Idle_Delta")

    # Spine2 輕微旋轉（在基準四元數上增量）
    if 'spine2' in bones_base:
        bone_data = bones_base['spine2']
        bone = bone_data['bone']
        base_quat = bone_data['base_quat']

        # 創建增量旋轉（X 軸 15 度）
        angle_rad = math.radians(15 * math.sin(t * 2 * math.pi))
        delta_euler = Euler((angle_rad, 0, 0), 'XYZ')
        delta_quat = delta_euler.to_quaternion()

        # 四元數乘法：base_quat @ delta_quat
        new_quat = base_quat @ delta_quat
        bone.rotation_quaternion = new_quat
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame, group="Idle_Delta")

print("✅ Idle 完成")

# ============================================
# Walk 動畫（使用增量旋轉）
# ============================================
print("\n【2/5】Walk 動畫（增量旋轉）...")

action_walk = bpy.data.actions.new(name="Walk_Delta")
armature.animation_data.action = action_walk

bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = 48

for frame in range(0, 49, 4):
    bpy.context.scene.frame_set(frame)
    t = frame / 48 * 2 * math.pi

    # Hip 上下移動
    if 'hip' in bones_base:
        bone_data = bones_base['hip']
        bone = bone_data['bone']
        base_loc = bone_data['base_loc']

        new_loc = base_loc + Vector((0, 0.15 * abs(math.sin(t)), 0))
        bone.location = new_loc
        bone.keyframe_insert(data_path="location", frame=frame, group="Walk_Delta")

print("✅ Walk 完成")

# 回到物件模式
bpy.ops.object.mode_set(mode='OBJECT')

print(f"\n總動畫: {len(bpy.data.actions)} 個")

# 導出
output = '/mnt/e_drive/claude-office/blender/exports/character_delta_rotation.glb'
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
print("\n✅ 關鍵修正：基於原始四元數的增量旋轉（四元數乘法）")
