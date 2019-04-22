import time, os

class OpenStageControl():
    def __init__(self, Grid, coord, Slobj, stage_osc_cli, midicc):
        self.Grid = Grid
        self.Slmast = Slobj
        self.stage_osc = stage_osc_cli
        self.coord = coord
        self.send = stage_osc_cli.send
        self.glass_cc = midicc

        self.x0, self.y0, self.p0 = 0, 0, 0
        
    def stage_handler(self, *args):
        #print ('stage', args)
        Grid = self.Grid
        send = self.send
        if args[0][:8] == "/beatpad":  # open-stage-c matrix - emulation of launchpad
            button = int(args[0][9:])
            vel = args[-1]
            x = button % 8
            y = 0 if button < 8 else int(button / 8)
            y = -y + 7
        
            self.coord(x, y, vel)  # button outputs identical to launchpad

        elif args[0][:14] == '/automap_push/': # switch this to be for mk2 inputs too!! currently misplaced
                button = int(args[0][14:])
                vel = args[-1]
                print('automap', vel)
                self.coord(button, 8, vel)

        elif args[0][:13] == '/column_push/': # switch this to be for mk2 inputs too!! currently misplaced
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
            loop = -loop + 7
            self.Slmast.sl_osc_cmd("/sl/{}/set".format(loop), ["use_common_ins", args[-1]])

        elif args[0][:12] == "/common_outs":  # use common pits (per each loop)
            self.Slmast.sl_osc_cmd("/sl/{}/set".format(args[0][-1]), ["use_common_outs", args[-1]])

        elif args[0][:6] == "/fader":
            vel = int(args[1] * 127)
            note = int(args[0][7])
            #note = -note + 7
            glass_cc.send_noteon(144, note, vel) # send fader controls to EQ

        elif args[0] == "/bitbeats":
            glass_cc.send_noteon(144, 38, args[-1])

        elif args[0][:6] == "/mutes":
            print (args[0][:6], args[0][-1])
            loop = int(args[0][-1])
            #loop = -loopinv + 7
            print ('loop', loop)
            #if self.Slmast.loops[loop].state == 4:
            self.Slmast.sl_osc_cmd("/sl/{}/hit".format(str(loop)), "mute")




        elif args[0][:5] == "/save": #into directory labelled as the exact time
            if args[-1] == 1:
                md = os.getcwd()[:14]
                slsesstime = time.asctime()
                print (type(slsesstime))
                os.mkdir(slsesstime)
                self.Slmast.sl_osc_cmd("/save_session", [slsesstime + "/" + slsesstime, "localhost:9998", "error_path"])
                for i in range(8):
                   self.Slmast.sl_osc_cmd("/sl/{}/save_loop".format(str(i)), [slsesstime + "/" + slsesstime + "+loop" + str(i) + ".wav", "32", "endian", "localhost:9998", "error_path"])


        elif args[0][:9] == "/bittempo":
            self.glass_cc.send_noteon(176, 2, args[-1])  # via carla file assigned

        elif args[0][:4] == "/xy":
            #if x != 0 and y != 0:
            pt0 = args[1:4]
            pt1 = args[4:7]
            pt2 = args[7:10]
            pt3 = args[10:13]
            x0, y0 = pt0[0], pt0[1]
            #print (args)

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
            


        
            
    
    
        
