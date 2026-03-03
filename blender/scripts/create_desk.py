#!/usr/bin/env python3
"""
Claude Office - Blender 桌子建模
學習練習：創建一個簡單的辦公桌
"""

import bpy
import math

def clear_scene():
    """清除場景中的所有物件"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    print("場景已清除")

def create_desk(x=0, y=0, z=0):
    """創建辦公桌"""
    # 創建群組
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    desk_group = bpy.context.active_object
    desk_group.name = "Desk"
    desk_group.location = (x, y, z)
    
    # 創建桌面
    bpy.ops.mesh.primitive_cube_add(size=1)
    desktop = bpy.context.active_object
    desktop.name = "Desktop"
    desktop.scale = (1.2, 0.6, 0.025)  # 1.2m x 0.6m x 0.025m
    desktop.location = (x, y, z + 0.75)
    
    # 設置桌面材質（木紋）
    mat_wood = bpy.data.materials.new(name="Wood_Material")
    mat_wood.use_nodes = True
    nodes = mat_wood.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.6, 0.4, 0.2, 1)  # 木色
    bsdf.inputs['Roughness'].default_value = 0.4
    desktop.data.materials.append(mat_wood)
    
    # 創建桌腿（4 個）
    leg_positions = [
        (x - 0.55, y - 0.25),
        (x - 0.55, y + 0.25),
        (x + 0.55, y - 0.25),
        (x + 0.55, y + 0.25),
    ]
    
    # 金屬材質
    mat_metal = bpy.data.materials.new(name="Metal_Material")
    mat_metal.use_nodes = True
    nodes = mat_metal.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.3, 0.3, 0.3, 1)  # 金屬灰
    bsdf.inputs['Metallic'].default_value = 0.9
    bsdf.inputs['Roughness'].default_value = 0.3
    
    for i, (leg_x, leg_y) in enumerate(leg_positions):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.725)
        leg = bpy.context.active_object
        leg.name = f"Leg_{i+1}"
        leg.location = (leg_x, leg_y, z + 0.3625)
        leg.data.materials.append(mat_metal)
    
    print(f"桌子創建完成：位置 ({x}, {y}, {z})")
    return desk_group

def main():
    """主程式"""
    print("=== Claude Office - Blender 桌子建模 ===")
    
    # 清除場景
    clear_scene()
    
    # 創建桌子
    create_desk(0, 0, 0)
    
    # 保存檔案
    bpy.ops.wm.save_as_mainfile(
        filepath="/mnt/e_drive/claude-office/blender/desk.blend"
    )
    
    print("建模完成！")
    print("檔案已保存：/mnt/e_drive/claude-office/blender/desk.blend")

if __name__ == "__main__":
    main()
