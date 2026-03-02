# Claude Office - 美術資產

## 📁 目錄結構

```
assets/
├── characters/        # 角色立繪
│   ├── sakura/       # 櫻（粉色）
│   ├── homura/       # 焰（紅色）
│   ├── ryo/          # 涼（藍色）
│   ├── koto/         # 琴（黃色）
│   └── yoi/          # 宵（紫色）
├── backgrounds/      # 場景背景
├── props/            # 道具（辦公桌、沙發等）
└── effects/          # 特效（打字光效等）
```

## 🎨 資產規格

### 角色立繪
- **格式**: PNG（透明背景）
- **尺寸**: 512x512 px
- **風格**: 原神風格、6 頭身比例
- **幀數**: 
  - `idle.png` - 休息狀態
  - `working.png` - 工作狀態
  - `waiting.png` - 等待狀態

### 背景
- **格式**: PNG
- **尺寸**: 1200x700 px
- **場景**: 
  - `office.png` - 主辦公室

### 道具
- **格式**: PNG（透明背景）
- **尺寸**: 依道具比例
- **列表**:
  - `desk.png` - 辦公桌
  - `sofa.png` - 沙發
  - `monitor.png` - 螢幕

## 🔧 生成工具

### Stable Diffusion Prompt 範本
```
genshin impact style, anime girl, 6-head proportion,
[hair color] hair, [eye color] eyes,
office attire, sitting at desk,
high quality, detailed, soft lighting
```

### LoRA 模型
- 推薦: `genshin_impact_style_v1`

## ⚠️ GPU 限制
- 當前 GPU 佔用: ~91%（主專案使用）
- 生成時需等待 GPU 釋放
- 目標: GPU+VRAM ≤ 10%
