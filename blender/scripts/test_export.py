import bpy
import os

print("\n=== 測試導出 ===")

# 清空場景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 載入原始模型
bpy.ops.import_scene.gltf(filepath='/mnt/e_drive/claude-office/assets/characters/3d/realistic_female_character__game-ready_3d_model.glb')

armature = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
print(f"✅ 骨骼: {armature.name}")

# 列出大腿和小腿的 head/tail 位置
bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode='EDIT')

l_thigh = armature.data.edit_bones.get('CC_Base_L_Thigh_05')
l_calf = armature.data.edit_bones.get('CC_Base_L_Calf_06')
l_foot = armature.data.edit_bones.get('CC_Base_L_Foot_07')

if l_thigh:
    print(f"\nL_Thigh head: {l_thigh.head}, tail: {l_thigh.tail}")
    print(f"L_Thigh length: {l_thigh.length}")
if l_calf:
    print(f"L_Calf head: {l_calf.head}, tail: {l_calf.tail}")
    print(f"L_Calf length: {l_calf.length}")
if l_foot:
    print(f"L_Foot head: {l_foot.head}, tail: {l_foot.tail}")

bpy.ops.object.mode_set(mode='OBJECT')

# 直接導出，不做任何修改
output = '/mnt/e_drive/claude-office/blender/exports/test_export_original.glb'
bpy.ops.export_scene.gltf(
    filepath=output,
    export_format='GLB',
    export_cameras=False,
    export_lights=False,
    export_animations=True,
    export_skins=True,
    export_morph=False
)

size = os.path.getsize(output) / 1024 / 1024
print(f"\n✅ 導出成功！大小: {size:.1f} MB")
