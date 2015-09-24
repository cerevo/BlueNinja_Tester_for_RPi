#!/bin/bash

DEV_NAME=CDP-TZ01B_01
TEMP_FILE=/tmp/lescan_detect

sudo rm -rf $TEMP_FILE

sudo hciconfig hci0 up
sudo hcidump 2>/dev/null | grep --line-buffered -B 3 -A 1 $DEV_NAME > $TEMP_FILE &
#echo -n "Beging scan"
sudo hcitool lescan > /dev/null 2>&1 &

for ((i = 0; i < 20; i++))
do
	#echo -n "."
	if [ -s $TEMP_FILE ]
	then
		#echo "Detect"
		RSSI=`awk '/RSSI/ {print $2; exit 10}' $TEMP_FILE`
		if [ $? != "10" ]
		then
			continue
		fi
		BDADDR=`awk '/bdaddr/{print $2; exit 10}' $TEMP_FILE`
		if [ $? != "10" ]
		then
			continue
		fi
		sudo killall hcidump
		#sudo killall hcitool
		rm -f $TEMP_FILE

		echo $BDADDR
		echo $RSSI
		exit 0
	fi
	sleep 1
done
exit 1
