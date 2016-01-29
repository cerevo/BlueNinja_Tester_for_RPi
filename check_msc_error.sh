#!/bin/sh
dmesg | grep "usb.*: device .*error \-71" | wc -l
