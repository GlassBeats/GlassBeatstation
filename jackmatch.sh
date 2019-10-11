#!/bin/bash
trap "exit" INT TERM ERR
trap "kill 0" EXIT

jack-matchmaker ^a2j:mk2 ^Launchpad \
                ^Launchpad ^a2j:mk2 \
		^a2j:glass_cc ^a2j:sooperlooper \
		^a2j:glass_instr ^ardour:Ninja Sampler/midi \
		^a2j:glass_drum ardour:Drum
		
