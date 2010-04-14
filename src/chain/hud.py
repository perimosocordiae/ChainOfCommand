from time import time
from pandac.PandaModules import TransparencyAttrib, Point3
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from constants import *

#Constants
EMPTY_PROG_STR = "[ - ]"
HUD_SCALE = 0.06
HUD_FG, HUD_BG = (0, 0, 0, 0.8), (1, 1, 1, 0.8)

class HUD(object):
    def __init__(self,player):
        self.player = player
        self.font = player.game.font
        base.setFrameRateMeter(True)
        self.crosshairs = OnscreenImage(image="%s/crosshairs.tif" % TEXTURE_PATH, pos=(-0.025, 0, 0), scale=0.05)
        self.crosshairs.setTransparency(TransparencyAttrib.MAlpha)
        
        self.bottomHUD = DirectFrame(frameSize=(-0.77,0.77,-0.04,0.04), frameColor=HUD_BG, pos=(0,0,-0.96))
        self.programHUD = [
            OnscreenText(text=EMPTY_PROG_STR, pos=(-0.3, -0.98), scale=HUD_SCALE,
                         fg=HUD_FG, font=self.font, mayChange=True),
            OnscreenText(text=EMPTY_PROG_STR, pos=(0, -0.98), scale=HUD_SCALE,
                         fg=HUD_FG, font=self.font, mayChange=True),
            OnscreenText(text=EMPTY_PROG_STR, pos=(0.3, -0.98), scale=HUD_SCALE,
                         fg=HUD_FG, font=self.font, mayChange=True)
		]
        # red flash for indicating hits
        self.redScreen = None
        self.flashRed = Sequence(Func(self.flash_red), Wait(0.25), Func(self.flash_red))
        self.grayScreen = None
        self.topHUD = DirectFrame(frameSize=(-0.57,0.57,-0.04,0.04), frameColor=HUD_BG, pos=(0,0,0.96))
        self.healthBAR = DirectWaitBar(range=100, value=100, pos=(0,0,0.88), barColor=(0,1,0,0.5), scale=0.5, text="", text_scale=0.12, text_font=self.font, frameColor=HUD_BG, sortOrder=2)
        self.healthBAR.setSx(0.57)
        self.healthBAR.setTransparency(TransparencyAttrib.MAlpha)
        self.killHUD = OnscreenText(text="Kills:%d" % player.killcount(), pos=(-0.39, 0.94), scale=HUD_SCALE, fg=HUD_FG, font=self.font, mayChange=True)
        self.musicHUD = OnscreenImage(image="%s/music_off.png" % TEXTURE_PATH, pos=(0.43,0,0.96), scale=0.04)
        self.musicHUD.setImage(image="%s/music_on.png" % TEXTURE_PATH)
        self.musicHUD.setTransparency(TransparencyAttrib.MAlpha)
        self.soundHUD = OnscreenImage(image="%s/speaker_off.png" % TEXTURE_PATH, pos=(0.51,0,0.96), scale=0.04)
        self.soundHUD.setImage(image="%s/speaker_on.png" % TEXTURE_PATH)
        self.soundHUD.setTransparency(TransparencyAttrib.MAlpha)
        self.timer = OnscreenText(text="Time:", pos=(0,0.94), scale=HUD_SCALE, fg=HUD_FG, font=self.font, mayChange=True)
        
    def setup_radar(self):
        print "setup radar"
        self.radar_background = OnscreenImage(image="%s/white_circle.png" % TEXTURE_PATH, color=(.871,.722,.529, 0.5), 
                                            scale=0.25, pos=(1.08, 0, -0.75))
        self.radar_background.setTransparency(TransparencyAttrib.MAlpha)
        self.radarPoints = []
        taskMgr.doMethodLater(0.01, self.radarTask, 'radarTask')
        
        
    def start_timer(self):
        taskMgr.doMethodLater(0.01, self.timerTask, 'timerTask')
    
    def destroy_radar(self):
        print "destroy radar"
        if hasattr(self, "radar_background") and self.radar_background is not None:
            self.radar_background.removeNode()
        taskMgr.remove('radarTask')
        if hasattr(self, "radarPoints") and self.radarPoints is not None:
            for radarPoint in self.radarPoints : radarPoint.destroy()

    def show_scores(self):
        #self.crosshairs.hide()
        try: self.score_screen.destroy()
        except: pass
        players = reversed(sorted(self.player.game.players.values(), key=lambda p: p.killcount()))
        score_str = "\n".join(["%s:\t\t%d"%(p.name,p.killcount()) for p in players])
        #self.score_screen = OnscreenText(text="Kills: \n"+score_str,bg=(1,1,1,0.8),pos=(0,0.75))
        self.score_screen = DirectLabel(text="Kills: \n"+score_str, pos=(-0.1,0,0.75), frameColor=HUD_BG, text_fg=HUD_FG, text_font=self.font, scale=HUD_SCALE, sortOrder=4)
                                        
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
        self.healthBAR['value'] = self.player.health
        hpct = self.player.health/100.0
        self.healthBAR['barColor'] = (1-hpct,hpct,0,1)
        
    def heal(self):
        if hasattr(self, "healthBAR") and self.healthBAR is not None:
            self.healthBAR['value'] = self.player.health
            hpct = self.player.health/100.0
            self.healthBAR['barColor'] = (1-hpct,hpct,0,1)
    
    def collect(self,i,prog_name):
        self.programHUD[i].setText("[%s]" % prog_name)
    
    def drop(self, prog_index):
        self.programHUD[prog_index].setText(EMPTY_PROG_STR)
        
    def add_slot(self):
        x = self.programHUD[-1].getPos()[0]
        self.programHUD.append(OnscreenText(text=EMPTY_PROG_STR,
                        pos=(x + 0.3, -0.98), scale=HUD_SCALE,
                        fg=HUD_FG, font=self.font, mayChange=True))
        for txt in self.programHUD:
            #they couldn't just make it simple and override getX() could they?
            txt.setX(txt.getPos()[0] - 0.15)
        
    def add_kill(self):
        self.killHUD.setText("Kills:%d" % self.player.killcount())
    
    def destroy_HUD(self):
        self.crosshairs.destroy() 
        for programDisp in self.programHUD : programDisp.destroy() 
        if self.bottomHUD:
            self.bottomHUD.destroy()
            self.bottomHUD = None
        if self.topHUD:
            self.topHUD.destroy()
            self.topHUD = None
        if self.healthBAR:
            self.healthBAR.destroy()
            self.healthBAR = None
        if self.killHUD:
            self.killHUD.destroy() 
            self.killHUD = None
        if self.musicHUD:
            self.musicHUD.destroy()
            self.musicHUD = None
        if self.soundHUD:
            self.soundHUD.destroy()
            self.soundHUD = None
        if self.timer:
            self.timer.destroy()
            self.timer = None
        if self.grayScreen:
            self.grayScreen.destroy()
            self.grayScreen = None
        self.hide_scores()
        self.destroy_radar()
        base.setFrameRateMeter(False) 
    
    def flash_red(self):
        if not self.redScreen:
            self.redScreen = OnscreenImage(image="%s/red_screen.png" % TEXTURE_PATH, pos=(0, 0, 0), scale=(2, 1, 1))
            self.redScreen.setTransparency(TransparencyAttrib.MAlpha)
        else:
            self.redScreen.destroy()
            self.redScreen = None
            
    def display_gray(self):
        if not self.grayScreen:
            self.grayScreen = DirectFrame(frameSize=(-1.34,1.34,-1,1), frameColor=HUD_FG, sortOrder=3)
    
    def destroy_gray(self):
        self.grayScreen.destroy()
        self.grayScreen = None
    
    def timerTask(self, task):
        game = self.player.game
        game.gameTime = game.endTime - time()
        self.timer.setText("Time:%.2fs"%game.gameTime)
        if 0 < game.gameTime < 10:
            self.timer.setFg((1,0,0,0.8))
        elif game.gameTime <= 0:
            self.timer.setText("Time:%.2fs"%0)
            game.game_over()
            return task.done
        return task.again
    
    def radarTask(self, task):
        for radarPoint in self.radarPoints : radarPoint.destroy()
        game = self.player.game
        myPos = self.player.get_model().getPos()
        clipConstant = game.tile_size * 2 * self.player.radar_mod()
        clipConstantSquared = clipConstant * clipConstant
        scaleConstant = clipConstant/0.40
        for drone in game.drones :
            vectorToDrone = game.drones[drone].get_model().getPos() - myPos
            if (vectorToDrone.lengthSquared() < clipConstantSquared) :
                vectorToDrone = -self.player.get_model().getRelativeVector(render, vectorToDrone)/scaleConstant
                radarPoint = OnscreenImage(image="%s/white_circle.png" % TEXTURE_PATH, pos = (vectorToDrone.getX(),0,vectorToDrone.getY()), 
                                         scale=0.05, color=(.6,.6,.6,.8), parent=self.radar_background)
                self.radarPoints.append(radarPoint)
        for player in game.players :
            vectorToPlayer = game.players[player].get_model().getPos() - myPos
            if (vectorToPlayer.lengthSquared() < clipConstantSquared) :
                vectorToPlayer = -self.player.get_model().getRelativeVector(render, vectorToPlayer)/scaleConstant
                teamColor = TEAM_COLORS[game.players[player].color]
                radarPoint = OnscreenImage(image="%s/white_circle.png" % TEXTURE_PATH, pos = (vectorToPlayer.getX(),0,vectorToPlayer.getY()), 
                                         scale=0.05, color=teamColor+(0.8,), parent=self.radar_background)
                self.radarPoints.append(radarPoint)
        return task.cont
