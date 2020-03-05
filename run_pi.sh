#!/bin/bash
trap "exit" INT TERM ERR
trap "kill 0" EXIT

sleep 5 &&
jack_control start && a2j_control start && jack_bufsize 400 &&

./interfaces/jackmatch.sh &

#ardour5 /home/pi/Music/ardour/pinauguration

sooperlooper -L /home/pi/projects/glass_beatstation/interfaces/default.slsess -l 8 -m /home/pi/projects/glass_beatstation/interfaces/sl_bindings.slb &

sleep 2 &&

node /home/pi/installed_local/open-stage-control/app/ -n -l /home/pi/projects/glass_beatstation/interfaces/stagecontrol.json  -s 127.0.0.1:9998 -m "open-stage-cc:virtual" &

#cd /home/pi/installed_local/VL53L0X_rasp_python/python/ && python3 ./vlidar_midi.py &

sleep 10 &&

python3 /home/pi/projects/glass_beatstation/gbeatstation_main.py
