#!/bin/bash
echo -e "MAKE SURE GPS AND FSH ARE CONNECTED?"
echo -e "PRESS ANY KEY FOR NEXT ... ..."
read tipka2
#su -c ./testports.sh
#echo -e "AKO JE SVE UREDU, PRITISNITE d ZA NASTAVAK. "
#read tipka2
#if [ $tipka2!="d" ]; then
#exit()
#fi
su -c "chmod 777 /dev/ttyUSB0; chmod 777 /dev/ttyUSB1"
python gpspectrum.py -g off -p /dev/ttyUSB0 -d data/rfid -c rfid -t 10 -s 3
echo -e "PRESS ANY KEY FOR NEXT ... OR Ctrl+C TO STOP."
read tipka3
echo "HOW LONG THE MEASUREMENT IS GOING TO LAST IN secs:"
read timesec
echo -e "MEASUREMENT IS STARTING..."
python gpspectrum.py -g /dev/ttyUSB1 -p /dev/ttyUSB0 -d data/rfid -c rfid -t $timesec -s 3

