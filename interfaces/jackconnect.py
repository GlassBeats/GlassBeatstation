import jack, sys, rtmidi2

class JackConnections():
    def __init__(self):

        try:    
            self.client = jack.Client('glassbeats')
        except jack.JackError:
            sys.exit('JACK server not running?')

        self.client.activate()

        self.curr_connex = {}

        self.inports = [
                         "sooperlooper:common_in_",
                         ]
        self.INPORTS= [
                        "sooperlooper:common_out_",
                        ]

        self.initial_connections = [            
            ["sooperlooper:common_out_1", "ardour:Sloop_Main/audio_in 1"],
            ["sooperlooper:common_out_2", "ardour:Sloop_Main/audio_in 2"],
            
            ]



            
        self.initial_connect(self.initial_connections)
        


    def connect(self, OUTPORT, INPORT, stereo=True):
        j = self.client

        for item in j.get_all_connections(OUTPORT):
            print (item.name)

        current_inputs = [o.name for o in j.get_all_connections(OUTPORT)]

        if INPORT not in current_inputs:
            try:
                j.connect(OUTPORT, INPORT)
                print ('connecting', OUTPORT, INPORT)
            except jack.JackError:
                print('fail', OUTPORT, INPORT)
        else:
            print ('already connected', OUTPORT, INPORT)


    def routyconnect(self, OUTPORT, INPORTS, stereo=True):
        j = self.client

        
        print ('*** current connections ***')
        current_inputs = [o.name for o in j.get_all_connections(OUTPORT)]
        print('currently', OUTPORT, '-->', current_inputs)
        print('going to connect ', OUTPORT, '-->', INPORTS)

        for i in range(1,3):
            try:
                current_inputs.remove('ardour:Master/audio_in ' + str(i)) #dont disconect main
                current_inputs.remove('sooperlooper/common_in_ ' + str(i))
                current_inputs.remove('ardour:Sloop_Main/common_in_ ' + str(i))
            except:
                pass

        if INPORTS == []:
            for o in current_inputs:
                print ('disconnect all')
                j.disconnect(OUTPORT, o)
        else:
            for inport in current_inputs:
                print ('INPORTS', INPORTS)
                if inport not in INPORTS and inport != INPORTS:
                    print ('test', inport[:7])
                    if inport[:6] != "ardour": #dont auto-disconnect from ardour
                        print('disconnecting', OUTPORT, inport)
                        j.disconnect(OUTPORT, inport) 
                        
            for inputs in INPORTS:
                if inputs not in current_inputs:
                    try:
                        j.connect(OUTPORT, inputs)
                        print('connecting', OUTPORT, INPORTS)
                    except jack.JackError:
                        print('failed to connect', OUTPORT, INPORTS)

            print ('-' * 80)

    def initial_connect(self, connections):
        print (connections)

        for i in range(len(connections)):
            try:
                self.client.connect(*connections[i])
                print ('-' * 50)
                print('connecting : ', connections[i])

            except jack.JackError:
                print ('fail', connections[i])
