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
        Server(port)
        if getOS() == 'Windows': # epic hacks
            ip = Popen('ipconfig',stdout=PIPE).stdout.readlines()[11].split()[-1]
        else:
            ip = Popen('ifconfig',stdout=PIPE).stdout.readlines()[1].split(':')[1].split()[0]
        OnscreenText(text="Server on port %d at IP: %s"%(port,ip))
    else:
        Shell(True)
    run()
