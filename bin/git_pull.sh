#!/bin/bash
script_path=`realpath $0`
script_directory_path=`dirname ${script_path}`
cd "${script_directory_path}/.."
git pull