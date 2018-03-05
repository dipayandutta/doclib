#!/bin/bash

path=$1
searchString=$2

find $path -iname "*" -type f -print0 | xargs -0 grep -H $searchString 2> error.log

find $path -iname "*.pdf" -exec pdfgrep $searchString {} + 2 > error.log 