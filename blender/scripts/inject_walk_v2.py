#!/usr/bin/env python3
"""
修正版：注入動畫到原始模型，正確處理 accessor 索引偏移
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

print("=== 注入動畫（修正版） ===\n")

# 1. 讀取原始模型
print("1. 讀取原始模型...")
orig_chunks = read_glb('/mnt/e_drive/claude-office/assets/characters/3d/realistic_female_character__game-ready_3d_model.glb')
orig_gltf = get_json(orig_chunks)
orig_buffer = bytearray(get_binary(orig_chunks))

# 建立骨骼映射
orig_bone_map = {node.get('name'): i for i, node in enumerate(orig_gltf.get('nodes', [])) if node.get('name')}

# 2. 讀取 Blender 導出
print("2. 讀取 Blender 導出...")
blend_chunks = read_glb('/mnt/e_drive/claude-office/blender/exports/character_walk_fixed.glb')
blend_gltf = get_json(blend_chunks)
blend_buffer = get_binary(blend_chunks)

# 建立骨骼映射
blend_bone_map = {node.get('name'): i for i, node in enumerate(blend_gltf.get('nodes', [])) if node.get('name')}

# 3. 準備追加數據
# 獲取當前的偏移量
acc_offset = len(orig_gltf.get('accessors', []))
bv_offset = len(orig_gltf.get('bufferViews', []))
buffer_offset = len(orig_buffer)

print(f"   Accessor offset: {acc_offset}")
print(f"   BufferView offset: {bv_offset}")
print(f"   Buffer offset: {buffer_offset}")

# 4. 提取動畫
print("\n3. 提取 Walk 動畫...")

new_animations = []
new_buffer = bytearray()

for anim in blend_gltf.get('animations', []):
    if 'Walk' not in anim.get('name', ''):
        continue

    print(f"處理: {anim.get('name')}")

    new_channels = []
    new_samplers = []
    sampler_acc_map = {}  # 舊 accessor -> 新 accessor

    for channel in anim.get('channels', []):
        target = channel['target']
        blend_node_idx = target['node']
        blend_node = blend_gltf['nodes'][blend_node_idx]
        bone_name = blend_node.get('name')

        if bone_name not in orig_bone_map:
            continue

        orig_node_idx = orig_bone_map[bone_name]
        path = target['path']

        # 處理 sampler
        sampler = anim['samplers'][channel['sampler']]

        # 創建或獲取新的 input accessor
        old_input_acc_idx = sampler['input']
        if old_input_acc_idx not in sampler_acc_map:
            # 複製數據
            input_acc = blend_gltf['accessors'][old_input_acc_idx]
            input_bv = blend_gltf['bufferViews'][input_acc['bufferView']]
            input_offset = input_bv.get('byteOffset', 0) + input_acc.get('byteOffset', 0)
            input_data = blend_buffer[input_offset:input_offset + input_bv['byteLength']]

            # 追加到新 buffer
            new_bv_start = len(new_buffer)
            new_buffer.extend(input_data)

            # 創建新 bufferView
            new_bv_idx = bv_offset + len(orig_gltf.get('bufferViews', [])) - bv_offset
            orig_gltf.setdefault('bufferViews', []).append({
                'buffer': 0,
                'byteOffset': buffer_offset + new_bv_start,
                'byteLength': len(input_data)
            })

            # 創建新 accessor
            new_acc_idx = acc_offset + len(orig_gltf.get('accessors', [])) - acc_offset
            orig_gltf.setdefault('accessors', []).append({
                'bufferView': new_bv_idx,
                'byteOffset': 0,
                'componentType': input_acc['componentType'],
                'count': input_acc['count'],
                'type': input_acc['type'],
                'min': input_acc.get('min'),
                'max': input_acc.get('max')
            })

            sampler_acc_map[old_input_acc_idx] = new_acc_idx

        new_input_acc_idx = sampler_acc_map[old_input_acc_idx]

        # 創建或獲取新的 output accessor
        old_output_acc_idx = sampler['output']
        if old_output_acc_idx not in sampler_acc_map:
            output_acc = blend_gltf['accessors'][old_output_acc_idx]
            output_bv = blend_gltf['bufferViews'][output_acc['bufferView']]
            output_offset = output_bv.get('byteOffset', 0) + output_acc.get('byteOffset', 0)
            output_data = blend_buffer[output_offset:output_offset + output_bv['byteLength']]

            new_bv_start = len(new_buffer)
            new_buffer.extend(output_data)

            new_bv_idx = bv_offset + len(orig_gltf.get('bufferViews', [])) - bv_offset
            orig_gltf.setdefault('bufferViews', []).append({
                'buffer': 0,
                'byteOffset': buffer_offset + new_bv_start,
                'byteLength': len(output_data)
            })

            new_acc_idx = acc_offset + len(orig_gltf.get('accessors', [])) - acc_offset
            orig_gltf.setdefault('accessors', []).append({
                'bufferView': new_bv_idx,
                'byteOffset': 0,
                'componentType': output_acc['componentType'],
                'count': output_acc['count'],
                'type': output_acc['type'],
                'min': output_acc.get('min'),
                'max': output_acc.get('max')
            })

            sampler_acc_map[old_output_acc_idx] = new_acc_idx

        new_output_acc_idx = sampler_acc_map[old_output_acc_idx]

        # 創建新 sampler
        new_sampler_idx = len(new_samplers)
        new_samplers.append({
            'input': new_input_acc_idx,
            'output': new_output_acc_idx,
            'interpolation': sampler.get('interpolation', 'LINEAR')
        })

        # 創建新 channel
        new_channels.append({
            'sampler': new_sampler_idx,
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

print(f"   提取了 {len(new_animations)} 個動畫")
print(f"   新增 buffer: {len(new_buffer)} bytes")

# 5. 合併
print("\n4. 合併數據...")

# 擴展 buffer
orig_buffer.extend(new_buffer)
orig_gltf['buffers'][0]['byteLength'] = len(orig_buffer)

# 添加動畫
orig_gltf.setdefault('animations', []).extend(new_animations)

print(f"   最終 accessors: {len(orig_gltf.get('accessors', []))}")
print(f"   最終 bufferViews: {len(orig_gltf.get('bufferViews', []))}")
print(f"   最終 animations: {len(orig_gltf.get('animations', []))}")

# 6. 寫入
print("\n5. 寫入文件...")

output_path = '/mnt/e_drive/claude-office/blender/exports/character_with_walk_v2.glb'
json_data = json.dumps(orig_gltf, separators=(',', ':')).encode('utf-8')
total_len = 12 + 8 + len(json_data) + 8 + len(orig_buffer)

with open(output_path, 'wb') as f:
    f.write(struct.pack('<I', 0x46546C67))
    f.write(struct.pack('<I', 2))
    f.write(struct.pack('<I', total_len))

    f.write(struct.pack('<I', len(json_data)))
    f.write(struct.pack('<I', 0x4E4F534A))
    f.write(json_data)

    f.write(struct.pack('<I', len(orig_buffer)))
    f.write(struct.pack('<I', 0x004E4942))
    f.write(orig_buffer)

import os
print(f"\n✅ 完成！")
print(f"   大小: {os.path.getsize(output_path) / 1024 / 1024:.1f} MB")
print(f"   路徑: {output_path}")
