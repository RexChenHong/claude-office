#!/usr/bin/env python3
"""
完整修復 Blender 導出的骨骼問題：
1. Node translation（骨骼位置）
2. Node rotation（骨骼旋轉）
3. InverseBindMatrix（蒙皮矩陣）
"""
import struct
import json

def read_glb(filepath):
    with open(filepath, 'rb') as f:
        magic = struct.unpack('<I', f.read(4))[0]
        version = struct.unpack('<I', f.read(4))[0]
        length = struct.unpack('<I', f.read(4))[0]

        chunks = []
        while f.tell() < length:
            chunk_len = struct.unpack('<I', f.read(4))[0]
            chunk_type = struct.unpack('<I', f.read(4))[0]
            chunk_data = f.read(chunk_len)
            chunks.append((chunk_type, chunk_data))
        return chunks, length

def write_glb(filepath, chunks, length):
    with open(filepath, 'wb') as f:
        f.write(struct.pack('<I', 0x46546C67))  # magic
        f.write(struct.pack('<I', 2))  # version
        f.write(struct.pack('<I', length))
        for chunk_type, chunk_data in chunks:
            f.write(struct.pack('<I', len(chunk_data)))
            f.write(struct.pack('<I', chunk_type))
            f.write(chunk_data)

def get_json_chunk(chunks):
    for ctype, data in chunks:
        if ctype == 0x4E4F534A:
            return json.loads(data.decode('utf-8'))
    return None

def get_binary_chunk(chunks):
    for ctype, data in chunks:
        if ctype == 0x004E4942:
            return data
    return None

def set_binary_chunk(chunks, new_data):
    for i, (ctype, data) in enumerate(chunks):
        if ctype == 0x004E4942:
            chunks[i] = (ctype, new_data)
            return
    chunks.append((0x004E4942, new_data))

def set_json_chunk(chunks, gltf):
    for i, (ctype, data) in enumerate(chunks):
        if ctype == 0x4E4F534A:
            chunks[i] = (ctype, json.dumps(gltf, separators=(',', ':')).encode('utf-8'))
            return
    chunks.append((0x4E4F534A, json.dumps(gltf, separators=(',', ':')).encode('utf-8')))

# 讀取原始模型
print("讀取原始模型...")
orig_chunks, orig_length = read_glb('/mnt/e_drive/claude-office/assets/characters/3d/realistic_female_character__game-ready_3d_model.glb')
orig_gltf = get_json_chunk(orig_chunks)
orig_buffer = get_binary_chunk(orig_chunks)

# 從原始模型建立骨骼名稱 → 變換映射
bone_data = {}
for node in orig_gltf.get('nodes', []):
    name = node.get('name', '')
    if name:
        bone_data[name] = {
            'translation': node.get('translation'),
            'rotation': node.get('rotation'),
            'scale': node.get('scale')
        }

# 讀取原始 IBM
orig_skin = orig_gltf['skins'][0]
orig_joints = orig_skin['joints']
orig_ibm_accessor_idx = orig_skin['inverseBindMatrices']
orig_ibm_accessor = orig_gltf['accessors'][orig_ibm_accessor_idx]
orig_buffer_view = orig_gltf['bufferViews'][orig_ibm_accessor['bufferView']]
orig_ibm_offset = orig_buffer_view.get('byteOffset', 0) + orig_ibm_accessor.get('byteOffset', 0)
orig_ibm_count = orig_ibm_accessor['count']
orig_ibm_data = orig_buffer[orig_ibm_offset:orig_ibm_offset + orig_ibm_count * 64]

print(f"找到 {len(bone_data)} 個骨骼數據")
print(f"原始 IBM: {orig_ibm_count} 個矩陣, {len(orig_ibm_data)} bytes")

# 讀取目標模型
print("\n讀取目標模型...")
target_chunks, target_length = read_glb('/mnt/e_drive/claude-office/blender/exports/character_walk_fixed.glb')
target_gltf = get_json_chunk(target_chunks)
target_buffer = get_binary_chunk(target_chunks)

# 修復骨骼 translation 和 rotation
fixed_t = 0
fixed_r = 0
for node in target_gltf.get('nodes', []):
    name = node.get('name', '')
    if name in bone_data:
        orig = bone_data[name]
        
        # 修復 translation
        if orig['translation'] is not None:
            curr_t = node.get('translation')
            if curr_t != orig['translation']:
                node['translation'] = orig['translation']
                fixed_t += 1
        
        # 修復 rotation
        if orig['rotation'] is not None:
            curr_r = node.get('rotation')
            if curr_r != orig['rotation']:
                node['rotation'] = orig['rotation']
                fixed_r += 1

print(f"修復了 {fixed_t} 個 translation, {fixed_r} 個 rotation")

# 修復 inverseBindMatrix
target_skin = target_gltf['skins'][0]
target_ibm_accessor_idx = target_skin['inverseBindMatrices']
target_ibm_accessor = target_gltf['accessors'][target_ibm_accessor_idx]
target_buffer_view = target_gltf['bufferViews'][target_ibm_accessor['bufferView']]
target_ibm_offset = target_buffer_view.get('byteOffset', 0) + target_ibm_accessor.get('byteOffset', 0)
target_ibm_count = target_ibm_accessor['count']

# 創建新的 buffer
new_buffer = bytearray(target_buffer)

# 用原始 IBM 替換
if orig_ibm_count == target_ibm_count:
    new_buffer[target_ibm_offset:target_ibm_offset + orig_ibm_count * 64] = orig_ibm_data
    print(f"替換了 {target_ibm_count} 個 inverseBindMatrix")
else:
    print(f"警告: IBM 數量不匹配! 原={orig_ibm_count}, 目標={target_ibm_count}")

# 更新 buffer 和 JSON
set_binary_chunk(target_chunks, bytes(new_buffer))
set_json_chunk(target_chunks, target_gltf)

# 重新計算總長度
new_length = 12
for ctype, data in target_chunks:
    new_length += 8 + len(data)

# 寫入
output = '/mnt/e_drive/claude-office/blender/exports/character_walk_fixed_v4.glb'
write_glb(output, target_chunks, new_length)

import os
size = os.path.getsize(output) / 1024 / 1024
print(f"\n✅ 導出成功！大小: {size:.1f} MB")
print(f"路徑: {output}")
