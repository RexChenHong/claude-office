#!/usr/bin/env python3
"""
Claude Office - 角色立繪生成腳本
使用 Stable Diffusion 生成原神風格角色
"""

import torch
from diffusers import StableDiffusionPipeline
from pathlib import Path
import json

# 配置
OUTPUT_DIR = Path("/mnt/e_drive/claude-office/assets/characters")
CHARACTER_SPECS = json.load(open(OUTPUT_DIR / "character_specs.json"))

def load_model():
    """載入 Stable Diffusion 模型"""
    model_id = "runwayml/stable-diffusion-v1-5"  # 基礎模型
    
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        safety_checker=None,
    )
    pipe = pipe.to("cuda")
    
    # 載入原神風格 LoRA（如果有）
    # pipe.load_lora_weights("/path/to/genshin_lora")
    
    return pipe

def generate_character(pipe, character, state="idle"):
    """生成單個角色的單一狀態圖片"""
    
    # 根據狀態調整 prompt
    state_prompts = {
        "idle": "sitting on sofa, relaxed pose, drinking tea",
        "working": "sitting at desk, typing on keyboard, focused expression",
        "waiting": "sitting on sofa, looking at phone, casual pose",
    }
    
    prompt = f"""
    {character['prompt_template']},
    {state_prompts[state]},
    masterpiece, best quality, highly detailed,
    soft studio lighting, white background,
    upper body portrait
    """
    
    negative_prompt = """
    low quality, bad anatomy, worst quality, 
    deformed, disfigured, missing limbs,
    extra limbs, blurry, text, watermark
    """
    
    image = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=30,
        guidance_scale=7.5,
        width=512,
        height=512,
    ).images[0]
    
    return image

def main():
    print("🎨 Claude Office 角色生成器")
    print("=" * 50)
    
    # 檢查 GPU
    if not torch.cuda.is_available():
        print("❌ CUDA 不可用")
        return
    
    print(f"✅ GPU 可用: {torch.cuda.get_device_name(0)}")
    print(f"💾 VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    
    # 載入模型
    print("\n📦 載入 Stable Diffusion 模型...")
    pipe = load_model()
    print("✅ 模型載入完成")
    
    # 生成所有角色
    for character in CHARACTER_SPECS["characters"]:
        print(f"\n🎨 生成角色: {character['name']}")
        
        char_dir = OUTPUT_DIR / character['name_en'].lower()
        char_dir.mkdir(exist_ok=True)
        
        # 生成三種狀態
        for state in ["idle", "working", "waiting"]:
            print(f"  - {state}...")
            image = generate_character(pipe, character, state)
            
            output_path = char_dir / f"{state}.png"
            image.save(output_path)
            print(f"    ✅ 已保存: {output_path}")
    
    print("\n🎉 所有角色生成完成！")

if __name__ == "__main__":
    main()
