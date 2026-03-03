#!/usr/bin/env python3
"""
日系原神風格素材生成器
使用 Stable Diffusion 生成遊戲場景和角色
"""

import subprocess
import json
from pathlib import Path
import time

# Stable Diffusion API 設置
SD_API = "http://127.0.0.1:7860"
OUTPUT_DIR = Path("/mnt/e_drive/claude-office/assets")

# 日系原神風格通用提示詞
GENSHIN_STYLE = """
genshin impact style, anime style, cel shading,
high quality, detailed, beautiful artwork,
soft lighting, vibrant colors, 2D game art,
official art style, masterpiece, best quality
"""

# 場景提示詞（辦公室）
OFFICE_SCENE = """
cozy office interior, anime style, genshin impact style,
warm lighting, wooden floor, white walls,
comfortable sofa, desk with computer, plant decorations,
window with view, gentle atmosphere,
2D game background, horizontal scroll game,
high resolution, detailed interior, masterpiece
"""

# 角色提示詞（櫻 - 粉色雙馬尾）
SAKURA_BASE = """
genshin impact style, anime girl, game character,
pink twin-tail hair, blue eyes, cute face,
white school uniform, blue ribbon, 
6-head proportion, full body, standing pose,
soft smile, beautiful eyes,
high quality character design, official art style,
transparent background, PNG
"""

def generate_scene():
    """生成辦公室場景"""
    print("🎮 生成日系原神風格辦公室場景...")
    
    prompt = f"{GENSHIN_STYLE}, {OFFICE_SCENE}"
    
    # 使用 Stable Diffusion WebUI API
    payload = {
        "prompt": prompt,
        "negative_prompt": "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, 3D, realistic",
        "steps": 30,
        "cfg_scale": 7,
        "width": 1024,
        "height": 512,
        "seed": 12345,  # 固定種子確保一致性
    }
    
    # 調用 API
    cmd = [
        "curl", "-s", "-X", "POST",
        f"{SD_API}/sdapi/v1/txt2img",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload),
        "-o", str(OUTPUT_DIR / "backgrounds" / "office_scene_raw.json")
    ]
    
    print("  調用 Stable Diffusion API...")
    # subprocess.run(cmd, check=True)
    
    # 模擬生成（測試用）
    print("  ⚠️  Stable Diffusion 未啟動，使用模擬模式")
    print("  💡 請先啟動 Stable Diffusion WebUI:")
    print("     cd /path/to/stable-diffusion-webui")
    print("     ./webui.sh --api")
    
    return False

def generate_character_sakura():
    """生成櫻的角色插圖"""
    print("👧 生成櫻的角色插圖...")
    
    prompt = f"{GENSHIN_STYLE}, {SAKURA_BASE}"
    
    payload = {
        "prompt": prompt,
        "negative_prompt": "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, 3D, realistic, multiple girls, different clothes",
        "steps": 30,
        "cfg_scale": 7,
        "width": 512,
        "height": 1024,
        "seed": 11111,  # 固定種子
    }
    
    print("  調用 Stable Diffusion API...")
    # TODO: 實際調用 API
    
    return False

def main():
    print("🎨 日系原神風格素材生成器")
    print("=" * 50)
    
    # 創建輸出目錄
    (OUTPUT_DIR / "backgrounds").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "characters").mkdir(parents=True, exist_ok=True)
    
    # 檢查 Stable Diffusion 是否可用
    print("\n檢查 Stable Diffusion 服務...")
    try:
        result = subprocess.run(
            ["curl", "-s", "-f", f"{SD_API}/sdapi/v1/sd-models"],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            print("  ✅ Stable Diffusion 服務可用")
            
            # 生成素材
            generate_scene()
            generate_character_sakura()
            
        else:
            print("  ❌ Stable Diffusion 服務未啟動")
            print("\n請先啟動 Stable Diffusion WebUI:")
            print("  cd /path/to/stable-diffusion-webui")
            print("  ./webui.sh --api --listen")
            print("\n或使用其他 Stable Diffusion 服務")
            
    except Exception as e:
        print(f"  ❌ 檢查失敗: {e}")
        print("\n替代方案:")
        print("1. 使用線上 Stable Diffusion 服務")
        print("2. 手動下載現成的原神風格素材")
        print("3. 使用其他 AI 繪圖工具")
    
    print("\n" + "=" * 50)
    print("完成！")

if __name__ == "__main__":
    main()
