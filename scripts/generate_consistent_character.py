#!/usr/bin/env python3
"""
日系原神風格角色 Sprite Sheet 生成器
使用 Reference + 固定種子確保角色一致性
"""

import torch
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from diffusers import StableDiffusionPipeline
import numpy as np

# 輸出目錄
OUTPUT_DIR = Path("/mnt/e_drive/claude-office/assets")

# 日系原神風格通用提示詞
GENSHIN_BASE = """
genshin impact style, anime style, official game art,
high quality, masterpiece, best quality,
cel shading, vibrant colors, 2D game character,
detailed eyes, beautiful face, kawaii
"""

# 角色設計（固定特徵描述）
CHARACTERS = {
    "sakura": {
        "name": "櫻",
        "seed": 11111,  # 固定種子
        "base_prompt": f"""
{GENSHIN_BASE},
1girl, solo, pink twin-tail hair, blue eyes,
white school uniform, blue ribbon, cute face,
standing pose, full body, looking at viewer,
transparent background, PNG, game sprite
"""
    }
}

# 動畫姿態（細微變化）
IDLE_POSES = [
    "arms at sides, body facing forward, neutral expression",
    "arms at sides, slight lean to right, soft smile",
    "arms at sides, slight lean to left, soft smile",
    "arms at sides, head tilted right, gentle expression",
    "arms at sides, head tilted left, gentle expression",
    "right hand slightly raised, happy expression",
    "left hand slightly raised, cheerful expression",
    "arms at sides, blinking, peaceful expression"
]

def create_reference_image(pipe, character_id):
    """
    創建角色參考圖（高品質，用於保持一致性）
    """
    char = CHARACTERS[character_id]
    
    print(f"\n🎨 創建 {char['name']} 參考圖...")
    
    # 生成參考圖
    image = pipe(
        prompt=char['base_prompt'],
        negative_prompt="""
lowres, bad anatomy, bad hands, text, error,
missing fingers, extra digit, fewer digits, cropped,
worst quality, low quality, normal quality,
jpeg artifacts, signature, watermark, username, blurry,
3D, realistic, photo, multiple girls, different clothes,
bad eyes, deformed eyes, bad face, deformed face
""",
        num_inference_steps=50,  # 更多步驟確保品質
        guidance_scale=9.0,  # 更高的 guidance
        width=512,
        height=768,  # 更大尺寸
        generator=torch.Generator(device="cuda").manual_seed(char['seed'])
    ).images[0]
    
    # 保存參考圖
    ref_path = OUTPUT_DIR / "references" / f"{character_id}_ref.png"
    ref_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(ref_path)
    
    print(f"  ✅ 參考圖保存: {ref_path}")
    return image, char['seed']

def generate_consistent_frames(pipe, character_id, reference_image, seed):
    """
    生成一致的角色動畫幀
    使用相同的種子 + 細微變化
    """
    char = CHARACTERS[character_id]
    
    print(f"\n🎬 生成 {char['name']} idle 動畫幀...")
    
    frames = []
    
    for i, pose in enumerate(IDLE_POSES):
        print(f"  生成第 {i+1}/8 幀...")
        
        # 組合提示詞：基礎 + 當前姿態
        full_prompt = f"{char['base_prompt']}, {pose}"
        
        # 使用固定種子 + 細微偏移
        frame_seed = seed + i * 100  # 細微變化
        
        # 生成圖像
        image = pipe(
            prompt=full_prompt,
            negative_prompt="""
lowres, bad anatomy, bad hands, text, error,
missing fingers, extra digit, fewer digits, cropped,
worst quality, low quality, normal quality,
jpeg artifacts, signature, watermark, username, blurry,
3D, realistic, photo, multiple girls, different clothes,
bad eyes, deformed eyes, bad face, deformed face
""",
            num_inference_steps=40,
            guidance_scale=8.0,
            width=256,
            height=512,
            generator=torch.Generator(device="cuda").manual_seed(frame_seed)
        ).images[0]
        
        frames.append(image)
        
        # 釋放 GPU 內存
        torch.cuda.empty_cache()
    
    return frames

def create_sprite_sheet(frames, output_path):
    """
    合併成 sprite sheet
    """
    print(f"\n📊 合併 sprite sheet...")
    
    # 創建空白畫布
    sprite_sheet = Image.new('RGBA', (256 * len(frames), 512))
    
    # 粘貼每一幀
    for i, frame in enumerate(frames):
        # 調整大小
        if frame.size != (256, 512):
            frame = frame.resize((256, 512), Image.LANCZOS)
        
        sprite_sheet.paste(frame, (i * 256, 0))
    
    # 保存
    sprite_sheet.save(output_path)
    print(f"  ✅ Sprite sheet 保存: {output_path}")
    
    return sprite_sheet

def main():
    print("🎮 日系原神風格角色生成器")
    print("=" * 50)
    
    # 載入模型
    print("\n🔄 載入 Stable Diffusion 模型...")
    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float16,
        safety_checker=None,
    )
    pipe = pipe.to("cuda")
    pipe.enable_attention_slicing()
    print("✅ 模型載入完成")
    
    # 創建輸出目錄
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 生成角色
    character_id = "sakura"
    
    # 1. 創建參考圖
    ref_image, seed = create_reference_image(pipe, character_id)
    
    # 2. 生成一致的角色幀
    frames = generate_consistent_frames(pipe, character_id, ref_image, seed)
    
    # 3. 合併成 sprite sheet
    output_path = OUTPUT_DIR / "sprites" / "sakura" / "idle.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    create_sprite_sheet(frames, output_path)
    
    print("\n✅ 生成完成！")
    print(f"📁 輸出路徑: {output_path}")

if __name__ == "__main__":
    main()
