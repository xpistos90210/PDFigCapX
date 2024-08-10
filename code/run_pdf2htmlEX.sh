#!/bin/bash

INPUT_FILE=$1
OUTPUT_DIR=$2

docker run --rm -v $(pwd):/pdf bwits/pdf2htmlex pdf2htmlEX /pdf/${INPUT_FILE} /pdf/${OUTPUT_DIR}
