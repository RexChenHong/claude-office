#!/usr/bin/env python3
"""
導出 GLTF 格式
"""

import bpy

# 導出 GLTF
bpy.ops.export_scene.gltf(
    filepath='/mnt/e_drive/claude-office/blender/exports/desk.glb',
    export_format='GLB',
    export_cameras=False,
    export_lights=False,
    export_extras=True
)

print("GLTF 導出完成！")
print("檔案路徑：/mnt/e_drive/claude-office/blender/exports/desk.glb")
