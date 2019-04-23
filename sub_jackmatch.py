import jackmatchmaker

jmatchmkr = jackmatchmaker.JackMatchmaker([
        ["^a2j:mk2", "^Launchpad"],
        ["^Launchpad", "^a2j:mk2"],

        ["^a2j:open-stage_cc", "^Bitrot"],
        ["^a2j:open-stage_cc", "^sooperloop"],

        ["zynaddsubfx:out_1", "sooperlooper:common_in_1"],
        ["zynaddsubfx:out_2", "sooperlooper:common_in_2"],                

        ["^a2j:glass_instr","^zynaddsubfx:midi_input"],
        ["sooperlooper:common_out_1", "Bitrot:Audio Input 1"],
        ["sooperlooper:common_out_2", "Bitrot:Audio Input 2"],
        
        ["^a2j:glass_cc", "^sooperlooper"],
        ["^a2j:glass_cc", "^Bitrot"],

        ["^a2j:glass_drum", "^Hydrogen"],

        ])          
     
    
#jackmatchmaker.main("-v")
jmatchmkr.run()