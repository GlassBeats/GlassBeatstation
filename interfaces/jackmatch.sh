#!/bin/bash
trap "exit" INT TERM ERR
trap "kill 0" EXIT

cd  &&
.local/bin/jack-matchmaker \
                ^a2j:mk2 ^a2j:Launchpad \
                ^a2j:Launchpad ^a2j:mk2 \
                ^a2j:open-stage-cc ^ardour:MIDI \
                ^a2j:open-stage-cc ^a2j:sooperlooper \
                .*glass_cc ^a2j:sooperlooper \
                .*glass_drum ^ardour:Drum \
                .*glass_sequencer ^ardour:Drum \
                .*glass_cc ^ardour:MIDI control \
                ^a2j:open-stage ^a2j:sooperlooper \

                
