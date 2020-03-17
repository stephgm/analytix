#!/bin/bash

echo -n "Enter password : "
read -s pw

while (( "$#" ));
do
bn=$(basename $1)
fl=${#bn}
openssl enc -aes-256-cbc -d -in "$1" -out ${1:0:fl-4} -k ${pw}
shift
done
