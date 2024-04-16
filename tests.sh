#!/bin/bash
# TODO: проверить чтобы необязательный парметр filename
#       для create всегда был последним и работал

set -euo pipefail
set -x

./main.py create arithmetic 0 100
./main.py create random plus x-x 5
./main.py create random minus x-x 5
./main.py create random plus-minus-roundtrip x-x 5
./main.py create random plus-minus x-x 5
./main.py create cover-units plus x-x
./main.py create cover-units minus x-x
./main.py create cover-units plus-minus-roundtrip x-x
# TODO: ./main.py create cover-units plus-minus x-x
./main.py run-new arithmetic 0 100
./main.py run-new random plus x-x 5
./main.py run-new random minus x-x 5
# TODO: ./main.py run-new random plus-minus-roundtrip x-x 5
# TODO: ./main.py run-new random plus-minus x-x 5
./main.py run-new cover-units plus x-x
./main.py run-new cover-units minus x-x
# TODO: ./main.py run-new cover-units plus-minus-roundtrip x-x
# TODO: ./main.py run-new cover-units plus-minus x-x

# TODO: ./main.py run-new training arithmetic 0 100
# TODO: ./main.py run-new training random plus x-x
# TODO: ./main.py run-new training random minus x-x
# TODO: ./main.py run-new training random plus-minus-roundtrip x-x
# TODO: ./main.py run-new training random plus-minus x-x
# TODO: ./main.py run-new training cover-units plus x-x
# TODO: ./main.py run-new training cover-units minus x-x
# TODO: ./main.py run-new training cover-units plus-minus-roundtrip x-x
# TODO: ./main.py run-new training cover-units plus-minus x-x
# TODO: ./main.py run-new exam arithmetic 0 100
# TODO: ./main.py run-new exam random plus x-x
# TODO: ./main.py run-new exam random minus x-x
# TODO: ./main.py run-new exam random plus-minus-roundtrip x-x
# TODO: ./main.py run-new exam random plus-minus x-x
# TODO: ./main.py run-new exam cover-units plus x-x
# TODO: ./main.py run-new exam cover-units minus x-x
# TODO: ./main.py run-new exam cover-units plus-minus-roundtrip x-x
# TODO: ./main.py run-new exam cover-units plus-minus x-x
# TODO: ./main.py study
