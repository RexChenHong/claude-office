import bpy
import math

# 啟用 Rigify 插件
bpy.ops.preferences.addon_enable(module='rigify')

# 清除場景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 角色配置（原神風格）
CHARACTER_CONFIG = {
    'sakura': {
        'name': '櫻',
        'hair_color': (1.0, 0.714, 0.757),  # 粉色
        'eye_color': (0.255, 0.412, 0.882),  # 藍色
        'skin_color': (1.0, 0.894, 0.769),   # 膚色
        'cloth_color': (1.0, 1.0, 1.0),      # 白色
        'accent_color': (0.255, 0.412, 0.882)  # 藍色
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

def create_professional_character(char_id, config, offset_x):
    """創建專業級別的角色模型（使用細分曲面）"""
    
    # 創建材質
    def create_material(name, color, metallic=0.0, roughness=0.7):
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs['Base Color'].default_value = (*color, 1.0)
        bsdf.inputs['Metallic'].default_value = metallic
        bsdf.inputs['Roughness'].default_value = roughness
        return mat
    
    skin_mat = create_material(f"{char_id}_skin", config['skin_color'], 0.0, 0.5)
    hair_mat = create_material(f"{char_id}_hair", config['hair_color'], 0.2, 0.4)
    eye_mat = create_material(f"{char_id}_eye", config['eye_color'], 0.1, 0.2)
    cloth_mat = create_material(f"{char_id}_cloth", config['cloth_color'], 0.0, 0.8)
    accent_mat = create_material(f"{char_id}_accent", config['accent_color'], 0.3, 0.3)
    
    # === 頭部（更精細的球體）===
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(offset_x, 0, 1.55))
    head = bpy.context.active_object
    head.scale = (1.0, 0.95, 1.1)
    head.name = f"{char_id}_head"
    
    # 添加細分曲面
    subsurf = head.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 3
    
    # 添加平滑著色
    bpy.ops.object.shade_smooth()
    head.data.materials.append(skin_mat)
    
    # === 頭髮（多層次）===
    # 主體頭髮
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.135, location=(offset_x, 0.01, 1.56))
    hair_main = bpy.context.active_object
    hair_main.scale = (1.1, 1.0, 1.2)
    hair_main.name = f"{char_id}_hair_main"
    
    subsurf = hair_main.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    bpy.ops.object.shade_smooth()
    hair_main.data.materials.append(hair_mat)
    
    # 劉海
    bpy.ops.mesh.primitive_cube_add(size=0.15, location=(offset_x, -0.1, 1.62))
    bangs = bpy.context.active_object
    bangs.scale = (1.2, 0.3, 0.4)
    bangs.rotation_euler = (0.2, 0, 0)
    bangs.name = f"{char_id}_bangs"
    
    subsurf = bangs.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    bpy.ops.object.shade_smooth()
    bangs.data.materials.append(hair_mat)
    
    # === 眼睛（更精細）===
    for side in [-1, 1]:
        # 眼白
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.025, location=(offset_x + side * 0.045, -0.1, 1.57))
        eye_white = bpy.context.active_object
        eye_white.name = f"{char_id}_eye_white_{'left' if side == -1 else 'right'}"
        eye_white.data.materials.append(skin_mat)
        
        # 瞳孔
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.015, location=(offset_x + side * 0.045, -0.12, 1.57))
        eye_iris = bpy.context.active_object
        eye_iris.name = f"{char_id}_eye_iris_{'left' if side == -1 else 'right'}"
        eye_iris.data.materials.append(eye_mat)
    
    # === 身體（使用曲線和細分）===
    # 軀幹
    bpy.ops.mesh.primitive_cube_add(size=0.3, location=(offset_x, 0, 1.25))
    torso = bpy.context.active_object
    torso.scale = (1.0, 0.8, 1.5)
    torso.name = f"{char_id}_torso"
    
    subsurf = torso.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    bpy.ops.object.shade_smooth()
    torso.data.materials.append(cloth_mat)
    
    # 腰部
    bpy.ops.mesh.primitive_cube_add(size=0.25, location=(offset_x, 0, 0.95))
    waist = bpy.context.active_object
    waist.scale = (1.0, 0.8, 0.8)
    waist.name = f"{char_id}_waist"
    
    subsurf = waist.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    bpy.ops.object.shade_smooth()
    waist.data.materials.append(cloth_mat)
    
    # === 裙子（多層次）===
    # 上層
    bpy.ops.mesh.primitive_cone_add(radius1=0.2, radius2=0.15, depth=0.35, location=(offset_x, 0, 0.75))
    skirt_top = bpy.context.active_object
    skirt_top.name = f"{char_id}_skirt_top"
    
    subsurf = skirt_top.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    bpy.ops.object.shade_smooth()
    skirt_top.data.materials.append(cloth_mat)
    
    # 下層
    bpy.ops.mesh.primitive_cone_add(radius1=0.25, radius2=0.2, depth=0.3, location=(offset_x, 0, 0.5))
    skirt_bottom = bpy.context.active_object
    skirt_bottom.name = f"{char_id}_skirt_bottom"
    
    subsurf = skirt_bottom.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    bpy.ops.object.shade_smooth()
    skirt_bottom.data.materials.append(cloth_mat)
    
    # === 手臂（分段式）===
    for side in [-1, 1]:
        # 肩膀
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.04, location=(offset_x + side * 0.2, 0, 1.45))
        shoulder = bpy.context.active_object
        shoulder.name = f"{char_id}_shoulder_{'left' if side == -1 else 'right'}"
        shoulder.data.materials.append(cloth_mat)
        
        # 上臂
        bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.25, location=(offset_x + side * 0.22, 0, 1.3))
        upper_arm = bpy.context.active_object
        upper_arm.rotation_euler = (side * 0.2, 0, 0)
        upper_arm.name = f"{char_id}_upper_arm_{'left' if side == -1 else 'right'}"
        
        subsurf = upper_arm.modifiers.new(name="Subdivision", type='SUBSURF')
        subsurf.levels = 2
        upper_arm.data.materials.append(skin_mat)
        
        # 肘部
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.032, location=(offset_x + side * 0.24, 0, 1.15))
        elbow = bpy.context.active_object
        elbow.name = f"{char_id}_elbow_{'left' if side == -1 else 'right'}"
        elbow.data.materials.append(skin_mat)
        
        # 前臂
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.25, location=(offset_x + side * 0.26, 0, 1.0))
        forearm = bpy.context.active_object
        forearm.rotation_euler = (side * 0.2, 0, 0)
        forearm.name = f"{char_id}_forearm_{'left' if side == -1 else 'right'}"
        
        subsurf = forearm.modifiers.new(name="Subdivision", type='SUBSURF')
        subsurf.levels = 2
        forearm.data.materials.append(skin_mat)
        
        # 手掌
        bpy.ops.mesh.primitive_cube_add(size=0.06, location=(offset_x + side * 0.28, 0, 0.85))
        hand = bpy.context.active_object
        hand.scale = (0.8, 0.5, 1.2)
        hand.name = f"{char_id}_hand_{'left' if side == -1 else 'right'}"
        
        subsurf = hand.modifiers.new(name="Subdivision", type='SUBSURF')
        subsurf.levels = 2
        hand.data.materials.append(skin_mat)
    
    # === 腿部（分段式）===
    for side in [-1, 1]:
        # 大腿
        bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.4, location=(offset_x + side * 0.1, 0, 0.25))
        thigh = bpy.context.active_object
        thigh.name = f"{char_id}_thigh_{'left' if side == -1 else 'right'}"
        
        subsurf = thigh.modifiers.new(name="Subdivision", type='SUBSURF')
        subsurf.levels = 2
        thigh.data.materials.append(skin_mat)
        
        # 膝蓋
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(offset_x + side * 0.1, 0, 0.05))
        knee = bpy.context.active_object
        knee.name = f"{char_id}_knee_{'left' if side == -1 else 'right'}"
        knee.data.materials.append(skin_mat)
        
        # 小腿
        bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=0.4, location=(offset_x + side * 0.1, 0, -0.15))
        calf = bpy.context.active_object
        calf.name = f"{char_id}_calf_{'left' if side == -1 else 'right'}"
        
        subsurf = calf.modifiers.new(name="Subdivision", type='SUBSURF')
        subsurf.levels = 2
        calf.data.materials.append(skin_mat)
        
        # 腳踝
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.035, location=(offset_x + side * 0.1, 0, -0.35))
        ankle = bpy.context.active_object
        ankle.name = f"{char_id}_ankle_{'left' if side == -1 else 'right'}"
        ankle.data.materials.append(skin_mat)
        
        # 鞋子
        bpy.ops.mesh.primitive_cube_add(size=0.1, location=(offset_x + side * 0.1, -0.03, -0.4))
        shoe = bpy.context.active_object
        shoe.scale = (1.0, 1.8, 0.6)
        shoe.name = f"{char_id}_shoe_{'left' if side == -1 else 'right'}"
        
        subsurf = shoe.modifiers.new(name="Subdivision", type='SUBSURF')
        subsurf.levels = 1
        shoe.data.materials.append(cloth_mat)
    
    # === 裝飾品（領結/蝴蝶結）===
    bpy.ops.mesh.primitive_cube_add(size=0.08, location=(offset_x, -0.15, 1.38))
    bow = bpy.context.active_object
    bow.scale = (2.0, 0.4, 0.8)
    bow.name = f"{char_id}_bow"
    
    subsurf = bow.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    bow.data.materials.append(accent_mat)
    
    print(f"✅ 專業角色 {config['name']} 創建完成")

# 創建所有角色
for idx, (char_id, config) in enumerate(CHARACTER_CONFIG.items()):
    offset_x = idx * 2.0
    create_professional_character(char_id, config, offset_x)

print("✅ 所有專業角色創建完成！")

# 保存 Blender 檔案
bpy.ops.wm.save_as_mainfile(filepath="/mnt/e_drive/claude-office/blender/characters_v2_professional.blend")

# 導出每個角色為 GLB
for char_id, config in CHARACTER_CONFIG.items():
    # 選擇當前角色的所有物件
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.name.startswith(char_id):
            obj.select_set(True)
    
    # 導出 GLB
    export_path = f"/mnt/e_drive/claude-office/blender/exports/character_v2_{char_id}.glb"
    bpy.ops.export_scene.gltf(
        filepath=export_path,
        export_format='GLB',
        use_selection=True,
        export_cameras=False,
        export_lights=False,
        export_draco_mesh_compression_enable=False
    )
    print(f"✅ 導出 {config['name']} 到 {export_path}")

print("✅ 所有專業角色導出完成！")
