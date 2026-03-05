#!/usr/bin/env python3
"""
轉換 ActorCore FBX → GLB（給 Three.js 使用）
"""
import sys
sys.path.insert(0, '/mnt/e_drive/claude-office/.venv/lib/python3.12/site-packages')

import bpy
import os

# 清空場景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 導入 FBX
input_fbx = '/mnt/e_drive/claude-office/src/ui/public/actorcore/Actor/motion-dummy-female-643083/motion-dummy-female-643083.fbx'
output_glb = '/mnt/e_drive/claude-office/src/ui/public/actorcore/actor.glb'

print(f"導入: {input_fbx}")
bpy.ops.import_scene.fbx(filepath=input_fbx)

# 導出 GLB
print(f"導出: {output_glb}")
bpy.ops.export_scene.gltf(
    filepath=output_glb,
    export_format='GLB',
    use_selection=False
)

print(f"✅ 完成！大小: {os.path.getsize(output_glb) / 1024:.1f} KB")
