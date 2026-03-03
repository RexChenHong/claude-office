#!/usr/bin/env python3
"""
日系原神風格素材生成器
使用 Stable Diffusion 生成高品質的遊戲素材
"""

import os
import sys
import torch
from pathlib import Path
from PIL import Image
from diffusers import StableDiffusionPipeline
import argparse

# 日系原神風格通用提示詞
GENSHIN_STYLE = """
genshin impact style, anime style, cel shading,
high quality, detailed, beautiful artwork,
soft lighting, vibrant colors, 2D game art,
official art style, masterpiece, best quality,
kawaii, moe, detailed eyes
"""

# 角色設計（日系原神風格）
CHARACTERS = {
    "sakura": {
        "name": "櫻",
        "prompt": """
genshin impact style, anime girl, game character,
pink twin-tail hair, blue eyes, cute face,
white school uniform, blue ribbon,
standing pose, soft smile, beautiful eyes,
high quality character design, official art style,
full body, transparent background, PNG
"""
    },
    "homura": {
        "name": "焰",
        "prompt": """
genshin impact style, anime girl, game character,
red short hair, red eyes, serious face,
black school uniform, red tie,
standing pose, determined expression,
high quality character design, official art style,
full body, transparent background, PNG
"""
    }
}

# 動畫姿態
ANIMATIONS = {
    "idle": [
        "standing, arms at sides, slight body sway right",
        "standing, arms at sides, slight body sway left",
        "standing, arms at sides, head turn right",
        "standing, arms at sides, head turn left",
        "standing, right arm raised slightly",
        "standing, left arm raised slightly",
        "standing, arms at sides, blinking",
        "standing, arms at sides, smiling"
    ]
}

def load_model():
    """載入 Stable Diffusion 模型"""
    print("🔄 載入 Stable Diffusion 模型...")
    
    # 使用公開可用的模型
    model_id = "runwayml/stable-diffusion-v1-5"
    
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        safety_checker=None,
    )
    pipe = pipe.to("cuda")
    pipe.enable_attention_slicing()
    
    print("✅ 模型載入完成")
    return pipe

def generate_character(pipe, character_id, animation_type, output_dir):
    """生成角色動畫幀"""
    char = CHARACTERS[character_id]
    anim = ANIMATIONS[animation_type]
    
    print(f"\n👧 生成角色: {char['name']} - {animation_type}")
    
    frames_dir = output_dir / character_id / f"{animation_type}_frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    
    frames = []
    for i, pose in enumerate(anim):
        print(f"  生成第 {i+1}/{len(anim)} 幀...")
        
        # 組合提示詞
        prompt = f"{char['prompt']}, {pose}"
        
        # 生成圖像
        image = pipe(
            prompt=prompt,
            negative_prompt="""
lowres, bad anatomy, bad hands, text, error,
missing fingers, extra digit, fewer digits, cropped,
worst quality, low quality, normal quality,
jpeg artifacts, signature, watermark, username, blurry,
3D, realistic, photo, multiple girls, different clothes
""",
            num_inference_steps=30,
            guidance_scale=7.0,
            width=256,
            height=512,
        ).images[0]
        
        # 保存幀
        frame_path = frames_dir / f"frame_{i:03d}.png"
        image.save(frame_path)
        frames.append(image)
        
        # 釋放 GPU 內存
        torch.cuda.empty_cache()
    
    # 合併成 sprite sheet
    print("  合併 sprite sheet...")
    sprite_sheet = Image.new('RGBA', (256 * len(frames), 512))
    for i, frame in enumerate(frames):
        sprite_sheet.paste(frame, (i * 256, 0))
    
    sprite_path = output_dir / character_id / f"{animation_type}.png"
    sprite_sheet.save(sprite_path)
    
    print(f"  ✅ 完成: {sprite_path}")
    return sprite_path

def generate_office_scene(pipe, output_dir):
    """生成辦公室場景"""
    print("\n🏢 生成日系原神風格辦公室...")
    
    prompt = """
genshin impact style, cozy office interior, anime background,
warm lighting, wooden floor, white walls,
comfortable sofa, desk with computer, plant decorations,
window with sky view, gentle atmosphere,
2D game background, horizontal scroll,
high resolution, detailed, masterpiece
"""
    
    image = pipe(
        prompt=prompt,
        negative_prompt="""
lowres, bad anatomy, text, error, cropped,
worst quality, low quality, normal quality,
jpeg artifacts, signature, watermark, blurry,
3D, realistic, photo, people, characters
""",
        num_inference_steps=30,
        guidance_scale=7.0,
        width=1024,
        height=512,
    ).images[0]
    
    scene_path = output_dir / "backgrounds" / "office_scene.png"
    scene_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(scene_path)
    
    print(f"  ✅ 完成: {scene_path}")
    return scene_path

def main():
    parser = argparse.ArgumentParser(description='生成日系原神風格素材')
    parser.add_argument('--scene', action='store_true', help='生成場景')
    parser.add_argument('--character', type=str, help='角色ID (sakura, homura)')
    parser.add_argument('--animation', type=str, default='idle', help='動畫類型')
    
    args = parser.parse_args()
    
    output_dir = Path("/mnt/e_drive/claude-office/assets")
    
    # 檢查 GPU
    print("📊 GPU 狀態:")
    os.system("nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used --format=csv,noheader")
    
    # 載入模型
    pipe = load_model()
    
    # 生成素材
    if args.scene:
        generate_office_scene(pipe, output_dir)
    
    if args.character:
        generate_character(pipe, args.character, args.animation, output_dir)
    
    print("\n✅ 所有素材生成完成！")

if __name__ == "__main__":
    main()
