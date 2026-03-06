# 20260306-1_FIX_RetargetSkeletonAlignment

## Metadata
- **Type**: FIX
- **Risk**: LOW (前端 JS 修改，不影響後端/生產)
- **Status**: DONE
- **Created**: 2026-03-06
- **Owner**: CTO (dispatch to SubAgent)

## Title
Mixamo Retarget 骨架對齊修復 — 頭髮跳過 + 手部校正

## Description
V7 Mixamo 3D 角色版的 runtime retargeting（即時骨架動作複製）有兩個問題：
1. 長頭髮角色（如 Columbina 27 根頭髮骨頭）的頭髮被 retarget 影響，看起來像手的延伸
2. 手指 bind pose 差異導致手部變形（Mixamo T-pose vs 原神 A-pose）

## Root Cause Analysis
- 頭髮骨頭掛在 `Bip001 Head` 下，Head 被 retarget 旋轉後頭髮跟著動但方向錯誤
- 手指骨頭 delta retargeting 在末端小骨頭上誤差累積放大
- bind pose 世界旋轉差異在手指鏈（4-5 節）上逐級放大

## Files to Modify
- src/ui/public/v7-mixamo.html (主要修改)

## Execution Steps
- [x] 1. 頭髮骨頭每幀重置 bind pose（hairBindPoses 機制），不參與 retarget
- [x] 2. 跳過整條手臂鏈（Clavicle→UpperArm→Forearm→Hand→Finger），避免 T/A-pose 差異造成變形
- [x] 3. 用戶目視驗證修復效果（Playwright 截圖 timeout，改人工確認）
- [ ] 4. 部署到 PM2 服務（已自動部署，PM2 watch 模式）

## Acceptance Criteria
- [x] 頭髮不再跟隨 Mixamo 動畫扭曲，保持自然垂落
- [x] 手臂/手指不再明顯變形（代價：手部動畫不顯示，working 動畫只有身體動作）
- [x] 5 個角色都正常顯示
- [x] 無 console error

## Known Limitations
- 手臂完全跳過 retarget，因此 working/typing 動畫中手部保持靜止
- 未來可考慮只對手臂做 bind pose 補償而非完全跳過

## Technical Notes
- 角色骨頭命名: `Bip001 *_數字後綴` (原神) vs `mixamorig*` (Mixamo)
- 頭髮骨頭: `Bone_Hair*`，全部掛在 `Bip001 Head` 下
- retarget 核心函數: `syncSkeletonPose()` (line 286)
- 骨頭配對: `buildBonePairs()` (line 241)
- 每幀 delta 計算: worldQ * srcBindWorldInv * tgtBindWorld → local
