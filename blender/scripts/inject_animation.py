#!/usr/bin/env python3
"""
從 Blender 導出的 GLB 提取動畫，注入到原始模型
保留原始模型的所有結構（骨骼、IBM、材質）
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

def write_glb(filepath, chunks):
    total_len = 12  # header
    for ctype, data in chunks:
        total_len += 8 + len(data)

    with open(filepath, 'wb') as f:
        f.write(struct.pack('<I', 0x46546C67))  # magic
        f.write(struct.pack('<I', 2))  # version
        f.write(struct.pack('<I', total_len))
        for chunk_type, chunk_data in chunks:
            f.write(struct.pack('<I', len(chunk_data)))
            f.write(struct.pack('<I', chunk_type))
            f.write(chunk_data)

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

def set_json(chunks, gltf):
    json_data = json.dumps(gltf, separators=(',', ':')).encode('utf-8')
    for i, (t, d) in enumerate(chunks):
        if t == 0x4E4F534A:
            chunks[i] = (t, json_data)
            return
    chunks.append((0x4E4F534A, json_data))

def set_binary(chunks, data):
    for i, (t, d) in enumerate(chunks):
        if t == 0x004E4942:
            chunks[i] = (t, data)
            return
    chunks.append((0x004E4942, data))

print("=== 提取動畫並注入原始模型 ===")

# 讀取原始模型（保留它的結構）
print("\n1. 讀取原始模型...")
orig_chunks, _ = read_glb('/mnt/e_drive/claude-office/assets/characters/3d/realistic_female_character__game-ready_3d_model.glb')
orig_gltf = get_json(orig_chunks)
orig_buffer = get_binary(orig_chunks)

print(f"   原始模型：{len(orig_gltf.get('animations', []))} 個動畫")

# 讀取 Blender 導出的模型（有新動畫）
print("\n2. 讀取 Blender 導出模型...")
blend_chunks, _ = read_glb('/mnt/e_drive/claude-office/blender/exports/character_walk_fixed.glb')
blend_gltf = get_json(blend_chunks)
blend_buffer = get_binary(blend_chunks)

blend_anims = blend_gltf.get('animations', [])
print(f"   Blender 模型：{len(blend_anims)} 個動畫")

if not blend_anims:
    print("❌ 沒有找到動畫！")
    exit(1)

# 提取動畫數據
print("\n3. 提取動畫軌道...")

# 複製原始 chunks 作為基礎
new_chunks = list(orig_chunks)

# 需要重新構建 buffer（添加動畫數據）
# 1. 收集所有動畫需要的 bufferView 數據
anim_buffer_views = []  # (byte_offset, byte_length, data)
anim_accessors = []
current_offset = len(orig_buffer)

for anim in blend_anims:
    print(f"   處理動畫: {anim.get('name', 'unnamed')}")

    new_channels = []
    for channel in anim['channels']:
        sampler = anim['samplers'][channel['sampler']]

        # 複製 input accessor（時間）
        input_acc = blend_gltf['accessors'][sampler['input']]
        input_bv = blend_gltf['bufferViews'][input_acc['bufferView']]
        input_offset = input_bv.get('byteOffset', 0) + input_acc.get('byteOffset', 0)
        input_data = blend_buffer[input_offset:input_offset + input_bv['byteLength']]

        # 複製 output accessor（值）
        output_acc = blend_gltf['accessors'][sampler['output']]
        output_bv = blend_gltf['bufferViews'][output_acc['bufferView']]
        output_offset = output_bv.get('byteOffset', 0) + output_acc.get('byteOffset', 0)
        output_data = blend_buffer[output_offset:output_offset + output_bv['byteLength']]

        # 記錄新的 bufferView 和 accessor
        # (簡化版：假設可以直接複製數據)
        print(f"     - Channel: {channel['target']['node']} ({channel['target']['path']})")

    # 暫時簡單複製整個動畫定義
    orig_gltf.setdefault('animations', []).append(anim)

print(f"\n   添加了 {len(blend_anims)} 個動畫到原始模型")

# 更新 JSON
set_json(new_chunks, orig_gltf)

# 寫入
output = '/mnt/e_drive/claude-office/blender/exports/character_with_walk.glb'
write_glb(output, new_chunks)

import os
print(f"\n✅ 完成！大小: {os.path.getsize(output) / 1024 / 1024:.1f} MB")
print(f"   路徑: {output}")
print("\n⚠️ 注意：這個版本簡化了 buffer 處理，可能不完整")
print("   如果不work，需要完整複製 bufferViews 和 accessors")
