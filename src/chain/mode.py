from direct.interval.IntervalGlobal import Parallel, Func, Sequence, Wait
from direct.gui.OnscreenText import OnscreenText
from itertools import izip
from level import SniperLevel,CubeLevel,Beaumont

class Mode(object):
    def __init__(self,game,drone_rate):
        self.game = game
        self.fragLimit = 9999
        self.gameLength = -1
        if drone_rate > 0:
            self.drone_adder = Sequence(Wait(drone_rate), Func(self.game.send_drone_signal))
    
    def start_drones(self):
        if hasattr(self,'drone_adder'):
            self.drone_adder.loop()
    
    def destroy(self):
        if hasattr(self,'drone_adder'):
            self.drone_adder.finish()
        self.level.destroy()
    
    def post_environment_init(self): pass
    def load_level(self,environ): pass
    def score(self,player): return 0
    
class CaptureTheFlag(Mode):
    def __init__(self,game):
        super(CaptureTheFlag,self).__init__(game,20)
        self.fragLimit = 3
        self.name = 'capture the --flag'
        self.desc = "Steal another team's flag to score points"
        self.ctf_scores = {}
        self.min_players = 2
    
    def post_environment_init(self):
        self.ctf_scores = dict((p.color,0) for p in self.game.players.itervalues())
    
    def load_level(self,environ):
        self.level = SniperLevel(self.game, environ, addFlags=True)
    
    def score(self,player):
        if player.color in self.ctf_scores:
            return self.ctf_scores[player.color]
        return 0

class ForTheHoard(Mode):
    def __init__(self,game):
        super(ForTheHoard,self).__init__(game,20)
        self.gameLength = 180
        self.ctf_scores = {}
        self.name = 'for the hoard'
        self.desc = "Hoard programs at your base to score points"
        self.min_players = 1
        
    def load_level(self,environ):
        self.level = SniperLevel(self.game, environ)
    
    def score(self,player):
        if not hasattr(self,'level'): return 0
        base = self.level.bases[player.color]
        progs_in_base = 0
        for p in self.game.programs.itervalues():
            if base.has_point(p.get_model().getPos()):
                progs_in_base += 1
        return progs_in_base

class Pwnage(Mode):
    def __init__(self,game):
        super(Pwnage,self).__init__(game,20)
        self.gameLength = 180
        self.ctf_scores = {}
        self.name = 'pwnage'
        self.desc = "Attack another team's base to score points"
        self.min_players = 1
        
    def load_level(self,environ):
        self.level = SniperLevel(self.game, environ)
    
    def score(self,player):
        if not hasattr(self,'level'): return 0
        if player.color not in self.level.bases: return 0
        return sum(p.stats.get('BaseTerminal_kill',0) for p in player.my_team())

class Deathmatch(Mode):
    def __init__(self,game,is_team,is_timed):
        super(Deathmatch,self).__init__(game,20)
        self.fragLimit = 15 if is_team else 5
        self.gameLength = 180 if is_timed else -1
        if not is_team:
            self.min_players = 1
            if not is_timed:
                self.name = 'deathmatch'
                self.desc = "Every man for himself, first to 5 kills wins"
            else:
                self.name = 'timed deathmatch'
                self.desc = "Every man for himself, highest score after 3 minutes wins"
        else: # team game 
            self.min_players = 2
            if not is_timed:
                self.name = 'team deathmatch'
                self.desc = "Team vs team, first to 15 kills wins"
            else:
                self.name = 'timed team deathmatch'
                self.desc = "Team vs team, highest score after 3 minutes wins"
                
    def load_level(self,environ):
        if 'team' in self.name.split():
            self.level = SniperLevel(self.game, environ)
        else:
            self.level = Beaumont(self.game, environ)
    
    def score(self,player):
        if 'team' in self.name.split():
            return sum(p.stats.get('LocalPlayer_kill',0)+p.stats.get('Player_kill',0) for p in player.my_team())
        return player.stats.get('LocalPlayer_kill',0)+player.stats.get('Player_kill',0)+player.stats.get('Drone_kill',0)

PROMPTS = """Welcome to the tutorial for Chain of Command.
I'm your friendly guide, the Master Control Program.
I'll do my best to make this process simple enough for your tiny human brain.
At each step, press c when you're ready to move on.EOF
Behold my dominion! Bask in its glory!
Move your mouse pointer to look around.EOF
You should probably get moving. I will soon be sending my drones to kill you.
%(forward)s will impel you to run boldly forwards.
%(backward)s will cause you to run backwards like a coward.
%(moveleft)s and %(moveright)s will make you scuttle left and right.EOF
Good. To be sporting, I suppose I'll supply you with a laser.
%(shoot)s is your trigger, and don't you forget it!EOF
You've probably noticed some objects spinning enticingly at various locations. 
Those are programs. Programs are essential to life.
Press %(collect)s to snag them when you get close.EOF
Each program you collect will be added to your Chain Of Command. (See what I did there?)
You can see your current chain the bottom of the screen.
Press the number keys to drop a program.EOF
Sometimes, you may find yourself desiring vertical velocity.
Press %(jump)s to leap into the air.
Try not to hurt yourself.
It would deny me the pleasure of destroying you myself.EOF
You have several more abilities, but I think I'll let you discover those on your own.
You may want to RTFM.EOF
Enjoy your brief stay in the computer.
I know I'll enjoy destroying you.
Press Esc to exit. End Of Line."""

class Tutorial(Mode):
    def __init__(self,game):
        super(Tutorial,self).__init__(game,0)
        self.name = 'tutorial'
        self.desc = "Learn how to play"
        self.tutorialScreen = OnscreenText(text='', pos=(0,0.75), scale=0.07, mayChange=True, 
                                bg=(0,0,0,0.9), fg=(0,1,0,0.8), font=self.game.shell.font, wordwrap=35)
        self.tutorialScreen.hide()
        self.min_players = 1
        self.read_prompt = (p for p in (PROMPTS%self.game.shell.nice_controls()).split('EOF\n')) # generator ftw
    
    def load_level(self,environ):
        self.level = CubeLevel(self.game, environ)
    
    def post_environment_init(self):
        self.tutorialScreen.show() # maybe here
        self.advance_tutorial()
        self.tutorialScreen.accept('c', self.advance_tutorial)
    
    def advance_tutorial(self):
        try:
            p = self.read_prompt.next()
        except StopIteration: return
        self.tutorialScreen.setText(p)
    
    def destroy(self):
        self.tutorialScreen.ignoreAll()
        self.tutorialScreen.destroy()
        delattr(self, 'tutorialScreen')