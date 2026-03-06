# Character Roaming AI - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Characters freely roam with context-appropriate animations when no Claude session is active; walk back to workstations when a session starts.

**Architecture:** POI waypoint system + FSM on existing collision/pathfinding in v7-mixamo.html. ~200 lines added.

**Tech Stack:** Three.js, Mixamo FBX, existing findPath()/checkCollision()

**Design doc:** `docs/plans/2026-03-06-character-roaming-ai-design.md`

---

### Task 1: Download New Mixamo Animations

**Files:**
- Create: `src/ui/public/mixamo/Stretching.fbx`
- Create: `src/ui/public/mixamo/Looking Around.fbx`
- Create: `src/ui/public/mixamo/Waving.fbx`
- Create: `src/ui/public/mixamo/Leaning.fbx`

**Step 1: Download 4 FBX files from Mixamo**

Go to https://www.mixamo.com/ and download these animations (use "Y Bot" character, FBX Binary, Without Skin):

| Search term | Filename to save as | Settings |
|------------|-------------------|----------|
| "Stretching" | Stretching.fbx | In Place: off |
| "Looking Around" | Looking Around.fbx | In Place: on |
| "Happy Hand Gesture" or "Waving" | Waving.fbx | In Place: on |
| "Leaning" or "Standing Idle 02" | Leaning.fbx | In Place: on |

Place all files in `/mnt/e_drive/claude-office/src/ui/public/mixamo/`.

**Step 2: Verify files load**

Open browser console on `http://localhost:8055/v7-mixamo.html` and run:
```js
const loader = new THREE.FBXLoader();
for (const f of ['Stretching.fbx', 'Looking Around.fbx', 'Waving.fbx', 'Leaning.fbx']) {
  loader.loadAsync('/mixamo/' + f).then(m => console.log(f, 'OK, clips:', m.animations.length)).catch(e => console.error(f, e));
}
```
Expected: All 4 print "OK, clips: 1"

**Step 3: Commit**

```bash
git add src/ui/public/mixamo/
git commit -m "feat(roaming): add 4 new Mixamo idle animations"
```

---

### Task 2: Expand ANIMATION_MAP + POI Data Table

**Files:**
- Modify: `src/ui/public/v7-mixamo.html` (lines ~126-134, add after ANIMATION_MAP)

**Step 1: Expand ANIMATION_MAP**

Find the existing `ANIMATION_MAP` object (line ~126) and add new entries:

```js
const ANIMATION_MAP = {
  'working': 'Typing.fbx',
  'idle': 'Typing.fbx',
  'open': 'Standing Idle.fbx',
  'walking': 'Walking.fbx',
  'closed': 'Sitting.fbx',
  'sitting': 'Sitting.fbx',
  'sitting-idle': 'Sitting Idle.fbx',
  // New roaming animations
  'standing-idle': 'Standing Idle.fbx',
  'stretching': 'Stretching.fbx',
  'looking-around': 'Looking Around.fbx',
  'waving': 'Waving.fbx',
  'leaning': 'Leaning.fbx',
  'walk-circle': 'Walk In Circle.fbx',
  'running': 'Running.fbx'
};
```

**Step 2: Add animation classification**

Add after ANIMATION_MAP:

```js
// Animation pose type: determines which retarget path to use
// 'standing' = character upright, arms at sides (walking arm logic applies)
// 'sitting' = character seated (IK/bind-pose arm logic applies)
const ANIM_POSE_TYPE = {
  'working': 'sitting',
  'idle': 'sitting',
  'open': 'standing',
  'walking': 'standing',
  'closed': 'sitting',
  'sitting': 'sitting',
  'sitting-idle': 'sitting',
  'standing-idle': 'standing',
  'stretching': 'standing',
  'looking-around': 'standing',
  'waving': 'standing',
  'leaning': 'standing',
  'walk-circle': 'standing',
  'running': 'standing'
};

// Animations that should loop (vs play-once)
const ANIM_LOOP_ONCE = new Set(['stretching', 'waving', 'sitting']);
```

**Step 3: Add POI table**

Add after ANIM_LOOP_ONCE:

```js
// Points of Interest for character roaming
// type: 'standing' or 'sitting' (must match ANIM_POSE_TYPE of chosen animation)
// anims: list of animation names to randomly pick from at this POI
// duration: [min, max] seconds to stay
const POI_TABLE = [
  // Corridor standing spots
  { id: 'corridor-w', x: -5, z: 0, type: 'standing', anims: ['standing-idle', 'stretching', 'looking-around'], duration: [8, 15], facing: 0 },
  { id: 'corridor-c', x: 0, z: 0, type: 'standing', anims: ['standing-idle', 'looking-around'], duration: [8, 15], facing: 0 },
  { id: 'corridor-e', x: 5, z: 0, type: 'standing', anims: ['standing-idle', 'stretching'], duration: [8, 15], facing: Math.PI },
  // Window spots
  { id: 'window-w', x: -7, z: 0, type: 'standing', anims: ['leaning', 'looking-around'], duration: [10, 20], facing: Math.PI / 2 },
  { id: 'window-e', x: 7, z: 0, type: 'standing', anims: ['leaning', 'looking-around'], duration: [10, 20], facing: -Math.PI / 2 },
  // Meeting room
  { id: 'meeting-1', x: -5, z: 3, type: 'standing', anims: ['standing-idle', 'looking-around'], duration: [10, 25], facing: Math.PI },
  { id: 'meeting-2', x: -4, z: 3, type: 'standing', anims: ['standing-idle'], duration: [10, 25], facing: 0 },
  // Wandering (walk-in-circle at a spot)
  { id: 'wander-1', x: -3, z: 1, type: 'standing', anims: ['walk-circle'], duration: [5, 10], facing: 0 },
  { id: 'wander-2', x: 3, z: 1, type: 'standing', anims: ['walk-circle'], duration: [5, 10], facing: Math.PI },
];

// Per-character dynamic POIs (own desk, neighbor desks) are added at runtime in initRoamingPOIs()
```

**Step 4: Verify no syntax errors**

Reload `http://localhost:8055/v7-mixamo.html`, check browser console for errors.
Expected: No errors, page loads normally.

**Step 5: Commit**

```bash
git add src/ui/public/v7-mixamo.html
git commit -m "feat(roaming): add POI table, animation classification, and new animation mappings"
```

---

### Task 3: Character Object Extensions + Dynamic POI Init

**Files:**
- Modify: `src/ui/public/v7-mixamo.html` (character object ~line 1155, new function)

**Step 1: Extend character object with AI state**

Find the character object creation (line ~1155, `const character = {`). Add these fields after `targetRotation: 0`:

```js
        // AI roaming state
        aiState: 'IDLE',       // 'ROAMING_IDLE' | 'ROAMING_WALK' | 'ROAMING_CHOOSE' | 'RETURNING' | 'WORKING'
        aiTimer: 0,            // countdown timer for current POI action
        currentPOI: null,      // current POI object reference
        workstationIndex: -1,  // assigned workstation index (set during load)
        sessionActive: false   // whether Claude session is active for this character
```

Also, in `loadCharacterModel()`, the `index` parameter is the workstation index. After `characters.set(sessionId, character)` (line ~1180), add:

```js
      character.workstationIndex = index;
```

**Step 2: Add dynamic POI initialization function**

Add a new function after the POI_TABLE definition:

```js
    // Add per-character POIs (own desk, left/right neighbor)
    function initRoamingPOIs() {
      const charArray = Array.from(characters.values());
      charArray.forEach((char, i) => {
        const ws = WORKSTATIONS[char.workstationIndex];
        if (!ws) return;

        // Own desk (sitting idle, not typing)
        POI_TABLE.push({
          id: `own-desk-${i}`, x: ws.x, z: ws.z + 0.5, type: 'sitting',
          anims: ['sitting-idle'], duration: [10, 20], facing: 0,
          ownerOnly: char.workstationIndex  // only this character uses this POI
        });

        // Left neighbor (if exists)
        if (i > 0) {
          const leftWs = WORKSTATIONS[char.workstationIndex - 1];
          POI_TABLE.push({
            id: `visit-left-${i}`, x: leftWs.x + 0.5, z: leftWs.z + 1.0, type: 'standing',
            anims: ['standing-idle', 'waving'], duration: [8, 15], facing: 0
          });
        }

        // Right neighbor (if exists)
        if (i < charArray.length - 1) {
          const rightWs = WORKSTATIONS[char.workstationIndex + 1];
          POI_TABLE.push({
            id: `visit-right-${i}`, x: rightWs.x - 0.5, z: rightWs.z + 1.0, type: 'standing',
            anims: ['standing-idle', 'waving'], duration: [8, 15], facing: 0
          });
        }
      });

      // Initialize occupiedBy for all POIs
      POI_TABLE.forEach(poi => { poi.occupiedBy = null; });
    }
```

**Step 3: Verify no errors**

Reload page, check console.
Expected: No errors.

**Step 4: Commit**

```bash
git add src/ui/public/v7-mixamo.html
git commit -m "feat(roaming): extend character object with AI state + dynamic POI init"
```

---

### Task 4: FSM Core - characterAI() Function

**Files:**
- Modify: `src/ui/public/v7-mixamo.html` (new function, add before animate())

**Step 1: Implement characterAI()**

Add before the `animate()` function (line ~1434):

```js
    // ========== Character AI - Roaming FSM ==========
    function characterAI(character, delta) {
      // Only roam when no session is active
      if (character.sessionActive) return;
      // Don't interfere while moving (pathfinding handles it)
      if (character.isMoving) return;

      switch (character.aiState) {
        case 'ROAMING_CHOOSE': {
          // Pick a random unoccupied POI
          const candidates = POI_TABLE.filter(p => {
            if (p.occupiedBy !== null) return false;
            // ownerOnly POIs can only be used by their owner
            if (p.ownerOnly !== undefined && p.ownerOnly !== character.workstationIndex) return false;
            // Don't pick current POI again
            if (character.currentPOI && p.id === character.currentPOI.id) return false;
            return true;
          });

          if (candidates.length === 0) {
            // All POIs occupied, just wait
            character.aiTimer = 2.0;
            character.aiState = 'ROAMING_IDLE';
            return;
          }

          // Weighted random: prefer closer POIs (but not deterministic)
          const pos = character.model.position;
          const weighted = candidates.map(p => {
            const dist = Math.sqrt((p.x - pos.x) ** 2 + (p.z - pos.z) ** 2);
            return { poi: p, weight: 1 / (1 + dist * 0.3) };
          });
          const totalWeight = weighted.reduce((sum, w) => sum + w.weight, 0);
          let roll = Math.random() * totalWeight;
          let chosen = weighted[0].poi;
          for (const w of weighted) {
            roll -= w.weight;
            if (roll <= 0) { chosen = w.poi; break; }
          }

          // Lock POI
          chosen.occupiedBy = character;

          // Release old POI
          if (character.currentPOI) {
            character.currentPOI.occupiedBy = null;
          }
          character.currentPOI = chosen;

          // Navigate to POI
          character.targetRotation = chosen.facing;
          character.targetAnimation = null; // we'll set animation on arrival
          character.aiState = 'ROAMING_WALK';

          // Use findPath + movement system
          const from = { x: character.model.position.x, z: character.model.position.z };
          const to = { x: chosen.x, z: chosen.z };
          const dx = to.x - from.x, dz = to.z - from.z;
          const dist = Math.sqrt(dx * dx + dz * dz);

          if (dist < 0.5) {
            // Already close enough, skip walking
            character.aiState = 'ROAMING_ARRIVE';
            return;
          }

          const path = findPath(from, to);
          character.path = path;
          character.pathIndex = 0;
          character.isMoving = true;
          switchAnimation(character, 'walking');
          break;
        }

        case 'ROAMING_WALK': {
          // Movement finished (isMoving went false)
          character.aiState = 'ROAMING_ARRIVE';
          break;
        }

        case 'ROAMING_ARRIVE': {
          // Just arrived at POI, pick and play animation
          const poi = character.currentPOI;
          if (!poi) { character.aiState = 'ROAMING_CHOOSE'; return; }

          // Pick random animation from POI's list
          const animName = poi.anims[Math.floor(Math.random() * poi.anims.length)];

          // Set facing
          character.model.rotation.y = poi.facing;

          // Play animation
          const isLoopOnce = ANIM_LOOP_ONCE.has(animName);
          switchAnimation(character, animName, { loopOnce: isLoopOnce });

          // Set timer
          const [minDur, maxDur] = poi.duration;
          character.aiTimer = minDur + Math.random() * (maxDur - minDur);
          character.aiState = 'ROAMING_IDLE';
          break;
        }

        case 'ROAMING_IDLE': {
          // Waiting at POI
          character.aiTimer -= delta;
          if (character.aiTimer <= 0) {
            character.aiState = 'ROAMING_CHOOSE';
          }
          break;
        }

        case 'RETURNING': {
          // Walk back to workstation (triggered externally)
          // Movement system handles the walk; when isMoving goes false, we're there
          character.aiState = 'WORKING';

          // Release POI
          if (character.currentPOI) {
            character.currentPOI.occupiedBy = null;
            character.currentPOI = null;
          }

          // Play working animation
          switchAnimation(character, 'working');
          break;
        }

        case 'WORKING': {
          // Do nothing, session controls this state
          break;
        }

        default: {
          // Initial state or unknown -> start roaming
          character.aiState = 'ROAMING_CHOOSE';
          break;
        }
      }
    }
```

**Step 2: Hook characterAI into animate loop**

Find the `animate()` function (line ~1436). In the `characters.forEach` callback, add `characterAI(character, delta)` BEFORE `updateCharacterMovement`:

```js
      characters.forEach(character => {
        characterAI(character, delta);    // <-- ADD THIS LINE
        updateCharacterMovement(character, delta);
        if (character.mixer) {
          character.mixer.update(delta);
        }
        syncSkeletonPose(character);
      });
```

**Step 3: Verify basic roaming**

Modify `startDemoMode()`: instead of walking to workstations, let characters roam. Change the setTimeout block (line ~1470) to:

```js
      // 等 2 秒後，初始化 POI 並開始漫遊
      setTimeout(() => {
        initRoamingPOIs();
        // All characters start roaming (no session active)
        characters.forEach(character => {
          character.aiState = 'ROAMING_CHOOSE';
          character.sessionActive = false;
        });
        console.log('[Demo] 角色開始自由漫遊');
      }, 2000);
```

Reload page. Characters should start walking to random POIs after 2 seconds.
Expected: Characters walk to different locations, stop, play an animation, then walk somewhere else.

**Step 4: Commit**

```bash
git add src/ui/public/v7-mixamo.html
git commit -m "feat(roaming): implement FSM core - characters freely roam between POIs"
```

---

### Task 5: Character Avoidance

**Files:**
- Modify: `src/ui/public/v7-mixamo.html` (new function, add to animate loop)

**Step 1: Implement avoidCharacters()**

Add before `characterAI()`:

```js
    // ========== Character Avoidance ==========
    function avoidCharacters() {
      const chars = Array.from(characters.values());
      const MIN_DIST = 0.6;
      const PUSH_FORCE = 0.02;

      for (let i = 0; i < chars.length; i++) {
        for (let j = i + 1; j < chars.length; j++) {
          const a = chars[i].model.position;
          const b = chars[j].model.position;
          const dx = a.x - b.x;
          const dz = a.z - b.z;
          const dist = Math.sqrt(dx * dx + dz * dz);

          if (dist < MIN_DIST && dist > 0.01) {
            const nx = dx / dist;
            const nz = dz / dist;

            const newAx = a.x + nx * PUSH_FORCE;
            const newAz = a.z + nz * PUSH_FORCE;
            const newBx = b.x - nx * PUSH_FORCE;
            const newBz = b.z - nz * PUSH_FORCE;

            if (!checkCollision(newAx, newAz)) { a.x = newAx; a.z = newAz; }
            if (!checkCollision(newBx, newBz)) { b.x = newBx; b.z = newBz; }
          }
        }
      }
    }
```

**Step 2: Add to animate loop**

In `animate()`, add `avoidCharacters()` call after the forEach:

```js
      characters.forEach(character => {
        characterAI(character, delta);
        updateCharacterMovement(character, delta);
        if (character.mixer) {
          character.mixer.update(delta);
        }
        syncSkeletonPose(character);
      });

      avoidCharacters();  // <-- ADD THIS LINE
```

**Step 3: Verify**

Reload page. Watch two characters approach the same area.
Expected: They don't overlap, they smoothly push apart if they get too close.

**Step 4: Commit**

```bash
git add src/ui/public/v7-mixamo.html
git commit -m "feat(roaming): add character-to-character avoidance"
```

---

### Task 6: Session Integration (ROAMING <-> WORKING)

**Files:**
- Modify: `src/ui/public/v7-mixamo.html` (startDemoMode, handleSessionSync, updateCharacterStates)

**Step 1: Add session activation functions**

Add after `characterAI()`:

```js
    // Trigger character to return to workstation (session started)
    function activateSession(character) {
      if (character.sessionActive) return;
      character.sessionActive = true;

      // Release current POI
      if (character.currentPOI) {
        character.currentPOI.occupiedBy = null;
        character.currentPOI = null;
      }

      // If currently moving somewhere else, let them finish the current path segment then redirect
      character.isMoving = false;
      character.path = [];

      // Navigate to workstation
      character.targetAnimation = 'working';
      moveCharacterTo(character, 'workstation', character.workstationIndex);
      character.aiState = 'RETURNING';

      // If already at workstation
      if (!character.isMoving) {
        switchAnimation(character, 'working');
        character.aiState = 'WORKING';
      }
    }

    // Trigger character to start roaming (session ended)
    function deactivateSession(character) {
      if (!character.sessionActive) return;
      character.sessionActive = false;
      character.aiState = 'ROAMING_CHOOSE';
    }
```

**Step 2: Update Demo mode with session simulation**

Replace the `startDemoMode` setTimeout block to simulate session on/off:

```js
      // 等 2 秒後，初始化 POI 並開始漫遊
      setTimeout(() => {
        initRoamingPOIs();
        characters.forEach(character => {
          character.aiState = 'ROAMING_CHOOSE';
          character.sessionActive = false;
        });
        console.log('[Demo] 角色開始自由漫遊');

        // Demo: 15 秒後模擬 Claude session 開始，所有人回工作站
        setTimeout(() => {
          console.log('[Demo] 模擬 Claude session 開始 — 所有人回工作站');
          characters.forEach(character => activateSession(character));
        }, 15000);

        // Demo: 30 秒後模擬 session 結束，重新漫遊
        setTimeout(() => {
          console.log('[Demo] 模擬 session 結束 — 重新漫遊');
          characters.forEach(character => deactivateSession(character));
        }, 30000);
      }, 2000);
```

**Step 3: Update updateCharacterStates() for live WebSocket mode**

In the existing `updateCharacterStates()` function (line ~1386), replace the content with:

```js
    function updateCharacterStates() {
      const sessionArray = Array.from(sessions.values());

      sessionArray.forEach((session, index) => {
        const character = characters.get(session.id);
        if (!character) return;

        if (session.status === 'working' || session.status === 'idle' || session.status === 'open') {
          // Session is active -> return to workstation
          activateSession(character);
        } else {
          // Session closed -> roam freely
          deactivateSession(character);
        }
      });
    }
```

**Step 4: Verify Demo cycle**

Reload page and observe:
- 0-2s: Characters load in cells
- 2s: Characters start roaming (walking to random POIs)
- 17s: All characters walk back to workstations, sit down typing
- 32s: Characters stand up and resume roaming

Expected: Smooth transitions, no teleporting, no wall clipping.

**Step 5: Commit**

```bash
git add src/ui/public/v7-mixamo.html
git commit -m "feat(roaming): session integration - ROAMING <-> WORKING transitions"
```

---

### Task 7: Seated Animation Fix (useIKNow for POI sitting)

**Files:**
- Modify: `src/ui/public/v7-mixamo.html` (syncSkeletonPose)

**Context:** The `syncSkeletonPose` function uses `useIKNow` flag to determine if IK arm logic should apply. Currently this is tied to `seatedAnims` list. Characters sitting at a POI (sitting-idle) need the same IK treatment as at workstations.

**Step 1: Verify seatedAnims list includes all sitting animations**

Find the `seatedAnims` array in `switchAnimation()` (line ~1204):

```js
const seatedAnims = ['idle', 'sitting-idle', 'closed', 'working', 'sitting'];
```

This is already correct - `sitting-idle` is in the list, which is the animation used at POI sitting spots. No change needed here.

**Step 2: Verify syncSkeletonPose IK logic**

Find where `useIKNow` is computed in `syncSkeletonPose()`. Ensure it checks `character.currentState` against the seatedAnims list. If it does, POI sitting will automatically get IK treatment.

Read and verify - if the existing logic already uses `seatedAnims.includes(character.currentState)`, no code change needed. Otherwise, ensure the POI sitting animation names are included.

**Step 3: Commit (only if changes were made)**

```bash
git add src/ui/public/v7-mixamo.html
git commit -m "fix(roaming): ensure seated POI animations get proper IK arm treatment"
```

---

### Task 8: Visual Verification + Polish

**Files:**
- Modify: `src/ui/public/v7-mixamo.html` (minor adjustments)

**Step 1: Full visual test**

Reload page and observe full cycle:

| Check | Expected |
|-------|----------|
| Characters start roaming | Walk to different POIs, play animations |
| No wall clipping | Characters navigate through doors, avoid walls |
| No character overlap | Two characters near each other push apart |
| Group A arms (columbina/lauma/zibai) | Bind-pose arms in all animations (no distortion) |
| Group B arms (alice/flins) | Natural arm movement in walking, IK when seated |
| Session start | All characters walk back to workstations smoothly |
| Session end | Characters stand up and resume roaming |
| Animation transitions | Smooth crossfade, no sudden pops |

**Step 2: Adjust timing/weights if needed**

Based on visual observation, tune:
- POI durations (too long? too short?)
- Walk speed during roaming (should it be slower than current 2.0?)
- POI selection weights
- Character avoidance distance/force

**Step 3: Final commit**

```bash
git add src/ui/public/v7-mixamo.html
git commit -m "feat(roaming): visual polish and timing adjustments"
```

---

### Task 9: Push + PR

**Step 1: Push branch**

```bash
git push origin fix/walking-arm-distortion
```

**Step 2: Create or update PR**

Update existing PR #2 description to include roaming AI changes, or create new PR if preferred.

---

## Execution Notes

- **Group A arms**: The existing `character.abnormalArms` flag + bind-pose code path handles ALL animations automatically. New standing animations (stretching, looking around, etc.) will get bind-pose arms for Group A with zero extra code.
- **Collision safety**: All movement goes through `findPath()` + `checkCollision()` + wall sliding. POI coordinates must be in walkable areas (not inside walls).
- **Animation loading**: `switchAnimation()` already lazy-loads FBX on first use and caches. New animations just need entries in `ANIMATION_MAP`.
- **seatedAnims logic**: When a character sits at a meeting room or own desk during roaming, the existing `seatedAnims` check in `syncSkeletonPose` will correctly activate IK mode.
