# IK Arm Retargeting Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace failed delta retargeting for arms with 2-bone IK (inverse kinematics), starting with alice only.

**Architecture:** Each frame, read Mixamo hand world position, scale it to Genshin proportions, then analytically solve the arm chain (UpperArm + Forearm) to reach that target. Body/spine/legs/head keep existing world-space delta retarget. Hair/accessories keep bind pose reset.

**Tech Stack:** Three.js 0.160.0 (CDN importmap), single HTML file, no build step

---

## Context for the Engineer

### File
- **Modify:** `/mnt/e_drive/claude-office/src/ui/public/v7-mixamo.html` (1143 lines, single HTML file)
- PM2 watch mode auto-deploys on save (no manual deploy needed)

### Key Architecture
- Each Genshin character has a **hidden Mixamo dummy** that plays animations
- `buildBonePairs()` (L241-339) creates bone pair table at load time
- `syncSkeletonPose()` (L349-409) runs every frame to copy poses
- **FBX double-bone structure**: `src.parent.quaternion` has animation data, `src.quaternion` is identity
- alice is CHARACTER_MODELS index 3 (`models/vrm/alice.glb`), Group B (Clavicle ~0.1m, UpperArm still abnormally long)
- Both models are scaled to 1.7m height at load time

### Why Delta Retarget Failed for Arms
Genshin UpperArm bone ~1.4m vs Mixamo ~0.25m. Even 5 degree rotation error on a 1.4m bone = 12cm hand offset. Error accumulates down chain. **IK solves this by working backwards from desired hand position.**

### Bone Names
- Mixamo: `mixamorigLeftShoulder` → `mixamorigLeftArm` → `mixamorigLeftForeArm` → `mixamorigLeftHand`
- Genshin: `Bip001_L_Clavicle` → `Bip001_L_UpperArm` → `Bip001_L_Forearm` → `Bip001_L_Hand` (with `_NN` suffix in GLB)
- Same pattern for Right side

### Character Object Shape (L778-798)
```javascript
{
  model, mixamoModel, mixer, skeleton, boneMap,
  bonePairs, hairBindPoses, hipsPair, srcHipsBindY,
  currentAction, currentPosition, currentState, animations,
  path, pathIndex, isMoving, moveSpeed, targetAnimation, targetRotation
}
```

---

## Task 1: Add IK Data Structure to buildBonePairs

**Files:**
- Modify: `v7-mixamo.html` lines 241-339 (`buildBonePairs` function)

**What to do:**

After building the `pairs` array and before the `return` statement, add IK chain data for arm bones. This stores the bone references and measured bone lengths needed by the IK solver.

**Step 1: Add IK chain builder after L306 (after pairs.sort)**

Insert the following code between the `pairs.sort(...)` block (L306) and the `// 收集需要每幀重設 bind pose` comment (L308):

```javascript
      // === IK 手臂鏈 ===
      // 為每隻手臂建立 IK 鏈：Clavicle → UpperArm → Forearm → Hand
      // IK 只用於 alice（index 3），其他角色保持 delta retarget
      const ikChains = [];
      const sides = ['L', 'R'];
      for (const side of sides) {
        const clavicle = pairs.find(p => p.tgt.name.includes(`${side}_Clavicle`));
        const upperArm = pairs.find(p => p.tgt.name.includes(`${side}_UpperArm`));
        const forearm = pairs.find(p => p.tgt.name.includes(`${side}_Forearm`));
        const hand = pairs.find(p => p.tgt.name.includes(`${side}_Hand`));
        if (!clavicle || !upperArm || !forearm || !hand) continue;

        // 測量 Genshin 骨頭世界距離（非骨頭長度，是關節間距離）
        const _p1 = new THREE.Vector3(), _p2 = new THREE.Vector3(), _p3 = new THREE.Vector3(), _p4 = new THREE.Vector3();
        upperArm.tgt.getWorldPosition(_p1);  // 肩關節
        forearm.tgt.getWorldPosition(_p2);   // 肘關節
        hand.tgt.getWorldPosition(_p3);      // 腕關節

        const tgtUpperLen = _p1.distanceTo(_p2);
        const tgtForeLen = _p2.distanceTo(_p3);

        // 測量 Mixamo 骨頭世界距離
        upperArm.src.getWorldPosition(_p1);
        forearm.src.getWorldPosition(_p2);
        hand.src.getWorldPosition(_p3);

        const srcUpperLen = _p1.distanceTo(_p2);
        const srcForeLen = _p2.distanceTo(_p3);

        // Mixamo 肩膀位置（IK 起點參考）
        clavicle.src.getWorldPosition(_p4);
        const srcShoulderBindPos = _p4.clone();

        // Genshin 肩膀位置
        clavicle.tgt.getWorldPosition(_p4);
        const tgtShoulderBindPos = _p4.clone();

        // Pole target 方向：肘部偏向（bind pose 時的肘部相對肩膀方向）
        // 用於控制肘部朝向（向後彎而非向前）
        forearm.tgt.getWorldPosition(_p1);
        upperArm.tgt.getWorldPosition(_p2);
        const elbowDir = _p1.clone().sub(_p2).normalize();

        ikChains.push({
          side,
          clavicle, upperArm, forearm, hand,
          tgtUpperLen, tgtForeLen,
          srcUpperLen, srcForeLen,
          srcShoulderBindPos, tgtShoulderBindPos,
          elbowDir
        });

        console.log(`[IK] ${side} arm: tgt upper=${tgtUpperLen.toFixed(3)} fore=${tgtForeLen.toFixed(3)}, src upper=${srcUpperLen.toFixed(3)} fore=${srcForeLen.toFixed(3)}`);
      }
```

**Step 2: Update the return statement (L339)**

Change:
```javascript
      return { pairs, hairBindPoses: resetBindPoses };
```
To:
```javascript
      return { pairs, hairBindPoses: resetBindPoses, ikChains };
```

**Step 3: Store ikChains in character object**

In `loadCharacterModel()` at L746-748, after extracting `bonePairs` and `hairBindPoses`, also extract `ikChains`:

Change:
```javascript
      const retargetResult = skeleton ? buildBonePairs(mixamoModel, model, skeleton, boneMap) : { pairs: [], hairBindPoses: [] };
      const bonePairs = retargetResult.pairs;
      const hairBindPoses = retargetResult.hairBindPoses;
```
To:
```javascript
      const retargetResult = skeleton ? buildBonePairs(mixamoModel, model, skeleton, boneMap) : { pairs: [], hairBindPoses: [], ikChains: [] };
      const bonePairs = retargetResult.pairs;
      const hairBindPoses = retargetResult.hairBindPoses;
      const ikChains = retargetResult.ikChains;
```

**Step 4: Add ikChains and useIK flag to character object**

In the character object literal (L778-798), add after `hairBindPoses`:

```javascript
        ikChains: ikChains,
        useIK: modelPath.includes('alice'),  // Only alice uses IK initially
```

**Step 5: Verify** — Open browser, check console for `[IK] L arm:` and `[IK] R arm:` log lines with measured bone lengths. No visual change yet.

---

## Task 2: Implement 2-Bone IK Solver

**Files:**
- Modify: `v7-mixamo.html` — insert new function before `syncSkeletonPose` (before L342)

**What to do:**

Add an analytical 2-bone IK solver. This is the standard game dev algorithm:
1. Given: shoulder position, target position, upper arm length, forearm length
2. Use law of cosines to compute elbow angle
3. Construct rotations for UpperArm and Forearm bones

**Step 1: Add the IK solver function**

Insert before the `// 每幀同步骨架姿態` comment (L342):

```javascript
    /**
     * 2-Bone IK Solver (analytical)
     * Solves the arm chain: UpperArm → Forearm to reach target position.
     *
     * @param {THREE.Bone} upperArmBone - The UpperArm bone (Genshin target)
     * @param {THREE.Bone} forearmBone - The Forearm bone (Genshin target)
     * @param {THREE.Vector3} targetWorldPos - Where the hand should be (world space)
     * @param {THREE.Vector3} poleDir - Hint direction for elbow (world space, normalized)
     * @param {number} upperLen - Distance from UpperArm joint to Forearm joint
     * @param {number} foreLen - Distance from Forearm joint to Hand joint
     */
    const _ikShoulderPos = new THREE.Vector3();
    const _ikTargetDir = new THREE.Vector3();
    const _ikCross = new THREE.Vector3();
    const _ikUp = new THREE.Vector3(0, 1, 0);
    const _ikMat = new THREE.Matrix4();
    const _ikQuat = new THREE.Quaternion();
    const _ikParentWorldQInv = new THREE.Quaternion();

    function solveTwoBoneIK(upperArmBone, forearmBone, targetWorldPos, poleDir, upperLen, foreLen) {
      // 1. Get shoulder world position (UpperArm joint position)
      upperArmBone.getWorldPosition(_ikShoulderPos);

      // 2. Direction and distance to target
      _ikTargetDir.copy(targetWorldPos).sub(_ikShoulderPos);
      let dist = _ikTargetDir.length();

      // Clamp to reachable range (avoid NaN in acos)
      const maxReach = upperLen + foreLen;
      const minReach = Math.abs(upperLen - foreLen);
      dist = Math.max(minReach + 0.001, Math.min(maxReach - 0.001, dist));
      _ikTargetDir.normalize();

      // 3. Law of cosines: angle at shoulder
      const cosA = (upperLen * upperLen + dist * dist - foreLen * foreLen) / (2 * upperLen * dist);
      const angleA = Math.acos(Math.max(-1, Math.min(1, cosA)));

      // 4. Law of cosines: angle at elbow
      const cosB = (upperLen * upperLen + foreLen * foreLen - dist * dist) / (2 * upperLen * foreLen);
      const angleB = Math.acos(Math.max(-1, Math.min(1, cosB)));

      // 5. Build rotation plane (using pole direction as hint for elbow orientation)
      // Cross product of target direction and pole direction gives the bend axis
      _ikCross.crossVectors(_ikTargetDir, poleDir);
      if (_ikCross.lengthSq() < 0.0001) {
        // Fallback: use world up if pole is parallel to target
        _ikCross.crossVectors(_ikTargetDir, _ikUp);
      }
      _ikCross.normalize();

      // 6. UpperArm: rotate from target direction by shoulder angle around bend axis
      // The upper arm points toward the elbow (rotated from target dir by angleA)
      _ikQuat.setFromAxisAngle(_ikCross, angleA);
      const upperArmDir = _ikTargetDir.clone().applyQuaternion(_ikQuat);

      // 7. Set UpperArm world rotation to look along upperArmDir
      _ikMat.lookAt(
        _ikShoulderPos,
        _ikShoulderPos.clone().add(upperArmDir),
        poleDir
      );
      const upperWorldQ = new THREE.Quaternion().setFromRotationMatrix(_ikMat);

      // Convert to local space
      if (upperArmBone.parent) {
        upperArmBone.parent.getWorldQuaternion(_ikParentWorldQInv);
        _ikParentWorldQInv.invert();
        upperArmBone.quaternion.copy(_ikParentWorldQInv).multiply(upperWorldQ);
      } else {
        upperArmBone.quaternion.copy(upperWorldQ);
      }
      upperArmBone.updateMatrix();
      upperArmBone.updateMatrixWorld(false);

      // 8. Forearm: bend by (PI - elbow angle) relative to upper arm
      // In local space, forearm just needs to bend by the elbow angle
      const elbowLocalQ = new THREE.Quaternion().setFromAxisAngle(
        new THREE.Vector3(1, 0, 0), // Local X axis (bend axis in forearm's local space)
        -(Math.PI - angleB)
      );

      // Get forearm's bind pose and apply elbow bend
      forearmBone.quaternion.copy(elbowLocalQ);
      forearmBone.updateMatrix();
      forearmBone.updateMatrixWorld(false);
    }
```

**Step 2: Verify** — No visual change yet. Function exists but is not called.

---

## Task 3: Integrate IK into syncSkeletonPose for alice

**Files:**
- Modify: `v7-mixamo.html` — modify `syncSkeletonPose` function (L349-409)

**What to do:**

For characters with `useIK === true`, skip the delta retarget for arm bones (Clavicle/UpperArm/Forearm/Hand) and instead:
1. Retarget Clavicle with world-space delta (same as body — alice's Clavicle is 0.1m, safe)
2. Use 2-bone IK for UpperArm + Forearm targeting the Mixamo hand world position
3. Copy Mixamo hand rotation to Genshin hand (with bind pose compensation)
4. Skip fingers (keep bind pose reset)

**Step 1: Add IK target position helpers**

Add after the existing temp variables (L347, after `const _tmpPos`):

```javascript
    const _ikHandTarget = new THREE.Vector3();
    const _ikMixamoShoulder = new THREE.Vector3();
    const _ikGenshinShoulder = new THREE.Vector3();
```

**Step 2: Modify the bone pair loop in syncSkeletonPose**

Replace the `for (const pair of character.bonePairs)` loop (L359-390) with:

```javascript
      // Determine which bones are handled by IK (skip in pair loop)
      const ikHandledBones = new Set();
      if (character.useIK && character.ikChains) {
        for (const chain of character.ikChains) {
          ikHandledBones.add(chain.upperArm.tgt.name);
          ikHandledBones.add(chain.forearm.tgt.name);
          ikHandledBones.add(chain.hand.tgt.name);
          // Fingers are already armDampen=0, will be skipped anyway
        }
      }

      for (const pair of character.bonePairs) {
        // Skip bones handled by IK
        if (ikHandledBones.has(pair.tgt.name)) continue;

        if (pair.isArm && pair.srcAnimBone && !character.useIK) {
          // Non-IK characters: Local-space delta retargeting for arms (existing code)
          _deltaQ.copy(pair.srcBindLocalInv).multiply(pair.srcAnimBone.quaternion);
          if (pair.armDampen < 1.0) {
            _deltaQ.slerp(_identQ, 1.0 - pair.armDampen);
          }
          pair.tgt.quaternion.copy(pair.tgtBindLocal).multiply(_deltaQ);
        } else if (pair.isArm && character.useIK) {
          // IK character: Clavicle uses world-space delta (safe for alice, 0.1m bone)
          pair.src.getWorldQuaternion(_worldQ);
          _deltaQ.copy(_worldQ).multiply(pair.srcBindWorldInv);
          _worldQ.copy(_deltaQ).multiply(pair.tgtBindWorld);
          if (pair.tgt.parent) {
            pair.tgt.parent.getWorldQuaternion(_parentQ);
            _parentQ.invert();
            pair.tgt.quaternion.copy(_parentQ).multiply(_worldQ);
          } else {
            pair.tgt.quaternion.copy(_worldQ);
          }
        } else {
          // Body/spine/legs/head: World-space delta retargeting (unchanged)
          pair.src.getWorldQuaternion(_worldQ);
          _deltaQ.copy(_worldQ).multiply(pair.srcBindWorldInv);
          _worldQ.copy(_deltaQ).multiply(pair.tgtBindWorld);
          if (pair.tgt.parent) {
            pair.tgt.parent.getWorldQuaternion(_parentQ);
            _parentQ.invert();
            pair.tgt.quaternion.copy(_parentQ).multiply(_worldQ);
          } else {
            pair.tgt.quaternion.copy(_worldQ);
          }
        }

        pair.tgt.updateMatrix();
        pair.tgt.updateMatrixWorld(false);
      }

      // === IK Pass: solve arm chains ===
      if (character.useIK && character.ikChains) {
        for (const chain of character.ikChains) {
          // Get Mixamo hand world position (this is where the hand SHOULD be)
          chain.hand.src.getWorldPosition(_ikHandTarget);

          // Scale: both models are 1.7m, but arm proportions differ
          // Get current Mixamo shoulder position and compute hand offset from shoulder
          chain.upperArm.src.getWorldPosition(_ikMixamoShoulder);
          const handOffset = _ikHandTarget.clone().sub(_ikMixamoShoulder);

          // Scale the offset by the ratio of Genshin arm reach / Mixamo arm reach
          const srcArmLen = chain.srcUpperLen + chain.srcForeLen;
          const tgtArmLen = chain.tgtUpperLen + chain.tgtForeLen;
          const armScale = tgtArmLen / srcArmLen;
          handOffset.multiplyScalar(armScale);

          // Compute target in world space (Genshin shoulder + scaled offset)
          chain.upperArm.tgt.getWorldPosition(_ikGenshinShoulder);
          _ikHandTarget.copy(_ikGenshinShoulder).add(handOffset);

          // Solve IK
          solveTwoBoneIK(
            chain.upperArm.tgt,
            chain.forearm.tgt,
            _ikHandTarget,
            chain.elbowDir,
            chain.tgtUpperLen,
            chain.tgtForeLen
          );

          // Hand: copy Mixamo hand rotation (world-space delta, same as body)
          chain.hand.src.getWorldQuaternion(_worldQ);
          _deltaQ.copy(_worldQ).multiply(chain.hand.srcBindWorldInv);
          _worldQ.copy(_deltaQ).multiply(chain.hand.tgtBindWorld);
          if (chain.hand.tgt.parent) {
            chain.hand.tgt.parent.getWorldQuaternion(_parentQ);
            _parentQ.invert();
            chain.hand.tgt.quaternion.copy(_parentQ).multiply(_worldQ);
          } else {
            chain.hand.tgt.quaternion.copy(_worldQ);
          }
          chain.hand.tgt.updateMatrix();
          chain.hand.tgt.updateMatrixWorld(false);
        }
      }
```

**Step 3: Verify** — Open `http://<host>:8055/v7-mixamo.html` in browser. Watch alice (4th character, index 3). Her arms should move naturally during walking, typing, and sitting. Other 4 characters should be unchanged.

**IMPORTANT:** The IK solver's `lookAt` and elbow bend axis may need tuning. The initial implementation may have the arms pointing in wrong directions because:
- `lookAt` assumes Z-forward, but bones may use different axes
- The local bend axis (`new THREE.Vector3(1, 0, 0)`) may need to be Y or Z depending on bone orientation

If arms point wrong way, the engineer should:
1. Log the bind pose bone axes (bone.matrixWorld columns) for alice's UpperArm
2. Adjust `lookAt` up-vector and forearm bend axis to match

---

## Task 4: Visual Verification via Playwright

**What to do:**

Take Playwright screenshots of alice during:
1. Walking (arms should swing naturally)
2. Sitting/Typing (hands should be roughly near keyboard)

**Step 1: Navigate to the page**

Use `mcp__playwright__browser_navigate` to open `http://localhost:8055/v7-mixamo.html`

**Step 2: Wait for loading**

Use `mcp__playwright__browser_wait_for` to wait for the loading overlay to disappear.

**Step 3: Position camera on alice**

Use `mcp__playwright__browser_evaluate` to run:
```javascript
// Focus camera on alice (index 3)
const alice = Array.from(characters.values())[3];
if (alice) {
  camera.position.set(alice.model.position.x + 2, 2, alice.model.position.z + 3);
  controls.target.set(alice.model.position.x, 1, alice.model.position.z);
  controls.update();
}
```

**Step 4: Take screenshot and analyze**

Use `mcp__playwright__browser_take_screenshot` to capture the current frame, then `mcp__zai-mcp-server__analyze_image` to verify arm posture.

**Step 5: Delete screenshot file after analysis** (per project rules)

---

## Task 5: Iterate and Debug (if needed)

If the arms point in wrong directions after Task 3:

**Common fixes:**

1. **Arms point straight up/down**: The `lookAt` function's up vector needs adjustment. Change `poleDir` to the bone's actual up direction in bind pose.

2. **Elbow bends wrong way**: The pole direction is wrong. Try negating `chain.elbowDir` or using the opposite direction.

3. **Arms rotated 90 degrees**: The bone's local axes don't align with the IK solver's assumption. Need to add a bind pose compensation rotation:
   ```javascript
   // After IK solve, compensate for bind pose axis difference
   const bindCompensation = chain.upperArm.tgtBindLocal.clone();
   upperArmBone.quaternion.premultiply(bindCompensation);
   ```

4. **Arm scale is way off**: Log `armScale` — if it's very large (>5) or very small (<0.2), the bone length measurement is wrong. Check if bone world positions are being read correctly (after updateMatrixWorld).

---

## Task 6: Commit

```bash
cd /mnt/e_drive/claude-office
git add src/ui/public/v7-mixamo.html
git commit -m "feat(retarget): replace arm delta retarget with 2-bone IK for alice

Previous approach (4 iterations of delta retargeting) failed due to
Genshin model bone length mismatch (UpperArm 1.4m vs Mixamo 0.25m).
IK works backwards from desired hand position, avoiding error accumulation.

- Add analytical 2-bone IK solver (law of cosines)
- Build IK chain data (bone lengths, pole direction) at load time
- alice uses IK for arms, other characters keep delta retarget
- Body/spine/legs/head unchanged (world-space delta)
- Hair/accessories unchanged (bind pose reset)

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```
