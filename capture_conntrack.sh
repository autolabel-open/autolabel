#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <output_file_path> <pid>"
    exit 1
fi

output_file=$1
pid=$2

if ! ps -p "$pid" > /dev/null 2>&1; then
    echo "Error: process with pid $pid does not exist."
    exit 1
fi

sudo nsenter -t "$pid" -n sh -c "conntrack -E -o timestamp > \"$output_file\""
