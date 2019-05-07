#!/bin/bash

# Open code block, output of which we will redirect to a file.
{
    time ./rcc.sh "${1}"
} 2>&1 | tee -a rcc.sh_${1}_output-$(date +"%Y%m%d%H%M%S").txt
