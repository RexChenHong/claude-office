#!/usr/bin/env python3
"""
合併 ActorCore 角色和動畫 → GLB
"""
import sys
sys.path.insert(0, '/mnt/e_drive/claude-office/.venv/lib/python3.12/site-packages')

import bpy
import os

# 清空場景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 導入角色
actor_fbx = '/mnt/e_drive/claude-office/src/ui/public/actorcore/Actor/motion-dummy-female-643083/motion-dummy-female-643083.fbx'
print(f"導入角色: {actor_fbx}")
bpy.ops.import_scene.fbx(filepath=actor_fbx)

# 導入動畫
motion_fbx = '/mnt/e_drive/claude-office/src/ui/public/actorcore/Motion/catwalk-625492/catwalk-loop-378982.fbx'
print(f"導入動畫: {motion_fbx}")
bpy.ops.import_scene.fbx(filepath=motion_fbx)

# 檢查動畫
armature = bpy.data.objects['mixamo1']
if armature.animation_data:
    action = armature.animation_data.action
    if action:
        print(f"✅ 動畫: {action.name} ({action.frame_range.x}, {action.frame_range.y})")

# 導出 GLB
output_glb = '/mnt/e_drive/claude-office/src/ui/public/actorcore/catwalk_loop.glb'
print(f"導出: {output_glb}")
bpy.ops.export_scene.gltf(
    filepath=output_glb,
    export_format='GLB',
    use_selection=False
)

print(f"✅ 完成！大小: {os.path.getsize(output_glb) / 1024:.1f} KB")
