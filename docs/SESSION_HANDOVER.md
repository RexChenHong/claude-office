# Claude Office - 會話銜接文檔

## 📅 更新時間：2026-03-03 23:20 (Asia/Taipei)

---

## 🎯 專案狀態

### 當前版本：V21（HDRI 環境光 + 曝光修正）
- **完成度**：85%
- **測試地址**：http://100.113.156.108:8055/v6.html
- **模型大小**：2.1MB（office_v19.glb）
- **當前問題**：過度曝光（太亮，幾乎全白）

---

## ✅ 已完成（2026-03-03）

### 場景內容

| 區域 | 內容 | 狀態 |
|------|------|------|
| **工作區** | 5 個工作站（桌子、椅子、雙螢幕、鍵盤、檯燈、盆栽） | ✅ |
| **會議室** | 玻璃隔間、橢圓桌、4 椅、白板 | ✅ |
| **休息區** | L 型沙發、茶几、地毯 | ✅ |
| **設備** | 印表機、飲水機、文件櫃、垃圾桶、檯燈、綠植 | ✅ |
| **環境** | 地板、牆面、落地窗、玻璃隔間 | ✅ |

### 版本進度

| 版本 | 日期 | 內容 | 狀態 |
|------|------|------|------|
| **V12** | 03-03 | 修正椅子和螢幕朝向 | ✅ |
| **V13** | 03-03 | 專業室內設計風格（玻璃隔間、黑色框架） | ✅ |
| **V14** | 03-03 | L 型隔間佈局 | ✅ |
| **V15** | 03-03 | 添加設備（印表機、飲水機、文件櫃） | ✅ |
| **V16** | 03-03 | 牆壁連接修正、主官辦公室隔間 | ✅ |
| **V17** | 03-03 | 程序化 PBR 材質（失敗） | ❌ |
| **V18** | 03-03 | 真實 PBR 紋理（導出失敗） | ❌ |
| **V19** | 03-03 | 深色木地板（純色材質） | ✅ |
| **V21** | 03-03 | HDRI 環境光 + 曝光修正（進行中） | 🔄 |

### 技術成就

1. **Blender 建模**
   - ✅ 5 個工作站（正確的椅子和螢幕朝向）
   - ✅ L 型玻璃隔間（會議室 + 休息區）
   - ✅ 所有設備（印表機、飲水機等）
   - ✅ 深色木地板（純色材質）

2. **Three.js 整合**
   - ✅ GLTFLoader 載入 GLB 模型
   - ✅ ACES 電影級色調映射
   - ✅ PCF 軟陰影
   - ✅ 泛光後期處理
   - 🔄 HDRI 環境光（過度曝光問題）

3. **座標系統學習**
   - ✅ Blender 座標系：Y+ 是北方
   - ✅ 旋轉角度：0 = 面向 Y+，π/2 = 面向 X+
   - ✅ 椅子/螢幕定位公式：`offset * sin/cos(rot)`

---

## ⚠️ 當前問題（2026-03-03 23:20）

### 1. 過度曝光（嚴重）
- **症狀**：整個場景幾乎全白，看不清楚物體
- **原因**：
  - HDRI 環境光太亮
  - 曝光度過高（1.5）
  - 所有光源強度過高
- **修正進度**：
  - 曝光度：1.5 → 0.8 → 0.5（仍需調整）
  - 環境光：0.5 → 0.2 → 0.1 → 0.05
  - 半球光：0.6 → 0.4 → 0.2 → 0.1
  - 主光源：1.0 → 0.8 → 0.5 → 0.3
  - HDRI：只用作環境反射，不作為背景
- **下一步**：繼續降低曝光度到 0.3 或更低

### 2. 視覺品質問題
- **症狀**：模型看起來像「幾何圖形」，不像真實照片
- **原因**：
  - 低模（簡單 Cube/Cylinder）
  - 沒有圓角（Bevel）
  - 純色材質（沒有紋理）
  - 缺少烘焙光照（AO）
- **解決方案**：
  - 方案 A：優化當前模型（添加圓角、應用紋理、烘焙光照）
  - 方案 B：下載 Sketchfab 模型（需要付費 $10-50 USD）

### 3. Blender 3.0 限制
- **問題**：GLTF 導出器不支持程序化紋理節點
- **症狀**：紋理無法導出到 GLB
- **解決方案**：在 Three.js 中直接應用紋理

---

## 📋 待辦事項（下一階段）

### 優先級 1：曝光修正
- [ ] 繼續降低曝光度（0.5 → 0.3 → 0.2）
- [ ] 調整 HDRI 強度
- [ ] 測試不同 HDRI（室內 vs 室外）

### 優先級 2：視覺品質提升
- [ ] 添加圓角（Bevel Modifier）
- [ ] 在 Three.js 中應用 PBR 紋理
- [ ] 烘焙環境光遮蔽（AO）
- [ ] 添加更多細節（書籍、咖啡杯等）

### 優先級 3：功能完善
- [ ] 添加景深（DOF）
- [ ] 添加色差效果
- [ ] 優化相機角度
- [ ] 添加用戶互動（點擊工作站查看詳情）

---

## 📁 關鍵檔案路徑

### Blender
```
/mnt/e_drive/claude-office/blender/
├── scripts/
│   ├── create_office_v19.py    # 當前版本（深色木地板）
│   ├── create_office_v20.py    # 紋理測試（失敗）
│   └── ...（其他版本）
├── exports/
│   ├── office_v19.glb          # 2.1MB - 當前版本
│   ├── office_v20.glb          # 2.1MB - 紋理測試（無紋理）
│   └── ...（其他模型）
└── textures/
    ├── wood_diffuse.jpg        # 木地板紋理
    ├── wood_normal.jpg         # 木地板法線
    ├── fabric_diffuse.jpg      # 布料紋理
    └── ...（其他紋理）
```

### Three.js
```
/mnt/e_drive/claude-office/src/ui/
├── v6.html                     # V21 入口（HDRI 環境光）
└── src/
    └── main-office-v6.js       # V6 邏輯
```

### 文檔
```
/mnt/e_drive/claude-office/docs/
├── SESSION_HANDOVER.md         # 本文件
├── BLENDER_LEARNING_NOTES.md   # Blender 學習筆記
└── LAYOUT_V4.md                # 佈局設計
```

---

## 🎮 服務狀態

| 服務 | 端口 | 狀態 |
|------|------|------|
| claude-office-ui | 8055 | ✅ 線上 |
| claude-office-monitor | 8053 | ✅ 線上 |

---

## 🚀 新會話啟動命令

```bash
# 檢查服務
pm2 status

# 測試模型
curl -I http://localhost:8055/blender/exports/office_v19.glb

# 編輯場景
cd /mnt/e_drive/claude-office/blender
blender -b --python scripts/create_office_v19.py

# 重新生成 GLB
blender -b --python scripts/create_office_v19.py --python-expr "
import bpy
bpy.ops.export_scene.gltf(filepath='/mnt/e_drive/claude-office/blender/exports/office_v19.glb', export_format='GLB')
print('EXPORT_DONE')
"

# 測試 HDRI
curl -I https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/1k/studio_small_03_1k.hdr
```

---

## 📝 技術筆記

### 座標系統
- **Blender**：Y+ 是北方，X+ 是東方
- **旋轉**：0 = 面向 Y+，π/2 = 面向 X+，-π/2 = 面向 X-
- **定位公式**：
  ```python
  chair_x = x + offset * math.sin(rot)
  chair_y = y + offset * math.cos(rot)
  ```

### 材質導出限制
- **Blender 3.0**：GLTF 導出器不支持程序化紋理節點
- **解決方案**：在 Three.js 中直接應用紋理

### HDRI 環境光
- **來源**：Poly Haven（免費 CC0）
- **當前**：studio_small_03（室內攝影棚）
- **問題**：太亮，導致過度曝光

---

## 🎯 目標

**達到 Sketchfab 參考模型的 95% 視覺品質**
- **參考模型**：https://sketchfab.com/3d-models/office-ea1d5422c80141aa8ec2478cc359fe41
- **關鍵特徵**：
  - 真實照片級渲染
  - 高品質 PBR 紋理
  - 烘焙光照（AO）
  - 圓角邊緣
  - 細節豐富

---

**最後更新**：2026-03-03 23:20 (Asia/Taipei)
**下次會話**：繼續修正曝光問題 + 提升視覺品質
**交接提示**：當前最大問題是過度曝光，需要繼續降低曝光度
