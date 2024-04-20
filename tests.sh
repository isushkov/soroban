#!/bin/bash

set -uo pipefail

announce_block() {
    local msg=("${@:1}")
    echo
    echo "=== $msg ========================="
}
expect() {
    local expected_exit_code=$1
    local cmd=("${@:2}")
    echo ">>>"
    echo ">>> Running command: ${cmd[*]}"
    echo ">>>"
    "${cmd[@]}"
    local exit_code=$?
    if [ $exit_code -eq $expected_exit_code ]; then
        echo "... passed with code $exit_code"
        echo
    else
        echo "<<< Command failed with unexpected exit code $exit_code"
        exit 1
    fi
}

announce_block "create arithmetic"
announce_block "create arithmetic - ok"
expect 0 ./main.py create arithmetic 0 1 100
expect 0 ./main.py create arithmetic 0 1 100 --path=./data/custom.txt
expect 0 ./main.py create arithmetic 0 1 --path=./data/custom.txt 100
# почему это работает?
expect 0 ./main.py create arithmetic 100 -1.2 100
expect 0 ./main.py create arithmetic 100 -1.2 100 --path=./data/custom1.txt
expect 0 ./main.py create arithmetic 100 -1.2 --path=./data/custom2.txt 100
expect 0 ./main.py create arithmetic 100 --path=./data/custom3.txt -1.2 100
expect 0 ./main.py create arithmetic --path=./data/custom4.txt 100 -1.2 100
announce_block "create arithmetic - err"
expect 2 ./main.py create arithmetic 0
expect 2 ./main.py create arithmetic 0 1
expect 2 ./main.py create arithmetic 0 1 --path=./data/custom.txt
expect 2 ./main.py create arithmetic --path=./data/custom.txt

announce_block "create random params - required"
announce_block "create random params - required - start-number ok"
expect 0 ./main.py create random "s0,+,1-99,10"
expect 0 ./main.py create random "sr,+,1-99,10"
expect 0 ./main.py create random "s3.2,+,1-99,10:.1"
expect 0 ./main.py create random "s-3,+,1-99,10"
announce_block "create random params - required - start-number err"
expect 1 ./main.py create random "+,1-99,10"
expect 1 ./main.py create random ",+,1-99,10"
expect 1 ./main.py create random "asdf,+,1-99,10"
expect 1 ./main.py create random "x1,+,1-99,10"
expect 1 ./main.py create random "y-2,+,1-99,10"
expect 1 ./main.py create random "1,+,1-99,10"
# отрицательный start-number без "s" воспринимается как опциональный параметр
expect 2 ./main.py create random "-1,+,1-99,10"
# не уточняется с какой точностью после запятой генерировать числа
expect 1 ./main.py create random "s3.2,+,1-99,10"

announce_block "create random params - required - operands ok"
expect 0 ./main.py create random "s0,+,1-99,10"
expect 0 ./main.py create random "s0,+-,1-99,10"
expect 0 ./main.py create random "s0,-+,1-99,10"
expect 0 ./main.py create random "s0,+2,1-99,10"
expect 0 ./main.py create random "s0,+2-1,1-99,10"
announce_block "create random params - required - operands err"
expect 1 ./main.py create random "s0,1-99,10"
expect 1 ./main.py create random "s0,,1-99,10"
expect 1 ./main.py create random "s0,^,1-99,10"
expect 1 ./main.py create random "s0,asdf,1-99,10"
expect 1 ./main.py create random "s0,+a-b,1-99,10"
# невозможно создать потомучто отрицальтельные числа не разрешены
expect 1 ./main.py create random "s0,-,1-99,10"
announce_block "create random params - required - range ok"
expect 0 ./main.py create random "s0,+,1-99,10"
expect 0 ./main.py create random "s0,+,0-99,10"
expect 0 ./main.py create random "s0,+,20-10,10"
announce_block "create random params - required - range err"
expect 1 ./main.py create random "s0,+,-99-99,10"
expect 1 ./main.py create random "s0,+,adsf,10"
expect 1 ./main.py create random "s0,+,1a-99df,10"
expect 1 ./main.py create random "s0,+,1-99asdf,10"
announce_block "create random params - required - length ok"
expect 0 ./main.py create random "s0,+,1-99,10"
announce_block "create random params - required - length err"
expect 1 ./main.py create random "s0,+,1-99"
expect 1 ./main.py create random "s0,+,1-99,"
expect 1 ./main.py create random "s0,+,1-99,0"
expect 1 ./main.py create random "s0,+,1-99,10.2"
expect 1 ./main.py create random "s0,+,1-99,-10"
expect 1 ./main.py create random "s0,+,1-99,asdf"

announce_block "create random params - optional"
announce_block "create random params - optional - ok"
expect 0 ./main.py create random "s0,+,1-99,10"
expect 0 ./main.py create random "s0,+,1-99,10:"
expect 0 ./main.py create random "s0,+,1-99,10:<"
expect 0 ./main.py create random "s0,+,1-99,10:n"
expect 0 ./main.py create random "s0,+,1-99,10:.2"
expect 0 ./main.py create random "s0,+,1-99,10:.2%50"
expect 0 ./main.py create random "s0,+,1-99,10:<n.2%50"
expect 0 ./main.py create random "s0,+,1-99,10:n.2%50<"
# its fine
expect 0 ./main.py create random "s0,+,1-99,10:,"
expect 0 ./main.py create random "s0,+,1-99,10:x"
expect 0 ./main.py create random "s0,+,1-99,10:-1"
expect 0 ./main.py create random "s0,+,1-99,10:asdf"
expect 0 ./main.py create random "s0,+,1-99,10:asdf<n.2"
announce_block "create random params - optional - err"
expect 1 ./main.py create random "s0,+,1-99,10<"
expect 1 ./main.py create random "s0,+,1-99,10n"
expect 1 ./main.py create random "s0,+,1-99,10.2"
expect 1 ./main.py create random "s0,+,1-99,10.2%50"
expect 1 ./main.py create random "s0,+,1-99,10<n.2%50"
expect 1 ./main.py create random "s0,+,1-99,10n.2%50<"

announce_block "create random params - sequences"
announce_block "create random params - sequences - ok"
expect 0 ./main.py create random "s0,+,1-99,20 -,1-99,10"
expect 0 ./main.py create random "s0,+,1-99,20:n -,1-99,10:n<"
expect 0 ./main.py create random "s0,+,1-99,20    -,1-99,10"
expect 0 ./main.py create random "s0,+,1-99,20
                                        -,1-99,10"
announce_block "create random params - sequences - err"
expect 1 ./main.py create random "s0,+,1-99,20 99,-,1-99,10"
expect 1 ./main.py create random "s0,+,1-99,20 ,-,1-99,10"
expect 1 ./main.py create random "s0,+,1-99,20; -,1-99,10"
expect 1 ./main.py create random "s0,+,1-99,20 adsf 99,-,1-99,10"

announce_block "TODO"
# TODO: analyze "*" and "/"
expect 1 ./main.py create random "s0,+-*/,1-99,10"
expect 1 ./main.py create random "s0,+3-2*/1,1-99,10"
