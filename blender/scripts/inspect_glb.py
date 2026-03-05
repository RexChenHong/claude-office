import bpy

print("\n=== 檢查 GLB 文件中的動畫 ===")

# 載入導出的文件
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

file = '/mnt/e_drive/claude-office/blender/exports/character_simple.glb'
bpy.ops.import_scene.gltf(filepath=file)

print(f"\n場景中的物件:")
for obj in bpy.data.objects:
    print(f"  - {obj.name} (類型: {obj.type})")

print(f"\n所有動畫動作:")
for action in bpy.data.actions:
    print(f"  - {action.name}")
    print(f"    幀範圍: {action.frame_range}")
    print(f"    曲線數量: {len(action.fcurves)}")

# 檢查骨骼
armature = None
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE':
        armature = obj
        break

if armature:
    print(f"\n骨骼系統: {armature.name}")
    print(f"骨骼數量: {len(armature.pose.bones)}")

    if armature.animation_data:
        print(f"當前動作: {armature.animation_data.action.name if armature.animation_data.action else '無'}")

    # 檢查第一個動畫的數據
    if bpy.data.actions:
        action = bpy.data.actions[0]
        print(f"\n第一個動畫 '{action.name}' 的詳細信息:")
        print(f"  - 幀開始: {action.frame_range.x}")
        print(f"  - 幀結束: {action.frame_range.y}")

        # 檢查前 5 個曲線
        for i, fcurve in enumerate(action.fcurves[:5]):
            print(f"  - 曲線 {i}: {fcurve.data_path} (骨骼: {fcurve.group.name if fcurve.group else '無組'})")
