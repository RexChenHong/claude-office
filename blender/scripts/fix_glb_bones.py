#!/usr/bin/env python3
"""
修復 Blender 導出時破壞的骨骼 translation
從原始模型讀取正確的骨骼位置，寫入到目標模型
"""
import struct
import json
import copy

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
        if ctype == 0x4E4F534A:  # JSON
            return json.loads(data.decode('utf-8'))
    return None

def set_json_chunk(chunks, gltf):
    for i, (ctype, data) in enumerate(chunks):
        if ctype == 0x4E4F534A:
            chunks[i] = (ctype, json.dumps(gltf, separators=(',', ':')).encode('utf-8'))
            return
    chunks.append((0x4E4F534A, json.dumps(gltf, separators=(',', ':')).encode('utf-8')))

# 讀取原始模型的骨骼 translation
print("讀取原始模型...")
orig_chunks, orig_length = read_glb('/mnt/e_drive/claude-office/assets/characters/3d/realistic_female_character__game-ready_3d_model.glb')
orig_gltf = get_json_chunk(orig_chunks)

# 建立骨骼名稱到 translation 的映射
bone_translations = {}
for node in orig_gltf.get('nodes', []):
    name = node.get('name', '')
    if 'translation' in node:
        bone_translations[name] = node['translation']

print(f"找到 {len(bone_translations)} 個骨骼的 translation")

# 讀取目標模型
print("讀取目標模型...")
target_chunks, target_length = read_glb('/mnt/e_drive/claude-office/blender/exports/character_walk_fixed.glb')
target_gltf = get_json_chunk(target_chunks)

# 修復骨骼 translation
fixed_count = 0
for node in target_gltf.get('nodes', []):
    name = node.get('name', '')
    if name in bone_translations:
        orig_t = bone_translations[name]
        curr_t = node.get('translation', [0,0,0])

        # 檢查是否需要修復（如果不一樣）
        if curr_t != orig_t:
            node['translation'] = orig_t
            fixed_count += 1
            if fixed_count <= 10:
                print(f"  修復 {name}: {curr_t[:3]} -> {orig_t[:3]}")

print(f"\n修復了 {fixed_count} 個骨骼的 translation")

# 重新計算 JSON chunk 大小
set_json_chunk(target_chunks, target_gltf)

# 重新計算總長度
new_length = 12  # header
for ctype, data in target_chunks:
    new_length += 8 + len(data)

# 寫入修復後的文件
output = '/mnt/e_drive/claude-office/blender/exports/character_walk_fixed_v2.glb'
write_glb(output, target_chunks, new_length)

import os
size = os.path.getsize(output) / 1024 / 1024
print(f"\n✅ 導出成功！大小: {size:.1f} MB")
print(f"路徑: {output}")
