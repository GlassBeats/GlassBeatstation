class Gridmaster():
    def __init__(self, stage_osc, mk2_out):
        self.stage_osc = stage_osc
        self.mk2_out = mk2_out
        self.mode = "rand"
        self.modelst = ["loop", "instr", "lplay", "rand"]
        self.cmds = ["record", "overdub", "oneshot", "trigger",
                      "pause", "reverse", "undo", "redo"]


        self.pgrid = {} #primarygrid for mode states of buttons, NOT for loopstates
        clroff, clron = [0,0,0], [63,63,63]
        for x in range(9):
            for y in range (9):
                self.pgrid[x,y] = {"loop":[clroff,clron],  #layers for modes
                                  "instr":[clroff, clron],  #[x*7,y*7, (-y+7)*7]],
                                  "lplay":[[x*7, y*7, (-y+8)*7],clron],
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
                   

        for x in range(8): # to highligh ionian scale
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
                    
                

    def buttonclrchange(self, x, y, vel, clr):
        print(x ,y, vel,'changing color from', self.pgrid[x,y]["rand"][vel], "to ", clr)
        self.pgrid[x,y]["rand"][vel] = clr
        self.ledout(x,y, clr)
        
    def alter_pressfunc(self, x, y, vel, mode="rand", func=None, args=None, color=None):
        if func == None or args == None:
            raise Exception('no function or argument passed')

        if color:
            #self.pgrid[x,y]["rand"][vel] = color
            self.buttonclrchange(x, y, vel, color)

        print (self.fgrid[x,y][mode])
        self.fgrid[x,y][mode][0][vel] = func
        self.fgrid[x,y][mode][1][vel] = args
        print ('altered', self.fgrid[x,y][mode])

            

    def buttonchange(self, x, y, vel, arg=None, func=None, clr=None): #clr=None?
        self.fgrid[x,y]["rand"][vel] = func
        if clr:
            self.pgrid["rand"][x,y][vel] = clr
        
                
    def gridpress(self, x, y, vel):
        print (self.pgrid[x,y][self.mode][vel])
        self.ledout(x, y, self.pgrid[x,y][self.mode][vel])

        func = self.fgrid[x,y][self.mode][0][vel]
        #print (self.fgrid[x,y][self.mode][0][vel], self.fgrid[x,y][self.mode][1][vel])
        args = self.fgrid[x,y][self.mode][1][vel]

        if func != None:
            if isinstance(func,list) == True:
                for f in range(len(func)):
                    print (func[f], *args[f])
                    func[f](*args[f])
            else:
                func(*args)
        
        else:
            print ('this button is unassigned to any function')
            #func(self.fgrid[func][self.mode][1])
        #for range(len(funcs)) or range(len(fgrid[self.mode][x,y][0][vel]))


    def ledout(self, x, y, color, var=None, stage=True, temp=False):
        if x > 8 or y > 8 or x < 0 or y < 0:
            #raise Exception('out of range', x, y)
            print ('---key error---', x, y)
        if self.pgrid[x,y]["current"] != color or temp==True: # dont repeat needlessly
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
        if mode not in self.modelst: raise TypeError( mode ," is not a valid mode")
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
        #clr = [0,255,255] if colorcode == 90 else [0,0,0]
        #for x in range(8):
        #    self.stage_osc.send("/griddy/"+ str(x + (8 * (-y + 7))), clr)

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
                    self.stage_osc.send("/column_text/" + str(i), " ")

