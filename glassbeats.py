#/usr/bin/python3

import rtmidi2, time, jack, pythonosc
from pythonosc import udp_client


def openhandle(*args):
    print (args)

class MidiPort(): #opens midiport/s
    def __init__(self, name, direction="out"):
        if direction == 'out' or direction == 'both':
            self.outport = rtmidi2.MidiOut(name)
            self.outport.open_virtual_port(name)
        if direction == 'in' or direction == 'both':
            self.inport = rtmidi2.MidiIn(name)
            self.inport.open_virtual_port(name)


    def callback(self, function): #recieve incoming midi
        print ('setting up midi callback')
        self.inport.callback = function

    def send(self, note, vel, channel=176):
        self.outport.sendMessage(channel, note, vel)

class Grid():
    mode = "default"
    modes = ["default", "different"]
    def __init__(self, rows, columns):
        self.Button = {}
        for x in range(rows):
            for y in range(columns):
                self.Button[(x,y)] = Button((x, y))


class track_action():
    def __init__(self):
        pass
                
class Button (Grid):
    def __init__(self, coord):
        self.coord = coord
        self.state = 0
        self.color = [{}, {}] #this should be stackable
        self.clrstack = [] # for when there are multiple active lights, top of stack is displayed: FIFO
        self.actions= {} #array of arrays [[0] is function and [1] is arguments]
        for m in self.modes:
            self.actions[m] = [[], []]
        
    def __str__(self):
        return (str(self.coord) + str(self.actions))

    def get_action():
        pass

    def check_num(self, vel, mode, checkpoint):
        #check number of existing actions/args, return the # of actions/args
        print ('checking num', checkpoint)
        
        try:
            return len(checkpoint[mode][vel])
 
        except KeyError:
            return 0


    def clear_action(self, vel, mode=None):
        if mode == None: mode = self.mode
        num_args = self.check_num(vel, mode, self.actions)
        #self.actions[mode][vel].
    
    def add_action(self, vel, action, args=None, mode=None): #activate action for given mode
        if mode == None: mode = self.mode #default mode is current

        numactions = self.check_num(vel,mode, self.actions)
        print ('*' * 10, numactions, self.actions[mode][vel])
        if numactions == 0 :
            print (self.coord,'new action : {}'.format(action))
            #print (type(self.actions), self.actions, "****", args)
            self.actions[mode][vel] = [[action, args]]
            

        elif numactions == 1:
            print (self, 'adding {} to current button action {}'.format(action, self.actions[mode][vel]))
            self.actions[mode][vel].append([action, args])
            
        elif numactions > 2:
            print (self, 'adding {} to current {} actions {}'.format(action, numactions, self.actions[mode][vel]))
            self.actions[mode][vel].append(function)


    def activate(self, vel, mode=None):
        if mode == None: mode = self.mode
        numactions = self.check_num(vel, mode, self.actions) #check
        if numactions == 0: print ('there is no assigned action to activate')
        elif numactions == 1:
            print (self.actions[mode][vel])
            self.actions[mode][vel][0][0](self.actions[mode][vel][0][1])
        elif numactions> 1:
            print ('active', self.actions[mode][vel])
            for a in range(len(self.actions[mode][vel])):
                self.actions[mode][vel][a][0](self.actions[mode][vel][a][1])

class OSCClient(): #setup client to send OSC messages
    def __init__(self, port, ipaddr="127.0.0.1"):
        self.client= udp_client.SimpleUDPClient(ipaddr, port)
        self.port = port
        self.ipaddr = ipaddr
    def send(self, msg, port=None, ipaddr=None):
        if port==None: port = self.port
        if ipaddr==None: ipaddr = self.ipaddr
        self.client.send_message(ipaddr, port)


def test(*args):
    print ('***test*** ', *args)

if __name__ == '__main__':
    
    Matrix = Grid(5,5)   
    Matrix.Button[0,0].add_action(True, test, args='foxy')
    Matrix.Button[0,0].add_action(True, test, args='foxy2')
    Matrix.Button[0,0].activate(True)
##    Matrix.Button[0,0].activate(True)
##    Matrix.Button[0,0].change_action(True, test, args='foxy2', replace=True)
##    Matrix.Button[0,0].activate(True)
##    Matrix.Button[0,0].change_action(True, test, args='foxy3')
    #rint ('***')
    #Matrix.Button[0,0].change_action(True, test, args='cat')
    
    LaunchPadMidi = MidiPort('launchpad mk2', direction='both')
    LaunchPadMidi.callback(openhandle)

    #start osc clients
    '''SoopCli = OSCClient(9951)
    SoopCli.send('message')'''

    
