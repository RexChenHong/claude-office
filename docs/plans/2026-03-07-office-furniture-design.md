# Office Furniture Decoration Design

## Summary
Add office furniture props (printer, water cooler, potted plants) to Claude Office V7 3D scene to reduce visual monotony.

## Objects

| Object | Location | Approx Coords | NavMesh Box | Style |
|--------|----------|---------------|-------------|-------|
| Copier/Printer | Right corridor, south wall | x=6, z=-7 | 0.6m x 0.5m | Realistic |
| Water Cooler | Left corridor, south wall | x=-6, z=-7 | 0.4m x 0.4m | Realistic |
| Large Plant x2 | Central corridor entrance sides | x=+/-2, z=-2.5 | 0.5m x 0.5m | Realistic |
| Small Plant | Cell area corner | x=0.3, z=4.5 | 0.3m x 0.3m | Realistic |
| Small Plant | Meeting room entrance | x=-2.2, z=4 | 0.3m x 0.3m | Realistic |

## Approach
- Model each object in Blender via Blender MCP
- Export as individual GLB files to `src/ui/public/models/furniture/`
- Load in v7-mixamo.html via GLTFLoader, position at coordinates
- Add corresponding addBox() calls in NavMesh construction to prevent character walk-through
- Pure decoration, no POI interaction

## Constraints
- Do NOT modify locked objects (desks, monitors, chairs, walls, railings)
- Do NOT block doorways or existing POI paths
- Keep total added file size reasonable (< 5MB total)
