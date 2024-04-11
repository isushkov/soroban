#!/bin/bash

echo ">>> ./main.py"
./main.py
echo ">>> ./main.py create"
./main.py create
echo ">>> ./main.py create arithmetic"
./main.py create arithmetic
echo ">>> ./main.py create arithmetic 0"
./main.py create arithmetic 0
echo ">>> ./main.py create arithmetic 10"
./main.py create arithmetic 10
echo ">>> ./main.py create arithmetic 0 my-arithmetic"
./main.py create arithmetic 0 my-arithmetic
echo ">>> ./main.py create arithmetic 0 100"
./main.py create arithmetic 0 100
echo ">>> ./main.py create arithmetic 0 1000 my-arithmetic"
./main.py create arithmetic 0 1000 my-arithmetic
echo ">>> ./main.py create random"
./main.py create random
echo ">>> ./main.py create random plus"
./main.py create random plus
echo ">>> ./main.py create random plus xx-xxx"
./main.py create random plus xx-xxx
echo ">>> ./main.py create random plus xx-xxx my-random"
./main.py create random plus xx-xxx my-random
echo ">>> ./main.py create random minus x-x"
./main.py create random minus x-x
echo ">>> ./main.py create random plus-minus x-x"
./main.py create random plus-minus x-x
echo ">>> ./main.py create random linear-plus-minus x-x"
./main.py create random linear-plus-minus x-x
echo ">>> ./main.py create cover-units plus"
./main.py create cover-units plus
echo ">>> ./main.py create cover-units plus"
./main.py create cover-units plus
echo ">>> ./main.py create cover-units plus xx-xxx"
./main.py create cover-units plus xx-xxx
echo ">>> ./main.py create cover-units plus xx-xxx my-cover-units"
./main.py create cover-units plus xx-xxx my-cover-units
echo ">>> ./main.py create cover-units minus x-x"
./main.py create cover-units minus x-x
echo ">>> ./main.py create cover-units plus-minus x-x"
./main.py create cover-units plus-minus x-x
echo ">>> ./main.py create cover-units linear-plus-minus x-x"
./main.py create cover-units linear-plus-minus x-x
echo ">>> ./main.py analyze"
./main.py analyze
echo ">>> ./main.py analyze my-arithmetic"
./main.py analyze my-arithmetic
echo ">>> ./main.py analyze my-random"
./main.py analyze my-random
echo ">>> ./main.py analyze my-cover-units"
./main.py analyze my-cover-units
echo ">>> ./main.py run"
./main.py run
echo ">>> ./main.py run my-arithmetic"
./main.py run my-arithmetic
echo ">>> ./main.py run my-random"
./main.py run my-random
echo ">>> ./main.py run my-cover-units"
./main.py run my-cover-units
echo ">>> ./main.py run-new"
./main.py run-new
echo ">>> ./main.py run-new arithmetic"
./main.py run-new arithmetic
echo ">>> ./main.py run-new arithmetic 0"
./main.py run-new arithmetic 0
echo ">>> ./main.py run-new arithmetic 10"
./main.py run-new arithmetic 10
echo ">>> ./main.py run-new arithmetic 0 my-arithmetic-new"
./main.py run-new arithmetic 0 my-arithmetic-new
echo ">>> ./main.py run-new arithmetic 0 100"
./main.py run-new arithmetic 0 100
echo ">>> ./main.py run-new arithmetic 0 1000 my-arithmetic-new"
./main.py run-new arithmetic 0 1000 my-arithmetic-new
echo ">>> ./main.py run-new random"
./main.py run-new random
echo ">>> ./main.py run-new random plus"
./main.py run-new random plus
echo ">>> ./main.py run-new random plus xx-xxx"
./main.py run-new random plus xx-xxx
echo ">>> ./main.py run-new random plus xx-xxx my-random-new"
./main.py run-new random plus xx-xxx my-random-new
echo ">>> ./main.py run-new random minus x-x"
./main.py run-new random minus x-x
echo ">>> ./main.py run-new random plus-minus x-x"
./main.py run-new random plus-minus x-x
echo ">>> ./main.py run-new random linear-plus-minus x-x"
./main.py run-new random linear-plus-minus x-x
echo ">>> ./main.py run-new cover-units plus"
./main.py run-new cover-units plus
echo ">>> ./main.py run-new cover-units plus"
./main.py run-new cover-units plus
echo ">>> ./main.py run-new cover-units plus xx-xxx"
./main.py run-new cover-units plus xx-xxx
echo ">>> ./main.py run-new cover-units plus xx-xxx my-cover-units-new"
./main.py run-new cover-units plus xx-xxx my-cover-units-new
echo ">>> ./main.py run-new cover-units minus x-x"
./main.py run-new cover-units minus x-x
echo ">>> ./main.py run-new cover-units plus-minus x-x"
./main.py run-new cover-units plus-minus x-x
echo ">>> ./main.py run-new cover-units linear-plus-minus x-x"
./main.py run-new cover-units linear-plus-minus x-x
