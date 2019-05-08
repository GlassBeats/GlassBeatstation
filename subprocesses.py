import subprocess, os, atexit

cwd = os.getcwd()
print ('staging control')
stagecontrol = subprocess.Popen(["open-stage-control","-l", cwd + "/stagecontrol.json",  # initiate stagecontrol with midi ports
    "-s", "127.0.0.1:9998", "-d"], stdout=subprocess.PIPE)

sl = subprocess.Popen(["sooperlooper", "-l 8", "-m", cwd + "/sl_bindings.slb"], stdout=subprocess.PIPE)  # start sooperlooper

jackmatch = subprocess.Popen(["python3", cwd + "/sub_jackmatch.py"], stdout=subprocess.PIPE) 

carla = subprocess.Popen(["carla", cwd + "/glass_car.carxp"]) #, "-n"], stdout=subprocess.PIPE) #  "-n" to run headless


def exit_handler():
    print ("exiting")
    jackmatch.terminate()
    sl.terminate()
    #carla.terminate()
    stagecontrol.terminate()

atexit.register(exit_handler)

while True:
    pass
    
