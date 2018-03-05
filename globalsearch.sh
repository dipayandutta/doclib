#!/bin/bash
searchString=$1


find /work/python/flask_application/doclib -iname "*" -type f -print0 | xargs -0 grep -H $searchString 2> error.log

find /work/python/flask_application/doclib -iname "*.pdf" -exec pdfgrep $searchString {} + 2 > error.log 
