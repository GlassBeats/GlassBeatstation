import jackmatchmaker

jmatchmkr = jackmatchmaker.JackMatchmaker([
        ["^a2j:mk2", "^Launchpad"],
        ["^Launchpad", "^a2j:mk2"],

        ["^a2j:open-stage_cc", "^Bitrot"],
        ["^a2j:open-stage_cc", "^sooperloop"],

        ["zynaddsubfx:out_1", "sooperlooper:common_in_1"],
        ["zynaddsubfx:out_2", "sooperlooper:common_in_2"],

        ["Hydrogen:out_L", "sooperlooper:common_in_1"],
        ["Hydrogen:out_R", "sooperlooper:common_in_2"],

        ["sooperlooper:common_out_1", "Bitrot Repeat:Audio Input 1"],
        ["sooperlooper:common_out_2", "Bitrot Repeat:Audio Input 2"],




        ["^a2j:glass_instr","^zynaddsubfx:midi_input"],


        ['^a2j:Pure Data', # [132] (capture): Pure Data Midi-Out 1',
         '^a2j:Hydrogen'], # [131] (playback): Hydrogen Midi-In'],


        
        ["^a2j:glass_cc", "^sooperlooper"],
        ["^a2j:glass_cc", "^Bitrot"],
        ["^a2j:glass_cc", 'C* Eq10X2 - 10-band equalizer:events-in'],

        ["^a2j:glass_drum", "^Hydrogen"],

        ])          
     
    
#jackmatchmaker.main("-v")
jmatchmkr.run()
