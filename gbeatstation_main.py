import rtmidi2, subprocess, atexit, time, os, random
from pythonosc import udp_client, dispatcher, osc_server

# project specific internals
import gridmaster, sequencer, gridmode, customOSC
from interfaces import openstagec, slooper, jackconnect
from interfaces.slooper import *

def callback_midi(note, time_stamp):
    chan, note, vel = note
    vel = 0 if vel <= 64 else 1
    if chan == 176:
        print(note, vel)
        x = note - 104
        y = 8
    else:                                                                                                                           
        x = (note - 1) % 10
        y = (99 - note) // 10
        y = -y + 8

    Grid.coordinate(x, y, vel)


def testing_oscin(*args):
    print (args)

if __name__ == "__main__":
    Mk2_in = rtmidi2.MidiIn("mk2")  # midi input AND output port combined
    Mk2_in.open_virtual_port("mk2-in")
    Mk2_in.callback = callback_midi
    Mk2_out = rtmidi2.MidiOut("mk2")  # midi output
    Mk2_out.open_virtual_port("mk2-out")

    # instrument
    glass_instr = rtmidi2.MidiOut("glassbeats")  # midi output
    glass_instr.open_virtual_port("glass_instrument")

    glass_drum = rtmidi2.MidiOut("glassbeats")  # midi output
    glass_drum.open_virtual_port("glass_drum")

    # midiccouts
    glass_cc = rtmidi2.MidiOut("glassbeats")  # midi output
    glass_cc.open_virtual_port("glass_cc")

    # sequencer
    glass_seq = rtmidi2.MidiOut("glassbeats")  # midi output
    glass_seq.open_virtual_port("glass_sequencer")

    jack = jackconnect.JackConnections()

    slclient = customOSC.OSC_Sender(ipaddr="127.0.0.1", port=9951)
    stage_osc = customOSC.OSC_Sender(ipaddr="127.0.0.1", port=8080)

    Instrumentmode = gridmode.Mode()
    Instrumentmode.octave = 0

    Meta = gridmode.Mode()
    Grid = gridmaster.Gridmaster(stage_osc, Mk2_out, glass_cc, glass_drum)
    Seq = sequencer.Sequencer(8, 8, glass_seq, Grid)
    Slmast = Slmaster(Grid, slclient, Seq)
    OStageC = openstagec.OpenStageControl(Grid, Grid.coordinate, Slmast, stage_osc, glass_cc, glass_instr, jack, Instrumentmode)


    
    
    invlps = [Sloop(Grid, slclient) for i in range(8)]  #initiate  8 initial loops
    Slmast.loops = invlps[::-1]
    Grid.postinit(Slmast)

    

    # osc server handlers
    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/sloop", Slmast.sloschandler)  # sooperlooper handler
    #dispatcher.set_default_handler(OStageC.stage_handler)
    dispatcher.set_default_handler(testing_oscin)
    server = osc_server.ThreadingOSCUDPServer(("localhost", 9998), dispatcher)

    Grid.reset()
    time.sleep(1)
    Grid.switchmode("rand")


    def exit_handler():
        print('exiting')
        Grid.reset()

    slclient.send("/ping", ["localhost:9998", "/sloop"]) #maybe not necessary

    for i in range(8):
        slclient.send("/sl/{}/get".format(i), ["loop_len", "localhost:9998", "/sloop"])

    atexit.register(exit_handler)
    server.serve_forever()  # blocking osc server=

