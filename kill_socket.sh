#!/bin/sh
sudo netstat -ap | grep 5000 | awk '{ print $4 }' | awk -F'[ :]' '{ system("sudo tcpkill -i eth0 host $1 and port $2") }'