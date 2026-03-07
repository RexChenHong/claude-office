# 20260306-1_FIX_RetargetSkeletonAlignment

## Metadata
- **Type**: FIX
- **Risk**: LOW (前端 JS 修改，不影響後端/生產)
- **Status**: DONE
- **Created**: 2026-03-06
- **Owner**: CTO (dispatch to SubAgent)

## Title
Mixamo Retarget 骨架對齊修復 — 頭髮已解決，手臂需全新方案

## Description
V7 Mixamo 3D 角色版的 runtime retargeting（即時骨架動作複製）：
1. ~~長頭髮角色的頭髮被 retarget 影響~~ → **已解決**（bind pose 每幀重置）
2. ~~配飾骨頭被拉扯~~ → **已解決**（Weapon/Ribbon/Sleeve/Shawl/Shoulder 也 bind pose 重置）
3. **手臂動作不自然** → **4+ 次迭代全部失敗，需根本性新方案**

## Root Cause Analysis
- 頭髮骨頭掛在 `Bip001 Head` 下 → bind pose 重置解決 ✅
- **手臂核心問題**: Genshin 模型骨頭比例與 Mixamo 骨頭比例差異太大
  - Genshin Group A (columbina/flins/zibai): Clavicle ~1.4m, UpperArm ~1.4m
  - Genshin Group B (alice/lauma): Clavicle ~0.1m（正常）但 UpperArm 仍異常
  - Mixamo 標準: 所有骨頭 < 0.3m
- **Delta retargeting（不論 world-space 或 local-space）在比例差異大的骨架上根本不可行**
  - 旋轉差（delta）在長骨頭上被放大成巨大的位移偏差
  - 衰減只能壓抑動作幅度，無法修正方向和比例

## Failed Iterations (知識累積)

### Iteration 1: World-space delta for all
- 方法: `delta = currentWorldQ * inv(bindWorldQ)` 全身統一
- 結果: 身體/脊椎/腿正常，手臂嚴重變形
- 教訓: World-space delta 在比例相近的骨頭（脊椎/腿）可行，手臂不行

### Iteration 2: Local-space delta + bone-length dampening
- 方法: 手臂改 `localDelta = inv(srcBindLocal) * srcCurrentLocal`，按骨頭長度衰減（>1m=15%, >0.5m=50%）
- 結果: 手指向後彎折
- 教訓: 衰減比例不足以修正根本的比例差異

### Iteration 3: Skip long bones entirely
- 方法: 骨頭長度 > 0.5m 的直接 dampening = 0（不動）
- 結果: 手臂完全不動，看起來像假人
- 教訓: 跳過關鍵骨頭等於放棄動畫

### Iteration 4: Name-based dampening
- 方法: Finger=0, Clavicle/UpperArm=20%, Forearm=60%, Hand=80%
- 結果: 行走時手臂動作仍不自然（船長確認）
- 教訓: **Delta retargeting 方法本身對此骨架比例差不適用**

## Next Approach (待執行)
- 比對 demo FBX `realistic_female_character_for_mixamo.fbx` 骨架 vs Genshin 骨架
- 嘗試完全不同的方法：可能需要 skeleton remapping 而非 delta retargeting
- **一次只處理一個角色**，成功後再推廣

## Files to Modify
- src/ui/public/v7-mixamo.html (主要修改)

## Execution Steps
- [x] 1. 頭髮骨頭每幀重置 bind pose — **成功**
- [x] 2. 配飾骨頭（Weapon/Ribbon/Sleeve）也 bind pose 重置 — **成功**
- [x] 3. 手臂 delta retarget — **4 次迭代失敗 → 2-bone IK 成功（Group B）**
- [x] 4. Group A: bind-pose arms（bone ratio>2 自動偵測，1.3m 骨頭無法做幾何 IK）
- [x] 5. 推廣到 5 個角色（Group B: alice+flins IK打字, Group A: columbina+lauma+zibai bind-pose坐姿）
- [x] 6. 截圖驗證 + PR #1 merged

## Acceptance Criteria
- [x] 頭髮不再跟隨 Mixamo 動畫扭曲，保持自然垂落
- [x] 手臂自然（Group B 打字時手在鍵盤上，Group A bind-pose 自然坐姿）
- [x] 5 個角色都正常顯示
- [x] 無 console error

## Technical Notes
- **FBX 雙層骨頭**: 每個骨頭有同名 parent（`bone.parent.quaternion` 有動畫資料）+ child（identity）
- 角色骨頭命名: `Bip001 *_數字後綴` (原神) vs `mixamorig*` (Mixamo)
- 頭髮骨頭: `Bone_Hair*`，全部掛在 `Bip001 Head` 下
- **身體**: world-space delta retarget（worldQ * srcBindWorldInv * tgtBindWorld → local）— 可行
- **手臂**: ❌ delta retargeting 全部失敗 — 需新方案
- 截圖流程: canvas.toDataURL → Bash base64 decode → ZAI analyze_image → rm
- 影片流程: canvas.captureStream(15) → MediaRecorder → WebM → ffmpeg → MP4 → ZAI analyze_video
- Demo FBX 檔案: `/mnt/e_drive/claude-office/assets/characters/3d/` 內有完整可用的動畫和角色
