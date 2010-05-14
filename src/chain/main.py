from sys import argv
from platform import system as getOS
from subprocess import Popen,PIPE
from direct.gui.OnscreenText import OnscreenText 
from shell import Shell
from networking import Server

if __name__ == '__main__':
    if len(argv) == 2:
        port = int(argv[1])
        assert 1000 <= port <= 99999
        Server(port) # dragons
        OnscreenText(text="Server on port %d at IP: %s"%(port,Shell.get_IP()))
    else:
        Shell(True)
        while True:
            try: 
                run()
                break
            except: pass 
