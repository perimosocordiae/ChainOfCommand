import sys
from platform import uname
from time import sleep
import direct.directbase.DirectStart
from direct.gui.DirectGui import DirectEntry, DirectLabel, DirectFrame
from direct.gui.OnscreenText import OnscreenText 
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import TextNode
from networking import Client,Server
from game import Game
from program import DashR, Rm, Chmod, RAM
from constants import MODEL_PATH

CHARACTER_DELAY = 0.08
INTRO = "Hello\nWelcome to\n"
PROMPT = "Enter a command"
# generated with: figlet -f slant "Chain of Command"
LOGO = """\n\n\n
    ________          _                ____
   / ____/ /_  ____  (_)___     ____  / __/
  / /   / __ \/ __ `/ / __ \   / __ \/ /_  
 / /___/ / / / /_/ / / / / /  / /_/ / __/  
 \____/_/ /_/\__,_/_/_/ /_/   \____/_/     
                                          
    ______                                          __
   / ____/___  ____ ___  ____ ___  ____ ____  ____/ /
  / /   / __ \/ __ `__ \/ __ `__ \/ __ `/ __ \/ __  / 
 / /___/ /_/ / / / / / / / / / / / /_/ / / / / /_/  /  
 \____/\____/_/ /_/ /_/_/ /_/ /_/\__,_/_/ /_/\__,_/   
\n\n\n\n\n
"""
PROGRAMS = {'rm' : 'Doubles attack power',
            'chmod' : 'Doubles shield strength',
            '-r' : 'Increases shoot speed',
            'RAM' : 'Provides an additional program slot' 
           }


class Shell(object):
    def __init__(self,quick):
        if not quick:
            main(1337,None)
        else:
            self.font = loader.loadFont('%s/FreeMono.ttf'%MODEL_PATH)
            self.screen = DirectFrame(frameSize=(-1.33,1.33,-1,1), frameColor=(0,0,0,1), pos=(0,0,0))
            self.output = OnscreenText(text="\n"*24, pos=(-1.31,0.95), scale=0.07, align=TextNode.ALeft, mayChange=True, fg=(1,1,1,0.8), font=self.font)
            self.intro()
            self.cmd_dict = { 
                'quit' : self.quit, 'exit' : self.quit, 'bye' : self.quit,
                'help' : self.help, 'ls' : self.help, 'dir' : self.help,
                'man' : self.manual,
                'scores' : self.scores, 'score' : self.scores, 'highscore' : self.scores,
                'rm': self.permission_error,
                'start': self.start_game, 'run': self.start_game
            }
            self.cmd_hist = [""]

    def intro(self):
        textType = Sequence(Wait(0.5))
        for char in INTRO:
            if char == "\n":
                textType.append(Func(self.append_line, ""))
                textType.append(Wait(0.5))
            else:
                textType.append(Func(self.append_char, char))
                textType.append(Wait(CHARACTER_DELAY))
        for line in LOGO.split('\n') :
            textType.append(Func(self.append_line, line));
            textType.append(Wait(CHARACTER_DELAY))
        for char in PROMPT:
            textType.append(Func(self.append_char, char))
            textType.append(Wait(CHARACTER_DELAY))
        textType.append(Func(self.user_input))
        textType.start()
    
    def user_input(self):
        self.prompt = DirectLabel(text=">", frameSize=(-0.05,0.06,-0.03,0.084), pos=(-1.29,0,-0.97), text_scale=0.07, frameColor=(0,0,0,1), text_fg=(1,1,1,0.8), text_font=self.font, )
        self.input = DirectEntry(scale=0.07, command=self.parse_cmd, focus=1, entryFont=self.font, frameColor=(0,0,0,1), text_fg=(1,1,1,1), width=38, pos=(-1.23,0,-0.97), rolloverSound=None, clickSound=None)
        self.screen.accept('arrow_up',self.up_hist)
        self.screen.accept('arrow_down',self.down_hist)
        self.input.enterText("")
    
    def up_hist(self):
        self.cmd_pos = max(self.cmd_pos-1,-len(self.cmd_hist)+1)
        self.input.enterText(self.cmd_hist[self.cmd_pos])
    
    def down_hist(self):
        self.cmd_pos = min(self.cmd_pos+1,0)
        self.input.enterText(self.cmd_hist[self.cmd_pos])
        
    def start_game(self,cmd,arglist=[]):
        if len(arglist) < 2 or arglist[0] not in ['host','join']:
            self.append_line("Usage: %s host [port_num]"%cmd)
            self.append_line("       %s join [port_num] [host_ip]"%cmd)
            return
        if arglist[0] == 'host':
            self.main(int(arglist[1]),None)
        else:
            if len(arglist) == 2: self.append_line("Error: no IP provided")
            else : self.main(int(arglist[1]),arglist[2])

    def quit(self,cmd,arglist=[]):
        self.append_line("Bye!")
        sleep(0.5)
        sys.exit()

    def permission_error(self,cmd,arglist=[]):
        self.append_line("Error: permission denied")
        
    def help(self,cmd,arglist=[]):
        self.append_line("Available Commands:")
        for cmd in self.cmd_dict:
            self.append_line("   " + cmd)
            
    def manual(self,cmd,arglist=[]):
        if len(arglist) == 0:
            self.append_line("Usage: man [program]")
            self.append_line("Program listing: %s"%', '.join(PROGRAMS.keys()))
        elif arglist[0] in PROGRAMS:
            self.append_line("%s -- %s"%(arglist[0],PROGRAMS[arglist[0]]))
        else:
            self.append_line("Error: no such program: %s"%arglist[0])
            
    def scores(self,cmd,arglist=[]):
        self.append_line("High Scores: ")
        self.append_line("   1. Dude - 42")

    def resume_shell(self):
        self.output.unstash()
        self.prompt.unstash()
        self.input.unstash()
        self.screen.unstash()
        
    def append_line(self,txt):
        lines = self.output.getText().split('\n')
        del lines[0] # scroll
        lines.append(txt)
        self.output.setText('\n'.join(lines))
        
    def append_char(self,char):
        self.output.appendText(char)
    
    def parse_cmd(self,str):
        self.cmd_hist.append(str)
        self.cmd_pos = 0
        self.append_line("> %s"%str)
        input = str.split()
        cmd,args = input[0],input[1:]
        if cmd in self.cmd_dict:
            self.cmd_dict[cmd](cmd,args)
        else:
            self.append_line("unknown command: %s" % cmd)
        self.input.enterText("")
        self.input.setFocus()
    
    def main(self,port_num,ip):
        if not ip:
            Server(port_num)
            ip = "127.0.0.1"
        c = Client(ip,port_num)
        Sequence(Wait(1.0), Func(lambda: c.send("Client: %s"%uname()[1]))).loop()
        Sequence(Wait(0.1), Func(lambda: print_data(c))).loop()
        
        if False:
            g = Game(360,60.0,12.0,120)
            g.add_player('player_1')
            for _ in range(4):
                g.add_program(Rm)
                g.add_program(Chmod)
                g.add_program(DashR)
                g.add_program(RAM)
            g.add_event_handler()
            Sequence(Wait(2.0), Func(lambda:add_drone(g))).loop()
        
        self.output.stash()
        self.prompt.stash()
        self.input.stash()
        self.screen.stash()
# end Shell class

def add_drone(g):
    if len(g.drones) < 20:
        g.add_drone()

def print_data(c):
    data = c.getData()
    if len(data) > 0:
        print data

if __name__ == '__main__':
    Shell(True)
    run()
