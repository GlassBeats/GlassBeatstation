import rtmidi2, jackmatchmaker, subprocess, atexit, time, os, random
from pythonosc import udp_client, dispatcher, osc_server

#project specific internals
import gridmaster, openstagec, jackconnect
from slooper import *

def callback_midi(note, time_stamp):
    chan, note, vel = note
    vel = 0 if vel <= 64 else 1
    if chan == 176:
        print (note, vel)
        x = note - 104
        y = 8
    else:
        x = ( note - 1) % 10
        y = ( 99 - note ) // 10
        y = -y + 8
        
    coordinate(x,y, vel)

def coordinate(x, y, vel):
    if Grid.swap != None:
        if vel == True:
            if Grid.swap == "add": #swapping button functions dynamically
                Grid.addaction["function"] = Grid.fgrid[x, y][Grid.mode][0][vel]
                Grid.addaction["args"] = Grid.fgrid[x, y][Grid.mode][1][vel]
                Grid.addaction["color"] = Grid.pgrid[x, y][Grid.mode][vel]
                print ('addict', Grid.addaction)
            elif Grid.swap == "implement":
                print ('implementing')
                print (x, y, Grid.addaction["function"], Grid.addaction["args"])
                Grid.alter_pressfunc(x, y, vel, func = Grid.addaction["function"], args=Grid.addaction["args"],
                                     color= [63, 63, 63])#Grid.addaction["color"])
                Grid.buttonclrchange(x, y, False, Grid.addaction["color"])

    else:

        if y < 8 and x < 8 and vel == True: #pulse when pressed
            var = ["pulse", 119]
        else:  var = None

        if (x,y) not in Grid.pressed:
            Grid.pressed[x, y] = True
        elif (x,y) in Grid.pressed:
            del Grid.pressed[x,y]

        print (Grid.pressed)

        if x == 8:
            if Grid.mode in ["loop", 'rand']:
                loopsync = Slmast.loops[y].sync
                syncclr = [0, 0, 0] if loopsync == True else [0,0,63]
                if vel == True:
                    Grid.ledout(8, y, syncclr, temp=True)
                    Slmast.loops[y].sync = not Slmast.loops[y].sync
                    yinv = -y + 7
                    Slmast.sl_osc_cmd("/sl/{}/set".format(str(yinv)), ["sync", int(Slmast.loops[y].sync)])
                    stage_osc.send('/sync/' + str(-y + 7), int(loopsync))


                elif vel == False:
                    Grid.ledout(8, y, Grid.pgrid[x,y]["current"], temp=True)

            elif Grid.mode in ["instr"]:
                if vel == True:
                    sl_loopmode_cmd(0, y, vel)

                elif vel == False:
                    if Slmast.loops[y].sync == True:
                        sl_loopmode_cmd(0, y, vel)
                    else:
                        sl_loopmode_cmd(4, y, True)


        elif y == 8:  # automap row
            if vel == 1:
                if x < 4:
                    Grid.switchmode(Grid.modelst[x])
                elif x == 4:
                    for y in range(8): # consider directionality
                        if Slmast.loops[y].state != 14:
                            loop_pause(y)

        else: # 8x8 grid
            Grid.ledout(x, y, Grid.pgrid[x, y][Grid.mode][vel], var)
            if Grid.mode == "loop":
                sl_loopmode_cmd(x, y, vel)
            elif Grid.mode == "instr":
                var = None
                midinote = x + (y * 8) + 12
                print (midinote)
                glass_instr.send_noteon(144, midinote, vel * 127)
            elif Grid.mode == "rand":
                Grid.gridpress(x, y, vel)



def sl_loopmode_cmd(x, y, vel):
    yinv = y
    y = -y + 7
    lp = Slmast.loops[y]

    '''if x == 1 or x == 2 :
        if Grid.mode == "loop":
            if vel == 1:
                for i in range(7):  # change colors of row to clear old loop pos
                    if i +1 != x:
                        y = -y + 7
                        Grid.ledout(i + 1, y, Grid.pgrid[x,y][Grid.mode][False])'''
    if x == 2:
        if vel == True:
            if Slmast.loops[y].sync == False:
                slclient.send("/sl/{}/set".format(y), ["sync", True])
                Slmast.loops[y].sync = True

            slclient.send("/sl/{}/down".format(str(y)), "oneshot")
            #Grid.ledrow(1, 90)
            
        elif vel == False:# 'oneshot' release is a pause
            if lp.state != 14:
                loop_pause(y)
                #Grid.ledrow(1, 0)
        Grid.ledout(0, yinv, Grid.pgrid[0, yinv][Grid.mode][vel])

    elif vel == True:
        slclient.send("/sl/{}/down".format(str(y)), Slmast.cmds[x])            


def loop_pause(y):  # aka mute pause for the weird states
    if Slmast.loops[y].state != 14:
        slclient.send("/sl/{}/down".format(str(y)), "mute")
        slclient.send("/sl/{}/down".format(str(y)), "pause")
        #reset loop_pos to start?

            
class OSC_Sender():
    def __init__(self, ipaddr="127.0.0.1", port=9951):
        self.osc_client = udp_client.SimpleUDPClient(ipaddr, port)

    def send(self, addr, arg):
        self.osc_client.send_message(addr, arg)




#should commands to sooperlooper be midi driven for expediency? if less bytes, diff bottleneck


if __name__ == "__main__":
    Mk2_in = rtmidi2.MidiIn("mk2-launchpad") #midi input AND output port combined
    Mk2_in.open_virtual_port("mk2-in")  
    Mk2_in.callback = callback_midi
    Mk2_out = rtmidi2.MidiOut("mk2-launchpad") # midi output
    Mk2_out.open_virtual_port("mk2-out")

    #instrument
    glass_instr = rtmidi2.MidiOut("glass_instrument") # midi output
    glass_instr.open_virtual_port("glass_instrument")

    glass_drum = rtmidi2.MidiOut("glass_drum") # midi output
    glass_drum.open_virtual_port("glass_drum")

    #midiccouts
    glass_cc = rtmidi2.MidiOut("glass_cc") # midi output
    glass_cc.open_virtual_port("glass_cc")

    #sequencer
    glass_seq = rtmidi2.MidiOut("glass_sequencer") # midi output
    glass_seq.open_virtual_port("glass_sequencer")

    jack = jackconnect.JackConnections()
      
    slclient = OSC_Sender(ipaddr="127.0.0.1", port=9951)
    stage_osc = OSC_Sender(ipaddr="127.0.0.1", port=8080)
    
    Grid = gridmaster.Gridmaster(stage_osc, Mk2_out, glass_cc)
    Slmast = Slmaster(Grid, slclient)                        
    OStageC = openstagec.OpenStageControl(Grid, coordinate, Slmast, stage_osc, glass_cc, jack)


    for y in range(4):
        clr = Slmast.loops[y].color # this is confusing..
        y = -y + 7 #invert  y
        for x in range(8):   # setup 'rand' mode functionalityy
            Grid.alter_pressfunc(x, y, True, func=sl_loopmode_cmd, args=[x, y, 1], color=clr)
            if x == 2:
                Grid.alter_pressfunc(x, y, False, func=sl_loopmode_cmd, args=[x, y, 0])
            Grid.pgrid[x,y]['rand'][True] = clr
            #else:  # could probably reduce this redundancy and get ri["^a2j:glass_cc", "^Bitrot"],d of if/else
                #Grid.alter_pressfunc(i, y, False)
                #??

    for x in range(4):
        y = 8
        Grid.alter_pressfunc(x, y, True, func=Grid.switchmode, args=x)

    for x in range(4):  # add drum buttons
        for y in range(4):
            note = x + (y * 4) + 36
            for i in True, False:
                Grid.alter_pressfunc(x + 4, y, i, func=glass_drum.send_noteon, args =[144, note, i * 127], color = [30,20,15])
            #Grid.alter_pressfunc(x + 4, 0, False, func=glass_instr.send_noteon, args =[144, note, 0], color = [30,20,15])


    for y in range(4):  # add oneshot buttons
        x = 3
        clr = Slmast.loops[-y + 7].color
        Grid.alter_pressfunc(x, y, True, func=sl_loopmode_cmd, args=[2,y, True])
        Grid.alter_pressfunc(x, y, False, func=sl_loopmode_cmd, args=[2,y, False], color=clr)

    for y in range(4):  # add oneshot buttons
        x = 2
        loop = y + 4
        clr = Slmast.loops[-loop + 7].color
        Grid.alter_pressfunc(x, y, True, func=sl_loopmode_cmd, args=[2,loop, True])
        Grid.alter_pressfunc(x, y, False, func=sl_loopmode_cmd, args=[2,loop, False], color=clr)

    cc_clr = [0,0,13]

    for i in range(4):
        invi = -i + 3

        Grid.alter_pressfunc(0, invi, True, func=[Grid.bitrotchange],
                             args=[[True, i * 31], None], color = [63, 63, 63])  # estimated good cc note values
        Grid.alter_pressfunc(0, i, False, func=[Grid.bitrotchange], args=[[False, 0],None],
                             color=[30 + c * i for c in cc_clr])






        '''Grid.alter_pressfunc(0, invi, True,  func=[glass_cc.send_noteon, Grid.bitrotchange],
                                          args=[[176, 3, i * 31], True]) #estimated good cc note values
        Grid.alter_pressfunc(0, i, False, func=[Grid.bitrotchange], args=[False, [176, 1, 0]],
                             color = [30 + c * i for c in cc_clr])'''

    toprow = ['loop', 'instr', 'clr', 'custom', 'pause', ' ', ' ', ' ']  #automap controls labels
    for y in range(8):
        OStageC.send('/column_text/' + str(y), str(y))
        OStageC.send('/automap_text/' + str(y), toprow[y])

                          
# osc server handlers
    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/sloop", Slmast.sloschandler)  # sooperlooper handler
    dispatcher.set_default_handler(OStageC.stage_handler)    
    server = osc_server.ThreadingOSCUDPServer(("localhost", 9998), dispatcher)
    
    for mde in Grid.modelst:
        Grid.switchmode(mde)
        time.sleep(.25)
      
    def exit_handler():
        print ('exiting')
        Grid.reset()

    slclient.send("/ping", ["localhost:9998", "/sloop"])
    for i in range(8):
        slclient.send("/sl/{}/get".format(i), ["loop_len", "localhost:9998", "/sloop"])


    atexit.register(exit_handler)
    server.serve_forever()  # blocking osc server=
    
