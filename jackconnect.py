import jack

class JackConnections():
    def __init__(self):

        try:    
            self.client = jack.Client('glassbeats')
        except jack.JackError:
            sys.exit('JACK server not running?')

        self.client.activate()


        connections = [
        ["sooperlooper:common_out_1", "Bitrot Repeat:Audio Input 1"],
        ["sooperlooper:common_out_2", "Bitrot Repeat:Audio Input 2"],
        #["lp-seq", "Hydrogen:Hydrogen Midi-In"],
        ["Hydrogen:out_L", "system:playback_1"],
        ["Hydrogen:out_R", "system:playback_2"], 
        ]

        self.connecting(connections)

        

    def connecting(self, connections):
        print (connections)
        for i in range(8):
            for s in range(1,3):
                connections.append(["sooperlooper:loop{}_out_{}".format(str(i),str(s)), "pure_data_0:input" + str(i)])
          
        for i in range(len(connections)):
            try:
                self.client.connect(*connections[i])
                print ('-' * 50)
                print('connecting : ', connections[i])
                
            except jack.JackError:
                print ('fail', connections[i])
