#/usr/bin/python3

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

    def __str__(self):
        return (str(self.coord) + str(self.funcs))

    def checkfuncs(self, vel, mode):
        try:
            if isinstance(self.funcs[vel][mode], list) == True:
                return len(self.funcs[vel][mode])
            else: return 1
        except KeyError:
            return 0

    def replace_func(self, vel, function, mode=None):
        if mode == None: mode = self.mode
        if self.checkfuncs(vel, mode) > 1:
            print (self, 'replacing {} with {}'.format(self.funcs[vel][mode], function))
            self.funcs[vel][mode] = function
        elif self.checkfuncs(vel,mode) == 1:
                print (self,'no function to replace, use add_func')
                       
    def add_func(self, vel, function, mode=None):
        if mode == None: mode = self.mode
        numfuncs = self.checkfuncs(vel,mode)
        if numfuncs == 0:
            print (self,' : adding function ', function)
            self.funcs[vel][mode] = function
        elif numfuncs == 1:
            print (self, 'adding {} to current action'.format(function))
            self.funcs[vel][mode] = ([self.funcs[vel][mode],function])
        elif numfuncs > 2:
            print (self, 'adding {} to current actions {}'.format(function))
            self.funcs[vel][mode].append(function)

        
    def press(self, vel, mode=None):
        if mode == None: mode = self.mode
        numfuncs = self.checkfuncs(vel, mode)
        if numfuncs == 0: print ('there is no assigned action yet')
        elif numfuncs == 1:
            print (self.coord, self.funcs[vel][mode])
            self.funcs[vel][mode]()
        elif numfuncs > 1:
            for a in self.funcs[vel][mode]:
                a()


def testfunc():
    print ('first action')

def testfunc2():
    print ('secondary action')

if __name__ == '__main__':
    Matrix = Grid(5,5)
    Matrix.Buttons[1,1,].add_func(True, testfunc)
    Matrix.Buttons[1,1,].press(True)
    print ('*********')

    
    Matrix.Buttons[1,1,].add_func(True, testfunc2)
    Matrix.Buttons[1,1,].press(True)
    print(Matrix)
