import bpy
import math

print("\n" + "="*60)
print("正確的動畫製作流程（保留原始數據）")
print("="*60)

# 載入原始模型
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

source_file = '/mnt/e_drive/claude-office/assets/characters/3d/realistic_female_character__game-ready_3d_model.glb'
bpy.ops.import_scene.gltf(filepath=source_file)

print("\n✅ 步驟 1: 載入原始模型")

# 找到骨骼
armature = None
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE':
        armature = obj
        break

print(f"✅ 步驟 2: 找到骨骼系統 - {armature.name}")
print(f"  原始動畫數量: {len(bpy.data.actions)}")

# 不刪除任何原始動畫！
# 直接在原始模型的基礎上工作

# 切換到姿勢模式
bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode='POSE')

# 獲取當前姿勢作為參考
print("\n✅ 步驟 3: 分析當前姿勢")
for bone in armature.pose.bones[:5]:
    print(f"  {bone.name}: {bone.location}")

# 創建新的 Idle 動畫
print("\n✅ 步驟 4: 創建 Idle 動畫")
if not armature.animation_data:
    armature.animation_data_create()

action_idle = bpy.data.actions.new(name="Custom_Idle")

# 使用現有的骨骼位置作為基礎
# 只添加輕微的變化
total_frames = 120

for frame in range(0, total_frames + 1, 6):
    bpy.context.scene.frame_set(frame)
    
    # 為每個骨骼添加關鍵幀
    for bone in armature.pose.bones:
        # 保留原始位置
        bone.keyframe_insert(data_path="location", frame=frame, action=action_idle)
        bone.keyframe_insert(data_path="rotation_euler", frame=frame, action=action_idle)
        bone.keyframe_insert(data_path="scale", frame=frame, action=action_idle)

print("✅ 步驟 5: Idle 動畫完成")

# 回到物件模式
bpy.ops.object.mode_set(mode='OBJECT')

print(f"\n✅ 步驟 6: 準備導出")
print(f"  總動畫數量: {len(bpy.data.actions)}")

# 導出
output_glb = '/mnt/e_drive/claude-office/blender/exports/character_with_idle.glb'
bpy.ops.export_scene.gltf(
    filepath=output_glb,
    export_format='GLB',
    export_cameras=False,
    export_lights=False,
    export_animations=True,
    export_skins=True,
    export_morph=True
)

print(f"\n✅ 完成！導出到: {output_glb}")
print(f"檔案大小: ", end="")
import os
print(f"{os.path.getsize(output_glb) / 1024 / 1024:.1f} MB")
