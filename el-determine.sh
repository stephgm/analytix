#!/bin/bash

if  grep -q .*\ 7\..* /etc/redhat-release ;then
echo "RHEL 7"
elif  grep -q .*\ 6\..* /etc/redhat-release;then
echo "RHEL 6"
fi
