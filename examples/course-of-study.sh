#!/bin/bash
# check yq
if ! command -v yq &> /dev/null; then
    echo 'Please install "yq". like:'
    echo '   sudo apt install yq -y'
    exit 1
fi
step=$(yq e '.common.course_of_study_step' config.yaml)
declare -A commands=(
    [1]="run-new training cover-units plus x-x 4"
    [2]="run-new exam cover-units plus x-x 4"
    [3]="run-new training cover-units plus xx-xx 4"
    [4]="run-new exam cover-units plus xx-xx 4"
    [5]="run-new training cover-units minis xx-xx 4"
    [6]="run-new exam cover-units minis xx-xx 4"
    [7]="run-new training cover-units plus-minis xx-xx 4"
    [8]="run-new exam cover-units plus-minis xx-xx 4"
    [9]="run-new cover-units plus-minus-loop xx-xx 8"
    [10]="run-new exam plus-minus-loop xx-xx 8"
)
if [ -n "${commands[$step]}" ]; then
    read -r cmd time <<< "${commands[$step]}"
    echo ">>> Expected execution time to successfully complete this step:"
    echo ">>>    $time minutes"
    ./main.py $cmd
else
    echo "Неизвестное значение: $step"
    exit 1
fi
