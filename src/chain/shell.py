from platform import uname,system as getOS
from subprocess import Popen,PIPE
from itertools import izip
from pickle import load,dump
from re import match
import direct.directbase.DirectStart
from direct.gui.DirectGui import DirectEntry, DirectLabel, DirectFrame
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.filter.CommonFilters import CommonFilters
from pandac.PandaModules import TextNode, Thread, TransparencyAttrib
from direct.interval.IntervalGlobal import Func, Sequence, Wait
from networking import Server, Client
from game import Game
from constants import MODEL_PATH,USE_GLOW,TEAM_COLORS,TEXTURE_PATH


SCOREFILE = 'hiscores.pyz'
CONTROLSFILE = 'controls.pyz'
CHARACTER_DELAY = 0.08
INTRO = "Hello\nWelcome to\n"
PROMPT = "Enter a command to get started ('help' lists commands)"
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
LOADINGTEXT = """In-game Controls:
  Look and turn                 | mouse
  Shoot                         | %(shoot)s
  Move forward/left/back/right  | %(forward)s/%(moveleft)s/%(backward)s/%(moveright)s
  Pick up programs              | %(collect)s
  Drop programs                 | 1-9
  Jump                          | %(jump)s
  Scope zoom                    | %(scope)s
  Change perspective            | %(changePerspective)s or scroll
  Pause                         | %(pause)s
  Toggle music/sound effects    | %(toggleMusic)s/%(toggleSoundEffects)s
  Show leaderboard              | %(scores)s
  Quit game                     | escape
"""

PROGRAMS = {'rm' : 'Doubles attack power',
            'chmod' : 'Doubles shield strength (halves damage taken)',
            '-r' : 'Increases shoot speed',
            'RAM' : 'Provides an additional program slot',
            'gdb' : 'Debugger restores health over time',
            'ls' : 'Increases radar range by 1.5',
            'locate' : 'Doubles scope zoom',
           }

class Shell(object):
    def __init__(self,full):
        self.name = uname()[1]
        try:
            self.hiscores = load(open(SCOREFILE))
        except:
            self.hiscores = {}
        try :
            self.controls = load(open(CONTROLSFILE, 'rb'))
        except:
            self.loadDefaultSettings()
        self.font = loader.loadFont('%s/FreeMono.ttf'%MODEL_PATH)
        self.screen = DirectFrame(frameSize=(-1.33,1.33,-1,1), frameColor=(0,0,0,1), pos=(0,0,0))
        self.output = OnscreenText(text="\n"*24, pos=(-1.31,0.95), scale=0.07, align=TextNode.ALeft, mayChange=True, fg=(1,1,1,0.8), font=self.font)
        self.intro(full)
        self.cmd_dict = { 
            'quit' : self.quit, 'exit' : self.quit, 'bye' : self.quit,
            'help' : self.help, 'ls' : self.help, 'dir' : self.help, 'wtf': self.help,
            'man' : self.manual,'clear' : self.clear, 'echo' : self.echo, 'su' : self.su,
            'scores' : self.scores, 'score' : self.scores, 'highscore' : self.scores,
            'rm': self.rm, 'sudo': self.sudo, 'make':self.make, '!!':self.bangbang,
            'host': self.start_server, 'server': self.start_server,
            'start': self.start_game, 'run': self.start_game, 'join': self.start_game,
            'ifconfig': self.ifconfig, 'ipconfig': self.ifconfig, 'settings': self.settingsPrompt
        }
        # subset of commands, to get the user started
        self.help_cmds = {
            'help' : 'List available commands',
            'host' : 'Host a game on your computer',
            'join' : 'Join an already hosted game',
            'man' : 'Manual page for in-game upgrade programs',
            'scores' : 'List the scores of the previous round',
            'quit' : 'Exit the game and close the shell',
            'settings' : 'Change the controls for the game'
        }
        self.cmd_hist = [""]
        self.cmd_pos = 0
        self.server = None
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
            for line in LOGO.splitlines():
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
        self.prompt = DirectLabel(text='', frameSize=(-0.04,0.06,-0.03,0.084), pos=(0,0,-0.97), text_scale=0.07, frameColor=(0,0,0,1), text_fg=(1,1,1,0.8), text_font=self.font)
        self.input = DirectEntry(scale=0.07, command=self.parse_cmd, focus=1, entryFont=self.font, frameColor=(0,0,0,1), text_fg=(1,1,1,0.8), width=36, pos=(0,0,-0.97), rolloverSound=None, clickSound=None)
        self.set_prompt_str()
        self.screen.accept('arrow_up',self.history,[True])
        self.screen.accept('arrow_down',self.history,[False])
        self.screen.accept('tab', self.tab_completion)
        self.input.enterText("")
    
    def set_prompt_str(self):
        prompt_str = "%s>"%self.name
        self.prompt['text'] = prompt_str
        self.prompt.setText()
        char_width = 0.02286 # yay magic constants
        lpos = -1.29 + char_width*(len(prompt_str)-1)
        self.prompt.setX(lpos)
        ipos = lpos + char_width*(len(prompt_str)+1)
        self.input.setX(ipos)
    
    def history(self,up=True):
        if up: self.cmd_pos = max(self.cmd_pos-1,-len(self.cmd_hist)+1)
        else:  self.cmd_pos = min(self.cmd_pos+1,0)
        self.input.enterText(self.cmd_hist[self.cmd_pos])
    
    def tab_completion(self):
        words = self.input.get().split()
        if len(words) == 0: return
        currentInput = words.pop(-1)
        valids = [cmd for cmd in self.cmd_dict if cmd.startswith(currentInput)]
        if len(valids) == 0 or currentInput in valids: return
        if len(valids) == 1:
            words.append(valids[0])
            self.input.enterText(' '.join(words))
            return
        # look for max common substring
        for i in range(len(currentInput),min(len(s) for s in valids)):
            if len(set(s[i] for s in valids)) > 1: break
        else: # got to the end of the minstr
            i += 1
        if len(valids) > 1:
            self.append_line(' '.join(valids))
        words.append(valids[0][:i])
        self.input.enterText(' '.join(words))
    
    def hide_inputs(self):
        self.input.destroy()
        self.prompt.destroy()
        self.screen.ignoreAll()
        
    def hide_shell(self):
        self.output.stash()
        self.screen.stash()
        
    def resume_shell(self,stats_list):
        self.screen.unstash()
        self.output.unstash()
        self.game_recap(stats_list)
    
    def update_hiscores(self,name,is_winner,stats):
        if name not in self.hiscores:
            self.hiscores[name] = {}
        mystats = self.hiscores[name]
        if 'wins' in mystats:
            mystats['wins'] += 1 if is_winner else 0
        else:
            mystats['wins'] = 1 if is_winner else 0
        for k,s in stats.iteritems():
            if k in mystats:
                mystats[k] += int(s)
            else:
                mystats[k] = int(s)
        dump(self.hiscores,open(SCOREFILE,'w'),-1) # write out high scores
    
    def game_recap(self,stats_list):
        self.update_hiscores(*((s for s in stats_list if s[0]==self.name).next()))
        textType = Sequence(Func(self.append_line,"Game recap:"))
        for name,is_winner,stats in stats_list:
            textType.append(Wait(0.5))
            winstr = "won" if is_winner else "lost"
            textType.append(Func(self.append_line,"  Player %s (%s)"%(name,winstr)))
            for k,s in sorted(stats.iteritems()):
                textType.append(Func(self.append_line,"    %s = %d"%(k,int(s))))
                textType.append(Wait(0.1))
        textType.append(Func(self.user_input))
        textType.start()
        
    def append_line(self,txt):
        lines = self.output.getText().split('\n')
        del lines[0] # scroll
        lines.append(txt)
        self.output.setText('\n'.join(lines))
        
    def append_char(self,char):
        self.output.appendText(char)
    
    def overwrite_line(self,idx,txt):
        lines = self.output.getText().split('\n')
        lines[idx] = txt
        self.output.setText('\n'.join(lines))

    def parse_cmd(self,str):
        self.append_line("%s> %s"%(self.name,str))
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
        
    def square_bracket_checker(self, argToCheck):
        if match(r"\[.*\]",argToCheck) is not None:
            self.append_line("Parameters shouldn't have square brackets around them")
    
    def ip_validator(self, is_this_an_ip) :
        if is_this_an_ip == 'localhost' : return True
        m = match(r"(\d+)\.(\d+)\.(\d+)\.(\d+)",is_this_an_ip)
        if not m or len(m.groups()) != 4: return False
        for section in m.groups():
            if not (1 <= len(section) <= 3 or  0 <= int(section) <= 255): return False
        return True
            
    def load_finished(self):
        idx = len(LOADINGTEXT.splitlines())+1
        self.overwrite_line(idx,"Loading... Done.")
        self.overwrite_line(idx+2,"Players: (up/down to change team)")
        self.overwrite_line(idx+5,"Game: (left/right to change type)")
        self.overwrite_line(idx+9,"When everyone is ready, press 'b' to begin")
        self.overwrite_line(idx+10,"To go back to the shell, press 'x'")
        self.g.client.send("player %s"%self.name)
        self.screen.accept('b',self.staging_ready)
        self.screen.accept('x',self.exit_staging)
        self.screen.accept('arrow_up', self.g.send_color_change, [1])
        self.screen.accept('arrow_down', self.g.send_color_change, [-1])
        self.screen.accept('arrow_right', self.g.send_type_change, [1])
        self.screen.accept('arrow_left', self.g.send_type_change, [-1])
        
    def staging_ready(self):
        min_p = self.g.get_mode().min_players
        if len(self.g.players) < min_p:
            idx = len(LOADINGTEXT.splitlines())+9
            self.overwrite_line(idx, ("Sorry, this game mode needs at least %d players"%min_p).center(60))
        else:
            self.g.client.send('start')
    
    def exit_staging(self):
        self.g.client.send('unreg %s'%self.name)
        self.screen.ignoreAll()
        self.user_input()
        self.append_line("Welcome back!")
    
    def refresh_staging(self):
        player_names = ("%s (%s)"%(n,TEAM_COLORS.keys()[t]) for n,t in self.g.players.iteritems())
        type,desc = self.g.get_mode().name, self.g.get_mode().desc
        name_idx = len(LOADINGTEXT.splitlines())+4
        self.overwrite_line(name_idx," | ".join(player_names).center(60))
        self.overwrite_line(name_idx+3,type.upper().center(60))
        self.overwrite_line(name_idx+4,desc.center(60))
        self.overwrite_line(name_idx+5,'')

    def finish_staging(self):
        idx = len(LOADINGTEXT.splitlines())+1
        self.overwrite_line(idx+2,"Players:")
        self.overwrite_line(idx+5,"Game:")
        self.overwrite_line(idx+9,"Starting game...")
        self.overwrite_line(idx+10,"")
        self.screen.ignoreAll()
    
    def show_sync(self):
        idx = len(LOADINGTEXT.splitlines())+1
        self.overwrite_line(idx+9,"Synchronizing watches...")
            
    def main(self, client):
        print "creating new Game object"
        self.g = Game(client,self,100.0)
        
    ########## HERE THERE BE SETTINGS #############

    def settingsPrompt(self,cmd,arglist=[],sudo=False):
        self.input.stash()
        self.prompt.stash()
        self.output.stash()
        self.screen.ignoreAll()
        self.settingsOutput = OnscreenText(text="\n"*24, pos=(-1.31,0.95), scale=0.07, 
                                           align=TextNode.ALeft, mayChange=True, fg=(1,1,1,0.8), font=self.font)
        self.controlIndex = 0
        self.validBindings = ['a','b','c','d','e','f','g','h','i','j','k',
               'l','m','n','o','p','q','r','s','t','u','v','w','x','y','n','z',
               '`','-','=','[',']','\\',';',"'",',','.','/','+','*',    #note that \\ is the \ key     
               'f1','f2','f3','f4','f5','f6','f7','f8','f9','f10','f11','f12','scroll_lock',
               'backspace','insert','home','page_up','num_lock','tab','delete','end',
               'page_down','caps_lock','arrow_left','arrow_right','mouse1','mouse2','mouse3',
               'lshift','rshift','lcontrol','rcontrol','lalt','ralt','space'
               ]
        self.invalidBindings = ['0','1','2','3','4','5','6','7','8','9','escape']
        self.settingsBorder = OnscreenImage(image="%s/white_border.png" % TEXTURE_PATH, pos = (-.33,0,.662), 
                                         scale=(0.97, 1, 0.04), color=(1,1,1,.8), parent=self.settingsOutput)
        self.settingsBorder.setTransparency(TransparencyAttrib.MAlpha)
        self.selected = False
        self.draftControls = dict(self.controls)
        self.refreshSettingsPrompt(None)
        self.settingsOutput.accept('arrow_up', self.incrementControlIndex,[-1])
        self.settingsOutput.accept('arrow_down', self.incrementControlIndex,[1])
        Sequence(Wait(0.001), Func(self.settingsOutput.accept,'enter', self.youPressedEnter)).start()
        for key in self.validBindings :
            self.settingsOutput.accept(key, self.refreshSettingsPrompt,[key])
        for key in self.invalidBindings :
            self.settingsOutput.accept(key, self.refreshSettingsPrompt,[key])
    
    def incrementControlIndex(self, change):
        if self.selected : # bind this key
            if change == -1 : self.refreshSettingsPrompt('arrow_up')
            elif change == 1 : self.refreshSettingsPrompt('arrow_down')
            return
        self.controlIndex += change
        if self.controlIndex < 0 : self.controlIndex = len(self.draftControls)-1+3
        if self.controlIndex > len(self.draftControls)-1+3 : self.controlIndex = 0
        settingsBorderPos = self.settingsBorder.getPos()
        settingsBorderZPos = 0.662 - (.076*self.controlIndex)
        if self.controlIndex > len(self.draftControls)-1 : settingsBorderZPos -= (.076*3)
        self.settingsBorder.setPos(settingsBorderPos[0], settingsBorderPos[1], settingsBorderZPos)
        
    def formatControls(self, control, press=True, uppercase=False):
        result = self.controls[control]
        if result == 'mouse1' : result = 'Left click'
        elif result == 'mouse2' : result = 'Middle click'
        elif result == 'mouse3' : result = 'Right click'
        elif press : result = "Press " + result
        if uppercase : result = result.upper()
        return result
    
    def youPressedEnter(self):
        if self.controlIndex == len(self.draftControls)-1+3-2 : 
            self.loadDefaultSettings()
            self.draftControls = self.controls
            self.refreshSettingsPrompt(None)
            return
        elif self.controlIndex == len(self.draftControls)-1+3-1 : 
            self.destroySettingsPrompt()
            return
        elif self.controlIndex == len(self.draftControls)-1+3 : 
            self.exitSettingsPrompt()
            return
        if self.selected : 
            self.refreshSettingsPrompt('enter')
            return
        self.selected = True
        self.settingsBorder.setColor(0,1,0,.8)
        
    def deselect(self):
        self.selected = False
        self.settingsBorder.setColor(1,1,1,.8)
    
    def refreshSettingsPrompt(self, key):
        if not self.selected and key : return
        self.deselect()
        errorMessage = ""
        if key :
            if 0 > self.controlIndex or self.controlIndex > len(self.draftControls) - 1 : return
            if key not in self.validBindings and key not in ['arrow_up','arrow_down','enter'] :
                errorMessage = "Invalid binding"
            elif key in self.draftControls.values() :
                errorMessage = "Key already in use"
            else :
                self.draftControls[('forward', 'backward', 'moveleft', 'moveright', 'shoot', 'jump', 
                               'collect', 'scope', 'pause', 'changePerspective', 'toggleMusic', 
                               'toggleSoundEffects', 'scores')[self.controlIndex]] = key
        format = dict(self.draftControls)
        format['error'] = errorMessage
        settingsText = """  Below are the game controls.
  Use the up and down arrows to select a control,
  and press enter to change it
                
  Move forward: \t\t\t%(forward)s
  Move backward: \t\t%(backward)s
  Move left: \t\t\t%(moveleft)s
  Move right: \t\t\t%(moveright)s
  Shoot: \t\t\t%(shoot)s
  Jump:\t\t\t\t%(jump)s
  Collect a program:\t\t%(collect)s
  Scope: \t\t\t%(scope)s
  Pause:\t\t\t\t%(pause)s
  Change perspective:\t\t%(changePerspective)s
  Toggle background music:\t%(toggleMusic)s
  Toggle sound effects:\t\t%(toggleSoundEffects)s
  Show scores:\t\t\t%(scores)s
  
  %(error)s
  
  Restore default settings
  Exit without saving
  Save and exit"""%format
        self.settingsOutput.setText(settingsText)
        
    def loadDefaultSettings(self):
        self.controls = {'forward': 'w', 'backward': 's', 'moveleft': 'a', 'moveright': 'd',
                    'shoot': 'mouse1', 'jump': 'space', 'collect': 'e', 'scope': 'mouse3',
                    'pause': 'p', 'changePerspective': 'f', 'toggleMusic': 'm', 
                    'toggleSoundEffects': 'n', 'scores': 'tab'}
        
    def exitSettingsPrompt(self):
        self.controls = self.draftControls
        dump(self.draftControls,open(CONTROLSFILE,'wb'),-1)
        self.destroySettingsPrompt()
        self.append_line("Settings saved")
        
    def destroySettingsPrompt(self):
        self.settingsOutput.ignoreAll()
        self.settingsBorder.destroy()
        self.settingsOutput.destroy()
        self.output.unstash()
        self.prompt.unstash()
        self.input.unstash()        
        self.screen.accept('arrow_up',self.history,[True])
        self.screen.accept('arrow_down',self.history,[False])
        self.screen.accept('tab', self.tab_completion)

    #### HERE THERE BE SHELL COMMANDS ####
    
    def start_game(self,cmd,arglist=[],sudo=False):
        if len(arglist) < 2:
            self.append_line("Usage: %s [port_num] [host_ip]"%cmd)
            self.append_line("  join the specified server, to get the game started")
        else:               
            try :
                port = int(arglist[0])
            except ValueError:
                self.append_line("Error: Invalid format for port number")
                self.square_bracket_checker(arglist[0])
                return
            if not self.ip_validator(arglist[1]) :
                self.append_line("Error: Invalid format for IP address")
                self.square_bracket_checker(arglist[1])
                return 
            try :
                client = Client(arglist[1],port)
            except EnvironmentError :
                self.append_line("Error: Can't find a host on that IP and port")
                return
            loadingScreen = Sequence(Func(self.hide_inputs))#,Func(self.output.setText,""))
            format = dict(self.controls)
            for value in format :
                if format[value] == 'mouse1' : format[value] = 'left click'
                elif format[value] == 'mouse2' : format[value] = 'middle click'
                elif format[value] == 'mouse3' : format[value] = 'right click'
            for line in (LOADINGTEXT%format).splitlines():
                loadingScreen.append(Func(self.append_line, line))
                loadingScreen.append(Wait(0.05))
            loadingScreen.append(Func(self.append_line,""))
            loadingScreen.append(Func(self.append_line,"Loading... "))
            for _ in range(23 - len(LOADINGTEXT.splitlines())):
                loadingScreen.append(Func(self.append_line, ""))
                loadingScreen.append(Wait(0.05))
            loadingScreen.append(Func(self.main, client))
            loadingScreen.start()
    
    def start_server(self,cmd,arglist=[],sudo=False):
        if len(arglist) != 1:
            self.append_line("Usage: %s [port_num]"%cmd)
            self.append_line("  start a server on this machine")
            return
        try :
            port = int(arglist[0])
        except ValueError:
            self.append_line("Error: Invalid format for port number")
            self.square_bracket_checker(arglist[0])
            return
        if self.server is not None:
            if self.server.port == port:
                self.append_line("A server is already running on that port.")
                return
            self.append_line("Moving server from port %d to port %d"%(self.server.port,port))
            self.server.shutdown()
        else:
            adverb = "vigorously " if sudo else ""
            self.append_line("Starting server %son port %d..."%(adverb,port))
        self.server = Server(port)
        self.append_line("Server active, use 'join %d %s' to connect"%(port,self.get_IP()))
            
    def quit(self,cmd,arglist=[],sudo=False):
        Sequence(Func(self.append_line,"Saving scores..."),Wait(0.5),
                 Func(self.append_line,"Done."),Wait(0.5),
                 Func(taskMgr.stop)).start()
    
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
            cmdlst = self.cmd_dict.keys()
            writeln = lambda cmds: self.append_line("  "+"\t\t".join(sorted(cmds,key=str.__len__)))
            for cmds in izip(*[iter(cmdlst)]*3):
                writeln(cmds)
            rem = len(cmdlst)%3
            if rem != 0:
                writeln(cmdlst[-rem:])
        else:
            for (cmd,effect) in self.help_cmds.iteritems():
                self.append_line("   " + cmd + " -- " + effect)
        self.append_line("Enter a command by itself for usage instructions")

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
        if len(self.hiscores) == 0:
            self.append_line("No high scores found. Play a few games and check back later!")
            return
        if sudo and len(arglist) > 0 and arglist[0] == 'clear':
            self.append_line("Clearing high scores list")
            self.hiscores = {}
            return
        statnames = ['wins','deaths','Player_kill','Drone_kill','damage_taken']
        playnames = self.hiscores.keys()
        maxpname = max(max(len(n) for n in playnames),5)
        self.append_line("Name%s| %s"%(" "*(maxpname-4)," ".join(statnames)))
        for p in sorted(self.hiscores,key=lambda k:self.hiscores[k]['wins']):
            stats = []
            for k in statnames:
                if k in self.hiscores[p]:
                    stats.append(str(self.hiscores[p][k]).center(len(k)))
                else:
                    stats.append('0'.center(len(k)))
            self.append_line("%s| %s"%(p.ljust(maxpname)," ".join(stats)))
    
    def make(self,cmd,arglist=[],sudo=False):
        if ' '.join(arglist) == "me a sandwich":
            if sudo:
                self.append_line("Okay.")
            else:
                self.append_line("What? Make it yourself.")
        elif len(arglist) > 0 and arglist[0] in ["clean", "realclean"]:
            if sudo:
                self.append_line("All done.")
            else:
                self.append_line("Clean it yourself!")
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
    
    def su(self,cmd,arglist=[],sudo=False):
        if len(arglist) == 0 and not sudo:
            self.append_line("Usage: %s [new_username]"%cmd)
            self.append_line("  change your username")
        else:
            self.name = 'root' if sudo else '_'.join(arglist)
            self.set_prompt_str()
            self.append_line("Username changed to: %s"%self.name)
    
    def ifconfig(self,cmd,arglist=[],sudo=False):
        self.append_line("inet addr:%s..."%self.get_IP())
        self.append_line("And that's all you need to know!")
        
    def get_IP(self):
        if getOS() == 'Windows': # epic hacks
            return Popen('ipconfig',stdout=PIPE).stdout.readlines()[7].split()[-1]
        else:
            return Popen('ifconfig',stdout=PIPE).stdout.readlines()[1].split(':')[1].split()[0]
    
    def default(self,cmd,arglist=[],sudo=False):
        def_cmds = {'emacs': "Sorry, emacs is not installed",
                    'vi'   : "Sorry, vi is not installed",
                    'vim'  : "Sorry, vim is not installed",
                    'nethack': "You zap a cursed wand of magic missile. It bounces! You die.",
                    'cat': "meow",
                    'sleep': "zzz... Nap time over! You awake refreshed.",
                    'kill': "Killing is wrong!",
                    'killall': "My God, what have you done?",
                    'top': "Come on, I'm ONLY running 'Chain of Command'",
                    'ps': "Come on, I'm ONLY running 'Chain of Command'",
                    'reboot': "System restarted... I'm fast, aren't I?",
                    'nano': "Really, now? Poor editor choice: -5 CHA",
                    'pico': "Really, now? Poor editor choice: -5 CHA",
                    'ed'  : "Really, now? Poor editor choice: -5 CHA",
                    'tar': "Aww, now I'm all sticky..."}
        if cmd in def_cmds:
            self.append_line(def_cmds[cmd])
        elif cmd in ['notepad','textedit','gedit']:
            self.append_line("What do I look like, a graphical user interface?")
        elif cmd in ['apt-get','aptitude']:
            self.append_line("I'm fine with the way I am, thanks.")
        elif cmd in ['cmp', 'diff']:
            self.append_line("Everybody's different in their own way.")
        elif cmd in ['touch','finger']:
            self.append_line("That would be inappropriate")
        elif cmd in ['cd', 'chown', 'chmod', 'chgrp', 'cp', 'mkdir', 'mv']:
            if sudo:
                self.append_line("No really. A BAD IDEA.")
            else:
                self.append_line("Mmm, I don't think that would be a good idea...")
        
        elif sudo:
            self.append_line("sudo: %s: command not found" % cmd)
        else:
            self.append_line("%s: command not found" % cmd)
    
# end Shell class

def klaatu_barada_nikto():
    # callable in-game with tricky shell-fu
    return "Aha! An easter egg. We should do something cool here"

if __name__ == '__main__':
    s = Shell(False)
    # hack the history, but only for our debugging runs
    s.cmd_hist = ["","join 1337 localhost", "host 1337"]
    run()
