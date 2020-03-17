#!/bin/bash

echo -n "Enter password : "
read -s pw

while (( "$#" ));
do
bn=$(basename $1)
fl=${#bn}
openssl enc -aes-256-cbc -in "$1" -out "${1}.ssl" -k ${pw}
shift
done
