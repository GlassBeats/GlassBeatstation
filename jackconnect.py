import jack, sys

class JackConnections():
    def __init__(self):

        try:    
            self.client = jack.Client('glassbeats')
        except jack.JackError:
            sys.exit('JACK server not running?')

        self.client.activate()

        self.curr_connex = {}

        self.inports = ["Bitrot Repeat:Audio Input ",
                         "system:playback_",
                         "sooperlooper:common_in_",
                         ]

        self.outports= ["Bitrot Repeat:Audio Output ",
                        "sooperlooper:common_out_",
                        ]

        connections = [

        #["Hydrogen:out_L", "sooperlooper:common_in_1"],
        #["Hydrogen:out_R", "sooperlooper:common_in_2"],



        ["Hydrogen:out_L",'C* Eq10X2 - 10-band equalizer:In Left'],
        ["Hydrogen:out_R",'C* Eq10X2 - 10-band equalizer:In Right'],

        ["zynaddsubfx:out_1", 'C* Eq10X2 - 10-band equalizer:In Left'],
        ["zynaddsubfx:out_2", 'C* Eq10X2 - 10-band equalizer:In Right'],

        ['C* Eq10X2 - 10-band equalizer:Out Left', "sooperlooper:common_in_1"],
        ['C* Eq10X2 - 10-band equalizer:Out Right', "sooperlooper:common_in_2"],


        ["sooperlooper:common_out_1", "Bitrot Repeat:Audio Input 1"],
        ["sooperlooper:common_out_2", "Bitrot Repeat:Audio Input 2"],
        ]

        midiconnections = [
        ['a2j:mk2-launchpad [133] (capture): mk2-out', 'a2j:Launchpad MK2 [20] (playback): Launchpad MK2 MIDI 1'],
        ['a2j:Launchpad MK2 [20] (playback): Launchpad MK2 MIDI 1', 'a2j:mk2-launchpad [132] (playback): mk2-out'],

            #['a2j:glass_instrument [134] (capture): glass_instrument',]
        ]

        self.initial_connect(connections)
        try:
            self.client.disconnect("Hydrogen:out_L", "system:playback_1")
            self.client.disconnect("Hydrogen:out_R", "system:playback_2")
        except jack.JackError:
            print ("Hydrogen isn't open")

    def connect(self, inport, outport, stereo=True):
        j = self.client

        for item in j.get_all_connections(inport):
            print (item.name)

        current_outs = [o.name for o in j.get_all_connections(inport)]

        if outport not in current_outs:
            try:
                j.connect(inport, outport)
                print ('connecting', inport, outport)
            except jack.JackError:
                print('fail', inport, outport)
        else:
            print ('already connected', inport, outport)


    def routyconnect(self, inport, outports, stereo=True):
        j = self.client


        print ('*** current connections ***')
        current_outs = [o.name for o in j.get_all_connections(inport)]
        print('***')
        print('currently', inport, '-->', current_outs)
        print('going to connect ', inport, '-->', outports)


        if outports == []:
            for o in current_outs:
                print ('disconnect all')
                j.disconnect(inport, o)
        else:
            for out in current_outs:
                print ('out', out)
                print ('outports', outports)
                if out not in outports and out != outports:
                    j.disconnect(inport, out)
                    print('disconnecting', inport, out)
            for outs in outports:
                if outs not in current_outs:
                    try:
                        j.connect(inport, outs)
                        print('connecting', inport, outports)
                    except jack.JackError:
                        print('failed to connect', inport, outports)

            print ('-' * 80)



                            #print('fail', inport, outports)
                #else:
                    #print ('already connected', inport, outports)


    def initial_connect(self, connections):
        print (connections)
        #for i in range(8):
        #    for s in range(1,3):
        #        connections.append(["sooperlooper:loop{}_out_{}".format(str(i),str(s)), "pure_data_0:input" + str(i)])
          
        for i in range(len(connections)):
            try:
                self.client.connect(*connections[i])
                print ('-' * 50)
                print('connecting : ', connections[i])

            except jack.JackError:
                print ('fail', connections[i])
