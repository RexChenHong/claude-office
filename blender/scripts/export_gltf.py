#!/usr/bin/env python3
"""
導出 GLTF 格式（已修復 numpy 路徑問題）
"""

import sys
import os

# 修復 numpy 路徑問題
user_site = '/home/rex/.local/lib/python3.10/site-packages'
if user_site not in sys.path:
    sys.path.insert(0, user_site)

import bpy

# 預設輸出路徑
export_dir = '/mnt/e_drive/claude-office/blender/exports'
os.makedirs(export_dir, exist_ok=True)

# 使用當前 .blend 檔名作為輸出檔名
blend_name = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
if not blend_name:
    blend_name = 'untitled'

output_path = os.path.join(export_dir, f'{blend_name}.glb')

# 導出 GLTF
bpy.ops.export_scene.gltf(
    filepath=output_path,
    export_format='GLB',
    export_cameras=False,
    export_lights=False,
    export_extras=True
)

print(f"✅ GLTF 導出完成！")
print(f"檔案路徑：{output_path}")
