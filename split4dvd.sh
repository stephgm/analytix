#!/bin/bash
if [ "$1" == "" ];then
echo "usage: $0 file2split"
exit
fi
# to reformat DVD
# yum -y install udftools
# mkudffs /dev/sr0
# 3.2 GB
split -b 3221225472 "${1}" "${1}_"
# 4.2 GB
#split -b 4509715660 "${1}" "${1}_"
#split -b 4689887232 "${1}" "${1}_"
#split -b 4702989189 "${1}" "${1}_"
