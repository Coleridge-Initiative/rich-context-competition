#!/bin/bash

# Open code block, output of which we will redirect to a file.
{
    time ./rcc.sh run-stop
} 2>&1 | tee -a model_run_output$(date +"%Y%m%d%H%M%S").txt
