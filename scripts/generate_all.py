#!/usr/bin/env python3
"""
Claude Office - 完整美術生成腳本
生成：背景 + 5名角色立繪（原神風格 6 頭身）
"""

import torch
from diffusers import StableDiffusionPipeline
from pathlib import Path
import json

OUTPUT_DIR = Path("/mnt/e_drive/claude-office/assets")

def load_pipeline():
    """載入 Stable Diffusion"""
    model_id = "runwayml/stable-diffusion-v1-5"
    
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        safety_checker=None,
    )
    pipe = pipe.to("cuda")
    pipe.enable_attention_slicing()
    
    return pipe

def generate_background(pipe, bg_type):
    """生成背景"""
    prompts = {
        "work_area": """
        genshin impact style background, anime office work area,
        modern desk setup with computer monitors, office chair,
        clean minimalist design, soft lighting through windows,
        indoor scene, no people, high quality, detailed,
        warm color palette, professional atmosphere
        """,
        "lounge_area": """
        genshin impact style background, anime office lounge area,
        comfortable purple sofas, coffee table, potted plants,
        cozy atmosphere, soft ambient lighting,
        indoor scene, no people, high quality, detailed,
        cool color palette, relaxing atmosphere
        """
    }
    
    negative = """
    low quality, blurry, distorted, people, characters,
    text, watermark, ugly, bad anatomy
    """
    
    print(f"  生成背景: {bg_type}")
    image = pipe(
        prompt=prompts[bg_type],
        negative_prompt=negative,
        num_inference_steps=30,
        guidance_scale=7.5,
        width=1024,
        height=512,
    ).images[0]
    
    return image

def generate_character(pipe, char_spec, state):
    """生成角色立繪"""
    state_prompts = {
        "idle": "sitting elegantly on purple sofa, relaxed pose, gentle smile, hands on lap",
        "working": "sitting at office desk, typing on keyboard, focused expression, facing monitor",
        "waiting": "sitting on sofa, looking at smartphone, casual pose, slight smile"
    }
    
    prompt = f"""
    genshin impact official art style, 
    {char_spec['prompt_template']},
    {state_prompts[state]},
    full body, 6-head proportion, normal anime body ratio,
    highly detailed face, expressive eyes,
    masterpiece, best quality, official game art,
    transparent background, character sprite
    """
    
    negative = """
    low quality, bad anatomy, worst quality, deformed,
    disfigured, missing limbs, extra limbs, blurry,
    text, watermark, background, scenery, q-version,
    chibi, 3-head proportion, 4-head proportion
    """
    
    print(f"  生成角色: {char_spec['name']} - {state}")
    image = pipe(
        prompt=prompt,
        negative_prompt=negative,
        num_inference_steps=35,
        guidance_scale=8.0,
        width=512,
        height=768,
    ).images[0]
    
    return image

def main():
    print("=" * 60)
    print("  Claude Office 美術生成器")
    print("  風格: 日系原神 | 比例: 6 頭身")
    print("=" * 60)
    
    # 檢查 GPU
    if not torch.cuda.is_available():
        print("❌ CUDA 不可用")
        return
    
    print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
    print(f"✅ VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    
    # 載入模型
    print("\n📦 載入 Stable Diffusion...")
    pipe = load_pipeline()
    print("✅ 模型載入完成")
    
    # 載入角色規格
    specs_path = OUTPUT_DIR / "characters/character_specs.json"
    specs = json.load(open(specs_path))
    
    # 1. 生成背景
    print("\n🖼️ 生成背景...")
    bg_dir = OUTPUT_DIR / "backgrounds"
    bg_dir.mkdir(exist_ok=True)
    
    for bg_type in ["work_area", "lounge_area"]:
        img = generate_background(pipe, bg_type)
        img.save(bg_dir / f"{bg_type}.png")
        print(f"    ✅ {bg_type}.png")
    
    # 2. 生成角色
    print("\n🎭 生成角色立繪...")
    for char in specs["characters"]:
        char_dir = OUTPUT_DIR / "characters" / char["name_en"].lower()
        char_dir.mkdir(exist_ok=True)
        
        for state in ["idle", "working", "waiting"]:
            img = generate_character(pipe, char, state)
            img.save(char_dir / f"{state}.png")
            print(f"    ✅ {char['name']}/{state}.png")
    
    print("\n" + "=" * 60)
    print("🎉 所有美術素材生成完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
