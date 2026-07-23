#!/usr/bin/env bash

default_usb_volume="/Volumes/ADATA SC740"

usb_volume() {
  printf "%s" "${USB_VOLUME:-$default_usb_volume}"
}

repo_root() {
  local script_dir
  script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
  cd -- "$script_dir/.." && pwd
}

fail() {
  echo "Error: $*" >&2
  exit 1
}

require_usb() {
  local volume
  volume="$(usb_volume)"
  [[ -d "$volume" ]] || fail "No encuentro la USB: $volume. Conectala o usa USB_VOLUME='/Volumes/NOMBRE USB'."
}

bytes_available() {
  local path="$1"
  df -k "$path" | awk 'NR == 2 {print $4 * 1024}'
}

now_iso() {
  date -u +"%Y-%m-%dT%H:%M:%SZ"
}

path_size_bytes() {
  local path="$1"
  if [[ -f "$path" ]]; then
    stat -f %z "$path"
  else
    du -sk "$path" | awk '{print $1 * 1024}'
  fi
}

human_size() {
  local bytes="$1"
  awk -v bytes="$bytes" 'BEGIN {
    split("B KB MB GB TB", units, " ")
    size = bytes
    unit = 1
    while (size >= 1024 && unit < 5) {
      size = size / 1024
      unit++
    }
    printf "%.1f%s", size, units[unit]
  }'
}

dir_size_bytes() {
  local path="$1"
  if [[ -e "$path" ]]; then
    du -sk "$path" 2>/dev/null | awk '{print $1 * 1024}'
  else
    printf "0"
  fi
}

file_count() {
  local path="$1"
  if [[ -d "$path" ]]; then
    find "$path" -type f 2>/dev/null | wc -l | tr -d ' '
  else
    printf "0"
  fi
}

metadata_count() {
  local path="$1"
  if [[ -d "$path" ]]; then
    find "$path" \( -name '._*' -o -name '.DS_Store' \) -type f 2>/dev/null | wc -l | tr -d ' '
  else
    printf "0"
  fi
}

chrome_profile_in_use() {
  local profile_dir="$1"
  ps -axo comm=,args= | awk -v profile="--user-data-dir=$profile_dir" 'index($0, "Google Chrome") > 0 && index($0, profile) > 0 {found=1} END {exit found ? 0 : 1}'
}

ensure_space_for() {
  local source_path="$1"
  local destination_root="$2"
  local required available margin
  required="$(path_size_bytes "$source_path")"
  margin=$((250 * 1024 * 1024))
  available="$(bytes_available "$destination_root")"

  if (( available < required + margin )); then
    fail "No hay espacio suficiente en la USB. Necesitas $(human_size "$((required + margin))") y hay $(human_size "$available")."
  fi
}

safe_destination() {
  local destination_root="$1"
  local source_path="$2"
  local base_name destination suffix extension name

  base_name="$(basename "$source_path")"
  destination="$destination_root/$base_name"

  if [[ ! -e "$destination" ]]; then
    printf "%s" "$destination"
    return
  fi

  suffix="$(date +%Y%m%d-%H%M%S)"
  if [[ -f "$source_path" && "$base_name" == *.* ]]; then
    extension=".${base_name##*.}"
    name="${base_name%.*}"
    printf "%s" "$destination_root/$name-$suffix$extension"
  else
    printf "%s" "$destination_root/$base_name-$suffix"
  fi
}

verify_copy() {
  local source_path="$1"
  local destination="$2"

  if [[ -f "$source_path" ]]; then
    [[ -f "$destination" ]] || return 1
    cmp -s "$source_path" "$destination"
    return
  fi

  [[ -d "$source_path" && -d "$destination" ]] || return 1

  local source_files destination_files source_size destination_size
  source_files="$(find "$source_path" -type f | wc -l | tr -d ' ')"
  destination_files="$(find "$destination" -type f | wc -l | tr -d ' ')"
  source_size="$(du -sk "$source_path" | awk '{print $1}')"
  destination_size="$(du -sk "$destination" | awk '{print $1}')"

  [[ "$source_files" == "$destination_files" && "$source_size" == "$destination_size" ]]
}
