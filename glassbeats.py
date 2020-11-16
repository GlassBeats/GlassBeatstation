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
        print ('setting up callback')
        self.inport.callback = function

    def send(self, note, vel, channel=176):
        self.outport.sendMessage(channel, note, vel)

class Grid():
    mode = 0
    def __init__(self, rows, columns):
        self.Button = {}
        for x in range(rows):
            for y in range(columns):
                self.Button[(x,y)] = Button(self.mode, (x, y))
                
class Button (Grid):
    def __init__(self, mode, coord):
        self.coord = coord
        self.state = 0
        self.color = [{}, {}] #this should be stackable, last off
        self.clrstack = [] # for when there are multiple active lights, top of stack is displayed: FIFO
        self.actions = [{}, {}]
        
    def __str__(self):
        return (str(self.coord) + str(self.actions))

    def changeclr(self, position, color): # for changing colors in the stack
        pass
    
    def led(self, position=0): #Activate color
        pass

    def check_action(self, vel, mode):
        #check if there is an action assigned, return # of actions
        try:
            if isinstance(self.actions[vel][mode], list) == True:
                return len(self.actions[vel][mode])
            else: return 1 
        except KeyError:
            return 0
        
    '''def change_action(self, vel, action, mode=None):
        if mode == None: mode = self.mode
        if self.check_action(vel, mode) > 1:
            print (self, 'replacing action {} with {}'.format(self.actions[vel][mode], action))
            self.actions[vel][mode] = action
        elif self.check_action(vel,mode) == 1:
                print (self,'previously no action, adding action {}'.format(action))
        else:
            print ('there is no action to change')
              /'''        
                       
    def change_action(self, vel, action, mode=None, replace=False): #activate action for given mode
        if mode == None: mode = self.mode #default mode is current
        numactions = self.check_action(vel,mode)
        
        if numactions == 0 or replace == True:
            print (self,'new action : {}'.format(action))
            self.actions[vel][mode] = action
        elif numactions == 1:
            print (self, 'adding {} to current button action {}'.format(action, self.actions[vel][mode]))
            self.actions[vel][mode] = ([self.actions[vel][mode],action])
        elif numactions > 2:
            print (self, 'adding {} to current button actions {}'.format(action))
            self.actions[vel][mode].append(function)

        
    def activate(self, vel, mode=None):
        if mode == None: mode = self.mode
        numactions = self.check_action(vel, mode) #check
        if numactions == 0: print ('there is no assigned action to activate')
        elif numactions == 1:
            print (self.coord, self.actions[vel][mode])
            self.actions[vel][mode]()
        elif numactions> 1:
            for a in self.actions[vel][mode]:
                a()




class OSCClient(): #setup client to send OSC messages
    def __init__(self, port, ipaddr="127.0.0.1"):
        self.client= udp_client.SimpleUDPClient(ipaddr, port)
        self.port = port
        self.ipaddr = ipaddr
    def send(self, msg, port=None, ipaddr=None):
        if port==None: port = self.port
        if ipaddr==None: ipaddr = self.ipaddr
        self.client.send_message(ipaddr, port)


def test():
    print ('test')

if __name__ == '__main__':
    
    Matrix = Grid(5,5)
    print(Matrix.mode)
    Matrix.Button[0,0].change_action(True, test)
    Matrix.Button[0,0].change_action(True, test, replace=True)
    
    Matrix.Button[0,0].activate(True)
    
    LaunchPadMidi = MidiPort('launchpad mk2', direction='both')
    LaunchPadMidi.callback(openhandle)

    #start osc clients
    SoopCli = OSCClient(9951)
    SoopCli.send('message')

    
    
    while True:
        time.sleep(.1)
