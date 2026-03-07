# Session Binding Design -- Claude Office 3D x CLI Activity

## Summary

Let 3D office characters reflect real Claude CLI session states. Characters stay at their workstation while a session is open, with visual indicators (nameplate + color) showing session identity and status.

## Architecture

- **Data source**: Existing session-monitor WebSocket (:8053), no modification needed
- **Change scope**: v7-mixamo.html only (+ PM2 startup config)
- **Approach**: Handle all 5 WebSocket event types; add Three.js Sprite nameplates

## State Mapping

| WebSocket Event    | Character Behavior                        | Nameplate Color |
|--------------------|-------------------------------------------|-----------------|
| `session_open`     | Load character, go to workstation, sit    | White           |
| `session_working`  | Typing animation at workstation           | Red             |
| `session_idle`     | Seated idle animation at workstation      | Yellow          |
| `session_close`    | Stand up, walk to exit, fade out          | (removed)       |

### Core Rule

**Session open = character stays at workstation.** No roaming while session exists. Only `session_close` triggers leaving the workstation. This ensures a "standing by" visual at all times.

### No-Session Characters

Characters without a bound session continue roaming as demo NPCs (backwards-compatible with current demo mode).

## Nameplate System

- **Tech**: Three.js `Sprite` + `CanvasTexture`
- **Position**: Follows character, Y offset ~0.3m above head
- **Content**: Project short name extracted from path
  - `-mnt-e-drive-trading` -> `trading`
  - `-mnt-e-drive-claude-office` -> `claude-office`
- **Color coding**: Working=Red, Idle=Yellow, Open=White
- **Demo mode**: Shows default name (e.g., `demo-cto`)

## Connection Mode

- Page load: auto-connect to WebSocket :8053 (no manual `connectLive()`)
- Connected: live mode -- sessions control characters
- Disconnected: fallback to demo mode, background retry every 3s
- Seamless transition: session-monitor starts later -> auto picks up

## Persistence (PM2 Startup)

- `pm2 startup` + `pm2 save` for boot persistence
- UI (:8055) and Monitor (:8053) auto-start on reboot
- Open browser anytime to see live state

## Files to Modify

- `src/ui/public/v7-mixamo.html` -- all frontend changes
- PM2 config -- startup persistence

## Constraints

- Do NOT modify session-monitor (src/session-monitor/index.js)
- Do NOT modify locked objects (desks, monitors, chairs, walls, railings)
- Typing animation ONLY during `session_working`, never in roaming animation pool
