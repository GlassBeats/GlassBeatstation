#!/bin/bash
trap "exit" INT TERM ERR
trap "kill 0" EXIT

jack-matchmaker \
	.*glass_cc ^a2j:sooperlooper \
	".*open-stage-cc" ^a2j:sooperlooper \

