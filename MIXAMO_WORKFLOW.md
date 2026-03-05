# Mixamo 工作流程

## 步驟 1：上傳模型到 Mixamo

1. 訪問：https://www.mixamo.com
2. 點擊 **"Upload Character"**
3. 上傳 FBX 檔案
4. 等待自動綁定（約 30 秒）

## 步驟 2：選擇動畫

### 推薦動畫列表
| 動畫名稱 | 用途 | Mixamo 搜索關鍵字 |
|---------|------|------------------|
| 待機 | 角色站立 | "Idle" |
| 行走 | 移動 | "Walking" |
| 跑步 | 快速移動 | "Running" |
| 跳躍 | 跳躍動作 | "Jump" |
| 揮手 | 互動 | "Wave" |
| 坐下 | 休息 | "Sitting" |

### 設置參數
- **In Place**: ✅ 勾選（原地動畫）
- **Speed**: 根據需要調整（0.8 ~ 1.2）
- **Stride**: 保持默認

## 步驟 3：下載

- **格式**: FBX Binary
- **Skin**: ✅ 勾選（包含蒙皮）
- **Motion**: ✅ 勾選（包含動畫）

## 步驟 4：整合到遊戲

### 檔案命名規則
```
/assets/animations/
  ├── idle.fbx
  ├── walk.fbx
  ├── run.fbx
  ├── jump.fbx
  └── wave.fbx
```

### 載入到 Three.js
```javascript
const loader = new FBXLoader();
const animations = {};

async function loadAnimation(name, path) {
  const object = await loader.loadAsync(path);
  animations[name] = object.animations[0];
}

// 切換動畫
function playAnimation(name) {
  mixer.stopAllAction();
  const action = mixer.clipAction(animations[name]);
  action.play();
}
```

## 檔案大小估計

| 動畫類型 | 預估大小 |
|---------|---------|
| 待機 | 2-5 MB |
| 行走 | 3-8 MB |
| 跑步 | 3-8 MB |
| 跳躍 | 2-6 MB |

---

*建立時間：2026-03-05 18:10*
