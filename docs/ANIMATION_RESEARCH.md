# Claude Office - 動畫技術研究

## 📋 用戶核心需求

1. **遊戲級動態場景** - 辦公室背景 + NPC 角色互動
2. **流暢角色動畫** - 走路、打字、滑手機、閒置
3. **背景與角色關係** - 不是死板貼圖，要有遊戲感
4. **日系原神畫風** - 6 頭身女性角色
5. **5 個角色** - 統一風格
6. **先做 1 個測試**

---

## 🔍 技術方案分析

### 方案 C：Live2D（用戶選擇）

**優點：**
- 專業二次元動態效果
- 可用 `pixi-live2d-display` 整合到 PixiJS
- 表情、呼吸、眨眼非常自然

**缺點：**
- ❌ **不支援走路動畫** - Live2D 主要用於半身虛擬主播
- ❌ 需要手動製作分層 PSD（SD 無法自動生成）
- ❌ 模型製作成本高（專業師傅要價數千美元）

**免費資源：**
- [Live2D 官方樣本](https://www.live2d.com/en/learn/sample/)
- [GitHub live2d-models](https://github.com/topics/live2d-models)
- [ShiraLive2D 免費模型](https://www.shiralive2d.com/live2d-sample-models/)

---

## 🚨 關鍵發現

用戶要求的「走路動畫」（從休息區走到辦公桌）**與 Live2D 的設計定位衝突**：

| 需求 | Live2D 支援度 |
|------|--------------|
| 半身表情動畫 | ✅ 完美 |
| 呼吸、眨眼 | ✅ 完美 |
| 打字動作 | ⚠️ 可做但有限 |
| 滑手機 | ⚠️ 可做但有限 |
| **走路動畫** | ❌ **不支援** |
| 全身移動 | ❌ **不支援** |

---

## 💡 混合方案（推薦）

結合多種技術實現完整效果：

### Layer 1：場景層（PixiJS）
- 背景：工作區 + 休息區
- 辦公桌、沙發、裝飾物
- 深度分層（前景遮擋角色）

### Layer 2：角色層（混合技術）

| 動作 | 技術 | 說明 |
|------|------|------|
| 休息區閒置 | Live2D | 坐在沙發上的呼吸、發呆 |
| 移動（走路） | Sprite Sheet | 8 幀走路動畫 |
| 坐下工作 | Live2D | 上半身打字動作 |
| 等待（滑手機） | Live2D | 拿手機動作 |

### Layer 3：互動層
- 滑鼠懸停效果
- 點擊對話框
- 狀態提示

---

## 🛠️ 實作步驟（Phase 2.5 - 單角色測試）

### Step 1：取得 Live2D 模型
- 下載免費模型（測試用）
- 或使用 Live2D 官方樣本

### Step 2：安裝 pixi-live2d-display
```bash
cd /mnt/e_drive/claude-office/src/ui
npm install pixi-live2d-display
```

### Step 3：整合到現有場景
- 修改 main.js 載入 Live2D 模型
- 實現狀態切換（idle ↔ working）

### Step 4：處理走路動畫
**選項 A**：淡入淡出移動（簡單）
**選項 B**：Sprite Sheet 走路（複雜）
**選項 C**：保持 Live2D idle 滑動（折衷）

### Step 5：測試驗證
- 確認動畫流暢度
- 確認背景互動感
- 調整細節

---

## ❓ 需要確認

1. **走路動畫處理方式**
   - 選項 A：淡入淡出（最簡單）
   - 選項 B：Sprite Sheet（需要額外生成）
   - 選項 C：Live2D 滑動（折衷）

2. **是否接受免費模型測試**
   - 先用現成模型驗證技術可行性
   - 確認效果後再考慮自定義角色

---

## 📚 參考資源

- [pixi-live2d-display GitHub](https://github.com/guansss/pixi-live2d-display)
- [Live2D 官方文檔](https://docs.live2d.com/)
- [Inochi Creator（開源替代）](https://github.com/Inochi2D/inochi-creator)

---

*建立時間：2026-03-03 11:15*
*最後更新：2026-03-03 11:15*
