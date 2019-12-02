class Mode():
    def __init__(self):
        self.grid = {}
        for x in range(9):
            for y in range (9):
                self.grid[(x, y)] = {}
        del self.grid[8,8]

        for xy in self.grid:
            self.grid[x,y]["func"] = ["released function", "pressed function"]
            self.grid[x,y]["color"] = [[0,0,0], [63, 63, 63]]
                

    def change_btn_func(self, x, y, press=None, release=None):
        if press:
            self.grid[x,y]["func"][True] = press
        if release: 
            self.grid[x,y]["func"][False] = release

    def change_btn_clr(self, x, y, press=None, release=None):
        if press:
            self.grid[x,y]["color"][True] = press
        if release: 
            self.grid[x,y]["color"][False] = release
