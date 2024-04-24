#!/bin/bash

set -uo pipefail

show_data() {
    for file in ./data/*.txt; do
        if [ -f "$file" ]; then
            echo "$(basename "$file"):"
            cat "$file"
            echo
            echo
        fi
    done
}
announce_block() {
    local msg=("${@:1}")
    echo ">>> === $msg ========================="
}
expect() {
    local expected_exit_code=$1
    local cmd=("${@:2}")
    echo ">>> Running command: '${cmd[*]}'"
    echo ">>>"
    "${cmd[@]}"
    local exit_code=$?
    if [ $exit_code -eq $expected_exit_code ]; then
        echo "<<<"
        echo "<<< passed with code $exit_code"
    else
        echo "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
        echo "^^^ Command failed with unexpected exit code $exit_code ^^^"
        exit 1
    fi
}
run() {
    # # announce_block "specific"
    # progression
    expect 0 ./main.py create "s0   p+1,10"
    expect 0 ./main.py create "s0   p-1,10"
    expect 0 ./main.py create "s100 p+1,10"
    expect 0 ./main.py create "s100 p-1,10"
    expect 0 ./main.py create "s1   p*2,6"
    expect 0 ./main.py create "s100 p/2,6"
    expect 2 ./main.py create "s1   p*-2,6"
    expect 2 ./main.py create "s100 p/-2,6"
    expect 0 ./main.py create "s0   p+1.2,10"
    expect 0 ./main.py create "s0   p-1.2,10"
    expect 0 ./main.py create "s100 p+1.2,10"
    expect 0 ./main.py create "s100 p-1.2,10"
    expect 0 ./main.py create "s1   p*2.2,6"
    expect 0 ./main.py create "s100 p/2.2,6"
    expect 2 ./main.py create "s1   p*-2.2,6"
    expect 2 ./main.py create "s100 p/-2.2,6"
    # random
    expect 0 ./main.py create "s0 r+,1-9,10"
    expect 0 ./main.py create "s0 r-,1-9,10:n"
    expect 0 ./main.py create "s0 r+-,1-9,10:n"
    expect 2 ./main.py create "s0 r+-*/,1-9,10:n"
    # cover
    expect 0 ./main.py create "s0 c+,1-9"
    expect 1 ./main.py create "s0 c-,1-9"
    # expect 0,1 ./main.py create "s0 c+-,1-9"
    expect 2 ./main.py create "s0 c+-*/,1-9"
    expect 0 ./main.py create "s0 c-,1-9:n"
    expect 0 ./main.py create "s0 c+-,1-9:n"
    expect 2 ./main.py create "s0 c+-*/,1-9:n"

    announce_block "all"
    announce_block "create: ok"
    expect 0 ./main.py create "s0 p+1,10"
    expect 0 ./main.py create "s0 p+1,10" --path=./data/custom.txt
    expect 0 ./main.py create --path=./data/custom.txt "s0 p+1,10"
    announce_block "create: err"
    expect 2 ./main.py create
    expect 2 ./main.py create other
    expect 2 ./main.py create "s0 p+1,10" other
    expect 2 ./main.py create other "s0 p+1,10"
    expect 2 ./main.py create "s0 p+1,10" --other="hi"
    expect 2 ./main.py create other --other="hi"
    expect 2 ./main.py create "s0 p+1,10" other --other="hi"
    expect 2 ./main.py create other "s0 p+1,10" --other="hi"

    announce_block "create/params: ok"
    expect 0 ./main.py create "s0 p+1,10"
    expect 0 ./main.py create " s0 p+1,10"
    expect 0 ./main.py create "s0 p+1,10 "
    expect 0 ./main.py create " s0 p+1,10 "
    expect 0 ./main.py create "s0   p+1,10"
    expect 0 ./main.py create "s0
    p+1,10"
    expect 0 ./main.py create "s0 p+1,10 r+,1-99,10 r+,1-99,10"
    expect 0 ./main.py create "  s0 p+1,10 r+,1-99,10 r+,1-99,10"
    expect 0 ./main.py create "s0 p+1,10 r+,1-99,10 r+,1-99,10  "
    expect 0 ./main.py create "  s0 p+1,10    r+,1-99,10 r+,1-99,10  "
    expect 0 ./main.py create " s0 p+1,10    r+,1-99,10
    r+,1-99,10  "
    announce_block "create/params: err"
    expect 2 ./main.py create "s0p+1,10"
    expect 2 ./main.py create "s0,p+1,10"
    expect 2 ./main.py create "s0 p+1,10;"
    expect 2 ./main.py create "s0_p+1,10"
    expect 2 ./main.py create "s0_p+1,10x"
    expect 2 ./main.py create "^s0 r+,1-99,10"
    expect 2 ./main.py create "s0 r+,1-99,10^"
    expect 2 ./main.py create "s0!r+,1-99,10"
    expect 2 ./main.py create ".s0 r+,1-99,10"
    expect 2 ./main.py create "s0 r+,1-99,10."
    expect 2 ./main.py create "s0?c+,1-99"
    expect 2 ./main.py create "s0 p+1,10r+,1-99,10 r+,1-99,10"
    expect 2 ./main.py create "s0 p+1,10 r+,1-99,10c+,1-99"
    expect 2 ./main.py create "s0 p+1,10/r+,1-99,10 r+,1-99,10"
    expect 2 ./main.py create "s0 p+1,10 r+,1-99,10.c+,1-99"
    expect 2 ./main.py create "?s0 p+1,10 r+,1-99,10 r+,1-99,10"
    expect 2 ./main.py create "s0 p+1,10 r+,1-99,10 r+,1-99,10!"
    expect 2 ./main.py create "s0 p+1,10 r+,1-99,10 r+,1-99,10 !"
    expect 2 ./main.py create "? s0 p+1,10 r+,1-99,10 r+,1-99,10"
    expect 2 ./main.py create " s0 p+1,10 ___ r+,1-99,10 r+,1-99,10"

    announce_block "create/params/start-number: ok"
    expect 0 ./main.py create "s0 p+1,10"
    expect 0 ./main.py create "sr p+1,10"
    expect 0 ./main.py create "s1 p+1,10"
    expect 0 ./main.py create "s1.2 p+1,10"
    expect 0 ./main.py create "s-1 p+1,10"
    expect 0 ./main.py create "s-1.2 p+1,10"
    announce_block "create/params/start-number: err"
    expect 2 ./main.py create "p+1,10"
    expect 2 ./main.py create "s p+1,10"
    expect 2 ./main.py create "0 p+1,10"
    expect 2 ./main.py create "d0 p+1,10"
    expect 2 ./main.py create "sx p+1,10"

    announce_block "create/params/seq_params: ok"
    expect 0 ./main.py create "s0 p+1,10"
    expect 0 ./main.py create "s0 r+,1-99,10"
    expect 0 ./main.py create "s0 r+,1-99,10"
    announce_block "create/params/seq_params: err"
    expect 2 ./main.py create "s0 p+110"
    expect 2 ./main.py create "s0 p+1,10,"
    expect 2 ./main.py create "s0 ,p+1,10"
    expect 2 ./main.py create "s0 ,p+1,10,"
    expect 2 ./main.py create "s0 r+1-9910"
    expect 2 ./main.py create "s0 r+1-99,10"
    expect 2 ./main.py create "s0 r+,1-99,10,"
    expect 2 ./main.py create "s0 ,r+,1-99,10"
    expect 2 ./main.py create "s0 ,r+,1-99,10,"
    expect 2 ./main.py create "s0 r+1-9910"
    expect 2 ./main.py create "s0 r+1-99,10"
    expect 2 ./main.py create "s0 r+,1-99,10,"
    expect 2 ./main.py create "s0 ,c+,1-99"
    expect 2 ./main.py create "s0 ,c+,1-99,10,"
    expect 2 ./main.py create "s0 p+1,10x"
    expect 2 ./main.py create "s0 xp+1,10"
    expect 2 ./main.py create "s0 xp+1,10x"
    expect 2 ./main.py create "s0 r+,1-99,10_"
    expect 2 ./main.py create "s0 _r+,1-99,10"
    expect 2 ./main.py create "s0 _r+,1-99,10_"
    expect 2 ./main.py create "s0 r+,1-99,10?"
    expect 2 ./main.py create "s0 ?c+,1-99"
    expect 2 ./main.py create "s0 ?c+,1-99,10?"

    announce_block "create/params/seq_params/kind: ok"
    expect 0 ./main.py create "s0 p+1,10"
    expect 0 ./main.py create "s0 r+,1-99,10"
    expect 0 ./main.py create "s0 c+,1-99,10"
    announce_block "create/params/seq_params/kind: err"
    expect 2 ./main.py create "s0 0,10"
    expect 2 ./main.py create "s0 1,10"
    expect 2 ./main.py create "s0 1.2,10"
    expect 2 ./main.py create "s0 -1,10"
    expect 2 ./main.py create "s0 -1.2,10"
    expect 2 ./main.py create "s0 +,1-99,10"
    expect 2 ./main.py create "s0 +,1-99,10"
    expect 2 ./main.py create "s0 x0,10"
    expect 2 ./main.py create "s0 x1,10"
    expect 2 ./main.py create "s0 x1.2,10"
    expect 2 ./main.py create "s0 x-1,10"
    expect 2 ./main.py create "s0 x-1.2,10"
    expect 2 ./main.py create "s0 x+,1-99,10"
    expect 2 ./main.py create "s0 x+,1-99,10"

    # progression
    announce_block "create/params/seq_params/kind.progression/operand-diff: ok"
    expect 0 ./main.py create "s0 p+1,10"
    expect 0 ./main.py create "s0 p+1.2,10"
    expect 0 ./main.py create "s100 p-1,10"
    expect 0 ./main.py create "s100 p-1.2,10"
    expect 0 ./main.py create "s0 p*2,10"
    expect 0 ./main.py create "s0 p*1.2,10"
    expect 0 ./main.py create "s0 p/2,10"
    expect 0 ./main.py create "s0 p/1.2,10"
    announce_block "create/params/seq_params/kind.progression/operand-diff: err"
    expect 2 ./main.py create "s0 p+0,10" # diff can't be 0
    expect 2 ./main.py create "s100 p-0,10" # diff can't be 0
    expect 2 ./main.py create "s0 p/0,10" # diff can't be 0
    expect 2 ./main.py create "s0 p*0,10" # diff can't be 0
    expect 2 ./main.py create "s0 p+,10"
    expect 2 ./main.py create "s0 p+x,10"
    expect 2 ./main.py create "s0 p+1.x,10"
    expect 2 ./main.py create "s0 p+x.2,10"
    expect 2 ./main.py create "s100 p-x,10"
    expect 2 ./main.py create "s100 p-1.x,10"
    expect 2 ./main.py create "s100 p-x.2,10"
    announce_block "create/params/seq_params/kind.progression/length: ok"
    expect 0 ./main.py create "s0 p+1,1"
    expect 0 ./main.py create "s0 p+1,15"
    announce_block "create/params/seq_params/kind.progression/length: err"
    expect 2 ./main.py create "s0 p+1,"
    expect 2 ./main.py create "s0 p+1,0"
    expect 2 ./main.py create "s0 p+1,1.2"
    expect 2 ./main.py create "s0 p+1,-1"
    expect 2 ./main.py create "s0 p+1,-1.2"
    expect 2 ./main.py create "s0 p+1,x"
    announce_block "create/params/seq_params/kind.progression/optional: ok"
    expect 0 ./main.py create "s0 p+1,10"
    expect 0 ./main.py create "s0 p+1,10:"
    expect 0 ./main.py create "s0 p+1,10:n"
    expect 0 ./main.py create "s0 p+1,10:<"
    expect 0 ./main.py create "s0 p+1,10:n<"
    expect 0 ./main.py create "s0 p+1,10:<n"
    announce_block "create/params/seq_params/kind.progression/optional: err"
    expect 2 ./main.py create "s0 p+1,10:?"
    expect 2 ./main.py create "s0 p+1,10:.?"
    expect 2 ./main.py create "s0 p+1,10:.0"
    expect 2 ./main.py create "s0 p+1,10:.1.2"
    expect 2 ./main.py create "s0 p+1,10:.-1.2"
    expect 2 ./main.py create "s0 p+1,10:.2%?"
    expect 2 ./main.py create "s0 p+1,10:.2%0"
    expect 2 ./main.py create "s0 p+1,10:.2%101"
    expect 2 ./main.py create "s0 p+1,10:.2%1.2"
    expect 2 ./main.py create "s0 p+1,10:.2%-1"
    expect 2 ./main.py create "s0 p+1,10:.2%-1.2"
    expect 2 ./main.py create "s0 p+1,10n"
    expect 2 ./main.py create "s0 p+1,10.2"
    expect 2 ./main.py create "s0 p+1,10.2%10"
    expect 2 ./main.py create "s0 p+1,10<"
    expect 2 ./main.py create "s0 p+1,10:7n"
    expect 2 ./main.py create "s0 p+1,10:7.2"
    expect 2 ./main.py create "s0 p+1,10:7.2%10"
    expect 2 ./main.py create "s0 p+1,10:7<"
    expect 2 ./main.py create "s0 p+1,10:xn"
    expect 2 ./main.py create "s0 p+1,10:x.2"
    expect 2 ./main.py create "s0 p+1,10:x.2%10"
    expect 2 ./main.py create "s0 p+1,10:x<"
    expect 2 ./main.py create "s0 p+1,10:?n"
    expect 2 ./main.py create "s0 p+1,10:?.2"
    expect 2 ./main.py create "s0 p+1,10:?.2%10"
    expect 2 ./main.py create "s0 p+1,10:?<"
    expect 2 ./main.py create "s0 p+1,10:nx"
    expect 2 ./main.py create "s0 p+1,10:.2x"
    expect 2 ./main.py create "s0 p+1,10:.2%10x"
    expect 2 ./main.py create "s0 p+1,10:<x"

    # random
    announce_block "create/params/seq_params/kind.random/required: ok"
    expect 0 ./main.py create "s0 r+,1-99,10"
    announce_block "create/params/seq_params/kind.random/required: err"
    expect 2 ./main.py create "s0 r+1-99,10"
    expect 2 ./main.py create "s0 r+,1-9910"
    expect 2 ./main.py create "s0 r+1-9910"
    announce_block "create/params/seq_params/kind.random/required/operands: ok"
    expect 0 ./main.py create "s900 r+,1-99,10"
    expect 0 ./main.py create "s900 r-,1-99,10"
    expect 0 ./main.py create "s900 r+-,1-99,10"
    expect 0 ./main.py create "s900 r+1,1-99,10"
    expect 0 ./main.py create "s900 r+2,1-99,10"
    expect 0 ./main.py create "s900 r+15,1-99,10"
    expect 0 ./main.py create "s900 r+-2,1-99,10"
    expect 0 ./main.py create "s900 r+2-,1-99,10"
    expect 0 ./main.py create "s900 r+2-2,1-99,10"
    expect 0 ./main.py create "s900 r+2-3,1-99,10"
    announce_block "create/params/seq_params/kind.random/required/operands: err"
    expect 2 ./main.py create "s900 r,1-99,10"
    expect 2 ./main.py create "s900 r++,1-99,10"
    expect 2 ./main.py create "s900 rx,1-99,10"
    expect 2 ./main.py create "s900 r+x,1-99,10"
    expect 2 ./main.py create "s900 rx-,1-99,10"
    expect 2 ./main.py create "s900 r+0,1-99,10"
    expect 2 ./main.py create "s900 r+1.2,1-99,10"
    expect 2 ./main.py create "s900 r*,1-99,10" # TODO analyze */
    expect 2 ./main.py create "s900 r/,1-99,10" # TODO analyze */
    expect 2 ./main.py create "s900 r*-,1-99,10" # TODO analyze */
    expect 2 ./main.py create "s900 r/+,1-99,10" # TODO analyze */
    expect 2 ./main.py create "s900 r*+/,1-99,10" # TODO analyze */
    expect 2 ./main.py create "s900 r+-*/,1-99,10" # TODO analyze */
    announce_block "create/params/seq_params/kind.random/required/range: ok"
    expect 0 ./main.py create "s0 r+,1-99,10"
    announce_block "create/params/seq_params/kind.random/required/range: err"
    expect 2 ./main.py create "s0 r+,0-99,10"
    expect 2 ./main.py create "s0 r+,-1-99,10"
    expect 2 ./main.py create "s0 r+,-1.2-99,10"
    expect 2 ./main.py create "s0 r+,1-99.2,10"
    expect 2 ./main.py create "s0 r+,1x99,10"
    expect 2 ./main.py create "s0 r+,_1-99,10"
    expect 2 ./main.py create "s0 r+,1-99_,10"
    expect 2 ./main.py create "s0 r+,_1-99_,10"
    announce_block "create/params/seq_params/kind.random/required/length: ok"
    expect 0 ./main.py create "s0 r+,1-99,1"
    expect 0 ./main.py create "s0 r+,1-99,10"
    announce_block "create/params/seq_params/kind.random/required/length: err"
    expect 2 ./main.py create "s0 r+,1-99"
    expect 2 ./main.py create "s0 r+,1-99,0"
    expect 2 ./main.py create "s0 r+,1-99,1.2"
    expect 2 ./main.py create "s0 r+,1-99,-1"
    expect 2 ./main.py create "s0 r+,1-99,-1.2"
    expect 2 ./main.py create "s0 r+,1-99,0"
    expect 2 ./main.py create "s0 r+,1-99,1.2"
    expect 2 ./main.py create "s0 r+,1-99,-1"
    expect 2 ./main.py create "s0 r+,1-99,-1.2"
    expect 2 ./main.py create "s0 r+,1-99,"
    expect 2 ./main.py create "s0 r+,1-99,"
    expect 2 ./main.py create "s0 r+,1-99,x"
    expect 2 ./main.py create "s0 r+,1-99,x"
    announce_block "create/params/seq_params/kind.random/optional: ok"
    expect 0 ./main.py create "s0 r+,1-99,10"
    expect 0 ./main.py create "s0 r+,1-99,10:n"
    expect 0 ./main.py create "s0 r+,1-99,10:.2"
    expect 0 ./main.py create "s0 r+,1-99,10:.2%10"
    expect 0 ./main.py create "s0 r+,1-99,10:<"
    expect 0 ./main.py create "s0 r+,1-99,10:n.2"
    expect 0 ./main.py create "s0 r+,1-99,10:n.2%10"
    expect 0 ./main.py create "s0 r+,1-99,10:n<"
    expect 0 ./main.py create "s0 r+,1-99,10:.2n"
    expect 0 ./main.py create "s0 r+,1-99,10:.2<"
    expect 0 ./main.py create "s0 r+,1-99,10:.2%10n"
    expect 0 ./main.py create "s0 r+,1-99,10:.2%10<"
    expect 0 ./main.py create "s0 r+,1-99,10:<n"
    expect 0 ./main.py create "s0 r+,1-99,10:<.2"
    expect 0 ./main.py create "s0 r+,1-99,10:<.2%10"
    expect 0 ./main.py create "s0 r+,1-99,10:"
    announce_block "create/params/seq_params/kind.random/optional: err"
    expect 2 ./main.py create "s0 r+,1-99,10:?"
    expect 2 ./main.py create "s0 r+,1-99,10:.?"
    expect 2 ./main.py create "s0 r+,1-99,10:.0"
    expect 2 ./main.py create "s0 r+,1-99,10:.1.2"
    expect 2 ./main.py create "s0 r+,1-99,10:.-1.2"
    expect 2 ./main.py create "s0 r+,1-99,10:.2%?"
    expect 2 ./main.py create "s0 r+,1-99,10:.2%0"
    expect 2 ./main.py create "s0 r+,1-99,10:.2%101"
    expect 2 ./main.py create "s0 r+,1-99,10:.2%1.2"
    expect 2 ./main.py create "s0 r+,1-99,10:.2%-1"
    expect 2 ./main.py create "s0 r+,1-99,10:.2%-1.2"
    expect 2 ./main.py create "s0 r+,1-99,10n"
    expect 2 ./main.py create "s0 r+,1-99,10.2"
    expect 2 ./main.py create "s0 r+,1-99,10.2%10"
    expect 2 ./main.py create "s0 r+,1-99,10<"
    expect 2 ./main.py create "s0 r+,1-99,10:7n"
    expect 2 ./main.py create "s0 r+,1-99,10:7.2"
    expect 2 ./main.py create "s0 r+,1-99,10:7.2%10"
    expect 2 ./main.py create "s0 r+,1-99,10:7<"
    expect 2 ./main.py create "s0 r+,1-99,10:xn"
    expect 2 ./main.py create "s0 r+,1-99,10:x.2"
    expect 2 ./main.py create "s0 r+,1-99,10:x.2%10"
    expect 2 ./main.py create "s0 r+,1-99,10:x<"
    expect 2 ./main.py create "s0 r+,1-99,10:?n"
    expect 2 ./main.py create "s0 r+,1-99,10:?.2"
    expect 2 ./main.py create "s0 r+,1-99,10:?.2%10"
    expect 2 ./main.py create "s0 r+,1-99,10:?<"
    expect 2 ./main.py create "s0 r+,1-99,10:nx"
    expect 2 ./main.py create "s0 r+,1-99,10:.2x"
    expect 2 ./main.py create "s0 r+,1-99,10:.2%10x"
    expect 2 ./main.py create "s0 r+,1-99,10:<x"

    # cover
    announce_block "create/params/seq_params/kind.cover/required: ok"
    expect 0 ./main.py create "s0 c+,1-99"
    expect 0 ./main.py create "s0 c+,1-99,300"
    announce_block "create/params/seq_params/kind.cover/required: err"
    expect 2 ./main.py create "s0 c+1-99"
    expect 2 ./main.py create "s0 c+,1-99,"
    expect 2 ./main.py create "s0 ,c+,1-99"
    expect 2 ./main.py create "s0 ,c+,1-99,"
    announce_block "create/params/seq_params/kind.cover/required/operands: ok"
    expect 0 ./main.py create "s10000 c+,1-99"
    expect 0 ./main.py create "s10000 c-,1-99"
    expect 0 ./main.py create "s10000 c+-,1-99"
    expect 0 ./main.py create "s10000 c-+,1-99"
    expect 0 ./main.py create "s10000 c+1,1-99"
    expect 0 ./main.py create "s10000 c+2,1-99"
    expect 0 ./main.py create "s10000 c+15,1-99"
    expect 0 ./main.py create "s10000 c+-2,1-99"
    expect 0 ./main.py create "s10000 c+2-,1-99"
    expect 0 ./main.py create "s10000 c+2-2,1-99"
    expect 0 ./main.py create "s10000 c+2-3,1-99"
    expect 0 ./main.py create "s10000 c-,1-99"
    expect 0 ./main.py create "s10000 c-,1-99,300"
    expect 0 ./main.py create "s10000 c-,1-99"
    expect 0 ./main.py create "s10000 c-,1-99,300"
    expect 0 ./main.py create "s10000 c+-,1-99"
    expect 0 ./main.py create "s10000 c+-,1-99,300"
    expect 0 ./main.py create "s10000 c+-,1-99"
    expect 0 ./main.py create "s10000 c+-,1-99,300"
    announce_block "create/params/seq_params/kind.cover/required/operands: err"
    expect 2 ./main.py create "s10000 c,1-99"
    expect 2 ./main.py create "s10000 c++,1-99"
    expect 2 ./main.py create "s10000 rx,1-99"
    expect 2 ./main.py create "s10000 c+x,1-99"
    expect 2 ./main.py create "s10000 rx-,1-99"
    expect 2 ./main.py create "s10000 c+0,1-99"
    expect 2 ./main.py create "s10000 c+1.2,1-99"
    expect 2 ./main.py create "s10000 c*,1-99" # TODO create */
    expect 2 ./main.py create "s10000 c/,1-99" # TODO create */
    expect 2 ./main.py create "s10000 c*-,1-99" # TODO create */
    expect 2 ./main.py create "s10000 c/+,1-99" # TODO create */
    expect 2 ./main.py create "s10000 c*+/,1-99" # TODO create */
    expect 2 ./main.py create "s10000 c+-*/,1-99" # TODO create */
    announce_block "create/params/seq_params/kind.cover/required/range: ok"
    expect 0 ./main.py create "s0 c+,1-99"
    announce_block "create/params/seq_params/kind.cover/required/range: err"
    expect 2 ./main.py create "s0 c+,0-99,10"
    expect 2 ./main.py create "s0 c+,-1-99"
    expect 2 ./main.py create "s0 c+,-1.2-99,10"
    expect 2 ./main.py create "s0 c+,1-99.2,10"
    expect 2 ./main.py create "s0 c+,1x99,10"
    expect 2 ./main.py create "s0 c+,_1-99"
    expect 2 ./main.py create "s0 c+,1-99_,10"
    expect 2 ./main.py create "s0 c+,_1-99_,10"
    announce_block "create/params/seq_params/kind.cover/required/length: ok"
    expect 0 ./main.py create "s0 c+,1-99"
    expect 0 ./main.py create "s0 c+,1-99,1"
    expect 0 ./main.py create "s0 c+,1-99,300"
    announce_block "create/params/seq_params/kind.cover/required/length: err"
    expect 2 ./main.py create "s0 c+,1-99,"
    expect 2 ./main.py create "s0 c+,1-99,"
    expect 2 ./main.py create "s0 c+,1-99,0"
    expect 2 ./main.py create "s0 c+,1-99,1.2"
    expect 2 ./main.py create "s0 c+,1-99,-1"
    expect 2 ./main.py create "s0 c+,1-99,-1.2"
    expect 2 ./main.py create "s0 c+,1-99,0"
    expect 2 ./main.py create "s0 c+,1-99,1.2"
    expect 2 ./main.py create "s0 c+,1-99,-1"
    expect 2 ./main.py create "s0 c+,1-99,-1.2"
    expect 2 ./main.py create "s0 c+,1-99,x"
    expect 2 ./main.py create "s0 c+,1-99,x"
    announce_block "create/params/seq_params/kind.cover/optional: ok"
    expect 0 ./main.py create "s0 c+,1-99"
    expect 0 ./main.py create "s0 c+,1-99:"
    expect 0 ./main.py create "s0 c+,1-99:n"
    expect 2 ./main.py create "s0 c+,1-99:.2" # TODO cover for decimal
    expect 2 ./main.py create "s0 c+,1-99:.2%10" # TODO cover for decimal
    expect 0 ./main.py create "s0 c+,1-99:<"
    expect 2 ./main.py create "s0 c+,1-99:n.2" # TODO cover for decimal
    expect 2 ./main.py create "s0 c+,1-99:n.2%10" # TODO cover for decimal
    expect 0 ./main.py create "s0 c+,1-99:n<"
    expect 2 ./main.py create "s0 c+,1-99:.2n" # TODO cover for decimal
    expect 2 ./main.py create "s0 c+,1-99:.2<" # TODO cover for decimal
    expect 2 ./main.py create "s0 c+,1-99:.2%10n" # TODO cover for decimal
    expect 2 ./main.py create "s0 c+,1-99:.2%10<" # TODO cover for decimal
    expect 0 ./main.py create "s0 c+,1-99:<n"
    expect 2 ./main.py create "s0 c+,1-99:<.2" # TODO cover for decimal
    expect 2 ./main.py create "s0 c+,1-99:<.2%10" # TODO cover for decimal
    announce_block "create/params/seq_params/kind.cover/optional: err"
    expect 2 ./main.py create "s0 c+,1-99.2"
    expect 2 ./main.py create "s0 c+,1-99.2%10"
    expect 2 ./main.py create "s0 c+,1-99<"
    expect 2 ./main.py create "s0 c+,1-99:?"
    expect 2 ./main.py create "s0 c+,1-99:.?" # TODO cover for decimal
    expect 2 ./main.py create "s0 c+,1-99:.0" # TODO cover for decimal
    expect 2 ./main.py create "s0 c+,1-99:.1.2" # TODO cover for decimal
    expect 2 ./main.py create "s0 c+,1-99:.-1.2" # TODO cover for decimal
    expect 2 ./main.py create "s0 c+,1-99:.2%?" # TODO cover for decimal
    expect 2 ./main.py create "s0 c+,1-99:.2%0" # TODO cover for decimal
    expect 2 ./main.py create "s0 c+,1-99:.2%101" # TODO cover for decimal
    expect 2 ./main.py create "s0 c+,1-99:.2%1.2" # TODO cover for decimal
    expect 2 ./main.py create "s0 c+,1-99:.2%-1" # TODO cover for decimal
    expect 2 ./main.py create "s0 c+,1-99:.2%-1.2" # TODO cover for decimal
    expect 2 ./main.py create "s0 c+,1-99:7n"
    expect 2 ./main.py create "s0 c+,1-99:7.2" # TODO cover for decimal
    expect 2 ./main.py create "s0 c+,1-99:7.2%10" # TODO cover for decimal
    expect 2 ./main.py create "s0 c+,1-99:7<"
    expect 2 ./main.py create "s0 c+,1-99:xn"
    expect 2 ./main.py create "s0 c+,1-99:x.2" # TODO cover for decimal
    expect 2 ./main.py create "s0 c+,1-99:x.2%10" # TODO cover for decimal
    expect 2 ./main.py create "s0 c+,1-99:x<"
    expect 2 ./main.py create "s0 c+,1-99:?n"
    expect 2 ./main.py create "s0 c+,1-99:?.2" # TODO cover for decimal
    expect 2 ./main.py create "s0 c+,1-99:?.2%10" # TODO cover for decimal
    expect 2 ./main.py create "s0 c+,1-99:?<"
    expect 2 ./main.py create "s0 c+,1-99:nx"
    expect 2 ./main.py create "s0 c+,1-99:.2x" # TODO cover for decimal
    expect 2 ./main.py create "s0 c+,1-99:.2%10x" # TODO cover for decimal
    expect 2 ./main.py create "s0 c+,1-99:<x"
}

if [[ -z "${1-}" ]]; then
    echo "   run         - run tests"
    echo "   show-data   - show files content ./data/*.txt"
    exit 1
fi
case "$1" in
    run)
        run
        ;;
    show-data)
        show_data
        ;;
    *)
        echo "   run         - run tests"
        echo "   show-data   - show files content ./data/*.txt"
        exit 1
        ;;
esac
