#!/usr/bin/env python3
"""
正確合併 ActorCore 角色和動畫
"""
import sys
sys.path.insert(0, '/mnt/e_drive/claude-office/.venv/lib/python3.12/site-packages')

import bpy
import os

# 清空場景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 導入角色
print("=== 導入角色 ===")
bpy.ops.import_scene.fbx(filepath='/mnt/e_drive/claude-office/src/ui/public/actorcore/Actor/motion-dummy-female-643083/motion-dummy-female-643083.fbx')

armature = bpy.data.objects['Armature']
print(f"骨骼: {armature.name}")

# 導入動畫
print("\n=== 導入動畫 ===")
bpy.ops.import_scene.fbx(filepath='/mnt/e_drive/claude-office/src/ui/public/actorcore/Motion/catwalk-625492/catwalk-loop-378982.fbx')

# 找到 catwalk 動畫
catwalk_action = None
for action in bpy.data.actions:
    if 'catwalk-loop' in action.name:
        catwalk_action = action
        print(f"✅ 找到動畫: {action.name}")
        break

if not catwalk_action:
    print("❌ 找不到 catwalk 動畫")
    for action in bpy.data.actions:
        print(f"  - {action.name}")

# 刪除重複的 Armature
print("\n=== 清理重複骨骼 ===")
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE' and obj.name != 'Armature':
        print(f"刪除: {obj.name}")
        bpy.data.objects.remove(obj)

# 確保骨骼有動畫
if catwalk_action and armature:
    if not armature.animation_data:
        armature.animation_data_create()
    armature.animation_data.action = catwalk_action
    print(f"✅ 設定動畫: {catwalk_action.name}")

# 只保留需要的動作
print("\n=== 動作列表 ===")
for action in bpy.data.actions:
    print(f"  {action.name}")

# 導出 GLB（確保導出動畫）
output = '/mnt/e_drive/claude-office/src/ui/public/actorcore/catwalk.glb'
print(f"\n=== 導出: {output} ===")

bpy.ops.export_scene.gltf(
    filepath=output,
    export_format='GLB',
    use_selection=False,
    export_animations=True,  # 確保導出動畫
    export_frame_range=False,  # 導出所有幀
    export_nla_strips=True,
    export_nla_strips_merged_animation_name="catwalk"
)

print(f"✅ 完成！大小: {os.path.getsize(output) / 1024:.1f} KB")
