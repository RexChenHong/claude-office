# Character Roaming AI - Design Document

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:writing-plans to create implementation plan from this design.

**Goal:** Characters freely roam with context-appropriate animations when no Claude session is active; naturally walk back to workstations when a session starts.

**Architecture:** POI (Point of Interest) waypoint system + FSM state machine on top of existing collision/pathfinding. ~200 lines JS added to v7-mixamo.html.

**Tech Stack:** Three.js (existing), Mixamo FBX animations (existing + 4 new)

---

## FSM States

```
ROAMING (no Claude session)
  -> IDLE_AT_POI: doing animation at a POI, 5-25s
  -> CHOOSING: randomly pick next POI (unoccupied)
  -> WALKING_TO_POI: findPath() + updateCharacterMovement()
  -> repeat

RETURNING (Claude session starts)
  -> finish current animation naturally
  -> walk back to own workstation via findPath()
  -> transition to WORKING on arrival

WORKING (at workstation)
  -> existing typing/idle logic, unchanged
  -> on session end -> ROAMING
```

Transitions:
- Any state + Claude session -> RETURNING
- RETURNING completes -> WORKING
- WORKING + session ends -> ROAMING

## POI Table

| POI ID | Position (x, z) | Type | Animations | Duration | Notes |
|--------|-----------------|------|-----------|----------|-------|
| corridor-west | (-5, 0) | standing | Standing Idle, Stretching, Looking Around | 8-15s | West corridor |
| corridor-center | (0, 0) | standing | Standing Idle, Looking Around | 8-15s | Center corridor |
| corridor-east | (5, 0) | standing | Standing Idle, Stretching | 8-15s | East corridor |
| meeting-room-1 | (-5, 3) | sitting | Sitting Idle | 10-25s | Meeting room chair |
| meeting-room-2 | (-4, 3) | sitting | Sitting Idle | 10-25s | Meeting room chair |
| own-desk | (per character) | sitting | Sitting Idle | 10-20s | Own workstation, relax |
| coworker-left | (left neighbor desk) | standing | Standing Idle, Waving | 8-15s | Visit left colleague |
| coworker-right | (right neighbor desk) | standing | Standing Idle, Waving | 8-15s | Visit right colleague |
| wander-1 | (-3, 1) | walking | Walk In Circle | 5-10s | Corridor wandering |
| wander-2 | (3, 1) | walking | Walk In Circle | 5-10s | Corridor wandering |
| window-west | (-7, 0) | standing | Leaning, Looking Around | 10-20s | Looking out window |
| window-east | (7, 0) | standing | Leaning, Looking Around | 10-20s | Looking out window |

Each POI has `occupiedBy: null | characterId` to prevent overlap.

## New Mixamo Animations (4 FBX)

| File | Action | Loop | Use |
|------|--------|------|-----|
| Stretching.fbx | Stretch arms | once | Standing POIs |
| Looking Around.fbx | Look left/right | loop | Standing/window POIs |
| Waving.fbx | Wave hand | once | Coworker POIs |
| Leaning.fbx | Lean idle | loop | Window POIs |

## Animation Classification

Each animation tagged as `standing` or `sitting`:
- Standing: Walking, Standing Idle, Stretching, Looking Around, Waving, Leaning, Walk In Circle
- Sitting: Sitting, Sitting Idle, Typing

POI type must match animation type. A standing POI only plays standing animations.

## Group A Arm Handling (Critical)

Characters with `abnormalArms === true` (columbina, lauma, zibai):
- ALL animations use bind-pose arms (existing `character.abnormalArms` flag)
- No per-animation special casing needed
- New standing animations automatically get bind-pose treatment via existing code path:
  ```js
  if (pair.isArm && character.abnormalArms && !useIKNow) {
    pair.tgt.quaternion.copy(pair.tgtBindLocal); // bind-pose
  }
  ```

## Character Avoidance

Per frame, for each character pair (5 chars = 10 pairs):
```
distance = xz distance between two characters
if distance < 0.6m:
  pushDir = normalize(A.pos - B.pos)
  candidateA = A.pos + pushDir * 0.02
  candidateB = B.pos - pushDir * 0.02
  if !checkCollision(candidateA): A.pos = candidateA
  if !checkCollision(candidateB): B.pos = candidateB
```

## POI Occupation Lock

```
choosing POI:
  candidates = POI_TABLE.filter(p => p.occupiedBy === null)
  pick random from candidates (weighted by distance - prefer closer)
  set poi.occupiedBy = characterId

arriving at POI:
  already locked during choosing

leaving POI:
  set poi.occupiedBy = null
```

## Future-Proofing for Scene Objects

When adding furniture/objects later:
1. Add 3D model to scene
2. Add collision lines to COLLISION_WALLS (rectangle = 4 line segments)
3. Optionally add POI near the object
4. AI logic requires zero changes

## Files to Modify

- `src/ui/public/v7-mixamo.html` (main, ~200 lines added)
- `src/ui/public/mixamo/` (4 new FBX files)

## Not In Scope

- No physics engine
- No NavMesh library
- No scene decoration/furniture (separate task)
- No changes to existing WORKING state logic
