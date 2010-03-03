import sys
import direct.directbase.DirectStart
from direct.gui.DirectGui import DirectEntry, DirectLabel
from direct.gui.OnscreenText import OnscreenText 
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import TextNode
from game import Game
from program import Rm,Chmod,Ls
import time

# top line is a hack, to preserve the width
# generated with: figlet -f slant "Chain of Command"
WELCOME = """----------------------------------------------------------------
 Welcome to
\n\n\n\n
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
\n\n\n\n\n\n
 Enter a command"""


class Shell(object):
    def __init__(self):
        font = loader.loadFont('../../models/FreeMono.ttf')
        self.output = OnscreenText(text=WELCOME, pos=(-1.33,1.03), scale=0.07, align=TextNode.ALeft, mayChange=True, bg=(0,0,0,1), fg=(1,1,1,0.8), font=font)
        self.prompt = DirectLabel(text=">", frameSize=(-0.05,0.06,-0.03,0.084), pos=(-1.29,0,-0.97), text_scale=0.07, frameColor=(0,0,0,1), text_fg=(1,1,1,0.8), text_font=font, )
        self.userInput = ""
        self.input = DirectEntry(scale=0.07, command=self.parse_cmd, focus=1, entryFont=font, frameColor=(0,0,0,1), text_fg=(1,1,1,1), width=38, pos=(-1.23,0,-0.97), rolloverSound=None, clickSound=None)
        self.input.enterText(self.userInput)
        self.cmd_dict = { 'quit' : self.quit,
                          'exit' : self.quit,
                          'help' : self.help,
                          'man' : self.manual,
                          'scores' : self.scores,
                          'start': self.start_game }

    def start_game(self):
        self.output.stash()
        self.prompt.stash()
        self.input.stash()
        main()

    def quit(self):
        self.append_line(" Bye!")
        sys.exit()
        
    def help(self):
        self.append_line(" Available Commands:")
        for cmd in self.cmd_dict:
            self.append_line("    " + cmd)
            
    def manual(self):
        self.append_line(" Instructions:")
        for i in range(0,10):
            self.append_line("    Blah")
            
    def scores(self):
        self.append_line(" High Scores: ")
        self.append_line("    1. Dude - 42")

	def resume_shell(self):
		self.output.unstash()
		self.prompt.unstash()
        self.input.unstash()
        
    def append_line(self,txt):
        lines = self.output.getText().split('\n')
        del lines[1] # preserve topline hack, scroll
        lines.append(txt)
        self.output.setText('\n'.join(lines))
    
    def parse_cmd(self,str):
        cmd = str.lstrip(self.userInput).split()
        cmd = '_'.join(cmd)
        if cmd in self.cmd_dict:
            self.cmd_dict[cmd]()
        else:
            self.append_line("unknown command: %s" % cmd)
        self.input.enterText(self.userInput)
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
        g.add_program(Ls)
    for _ in range(5):
        g.add_drone()
    g.add_event_handler()
    g.add_background_music()
    Sequence(Wait(2.0), Func(lambda:add_drone(g))).loop()

if __name__ == '__main__':
    Shell()
    run()

