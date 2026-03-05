import bpy
import math

# 清除場景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 角色配置
CHARACTER_CONFIG = {
    'sakura': {
        'name': '櫻',
        'hair_color': (1.0, 0.714, 0.757),  # 粉色
        'eye_color': (0.255, 0.412, 0.882),  # 藍色
        'skin_color': (1.0, 0.894, 0.769),   # 膚色
        'cloth_color': (1.0, 1.0, 1.0),      # 白色
        'accent_color': (0.255, 0.412, 0.882)  # 藍色蝴蝶結
    },
    'homura': {
        'name': '焰',
        'hair_color': (0.1, 0.1, 0.1),       # 黑色
        'eye_color': (0.8, 0.2, 0.2),        # 紅色
        'skin_color': (1.0, 0.894, 0.769),
        'cloth_color': (0.2, 0.2, 0.2),      # 黑色
        'accent_color': (0.8, 0.2, 0.2)      # 紅色
    },
    'ryo': {
        'name': '涼',
        'hair_color': (0.75, 0.75, 0.75),    # 銀色
        'eye_color': (0.5, 0.2, 0.8),        # 紫色
        'skin_color': (1.0, 0.894, 0.769),
        'cloth_color': (0.5, 0.5, 0.5),      # 灰色
        'accent_color': (0.5, 0.2, 0.8)      # 紫色
    },
    'koto': {
        'name': '琴',
        'hair_color': (1.0, 0.843, 0.0),     # 金色
        'eye_color': (0.2, 0.8, 0.2),        # 綠色
        'skin_color': (1.0, 0.894, 0.769),
        'cloth_color': (1.0, 0.843, 0.0),    # 黃色
        'accent_color': (0.2, 0.8, 0.2)      # 綠色
    },
    'yoi': {
        'name': '宵',
        'hair_color': (0.5, 0.2, 0.8),       # 紫色
        'eye_color': (1.0, 0.843, 0.0),      # 黃色
        'skin_color': (1.0, 0.894, 0.769),
        'cloth_color': (0.5, 0.2, 0.8),      # 紫色
        'accent_color': (1.0, 0.843, 0.0)    # 黃色
    }
}

def create_character(char_id, config, offset_x):
    """創建角色模型"""
    
    # 創建材質
    def create_material(name, color):
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs['Base Color'].default_value = (*color, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.7
        return mat
    
    skin_mat = create_material(f"{char_id}_skin", config['skin_color'])
    hair_mat = create_material(f"{char_id}_hair", config['hair_color'])
    eye_mat = create_material(f"{char_id}_eye", config['eye_color'])
    cloth_mat = create_material(f"{char_id}_cloth", config['cloth_color'])
    accent_mat = create_material(f"{char_id}_accent", config['accent_color'])
    
    # 創建頭部（橢圓形）
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(offset_x, 0, 1.55))
    head = bpy.context.active_object
    head.scale = (1.0, 0.9, 1.1)
    head.name = f"{char_id}_head"
    head.data.materials.append(skin_mat)
    
    # 創建頭髮（簡單的橢圓）
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(offset_x, 0, 1.56))
    hair = bpy.context.active_object
    hair.scale = (1.05, 1.0, 1.15)
    hair.name = f"{char_id}_hair"
    hair.data.materials.append(hair_mat)
    
    # 創建眼睛（兩個小球）
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.02, location=(offset_x + side * 0.05, -0.1, 1.58))
        eye = bpy.context.active_object
        eye.name = f"{char_id}_eye_{'left' if side == -1 else 'right'}"
        eye.data.materials.append(eye_mat)
    
    # 創建身體（膠囊形）
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.5, location=(offset_x, 0, 1.2))
    body = bpy.context.active_object
    body.name = f"{char_id}_body"
    body.data.materials.append(cloth_mat)
    
    # 創建裙擺（圓錐）
    bpy.ops.mesh.primitive_cone_add(radius1=0.18, radius2=0.12, depth=0.3, location=(offset_x, 0, 0.85))
    skirt = bpy.context.active_object
    skirt.name = f"{char_id}_skirt"
    skirt.data.materials.append(cloth_mat)
    
    # 創建手臂
    for side in [-1, 1]:
        # 上臂
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.25, location=(offset_x + side * 0.2, 0, 1.3))
        upper_arm = bpy.context.active_object
        upper_arm.rotation_euler = (0, side * 0.3, 0)
        upper_arm.name = f"{char_id}_upper_arm_{'left' if side == -1 else 'right'}"
        upper_arm.data.materials.append(skin_mat)
        
        # 下臂
        bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.25, location=(offset_x + side * 0.28, 0, 1.1))
        lower_arm = bpy.context.active_object
        lower_arm.rotation_euler = (0, side * 0.3, 0)
        lower_arm.name = f"{char_id}_lower_arm_{'left' if side == -1 else 'right'}"
        lower_arm.data.materials.append(skin_mat)
        
        # 手
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.03, location=(offset_x + side * 0.35, 0, 0.95))
        hand = bpy.context.active_object
        hand.name = f"{char_id}_hand_{'left' if side == -1 else 'right'}"
        hand.data.materials.append(skin_mat)
    
    # 創建腿
    for side in [-1, 1]:
        # 大腿
        bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.35, location=(offset_x + side * 0.08, 0, 0.55))
        thigh = bpy.context.active_object
        thigh.name = f"{char_id}_thigh_{'left' if side == -1 else 'right'}"
        thigh.data.materials.append(skin_mat)
        
        # 小腿
        bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.35, location=(offset_x + side * 0.08, 0, 0.2))
        calf = bpy.context.active_object
        calf.name = f"{char_id}_calf_{'left' if side == -1 else 'right'}"
        calf.data.materials.append(skin_mat)
        
        # 腳
        bpy.ops.mesh.primitive_cube_add(size=0.08, location=(offset_x + side * 0.08, -0.02, 0.04))
        foot = bpy.context.active_object
        foot.scale = (1.0, 1.5, 0.5)
        foot.name = f"{char_id}_foot_{'left' if side == -1 else 'right'}"
        foot.data.materials.append(cloth_mat)
    
    # 創建蝴蝶結/裝飾（在胸口）
    bpy.ops.mesh.primitive_cube_add(size=0.08, location=(offset_x, -0.12, 1.35))
    bow = bpy.context.active_object
    bow.scale = (1.5, 0.3, 0.8)
    bow.name = f"{char_id}_bow"
    bow.data.materials.append(accent_mat)
    
    print(f"✅ 角色 {config['name']} 創建完成")

# 創建所有角色
for idx, (char_id, config) in enumerate(CHARACTER_CONFIG.items()):
    offset_x = idx * 2.0  # 每個角色間隔 2 米
    create_character(char_id, config, offset_x)

print("✅ 所有角色創建完成！")

# 保存 Blender 檔案
bpy.ops.wm.save_as_mainfile(filepath="/mnt/e_drive/claude-office/blender/characters_v1.blend")

# 導出每個角色為 GLB
for char_id, config in CHARACTER_CONFIG.items():
    # 選擇當前角色的所有物件
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.name.startswith(char_id):
            obj.select_set(True)
    
    # 導出 GLB
    export_path = f"/mnt/e_drive/claude-office/blender/exports/character_{char_id}.glb"
    bpy.ops.export_scene.gltf(
        filepath=export_path,
        export_format='GLB',
        use_selection=True,
        export_cameras=False,
        export_lights=False,
        export_draco_mesh_compression_enable=False
    )
    print(f"✅ 導出 {config['name']} 到 {export_path}")

print("✅ 所有角色導出完成！")
