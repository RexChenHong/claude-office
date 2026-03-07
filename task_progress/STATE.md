# Claude Office - Task State Tracking

- **Last Updated**: 2026-03-07 03:00

---

## Active Tasks

*No active tasks.*

## Recently Completed

| Task ID | Type | Result | Title | File |
|---------|------|--------|-------|------|
| 20260307-2_REFACTOR_RecastCrowd | REFACTOR | DONE | 棄用手寫碰撞(-202行)，改用 Recast Crowd 統一導航+碰撞+避障 | PR #2 (fix/walking-arm-distortion) |
| 20260307-1_FIX_NavMeshPathfinding | FIX | DONE | NavMesh 升級 — recast-navigation-js (Detour A*) + 程式化地板解決斷島問題 | PR #2 (fix/walking-arm-distortion) |
| 20260306-2_FEAT_CharacterRoamingAI | FEAT | DONE | Character Roaming AI — FSM漫遊+11動畫+Wall Sliding物理碰撞 | PR #2 (fix/walking-arm-distortion) |
| 20260306-1_FIX_RetargetSkeletonAlignment | FIX | 6/6 DONE | Mixamo Retarget — 全5角色IK完成(GroupB:IK打字, GroupA:bind-pose坐姿) | TASKS/20260306-1_FIX_RetargetSkeletonAlignment.md |

## System Health

| Component | Status |
|-----------|--------|
| V7 Mixamo 前端 | Active - http://:8055/v7-mixamo.html |
| PM2 UI Service | Active - port 8055 |
| PM2 Monitor | Active - port 8053 |
| Blender MCP | Connected |
| Character Roaming | Active - Demo mode (20s roam / 20s session cycle) |

## Project Version

| Component | Version |
|-----------|---------|
| Scene | V64 (監獄風格) |
| Character System | V7 (Mixamo 3D) + Roaming AI + Recast Crowd |
| Navigation | recast-navigation-js Crowd — 統一路徑+碰撞+避障（程式化 NavMesh） |
| Models | 5 GLB (alice, columbina, flins, lauma, zibai) |
| Animations | 21 FBX (10 original + 11 new roaming) |

## Archives

| Path | File |
|------|------|
| *(empty)* | |
