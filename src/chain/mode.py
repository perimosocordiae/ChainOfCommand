from direct.interval.IntervalGlobal import Parallel, Func, Sequence, Wait
from direct.gui.OnscreenText import OnscreenText
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
        self.level.destroy()
        if hasattr(self,'drone_adder'):
            self.drone_adder.finish()
    
    def post_environment_init(self): pass
    def load_level(self,environ): pass
    def score(self,player): return 0
    
class CaptureTheFlag(Mode):
    def __init__(self,game):
        super(CaptureTheFlag,self).__init__(game,20)
        self.fragLimit = 3
        self.name = 'capture the --flag'
        self.desc = "Steal another team's flag to score"
        self.ctf_scores = {}
        self.min_players = 2
    
    def post_environment_init(self):
        self.ctf_scores = dict((p.color,0) for p in self.game.players.itervalues())
    
    def load_level(self,environ):
        self.level = SniperLevel(self.game, environ)
    
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
        self.desc = "Score by bringing programs back to base"
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
        self.desc = "Attack another team's base to score"
        self.min_players = 1
        
    def load_level(self,environ):
        self.level = SniperLevel(self.game, environ)
    
    def score(self,player): return 0

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
            self.level = CubeLevel(self.game, environ)
    
    def score(self,player):
        if 'team' in self.name.split():
            return sum(p.stats.get('LocalPlayer_kill',0)+p.stats.get('Player_kill',0) for p in player.my_team())
        return player.stats.get('LocalPlayer_kill',0)+player.stats.get('Player_kill',0)+player.stats.get('Drone_kill',0)

PROMPTS = ["Welcome to the tutorial for \nChain of Command.\nPress c to continue.\n\n\n",
            "Use the mouse to look around.",
            "Use WASD to move around the world.\nW moves your player forwards.\nS moves your player backwards.\nA moves your player left.\nD moves your player right.",
            "Left click to shoot.",
            "Press e to pick up programs.\nYou can see your collected programs at the bottom of the screen.\nPress the number keys to drop a program.",
            "Press spacebar to jump.\n(Watch your height. Falling causes damage.)",
            "At the top of the screen is your health bar and game info.",
            "Press tab to see the current scores.\nPress p to pause the game.",
            "Press f or use the scroll wheel to change your perspective.",
            "Press n to toggle sound effects.\nPress m to toggle background music.",              
            "You've reached the end of our tutorial. Enjoy the game!\nPress Esc to exit the tutorial."]

class Tutorial(Mode):
    def __init__(self,game):
        super(Tutorial,self).__init__(game,0)
        self.name = 'tutorial'
        self.desc = "Learn how to play"
        self.continue_str = 'Press c to continue.'
        self.tutorialScreen = OnscreenText(text='', pos=(-1.31,0.75), scale=0.07, mayChange=True, 
                                           bg=(0,0,0,0.9), fg=(0,1,0,0.8), font=self.game.shell.font, wordwrap=35)
        self.tutorialScreen.hide()
        self.min_players = 1
    
    def load_level(self,environ):
        self.level = CubeLevel(self.game, environ)
    
    def post_environment_init(self):
        self.tutorialScreen.show() # maybe here
        self.tutorialScreen.accept('c', self.advance_tutorial)
        
    def read_prompt(self):
        for p in PROMPTS:
            yield p
    
    def advance_tutorial(self):
        self.tutorialScreen.setText(self.read_prompt())
    
    def destroy(self):
        self.tutorialScreen.ignoreAll()
        self.tutorialScreen.destroy()
        delattr(self, 'tutorialScreen')