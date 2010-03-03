import sys
import direct.directbase.DirectStart
from direct.gui.DirectGui import DirectEntry, DirectLabel, DirectFrame
from direct.gui.OnscreenText import OnscreenText 
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import TextNode
from game import Game
from program import Rm,Chmod,DashR
import time

INTRO = "Hello\nWelcome to\n"
PROMPT = "Enter a command"
# generated with: figlet -f slant "Chain of Command"
LOGO = """\n\n\n
    ________          _                ____
   / ____/ /_  ____ _(_)___     ____  / __/
  / /   / __ \/ __ `/ / __ \   / __ \/ /_  
 / /___/ / / / /_/ / / / / /  / /_/ / __/  
 \____/_/ /_/\__,_/_/_/ /_/   \____/_/     
                                          
    ______                                           __
   / ____/___  ____ ___  ____ ___  ____ _____  ____/ /
  / /   / __ \/ __ `__ \/ __ `__ \/ __ `/ __ \/ __  / 
 / /___/ /_/ / / / / / / / / / / / /_/ / / / / /_/ /  
 \____/\____/_/ /_/ /_/_/ /_/ /_/\__,_/_/ /_/\__,_/   
\n\n\n\n\n
"""


class Shell(object):
    def __init__(self,quick):
        if (not(quick)):
            main()
        else:
            self.font = loader.loadFont('../../models/FreeMono.ttf')
            self.screen = DirectFrame(frameSize=(-1.33,1.33,-1,1), frameColor=(0,0,0,1), pos=(0,0,0))
            self.output = OnscreenText(text="\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n", pos=(-1.31,0.95), scale=0.07, align=TextNode.ALeft, mayChange=True, fg=(1,1,1,0.8), font=self.font)
            self.intro()
            self.cmd_dict = { 'quit' : self.quit,
                              'exit' : self.quit,
                              'help' : self.help,
                              'man' : self.manual,
                              'scores' : self.scores,
                              'start': self.start_game }

    def intro(self):
        textType = Sequence(Wait(0.5))
        for char in INTRO:
            if char == "\n":
                textType.append(Func(self.append_line, ""))
                textType.append(Wait(0.5))
            else:
                textType.append(Func(self.append_char, char))
                textType.append(Wait(0.15))
        for line in LOGO.split('\n') :
            textType.append(Func(self.append_line, line));
            textType.append(Wait(0.15))
        for char in PROMPT:
            textType.append(Func(self.append_char, char))
            textType.append(Wait(0.15))
        textType.append(Func(self.user_input))
        textType.start()
    
    def user_input(self):
        self.prompt = DirectLabel(text=">", frameSize=(-0.05,0.06,-0.03,0.084), pos=(-1.29,0,-0.97), text_scale=0.07, frameColor=(0,0,0,1), text_fg=(1,1,1,0.8), text_font=self.font, )
        self.input = DirectEntry(scale=0.07, command=self.parse_cmd, focus=1, entryFont=self.font, frameColor=(0,0,0,1), text_fg=(1,1,1,1), width=38, pos=(-1.23,0,-0.97), rolloverSound=None, clickSound=None)
        self.input.enterText("")
        
    def start_game(self,arglist=[]):
        self.output.stash()
        self.prompt.stash()
        self.input.stash()
        self.screen.stash()
        main()

    def quit(self,arglist=[]):
        self.append_line("Bye!")
        sys.exit()
        
    def help(self,arglist=[]):
        self.append_line("Available Commands:")
        for cmd in self.cmd_dict:
            self.append_line("   " + cmd)
            
    def manual(self,arglist=[]):
        self.append_line("Instructions:")
        for i in range(0,10):
            self.append_line("   Blah")
            
    def scores(self,arglist=[]):
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
        text = self.output.appendText(char)
    
    def parse_cmd(self,str):
        self.append_line("> %s"%str)
        input = str.split()
        cmd,args = input[0],input[1:]
        if cmd in self.cmd_dict:
            self.cmd_dict[cmd](args)
        else:
            self.append_line("unknown command: %s" % cmd)
        self.input.enterText("")
        self.input.setFocus()
# end Shell class

def add_drone(g):
    if len(g.drones) < 20:
        g.add_drone()

def main():
    g = Game(360,12,120)
    g.add_player('player_1')
    for _ in range(4):
        g.add_program(Rm)
        g.add_program(Chmod)
        g.add_program(DashR)
    #for _ in range(5):
    #    g.add_drone()
    g.add_event_handler()
    g.add_background_music()
    #Sequence(Wait(2.0), Func(lambda:add_drone(g))).loop()

if __name__ == '__main__':
    Shell(True)
    run()