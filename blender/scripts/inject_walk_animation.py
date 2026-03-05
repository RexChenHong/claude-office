#!/usr/bin/env python3
"""
策略：保留原始模型完整結構，只注入動畫數據

步驟：
1. 讀取原始模型（IBM/骨骼/材質 全部保留）
2. 從 Blender 導出提取動畫軌道
3. 將動畫數據附加到原始模型的 buffer
4. 更新 bufferViews 和 accessors
"""
import struct
import json

def read_glb(filepath):
    with open(filepath, 'rb') as f:
        f.read(12)
        chunks = []
        while True:
            c = f.read(4)
            if not c:
                break
            chunk_len = struct.unpack('<I', c)[0]
            chunk_type = struct.unpack('<I', f.read(4))[0]
            chunk_data = f.read(chunk_len)
            chunks.append((chunk_type, chunk_data))
        return chunks

def get_json(chunks):
    for t, d in chunks:
        if t == 0x4E4F534A:
            return json.loads(d.decode('utf-8'))
    return None

def get_binary(chunks):
    for t, d in chunks:
        if t == 0x004E4942:
            return d
    return None

print("=== 注入動畫到原始模型 ===\n")

# 1. 讀取原始模型
print("1. 讀取原始模型...")
orig_chunks = read_glb('/mnt/e_drive/claude-office/assets/characters/3d/realistic_female_character__game-ready_3d_model.glb')
orig_gltf = get_json(orig_chunks)
orig_buffer = bytearray(get_binary(orig_chunks))

print(f"   Nodes: {len(orig_gltf.get('nodes', []))}")
print(f"   Animations: {len(orig_gltf.get('animations', []))}")

# 建立骨骼名稱 -> node index 映射
orig_bone_map = {}
for i, node in enumerate(orig_gltf.get('nodes', [])):
    name = node.get('name')
    if name:
        orig_bone_map[name] = i

print(f"   骨骼映射: {len(orig_bone_map)} 個")

# 2. 讀取 Blender 導出
print("\n2. 讀取 Blender 導出...")
blend_chunks = read_glb('/mnt/e_drive/claude-office/blender/exports/character_walk_fixed.glb')
blend_gltf = get_json(blend_chunks)
blend_buffer = get_binary(blend_chunks)

blend_anims = blend_gltf.get('animations', [])
print(f"   Animations: {len(blend_anims)}")

# 建立 Blender 的骨骼映射
blend_bone_map = {}
for i, node in enumerate(blend_gltf.get('nodes', [])):
    name = node.get('name')
    if name:
        blend_bone_map[name] = i

# 3. 提取並重定向動畫
print("\n3. 提取動畫並重定向骨骼索引...")

new_animations = []
new_buffer_data = bytearray()  # 新的動畫數據
new_buffer_views = []
new_accessors = []

for anim in blend_anims:
    if 'Walk' not in anim.get('name', ''):
        continue  # 只處理 Walk 動畫

    print(f"\n處理動畫: {anim.get('name')}")

    new_channels = []
    new_samplers = []

    for ch_idx, channel in enumerate(anim.get('channels', [])):
        target = channel.get('target', {})
        blend_node_idx = target.get('node')

        if blend_node_idx is None:
            continue

        # 獲取骨骼名稱
        blend_node = blend_gltf['nodes'][blend_node_idx]
        bone_name = blend_node.get('name')

        # 找到對應的原始模型 node index
        if bone_name not in orig_bone_map:
            print(f"  ⚠️ 骨骼 {bone_name} 在原始模型中找不到")
            continue

        orig_node_idx = orig_bone_map[bone_name]
        path = target.get('path')  # translation, rotation, scale

        # 處理 sampler
        sampler = anim['samplers'][channel['sampler']]
        input_acc = blend_gltf['accessors'][sampler['input']]
        output_acc = blend_gltf['accessors'][sampler['output']]

        # 複製 input（時間）數據
        input_bv = blend_gltf['bufferViews'][input_acc['bufferView']]
        input_offset = input_bv.get('byteOffset', 0) + input_acc.get('byteOffset', 0)
        input_data = blend_buffer[input_offset:input_offset + input_bv['byteLength']]

        # 複製 output（值）數據
        output_bv = blend_gltf['bufferViews'][output_acc['bufferView']]
        output_offset = output_bv.get('byteOffset', 0) + output_acc.get('byteOffset', 0)
        output_data = blend_buffer[output_offset:output_offset + output_bv['byteLength']]

        # 添加到新 buffer
        input_start = len(new_buffer_data)
        new_buffer_data.extend(input_data)
        input_end = len(new_buffer_data)

        output_start = len(new_buffer_data)
        new_buffer_data.extend(output_data)
        output_end = len(new_buffer_data)

        # 創建新的 bufferView
        input_bv_idx = len(new_buffer_views)
        new_buffer_views.append({
            'buffer': 0,
            'byteOffset': input_start,
            'byteLength': len(input_data),
            'target': 34962  # ARRAY_BUFFER
        })

        output_bv_idx = len(new_buffer_views)
        new_buffer_views.append({
            'buffer': 0,
            'byteOffset': output_start,
            'byteLength': len(output_data),
            'target': 34962
        })

        # 創建新的 accessor
        input_acc_idx = len(new_accessors)
        new_accessors.append({
            'bufferView': input_bv_idx,
            'byteOffset': 0,
            'componentType': input_acc['componentType'],
            'count': input_acc['count'],
            'type': input_acc['type'],
            'max': input_acc.get('max'),
            'min': input_acc.get('min')
        })

        output_acc_idx = len(new_accessors)
        new_accessors.append({
            'bufferView': output_bv_idx,
            'byteOffset': 0,
            'componentType': output_acc['componentType'],
            'count': output_acc['count'],
            'type': output_acc['type'],
            'max': output_acc.get('max'),
            'min': output_acc.get('min')
        })

        # 創建新的 sampler
        sampler_idx = len(new_samplers)
        new_samplers.append({
            'input': input_acc_idx,
            'interpolation': sampler.get('interpolation', 'LINEAR'),
            'output': output_acc_idx
        })

        # 創建新的 channel
        new_channels.append({
            'sampler': sampler_idx,
            'target': {
                'node': orig_node_idx,
                'path': path
            }
        })

    if new_channels:
        new_animations.append({
            'name': anim.get('name'),
            'channels': new_channels,
            'samplers': new_samplers
        })

print(f"\n4. 創建了 {len(new_animations)} 個動畫")
print(f"   新增 bufferViews: {len(new_buffer_views)}")
print(f"   新增 accessors: {len(new_accessors)}")
print(f"   新增 buffer 數據: {len(new_buffer_data)} bytes")

# 4. 合併到原始模型
print("\n5. 合併到原始模型...")

# 擴展 buffer
orig_buffer.extend(new_buffer_data)

# 添加新的 bufferViews（需要調整 offset）
bv_offset = len(orig_gltf.get('bufferViews', []))
for bv in new_buffer_views:
    orig_gltf.setdefault('bufferViews', []).append(bv)

# 添加新的 accessors（需要調整 bufferView index）
acc_offset = len(orig_gltf.get('accessors', []))
for i, acc in enumerate(new_accessors):
    orig_gltf.setdefault('accessors', []).append(acc)

# 添加動畫
orig_gltf.setdefault('animations', []).extend(new_animations)

# 更新 buffer byte length
orig_gltf['buffers'][0]['byteLength'] = len(orig_buffer)

print(f"   最終 bufferViews: {len(orig_gltf.get('bufferViews', []))}")
print(f"   最終 accessors: {len(orig_gltf.get('accessors', []))}")
print(f"   最終 animations: {len(orig_gltf.get('animations', []))}")

# 5. 寫入
print("\n6. 寫入文件...")

output_path = '/mnt/e_drive/claude-office/blender/exports/character_with_walk_injected.glb'
json_data = json.dumps(orig_gltf, separators=(',', ':')).encode('utf-8')

# 計算總長度
total_len = 12 + 8 + len(json_data) + 8 + len(orig_buffer)

with open(output_path, 'wb') as f:
    # Header
    f.write(struct.pack('<I', 0x46546C67))  # magic
    f.write(struct.pack('<I', 2))  # version
    f.write(struct.pack('<I', total_len))

    # JSON chunk
    f.write(struct.pack('<I', len(json_data)))
    f.write(struct.pack('<I', 0x4E4F534A))
    f.write(json_data)

    # BIN chunk
    f.write(struct.pack('<I', len(orig_buffer)))
    f.write(struct.pack('<I', 0x004E4942))
    f.write(orig_buffer)

import os
print(f"\n✅ 完成！")
print(f"   大小: {os.path.getsize(output_path) / 1024 / 1024:.1f} MB")
print(f"   路徑: {output_path}")
