# Claude Office - Sprite Sheet 動畫系統

## 🎯 技術方案（用戶確認）

**放棄 Live2D，改用全 Sprite Sheet 動畫**

原因：
- Live2D 不支援走路動畫
- Sprite Sheet 風格統一
- 更符合遊戲開發流程

---

## 📋 角色動畫狀態機

```
[休息區]
    │
    ├── idle（呼吸、發呆） 4-8 幀循環
    │
    │ ← session 開啟
    │
    ├── stand_up（起身） 4 幀
    │
    └── walk（走路） 8 幀循環
          │
          ↓ [移動到辦公桌]
          │
    ┌─── sit_down（坐下） 4 幀
    │
    ├── working（打字） 8 幀循環
    │
    ├── waiting（滑手機） 8 幀循環
    │
    │ ← session 關閉
    │
    └── stand_up（起身） 4 幀
          │
          └── walk（走路）回到休息區
```

---

## 🎨 美術素材清單

### 單一角色（測試用）

| 動作 | 幀數 | 方向 | 數量 |
|------|------|------|------|
| idle（閒置） | 8 | 正面 | 8 |
| walk（走路） | 8 | 左/右 | 16 |
| working（打字） | 8 | 正面 | 8 |
| waiting（滑手機） | 8 | 正面 | 8 |
| sit_down（坐下） | 4 | 正面 | 4 |
| stand_up（起身） | 4 | 正面 | 4 |

**總計：48 張小圖 / 角色**

### 5 角色（正式版）

48 × 5 = 240 張小圖

---

## 🛠️ 生成方式

### 方案 A：Stable Diffusion + ControlNet

1. **生成基礎立繪**（已完成）
2. **用 ControlNet 生成變體**
   - OpenPose 骨架控制
   - 保持角色一致性
3. **後處理**
   - 裁切、對齊
   - 組合成 sprite sheet

### 方案 B：Sprite Sheet 直接生成

修改 SD prompt，一次生成多幀：
```
sprite sheet, 8 frames, anime girl walking cycle,
genshin impact style, white background, 512x512 each frame
```

### 方案 C：手動微調

1. SD 生成關鍵幀
2. 用 Aseprite 手動調整
3. 組合成流暢動畫

---

## 📐 技術規格

### 圖片尺寸
- 單幀：256×512（適合 6 頭身）
- Sprite Sheet：2048×512（8 幀橫排）

### 幀率
- 8 FPS（流暢感）
- 可調整

### 格式
- PNG（透明背景）
- JSON（PixiJS sprite sheet 格式）

---

## 🚀 實作步驟（Phase 2.5）

### Step 1：生成單角色動畫幀
- [ ] 用 SD 生成走路動畫 8 幀
- [ ] 生成閒置動畫 8 幀
- [ ] 生成打字動畫 8 幀
- [ ] 生成滑手機動畫 8 幀

### Step 2：組合 Sprite Sheet
- [ ] 使用 Python + Pillow 組合
- [ ] 生成 PixiJS 格式 JSON

### Step 3：整合到 PixiJS
- [ ] 安裝 `@pixi/spritesheet`
- [ ] 修改 main.js 支援動畫播放
- [ ] 實現狀態切換邏輯

### Step 4：測試驗證
- [ ] 確認動畫流暢度
- [ ] 確認走路方向切換
- [ ] 確認背景互動感

---

## ⏱️ 預估時間

- Step 1：30 分鐘（SD 生成）
- Step 2：15 分鐘（組合 sprite sheet）
- Step 3：30 分鐘（程式整合）
- Step 4：15 分鐘（測試調整）

**總計：約 1.5 小時（單角色測試）**

---

*建立時間：2026-03-03 11:20*
