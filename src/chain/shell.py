import sys
from platform import uname
import direct.directbase.DirectStart
from direct.gui.DirectGui import DirectEntry, DirectLabel, DirectFrame
from direct.gui.OnscreenText import OnscreenText 
from direct.filter.CommonFilters import CommonFilters
from pandac.PandaModules import TextNode, Thread
from direct.interval.IntervalGlobal import Func, Sequence,Wait
from networking import Server
from game import Game
from constants import MODEL_PATH,USE_GLOW

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
   / ____/___  ____ ___  ____ ___  ____  ____  ____/ /
  / /   / __ \/ __ `__ \/ __ `__ \/ __ `/ __ \/ __  / 
 / /___/ /_/ / / / / / / / / / / / /_/ / / / / /_/ /  
 \____/\____/_/ /_/ /_/_/ /_/ /_/\__,_/_/ /_/\__,_/   
\n\n\n\n\n
"""
LOADINGTEXT = """\n\nControls:
  Mouse       | look and turn
  Left click  | shoot
  Right click | scope zoom
  E           | pick up programs
  1-9         | drop program
  W/A/S/D     | move forward/left/back/right
  Spacebar    | jump
  F or scroll | change perspective
  P           | pause
  M/N         | toggle music/sound fx
  tab         | show leaderboard
  \nGame Type: deathmatch
  Kill each other and AI drones
  Player with the highest combined killcount wins!
  \nLoading game...
"""
PROGRAMS = {'rm' : 'Doubles attack power',
            'chmod' : 'Doubles shield strength',
            '-r' : 'Increases shoot speed',
            'RAM' : 'Provides an additional program slot',
            'gdb' : 'Debugger restores health over time',
            'ls' : 'Increases radar range by 1.5',
            'locate' : 'Doubles scope zoom',
           }


class Shell(object):
    def __init__(self,full):
        self.font = loader.loadFont('%s/FreeMono.ttf'%MODEL_PATH)
        self.screen = DirectFrame(frameSize=(-1.33,1.33,-1,1), frameColor=(0,0,0,1), pos=(0,0,0))
        self.output = OnscreenText(text="\n"*24, pos=(-1.31,0.95), scale=0.07, align=TextNode.ALeft, mayChange=True, fg=(1,1,1,0.8), font=self.font)
        self.keep_last_line = False
        self.intro(full)
        self.cmd_dict = { 
            'quit' : self.quit, 'exit' : self.quit, 'bye' : self.quit,
            'help' : self.help, 'ls' : self.help, 'dir' : self.help, 'wtf': self.help,
            'man' : self.manual,'clear' : self.clear, 'echo' : self.echo,
            'scores' : self.scores, 'score' : self.scores, 'highscore' : self.scores,
            'rm': self.rm, 'sudo': self.sudo, 'make':self.make, '!!':self.bangbang,
            'host': self.start_server, 'server': self.start_server,
            'start': self.start_game, 'run': self.start_game, 'join': self.start_game
        }
        self.help_cmds = ['help','host','join','man','scores','quit']
        self.cmd_hist = [""]
        self.cmd_pos = 0
        if USE_GLOW:
            CommonFilters(base.win, base.cam).setBloom(blend=(0,0,0,1), desat=-0.5, intensity=3.0, size=2)
            render.setShaderAuto()

    def intro(self,full):
        if full:
            textType = Sequence(Wait(0.5))
            for line in INTRO.splitlines():
                for char in line:
                    textType.append(Func(self.append_char, char))
                    textType.append(Wait(CHARACTER_DELAY))
                textType.append(Func(self.append_line, ""))
                textType.append(Wait(0.5))
            for line in LOGO.splitlines() :
                textType.append(Func(self.append_line, line))
                textType.append(Wait(CHARACTER_DELAY))
            for char in PROMPT:
                textType.append(Func(self.append_char, char))
                textType.append(Wait(CHARACTER_DELAY))
            textType.append(Func(self.user_input))
            textType.start()
        else:
            for line in INTRO.splitlines():
                for char in line:
                    self.append_char(char)
                self.append_line("")
            for line in LOGO.splitlines():
                self.append_line(line)
            for char in PROMPT:
                self.append_char(char)
            self.user_input()
    
    def user_input(self):
        self.prompt = DirectLabel(text=">", frameSize=(-0.04,0.06,-0.03,0.084), pos=(-1.29,0,-0.97), text_scale=0.07, frameColor=(0,0,0,1), text_fg=(1,1,1,0.8), text_font=self.font)
        self.input = DirectEntry(scale=0.07, command=self.parse_cmd, focus=1, entryFont=self.font, frameColor=(0,0,0,1), text_fg=(1,1,1,1), width=36, pos=(-1.23,0,-0.97), rolloverSound=None, clickSound=None)
        self.screen.accept('arrow_up',self.up_hist)
        self.screen.accept('arrow_down',self.down_hist)
        self.screen.accept('tab', self.tab_completion)
        self.input.enterText("")
    
    def up_hist(self):
        self.cmd_pos = max(self.cmd_pos-1,-len(self.cmd_hist)+1)
        self.input.enterText(self.cmd_hist[self.cmd_pos])
    
    def down_hist(self):
        self.cmd_pos = min(self.cmd_pos+1,0)
        self.input.enterText(self.cmd_hist[self.cmd_pos])
        
    def tab_completion(self):
        currentInput = self.input.get()
        if len(currentInput) == 0: return
        valids = [cmd for cmd in self.cmd_dict if cmd.startswith(currentInput)]
        if len(valids) == 0: return
        # look for max common substring
        for i in range(len(currentInput),min(len(s) for s in valids)):
            if len(set(s[i] for s in valids)) > 1: break
        else: # got to the end of the minstr
            i += 1 
        if len(valids) > 1:
            self.append_line(' '.join(valids))
        self.input.enterText(valids[0][:i])
    
    def hide_inputs(self):
        self.input.destroy()
        self.prompt.destroy()
        self.screen.ignoreAll()
        self.keep_last_line = False
        
    def hide_shell(self):
        self.output.stash()
        self.screen.stash()
        
    def resume_shell(self,stats_list):
        self.screen.unstash()
        self.output.unstash()
        self.game_recap(stats_list)
        
    def show_start_prompt(self):
        self.append_line("Enter start to start the game when all players have joined")
        self.keep_last_line = True
        self.prompt = DirectLabel(text="> ", frameSize=(-0.04,0.06,-0.03,0.084), pos=(-1.29,0,-0.97), text_scale=0.07, frameColor=(0,0,0,1), text_fg=(1,1,1,0.8), text_font=self.font)
        self.input = DirectEntry(scale=0.07, command=self.parse_start_cmd, focus=1, entryFont=self.font, frameColor=(0,0,0,1), text_fg=(1,1,1,1), width=36, pos=(-1.23,0,-0.97), rolloverSound=None, clickSound=None)
    
    def remove_start_prompt(self):
        if self.keep_last_line :
            self.hide_inputs()
            lines = self.output.getText().split('\n')
            lines[len(lines)-1] = ""
            self.output.setText('\n'.join(lines))
            
    def game_recap(self,stats_list):
        textType = Sequence(Func(self.append_line,"Game recap:"))
        for p in stats_list: # for now
            textType.append(Wait(0.5))
            textType.append(Func(self.append_line,"  Player %s"%p[0]))
            for k,s in sorted(p[1].iteritems()):
                textType.append(Func(self.append_line,"    %s = %d"%(k,int(s))))
                textType.append(Wait(0.1))
        textType.append(Func(self.user_input))
        textType.start()
        
    def append_line(self,txt):
        lines = self.output.getText().split('\n')
        del lines[0] # scroll
        if self.keep_last_line:
            lines.append(lines[len(lines)-1])
            lines[len(lines)-2] = txt
        else:
            lines.append(txt)
        self.output.setText('\n'.join(lines))
        
    def append_char(self,char):
        self.output.appendText(char)
    
    def parse_cmd(self,str):
        self.append_line("> %s"%str)
        if str :
            self.cmd_hist.append(str)
            input = str.split()
            cmd,args = input[0],input[1:]
            if cmd in self.cmd_dict:
                self.cmd_dict[cmd](cmd,args,False)
            else:
                self.default(cmd, args, False)
        self.cmd_pos = 0
        self.input.enterText("")
        self.input.setFocus()
    
    def parse_start_cmd(self, str):
        valid_cmds = ['start', 'begin', 'go']
        if str and str in valid_cmds : 
            self.g.client.send("start")
            self.remove_start_prompt()
        else :
            self.input.enterText("")
            self.input.setFocus()
    
    def load_finished(self):
        print "loading finished"
        self.g.client.send("player %s"%uname()[1])
        
        self.append_line("Waiting for other players...")
        self.append_line("")
    
    def starting_output(self):
        self.remove_start_prompt()
        self.append_line("Starting...")
        self.append_line("")
        self.append_line("")
            
    def main(self,port_num,ip,last=False):
        print "starting up"
        self.g = Game(ip,port_num,self,100.0,16.0,120)

    #### HERE THERE BE SHELL COMMANDS ####
    
    def start_game(self,cmd,arglist=[],sudo=False):
        if len(arglist) < 2:
            self.append_line("Usage: %s [port_num] [host_ip] <last>"%cmd)
        else:
            loadingScreen = Sequence(Func(self.hide_inputs))
            for line in LOADINGTEXT.split("\n"):
                loadingScreen.append(Func(self.append_line, line))
                loadingScreen.append(Wait(0.05))
            for _ in range(25 - len(LOADINGTEXT.split("\n"))):
                loadingScreen.append(Func(self.append_line, ""))
                loadingScreen.append(Wait(0.05))
            loadingScreen.append(Func(self.main,int(arglist[0]),arglist[1],len(arglist) == 3))
            loadingScreen.start()
    
    def start_server(self,cmd,arglist=[],sudo=False):
        if len(arglist) != 1:
            self.append_line("Usage: %s [port_num]"%cmd)
        else:
            port = int(arglist[0])
            str = "vigorously " if sudo else ""
            self.append_line("Starting server %son port %d..."%(str,port))
            Server(port)
            self.append_line("Server active, use 'join' to connect")
            
    def quit(self,cmd,arglist=[],sudo=False):
        Sequence(Func(self.append_line,"Bye!"),Wait(0.75),Func(sys.exit)).start()
    
    def sudo(self,cmd,arglist=[],sudo=False):
        if len(arglist) == 0:
            self.append_line("sudo what?")
        elif arglist[0] in self.cmd_dict:
            self.cmd_dict[arglist[0]](arglist[0],arglist[1:],True)
        else:
            self.default(arglist[0], arglist[1:], True)
    
    def rm(self,cmd,arglist=[],sudo=False):
        if len(arglist) == 0:
            self.append_line("rm: missing operand")
        if sudo:
            if '/' in arglist:
                self.append_line("I'm sorry, Dave. I'm afraid I can't do that.")
        else:
            for arg in arglist:
                if not arg.startswith('-'):
                    self.append_line("rm: cannot remove `%s': Permission denied"%arg)

    def help(self,cmd,arglist=[],sudo=False):
        self.append_line("Commands:")
        if sudo:
            for cmd in self.cmd_dict:
                self.append_line("   " + cmd)
        else:
            for cmd in self.help_cmds:
                self.append_line("   " + cmd)
            
    def manual(self,cmd,arglist=[],sudo=False):
        if len(arglist) == 0:
            self.append_line("Usage: %s [program]"%cmd)
            self.append_line("Program listing: %s"%', '.join(PROGRAMS.keys()))
        elif arglist[0] in PROGRAMS:
            self.append_line("%s -- %s"%(arglist[0],PROGRAMS[arglist[0]]))
        elif arglist[0] in self.cmd_dict:
            self.append_line("Sorry, %s is only for in-game programs"%cmd)
        else:
            self.append_line("Error: no such program: %s"%arglist[0])
            
    def scores(self,cmd,arglist=[],sudo=False):
        self.append_line("High scores not yet implemented")
    
    def make(self,cmd,arglist=[],sudo=False):
        if ' '.join(arglist) == "me a sandwich":
            if sudo:
                self.append_line("Okay.")
            else:
                self.append_line("What? Make it yourself.")
        else:
            self.append_line("make: *** No targets specified and no makefile found.  Stop.")
    
    def bangbang(self,cmd,arglist=[],sudo=False):
        del self.cmd_hist[-1] # remove the '!!'
        if sudo:
            self.parse_cmd("sudo "+self.cmd_hist[-1])
        else:
            self.parse_cmd(self.cmd_hist[-1])
    
    def clear(self,cmd,arglist=[],sudo=False):
        for _ in range(24): # I think that's the height?
            self.append_line("")
    
    def echo(self,cmd,arglist=[],sudo=False):
        if len(arglist) == 0:
            self.append_line("Echo... echo... echo...")
        else:
            echo = ' '.join(arglist)
            try:
                echo = str(eval(echo))
            except: pass
            self.append_line(echo)
    
    def default(self,cmd,arglist=[],sudo=False):
        if cmd in ['emacs','gnuemacs']:
            self.append_line("Sorry, emacs is not installed")
        elif cmd in ['vi','vim','gvim']:
            self.append_line("Sorry, vi is not installed")
        elif cmd in ['nano','pico','ed']:
            self.append_line("Really, now? Poor editor choice: -5 CHA")
        elif cmd in ['notepad','textedit','gedit']:
            self.append_line("What do I look like, a graphical user interface?")
        elif cmd == 'nethack':
            self.append_line("You zap a cursed wand of magic missile. It bounces! You die.")
        elif cmd in ['apt-get','aptitude']:
            self.append_line("I'm fine with the way I am, thanks.")
        elif sudo:
            self.append_line("sudo: %s: command not found" % cmd)
        else:
            self.append_line("%s: command not found" % cmd)
    
# end Shell class

if __name__ == '__main__':
    s = Shell(False)
    # hack the history, but only for our debugging runs
    s.cmd_hist = ["","join 1337 localhost", "host 1337"]
    run()
