# NavMesh Pathfinding Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace hand-coded collision/pathfinding with three-pathfinding NavMesh so characters never walk through furniture.

**Architecture:** Create a walkable-area mesh in Blender (flat plane with obstacle holes), export as GLB, load with three-pathfinding. Characters use `findPath()` for A* routing and `clampStep()` per frame to stay on the mesh. All hand-coded collision code gets deleted.

**Tech Stack:** three-pathfinding 1.3.0 (CDN), Blender MCP (NavMesh creation), Three.js 0.160.0

---

## Context

### File to modify
- `/mnt/e_drive/claude-office/src/ui/public/v7-mixamo.html` (single-file app, ~1900 lines)

### Current architecture (to be replaced)
- `COLLISION_WALLS` (line 784-826): ~40 wall segments
- `COLLISION_BOXES` (line 829-843): 9 AABB furniture boxes
- `pointToSegmentDistance`, `pointToAABBDistance`, `nearestPointOnAABB` (line 845-865)
- `checkCollision` (line 877-887): checks walls + boxes
- `getNearestWallNormal` (line 891-940): wall sliding normals
- `wallSlide` (line 942-951): movement projection
- `getSection`, `getDoorForSection` (line 968-982): glass partition routing
- `MEETING_ROOM`, `isInMeetingRoom` (line 992-997): meeting room detection
- `deskApproachSide` (line 994-...): desk gap avoidance
- `findPath` (line 999-1085): hand-coded waypoint pathfinding
- Stuck timer in `updateCharacterMovement` (line 1582-1597)
- `checkCollision` calls in `avoidCharacters` (line 1695-1696)

### What stays unchanged
- All animation code (retarget, IK, FBX loading, switchAnimation)
- FSM states (ROAMING_CHOOSE, ROAMING_WALK, ROAMING_ARRIVE, ROAMING_IDLE, RETURNING, WORKING)
- POI_TABLE and roaming logic
- WebSocket connection
- Demo mode
- WORKSTATIONS, CELLS, FACING constants

### Scene dimensions (Blender Y -> Three.js Z = -Y)

```
Three.js coordinate map (top-down, Z points south):

z=-8 ┌─────────────────────────────────────┐ x=-8 to x=8
     │  [Desk1][Desk2]  [Desk3]  [Desk4][Desk5]  │ z ~ -5.5
     │  [Chair][Chair]  [Chair]  [Chair][Chair]  │ z ~ -6.0
z=-3 ├──door──────door──────door──────────────────┤ Long wall
     │                                            │
     │  ┌MeetingRoom┐    Corridor                 │
     │  │  Table     │                             │
     │  │  Chairs    │                             │
     │  └────door────┘                             │
z=+4 ├─────────────────┬cell┬cell┬cell┬cell┬cell──┤ Cell front
     │                 │sofa│sofa│sofa│sofa│sofa│  │
z=+7 └─────────────────┴────┴────┴────┴────┴────┘
```

Key locations:
- Desks: x = -6.5, -4.5, 0, 4.5, 6.5 at z ~ -5.5 (1.4m wide, 0.76m deep)
- Chairs: same x, z ~ -6.025
- Long wall: z = -3, doors at x = -5.5, 0, 5.5 (1.2m wide)
- Glass partitions: x = -2.5 and x = 2.5, from z=-3.15 to z=-7
- Meeting room: x=-7.85 to -2, z=1 to 6.85, door at x=-2, z=3.4~4.6
- Cells: x=0 to 8, z=4 to 7, each 1.6m wide, 0.8m door openings
- Floor bounds: roughly x=-8 to 8, z=-7 to 7

---

### Task 1: Create NavMesh in Blender

**Files:**
- Create: `/mnt/e_drive/claude-office/src/ui/public/blender/exports/navmesh.glb`

**Step 1: Create walkable floor plane in Blender via MCP**

Use Blender MCP `execute_blender_code` to create a NavMesh plane. The NavMesh is a flat mesh at y=0 that covers all walkable areas. Non-walkable areas (furniture, walls) are holes in the mesh.

Strategy: Create one large plane, then use boolean difference to cut out obstacles. Alternatively (simpler): build the NavMesh from individual rectangular walkable zones and join them.

The **additive approach** is simpler and more precise for our rectangular layout:

```python
import bpy
import bmesh

# Clear existing navmesh if any
for obj in bpy.data.objects:
    if obj.name.startswith('NavMesh'):
        bpy.data.objects.remove(obj, do_unlink=True)

# Helper: create a rectangle at y=0
def add_rect(bm, x1, y1, x2, y2):
    """Add a rectangular face. Blender coords: x=x, y=-z(threejs), z=0(up)"""
    v1 = bm.verts.new((x1, y1, 0))
    v2 = bm.verts.new((x2, y1, 0))
    v3 = bm.verts.new((x2, y2, 0))
    v4 = bm.verts.new((x1, y2, 0))
    bm.faces.new((v1, v2, v3, v4))

bm = bmesh.new()

# MARGIN = 0.35 (character radius 0.3 + buffer 0.05)
M = 0.35

# === CORRIDOR (between long wall z=-3 and cells z=+4) ===
# Full width corridor: x=-8 to 8, Blender y=-4 to 3 (Three.js z=-3 to +4... wait)
# Blender Y = -ThreeJS_Z. So Three.js z=-3 -> Blender y=3, Three.js z=4 -> Blender y=-4
# Corridor in Three.js: z = -3+M to +4-M (wall clearance)
# In Blender: y = -(z) => y = 3-M to -4+M => y = -3.65 to 2.65
# But meeting room wall is at Three.js z=1 (Blender y=-1) on west side
# Cells start at Three.js z=4 (Blender y=-4)
# Main corridor: x=-8+M to 8-M, Three.js z from -3+M to cell_front-M
add_rect(bm, -8+M, -4+M, 8-M, 3-M)
# Note: this is the main open area. Blender y from -3.65 to 2.65

# === WORKSTATION AISLES ===
# Characters need to reach chairs from corridor through wall doors
# Doors in long wall at x=-5.5, 0, 5.5 (width 1.2m = x +/- 0.6)
# Below long wall (Three.js z < -3, Blender y > 3):
# Aisle between wall and desks: Three.js z=-3 to desk_front=-5.12+M
# In Blender: y = 3 to 5.12-M = y from 3 to 4.77
# But only through door openings - full width aisle below wall
add_rect(bm, -8+M, 3-M, 8-M, 5.88-M)  # aisle between wall and desk back edge

# Chair approach zones - one per workstation, extending behind desks
# Desk Z range: Three.js -5.88 to -5.12, Blender 5.12 to 5.88
# Chairs at Three.js z=-6.025, Blender y=6.025
# Need walkable path from desk side to chair
# 5 chair slots, between glass partitions at x=-2.5 and 2.5
# West section (x < -2.5): desks 1,2 at x=-6.5, -4.5
# Center section (x -2.5 to 2.5): desk 3 at x=0
# East section (x > 2.5): desks 4,5 at x=4.5, 6.5

# Chair zones (behind each desk, extending to chair position)
# Each chair zone: desk_center_x - 0.5 to desk_center_x + 0.5, z from desk_back to chair
for cx in [-6.5, -4.5, 0.0, 4.5, 6.5]:
    # In Blender: x same, y from 5.88-M (desk back+margin) to 6.5 (behind chair)
    add_rect(bm, cx - 0.5, 5.88-M, cx + 0.5, 6.5)

# === MEETING ROOM ===
# Three.js: x=-7.85 to -2, z=1 to 6.85, door at x=-2, z=3.4 to 4.6
# In Blender: x=-7.85 to -2, y=-1 to -6.85, door at x=-2, y=-3.4 to -4.6
# Walkable area inside (avoid table x=-5.9 to -4.1, Three.js z=3.5 to 4.5 => Blender y=-3.5 to -4.5)
# Room floor minus table:
# Top part (above table): y from -1-M to -3.5+M
add_rect(bm, -7.85+M, -1-M, -2+M, -3.5+M)
# Bottom part (below table): y from -4.5-M to -6.85+M
add_rect(bm, -7.85+M, -4.5-M, -2+M, -6.85+M)
# Left of table: x from -7.85+M to -5.9+M, y = -3.5+M to -4.5-M
add_rect(bm, -7.85+M, -3.5+M, -5.9+M, -4.5-M)
# Right of table: x from -4.1-M to -2+M, y = -3.5+M to -4.5-M
add_rect(bm, -4.1-M, -3.5+M, -2+M, -4.5-M)

# Meeting room door connection to corridor
# Door at x=-2, Three.js z=3.4 to 4.6, Blender y=-3.4 to -4.6
# Need a connecting strip from corridor to room interior through door
add_rect(bm, -2-M, -3.4-M, -2+M+0.5, -4.6+M)

# === CELL INTERIORS ===
# 5 cells, each 1.6m wide, Three.js z=4 to 7, Blender y=-4 to -7
# Cell 1: x=0 to 1.6, door at x=0.4 to 1.2
# Sofa at back: Blender y approx -6.25 to -6.85
# Walkable: front of cell to sofa front
for i in range(5):
    cx_start = i * 1.6
    add_rect(bm, cx_start+M, -4-M, cx_start+1.6-M, -6.85+M)

# Create mesh from bmesh
mesh = bpy.data.meshes.new('NavMesh')
bm.to_mesh(mesh)
bm.free()

obj = bpy.data.objects.new('NavMesh', mesh)
bpy.context.collection.objects.link(obj)

# Triangulate (three-pathfinding requires triangulated mesh)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.triangulate()
# Remove doubles to merge shared vertices between rectangles
bpy.ops.mesh.remove_doubles(threshold=0.01)
bpy.ops.object.mode_set(mode='OBJECT')

print(f"NavMesh created: {len(mesh.polygons)} triangles, {len(mesh.vertices)} vertices")
```

**IMPORTANT NOTES for the engineer:**
- Blender Y = -(Three.js Z). All coordinates above use this conversion.
- The NavMesh must be **triangulated** (three-pathfinding requires triangles).
- Run `remove_doubles` to merge vertices where rectangles share edges (critical for pathfinding connectivity).
- Test: After creating, visually inspect in Blender that all areas are connected.
- The margin M=0.35 ensures characters (radius 0.3) don't visually clip furniture edges.

**Step 2: Export NavMesh as GLB**

```python
import bpy

# Select only NavMesh
bpy.ops.object.select_all(action='DESELECT')
bpy.data.objects['NavMesh'].select_set(True)
bpy.context.view_layer.objects.active = bpy.data.objects['NavMesh']

bpy.ops.export_scene.gltf(
    filepath='/mnt/e_drive/claude-office/src/ui/public/blender/exports/navmesh.glb',
    export_format='GLB',
    use_selection=True,
    export_apply=True
)
print("NavMesh exported to navmesh.glb")
```

**Step 3: Verify navmesh.glb exists and is small**

Run: `ls -la /mnt/e_drive/claude-office/src/ui/public/blender/exports/navmesh.glb`
Expected: File exists, size < 50KB (simple flat mesh).

---

### Task 2: Add three-pathfinding to importmap and load NavMesh

**Files:**
- Modify: `/mnt/e_drive/claude-office/src/ui/public/v7-mixamo.html`

**Step 1: Add three-pathfinding to importmap**

Find the importmap block (line ~80):
```html
<script type="importmap">
  {
    "imports": {
      "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
      "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
    }
  }
</script>
```

Add three-pathfinding entry:
```html
<script type="importmap">
  {
    "imports": {
      "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
      "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/",
      "three-pathfinding": "https://cdn.jsdelivr.net/npm/three-pathfinding@1.3.0/+esm"
    }
  }
</script>
```

**NOTE:** If the `+esm` CDN URL doesn't work with importmap (some CDNs redirect), try the direct path: `https://cdn.jsdelivr.net/npm/three-pathfinding@1.3.0/dist/three-pathfinding.module.js`. Test in browser console that the import resolves.

**Step 2: Add import statement**

After existing imports (line ~93), add:
```js
import { Pathfinding } from 'three-pathfinding';
```

**Step 3: Add NavMesh loading in initThreeJS**

Find the `initThreeJS()` function. After the office model loads (after the line `console.log('[Three.js] 場景初始化完成');`), add NavMesh loading:

```js
// ========== NavMesh 導航網格 ==========
const pathfinding = new Pathfinding();
const ZONE = 'office';
let navmeshGroup = null;  // will be set after loading

// Load navmesh
const navmeshGLB = await new Promise((resolve, reject) => {
  new GLTFLoader().load('blender/exports/navmesh.glb', resolve, undefined, reject);
});
const navmeshGeometry = navmeshGLB.scene.children[0].geometry;
// three-pathfinding expects Y-up. GLB from Blender is Y-up by default.
const zone = Pathfinding.createZone(navmeshGeometry);
pathfinding.setZoneData(ZONE, zone);
console.log('[NavMesh] 導航網格載入完成');

// Optional: visualize navmesh for debugging (remove later)
// const navmeshMaterial = new THREE.MeshBasicMaterial({ color: 0x00ff00, wireframe: true, transparent: true, opacity: 0.3 });
// const navmeshVisual = new THREE.Mesh(navmeshGeometry, navmeshMaterial);
// scene.add(navmeshVisual);
```

Make `pathfinding` and `ZONE` accessible to functions that need them (they should be in the same module scope, which they already are since everything is in one `<script type="module">` block).

**Step 4: Verify in browser**

Open `http://localhost:8055/v7-mixamo.html`, check console for:
- `[NavMesh] 導航網格載入完成` - no errors
- No import/loading failures

---

### Task 3: Replace findPath with NavMesh pathfinding

**Files:**
- Modify: `/mnt/e_drive/claude-office/src/ui/public/v7-mixamo.html`

**Step 1: Write new navmeshFindPath function**

Replace the old `findPath()` function and all its helpers (`getSection`, `getDoorForSection`, `isInMeetingRoom`, `deskApproachSide`, `MEETING_ROOM` constant) with:

```js
// ========== NavMesh 路徑規劃 ==========
function navmeshFindPath(from, to) {
  const startVec = new THREE.Vector3(from.x, 0, from.z);
  const endVec = new THREE.Vector3(to.x, 0, to.z);

  const groupID = pathfinding.getGroup(ZONE, startVec);
  const path = pathfinding.findPath(startVec, endVec, ZONE, groupID);

  if (!path || path.length === 0) {
    // Fallback: try closest nodes
    const closestStart = pathfinding.getClosestNode(startVec, ZONE, groupID);
    const closestEnd = pathfinding.getClosestNode(endVec, ZONE, groupID);
    if (closestStart && closestEnd) {
      const retryPath = pathfinding.findPath(
        closestStart.centroid, closestEnd.centroid, ZONE, groupID
      );
      if (retryPath && retryPath.length > 0) {
        return retryPath.map(p => ({ x: p.x, z: p.z }));
      }
    }
    console.warn('[NavMesh] 無法找到路徑', from, to);
    return [{ x: to.x, z: to.z }]; // direct fallback
  }

  return path.map(p => ({ x: p.x, z: p.z }));
}
```

**Step 2: Update all callers of findPath to use navmeshFindPath**

There are 3 call sites:

1. `moveCharacterTo()` (line ~1490): change `findPath(from, to)` -> `navmeshFindPath(from, to)`
2. `characterAI()` ROAMING_CHOOSE case (line ~1749): change `findPath(from, to)` -> `navmeshFindPath(from, to)`
3. Any other reference to old `findPath` (search and replace)

**Step 3: Delete old pathfinding code**

Delete the following functions/constants entirely:
- `WALL_Z`, `DOORS` constants
- `FACING` constant (keep if still used for rotation - check first)
- `getSection()`, `getDoorForSection()`
- `MEETING_ROOM`, `isInMeetingRoom()`
- `deskApproachSide()`
- Old `findPath()` function

**Keep:** `FACING` constant if it's used for character rotation at workstation/cell arrival.

**Step 4: Verify pathfinding works**

Open browser, watch Demo mode:
- Characters should calculate paths and start walking
- Console should show `[NavMesh] 導航網格載入完成` and no path errors
- Characters may still clip through furniture (collision replacement is next task)

---

### Task 4: Replace collision with clampStep

**Files:**
- Modify: `/mnt/e_drive/claude-office/src/ui/public/v7-mixamo.html`

**Step 1: Add per-character navmesh node tracking**

In `loadCharacterModel()`, when creating the character object (line ~1410), add:
```js
navNode: null,  // current navmesh node for clampStep
```

**Step 2: Rewrite updateCharacterMovement to use clampStep**

Replace the entire movement logic in `updateCharacterMovement()`. The new version:

```js
function updateCharacterMovement(character, delta) {
  if (!character.isMoving || character.path.length === 0) return;

  const target = character.path[character.pathIndex];
  const pos = character.model.position;

  const dx = target.x - pos.x;
  const dz = target.z - pos.z;
  const dist = Math.sqrt(dx * dx + dz * dz);

  // 面向行進方向
  if (dist > 0.01) {
    const angle = Math.atan2(dx, dz);
    character.model.rotation.y = angle;
  }

  const step = character.moveSpeed * delta;

  if (dist <= step) {
    // 到達當前路徑點
    pos.x = target.x;
    pos.z = target.z;
    character.pathIndex++;

    if (character.pathIndex >= character.path.length) {
      // 到達最終目標
      character.isMoving = false;
      character.path = [];
      character.pathIndex = 0;
      character.model.rotation.y = character.targetRotation;

      if (character.targetAnimation) {
        switchAnimation(character, character.targetAnimation);
        character.targetAnimation = null;
      }
      console.log(`[Movement] 角色到達目的地`);
    }
  } else {
    // 朝目標移動，用 clampStep 約束在 NavMesh 上
    const moveX = dx * (step / dist);
    const moveZ = dz * (step / dist);

    const startVec = new THREE.Vector3(pos.x, 0, pos.z);
    const endVec = new THREE.Vector3(pos.x + moveX, 0, pos.z + moveZ);
    const clampResult = new THREE.Vector3();

    // Initialize navNode if needed
    if (!character.navNode) {
      const groupID = pathfinding.getGroup(ZONE, startVec);
      character.navNode = pathfinding.getClosestNode(startVec, ZONE, groupID);
    }

    const groupID = pathfinding.getGroup(ZONE, startVec);
    character.navNode = pathfinding.clampStep(
      startVec, endVec, character.navNode, ZONE, groupID, clampResult
    );

    pos.x = clampResult.x;
    pos.z = clampResult.z;
  }
}
```

**Key difference:** No more `checkCollision`, `wallSlide`, stuck timer, or fallback logic. `clampStep` handles everything - if the desired position is off the NavMesh, it clamps to the nearest valid position on the mesh edge.

**Step 3: Update avoidCharacters to use clampStep**

Replace the `checkCollision` calls in `avoidCharacters()`:

```js
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

        // Clamp pushed positions to NavMesh
        const clampA = new THREE.Vector3();
        const clampB = new THREE.Vector3();
        const startA = new THREE.Vector3(a.x, 0, a.z);
        const endA = new THREE.Vector3(a.x + nx * PUSH_FORCE, 0, a.z + nz * PUSH_FORCE);
        const startB = new THREE.Vector3(b.x, 0, b.z);
        const endB = new THREE.Vector3(b.x - nx * PUSH_FORCE, 0, b.z - nz * PUSH_FORCE);

        const gA = pathfinding.getGroup(ZONE, startA);
        const gB = pathfinding.getGroup(ZONE, startB);

        if (chars[i].navNode) {
          chars[i].navNode = pathfinding.clampStep(startA, endA, chars[i].navNode, ZONE, gA, clampA);
          a.x = clampA.x; a.z = clampA.z;
        }
        if (chars[j].navNode) {
          chars[j].navNode = pathfinding.clampStep(startB, endB, chars[j].navNode, ZONE, gB, clampB);
          b.x = clampB.x; b.z = clampB.z;
        }
      }
    }
  }
}
```

**Step 4: Delete old collision code**

Delete entirely:
- `COLLISION_WALLS` array
- `COLLISION_BOXES` array
- `pointToSegmentDistance()`
- `pointToAABBDistance()`
- `nearestPointOnAABB()`
- `checkCollision()`
- `getNearestWallNormal()`
- `wallSlide()`

**Step 5: Verify in browser**

- Characters should walk along NavMesh edges when near obstacles (visible as smooth sliding)
- Characters should NOT walk through any desk, wall, or furniture
- Characters should NOT get stuck (no more stuck timer needed)
- Character avoidance should still push characters apart

---

### Task 5: Verify and polish

**Step 1: Run Demo mode for 10 minutes**

Open browser, let Demo run through full cycle:
- 0-2s: Characters in cells
- 2-20s: Free roaming
- 20-40s: Return to workstations (sit down)
- 40s+: Free roaming again

Watch for:
- Zero furniture clipping
- Zero stuck-in-place walking
- Characters successfully sit at desks
- Characters successfully enter/exit meeting room
- Characters successfully enter/exit cells
- FPS stays >= 30

**Step 2: Enable NavMesh debug visualization if issues found**

Uncomment the debug visualization code from Task 2 Step 3 to see the NavMesh wireframe overlaid on the scene. Verify it matches the floor layout.

**Step 3: Check resource usage**

In browser DevTools:
- Performance tab: check FPS
- Memory tab: check heap size vs before
- Expected: negligible increase (3.7KB library + tiny navmesh geometry)

**Step 4: Expose pathfinding to console for debugging**

Add to the `window` exports at bottom of main():
```js
window.pathfinding = pathfinding;
window.navmeshFindPath = navmeshFindPath;
```

**Step 5: Commit**

```bash
cd /mnt/e_drive/claude-office
git add src/ui/public/v7-mixamo.html src/ui/public/blender/exports/navmesh.glb docs/plans/
git commit -m "feat: replace hand-coded collision with NavMesh pathfinding (three-pathfinding)

- Create NavMesh in Blender covering all walkable areas
- Add three-pathfinding 1.3.0 via CDN importmap
- Replace findPath() with A* NavMesh pathfinding
- Replace checkCollision/wallSlide with clampStep()
- Delete ~200 lines of hand-coded collision/routing code
- Characters physically cannot leave walkable areas"
```

---

## Troubleshooting

### NavMesh zones disconnected
If `findPath()` returns null between areas that should be connected, the NavMesh rectangles don't share vertices. Fix: ensure `remove_doubles` ran in Blender, or increase threshold.

### Characters spawn off NavMesh
If characters start at positions not on the NavMesh, `getGroup()` returns -1. Fix: use `getClosestNode()` to snap to nearest valid position at spawn.

### clampStep returns wrong position
If character teleports or jitters, the `navNode` reference may be stale. Fix: reset `character.navNode = null` when teleporting (e.g., in `moveCharacterTo` or `activateSession`).

### three-pathfinding import fails
If CDN URL doesn't resolve, download the library file manually:
```bash
curl -o /mnt/e_drive/claude-office/src/ui/public/lib/three-pathfinding.module.js \
  "https://cdn.jsdelivr.net/npm/three-pathfinding@1.3.0/dist/three-pathfinding.module.js"
```
Then update importmap to use local path: `"three-pathfinding": "./lib/three-pathfinding.module.js"`
