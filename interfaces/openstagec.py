import time, os, re

class OpenStageControl():
    def __init__(self, Grid, coord, Slobj, stage_osc_cli, midicc, midiinstr, jack, instrmode):
        self.instrmode = instrmode
        self.glass_instr = midiinstr
        self.jack = jack
        self.Grid = Grid
        self.Slmast = Slobj
        self.stage_osc = stage_osc_cli
        self.coord = coord
        self.send = stage_osc_cli.send
        self.glass_cc = midicc

        self.x0, self.y0, self.p0 = 0, 0, 0

        self.portnames = {'common_out':'sooperlooper:common_out_',
                          'common_in': 'sooperlooper:common_in_',
                          'dac':'system:playback_',
                          }
        
        for p in range(8):
            self.portnames['loop{}_out'.format(str(p))] = "sooperlooper:loop{}_out_".format(str(p))
            self.portnames['loop{}_in'.format(str(p))] = "sooperlooper:loop{}_in_".format(str(p))


     


    def stage_handler(self, *args):
        print (args)
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
            loopnum, val = int(args[0][6]), int(args[-1])
            self.Slmast.loops[loopnum].sync = val
            self.Slmast.sl_osc_cmd("/sl/{}/set".format(loopnum), ["sync", val])



        elif args[0] == "/quantize":  # choose global? cycle size
            #self.Slmast.sl_osc_cmd("/sl/0/set", ["quantize", args[1]])
            self.glass_cc.send_noteon(176,100, args[-1] * 42)

        elif args[0] == "/globalsync":  # global sync sync source
            self.Slmast.sl_osc_cmd("/set", ["sync_source", args[-1]])


        elif args[0] == "/cycle":  # set cycle length for quantization
            self.Slmast.sl_osc_cmd("/set", ["eighth_per_cycle", args[-1]])

        elif args[0][:11] == "/common_ins":  # use common ins (per each loop)
            loop = args[0][-1]
            self.Slmast.sl_osc_cmd("/sl/{}/set".format(loop), ["use_common_ins", args[-1]])

        elif args[0][:12] == "/common_outs":  # use common outs (per each loop)
            self.Slmast.sl_osc_cmd("/sl/{}/set".format(args[0][-1]), ["use_common_outs", args[-1]])
            print ('common outs')
            self.Slmast.sl_osc_cmd("/sl/{}/get".format(args[0][-1]), "use_common_outs")

        elif args[0][:6] == "/fader":
            vel = int(args[1] * 127)
            note = int(args[0][7])
            self.glass_cc.send_noteon(144, note, vel) # send fader controls to EQ

        elif args[0] == "/bitbeats":
            self.glass_cc.send_noteon(144, 38, args[-1])

        elif args[0][:6] == "/mutes":
            print (args[0][:6], args[0][-1])
            loop = int(args[0][-1])
            print ('loop', loop)
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
                    if self.Slmast.loops[i].state == 0: pass
                    else:self.Slmast.sl_osc_cmd("/sl/{}/save_loop".format(str(i)), ["sessions/" + seshtime + '/' + seshtime + "+loop" + str(i) + ".wav", "32", "endian", "localhost:9998", "error_path"])


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

        elif args[0] == "/rgb":
            loop_num = int(args[1])
            self.Slmast.color_change(loop_num, args[2:])

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

        elif args[0] == '/patch':
            OUTPORT = self.portnames[args[1]] if args[1] in self.portnames else "ardour:" + args[1] + "/audio_out "
            inports = []

            print (args[1][:4])
            if args[1][:4] == "sooperlooper:loop":
                loop_num = args[1][:4]
                common_inputs = False if len(args) > 2 else True
                print (common_inputs)
                    
                self.Slmast.sl_osc_cmd("/sl/{}/set".format(loop_num), ["use_common_ins", str(common_inputs)])            
            
            for p in args[2:]:
                port = self.portnames[p] if p in self.portnames else p 
                inports.append(port)

            for channel in range(1, 3):
                chan = str(channel)
                INPORT = [p + chan for p in inports]
                self.jack.routyconnect(OUTPORT + str(channel), INPORT)
                
 
        elif args[0] == '/midipatch':
            pass


        elif args[0][:6] == '/psync':
            loop_num = args[0][7]
            print (loop_num, args[-1])
            self.Slmast.sl_osc_cmd("/sl/{}/set".format(loop_num), ['playback_sync', args[-1]])

        elif args[0][:9] ==  '/mastereq':
            idx = int(args[0][10:])
            self.glass_cc.send_noteon(176, 15 + idx, args[-1])

        elif args[0][:9] == '/oct_grid':
            idx = int(args[0][10:])
            print (idx)
            self.glass_instr.send_noteon(144, idx, args[-1] * 127)

        elif args[0] == '/playrate':
            idx = 0 
            print (idx, args[-1])
            self.Slmast.sl_osc_cmd('/sl/{}/set'.format(str(self.Slmast.loops[idx])), ['rate', args[-1]])

        elif args[0] == '/gridreset':
            self.Grid.reset()

        elif args[0] == '/octup':
            self.instrmode.octave += 1
        elif args[0] == '/octdown':
            self.instrmode.octave -= 1

        else:
            print ('no handler for ', args)
