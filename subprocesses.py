import subprocess, os, atexit

cwd = os.getcwd()
print ('staging control')
stagecontrol = subprocess.Popen(["open-stage-control","-l", cwd + "/stagecontrol.json",   # initiate stagecontrol with midi ports
"-m",  "open-stage-control:virtual",
    "-s", "127.0.0.1:9998", "-d"], stdout=subprocess.PIPE)

sl = subprocess.Popen(["sooperlooper", "-l 8", "-m", cwd + "/sl_bindings.slb"], stdout=subprocess.PIPE)  # start sooperlooper

jackmatch = subprocess.Popen(["python3", cwd + "/sub_jackmatch.py"], stdout=subprocess.PIPE)

def exit_handler():
    print ("exiting")
    jackmatch.terminate()
    stagecontrol.terminate()

atexit.register(exit_handler)

while True:
    pass
