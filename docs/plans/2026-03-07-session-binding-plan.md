# Session Binding Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Connect 3D office characters to real Claude CLI session states via WebSocket, with nameplates showing session identity.

**Architecture:** Handle all WebSocket event types in v7-mixamo.html to drive character FSM states. Add Three.js Sprite nameplates above characters. Auto-connect on page load with demo fallback. PM2 startup for boot persistence.

**Tech Stack:** Three.js (Sprite, CanvasTexture), WebSocket, PM2

**Design doc:** `docs/plans/2026-03-07-session-binding-design.md`

---

### Task 1: Auto-Connect WebSocket on Page Load

**Files:**
- Modify: `src/ui/public/v7-mixamo.html:1624-1665` (main function)
- Modify: `src/ui/public/v7-mixamo.html:1346-1374` (connectWebSocket)

**Step 1: Modify main() to auto-connect after demo mode starts**

In `main()` (line 1625), after `startDemoMode()` and `animate()`, replace the manual `connectLive` block with auto-connect:

```javascript
// Replace lines 1654-1660 with:
// Auto-connect to Session Monitor (fallback to demo mode if unavailable)
console.log('[V7-Mixamo] 自動連接 Session Monitor...');
connectWebSocket();
console.log('[V7-Mixamo] 啟動完成（Live 模式自動連接中）');
```

**Step 2: Update connectWebSocket() to not show loading text**

In `connectWebSocket()` (line 1346), remove the `loadingText.textContent` line since page is already loaded:

```javascript
function connectWebSocket() {
  // Remove: loadingText.textContent = '連接 Session Monitor...';
  ws = new WebSocket(`ws://${location.hostname}:8053`);
  // ... rest unchanged
}
```

**Step 3: Verify in browser**

Open `http://localhost:8055/v7-mixamo.html`, check console for:
- `[V7-Mixamo] 自動連接 Session Monitor...`
- Either `[WS] 已連接到 Session Monitor` (if monitor running) or reconnect attempts
- Demo characters should still roam normally regardless

**Step 4: Commit**

```bash
git add src/ui/public/v7-mixamo.html
git commit -m "feat(session): auto-connect WebSocket on page load"
```

---

### Task 2: Handle All WebSocket Event Types

**Files:**
- Modify: `src/ui/public/v7-mixamo.html:1356-1361` (ws.onmessage)
- Modify: `src/ui/public/v7-mixamo.html:1401-1413` (updateCharacterStates)
- Modify: `src/ui/public/v7-mixamo.html:1544-1565` (activateSession / deactivateSession)

**Step 1: Expand ws.onmessage to handle all 5 event types**

Replace the current `ws.onmessage` handler (lines 1356-1361):

```javascript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  switch (data.type) {
    case 'sync':
      handleSessionSync(data.sessions);
      break;
    case 'session_open':
      handleSessionOpen(data.sessionId, data.project);
      break;
    case 'session_working':
      handleSessionWorking(data.sessionId);
      break;
    case 'session_idle':
      handleSessionIdle(data.sessionId);
      break;
    case 'session_close':
      handleSessionClose(data.sessionId);
      break;
  }
};
```

**Step 2: Add individual event handler functions**

Add after `updateCharacterStates()` (after line 1413):

```javascript
// ========== Individual Session Event Handlers ==========
function handleSessionOpen(sessionId, project) {
  if (sessions.has(sessionId)) return; // Already tracked
  if (sessions.size >= 5) return; // Max characters

  const session = { id: sessionId, project: project, status: 'open' };
  sessions.set(sessionId, session);

  // Find or create character for this session
  const existingChar = characters.get(sessionId);
  if (!existingChar) {
    // Assign first available demo character to this session
    const demoChars = Array.from(characters.entries()).filter(
      ([key]) => key.startsWith('demo-') && !Array.from(sessions.values()).some(s => characters.get(s.id) === characters.get(key))
    );
    if (demoChars.length > 0) {
      const [demoKey, demoChar] = demoChars[0];
      // Rebind: remove old key, add new key
      characters.delete(demoKey);
      characters.set(sessionId, demoChar);
      demoChar.sessionId = sessionId;
    }
  }

  const character = characters.get(sessionId);
  if (character) {
    activateSession(character);
    updateNameplate(character, project, 'open');
  }

  updateSessionStatus(`${sessions.size} 個 Session 活躍`);
  console.log(`[Session] Open: ${sessionId} (${project})`);
}

function handleSessionWorking(sessionId) {
  const session = sessions.get(sessionId);
  if (!session) return;
  session.status = 'working';

  const character = characters.get(sessionId);
  if (character) {
    if (!character.sessionActive) activateSession(character);
    // Ensure typing animation
    if (character.currentState !== 'working' && character.aiState === 'WORKING') {
      switchAnimation(character, 'working');
    }
    updateNameplate(character, session.project, 'working');
  }
}

function handleSessionIdle(sessionId) {
  const session = sessions.get(sessionId);
  if (!session) return;
  session.status = 'idle';

  const character = characters.get(sessionId);
  if (character) {
    if (!character.sessionActive) activateSession(character);
    // Switch to seated idle (NOT roaming - stay at workstation)
    if (character.aiState === 'WORKING') {
      switchAnimation(character, 'sitting-idle');
    }
    updateNameplate(character, session.project, 'idle');
  }
}

function handleSessionClose(sessionId) {
  const session = sessions.get(sessionId);
  if (!session) return;

  const character = characters.get(sessionId);
  if (character) {
    deactivateSession(character);
    updateNameplate(character, null, null); // Remove nameplate text or show demo name
    // Rebind character back to demo key
    const agentIndex = character.workstationIndex;
    const demoKey = `demo-${DEMO_AGENTS[agentIndex]}`;
    characters.delete(sessionId);
    characters.set(demoKey, character);
    character.sessionId = null;
  }

  sessions.delete(sessionId);
  updateSessionStatus(sessions.size > 0 ? `${sessions.size} 個 Session 活躍` : 'Demo 模式');
  console.log(`[Session] Close: ${sessionId}`);
}
```

**Step 3: Modify activateSession to NOT allow idle roaming**

The current `activateSession()` is fine as-is (line 1544-1559) -- it sends character to workstation and sets `sessionActive = true`. The key change is that `handleSessionIdle` now calls `switchAnimation(character, 'sitting-idle')` INSTEAD of `deactivateSession()`. No code change needed in `activateSession()` itself.

**Step 4: Update handleSessionSync to use new status mapping**

Replace `updateCharacterStates()` (lines 1402-1413):

```javascript
function updateCharacterStates() {
  for (const [sessionId, session] of sessions) {
    const character = characters.get(sessionId);
    if (!character) continue;

    switch (session.status) {
      case 'working':
        handleSessionWorking(sessionId);
        break;
      case 'idle':
      case 'open':
        handleSessionIdle(sessionId);
        break;
    }
  }
}
```

**Step 5: Verify in browser**

1. Open the page, start a Claude session in another terminal
2. Console should show `[Session] Open: <uuid> (<project>)`
3. Character should go to workstation
4. When Claude is thinking/writing: character types (red nameplate)
5. When Claude waits for input: character sits idle (yellow nameplate)
6. Kill the Claude session: character leaves workstation and roams

**Step 6: Commit**

```bash
git add src/ui/public/v7-mixamo.html
git commit -m "feat(session): handle all WebSocket events with workstation binding"
```

---

### Task 3: Nameplate System (Three.js Sprite + CanvasTexture)

**Files:**
- Modify: `src/ui/public/v7-mixamo.html` (add after switchAnimation function, ~line 1270)

**Step 1: Add createNameplate() function**

Add a utility to create a floating text sprite:

```javascript
// ========== Nameplate System ==========
function createNameplate(text, color) {
  const canvas = document.createElement('canvas');
  canvas.width = 256;
  canvas.height = 64;
  const ctx = canvas.getContext('2d');

  // Clear
  ctx.clearRect(0, 0, 256, 64);

  // Background (semi-transparent black)
  ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
  const textWidth = ctx.measureText(text).width; // measure first
  ctx.font = 'bold 28px Arial';
  const measured = ctx.measureText(text).width;
  const padX = 16;
  const bgWidth = Math.min(measured + padX * 2, 256);
  const bgX = (256 - bgWidth) / 2;
  ctx.beginPath();
  ctx.roundRect(bgX, 8, bgWidth, 48, 8);
  ctx.fill();

  // Text
  ctx.fillStyle = color || '#ffffff';
  ctx.font = 'bold 28px Arial';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(text, 128, 32);

  const texture = new THREE.CanvasTexture(canvas);
  texture.needsUpdate = true;

  const material = new THREE.SpriteMaterial({
    map: texture,
    transparent: true,
    depthTest: false,
  });

  const sprite = new THREE.Sprite(material);
  sprite.scale.set(1.2, 0.3, 1);
  return { sprite, canvas, ctx, texture };
}

function extractProjectName(project) {
  if (!project) return 'demo';
  // "-mnt-e-drive-trading" -> "trading"
  // "-mnt-e-drive-claude-office" -> "claude-office"
  const parts = project.replace(/^-/, '').split('-');
  // Skip common prefixes: mnt, e, drive
  const skip = ['mnt', 'e', 'drive'];
  const meaningful = [];
  let skipping = true;
  for (const p of parts) {
    if (skipping && skip.includes(p)) continue;
    skipping = false;
    meaningful.push(p);
  }
  return meaningful.join('-') || project;
}

const STATUS_COLORS = {
  working: '#ff4444',  // Red
  idle: '#ffcc00',     // Yellow
  open: '#ffffff',     // White
};

function updateNameplate(character, project, status) {
  const text = project ? extractProjectName(project) : (character.sessionId ? '' : `demo-${DEMO_AGENTS[character.workstationIndex]}`);
  const color = status ? (STATUS_COLORS[status] || '#ffffff') : '#888888';

  if (!character.nameplate) {
    // Create nameplate
    const np = createNameplate(text, color);
    character.nameplate = np;
    character.model.add(np.sprite);
    np.sprite.position.set(0, 2.0, 0); // Above head
  } else {
    // Update existing nameplate
    const np = character.nameplate;
    const ctx = np.ctx;
    ctx.clearRect(0, 0, 256, 64);

    // Background
    ctx.font = 'bold 28px Arial';
    const measured = ctx.measureText(text).width;
    const padX = 16;
    const bgWidth = Math.min(measured + padX * 2, 256);
    const bgX = (256 - bgWidth) / 2;
    ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
    ctx.beginPath();
    ctx.roundRect(bgX, 8, bgWidth, 48, 8);
    ctx.fill();

    // Text
    ctx.fillStyle = color;
    ctx.font = 'bold 28px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, 128, 32);

    np.texture.needsUpdate = true;
  }
}
```

**Step 2: Initialize nameplates for demo characters**

In `startDemoMode()` (line 1602), after all characters are loaded, add nameplate initialization. Add inside the `setTimeout` callback (after line 1618):

```javascript
// Add nameplates to demo characters
characters.forEach((character, key) => {
  updateNameplate(character, null, null);
});
```

**Step 3: Verify in browser**

- Demo mode: each character has a gray `demo-cto`, `demo-lead-engineer` etc. nameplate above head
- Nameplates follow characters as they roam
- Text is readable from default camera angle

**Step 4: Commit**

```bash
git add src/ui/public/v7-mixamo.html
git commit -m "feat(session): add floating nameplate system with status colors"
```

---

### Task 4: PM2 Boot Persistence

**Step 1: Check current PM2 status**

```bash
pm2 list
```

Verify both services are running:
- `claude-office-ui` (port 8055)
- `claude-office-monitor` (port 8053)

**Step 2: Configure PM2 startup**

```bash
pm2 startup
```

This outputs a command like `sudo env PATH=... pm2 startup systemd -u rex --hp /home/rex`. Run that exact command.

**Step 3: Save current PM2 process list**

```bash
pm2 save
```

**Step 4: Verify**

```bash
pm2 list
systemctl status pm2-rex  # or whatever user
```

**Step 5: Commit (no code change, just document)**

No file changes needed -- PM2 startup is a system config. Add a note to the design doc if desired.

---

### Task 5: Integration Test & Polish

**Step 1: Full integration test**

1. Open `http://localhost:8055/v7-mixamo.html` in browser
2. Verify demo mode works (5 characters roaming with gray nameplates)
3. Open a new terminal, start a Claude session: `cd /mnt/e_drive/trading && claude`
4. Watch the 3D scene:
   - One character should go to workstation
   - Nameplate should show `trading` in white, then red when working
   - When waiting for input: nameplate turns yellow, character does sitting-idle
5. Exit the Claude session
6. Character should leave workstation and resume roaming
7. Nameplate reverts to demo name

**Step 2: Edge case checks**

- Open 2+ Claude sessions simultaneously -- each gets a different character
- Close sessions in different order -- characters release correctly
- Disconnect session-monitor (pm2 stop) -- scene falls back to demo mode gracefully
- Restart session-monitor (pm2 restart) -- auto-reconnects and picks up sessions

**Step 3: Fix any issues found**

Address visual or behavioral issues discovered during testing.

**Step 4: Final commit**

```bash
git add src/ui/public/v7-mixamo.html
git commit -m "fix(session): integration polish and edge case fixes"
```
