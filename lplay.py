class playloops_master():
    def __init__(self):
        loopbutton = {}
        self.loopbutton = loopbutton
        for x in range(9):
            for y in range(9):
                loopbutton[(x, y)] = None
        del loopbutton[8, 8]
    
    
class playloops():
    def __init__(self, Slmaster, slclient, playloops_master):
        Slmaster.loop_num += 1
        loopnum = Slmaster.loop_num
        print ('playyyyloop', loopnum)
        self.loop_num = Slmaster.loop_num
        self.slclient = slclient
        self.state = 0
        self.sync = False
        self.rev = False
        print ('adding additional loop')

        self.slclient.send("/loop_add", [2, 40.0])
        self.slclient.send("/sl/{}/register_auto_update".format(str(loopnum)), ["state", 10, "localhost:9998", "/sloop"])

    def press(self, x, y, vel):
        print (self.loopbutton)

        if vel == True:
            self.slclient.send("/sl/{}/down".format(str(y)), "trigger")
        elif vel == False:
            self.slclient.send("/sl/{}/down".format(str(y)), "pause")
