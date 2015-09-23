#!/bin/bash
echo "Start TZ1 tester"
cd `dirname $0`
source bin/activate
./00_tz1_tester_server.py
