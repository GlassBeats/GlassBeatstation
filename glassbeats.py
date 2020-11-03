#/usr/bin/python3

class Grid(object):
    mode = 0
    def __init__(self, rows, columns):
        self.Buttons = {}
        for x in range(rows):
            for y in range(columns):
                self.Buttons[(x,y)] = Button(self.mode, (x, y))
    def __repr__(self):
        pass
                 
class Button (Grid):
    def __init__(self, mode, coord):
        self.coord = coord
        self.funcs = [{}, {}] ##functions by index (mode)
        self.state = 0
        self.color = [{}, {}] #this should be stackable, last off


    def __str__(self):
        return (str(self.coord) + str(self.funcs))

    def replace_func(self, vel, function, mode=None):
        if mode == None: mode = self.mode  
        try:
            if self.funcs[vel][mode]:
                print ('{}[vel={}][mode={}] replacing {} with {}'.format(self.coord, vel, mode, self.funcs[vel][mode], function))
                self.funcs[vel][mode] = function

        except KeyError:
                print ('{}[vel={}][mode={}] has no function yet, use add_func'.format(self.coord, vel, mode))
                       
    def add_func(self, vel, function, mode=None):
        if mode == None: mode = self.mode
        print ('*' * 20)
        print (self)
        print ('*' * 20)
        try: 
            if isinstance(self.funcs[vel][mode], list):
                    self.funcs[vel][mode].append(function)
            elif self.funcs[vel][mode]:
                print ('adding {} to currrent action {}'.format)
        except KeyError:        
            print ('{}[vel={}][mode={}]: adding function '.format(self.coord, vel, mode, function))
            self.funcs[vel][mode] = function
        
    def press(self, vel, mode=None):
        if mode == None: mode = self.mode
        try: 
            action = self.funcs[vel][mode]
            print (self.coord, action, end= ' ')
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
    print ('first action')

def testfunc2():
    print ('secondary action')

if __name__ == '__main__':
    Matrix = Grid(5,5)
    Matrix.Buttons[1,1,].add_func(True, testfunc)
    Matrix.Buttons[1,1,].press(True)
    
    Matrix.Buttons[1,1,].add_func(True, testfunc2)
    Matrix.Buttons[1,1,].press(True)  
