#!/python3
class Gridmaster():
    def __init__(self, stage_osc, mk2_out, glass_cc, glass_drum):
        self.stage_osc = stage_osc
        self.glass_cc = glass_cc
        self.mk2_out = mk2_out
        self.mode = "rand"
        self.modelst = ["loop", "instr", "seq", "rand"]
        self.cmds = ["record", "overdub", "oneshot", "trigger",
                      "pause", "reverse", "undo", "redo"]
        self.bitrot = False
        self.glass_drum = glass_drum

        self.ledloops = [0,1,2,3]

        self.pgrid = {} #primarygrid for mode states of buttons
        clroff, clron = [0,0,0], [63,63,63]
        for x in range(9):
            for y in range (9):
                self.pgrid[x,y] = {"loop":[clroff,clron],  #layers for modes
                                  "instr":[clroff, clron],  #[x*7,y*7, (-y+7)*7]],
                                  "seq":[clroff,clron],
                                   "rand":[clroff, clron],
                                   "current":[0,0,0],}
        del self.pgrid[8,8]

        self.pressed = {}
        self.reset()

        self.swap = None
        self.addaction = {"function":None, "args":None, "color":None}


        fgrid= {}
        self.fgrid = fgrid
        for x in range(9):
            for y in range (9):
                fgrid[(x, y)] = {}
        del fgrid[8,8]


        for xy in fgrid:
            for mode in self.modelst:
                fgrid[xy][mode] = [[None, None], [None, None]]
        #[[['func for button release'], ['func button press']], [['argsoff'],['argson']]  ]
        
        for x in range(8): # to highlight ionian scale
            for y in range(8):
                note = x + (y * 8)
                print (note)

                ionclr = [0, 50, 50]

                if note % 12 == 0:  #INSTRUMENT MODE
                    self.pgrid[x,y]["instr"][False] = [0,63,63]
                elif note % 12 in [5,7]:
                    self.pgrid[x,y]["instr"][False] = [5, 14,40]
                elif note % 12 in [2, 4, 9, 11]:
                    self.pgrid[x,y]["instr"][False] = [0, 0, 15]

      ### initiation stuff from main
    def postinit(self, slmast):
        self.SLmast= slmast
        for y in range(4):
            clr = self.SLmast.loops[y].color  # this is confusing..
            y = -y + 7  # invert  y
            for x in range(8):  # setup 'rand' mode functionalityy
                self.alter_pressfunc(x, y, True, func=slmast.sl_loopmode_cmd, args=[x, y, 1], color=clr)
                if x == 2:
                    self.alter_pressfunc(x, y, False, func=slmast.sl_loopmode_cmd, args=[x, y, 0])
                self.pgrid[x, y]['rand'][True] = clr

        for x in range(4):
            y = 8
            self.alter_pressfunc(x, y, True, func=self.switchmode, args=x)

        for x in range(4):  # add drum buttons
            for y in range(4):
                note = x + (y * 4) + 36
                for i in True, False:
                    self.alter_pressfunc(x + 4, y, i, func=self.glass_drum.send_noteon, args=[144, note, i * 127],
                                         color=[30, 20, 15])

        for y in range(4):  # add oneshot buttons
            x = 3
            clr = self.SLmast.loops[-y + 7].color
            self.alter_pressfunc(x, y, True, func=slmast.sl_loopmode_cmd, args=[2, y, True], color=clr)
            self.alter_pressfunc(x, y, False, func=slmast.sl_loopmode_cmd, args=[2, y, False])

        for y in range(4):  # add oneshot buttons
            x = 2
            loop = y + 4
            clr = self.SLmast.loops[-loop + 7].color
            self.alter_pressfunc(x, y, True, func=slmast.sl_loopmode_cmd, args=[2, loop, True], color=clr)
            self.alter_pressfunc(x, y, False, func=slmast.sl_loopmode_cmd, args=[2, loop, False])

        cc_clr = [0, 0, 13]

        for i in range(4):
            invi = -i + 3
            self.alter_pressfunc(0, invi, True, func=[self.bitrotchange],
                                 args=[[True, i * 31], None], color=[63, 63, 63])  # estimated good cc note values

            self.alter_pressfunc(0, invi, False, func=[self.bitrotchange], args=[[False, 0], None],
                                 color=[30 + c * i for c in cc_clr])





             
    def buttonclrchange(self, x, y, vel, clr):
        self.pgrid[x,y]["rand"][vel] = clr
        self.ledout(x,y, clr)
        
    def alter_pressfunc(self, x, y, vel, mode="rand", func=None, args=None, color=None):
        if func == None or args == None:
            raise Exception('no function or argument passed')

        if color:
            self.buttonclrchange(x, y, vel, color)

        self.fgrid[x,y][mode][0][vel] = func
        self.fgrid[x,y][mode][1][vel] = args
         

    def buttonchange(self, x, y, vel, arg=None, func=None, clr=None): #clr=None?
        self.fgrid[x,y]["rand"][vel] = func
        if clr:
            self.pgrid["rand"][x,y][vel] = clr
        
                
    def gridpress(self, x, y, vel):
        self.ledout(x, y, self.pgrid[x,y][self.mode][vel])

        func = self.fgrid[x,y][self.mode][0][vel]
        args = self.fgrid[x,y][self.mode][1][vel]

        if func != None:
            if isinstance(func,list) == True:
                for f in range(len(func)):

                    if isinstance(args[f], list) == True:
                        func[f](*args[f])
                    else:
                        func[f](*args[f])
            else:

                func(*args)

        else:
            print ('this button is unassigned to any function')

    def ledout(self, x, y, color, var=None, stage=True, temp=False):
        if x > 8 or y > 8 or x < 0 or y < 0:
            print ('---key error---', x, y)
        if self.pgrid[x,y]["current"] != color or temp==True: # dont repeat
            if temp==False: self.pgrid[x,y]["current"] = color
            
            self.mk2_led(x, y, color, style=var)
            
            if stage == True:
                self.stage_grid(x, y, color)


    def xy_to_stage(self, x, y):
        return str(x + (8 * (-y + 7)))
            
    def stage_grid(self, x, y, color): #open stage control output
        sclclr = [c * 4 for c in color]
        if y == 8:
            self.stage_osc.send("/automap_led/" + str(x), sclclr)    
        elif x < 8:
            self.stage_osc.send("/griddy/"+ str(x + (8 * (-y + 7))), sclclr)
        elif x == 8:
            self.stage_osc.send("/loopstate/" + str(-y + 7), sclclr)    

                
    def mk2_led(self, x, y, color, style=None, byte=11): #midi output mk2
        r,g,b = color
        if y == 8:
            note = 104 + x
        else:    
            note = x + y*10 + 11

        if style == None:        
            self.mk2_out.send_sysex(0, 32, 41, 2, 24, byte, note, r, g, b)


        elif style != None:
            if isinstance(style, list) != True or len(style) != 2:
                raise TypeError(style)
            else:
                clrcode = style[1]
                style = style[0]
                if style == "pulse":
                    vari = 40
                if style == "flash":
                    vari = 35
                self.mk2_out.send_sysex(0, 32, 41, 2, 24, vari, 0, note, clrcode) 
        else:
            print ('your style is atrocious')

            
    def switchmode(self,mode, loopstuff=None):
        if mode not in self.modelst: raise TypeError(mode," is not a valid mode")
        else:
            print ('switching to', mode, "mode")
            self.mode = mode
            for i in self.pgrid:
                x, y = i
                if x < 8 and y < 8:
                    self.ledout(x, y, self.pgrid[i][mode][False])
                    if mode == "loop":
                        self.stage_osc.send("/textmat/" + self.xy_to_stage(x,y), self.cmds[x])
                    elif mode == "rand":
                        if y > 3:
                            self.stage_osc.send("/textmat/" + self.xy_to_stage(x, y), self.cmds[x])
                        else:
                            self.stage_osc.send("/textmat/" + self.xy_to_stage(x, y), " ")
                    else:
                        self.stage_osc.send("/textmat/" + self.xy_to_stage(x, y), " ")

    def ledclmn(self, y, colorcode): #left to right 0 - 8
        self.mk2_out.send_sysex(0, 32, 41, 2, 24, 12, colorcode)        

    def ledrow(self, y, colorcode): #bottom to top 0 - 8
        self.mk2_out.send_sysex(0, 32, 41, 2, 24, 13, colorcode)
    
    def ledall(self, colorcode):
        self.mk2_out.send_sysex(0, 32, 41, 2, 24, 14, colorcode)
        

    def scrolltext(self, text, clr, loop): #returns 0, 32, 41, 2, 24, 21 when done
        self.mk2_out.send_sysex(0, 32, 41, 2, 24, clr, loop, text)

    def speedtext(self, speed):
        '''clr, loop?'''
        self.mk2_out.send_sysex(0, 32, 41, 2, 24, speed)

    def reset(self):
        self.ledall(0)
        for i in range(64):
                self.stage_osc.send("/textmat/" + str(i), " ")
                self.stage_osc.send("/griddy/" + str(i), [0, 0, 0])
                if i < 8:
                    self.stage_osc.send("/automap_text/" + str(i), " ")
                    self.stage_osc.send("/columntext/" + str(i), " ")
                    
        toprow = ['loop', 'instr', 'seq', 'custom', 'pause', ' ', ' ', ' ']  # automap controls labels
        for y in range(8):
            self.stage_osc.send('/automap_text/' + str(y), toprow[y])
           

    def bitrotchange(self, active, val):

        bitrots = {(0,0),(0,1),(0,2),(0,3)}

        for b in bitrots:
            bitrotactivity = True if b in self.pressed else False

        if bitrotactivity == False:
            if active == False:
                self.glass_cc.send_noteon(176, 1, 0)

            elif active == True: #if not already on
                self.glass_cc.send_noteon(176, 4, val)
                self.glass_cc.send_noteon(176, 1, 127)


        elif bitrotactivity == True:
            self.glass_cc.send_noteon(176, 4, val)


    def coordinate(self, x, y, vel):
        if self.swap != None:
            if vel == True:
                if self.swap == "add":  # swapping button functions dynamically
                    self.addaction["function"] = self.fgrid[x, y][self.mode][0][vel]
                    self.addaction["args"] = self.fgrid[x, y][self.mode][1][vel]
                    self.addaction["color"] = self.pgrid[x, y][self.mode][vel]
                    print('addict', self.addaction)
                elif self.swap == "implement":
                    print('implementing')
                    print(x, y, self.addaction["function"], self.addaction["args"])
                    self.alter_pressfunc(x, y, vel, func=self.addaction["function"], args=self.addaction["args"],
                                         color=[63, 63, 63])  # self.addaction["color"])
                    self.buttonclrchange(x, y, False, self.addaction["color"])

        else:
            if y < 8 and x < 8 and vel == True:  # pulse when pressed
                var = ["pulse", 119]
            else:
                var = None

            if (x, y) not in self.pressed:
                self.pressed[x, y] = True
            elif (x, y) in self.pressed:
                del self.pressed[x, y]

            if x == 8:
                if self.mode in ["loop", 'rand']:
                    loopsync = self.SLmast.loops[y].sync
                    syncclr = [0, 0, 0] if loopsync == True else [0, 0, 63]
                    if vel == True:
                        self.ledout(8, y, syncclr, temp=True)
                        self.SLmast.loops[y].sync = not self.SLmast.loops[y].sync
                        yinv = -y + 7
                        self.SLmast.sl_osc_cmd("/sl/{}/set".format(str(yinv)), ["sync", int(self.SLmast.loops[y].sync)])
                        stage_osc.send('/sync/' + str(-y + 7), int(loopsync))
                        value = "Sync" if self.SLmast.loops[y].sync == True else " "
                        stage_osc.send("/columntext/" + str(-y + 7), value)


                    elif vel == False:
                        self.ledout(8, y, self.pgrid[x, y]["current"], temp=True)

                elif self.mode in ["instr"]:
                    if vel == True:
                        sl_loopmode_cmd(0, y, vel)

                    elif vel == False:
                        if self.SLmast.loops[y].sync == True:
                            sl_loopmode_cmd(0, y, vel)
                        else:
                            sl_loopmode_cmd(4, y, True)


            elif y == 8:  # automap row
                if vel == 1:
                    if x < 4:
                        self.switchmode(self.modelst[x])
                    elif x == 4:
                        for y in range(8):  # consider directionality
                            if self.SLmast.loops[y].state != 14:
                                loop_pause(y)

            else:  # 8x8 grid
                self.ledout(x, y, self.pgrid[x, y][self.mode][vel], var)
                if self.mode == "loop":
                    self.SLmast.sl_loopmode_cmd(x, y, vel)
                elif self.mode == "instr":
                    var = None
                    midinote = x + (y * 8) + (12 * Instrumentmode.octave)
                    print(midinote)
                    glass_instr.send_noteon(144, midinote, vel * 127)
                elif self.mode == "rand":
                    self.gridpress(x, y, vel)
                elif self.mode == "seq":
                    Seq.change_step(x,y,vel)


