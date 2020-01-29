#!/bin/bash

this=$(echo ${HOSTNAME} | awk -F "." '{print $1}')
echo $this

sharez=()

for i in $(cat machine_shares)
do
that=$(echo $i | awk -F "," '{print $1}')
if [ "${that}" == "${this}" ];then
share=$(echo $i | awk -F "," '{print $2}')
echo $share
sharez+=("$share")
fi
done

echo "#" > /etc/exports

for i in $(cat iplist.csv)
do
ip=$(echo $i | awk -F "," '{print $1}')
mach=$(echo $i | awk -F "," '{print $2}')
if ! [ "${mach}" == "${this}" ];then
for ((j=0;j<${#sharez[@]};j++));do
echo "${sharez[j]}""       ${ip}""/255.255.255.0(rw,sync,no_root_squash)" >> /etc/exports
done
fi
#last=$(echo $i | awk -F "," '{print $3}')
done
exportfs -r
exit
############################################################
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

# /etc/hosts
