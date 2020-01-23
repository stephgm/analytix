#!/bin/bash

cython foo.pyx

gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/storage/data/local/include/python3.7m -o foo.so foo.c
