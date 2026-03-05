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

# 不要刪除原始動作！
# 保留 Calibration 動作作為基礎

# 切換到姿勢模式
bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode='POSE')

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

print(f"找到 {len(bone_map)} 個骨骼")

# 確保有 animation_data
if not armature.animation_data:
    armature.animation_data_create()

# === 動畫 1: Idle（待機）===
print("\n=== 製作 Idle 動畫 ===")
action_idle = bpy.data.actions.new(name="Idle")

# 從第一個 Calibration 動作複製基礎姿勢
if bpy.data.actions:
    base_action = bpy.data.actions[0]
    print(f"使用基礎動作: {base_action.name}")

total_frames = 120
for frame in range(0, total_frames + 1, 4):
    bpy.context.scene.frame_set(frame)
    
    # 輕微呼吸動作
    if 'spine2' in bone_map:
        breath = 0.05 * math.sin(frame * 2 * math.pi / total_frames)
        bone_map['spine2'].rotation_euler = (breath, 0, 0)
        bone_map['spine2'].keyframe_insert(data_path="rotation_euler", frame=frame, action=action_idle)
    
    # 輕微上下晃動
    if 'hip' in bone_map:
        offset = 0.02 * math.sin(frame * 2 * math.pi / total_frames)
        # 使用 Y 軸（前後）而非 Z 軸
        bone_map['hip'].location = (0, offset, 0)
        bone_map['hip'].keyframe_insert(data_path="location", frame=frame, action=action_idle)

print("✅ Idle 完成")

# 回到物件模式
bpy.ops.object.mode_set(mode='OBJECT')

# 導出
output_glb = '/mnt/e_drive/claude-office/blender/exports/character_test_simple.glb'
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
print(f"包含動畫: Idle")
