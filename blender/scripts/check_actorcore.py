#!/usr/bin/env python3
import sys
sys.path.insert(0, '/mnt/e_drive/claude-office/.venv/lib/python3.12/site-packages')

import bpy

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 導入角色
bpy.ops.import_scene.fbx(filepath='/mnt/e_drive/claude-office/src/ui/public/actorcore/Actor/motion-dummy-female-643083/motion-dummy-female-643083.fbx')

print("=== 物件列表 ===")
for obj in bpy.data.objects:
    print(f"{obj.type}: {obj.name}")
    if obj.type == 'ARMATURE':
        print(f"  動畫數據: {obj.animation_data}")

print("\n=== 動作列表 ===")
for action in bpy.data.actions:
    print(f"  {action.name}")
