#!/usr/bin/env python3
"""
遊戲角色 Sprite Sheet 生成器
確保同一個角色的不同姿態保持一致
"""

import json
import os
import subprocess
from pathlib import Path

# 角色設計（固定特徵）
CHARACTERS = {
    "sakura": {
        "name": "櫻",
        "hair_color": "粉色",
        "hair_style": "雙馬尾",
        "eye_color": "藍色",
        "outfit": "白色校服，藍色蝴蝶結",
        "seed": 12345,  # 固定種子確保一致性
        "base_prompt": """
日系原神風格，動漫風格，遊戲角色設計，
粉色雙馬尾，藍色眼睛，白色校服，藍色蝴蝶結，
6頭身比例，精緻細節，柔和光線，
高品質插畫，全身，正面視角，白色背景
"""
    },
    "homura": {
        "name": "焰",
        "hair_color": "紅色",
        "hair_style": "短髮",
        "eye_color": "紅色",
        "outfit": "黑色校服，紅色領帶",
        "seed": 23456,
        "base_prompt": """
日系原神風格，動漫風格，遊戲角色設計，
紅色短髮，紅色眼睛，黑色校服，紅色領帶，
6頭身比例，精緻細節，柔和光線，
高品質插畫，全身，正面視角，白色背景
"""
    }
}

# 動畫姿態（同一角色的不同姿態）
ANIMATIONS = {
    "idle": {
        "frames": 8,
        "description": "輕微晃動的 idle 動畫",
        "poses": [
            "站立，雙手自然下垂，身體微微向右傾斜",
            "站立，雙手自然下垂，身體微微向左傾斜",
            "站立，雙手自然下垂，頭部微微向右轉",
            "站立，雙手自然下垂，頭部微微向左轉",
            "站立，右手輕微抬起，身體挺直",
            "站立，左手輕微抬起，身體挺直",
            "站立，雙手自然下垂，眨眼",
            "站立，雙手自然下垂，微笑"
        ]
    },
    "working": {
        "frames": 8,
        "description": "打字動作",
        "poses": [
            "坐在椅子上，雙手放在鍵盤上，身體前傾",
            "坐在椅子上，右手抬起準備打字",
            "坐在椅子上，右手按下鍵盤",
            "坐在椅子上，左手按下鍵盤",
            "坐在椅子上，雙手快速打字",
            "坐在椅子上，右手移動滑鼠",
            "坐在椅子上，左手托下巴，看著螢幕",
            "坐在椅子上，雙手放在鍵盤上，身體挺直"
        ]
    }
}

def generate_sprite_sheet(character_id, animation_type, output_dir):
    """
    生成單個 sprite sheet
    使用固定種子和詳細描述確保角色一致性
    """
    char = CHARACTERS[character_id]
    anim = ANIMATIONS[animation_type]
    
    print(f"生成 {char['name']} - {animation_type} 動畫...")
    
    frames_dir = output_dir / character_id / f"{animation_type}_frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成每一幀
    for i, pose in enumerate(anim['poses']):
        # 組合提示詞：基礎特徵 + 當前姿態
        full_prompt = f"""
{char['base_prompt']},
{pose},
遊戲角色 sprite，同一個角色，特徵完全一致，
保持髮型髮色服裝不變，只是姿態變化，
PNG 透明背景，2048x512，第 {i+1} 幀
"""
        
        # 使用 Stable Diffusion 生成
        # 固定種子確保角色一致性
        cmd = [
            "python3", "/mnt/e_drive/sd-scripts/txt2img.py",
            "--prompt", full_prompt,
            "--seed", str(char['seed']),
            "--output", str(frames_dir / f"frame_{i:03d}.png"),
            "--width", "256",
            "--height", "512",
            "--steps", "30",
            "--cfg_scale", "7.0"
        ]
        
        print(f"  生成第 {i+1}/{anim['frames']} 幀...")
        # 實際生成時取消註解
        # subprocess.run(cmd, check=True)
        
        # 模擬生成（測試用）
        (frames_dir / f"frame_{i:03d}.png").touch()
    
    # 合併成 sprite sheet
    # TODO: 使用 PIL 合併所有幀
    print(f"  合併成 sprite sheet...")
    
    return True

def main():
    output_dir = Path("/mnt/e_drive/claude-office/assets/sprites")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for char_id in CHARACTERS:
        for anim_type in ANIMATIONS:
            generate_sprite_sheet(char_id, anim_type, output_dir)
    
    print("✅ 所有 sprite sheets 生成完成")

if __name__ == "__main__":
    main()
