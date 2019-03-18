#! /usr/bin/python3

import rtmidi2, pythonosc, jack, sys, time, argparse, subprocess, atexit, re, time, os, random
from pythonosc import dispatcher, osc_server, osc_message_builder, udp_client


def noteout(note, vel, port = 0):
    midiout_inst.send_noteon(144, note, vel)

def bitrot_conv(digit): 
    summ = 6 
    for i in range(digit):
        summ += 3 if (i + 1) % 4 == 0 else 4
    return summ

def mode_switch(mode, num):
    lp.mode = mode
    lp.reset()
    lp.bg_switch(num)
    


def callback_midi(note, time_stamp):
    chan, note, vel = note
    if chan == 176:
        # automap / menu buttons (top row)
        if note == 105 and vel == 127:
            midiout_cc.send_noteon(144, 36, 127)


        elif vel == 127:                
            if note == 111:  # mode switching
                mode_switch("loop", 3)
                
            elif note == 110:
                mode_switch("instrument", 1)

            elif note == 109:
                lp.mode = "sequencer"
                for key in lp.fg_seq:
                    lp.ledout(key[1], key[0], 0, lp.fg_seq[key])
                    
            elif note == 108:
                lp.mode = "loopplay"
                lp.reset()
                slclient.send("/get", ["tempo", "localhost:9998", "/slooptemp"])
            print("mode = ", lp.mode)

    else:  # general input for presses on the grid
        y, x = lp.ingrid[note]  # convert to x, y to output led midi via dict
        #print ('midiin orig', x, y)
        #y = -y + 7
        lpinput.coordinator(x, y, vel)


class Jack_Client():
    def __init__(self):
        self.c = jack.Client('gbeatstation')
        self.c.activate()

class Sequencer():
    def __init__(self, steps):
        self.seq = [[0 for i in range(8)] for x in range(8)]

    def change_step(self, x, y, val):
        self.seq[y][x] = val
        lp.fg_seq[(y, x)] = val
        

class LPad_input():
    def __init__(self):
        self.pressed = {}

    def coordinator(self, x, y, vel):
        '''allocate presses based on current mode '''
        if vel == 127:
            self.pressed[x, y] = time.time()  # for tracking long button presses
        elif vel <= 64:
            elapsed = time.time() - self.pressed[x, y]
            if elapsed > 1 and lp.mode == "loop" and x == 1:
                slclient.send("/sl/{}/down".format(y), "multiply")
                print ('multiply')
            del self.pressed[x, y]

        if lp.mode == "loop":  # mode for controlling sooperlooper
            lpinput.loop(x, y, vel)
        elif lp.mode == "instrument":  # mode for sending midi output            
            lpinput.instr(x, y, vel)
        elif lp.mode == "sequencer" and vel == 127:  # sequencer mode
            lpinput.seq(x, y)
        elif lp.mode == "loopplay":  # for dynamic playback of loops
            lpinput.loopplay(x, y, vel)


    def loopplay(self, x, y, vel):
        '''dynamic repositioning(ish) of loop playback in sooperlooper'''
        if x == 0:
            if vel == 127:
                 slclient.send("/sl/{}/down".format(y), "trigger")
            elif vel <= 64:
                slclient.send("/sl/{}/down".format(y), "pause")
                for i in range(8):
                    lp.ledout(i, y, 0, 0)
        elif x == 1:
            midiout_cc.send_noteon(144, 36, 127) # if vel == 127 else 0)

    def loop(self, x, y, vel):
        '''sooperlooper controls for record, dubbing, pause, reverse, undo/redo,'''
        if x == 2:
            if vel == 127:
                slclient.send("/sl/{}/hit".format(y), "trigger")
            elif vel <= 64:
                if looplist[y].state != 14:
                    slclient.send("/sl/{}/down".format(y), "pause")
                    
                    for i in range(5):
                        lp.ledout(x + i, y, 0, 0)
                    lp.ledout(x - 1, y, 0, 0)
                    lp.ledout(x - 2, y, 0, 0)


        elif x == 8:  # if side controls, quantize on & off
            if vel == 127:  
                if looplist[y].quant == 0:
                    looplist[y].quant = 1
                    lp.ledout(x, y, 0, 1)
                else:
                    looplist[y].quant = 0
                    lp.ledout(x, y, 1, 0)
                q = looplist[y].quant

                slclient.send("/sl/{}/set".format(y), ["sync", q])
                stage_osc.send("/sync/" + str(y), q)
            else:
                lp.ledout(x, y, 0, 0)

        elif vel == 127:  # rest of commands
            if x == 4:  # if paused
                for i in range(8):  # turn off row of leds
                    lp.ledout(i, y, 0, 0)

            if x == 0:
                lp.ledout(x, y, lp.fg[(x, y)][0], lp.fg[(x, y)][1])
                looplist[0].command(x, y)
            elif looplist[y].len > .1:  # problematic if loops shorter than 1
                lp.ledout(x, y, lp.fg[(x, y)][0], lp.fg[(x, y)][1])
                looplist[0].command(x, y)
        elif vel <= 64:
            lp.ledout(x, y, lp.bg1[(x, y)][0], lp.bg1[(x, y)][1])


    def instr(self, x, y, vel):
        '''grid as instrument with midi output'''
        if x < 8:
            midinum = (x + (y * 8) ) + 16
            print ('midi : ', midinum)
            if vel == 127:
                if y > lp.splitpt:
                    noteout(midinum, vel)
                    lp.ledout(x, y, lp.fg[(x, y)][0], lp.fg[(x, y)][1])
                else:
                    looplist[0].command(x, y)
            elif vel <= 64:
                noteout(midinum, 0)
                lp.ledout(x, y, lp.bg0[(x, y)][0], lp.bg0[(x, y)][1])
        elif x == 8 and vel == 127:
            looplist[0].command(0, y)

    def seq(self, x, y,):
        '''sequencer values updater'''
        if Sequence.seq[y][x] == 0:
            Sequence.change_step(x, y, 1)
            lp.ledout(x, y, 1, 2)
        elif Sequence.seq[y][x] == 1:
            Sequence.change_step(x, y, 0)
            lp.ledout(x, y, 0, 0)

class OSC_Sender():
    def __init__(self, ipaddr="127.0.0.1", port=9951):
        self.osc_client = udp_client.SimpleUDPClient(ipaddr, port)

    def send(self, addr, arg):
        self.osc_client.send_message(addr, arg)

num_loops = 0    # change this - should not be a global var!!

class SL_global():
    loopclrsel = 0
    def __init__(self):
        global num_loops
        num_loops += 1
        self.tempo = -1
        self.interval = 5  # not sure if this is working below 10 ms
        self.state_clr = [[0, 0],[1, 0],  # off, waitstart
                         [3, 0], [0, 0],  # recording waitstop
                         [0, 3], [2, 2],  # playing  overdub
                         [1, 1], [0, 0], # multiplying, inserting
                         [0, 0], [0, 0], # "Replacing", "Delay"
                         [0, 0], [0, 0], #"Muted", "Scratching",
                         [1, 2], [0, 0], #"OneShot", "Subsitute",
                         [0, 0]]          # paused

        self.statenames = ["Off", "WaitStart", "Recording", "WaitStop", "Playing", "Overdubbing", "Multiplying",
                           "Inserting", "Replacing", "Delay", "Muted", "Scratching", "OneShot", "Subsitute", "Paused"]

        self.loop_state_rgb = {"Off": [0, 0, 0], "WaitStart": [100, 0, 0], "Recording": [255, 0, 0],
                               "WaitStop": [30, 30, 30], "Playing": [0, 255, 0], "Overdubbing": [130, 130, 0],
                               "Multiplying": [255, 255, 0], "Inserting": [0, 0, 100], "Replacing": [0, 0, 200],
                               "Delay": [0, 100, 200], "Muted": [150, 150, 150], "Scratching": [0, 150, 150],
                               "OneShot": [0, 255, 255], "Subsitute": [0, 0, 255], "Paused": [0, 0, 0]}


        self.cmds = ["record", "overdub", "trigger", "trigger",
                      "pause", "reverse", "undo", "redo"]

    def command(self, x, y):
        if x < 8:
            print (y, self.cmds[x])
            slclient.send("/sl/{}/down".format(str(y)), self.cmds[x])

            if self.cmds[x] == 'reverse':  # not implemented yet
                looplist[y].rev = not looplist[y].rev  # switch True & False

    def track_state(loop, loop_num,  state):
        loop.state = int(state)
        try:
           r, g = loop.state_clr[loop.state]
           lp.ledout(8, loop_num, r, g)
           print (loop_num, r, g)
           
        except IndexError:
            print ("index issue")
            
        stage_osc.send("/loopstate/{}".format(loop_num), looplist[0].loop_state_rgb[looplist[0].statenames[loop.state]])
        
    def track_len(loop, loop_num, length):
            loop.len = length
            seconds = int(loop.len) # on record: lights == # of seconds recorded
            if loop.state == 2:
                if seconds < 8:
                    x, r, g = seconds, 1, 0
                elif seconds < 16:
                    x, r, g = seconds - 8, 2, 0
                elif  seconds < 24:
                    x, r, g = seconds - 16, 3, 0
                else:
                    x = -1
                if x >= 0:
                    lp.ledout(x, loop_num, r, g)
            pass


    def track_pos(loop, loop_num, pos):      
        try:
            loop.pos = pos
            #rel_pos = int(loop.pos / loop.len) if loop.len > 0 else 0
            pos_8th = int(loop.pos / loop.len * 8) if loop.len > 0 else 0 #?
            if pos_8th != loop.eighth_pos and loop.state != 2:    
                    loop.eighth_pos = pos_8th
                    clr_pos = loop.color
                    
                    if pos_8th == 0:
                        lp.ledout(0, 8, 0, 3, rgb = clr_pos)
                        lp.ledout(7, 8, 0, 1) # this can't be set to 0 bc automap on led needs update

                        if lp.mode == "loop":
                            lp.ledout(0, loop_num, 0, 3, rgb=clr_pos)
                            lp.ledout(7, loop_num, 0, 0)
                    else:
                        lp.ledout(pos_8th, 8, 0, 3, rgb=clr_pos)
                        lp.ledout(pos_8th - 1, 8, 0, 1)
                        
                        if lp.mode == "loop":
                            lp.ledout(pos_8th, loop_num, 0, 3, rgb=clr_pos)
                            lp.ledout(pos_8th - 1, loop_num, 0, 0)
                                
                    if loop.seqbase == True:
                        for i in range(8):
                            if pos_8th < 8:
                                if Sequence.seq[i][pos_8th] > 0:
                                    midiout_seq.send_noteon(144, 36 + i, 127)
                                    stage_osc.send("/seq_hits/{}".format(str(i)), [200,30,75])

                                elif Sequence.seq[i][pos_8th - 1] == 0:
                                            stage_osc.send("/seq_hits/{}".format(str(i)), [0,0,0])    

        except KeyError:
            print ('keyerror') #update track length 
            slclient.send("/sl/{}/get".format(loop_num), ["loop_len", "localhost:9998", "/sloop"])
 
class Loop(SL_global):
    def __init__(self, cli):
        SL_global.__init__(self)
        '''autoregisters sooperlooper update vals and stores states'''
        print ('initializing loop #{}'.format(num_loops))

        self.len = 1
        self.pos = 1
        self.eighth_pos = 0
        self.state = 0
        self.rev = False
        self.quant = False
        self.seqbase = False # if this loop is timebase master for the sequencer
        self.color = [random.randint(125,255) for i in range(3)] #randomize loop colors

        # connect to sooperlooper
        cli.send("/sl/{}/register_auto_update".format(num_loops - 1), ["state", self.interval, "localhost:9998", "/sloop"])
        cli.send("/sl/{}/register_auto_update".format(num_loops - 1), ["loop_len", self.interval, "localhost:9998", "/sloop"])
        cli.send("/sl/{}/register_auto_update".format(num_loops - 1), ["loop_pos", self.interval, "localhost:9998","/sloop"])

class Lpad_lights():
    def __init__(self):
        '''class for holding values of color layouts for each mode'''
        automap = []
        self.automap = automap
        for i in range(8):
            automap.append(i + 104)
        # reformat grid midi messages to x,y (0 is bottom row)
        self.ingrid = {0: (7, 0), 1: (7, 1), 2: (7, 2), 3: (7,3), 4: (7, 4), 5: (7, 5), 6: (7, 6), 7: (7, 7), 8: (7, 8),
                   16: (6, 0), 17: (6, 1), 18: (6, 2), 19: (6, 3), 20: (6, 4), 21: (6, 5), 22: (6, 6), 23: (6, 7), 24: (6, 8),
                   32: (5, 0), 33: (5, 1), 34: (5, 2), 35: (5, 3), 36: (5, 4), 37: (5, 5), 38: (5, 6), 39: (5, 7), 40: (5, 8),
                   48: (4, 0), 49: (4, 1), 50: (4, 2), 51: (4, 3), 52: (4, 4), 53: (4, 5), 54: (4, 6), 55: (4, 7), 56: (4, 8),
                   64: (3, 0), 65: (3, 1), 66: (3, 2), 67: (3, 3), 68: (3, 4), 69: (3, 5), 70: (3, 6), 71: (3, 7), 72: (3, 8),
                   80: (2, 0), 81: (2, 1), 82: (2, 2), 83: (2, 3), 84: (2, 4), 85: (2, 5), 86: (2, 6), 87: (2, 7), 88: (2, 8),
                   96: (1, 0), 97: (1, 1), 98: (1, 2), 99: (1, 3), 100: (1, 4), 101: (1, 5), 102: (1, 6), 103: (1, 7), 104: (1, 8),
                   112: (0, 0), 113: (0, 1), 114: (0, 2), 115: (0, 3), 116: (0, 4), 117: (0, 5), 118: (0, 6), 119: (0, 7), 120: (0, 8)}

        self.outgrid = {v: k for k, v in self.ingrid.items()}
        

        self.highbound = 67
        self.lowbound = 16
        self.mode = 0
        self.splitpt = -1

        self.fg = {}  # foreground
        for k in self.outgrid:
            self.fg[k] = 0, 3

        self.bg0 = self.fg.copy()  # background #0
        for r in range(4): # colorful, ordered background for instr mode
            for c in range(4):
                self.bg0[(r, c)] = [-r + 3, -c + 3]
                self.bg0[(r + 4, c)] = [r, -c + 3]
                self.bg0[(r, c + 4)] = [-r + 3, c]
                self.bg0[(r + 4, c + 4)] = [r, c]


        self.bg1 = self.fg.copy()  # background #1
        self.bg2 = self.fg.copy()  # background #2
        self.fg_seq = self.fg.copy()  # foreground for sequencer
        self.led_cur = self.fg.copy()

        for idx in self.led_cur:
            self.led_cur[idx] = 0, 0
            self.fg_seq[idx] = 0

        self.layer_sel = [self.fg, self.bg0, self.bg1, self.bg2]  # mode select

    def reset(self):
            midiout_lp.send_noteon(176, 0, 0)
            for i in range(64):
                stage_osc.send("/textmat/" + str(i), " ")
                stage_osc.send("/griddy/" + str(i), [0, 0, 0])
                if i < 8: stage_osc.send("/automap_text/" + str(i), " ")
                
                

    def ledout(self, x, y, r, g, rgb=None):
        if (x, y) in self.led_cur:
            if self.led_cur[x, y] != (r, g):
                button = str(x + (8 * y))
                if rgb: # for updated/ full color val functions 
                    color = rgb
                else:
                    color = [r * 85 , g * 85, 0]
                if y < 8:  # if not an automap button, midiout on channel 144
                    midiout_lp.send_noteon(144, lp.outgrid[y, x], self.ledcol(r, g))
                    #print ('orig', lp.outgrid[y, x], "revert", )#lp.outgrid[-(y + 8))
                    #midiout_lp.send_noteon(144, ( (y-1) << 4) | x, self.ledcol(r, g))
                    stage_osc.send("/griddy/{}".format(button), color)
                    if x == 8:
                        pass
                    self.led_cur[x, y] = r, g
                    
                elif y == 8:  # if automap, noteon must be on channel 176 instead
                    midiout_lp.send_noteon(176, lp.automap[x], self.ledcol(r, g))
                    stage_osc.send("/automap/{}".format(x), color)
            

    def ledcol(self,red, green):
        led = 0
        red = min(int(red), 3)  # make int and limit to <=3
        red = max(red, 0)       # no negative numbers
        green = min(int(green), 3)  # make int and limit to <=3
        green = max(green, 0)      # no negative numbers
        led |= red
        led |= green << 4
        return led

    def monochrome(self, layer, red, green): # to make layers one color
        layer = lp.layer_sel[layer]
        for i in layer:
            layer[i] = [red, green]

    def bg_switch(self, selection):
        '''background selection & update values'''
        newbg = self.layer_sel[selection]

        for buttons in newbg:
            if buttons[1] < 8 and buttons[0] < 8:
                try:
                    lp.ledout(buttons[0], buttons[1], newbg[buttons][0], newbg[buttons][1])
                except KeyError:
                    print ('automap')

def slosc_handler(*args):  # osc from sooperlooper
    loop = looplist[args[1]]
    if args[2] == "out_peak_meter":
        stage_osc.send("/peakmtr/" + str(args[1]), args[-1])
        print (("/peakmtr/" + str(args[1]), args[-1]))
    if args[2] == "loop_pos":
        Loop.track_pos(loop, args[1], args[3])
    if args[2] == "state":  # update state in any mode
        Loop.track_state(loop, args[1], args[3])
    
    elif lp.mode == "loop" or lp.mode == "loopplay":
        loop = looplist[args[1]]
        loop_num = args[1]
        if args[0] == '/sloop':
            if args[2] == 'loop_len':
                Loop.track_len(loop, loop_num, args[3])
            elif args[2] == 'loop_pos':
                Loop.track_pos(loop, loop_num, args[3])
            elif args[2] == 'tempo':
                tempo = int(args[-1])
                SL_global.tempo = tempo # update global tempo

                if tempo > 10: #bitrot midi-tempo
                    midiout_cc.send_noteon(144, 36, int(tempo/3.75)) # via ardour midi learn
                    midiout_cc.send_noteon(176, 2, int(tempo/3.75))  # via carla file assigned
        

    #else:
     #   print (args)
        
def slosc_handler2(*args):
    if args[0] == "/slooptemp":
        tempo = int(args[-1])
        
        midiout_cc.send_messages(176, [(0, 1, temp)])

def stage_handler(*args):  # osc from open stage control
    if args[0][:8] == "/beatpad":  # open-stage-c matrix - emulation of launchpad
        button = int(args[0][9:])
        vel = args[-1] * 127
        x = button % 8
        y = 0 if button < 8 else int(button / 8)
    
        lpinput.coordinator(x, y, vel)  # button outputs identical to launchpad


    elif args[0][:5] == "/sync":  # quantize individual loops        
        loopnum, val = args[0][6], args[-1]
        print (loopnum, val)
        slclient.send("/sl/{}/set".format(loopnum), ["sync", args[-1]])


    elif args[0] == "/quantize":  # choose global? cycle size
        slclient.send("/sl/0/set", ["quantize", args[1]])

    elif args[0] == "/globalsync":  # global sync sync source
        slclient.send("/set", ["sync_source", args[-1]])

    elif args[0] == "/mode":  # change mode
        modelist = ["loop", "instrument", "sequencer", "loopplay"]
        lp.mode = modelist[args[-1]]

        if lp.mode == "loop":
            for i in range(64):
                txtlist = looplist[0].cmds
                txtlist[2] = "oneshot"
                stage_osc.send("/textmat/" + str(i), txtlist[i % 8])
        else:
            for i in range(64):
                stage_osc.send("/textmat/" + str(i), " ")
                
        if lp.mode == "loop":
            lp.bg_switch(3)
            print ('mode = ', lp.mode)

        elif lp.mode == "instrument":
            lp.bg_switch(1)

        
        elif lp.mode == "sequencer":
            for key in lp.fg_seq:
                    lp.ledout(key[1], key[0], 0, lp.fg_seq[key])

        #this should be moved into a proper 'modeswitch' function'
        

    elif args[0] == "/cycle":  # set cycle length for quantization
        slclient.send("/set", ["eighth_per_cycle", args[-1]])

    elif args[0] == "/common_ins":  # use common ins (per each loop)
        slclient.send("/sl/{}set".format(args[1]), ["use_common_ins", args[-1]])

    elif args[0][:6] == "/fader":
        vel = int(args[1] * 127)
        note = int(args[0][7])
        midiout_cc.send_noteon(144, note, vel) # send fader controls to EQ

    elif args[0] == "/bitbeats":
        midiout_cc.send_noteon(144, 38, args[-1])

    elif args[0][:6] == "/mutes":
        print (args[0][:6], args[0][-1])
        loop = int(args[0][-1])
        print (looplist[loop].state)
        if looplist[loop].state == 4 or 10:
            print('sendinggggg')
            slclient.send("/sl/{}/hit".format(args[0][-1]), "mute")

    elif args[0][:4] == "/xy":
        pt0 = args[1:4]
        pt1 = args[4:7]
        pt2 = args[7:10]
        pt3 = args[10:13]
        x1, y1 = pt0[0], pt0[1]
        x1, y1 = int(x1 * 8/ 127), int(y1 * 8/ 127)
        x1 = -x1 + 8
        gridxy = x1 + (y1 * 8)
        gridxy = -gridxy + 64
        stage_osc.send("/xyrgb/" + str(gridxy), [80, 80, 80])

    elif args[0][:5] == "/save":
        md = cwd[:14]
        #nwd
        #os.mkdir(  # change save dir
        slclient.send("/save_session", [time.asctime(), "localhost:9998", "error_path"])
        for i in range(8):
            slclient.send("/sl/{}/save_loop".format(str(i)), [time.asctime() + "+loop" + str(i) + ".wav", "32", "endian", "localhost:9998", "error_path"])

    elif args[0][:9] == "/bittempo":
        midiout_cc.send_noteon(176, 2, args[-1])  # via carla file assigned
        client.connect(["sooperlooper:common_out_1", "system:playback_1"])
        
    elif args[0][:7] == "/fxgrid":
        button = int(args[0][8:])
        vel = args[-1] * 127
        x = int((button % 8) * 18)
        y = 0 if button < 8 else int((button / 8) * 18)
        print (x,y)
        midiout_cc.send_noteon(176, 3, y) 
        midiout_cc.send_noteon(176, 4, x)
        midiout_cc.send_noteon(176, 1, args[-1] * 127)  # via carla file assigned

    elif args[0] == "/patch":
        inport = inport = "sooperlooper:{}_".format(args[1])
        
        if args[1] == "common":
            outport = "system:playback_"
        elif args[1] == "Dac": outport = "Bitrot Repeat:Audio Input "
        print (inport)    
        if len(args) > 2:            
            outports = []
            for port in args[2:]:
                if port == "dac":
                    outports.append("system:playback_")
                elif port == "bitrot":
                    outports.append("Bitrot Repeat:Audio Input ")
            # FOR TEST CASE, 2 ALREADY CONNECTED AND 1 NEEDS TO BE DISCONNECTED IMPLEMENT HERE
            for p in outports:
                for i in range(1,3):
                    try:    
                        client.connect("sooperlooper:{}_{}".format(args[1], str(i)), p + str(i))
                    except:  # will replace this hideousness with tracking already made connections
                          print ('already connected') #instead of brute forcing
                    try:
                        client.connect("sooperlooper:{}_{}".format(args[1], str(i)), p + str(i))
                    except:
                        print ('already connected')
                 
        elif len(args) == 2:
            outport1, outport2 = "system:playback_", "Bitrot Repeat:Audio Input "
            for port in outport1, outport2:
                for i in 1,2:
                        print (inport, port)
                        client.disconnect(inport + str(i), port + str(i))

    elif args[0] == "/loop_rgb":
        print (looplist[SL_global.loopclrsel].color)
        looplist[SL_global.loopclrsel].color = args[1:]


    elif args[0] == "/loopclrsel":
        print (SL_global.loopclrsel)
        SL_global.loopclrsel = args[-1]
        print (SL_global.loopclrsel)

         
    else:
        print ('no handler for : ', args)
    '''
  input_latency :: range 0 -> ...
  output_latency :: range 0 -> ...
  trigger_latency :: range 0 -> ...
  autoset_latency  :: 0 = off, not 0 = on

  cycle_len :: in seconds
  free_time :: in seconds
  total_time :: in seconds
  rate_output 
  in_peak_meter  :: absolute float sample value 0.0 -> 1.0 (or higher)
  out_peak_meter  :: absolute float sample value 0.0 -> 1.0 (or higher)
  is_soloed       :: 1 if soloed, 0 if not'''
              

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",  # make arguments for both server and client
        default="localhost", help="The ip to listen on")
    parser.add_argument("--port",
        type=int, default=9998, help="The port to listen on")
    args = parser.parse_args()
    cwd =  "/home/acepath/dev/glassbeats/glass_beatstation" #os.getcwd() #initiate python from cwd
    print (cwd)

    #init without the gui, but can run slgui after the fact and will run on same engine
    carla = subprocess.Popen(["carla", cwd + "/glass_car.carxp", "-n"], stdout=subprocess.PIPE) #  "-n" to run headless

    slgui = subprocess.Popen(["sooperlooper", "-l 8", "-m", cwd + "/sl_bindings.slb"], stdout=subprocess.PIPE)  # start sooperlooper
    
    stagecontrol = subprocess.Popen(["open-stage-control","-l", cwd + "/stagecontrol.json",  # initiate stagecontrol with midi ports
    "-s", "127.0.0.1:9998", "-t", "orange", "-m", "open-stage_cc:virtual", "open-stage_keys:virtual", "-d"], stdout=subprocess.PIPE) 

    #pd = subprocess.Popen(["puredata", "-jack", "-inchannels", "8", "midi_2_o-s-c.pd"])

    jackmatch = subprocess.Popen(["jack-matchmaker", # start jack-matchmaker
                "^a2j:lp-leds", "^Launchpad",
                "^Launchpad", "^a2j:RTMIDI",
                  "^a2j:open-stage_keys", "^ardour:midinstrument",
                  "^a2j:lp-instrument", "^ardour:MIDI Synth",
                  "^jack_trans_out", "^ardour:Drums/midi",
                  "^a2j:lp-cc", "ardour:MIDI control in",
                  "^a2j:lp-seq", "^ardour:Drums",
                "^a2j:open-stage_cc", "^Bitrot",
                "^a2j:lp-cc", "^Bitrot",                                  
                "^a2j:open-stage_cc", "^a2j:sooper", #working?               
                "alsa_in:capture_1", "sooperlooper:common_in_1",
                "alsa_in:capture_2", "sooperlooper:common_in_2",
                "zynaddsubfx:out_1", "sooperlooper:common_in_1",
                "zynaddsubfx:out_2", "sooperlooper:common_in_2",
                "^a2j:lp-instrument", "zynaddsubfx:midi_input",
                "-m 1"], stdout=subprocess.PIPE)

    time.sleep(2)  # let sooperlooper engine finish starting


    midi_in = rtmidi2.MidiIn()  # midiinput - begin callback
    midi_in.callback = callback_midi

    try:
        midi_in.open_virtual_port("input from launchpad")
    except ValueError:
        print ('port not found')

    # midioutputs
    midiout_lp = rtmidi2.MidiOut("lp-leds")
    midiout_lp.open_virtual_port("lp-leds")

    midiout_inst = rtmidi2.MidiOut('lp-instrument')  #"RtMidi-Instrument")
    midiout_inst.open_virtual_port('lp-instrument') #"RtMidi-Instrument")

    midiout_cc = rtmidi2.MidiOut('lp-cc')  # controls for plugins
    midiout_cc.open_virtual_port('lp-cc')

    midiout_seq = rtmidi2.MidiOut('lp-seq')  # sequencer output
    midiout_seq.open_virtual_port('lp-seq')

    

    slclient = OSC_Sender()  # connect to sooperlooper
    #.send("/load_midi_bindings", [cwd + "/sl_bindings.slb"]) #not currently working
    stage_osc = OSC_Sender(ipaddr="127.0.0.1", port=8080)  # open stage control
    pd_osc = OSC_Sender(ipaddr="127.0.0.1", port=9111)  # to puredata
    clientele = OSC_Sender(ipaddr="127.0.0.1", port=9997)
    looplist = [Loop(slclient) for i in range(8)]

    # osc server handlers
    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/sloop", slosc_handler)  # sooperlooper handler
    dispatcher.map("/slooptemp", slosc_handler2)

    #osc from openstage, default because it has many prefixes used
    dispatcher.set_default_handler(stage_handler)
    
    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), dispatcher)
    print("OSC server on {}".format(server.server_address))

    slclient.send("/register_auto_update", ["tempo", 10, "localhost:9998", "/sloop"])

    lp = Lpad_lights()
    lp.monochrome(0, 0, 3) #foreground fill with green
    lp.monochrome(3, 0, 0) #background blank
    lp.monochrome(2, 0, 0) #background2 blank

    lpinput = LPad_input()  # initialize input class

    Sequence = Sequencer(8)

    for i in range(3):  #
        lp.bg_switch(i)
        time.sleep(.3)


    try:    
        client = jack.Client('glassbeats')
    except jack.JackError:
        sys.exit('JACK server not running?')

    connections = [
    ["sooperlooper:common_out_1", "Bitrot Repeat:Audio Input 1"],
    ["sooperlooper:common_out_2", "Bitrot Repeat:Audio Input 2"],
    #["sooperlooper:common_out_1", "ardour:sooperlooper/audio_in 1"],
    #["sooperlooper:common_out_2", "ardour:sooperlooper/audio_in 2"],
    ["lp-seq", "Hydrogen:Hydrogen Midi-In"],
    ["Hydrogen:out_L", "ardour:Drums/audio_in 1"],
    ["Hydrogen:out_R", "ardour:Drums/audio_in 2"],
    ["ardour:midinstrument/audio_out 1", "sooperlooper:common_in_1"],
    ["ardour:midinstrument/audio_out 2", "sooperlooper:common_in_2"],
    ["ardour:Mic/audio_out 2", "sooperlooper:common_in_1"],
    ["ardour:Mic/audio_out 2", "sooperlooper:common_in_2"],
    ["ardour:Guitar/audio_out 2", "sooperlooper:common_in_1"],
    ["ardour:Guitar/audio_out 2", "sooperlooper:common_in_2"],
    ["lp-cc", "Bitrot Repeat:events-in"],
    ["open-stage-cc", "Bitrot Repeat:events-in"],
    ]


    for i in range(8):
        for s in range(1,3):
            connections.append(["sooperlooper:loop{}_out_{}".format(str(i),str(s)), "pure_data_0:input" + str(i)])
    

    for i in range(len(connections)):
        try:
            client.connect(*connections[i])
            print('connecting : ', connections[i])
        except jack.JackError:
            print ('fail', connections[i])

    looplist[0].seqbase = True
    
  

    def exit_handler():
        print ("exiting")
        lp.reset()  # button flush
        jackmatch.terminate()
        slgui.terminate()
        carla.terminate()
        #stagecontrol.terminate()  #why close when it takes time to open?



    time.sleep(1.5)
    lp.reset()
    
    mode_switch("loop", 3)
    
    atexit.register(exit_handler)
    server.serve_forever()  # blocking osc server
