import random
from collections import OrderedDict


class Slmaster():
    loop_num = 0
    interval = 5
    def __init__(self, Grid, oscclient):
        self.slclient = oscclient
        self.Grid = Grid
        self.tempo = -1
        self.seqmaster = 0 #which loop is timebase master for the sequencer
        self.states = OrderedDict([("Off", [0,0,0]),
                                ("WaitStart", [40,0,63]), #pulsings??
                                ("Recording", [63,0,0]),
                                 ("WaitStop", [63,0,40]), #pulse
                                 ("Playing", [0,63,0]), #4
                                ("Overdubbing", [40,40,0]),
                                 ("Multiplying", [63,63,0]),
                                 ("Inserting", [30,30,30]),
                                 ("Replacing", [30,30,30]),
                                ("Delay", [0,0,0]),
                                 ("Muted", [10,10,10]),  # 10
                                  ("Scratching", [0,0,40]), 
                                   ("OneShot", [0,63,63]),
                                    ("Subsitute", [30,30,30]),
                                     ("Paused", [0,5,20])])#blink
                                  
        self.stateslst = list(self.states.items())

        self.cmds = ["record", "overdub", "oneshot", "trigger",
                      "pause", "reverse", "undo", "redo"]


        oscclient.send("/register_auto_update", ["tempo", 10, "localhost:9998", "/sloop"])

        self.invlps = [Sloop(Grid, oscclient) for i in range(8)]
        self.loops = self.invlps[::-1]

        self.funcs = {"state":self.track_state, "loop_len":self.track_len, "loop_pos":self.track_pos}

    def sl_osc_cmd(self, prefix, args):  # necessary for scoping purposes perhaps
        self.slclient.send(prefix, args)
        


    def track_state(self, loopobj, state):
        if loopobj.state != state:
            loopobj.state = int(state)
            print ('hhhhh', loopobj.state)
            print (self.stateslst[loopobj.state])
            clr = (self.stateslst[loopobj.state][1])
            self.Grid.ledout(8, loopobj.loop_num, clr)
            #if loopobj.state == 4:
            #    for i in range(8):
            #        # add feature: if not in 'pressed'
            #        y = -loopobj.loop_num + 7
            #        loopclr = self.Grid.pgrid[i, y][self.Grid.mode][False]
            #        self.Grid.ledout(i, y, loopclr)
            

    def track_len(self, loopobj, length):

        print ('*' * 20, length)
        if loopobj.len != length:
            
            loopobj.len = length
            seconds = int(length)
            if int(loopobj.state) == 2: #change state val to "recording"
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
            if pos_8th > 8:
                oscclient.send("/sl/{}/get".format(str(y)), ["loop_len", "localhost:9998", "/sloop"])

            lp.pos_eighth = pos_8th

            if lp.state in [4,5,6,10,12]: #if in one of the playing states
                
                if pos_8th == 0:  # reconfigure to display oneshots ^^ 12d
                    Grid.ledout(0, 8, lp.color)
                    Grid.ledout(7, 8, [0,0,0])

                    if Grid.mode == "loop":
                        Grid.ledout(0, y, Grid.pgrid[0,y]["loop"][True])
                        Grid.ledout(7, y, Grid.pgrid[7,y]["loop"][False])

                else:
                    Grid.ledout(pos_8th, 8, lp.color)
                    Grid.ledout(pos_8th - 1, 8, [0,0,0])


                    if Grid.mode == "loop":
                        Grid.ledout(pos_8th, y, Grid.pgrid[pos_8th,y]["loop"][True])
                        Grid.ledout(pos_8th - 1, y, Grid.pgrid[pos_8th - 1,y]["loop"][False])


    def sloschandler(self, *args):
        if args[2] == 'tempo':
            print ('tempo', args[2])
            self.tempo = args[2]
        elif isinstance(args[1], str) == True:
            print ('random slosc', args)

            
        else:
            invloop = args[1]
            loop_num = invloop
            loopobj = self.loops[loop_num]
            param, value = args[2], args[3] # args[1:]
            if int(value) == 20:
                print ('xxxxxx', param, value)
            else:
                self.funcs[param](loopobj, value) # these could be more in parallel?
                
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
        #self.quant = False
        self.color = [random.randint(25,63) for i in range(3)] #randomize loop colors
        for x in range(8):
            grid.pgrid[x, self.loop_num]["loop"][True] = [63, 63, 63] #self.color
            grid.pgrid[x, self.loop_num]["loop"][False] = self.color #[0,0,0]#[63, 63, 63]#[int(c / 1.5) for c in self.color]
        # avoid ifelse, prevent 'x/ 0'
        intrvl = Slmaster.interval
        # connect to sooperlooper, autoreg updates for state, length, and position
        oscclient.send("/sl/{}/register_auto_update".format(self.loop_num), ["state", intrvl, "localhost:9998", "/sloop"])
        oscclient.send("/sl/{}/register_auto_update".format(self.loop_num), ["loop_len", intrvl, "localhost:9998", "/sloop"])
        oscclient.send("/sl/{}/register_auto_update".format(self.loop_num), ["loop_pos", intrvl, "localhost:9998","/sloop"])
        Slmaster.loop_num += 1

