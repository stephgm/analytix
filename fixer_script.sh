#!/bin/bash

for i in $(cat iplist)
do
ip=$(echo $i | awk -F "," '{print $1}')
first=$(echo $i | awk -F "," '{print $2}')
last=$(echo $i | awk -F "," '{print $3}')
done

# OR
un=()
while IFS= read -r line
do
un+=($(echo $line | awk '{split($0,a,":");print a[1]'))
done < passwd

for ((i=0;i<${#un[@]};i++));do
echo "${un[i]}"
done

newips=()
for ((i=0;i<${#newips[@]};i++));do
echo "/storage/share       ${newips[i]}/255.255.255.0(rw,sync,no_root_squash)" >> /etc/exports
done
exportfs -r

# /etc/hosts
