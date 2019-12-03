#!/bin/bash
trap "exit" INT TERM ERR
trap "kill 0" EXIT

sooperlooper -L ./interfaces/default.slsess -l 8 -m ./interfaces/sl_bindings.slb &

node /home/pi/installed_local/open-stage-control/app/ -n -l interfaces/stagecontrol.json  -s 127.0.0.1:9998 -m "open-stage-cc:virtual" &

python3 gbeatstation_main.py
