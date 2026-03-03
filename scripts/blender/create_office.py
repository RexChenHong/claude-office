#!/usr/bin/env python3
"""
Blender Office Scene Generator
使用 Blender Python API 創建辦公室場景
"""

import bpy
import math

def create_office_desk():
    """創建辦公桌"""
    # 清除場景
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # 創建桌面
    bpy.ops.mesh.primitive_cube_add()
    desk_top = bpy.context.active_object
    desk_top.name = "Desk_Top"
    desk_top.scale = (1.2, 0.6, 0.025)
    desk_top.location = (0, 0, 0.75)

    # 創建桌腿
    leg_positions = [(-0.5, -0.25, 0.375), (-0.5, 0.25, 0.375),
                     (0.5, -0.25, 0.375), (0.5, 0.25, 0.375)]

    for i, pos in enumerate(leg_positions):
        bpy.ops.mesh.primitive_cube_add()
        leg = bpy.context.active_object
        leg.name = f"Desk_Leg_{i+1}"
        leg.scale = (0.05, 0.05, 0.75)
        leg.location = pos

    print("✅ 辦公桌創建完成！")

def create_office_chair():
    """創建辦公椅"""
    # 創建座椅
    bpy.ops.mesh.primitive_cube_add()
    seat = bpy.context.active_object
    seat.name = "Chair_Seat"
    seat.scale = (0.5, 0.5, 0.1)
    seat.location = (0, 0.8, 0.5)

    # 創建椅背
    bpy.ops.mesh.primitive_cube_add()
    back = bpy.context.active_object
    back.name = "Chair_Back"
    back.scale = (0.5, 0.6, 0.1)
    back.location = (0, 0.8, 0.8)

    print("✅ 辦公椅創建完成！")

def create_floor():
    """創建地板"""
    bpy.ops.mesh.primitive_plane_add()
    floor = bpy.context.active_object
    floor.name = "Floor"
    floor.scale = (10, 10, 1)

    print("✅ 地板創建完成！")

def setup_lighting():
    """設置燈光"""
    # 主光源
    bpy.ops.object.light_add(type='SUN')
    sun = bpy.context.active_object
    sun.name = "Main_Light"
    sun.location = (5, 5, 10)
    sun.data.energy = 5

    # 環境光
    bpy.ops.object.light_add(type='AREA')
    area = bpy.context.active_object
    area.name = "Ambient_Light"
    area.location = (0, 0, 5)
    area.data.energy = 100

    print("✅ 燈光設置完成！")

def setup_camera():
    """設置相機"""
    bpy.ops.object.camera_add()
    camera = bpy.context.active_object
    camera.name = "Main_Camera"
    camera.location = (3, -3, 2)

    # 設置相機角度
    camera.rotation_euler = (math.radians(60), 0, math.radians(45))

    print("✅ 相機設置完成！")

def save_blend(filepath):
    """保存 .blend 檔案"""
    bpy.ops.wm.save_as_mainfile(filepath=filepath)
    print(f"✅ 場景已保存至：{filepath}")

def main():
    """主程序"""
    print("=" * 60)
    print("Blender Office Scene Generator")
    print("=" * 60)

    # 創建場景
    create_floor()
    create_office_desk()
    create_office_chair()

    # 設置燈光和相機
    setup_lighting()
    setup_camera()

    # 保存 .blend 檔案
    output_path = "/mnt/e_drive/claude-office/assets/blender/office_scene.blend"
    save_blend(output_path)

    print("=" * 60)
    print("✅ 辦公室場景創建完成！")
    print("注意：由於 GLTF 導出問題，已保存為 .blend 格式")
    print("下一步：手動在 Blender GUI 中導出 GLTF")
    print("=" * 60)

if __name__ == "__main__":
    main()
