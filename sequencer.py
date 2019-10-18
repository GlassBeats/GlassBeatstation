class Sequencer():
    def __init__(self, steps, sequences, midiout, Grid):
        self.steps = steps
        self.Grid = Grid
        self.midiout = midiout
        indv_seq = [0 for x in range(sequences)]
        self.seq = [indv_seq.copy() for y in range(8)]
        print ('*' * 200)
        print (self.seq)
        print ('*' * 200)
    def change_step(self, x, y, vel):
        if vel == True:
            print ('*****', x, y, self.seq[y])
            self.seq[y][x] = not self.seq[y][x]
            if self.seq[y][x] == True:
                self.Grid.pgrid[x,y]["seq"][False] = [0, 63, 63]
            else:
                self.Grid.pgrid[x,y]["seq"][False] = [0, 0, 0]

            

    def check_step(self, x):
        for y in range(8):                
            if self.seq[y][x] == 1:
                self.midiout.send_noteon(144, y + 36, 127)
                        #noteoff?
