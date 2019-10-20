#!/bin/bash
trap "exit" INT TERM ERR
trap "kill 0" EXIT

#this script needs to be run from the glass_beatstation directory

#this script is oriented towards working with ardour but doesn't need ardour to run, although you will need to route the audio accordingly. change the audio connections manually or in the jackconnect.py script
jack_bufsize 512 &&

sooperlooper -L default_sl.slsess -l 8 -m sl_bindings.slb &

./jackmatch.sh & # this script for automatically persisting midi connections with jack-matchmaker

open-stage-control -l stagecontrol.json -s 127.0.0.1:9998 -m "open-stage-cc:virtual" &&

sleep 5

#python3 gbeatstation_main.py