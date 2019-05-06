import time, os, re

class OpenStageControl():
    def __init__(self, Grid, coord, Slobj, stage_osc_cli, midicc, jack):
        self.jack = jack
        self.Grid = Grid
        self.Slmast = Slobj
        self.stage_osc = stage_osc_cli
        self.coord = coord
        self.send = stage_osc_cli.send
        self.glass_cc = midicc

        self.x0, self.y0, self.p0 = 0, 0, 0

        self.portnames = {'fx in':"Bitrot Repeat:Audio Input ",
                          'fx out': "Bitrot Repeat:Audio Output ",
                          'common_out':'sooperlooper:common_out_',
                          'common_in': 'sooperlooper:common_in_',
                          'dac':'system:playback_'}
        for p in range(8):
            self.portnames['loop{}_out'.format(str(p))] = "sooperlooper:loop{}_out_".format(str(p))
            self.portnames['loop{}_in'.format(str(p))] = "sooperlooper:loop{}_in_".format(str(p))

    def stage_handler(self, *args):
        Grid = self.Grid
        send = self.send
        if args[0][:8] == "/beatpad":  # open-stage-c matrix - emulation of launchpad
            button = int(args[0][9:])
            vel = args[-1]
            x = button % 8
            y = 0 if button < 8 else int(button / 8)
            y = -y + 7
        
            self.coord(x, y, vel)  # button outputs identical to launchpad

        elif args[0][:14] == '/automap_push/':
                button = int(args[0][14:])
                vel = args[-1]
                print('automap', vel)
                self.coord(button, 8, vel)

        elif args[0][:13] == '/column_push/':
                invbutton = int(args[0][13:])
                button = -invbutton + 7
                vel = args[-1]
                print('column', vel)
                self.coord(8, button, vel)


        elif args[0][:5] == "/sync":  # quantize individual loops        
            loopnum, val = args[0][6], args[-1]
            self.Slmast.loops[loopnum].sync = val
            self.Slmast.sl_osc_cmd("/sl/{}/set".format(loopnum), ["sync", val])


        elif args[0] == "/quantize":  # choose global? cycle size
            self.Slmast.sl_osc_cmd("/sl/0/set", ["quantize", args[1]])

        elif args[0] == "/globalsync":  # global sync sync source
            self.Slmast.sl_osc_cmd("/set", ["sync_source", args[-1]])


        elif args[0] == "/cycle":  # set cycle length for quantization
            self.Slmast.sl_osc_cmd("/set", ["eighth_per_cycle", args[-1]])

        elif args[0][:11] == "/common_ins":  # use common ins (per each loop)
            loop = args[0][-1]
            #loop = str(-int(loop) + 7)
            self.Slmast.sl_osc_cmd("/sl/{}/set".format(loop), ["use_common_ins", args[-1]])

        elif args[0][:12] == "/common_outs":  # use common outs (per each loop)
            self.Slmast.sl_osc_cmd("/sl/{}/set".format(args[0][-1]), ["use_common_outs", args[-1]])
            print ('common outs')
            self.Slmast.sl_osc_cmd("/sl/{}/get".format(args[0][-1]), "use_common_outs")

        elif args[0][:6] == "/fader":
            vel = int(args[1] * 127)
            note = int(args[0][7])
            #note = -note + 7
            self.glass_cc.send_noteon(144, note, vel) # send fader controls to EQ

        elif args[0] == "/bitbeats":
            self.glass_cc.send_noteon(144, 38, args[-1])

        elif args[0][:6] == "/mutes":
            print (args[0][:6], args[0][-1])
            loop = int(args[0][-1])
            #loop = -loopinv + 7
            print ('loop', loop)
            #if self.Slmast.loops[loop].state == 4:
            self.Slmast.sl_osc_cmd("/sl/{}/hit".format(str(loop)), "mute")

        elif args[0][:5] == "/save": #into directory labelled as the exact time
            if args[-1] == 1:
                seshtime= time.asctime()
                os.mkdir('sessions') if os.path.exists('sessions') == False else None
                os.mkdir('sessions/' + seshtime)
                print ('saving session to disk : sessions/', seshtime)
                print (os.path.exists('sessions'))
                self.Slmast.sl_osc_cmd("/save_session", ["sessions/" + seshtime + '/' + seshtime + ".slsess", "localhost:9998", "error_path"])
                for i in range(8):
                   self.Slmast.sl_osc_cmd("/sl/{}/save_loop".format(str(i)), ["sessions/" + seshtime + '/' + seshtime + "+loop" + str(i) + ".wav", "32", "endian", "localhost:9998", "error_path"])


        elif args[0][:9] == "/bittempo":
            self.glass_cc.send_noteon(176, 2, args[-1])  # via carla file assigned

        elif args[0][:4] == "/xy":
            #if x != 0 and y != 0:
            pt0 = args[1:4]
            pt1 = args[4:7]
            pt2 = args[7:10]
            pt3 = args[10:13]
            x0, y0 = pt0[0], pt0[1]

            if x0 + y0 == 0:
                self.p0 = 0
                self.glass_cc.send_noteon(176, 1, 0)

            elif x0 != self.x0 and y0 != self.y0:
                self.p0 = 1
                self.x0, self.y0 = x0, y0
                self.glass_cc.send_noteon(176, 3, y0) 
                self.glass_cc.send_noteon(176, 4, x0)
                self.glass_cc.send_noteon(176, 1, 127)
                

            print (x0, y0, self.p0)

        elif args[0] == "/pushypulse": #testing pulsing on o-s-c
            send("/loop_rgb", [100, 100, 100])
            send("/rgb_pulse", [255, 255, 255])
            time.sleep(1)
            send("/pulse", 1)

        elif args[0] == "/swapadd":
            Grid.swap = "add" if args[-1] else None
        elif args[0] == "/swapimp":
            Grid.swap = "implement" if args[-1] else None

        elif args[0] == "/monitor":
            self.glass_cc.send_noteon(175,11, args[-1])
        elif args[0] == "/main_out":
            self.glass_cc.send_noteon(175,10, args[-1])
        elif args[0] == "/input_gain":
            self.glass_cc.send_noteon(175, 12, args[-1])

        elif args[0][:5] == "/gain":
            self.glass_cc.send_noteon(175, int(args[0][5]), args[-1])

        elif args[0] == '/test':
            #print (self.Slmast.loops[0].pos_eighth)
            if args[-1] == True:

                self.jack.routyconnect('sooperlooper:common_out_1', 'Bitrot Repeat:Audio Input 2')


        elif args[0] == '/patch':
            inport = self.portnames[args[1]] if args[1] in self.portnames else args[1]
            outports = []
            for p in args[2:]:
                port = self.portnames[p] if p in self.portnames else p
                outports.append(port)
                x = [self.portnames[i] for i in args[2:]]
            print ('patching', inport, outports)
            for channel in range(1, 3):
                chan = str(channel)
                outport = [p + chan for p in outports]
                self.jack.routyconnect(inport + str(channel), outport)

        else:
            print ('no handler for ', args)
