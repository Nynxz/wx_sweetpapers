#!/bin/bash

BASE_DIR="$HOME/Wallpapers/packs/"

process_name="swww-daemon"
process_info=$(ps -eo pid,rss,comm | grep "$process_name" | grep -v "grep" | awk '{printf "%.2fMB %s\n", $2/1024, $3}')

directories=$(find "$BASE_DIR" -mindepth 1 -maxdepth 1 \( -type d -o -type l \))

commands="$directories"

if [ -n "$process_info" ]; then
  commands="$directories\n$process_info\nKill swww-daemon"
else
  commands="$commands\nStart swww-daemon"
fi

selected_option=$(echo -e "$commands" | wofi --show dmenu --insensitive true --prompt "Select a Wallpaper Pack")

if [[ "$selected_option" == "$process_info" ]] && [ -n "$process_info" ]; then
  pgrep "swww-daemon" | xargs kill
  # Get Updated Memory Usage
  hyprctl dispatch exec swww-daemon
  new_process_info=$(ps -eo pid,rss,comm | grep "$process_name" | grep -v "grep" | awk '{printf "%.2fMB %s\n", $2/1024, $3}')
  notify-send "♻️ Restarting swww-daemon" "Before $process_info\nAfter $new_process_info"
elif [[ "$selected_option" == "Kill swww-daemon" ]]; then
  notify-send "🔴 Killing swww-daemon"
  pkill 'swww-daemon'
elif [[ "$selected_option" == "Start swww-daemon" ]]; then
  notify-send "🟢 Starting swww-daemon"
  hyprctl dispatch exec swww-daemon
elif [ -d "$selected_option" ]; then
  selected_option=$(basename "$selected_option")
  if [ -z "$process_info" ]; then
    process_info="Starting..."
    hyprctl dispatch exec swww-daemon
  fi
  /home/user/.config/wx_sweetpapers/src/sweetpapers.py -c /home/user/.config/wx_sweetpapers/sweetpapers.jsonc -p "$selected_option" &
  notify-send "🟢 $selected_option" "$process_info"
else
  notify-send "❔No directory selected."
fi
