#!/bin/bash

# 下載 Poly Haven 免費 PBR 貼圖

TEXTURE_DIR="/mnt/e_drive/claude-office/public/textures"

mkdir -p $TEXTURE_DIR/{wood,fabric,metal,hdr}

echo "下載 PBR 貼圖..."

# 木地板貼圖（Poly Haven）
wget -q -O $TEXTURE_DIR/wood/wood_diffuse.jpg \
  "https://cdn.polyhaven.com/asset_img/thumbs/wooden_floor_boards.png?height=1024&width=1024" || echo "木地板貼圖下載失敗"

# 金屬貼圖
wget -q -O $TEXTURE_DIR/metal/metal_diffuse.jpg \
  "https://cdn.polyhaven.com/asset_img/thumbs/metal_tiles.png?height=512&width=512" || echo "金屬貼圖下載失敗"

# 布料貼圖
wget -q -O $TEXTURE_DIR/fabric/fabric_diffuse.jpg \
  "https://cdn.polyhaven.com/asset_img/thumbs/fabric_pattern.png?height=512&width=512" || echo "布料貼圖下載失敗"

echo "PBR 貼圖下載完成！"
