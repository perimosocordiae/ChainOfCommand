import sys
from math import sin, cos, radians, sqrt, pi
from direct.task import Task
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import (Shader, CollisionNode, CollisionRay, CollisionSphere,
    CollisionHandlerQueue, TransparencyAttrib, BitMask32, Vec2, Vec3, Point3, VBase3, TextureStage)
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.InputStateGlobal import inputState
from eventHandler import PlayerEventHandler
from projectile import Laser
from agent import Agent
from constants import *

#Constants
MOTION_MULTIPLIER = 100.0
TURN_MULTIPLIER = 0.3
LOOK_MULTIPLIER = 0.2
JUMP_SPEED = 100.0 #make sure this stays less than SAFE_FALL - he should be able to jump up & down w/o getting hurt!
TRON_ORIGIN_HEIGHT = 10
LASER_SPEED = 5000
BASE_DAMAGE = 10 #arbitrary
EMPTY_PROG_STR = "|        |"
HUD_PROG_SCALE = 0.08
HUD_FG, HUD_BG = (0, 0, 0, 0.8), (1, 1, 1, 0.8)

class Player(Agent):
    def __init__(self, game, name):
        super(Player, self).__init__(game, name)
        self.programs = [None, None, None]
        self.killcount = 0
        self.handleEvents = True
        self.laserGlow = False
        self.camera = None
        self.setup_collider()
        #add the camera collider:
        self.collisionQueue = CollisionHandlerQueue()
    
    def setup_collider(self):
        self.collider = self.attach_collision_node(self.name, CollisionSphere(0, 0, 0, 10), DRONE_COLLIDER_MASK)
        self.pusher = self.attach_collision_node("%s_wall" % self.name, CollisionSphere(0, 0, 0, 12), WALL_COLLIDER_MASK)
        #self.pusher.show()
    
    def set_glow(self, glow):
        if glow:
            self.tron.setTexture(self.ts, self.glow)
        else:
            self.tron.clearTexture(self.ts)
    
    def get_shield_sphere(self):
        return self.collider
    
    def get_model(self):
        return self.tron
    
    def findCrosshairHit(self):
        base.cTrav.traverse(render)
        if self.collisionQueue.getNumEntries() == 0: return "",""
        # This is so we get the closest object
        self.collisionQueue.sortEntries()
        
        for i in range(self.collisionQueue.getNumEntries()):
            pickedObj = self.collisionQueue.getEntry(i).getIntoNodePath().getName()
            pickedSpot = self.collisionQueue.getEntry(i).getSurfacePoint(render)
            if 'donthitthis' in pickedObj: continue
            if '_wall' in pickedObj: continue
            if not (self.name in pickedObj): break
        return pickedObj, pickedSpot
    
    def set_laser_glow(self, glow):
        self.laserGlow = glow
    
    def die(self):
        del self.game.players[self.name]
        self.collider.removeNode()
        self.pusher.removeNode()
        self.tron.cleanup()
        self.tron.removeNode()
        print "%s died!"%self.name
    
    def get_base_damage(self):
        return BASE_DAMAGE
    
    def jump(self):
        if self.handleEvents: super(Player, self).jump() 
    
    def get_origin_height(self):
        return TRON_ORIGIN_HEIGHT
    
    def get_jump_speed(self):
        return JUMP_SPEED
        
    def StartMovingAnim(self):
        if self.running: return
        self.running = True
        self.shortRun.loop()
        
    def StopMovingAnim(self):
        if not self.running: return
        self.tron.stop()
        if self.shortRun.isPlaying():
            run = self.shortRun
            t = run.getT()
            run.start(startT=t)
        self.running = False
        
    def load_model(self):
        #glowShader=Shader.load("%s/glowShader.sha"%MODEL_PATH)
        self.tron = Actor.Actor("%s/tron" % MODEL_PATH, {"running":"%s/tron_anim_updated" % MODEL_PATH})
        self.tron.reparentTo(render)
        self.tron.setScale(0.4, 0.4, 0.4)
        self.tron.setHpr(0, 0, 0)
        self.tron.setPos(-4, 34, TRON_ORIGIN_HEIGHT)
        self.tron.pose("running", 46)
        self.runInterval = self.tron.actorInterval("running", startFrame=0, endFrame=46)

        self.shortRun = self.tron.actorInterval("running", startFrame=25, endFrame=46)
        self.runLoop = Sequence(self.runInterval, Func(lambda i: i.loop(), self.shortRun))
        self.running = False
        Laser() # pre-cache laser model
        
        self.ts = TextureStage('ts')
        self.ts.setMode(TextureStage.MGlow)
        self.glow = loader.loadTexture("%s/tron-glow_on.png"%MODEL_PATH)
        self.ts.setSort(9)
        #self.no_glow = loader.loadTexture(NO_GLOW)
        #self.tron.setTexture(self.ts, self.no_glow)
        self.set_glow(False)
    
    def get_camera(self):
        if self.camera == None:
            self.camera = self.tron.attachNewNode("Camera")
        return self.camera
    
    def setup_camera(self):
        # the camera follows tron
        self.get_camera().reparentTo(self.tron)
        self.get_camera().setPos(0, 40, TRON_ORIGIN_HEIGHT)
        self.get_camera().setHpr(180, 0, 0)
        
    def initialize_camera(self):
        cameraNode = CollisionNode('cameracnode_%s'%self.name)
        cameraNP = self.get_camera().attachNewNode(cameraNode)
        cameraNP.node().setIntoCollideMask(0)
        self.cameraRay = CollisionRay(0, self.get_camera().getY(), 0, 0, 1, 0)
        cameraNode.addSolid(self.cameraRay)
        base.cTrav.addCollider(cameraNP, self.collisionQueue)
    
    def switchPerspective(self):
        #Switch between 3 perspectives
        if not self.handleEvents: return
        if self.get_camera().getY() > 60:
            self.get_camera().setPos(0, 0, TRON_ORIGIN_HEIGHT)
        elif self.get_camera().getY() > 20:
            self.get_camera().setPos(0, 100, TRON_ORIGIN_HEIGHT)
        else:
            self.get_camera().setPos(0, 40, TRON_ORIGIN_HEIGHT)
        self.cameraRay.setOrigin(Point3(0, self.get_camera().getY(), 0))
    
    def zoomIn(self):
        if not self.handleEvents: return
        if self.get_camera().getY() > 0:
            self.get_camera().setY(self.get_camera().getY() - 2)
        self.cameraRay.setOrigin(Point3(0, self.get_camera().getY(), 0))
            
    def zoomOut(self):
        if not self.handleEvents: return
        if self.get_camera().getY() < 100:
            self.get_camera().setY(self.get_camera().getY() + 2)
        self.cameraRay.setOrigin(Point3(0, self.get_camera().getY(), 0))
    
    def shoot(self):
        if not self.handleEvents: return
        #first get a ray coming from the camera and see what it first collides with
        objHit,spotHit = self.findCrosshairHit()
        print objHit
        if objHit in self.game.drones:
            d = self.game.drones[objHit]
            d.hit(self.damage())
            print "hit drone %s for %d damage" % (objHit, self.damage())
            if d.is_dead():
                print "killed it!"
                self.killcount += 1
                self.killHUD.setText("Kills: %d" % self.killcount)
        elif objHit in self.game.programs:
            p = self.game.programs[objHit]
            p.hit(self.damage())
            print "hit program %s for %d damage" % (objHit, self.damage())
            if p.is_dead():
                print "Oh no, you blew up a program!"
        elif objHit in self.game.players:
            p = self.game.players[objHit]
            p.hit(self.damage())
            print "hit %s for %d damage" % (objHit, self.damage())
            if p.is_dead():
                print "you killed %s!"%objHit
                self.killcount += 1
                self.killHUD.setText("Kills: %d" % self.killcount)
        #end if 
        self.fire_laser(objHit,spotHit)
   
    def fire_laser(self, objHit, spotHit):
        startPos = self.tron.getPos()
        startPos.setZ(startPos.getZ() + 2)
        laser = Laser()
        laser.set_pos(startPos)
        laser.model.setScale(16.0)
        laser.model.setHpr(self.tron.getHpr())
        laser.model.setH(laser.model.getH())
        laser.model.setP(-self.get_camera().getP())
        h, p = radians(self.tron.getH()), radians(self.get_camera().getP())
        pcos = cos(p)
        if self.laserGlow:
            laser.set_glow(True)
        #the .005 is a fudge factor - it just makes things work better
        laser.fire(Vec3(sin(h) * pcos, -cos(h) * pcos, sin(p) + 0.005) * LASER_SPEED)
    
    def collect(self):
        #sound/message depends on status
        i, prog = super(Player, self).collect()
        if not prog:
            if i >= 0: 
                print "No empty slots!"
            else:
                print "No program to pick up!"
        else:
            self.sounds['yes'].play()
            print "Program get: %s" % prog.name
            if i >= 0:
                self.programHUD[i].setText("|  %s  |" % prog.name)
    
    def drop(self, i):
        if (super(Player, self).drop(i)):
            print "Program dropped: %s" %self.programs[i]
            self.programHUD[i].setText("|        |")
    
    def move(self,vel,hpr,anim,firing):
        self.tron.setFluidPos(self.tron.getPos() + (vel * SERVER_TICK))
        self.tron.setH(self.tron.getH() + hpr.getX())
        self.get_camera().setP(self.get_camera().getP() + hpr.getY())
        print self.get_camera().getP()
        if anim == 'start':  self.StartMovingAnim()
        elif anim == 'stop': self.StopMovingAnim()
        if firing:
            self.shoot()

class LocalPlayer(Player):
    def __init__(self, game, name):
        super(LocalPlayer, self).__init__(game, name)
        self.hpr = VBase3(0,0,0)
        Sequence(Wait(SERVER_TICK), Func(self.game.network_listen)).loop()
        self.shooting = False
        self.setup_camera()
        self.setup_HUD()
        self.setup_shooting()
        self.eventHandle = PlayerEventHandler(self)
        self.setup_sounds()
        self.add_background_music()
    
    def move(self,vel,hpr,anim, firing):
        super(LocalPlayer,self).move(vel,hpr,anim,firing)
        self.shooting = False
        center = base.win.getXSize() / 2
        base.win.movePointer(0, center, center)
        
    def initialize_camera(self):
        super(LocalPlayer,self).initialize_camera()
        #base.camLens.setNearFar(10, 3000)
    
    def get_camera(self):
        return base.camera
    
    def die(self):
        super(LocalPlayer,self).die()
        #TODO something better here!
        sys.exit("GAME OVER, YOU DEAD") 
        
    def setup_sounds(self):
        keys = ['laser', 'yes', 'snarl']
        fnames = ["%s/hilas.mp3", "%s/Collect_success.mp3", "%s/Snarl.mp3"]
        self.sounds = dict(zip(keys, [base.sfxManagerList[0].getSound(f % SOUND_PATH) for f in fnames]))
        for s in self.sounds.itervalues():
            s.setVolume(0.3)
            
    def add_background_music(self):
        # from http://www.newgrounds.com/audio/listen/287442
        self.backgroundMusic = base.musicManager.getSound("%s/City_in_Flight.mp3"%SOUND_PATH)
        self.backgroundMusic.setVolume(0.3)
        self.backgroundMusic.setTime(35)  # music automatically starts playing when this command is issued
        print "Track: City in Flight in Neon Light" # attribution
        print "Author: Trevor Dericks"
    
    def toggle_background_music(self):
        base.enableMusic(not base.musicManager.getActive())
        if base.musicManager.getActive():
            self.backgroundMusic.setTime(35)
        
    def toggle_sound_effects(self):
        base.enableSoundEffects(not base.sfxManagerList[0].getActive())

    def target(self):
        objHit,spotHit = self.findCrosshairHit()
        if objHit in self.game.drones or objHit in self.game.players: #turn the crosshairs red
            self.crosshairs.setImage("%s/crosshairs_locked.tif" % MODEL_PATH)
        elif objHit in self.game.programs:
            self.crosshairs.setImage("%s/crosshairs_program.tif" % MODEL_PATH)
        else:
            self.crosshairs.setImage("%s/crosshairs.tif" % MODEL_PATH)
        self.crosshairs.setTransparency(TransparencyAttrib.MAlpha)
    
    def click(self):
        #self.shoot()
        delay = self.rapid_fire()
        self.shooting = True
        taskMgr.doMethodLater(delay, self.updateShotTask, "updateShotTask")
        
    def clickRelease(self):
        self.shooting = False
        taskMgr.remove("updateShotTask")
        
    def hit(self, amt=0):
        super(Player, self).hit(amt)
        self.sounds['snarl'].play()
        self.flashRed.start() # flash the screen red
        print "hit! health = %d" % self.health
        self.healthHUD.setText("HP: %d" % self.health)
    
    def fire_laser(self, objHit, spotHit):
        super(LocalPlayer, self).fire_laser(objHit, spotHit)
        self.sounds['laser'].play()
        
    def add_slot(self):
        currentCount = len(self.programs)
        if currentCount < 9:
            self.programs.append(None)
            x = self.programHUD[-1].getPos()[0]
            self.programHUD.append(OnscreenText(text=EMPTY_PROG_STR,
                            pos=(x + 0.3, -0.9), scale=HUD_PROG_SCALE,
                            fg=HUD_FG, bg=HUD_BG, mayChange=True))
            for txt in self.programHUD:
                #they couldn't just make it simple and override getX() could they?
                txt.setX(txt.getPos()[0] - 0.15)
        
    def setup_HUD(self):
        #show health, programs, crosshairs, etc. (some to come, some done now)
        base.setFrameRateMeter(True)
        self.crosshairs = OnscreenImage(image="%s/crosshairs.tif" % MODEL_PATH, pos=(-0.025, 0, 0), scale=0.05)
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
        # health status
        self.healthHUD = OnscreenText(text="HP: %d" % self.health, pos=(-0.9, 0.9), fg=HUD_FG, bg=HUD_BG, mayChange=True)
        # kill counter
        self.killHUD = OnscreenText(text="Kills: %d" % self.killcount, pos=(-0.9, 0.8), fg=HUD_FG, bg=HUD_BG, mayChange=True)
    
    def flash_red(self):
        if not self.redScreen:
            self.redScreen = OnscreenImage(image="%s/red_screen.png" % MODEL_PATH, pos=(0, 0, 0), scale=(2, 1, 1))
            self.redScreen.setTransparency(TransparencyAttrib.MAlpha)
        else:
            self.redScreen.destroy()
            self.redScreen = None

    def setup_camera(self):
        super(LocalPlayer,self).setup_camera()
        inputState.watch('forward', 'w', 'w-up') 
        inputState.watch('backward', 's', 's-up')
        inputState.watch('moveleft', 'a', 'a-up')
        inputState.watch('moveright', 'd', 'd-up')
        taskMgr.add(self.updateCameraTask, "updateCameraTask")
    
    def setup_shooting(self):
        inputState.watch('shoot', 'mouse1', 'mouse1-up')
    
    def updateShotTask(self, task):
        #self.shoot()
        self.shooting = True
        return task.again
        
    #Task to move the camera
    def updateCameraTask(self, task):
        self.target()
        if not self.handleEvents: return Task.cont
        self.handleGravity()
        self.LookAtMouse()
        
        anim = '"a"' # placeholder
        if not self.in_air(): # no mid-air corrections!
            cmds = [ c for c in ['forward', 'backward', 'moveleft', 'moveright'] if inputState.isSet(c)]
            new_vel = self.get_xy_velocity(cmds)
            self.velocity.setX(new_vel.getX())
            self.velocity.setY(new_vel.getY())
            if not len(cmds)==0: anim = '"start"'
            else:                anim = '"stop"'
        
        # send command to move tron, based on the values in self.velocity
        self.game.client.send(':'.join([self.name,str(self.velocity),str(self.hpr),anim,str(self.shooting)]))
        #print self.velocity * globalClock.getDt()
        return Task.cont
    
    def get_xy_velocity(self, cmds):
        new_vel = Vec2(0, 0)
        for cmd in cmds:
            new_vel += self.get_partial_velocity(cmd)
        
        new_vel.normalize()
        new_vel *= MOTION_MULTIPLIER
        return new_vel
    
    def get_partial_velocity(self, dir):
        h = radians(self.tron.getH())
        if dir in ['moveleft', 'moveright']: h += pi / 2.0
        if dir in ['forward', 'moveleft']:
            return Vec2(sin(h), -cos(h))
        else:
            return Vec2(-sin(h), cos(h))
    
    def LookAtMouse(self):
        md = base.win.getPointer(0)
        x, y = md.getX(), md.getY()
        center = base.win.getXSize() / 2
        self.hpr.setX(-(TURN_MULTIPLIER * (x - center)))
        newP = base.camera.getP()-(LOOK_MULTIPLIER * (y - center))
        #keep within +- 90 degrees
        newP = max(min(newP, 80), -80)
        self.hpr.setY(newP - base.camera.getP())
        #make sure lifter continues to point straight down
        #angle = radians(self.tron.getP())
        #self.lifterRay.setDirection(Vec3(0,-sin(angle), -cos(angle)))
    
