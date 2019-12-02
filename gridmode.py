class Mode():
    def __init__(self):
        self.grid = {}
        for x in range(9):
            for y in range (9):
                self.grid[(x, y)] = {}
        del self.grid[8,8]

        for xy in self.grid:
            self.grid[xy]["func"] = ["off", "on"]
            self.grid[xy]["clr"] = [[0,0,0], [63, 63, 63]]
                

    def change_button_func(self,press=None, release=None):
        pass
