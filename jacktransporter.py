#!/usr/bin/env python3
'''this script is intended to be used in conjunction with gbeatstation.py -
run gbeatstation_main script and start hydrogen/ardour first'''


import sys, jack, rtmidi2, threading
from pythonosc import dispatcher, osc_server, udp_client

class Sequencer():  # instan

    def __init__(self, steps):  # different sounds and # of steps? 8 & 8, 4now
        self.seq = [[0 for i in range(8)] for x in range(8)]

    def change_step(self, x, y, val):
        print (x, y, val)
        self.seq[y][x] = val

def slosc_handler(*args):
    path, stepx, y, val = args
    Sequence.change_step(stepx, y, val)

try:
    client = jack.Client('showtime')

except jack.JackError:
    sys.exit('JACK server not running?')


class Tracker():
    def __init__(self):
        inlist = client.get_ports(is_output=True)
        outlist = client.get_ports(is_input=True)
        for i in inlist:
            print (i)
        print ('-----')
        for i in outlist:
            print (i)

        self.count_start = -1


def showtime():
    '''polls jack and sends osc to gbeatstation_main.py'''
    state, pos = client.transport_query()
    items = []
    items.append('frame = {}  frame_time = {} usecs = {} '.format(
        pos['frame'], client.frame_time, pos['usecs']))
    items.append('state: {}'.format(state))

    if 'ticks_per_beat' and 'beats_per_bar' and 'tick' and 'beat' in pos:
        ticks_per_meas = pos['ticks_per_beat'] * pos['beats_per_bar']
        cnt = pos['tick'] + (pos['beat'] * pos['ticks_per_beat']) - pos['ticks_per_beat']
        cnt8 = cnt / ticks_per_meas * 8
        intcnt = int(cnt8)


        if intcnt != Track.count_start:
            print (intcnt)

            cli.send_message("/jtrans_out", [intcnt, 8, 2, 1])

            if intcnt == 0:
                cli.send_message("/jtrans_out", [7, 8, 0, 0])
            else:
                cli.send_message("/jtrans_out", [intcnt - 1, 8, 0, 0])

            for i in range(8):
                if Sequence.seq[i][intcnt] > 0:
                    print ('hit - midisend, i, intcnt')
                    midiout.send_noteon(144, 36 + i, 127)

        Track.count_start = intcnt



@client.set_shutdown_callback
def shutdown(status, reason):
    sys.exit('JACK shut down, exiting ...')

Sequence = Sequencer(8)  # initiate sequencer class

cli = udp_client.SimpleUDPClient("127.0.0.1", 9998) #osc client


dispatcher = dispatcher.Dispatcher()  # oscserver
dispatcher.map("/jtrans_in", slosc_handler)
server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 8000), dispatcher)
print("OSC server on {}".format(server.server_address))

midiout = rtmidi2.MidiOut("jack_trans_out")
midiout.open_virtual_port("hydro")

Track = Tracker()

connections = [
    ["sooperlooper:common_out_1", "ardour:sooperlooper/audio_in 1"],
    ["sooperlooper:common_out_2", "ardour:sooperlooper/audio_in 2"],
    ["jack_trans_out:hydro", "Hydrogen:Hydrogen Midi-In"],
    ["jack_trans_out:hydro", 'a2j:Hydrogen [130] (playback): Hydrogen Midi-In'],
    ["Hydrogen:out_L", "ardour:Drums/audio_in 1"],
    ["Hydrogen:out_R", "ardour:Drums/audio_in 2"],
    ["jack_trans_out:hydro", "ardour:Drums/midi_in 1"],
    ["ardour:midinstrument/audio_out 1", "sooperlooper:common_in_1"],
    ["ardour:midinstrument/audio_out 2", "sooperlooper:common_in_2"],
    ]

for i in range(len(connections)):
    try:
        client.connect(*connections[i])
        print('connecting : ', connections[i])
    except jack.JackError:
        print ('fail', connections[i])


server_thread = threading.Thread(target=server.serve_forever)
server_thread.start()
with client:
    try:
        while True:
            showtime()

    except KeyboardInterrupt:
        print('signal received, exiting ...')  # , file=sys.stderr)
        sys.exit(0)
