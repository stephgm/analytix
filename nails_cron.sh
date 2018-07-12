#!/bin/bash

mach=$(cat /etc/redhat-release | awk '{split($0,a);print a[3]}' | awk '{split($0,a,".");print a[1]}')
if [ "${mach}" == "6" ];then
echo "0 6 * * * root service nails stop" >> /etc/crontab
echo "0 18 * * * root service nails start" >> /etc/crontab
else
mach=$(cat /etc/redhat-release | awk '{split($0,a);print a[4]}' | awk '{split($0,a,".");print a[1]}')
if [ "${mach}" == "7" ];then
echo "0 6 * * * root systemctl stop nails" >> /etc/crontab
echo "0 18 * * * root systemctl start nails" >> /etc/crontab
fi
fi
