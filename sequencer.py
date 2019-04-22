class Sequencer():
    def __init__(self, steps, sequences, midiout):
        steps = self.steps

        self.seq = [[0 for i in range(sequences) for x in range(steps)]

    def change_step(x, y, vel):
        self.seq[y][x] = vel
        if vel == 127:
            
        




class Sequencer():
    def __init__(self, steps):
        

    def change_step(self, x, y, val):
        self.seq[y][x] = val
        lp.fg_seq[(y, x)] = val
        
        
        
        
