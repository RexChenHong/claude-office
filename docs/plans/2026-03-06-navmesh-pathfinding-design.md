# NavMesh Pathfinding Design

## Date: 2026-03-06

## Problem

Characters walk through desks and furniture. Hand-coded collision system (COLLISION_WALLS line segments + COLLISION_BOXES AABBs) is fragile:
- Adjacent desk gaps (0.6m) cause stuck loops
- Sitting POI inside desk bbox causes clipping
- Every new furniture requires manual collision box coordinates + findPath waypoint logic
- Wall sliding, stuck timers, and approach-side logic are band-aids on a fundamentally wrong approach

Game industry solved this decades ago with NavMesh.

## Decision

Adopt **three-pathfinding** (3.7KB gzipped) for NavMesh-based navigation.

### Why three-pathfinding

| Criteria | three-pathfinding | recast-navigation-js | Yuka |
|----------|------------------|---------------------|------|
| Size | 3.7 KB | ~1-2 MB (WASM) | ~30 KB |
| Install | CDN (jsDelivr) | npm only | CDN/npm |
| Complexity | 5 methods | WASM init + multi-pkg | Full Game AI |
| Fit | Perfect for 5 chars, 1 room | Overkill | Overlaps existing FSM |

### Key APIs

- `Pathfinding.createZone(geometry)` - Build navigation zone from mesh
- `Pathfinding.findPath(start, end, zoneID, groupID)` - A* pathfinding
- `Pathfinding.clampStep(start, end, node, zoneID, groupID, out)` - Constrain movement to NavMesh per frame

### What gets deleted

- `COLLISION_WALLS` array (~40 line segments)
- `COLLISION_BOXES` array (9 AABBs)
- `checkCollision()`, `pointToSegmentDistance()`, `pointToAABBDistance()`, `nearestPointOnAABB()`
- `getNearestWallNormal()`, `wallSlide()`
- `findPath()` (hand-coded waypoint logic)
- `deskApproachSide()`
- `getSection()`, `getDoorForSection()`
- Stuck timer logic in `updateCharacterMovement()`

## Architecture

### Blender Workflow

1. Create a flat plane at y=0 covering all walkable floor areas
2. Boolean subtract all obstacles (desks, walls, meeting table, cell bars, sofas)
3. Add margin (~0.3m) around obstacles for character radius
4. Export as `navmesh.glb` (separate from office model)

### Three.js Integration

```
Load navmesh.glb
  -> Extract BufferGeometry
  -> Pathfinding.createZone(geometry)
  -> Pathfinding.setZoneData('office', zone)

Character wants to move A -> B:
  -> groupID = pathfinding.getGroup('office', A)
  -> path = pathfinding.findPath(A, B, 'office', groupID)
  -> Character follows path waypoints

Per-frame movement:
  -> clampStep(currentPos, desiredPos, ...) -> actualPos
  -> Character physically cannot leave NavMesh
```

### NavMesh Zones

Single zone 'office' covering:
- Corridor (z: -3 to +4, full width)
- Workstation aisles (approach paths between desks)
- Meeting room interior (connected via door)
- Cell interiors (connected via door openings)

Workstation chairs and cell sofas are ON the NavMesh (characters walk to them and sit).
Desk surfaces, walls, and furniture are NOT on the NavMesh.

## Success Criteria

1. 5 characters roam 10 minutes: zero clipping, zero stuck
2. FPS >= 30, RAM increase < 10% vs current
3. Adding new furniture = update NavMesh plane in Blender + re-export, zero code changes

## Resources

- three-pathfinding: https://github.com/donmccurdy/three-pathfinding
- CDN: https://www.jsdelivr.com/package/npm/three-pathfinding
- API: createZone, setZoneData, findPath, clampStep, getGroup, getClosestNode, getRandomNode
