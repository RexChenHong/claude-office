#!/usr/bin/env python3
"""
Generate sprite sheet animations for Claude Office characters
Usage: python3 generate_sprites.py --character sakura --action walk --frames 8
"""

import os
import sys
import json
import argparse
from pathlib import Path
from PIL import Image

import torch
from diffusers import StableDiffusionPipeline
from diffusers.utils import logging

# Suppress warnings
logging.set_verbosity_error()

# Configuration
BASE_DIR = Path("/mnt/e_drive/claude-office")
OUTPUT_DIR = BASE_DIR / "assets" / "sprites"
CHARACTER_SPECS = {
    "sakura": {
        "name": "櫻",
        "hair_color": "pink",
        "outfit": "white office blouse and navy skirt",
        "prompt_suffix": "pink long hair, hair ribbon, cheerful expression"
    },
    "homura": {
        "name": "焰",
        "hair_color": "red",
        "outfit": "white office blouse and navy skirt",
        "prompt_suffix": "red long hair, ponytail, serious expression"
    },
    "ryo": {
        "name": "涼",
        "hair_color": "blue",
        "outfit": "white office blouse and navy skirt",
        "prompt_suffix": "blue short hair, glasses, calm expression"
    },
    "koto": {
        "name": "琴",
        "hair_color": "yellow",
        "outfit": "white office blouse and navy skirt",
        "prompt_suffix": "blonde twin tails, cheerful expression"
    },
    "yoi": {
        "name": "宵",
        "hair_color": "purple",
        "outfit": "white office blouse and navy skirt",
        "prompt_suffix": "purple long hair, mysterious smile"
    }
}

ANIMATION_PROMPTS = {
    "idle": "standing still, breathing animation, slight body movement",
    "walk_left": "walking cycle, facing left, side view",
    "walk_right": "walking cycle, facing right, side view",
    "working": "sitting at desk, typing on keyboard, hands moving",
    "waiting": "sitting at desk, looking at smartphone, scrolling",
    "sit_down": "sitting down animation, side view",
    "stand_up": "standing up animation, side view"
}

def load_model():
    """Load Stable Diffusion model"""
    print("🔄 載入 Stable Diffusion 模型...")
    
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

def generate_sprite_frames(pipe, character, action, num_frames=8, direction=None):
    """Generate individual frames for animation"""
    
    char_spec = CHARACTER_SPECS[character]
    
    # Build prompt
    action_desc = ANIMATION_PROMPTS[action]
    if direction:
        action_desc = action_desc.replace("side view", f"{direction} view")
    
    prompt = f"""genshin impact style anime girl, {char_spec['prompt_suffix']},
{char_spec['outfit']}, {action_desc},
sprite sheet animation frame, single character,
transparent background, simple white background,
full body, 6-head proportion, highly detailed,
official game art, masterpiece, best quality"""
    
    negative_prompt = """multiple characters, duplicate, crowd,
complex background, environment, furniture,
low quality, blurry, deformed, bad anatomy,
extra limbs, missing limbs, watermark, text"""
    
    print(f"🎨 生成 {char_spec['name']} - {action} ({num_frames} 幀)...")
    
    frames = []
    for i in range(num_frames):
        print(f"  生成第 {i+1}/{num_frames} 幀...")
        
        # Add frame number hint for variation
        frame_prompt = f"{prompt}, frame {i+1} of {num_frames}"
        
        image = pipe(
            prompt=frame_prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=20,
            guidance_scale=7.5,
            width=256,
            height=512,
        ).images[0]
        
        frames.append(image)
    
    return frames

def create_sprite_sheet(frames, output_path, frame_width=256, frame_height=512):
    """Combine frames into horizontal sprite sheet"""
    
    num_frames = len(frames)
    sheet_width = frame_width * num_frames
    sheet_height = frame_height
    
    # Create sprite sheet image
    sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
    
    for i, frame in enumerate(frames):
        # Convert to RGBA if needed
        if frame.mode != 'RGBA':
            frame = frame.convert('RGBA')
        
        # Resize if needed
        if frame.size != (frame_width, frame_height):
            frame = frame.resize((frame_width, frame_height), Image.Resampling.LANCZOS)
        
        # Paste into sheet
        x = i * frame_width
        sheet.paste(frame, (x, 0))
    
    # Save sprite sheet
    sheet.save(output_path, 'PNG')
    print(f"  ✅ 儲存 sprite sheet: {output_path}")
    
    return sheet

def generate_json_metadata(character, action, num_frames, frame_width=256, frame_height=512):
    """Generate PixiJS sprite sheet JSON metadata"""
    
    frames_data = {}
    
    for i in range(num_frames):
        frame_name = f"{character}_{action}_{i:03d}"
        frames_data[frame_name] = {
            "frame": {
                "x": i * frame_width,
                "y": 0,
                "w": frame_width,
                "h": frame_height
            },
            "rotated": False,
            "trimmed": False,
            "spriteSourceSize": {
                "x": 0,
                "y": 0,
                "w": frame_width,
                "h": frame_height
            },
            "sourceSize": {
                "w": frame_width,
                "h": frame_height
            }
        }
    
    metadata = {
        "frames": frames_data,
        "meta": {
            "app": "Claude Office Sprite Generator",
            "version": "1.0",
            "image": f"{character}_{action}.png",
            "format": "RGBA8888",
            "size": {
                "w": frame_width * num_frames,
                "h": frame_height
            },
            "scale": 1
        }
    }
    
    return metadata

def main():
    parser = argparse.ArgumentParser(description="Generate sprite sheet animations")
    parser.add_argument("--character", "-c", required=True, choices=CHARACTER_SPECS.keys(),
                        help="Character to generate")
    parser.add_argument("--action", "-a", required=True, choices=ANIMATION_PROMPTS.keys(),
                        help="Animation action")
    parser.add_argument("--frames", "-f", type=int, default=8,
                        help="Number of frames (default: 8)")
    parser.add_argument("--direction", "-d", choices=["left", "right"],
                        help="Direction for walk animations")
    parser.add_argument("--all", action="store_true",
                        help="Generate all actions for a character")
    
    args = parser.parse_args()
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    character_dir = OUTPUT_DIR / args.character
    character_dir.mkdir(parents=True, exist_ok=True)
    
    # Load model
    pipe = load_model()
    
    # Determine actions to generate
    if args.all:
        actions = list(ANIMATION_PROMPTS.keys())
    else:
        actions = [args.action]
    
    # Generate sprites
    for action in actions:
        print(f"\n{'='*60}")
        print(f"🎭 生成 {args.character} - {action}")
        print(f"{'='*60}")
        
        # Generate frames
        frames = generate_sprite_frames(
            pipe,
            args.character,
            action,
            args.frames,
            args.direction
        )
        
        # Create sprite sheet
        action_name = action
        if args.direction:
            action_name = f"{action}_{args.direction}"
        
        sheet_path = character_dir / f"{action_name}.png"
        create_sprite_sheet(frames, sheet_path)
        
        # Generate JSON metadata
        json_path = character_dir / f"{action_name}.json"
        metadata = generate_json_metadata(args.character, action_name, args.frames)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ 儲存 JSON: {json_path}")
    
    print(f"\n{'='*60}")
    print(f"🎉 Sprite 生成完成！")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
