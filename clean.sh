#!/bin/bash

files=$(find . -name "*.pyc")
if [ ${#files} -gt 0 ];then
	rm -fv $files
fi
files=$(find . -name "*_py.txt")
if [ ${#files} -gt 0 ];then
	rm -fv $files
fi
files=$(find . -name "bluemarble*.npy")
if [ ${#files} -gt 0 ];then
	rm -fv $files
fi
find . -name "*" -type d | xargs rmdir 2>/dev/null
