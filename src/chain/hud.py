from time import time
from pandac.PandaModules import TransparencyAttrib 
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from constants import *

#Constants
EMPTY_PROG_STR = "|        |"
HUD_PROG_SCALE = 0.06
HUD_FG, HUD_BG = (0, 0, 0, 0.8), (1, 1, 1, 0.8)

class HUD(object):
    def __init__(self,player):
        self.player = player
        base.setFrameRateMeter(True)
        self.crosshairs = OnscreenImage(image="%s/crosshairs.tif" % TEXTURE_PATH, pos=(-0.025, 0, 0), scale=0.05)
        self.crosshairs.setTransparency(TransparencyAttrib.MAlpha)
        
        self.programHUD = [
            OnscreenText(text=EMPTY_PROG_STR, pos=(-0.3, -0.9), scale=HUD_PROG_SCALE,
                         fg=HUD_FG, bg=HUD_BG, mayChange=True),
            OnscreenText(text=EMPTY_PROG_STR, pos=(0, -0.9), scale=HUD_PROG_SCALE,
                         fg=HUD_FG, bg=HUD_BG, mayChange=True),
            OnscreenText(text=EMPTY_PROG_STR, pos=(0.3, -0.9), scale=HUD_PROG_SCALE,
                         fg=HUD_FG, bg=HUD_BG, mayChange=True)
		]
        # red flash for indicating hits
        self.redScreen = None
        self.flashRed = Sequence(Func(self.flash_red), Wait(0.25), Func(self.flash_red))
        #self.healthHUD = OnscreenText(text="HP: %d" % player.health, pos=(-0.9, 0.9), fg=HUD_FG, bg=HUD_BG, mayChange=True)
        self.healthBAR = DirectWaitBar(range = 100, value = 100, pos = (0,.85,.85), barColor = (0,1,0,1), scale = 0.5)
        self.killHUD = OnscreenText(text="Kills: %d" % player.killcount(), pos=(-0.9, 0.8), fg=HUD_FG, bg=HUD_BG, mayChange=True)
        self.musicHUD = OnscreenImage(image="%s/music_off.png" % TEXTURE_PATH, pos=(-1.2,0,0.92), scale=HUD_PROG_SCALE)
        self.musicHUD.setImage(image="%s/music_on.png" % TEXTURE_PATH)
        self.musicHUD.setTransparency(TransparencyAttrib.MAlpha)
        self.soundHUD = OnscreenImage(image="%s/speaker_off.png" % TEXTURE_PATH, pos=(-1.2,0,0.82), scale=HUD_PROG_SCALE)
        self.soundHUD.setImage(image="%s/speaker_on.png" % TEXTURE_PATH)
        self.soundHUD.setTransparency(TransparencyAttrib.MAlpha)
        #timer
        self.timer = OnscreenText(text="Time:", pos=(0,0.9), scale=(0.08), fg=HUD_FG, bg=HUD_BG, mayChange=True)
        taskMgr.doMethodLater(0.01, self.timerTask, 'timerTask')

    def show_scores(self):
        #self.crosshairs.hide()
        try: self.score_screen.destroy()
        except: pass
        players = reversed(sorted(self.player.game.players.values(), key=lambda p: p.killcount()))
        score_str = "\n".join(["%s:\t\t%d"%(p.name,p.killcount()) for p in players])
        self.score_screen = OnscreenText(text="Kills: \n"+score_str,bg=(1,1,1,0.8),pos=(0,0.75))
    
    def hide_scores(self):
        #self.crosshairs.show()
        try: self.score_screen.destroy()
        except: pass
    
    def toggle_background_music(self):
        if base.musicManager.getActive():
            self.musicHUD.setImage("%s/music_on.png" % TEXTURE_PATH)
            self.musicHUD.setTransparency(TransparencyAttrib.MAlpha)
        else:
            self.musicHUD.setImage("%s/music_off.png" % TEXTURE_PATH)
            self.musicHUD.setTransparency(TransparencyAttrib.MAlpha)
        
    def toggle_sound_effects(self):
        if base.sfxManagerList[0].getActive():
            self.soundHUD.setImage("%s/speaker_on.png" % TEXTURE_PATH)
            self.soundHUD.setTransparency(TransparencyAttrib.MAlpha)
        else:
            self.soundHUD.setImage("%s/speaker_off.png" % TEXTURE_PATH)
            self.soundHUD.setTransparency(TransparencyAttrib.MAlpha)

    def target(self):
        objHit,spotHit = self.player.findCrosshairHit()
        if objHit in self.player.game.drones or objHit in self.player.game.players: #turn the crosshairs red
            self.crosshairs.setImage("%s/crosshairs_locked.tif" % TEXTURE_PATH)
        elif objHit in self.player.game.programs:
            self.crosshairs.setImage("%s/crosshairs_program.tif" % TEXTURE_PATH)
        else:
            self.crosshairs.setImage("%s/crosshairs.tif" % TEXTURE_PATH)
        self.crosshairs.setTransparency(TransparencyAttrib.MAlpha)
    
    def hit(self):
        self.flashRed.start() # flash the screen red
        #self.healthHUD.setText("HP: %d" % self.player.health)
        self.healthBAR['value'] = self.player.health
        if self.player.health <= 20:
            self.healthBAR['barColor'] = (1,0,0,1)
        
    def heal(self):
        if hasattr(self, "healthBAR") and self.healthBAR:
            #self.healthHUD.setText("HP: %d" % self.player.health)
            self.healthBAR['value'] = self.player.health
            if self.player.health > 20:
                self.healthBAR['barColor'] = (0,1,0,1)
    
    def collect(self,i,prog_name):
        self.programHUD[i].setText("|  %s  |" % prog_name)
    
    def drop(self, prog_index):
        self.programHUD[prog_index].setText(EMPTY_PROG_STR)
        
    def add_slot(self):
        x = self.programHUD[-1].getPos()[0]
        self.programHUD.append(OnscreenText(text=EMPTY_PROG_STR,
                        pos=(x + 0.3, -0.9), scale=HUD_PROG_SCALE,
                        fg=HUD_FG, bg=HUD_BG, mayChange=True))
        for txt in self.programHUD:
            #they couldn't just make it simple and override getX() could they?
            txt.setX(txt.getPos()[0] - 0.15)
        
    def add_kill(self):
        self.killHUD.setText("Kills: %d" % self.player.killcount())
    
    def destroy_HUD(self):
        self.crosshairs.destroy() 
        for programDisp in self.programHUD : programDisp.destroy() 
        #self.healthHUD.destroy()
        #self.healthHUD = None
        self.healthBAR.destroy()
        self.healthBAR = None
        self.killHUD.destroy() 
        self.killHUD = None
        self.musicHUD.destroy()
        self.musicHUD = None
        self.soundHUD.destroy()
        self.soundHUD = None
        self.hide_scores()
        base.setFrameRateMeter(False) 
    
    def flash_red(self):
        if not self.redScreen:
            self.redScreen = OnscreenImage(image="%s/red_screen.png" % TEXTURE_PATH, pos=(0, 0, 0), scale=(2, 1, 1))
            self.redScreen.setTransparency(TransparencyAttrib.MAlpha)
        else:
            self.redScreen.destroy()
            self.redScreen = None

    def timerTask(self, task):
        game = self.player.game
        game.gameTime = game.endTime - time()
        self.timer.setText("Time: %.2f seconds"%game.gameTime)
        if 0 < game.gameTime < 10:
            self.timer.setFg((1,0,0,0.8))
        elif game.gameTime <= 0:
            self.timer.setText("Time: %.2f seconds"%0)
            #gray screen here
            game.game_over()
            return task.done
        return task.again