#!/usr/bin/env python3
"""
轉換 GLB → FBX（給 Mixamo 使用）
"""
import sys
sys.path.insert(0, '/mnt/e_drive/claude-office/.venv/lib/python3.12/site-packages')

import bpy
import os

# 清空場景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 導入 GLB
input_path = '/mnt/e_drive/claude-office/assets/characters/3d/realistic_female_character__game-ready_3d_model.glb'
output_path = '/mnt/e_drive/claude-office/assets/characters/3d/realistic_female_character_for_mixamo.fbx'

print(f"導入: {input_path}")
bpy.ops.import_scene.gltf(filepath=input_path)

# 導出 FBX
print(f"導出: {output_path}")
bpy.ops.export_scene.fbx(
    filepath=output_path,
    use_selection=False,
    global_scale=1.0,
    apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_ALL',
    object_types={'ARMATURE', 'MESH', 'EMPTY'},
    use_armature_deform_only=True,
    add_leaf_bones=False
)

print(f"✅ 完成！大小: {os.path.getsize(output_path) / 1024 / 1024:.1f} MB")
