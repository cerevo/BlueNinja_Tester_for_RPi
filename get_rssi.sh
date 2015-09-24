#!/bin/bash

DEV_NAME=TZ101
TEMP_FILE=/tmp/lescan_detect

sudo rm -f $TEMP_FILE

#sudo hciconfig hci0 up
sudo hcidump 2>/dev/null | grep --line-buffered -B 2 -A 2 $DEV_NAME > $TEMP_FILE &
#echo -n "Beging scan"
#sudo hcitool lescan > /dev/null 2>&1 &

for ((i = 0; i < 20; i++))
do
	#echo -n "."
	if [ -s $TEMP_FILE ]
	then
		#sudo killall hcitool > /dev/null 2>&1
		sudo killall hcidump
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
		rm -f $TEMP_FILE

		echo $BDADDR
		echo $RSSI
		exit 0
	fi
	sleep 1
done

#sudo killall hcitool > /dev/null 2>&1
sudo killall hcidump
rm -f $TEMP_FILE
exit 1
