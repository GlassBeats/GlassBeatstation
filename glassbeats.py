#/usr/bin/python3
## Totally modular musical-gestural hardware & software interface
## aka how make any input do anything
## this is a story
## join the journey

## consider more stacking

class Grid(object):
    mode = 0
    def __init__(self, rows, columns):
        self.Buttons = {}
        for x in range(rows):
            for y in range(columns):
                self.Buttons[(x,y)] = Button(self.mode, (x, y))

                 
class Button (Grid):
    def __init__(self, mode, coord):
        self.coord = coord
        self.funcs = [{}, {}] ##functions by index (mode)
        self.state = 0
        self.color = [{}, {}] #this should be stackable, last off

    def __repr__(self):
        return str(self.funcs)

    def replace_func(self, vel, function, mode=None):
        if mode == None: mode = self.mode  
        try:
            if self.funcs[vel][mode]:
                print ("{}: replacing {} with {}".format(self.coord, self.funcs[vel][mode], function))
                self.funcs[vel][mode] = function
        except KeyError:
                print ("{}: has no function yet, use add_func")
                       
    def add_func(self, vel, function, mode=None):
        if mode == None: mode = self.mode            
        self.funcs[vel][mode] = function
        print (self.funcs[vel][mode])
        
    def press(self, vel, mode=None):
        if mode == None: mode = self.mode
        try: 
            action = self.funcs[vel][mode]
            print (action, end= " ")
            action()
        except KeyError:
            print ('there is no assigned function yet')
            
    def led(index, color, special=None):
        midiout.write(color)
        if color:
            #do special color stuff
            pass
    def changeclr(xy, mode, velocity, color):
        pass
        
def testfunc():
    print ('successful function')

def testfunc2():
    print ('secondary success')

if __name__ == "__main__":
    Griddy = Grid(5,5)
    Griddy.Buttons[1,1,].add_func(True, testfunc)
    Griddy.Buttons[1,1,].press(True)
    print ('test', Griddy.Buttons[1,1,])
    
    Griddy.Buttons[1,1,].replace_func(True, testfunc2)
    Griddy.Buttons[1,1,].press(True)  

'''
         
Grid.button[(x,y)].press(vel, mode)
Grid.press((x,y), vel, mode)
Grid.button[(x,y)].press()                       
'''

'''
class SuperLoop
    def __init__(self):
        self


class Loop(Superloop):
    def __init__(self):
        self.state:
'''
