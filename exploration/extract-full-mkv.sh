#!/usr/bin/env zsh

if [ -z "$1" ]; then
    echo "Usage: $0 <mkv-file>"
    exit 1
fi
parts=$(mkvmerge --identify "$1")
