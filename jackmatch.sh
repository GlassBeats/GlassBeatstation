#!/bin/bash
trap "exit" INT TERM ERR
trap "kill 0" EXIT

jack-matchmaker ^a2j:mk2 ^a2j:Launchpad \
                ^a2j:Launchpad ^a2j:mk2 \
		.*glass_cc ^a2j:sooperlooper \
		.*glass_instrument "^ardour:Ninja Sampler" \
		.*glass_drum ^ardour:Drum \
		.*glass_sequencer ^ardour:Drum \
		^a2j:open-stage-cc "^ardour:MIDI control" \
		^a2j:open-stage-cc ^a2j:sooperlooper \
