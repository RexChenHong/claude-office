#!/bin/bash
# Claude Office 服務守護腳本

LOG="/mnt/e_drive/claude-office/logs/daemon.log"
MONITOR_PORT=8053
UI_PORT=8054

echo "$(date '+%Y-%m-%d %H:%M:%S') 檢查服務狀態..." >> "$LOG"

# 檢查 Monitor
if ! lsof -i :$MONITOR_PORT | grep -q LISTEN; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') Monitor 掛了，重啟..." >> "$LOG"
    cd /mnt/e_drive/claude-office/src/session-monitor
    nohup npm start > /mnt/e_drive/claude-office/logs/monitor.log 2>&1 &
    sleep 2
fi

# 檢查 UI
if ! lsof -i :$UI_PORT | grep -q LISTEN; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') UI 掛了，重啟..." >> "$LOG"
    cd /mnt/e_drive/claude-office/src/ui
    nohup npm run dev -- --host 0.0.0.0 --port 8051 > /mnt/e_drive/claude-office/logs/ui.log 2>&1 &
    sleep 2
fi
