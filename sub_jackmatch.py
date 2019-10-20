import jackmatchmaker

jmatchmkr = jackmatchmaker.JackMatchmaker([
        ["^a2j:mk2", "^a2j:Launchpad"],
        ["^a2j:Launchpad", "^a2j:mk2"],

        #["^a2j:open-stage_cc", "^Bitrot"],
        ["^a2j:open-stage_control", "^sooperlooper"],

        ["zynaddsubfx:out_1", "sooperlooper:common_in_1"],
        ["zynaddsubfx:out_2", "sooperlooper:common_in_2"],

        ["Hydrogen:out_L", "sooperlooper:common_in_1"],
        ["Hydrogen:out_R", "sooperlooper:common_in_2"],

        ["sooperlooper:common_out_1", "Bitrot Repeat:Audio Input 1"],
        ["sooperlooper:common_out_2", "Bitrot Repeat:Audio Input 2"],




        ["^a2j:glass_instrument", "^ardour:Keys"],

        ["^a2j:open-stage-control", "^ardour:MIDI control in"],
        ["^a2j:USB Trigger Finger", "^ardour:MIDI control in"],
        ["^a2j:USB Trigger Finger", "^ardour:Drums"],

        ["^a2j:USB Axiom 61", "^ardour:Keys"],
        ["^a2j:glass_drum", "^ardour:Drums"],

        ["^a2j:glass_cc", "^a2j:sooperlooper"],
        ["^a2j:glass_cc", "^ardour:MIDI control in"],
        ["^a2j:glass_cc", "^Bitrot"],
        ["^a2j:glass_cc", 'C* Eq10X2 - 10-band equalizer:events-in'],

        ["^a2j:glass_drum", "^Hydrogen"],

        ])          

jmatchmkr.run()