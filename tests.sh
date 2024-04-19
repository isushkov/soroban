#!/bin/bash

set -euo pipefail

expect() {
    local expected_exit_code=$1
    local cmd=("${@:2}")
    echo ">>> Running command: ${cmd[*]}"
    "${cmd[@]}"
    local exit_code=$?
    if [ $exit_code -eq $expected_exit_code ]; then
        echo ">>> Command exited as expected with code $exit_code"
    else
        echo "<<< Command failed with unexpected exit code $exit_code"
        exit 1
    fi
}

expect 0 ./main.py create arithmetic 0 1 100
expect 0 ./main.py create arithmetic 0 1 100 ./data/custom_arithm.txt
expect 0 ./main.py create arithmetic 100 -1.2 100
expect 1 ./main.py create arithmetic 0
expect 1 ./main.py create arithmetic 0 1
expect 1 ./main.py create arithmetic 0 1 ./data/custom_arithm.txt
expect 1 ./main.py create arithmetic 0 1 ./data/custom_arithm.txt 100

# ./main.py create random plus x-x 5
# ./main.py create random minus x-x 5
# ./main.py create random plus-minus-roundtrip x-x 5
# ./main.py create random plus-minus x-x 5
# ./main.py create cover-units plus x-x
# ./main.py create cover-units minus x-x
# ./main.py create cover-units plus-minus-roundtrip x-x
# # TODO: ./main.py create cover-units plus-minus x-x
# ./main.py run-new arithmetic 0 100
# ./main.py run-new random plus x-x 5
# ./main.py run-new random minus x-x 5
# # TODO: ./main.py run-new random plus-minus-roundtrip x-x 5
# # TODO: ./main.py run-new random plus-minus x-x 5
# ./main.py run-new cover-units plus x-x
# ./main.py run-new cover-units minus x-x
# # TODO: ./main.py run-new cover-units plus-minus-roundtrip x-x
# # TODO: ./main.py run-new cover-units plus-minus x-x
#
# # TODO: ./main.py run-new training arithmetic 0 100
# # TODO: ./main.py run-new training random plus x-x
# # TODO: ./main.py run-new training random minus x-x
# # TODO: ./main.py run-new training random plus-minus-roundtrip x-x
# # TODO: ./main.py run-new training random plus-minus x-x
# # TODO: ./main.py run-new training cover-units plus x-x
# # TODO: ./main.py run-new training cover-units minus x-x
# # TODO: ./main.py run-new training cover-units plus-minus-roundtrip x-x
# # TODO: ./main.py run-new training cover-units plus-minus x-x
# # TODO: ./main.py run-new exam arithmetic 0 100
# # TODO: ./main.py run-new exam random plus x-x
# # TODO: ./main.py run-new exam random minus x-x
# # TODO: ./main.py run-new exam random plus-minus-roundtrip x-x
# # TODO: ./main.py run-new exam random plus-minus x-x
# # TODO: ./main.py run-new exam cover-units plus x-x
# # TODO: ./main.py run-new exam cover-units minus x-x
# # TODO: ./main.py run-new exam cover-units plus-minus-roundtrip x-x
# # TODO: ./main.py run-new exam cover-units plus-minus x-x
# # TODO: ./main.py study
