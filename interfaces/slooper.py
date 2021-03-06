import random
from collections import OrderedDict


class Slmaster():
    loop_num = 0
    interval = 10

    def add_loop(self):
        pass

    def __init__(self, Grid, oscclient, Sequencer):
        self.Seq = Sequencer
        self.slclient = oscclient
        self.Grid = Grid
        self.tempo = -1
        self.seqmaster = 0 #which loop is timebase master for the sequencer
        self.states = OrderedDict([("Off", [0,0,0]),
                                ("WaitStart", [30,0,63]), #pulsings??
                                ("Recording", [63,0,0]),
                                 ("WaitStop", [63,0,30]), #pulse
                                 ("Playing", [0,63,0]), #4
                                ("Overdubbing", [40,40,0]),
                                 ("Multiplying", [63,63,0]),
                                 ("Inserting", [0,60,30]),
                                 ("Replacing", [0,30,60]),
                                ("Delay", [0,0,0]),
                                 ("Muted", [10,10,10]),  # 10
                                  ("Scratching", [0,0,40]), 
                                   ("OneShot", [0,63,63]),
                                    ("Subsitute", [0,50,63]),
                                     ("Paused", [0,5,20])])#blink
                                  
        self.stateslst = list(self.states.items())

        self.cmds = ["record", "overdub", "oneshot", "trigger",
                      "pause", "reverse", "undo", "redo"]


        oscclient.send("/register_auto_update", ["tempo", 10, "localhost:9998", "/sloop"])


        self.loops = None #updated in main
        self.clrs = [
            [63,63,63],
            [0,63,63],
            [0,63,0],
            [0,20,63],
            [63,30,0],
            [0,0,63],
            [40,63,40],
            [20,40,60],
            ]
        self.funcs = {"state":self.track_state, "loop_len":self.track_len, "loop_pos":self.track_pos}

    def color_change(self, loop_num, color):
        print (loop_num, color)
        self.loops[loop_num].color = color

    def sl_osc_cmd(self, prefix, args):
        self.slclient.send(prefix, args)

    def track_state(self, loopobj, state):
        if loopobj.state != state: # if different than previous state
            
            if int(state) == 14 and loopobj.state != 4 or int(state) == 4 and loopobj.state == 2: # if paused and last state was playing
                if self.Grid.mode == "rand":
                    if loopobj.loop_num > 4:
                        for x in range(4): self.Grid.ledout(x, loopobj.loop_num, [0,0,0])
                elif self.Grid.mode == "loop":
                    for x in range(8):
                        self.Grid.ledout(x, loopobj.loop_num, [0,0,0])
             


            
            loopobj.state = int(state)
            print ('***'*20, self.stateslst[loopobj.state])
            clr = (self.stateslst[loopobj.state][1])
            self.Grid.ledout(8, loopobj.loop_num, clr)

    def track_len(self, loopobj, length):
        if loopobj.len != length:
            loopobj.len = length
            seconds = int(length)
            y = loopobj.loop_num
            if self.Grid.mode == "instr": pass
            elif self.Grid.mode == "rand" and y < 4: pass
            else:
                if int(loopobj.state) == 2:
                    if seconds < 8:
                        x = seconds
                        clr = [63,0,0]
                        code = 72
                    elif seconds < 16:
                        x = seconds - 8
                        clr = [40,0,0]
                        code = 106
                    elif  seconds >= 16:
                        x = seconds - 16
                        clr = [10,0,0]
                        code = 6
                    else:
                        x = seconds % 8

                    if seconds >= 0:
                        self.Grid.ledout(x, loopobj.loop_num, clr, var=["pulse", code])

    def track_pos(self, loopobj, pos):
        lp = loopobj
        lp.pos = pos
        if lp.rev == True:
            pass
        
        pos_8th = int(lp.pos / lp.len * 8) if lp.len > 0 else 0
        y = lp.loop_num            
        Grid = self.Grid
        if pos_8th != lp.pos_eighth:
            print (pos_8th, lp.state)

            
            if pos_8th > 8:  # if out of range, make sure length is updated
                self.slclient.send("/sl/{}/get".format(str(y)), ["loop_len", "localhost:9998", "/sloop"])

            lp.pos_eighth = pos_8th

            if pos_8th == 0 and lp.state == 2:
                self.Seq.check_step(0)

            if lp.state in [4,5,6,10,12]: #if in one of the playing states
                
                if y == 7: #correct to seqmaster
                    self.Seq.check_step(pos_8th)
                
                if pos_8th == 0:
                    Grid.ledout(0, 8, lp.color)
                    Grid.ledout(7, 8, [0,0,0])

                    if Grid.mode == "loop" or  Grid.mode == "rand" and y > 3:
                        Grid.ledout(0, y, lp.color)
                        Grid.ledout(7, y, Grid.pgrid[7,y]["loop"][False])

                else:
                    Grid.ledout(pos_8th, 8, lp.color)
                    Grid.ledout(pos_8th - 1, 8, [0,0,0])


                    if Grid.mode == "loop" or  Grid.mode == "rand" and y > 3:
                        Grid.ledout(pos_8th, y, lp.color)
                        Grid.ledout(pos_8th - 1, y, Grid.pgrid[pos_8th - 1, y]["loop"][False])


    def sloschandler(self, *args):
        if args[2] == 'tempo':
            print ('tempo', args[2])
            self.tempo = args[2]

        elif isinstance(args[1], str) == True:
            print (args[1][:4])
            if args[1][:4] == 'osc':
                print ('ping! - # of loops : ', args[-1])

            else:
                print ('random slosc', args)

            
        else:

            invloop = args[1]
            loop_num = invloop
            if loop_num < 8: #if one of the first 8 loops
                loopobj = self.loops[loop_num]
                param, value = args[2], args[3] 
                if param != "loop_len" and value > 40:
                    print("loop #", loop_num, param, value, "has not been recorded yet")
                else:
                    self.funcs[param](loopobj, value)
            else:
                print (args)

class Sloop(Slmaster):
    def __init__(self, grid, oscclient):
        '''individual sooperlooper tracking states, position'''
        self.loop_num = Slmaster.loop_num
        print ('initializing loop #{}'.format(self.loop_num))
        self.pos = -1
        self.pos_eighth = -2
        self.len = -1
        self.state = 0
        self.sync = False
        self.rev = False
        clrs = [
            [20,40,60],
            [40,63,40],
            [0,63,63],
            [63,30,0],
            [20,50,63],
            [0,63,63],
            [0,0,63],
            [63,63,63], ]
        self.color = clrs[self.loop_num]
        for x in range(8):
            grid.pgrid[x, self.loop_num]["loop"][True] = self.color
            grid.pgrid[x, self.loop_num]["loop"][False] = [0,0,0]#self.colors
        intrvl = Slmaster.interval
        # connect to sooperlooper, autoreg updates for state, length, and position
        oscclient.send("/sl/{}/register_auto_update".format(self.loop_num), ["state", intrvl, "localhost:9998", "/sloop"])
        oscclient.send("/sl/{}/register_auto_update".format(self.loop_num), ["loop_len", intrvl, "localhost:9998", "/sloop"])
        oscclient.send("/sl/{}/register_auto_update".format(self.loop_num), ["loop_pos", intrvl, "localhost:9998","/sloop"])
        Slmaster.loop_num += 1

