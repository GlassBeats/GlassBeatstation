DEPENDENCIES:

Jack audio
    http://jackaudio.org/downloads/
    
Python 3 (all available via pip3:)
    pip3 install jack-Client
    pip3 install rtmidi2
    pip3 install python-osc
    pip3 install jack-matchmaker
    
Open Stage Control 0.41.4
    https://osc.ammd.net/
    or
    https://github.com/jean-emmanuel/open-stage-control
    
Sooperlooper 1.7.3
    http://essej.net/sooperlooper/download.html
    or
    https://github.com/essej/sooperlooper
    
Hydrogen (optional - used for jack sync - sequencer will not work without):
    http://hydrogen-music.org/downloads/
    
Ardour (optional - other lv2 hosts can be used for instrumentation and bitrot
    https://community.ardour.org/download  
    (costs $50 or must be compiled - but I suggest downloading the kxstudio repos which contains it already)
 
USAGE: (must be run in seperate terminals simultaneously)
    python3 gbeatstation_main.py
    python3 jacktransporter.py
    
    
can use a variety of programs to route audio/midi to your liking. I recommend catia from the kxstudio repos for it's simplicity and patchbay style, but I believe qjackctl is quite commonly used as well






also credit to the project https://github.com/FMMT666/launchpad.py - the ledcolor function to map color levels to correct midi numbers and the function to organize the grid into xy coordinates