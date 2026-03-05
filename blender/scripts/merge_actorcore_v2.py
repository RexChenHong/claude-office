#!/usr/bin/env python3
import sys
sys.path.insert(0, '/mnt/e_drive/claude-office/.venv/lib/python3.12/site-packages')

import bpy
import os

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 導入角色
print("=== 導入角色 ===")
bpy.ops.import_scene.fbx(filepath='/mnt/e_drive/claude-office/src/ui/public/actorcore/Actor/motion-dummy-female-643083/motion-dummy-female-643083.fbx')

# 導入動畫
print("\n=== 導入動畫 ===")
bpy.ops.import_scene.fbx(filepath='/mnt/e_drive/claude-office/src/ui/public/actorcore/Motion/catwalk-625492/catwalk-loop-378982.fbx')

print("\n=== 物件列表 ===")
for obj in bpy.data.objects:
    print(f"{obj.type}: {obj.name}")
    if obj.type == 'ARMATURE' and obj.animation_data:
        print(f"  當前動作: {obj.animation_data.action}")

print("\n=== 動作列表 ===")
for action in bpy.data.actions:
    print(f"  {action.name} ({action.frame_range.x:.0f}-{action.frame_range.y:.0f})")

# 導出
output = '/mnt/e_drive/claude-office/src/ui/public/actorcore/catwalk.glb'
print(f"\n=== 導出: {output} ===")
bpy.ops.export_scene.gltf(
    filepath=output,
    export_format='GLB',
    use_selection=False
)

print(f"✅ 完成！大小: {os.path.getsize(output) / 1024:.1f} KB")
