#!/bin/bash
# 批次生成所有角色的 sprite sheets

CHARACTERS="ryo koto yoi"
ACTIONS="walk_right walk_left working waiting"

for char in $CHARACTERS; do
  echo "========================================="
  echo "生成角色: $char"
  echo "========================================="
  for action in $ACTIONS; do
    echo "--- $char - $action ---"
    python3 generate_sprites.py --character $char --action $action --frames 8
  done
done

echo "========================================="
echo "所有角色生成完成！"
echo "========================================="
