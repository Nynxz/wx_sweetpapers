#!/bin/bash

BASE_DIR="$HOME/Wallpapers/packs/"

process_name="swww-daemon"
process_info=$(ps -eo pid,rss,comm | grep "$process_name" | grep -v "grep" | awk '{printf "%.2fMB %s\n", $2/1024, $3}')

directories=$(find "$BASE_DIR" -mindepth 1 -maxdepth 1 -type d)
selected_dir=$(echo -e "$directories\n$process_info" | wofi --show dmenu --insensitive true --prompt "Select a Wallpaper Pack")

if [[ "$selected_dir" == "$process_info" ]]; then
  process_info=$(ps -eo pid,rss,comm | grep "$process_name" | grep -v "grep" | awk '{printf "%.2fMB %s\n",$2/1024, $3}')
  # Kill Running swww-daemon
  notify-send "Before: $process_info"
  #echo "$process_info" | awk '{print $1}' | xargs -r kill

  pgrep "swww-daemon" | xargs kill
  # Dispatch new swww-daemon
  hyprctl dispatch exec swww-daemon

  # Get Updated Memory Usage
  process_info=$(ps -eo pid,rss,comm | grep "$process_name" | grep -v "grep" | awk '{printf "%.2fMB %s\n", $2/1024, $3}')
  notify-send "-a" "yes" "After: $process_info"
elif [ -d "$selected_dir" ]; then
  selected_dir=$(basename "$selected_dir")
  echo "You Selected: $selected_dir"
  /home/user/.config/wx_sweetpapers/src/sweetpapers.py -c /home/user/.config/wx_sweetpapers/sweetpapers.jsonc -p "$selected_dir" &
  notify-send "$selected_dir" "$process_info"
else
  notify-send "❔No directory selected."
fi
