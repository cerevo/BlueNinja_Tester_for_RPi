#!/bin/bash
echo "Start TZ1 tester"
cd `dirname $0`

source bin/activate
#Enable BLE Scan
sudo hciconfig hci0 down
sudo hciconfig hci0 up
sudo hcitool lescan > /dev/null 2>&1 &

#Run tester server.
./00_tz1_tester_server.py

