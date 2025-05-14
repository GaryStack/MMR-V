#!/bin/bash

SOURCE_DIR="/current_path"
DESTINATION_DIR="/mnt/userdata/projects/HalluInducing"
EXCLUDE_DIRS=("results" "dataset/Fever" "dataset/INVITE" "dataset/FEVER" "dataset/CREPE" "zhuoran/result")

inotifywait -m -r -e modify,create,delete,move "$SOURCE_DIR" |
while read -r directory events filename; do
    exclude=false
    for exclude_dir in "${EXCLUDE_DIRS[@]}"; do
        if [[ "$directory" == "$SOURCE_DIR$exclude_dir"* ]]; then
            exclude=true
            break
        fi
    done

    if [ "$exclude" = false ]; then
        # shellcheck disable=SC2145
        rsync -av --exclude="${EXCLUDE_DIRS[@]}" "$SOURCE_DIR" "$DESTINATION_DIR"
    fi
done
