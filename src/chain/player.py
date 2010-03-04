import sys
from math import sin, cos, radians, sqrt, pi
from itertools import ifilter
from direct.task import Task
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import (Shader, CollisionNode, CollisionRay, CollisionSphere,
    CollisionHandlerQueue, TransparencyAttrib, BitMask32, Vec2, Vec3, Point3)
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.InputStateGlobal import inputState
from eventHandler import PlayerEventHandler
from projectile import Laser
from agent import Agent
from constants import *

#Constants
MODEL_PATH = "../../models"
SOUND_PATH = "../../sounds"
MOTION_MULTIPLIER = 3.0
TURN_MULTIPLIER = 0.5
LOOK_MULTIPLIER = 0.3

GRAVITATIONAL_CONSTANT = -0.15 # = -9.81 m/s^2 in theory! (not necessarily in computer world, but it's what's familiar)
SAFE_FALL = -5.0 #fall velocity after which damage is induced
FALL_DAMAGE_MULTIPLIER = 12.0 #How much to damage Tron per 1 over safe fall
TERMINAL_VELOCITY = -50.0
JUMP_SPEED = 4.0 #make sure this stays less than SAFE_FALL - he should
                 #be able to jump up & down w/o getting hurt!
TRON_ORIGIN_HEIGHT = 10
LASER_SPEED = 5000
BASE_DAMAGE = 10 #arbitrary

class Player(Agent):

    def __init__(self, game, name):
        super(Player, self).__init__(game)
        self.programs = [None, None, None]
        self.name = name
        self.killcount = 0
        self.load_model()
        self.setup_collider()
        self.setup_camera()
        self.setup_HUD()
        self.setup_shooting()
        self.eventHandle = PlayerEventHandler(self)
        self.setup_sounds()
        self.handleEvents = True
        self.canCollect = None
        self.velocity = Vec3(0, 0, 0)
        #add the camera collider:
        self.collisionQueue = CollisionHandlerQueue()
        self.floorQueue = CollisionHandlerQueue()
        base.cTrav.addCollider(self.lifter, self.floorQueue)
    
    def initialize_camera(self):
        cameraNode = CollisionNode('cameracnode')
        cameraNP = base.camera.attachNewNode(cameraNode)
        self.cameraRay = CollisionRay(0, base.camera.getY(), 0, 0, 1, 0)
        cameraNode.addSolid(self.cameraRay)
        base.cTrav.addCollider(cameraNP, self.collisionQueue)
        base.camLens.setNearFar(10, 3000)
    
    def setup_sounds(self):
        keys = ['laser', 'yes', 'no', 'snarl']
        fnames = ["%s/hilas.mp3", "%s/Collect_success.mp3", "%s/Collect_fail.mp3", "%s/Snarl.mp3"]
        self.sounds = dict(zip(keys, [base.sfxManagerList[0].getSound(f % SOUND_PATH) for f in fnames]))
        for s in self.sounds.itervalues():
            s.setVolume(0.3)
    
    def toggle_background_music(self):
        base.enableMusic(not base.musicManager.getActive()) 
        # bug, can't turn on once it's off
        
    def toggle_sound_effects(self):
        base.enableSoundEffects(not base.sfxManagerList[0].getActive())

    def target(self):
        objHit = self.findCrosshairHit()
        if objHit in self.game.drones: #turn the crosshairs red
            self.crosshairs.setImage("%s/crosshairs_locked.tif" % MODEL_PATH)
        elif objHit in self.game.programs:
            self.crosshairs.setImage("%s/crosshairs_program.tif" % MODEL_PATH)
        else:
            self.crosshairs.setImage("%s/crosshairs.tif" % MODEL_PATH)
        self.crosshairs.setTransparency(TransparencyAttrib.MAlpha)
    
    def click(self):
        self.shooting = True
        self.shoot()
        
    def clickRelease(self):
        self.shooting = False
    
    def shoot(self):
        if not self.handleEvents: return
        #first get a ray coming from the camera and see what it first collides with
        objHit = self.findCrosshairHit()
        if objHit in self.game.drones:
            d = self.game.drones[objHit]
            d.hit(self.damage())
            print "hit drone %s for %d damage" % (objHit, self.damage())
            if d.is_dead():
                print "killed it!"
                self.killcount += 1
                self.killHUD.setText("Frags: %d" % self.killcount)
        elif objHit in self.game.programs:
            p = self.game.programs[objHit]
            p.hit(self.damage())
            print "hit program %s for %d damage" % (objHit, self.damage())
            if p.is_dead():
                print "Oh no, you blew up a program!"
        #end if 
        self.fire_laser()
   
    def fire_laser(self):
        self.sounds['laser'].play()
        startPos = self.tron.getPos()
        startPos.setZ(startPos.getZ() + 2)
        laser = Laser()
        laser.set_pos(startPos)
        laser.model.setScale(16.0)
        laser.model.setHpr(self.tron.getHpr())
        laser.model.setH(laser.model.getH())
        laser.model.setP(-base.camera.getP())
        h, p = radians(self.tron.getH()), radians(base.camera.getP())
        pcos = cos(p)
        #the .005 is a fudge factor - it just makes things work
        laser.fire(Vec3(sin(h) * pcos, -cos(h) * pcos, sin(p) + 0.005) * LASER_SPEED)
    
    def findCrosshairHit(self):
        base.cTrav.traverse(render)
        if self.collisionQueue.getNumEntries() == 0: return ""
        # This is so we get the closest object
        self.collisionQueue.sortEntries()
        for i in range(self.collisionQueue.getNumEntries()):
            pickedObj = self.collisionQueue.getEntry(i).getIntoNodePath().getName()
            if 'donthitthis' in pickedObj: continue 
            if not (self.name in pickedObj): break
        return pickedObj

    def damage(self):
        d = BASE_DAMAGE
        for p in ifilter(lambda p: p != None, self.programs):
            d = p.damage_mod(d)
        return d

    def shield(self):
        s = 1.0 # no shield
        for p in ifilter(lambda p: p != None, self.programs):
            s = p.shield_mod(s)
        return s
    
    def rapid_fire(self):
        a = False; # no rapid-fire
        for p in ifilter(lambda p: p != None, self.programs):
            a = p.rapid_fire_mod(a)
        return a
    
    def die(self):
        #TODO something better here!
        sys.exit("GAME OVER, YOU DEAD")    
    
    def hit(self, amt=0):
        super(Player, self).hit(amt)
        self.sounds['snarl'].play()
        self.flashRed.start() # flash the screen red
        print "hit! health = %d" % self.health
        self.healthHUD.setText("HP: %d" % self.health)
        if self.health <= 0:
            self.die()
    
    def collect(self, i):
        if self.canCollect:
            prog = self.canCollect
            #for i,p in enumerate(self.programs):
            #    if not p: break
            #else:
            #    self.sounds['no'].play() 
            #    print "No empty slots!"
            #    return
            self.sounds['yes'].play()
            print "Program get: %s" % prog.name
            self.programs[i] = prog
            self.programHUD[i].setText("|  %s  |" % prog.name)
            prog.disappear()
            del self.game.programs[prog.unique_str()]  
            self.canCollect = None
        else:
            print "Program dropped: %s" %self.programs[i]
            if self.programs[i] != None:
                self.programs[i].reappear(self.tron.getPos())
                self.programs[i] = None
                self.programHUD[i].setText("|        |")    
        
    def load_model(self):
        #glowShader=Shader.load("%s/glowShader.sha"%MODEL_PATH)
        self.tron = Actor.Actor("%s/tron" % MODEL_PATH, {"running":"%s/tron_anim_updated" % MODEL_PATH})
        self.tron.reparentTo(render)
        self.tron.setScale(0.4, 0.4, 0.4)
        self.tron.setHpr(0, 0, 0)
        self.tron.setPos(-4, 34, 150)
        self.tron.pose("running", 46)
        self.runInterval = self.tron.actorInterval("running", startFrame=0, endFrame=46)

        self.shortRun = self.tron.actorInterval("running", startFrame=25, endFrame=46)
        self.runLoop = Sequence(self.runInterval, Func(lambda i: i.loop(), self.shortRun))
        self.running = False
        Laser() # pre-cache laser model

    def setup_collider(self):
        self.collider = self.attach_collision_node(self.name, CollisionSphere(0, 0, 0, 10), DRONE_COLLIDER_MASK)
        self.pusher = self.attach_collision_node("%s_wall" % self.name, CollisionSphere(0, 0, 0, 12), WALL_COLLIDER_MASK)
        #self.pusher.show()
        self.lifterRay = CollisionRay(0, 0, 0, 0, 0, -1) #ray pointing down
        self.lifter = self.attach_collision_node("%s_floor" % self.name, self.lifterRay, FLOOR_COLLIDER_MASK)
    
    def attach_collision_node(self, name, solid, mask):
        c = self.tron.attachNewNode(CollisionNode(name))
        c.node().addSolid(solid)
        c.node().setFromCollideMask(mask)
        c.node().setIntoCollideMask(mask)
        return c
        
    def setup_HUD(self):
        #show health, programs, crosshairs, etc. (some to come, some done now)
        base.setFrameRateMeter(True)
        self.crosshairs = OnscreenImage(image="%s/crosshairs.tif" % MODEL_PATH, pos=(-0.025, 0, 0), scale=0.05)
        self.crosshairs.setTransparency(TransparencyAttrib.MAlpha)
        none_str, scale, fg, bg = "|        |", 0.08, (0, 0, 0, 0.8), (1, 1, 1, 0.8)
        self.programHUD = [
            OnscreenText(text=none_str, pos=(-0.3, -0.9), scale=scale, fg=fg, bg=bg, mayChange=True),
            OnscreenText(text=none_str, pos=(0, -0.9), scale=scale, fg=fg, bg=bg, mayChange=True),
            OnscreenText(text=none_str, pos=(0.3, -0.9), scale=scale, fg=fg, bg=bg, mayChange=True)
		]
        # red flash for indicating hits
        self.redScreen = None
        self.flashRed = Sequence(Func(self.flash_red), Wait(0.25), Func(self.flash_red))
        # health status
        self.healthHUD = OnscreenText(text="HP: %d" % self.health, pos=(-0.9, 0.9), fg=fg, bg=bg, mayChange=True)
        # kill counter
        self.killHUD = OnscreenText(text="Frags: %d" % self.killcount, pos=(-0.9, 0.8), fg=fg, bg=bg, mayChange=True)
    
    def flash_red(self):
        if not self.redScreen:
            self.redScreen = OnscreenImage(image="%s/red_screen.png" % MODEL_PATH, pos=(0, 0, 0), scale=(2, 1, 1))
            self.redScreen.setTransparency(TransparencyAttrib.MAlpha)
        else:
            self.redScreen.destroy()
            self.redScreen = None

    def setup_camera(self):
        inputState.watch('forward', 'w', 'w-up') 
        inputState.watch('backward', 's', 's-up')
        inputState.watch('moveleft', 'a', 'a-up')
        inputState.watch('moveright', 'd', 'd-up')
        taskMgr.add(self.updateCameraTask, "updateCameraTask")
        # the camera follows tron
        base.camera.reparentTo(self.tron)
        base.camera.setPos(0, 40, TRON_ORIGIN_HEIGHT)
        base.camera.setHpr(180, -30, 0)
    
    def switchPerspective(self):
        #Switch between 3 perspectives
        if not self.handleEvents: return
        if base.camera.getY() > 60:
            base.camera.setPos(0, 0, TRON_ORIGIN_HEIGHT)
        elif base.camera.getY() > 20:
            base.camera.setPos(0, 100, TRON_ORIGIN_HEIGHT)
        else:
            base.camera.setPos(0, 40, TRON_ORIGIN_HEIGHT)
        self.cameraRay.setOrigin(Point3(0, base.camera.getY(), 0))
    
    def zoomIn(self):
        if not self.handleEvents: return
        if base.camera.getY() > 0:
            base.camera.setY(base.camera.getY() - 2)
        self.cameraRay.setOrigin(Point3(0, base.camera.getY(), 0))
            
    def zoomOut(self):
        if not self.handleEvents: return
        if base.camera.getY() < 100:
            base.camera.setY(base.camera.getY() + 2)
        self.cameraRay.setOrigin(Point3(0, base.camera.getY(), 0))
        
    def setup_shooting(self):
        self.shooting = False
        inputState.watch('shoot', 'mouse1', 'mouse1-up')
        taskMgr.add(self.updateShotTask, "updateShotTask")
        
    def updateShotTask(self, task):
        if self.shooting and self.rapid_fire() : self.shoot()
        return Task.cont
        
    #Task to move the camera
    def updateCameraTask(self, task):
        self.target()
        if not self.handleEvents: return Task.cont
        self.handleGravity()
        self.LookAtMouse()
        
        if not self.in_air(): # no mid-air corrections!
            cmds = [ c for c in ['forward', 'backward', 'moveleft', 'moveright'] if inputState.isSet(c)]
        
            new_vel = Vec2(0, 0)
            for cmd in cmds:
                new_vel += self.get_velocity(cmd)
        
            new_vel.normalize()
            new_vel *= MOTION_MULTIPLIER
            self.velocity.setX(new_vel.getX())
            self.velocity.setY(new_vel.getY())

            if not len(cmds) == 0: self.StartMovingAnim()
            else:                  self.StopMovingAnim()

        # actually move tron, based on the values in self.velocity
        self.tron.setFluidPos(self.tron.getPos() + self.velocity)
        return Task.cont
    
    def get_velocity(self, dir):
        h = radians(self.tron.getH())
        if dir in ['moveleft', 'moveright']: h += pi / 2.0
        if dir in ['forward', 'moveleft']:
            return Vec2(sin(h), -cos(h))
        else:
            return Vec2(-sin(h), cos(h))

    def handleGravity(self):
        #in the future, have 2 rays - one above, one below, so he can't jump
        #through things?  Or let him jump through things.  If he can't, adapt
        #2nd half of if statement to include 2nd ray.
        z_vel = self.velocity.getZ()
        if self.in_air() or z_vel > 0:
            self.velocity.setZ(max(z_vel + GRAVITATIONAL_CONSTANT, TERMINAL_VELOCITY)) # jump / fall
        else:
            #We hit (or stayed on) the ground...
            #how fast are we falling now? Use that to determine potential damage
            if z_vel < SAFE_FALL:
                damage = (-z_vel + SAFE_FALL) * FALL_DAMAGE_MULTIPLIER
                self.hit(damage)
            else:
                floorZ = self.floorQueue.getEntry(0).getSurfacePoint(render).getZ()
                self.tron.setZ(floorZ + TRON_ORIGIN_HEIGHT) # hack?
            self.velocity.setZ(0)
    
    def in_air(self):
        base.cTrav.traverse(render)
        if self.floorQueue.getNumEntries() == 0: return True # technically
        self.floorQueue.sortEntries()
        floorZ = self.floorQueue.getEntry(0).getSurfacePoint(render).getZ()
        return self.tron.getZ() > floorZ + TRON_ORIGIN_HEIGHT
    
    def jump(self):
        if not self.handleEvents: return
        if not self.in_air():
            self.velocity.setZ(JUMP_SPEED)  # he's on the ground - let him jump
    
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
    
    def LookAtMouse(self):
        md = base.win.getPointer(0)
        x, y = md.getX(), md.getY()
        center = base.win.getXSize() / 2
        if base.win.movePointer(0, center, center):
            self.tron.setH(self.tron.getH() - (TURN_MULTIPLIER * (x - center)))
            #self.tron.setP(self.tron.getP() + (TURN_MULTIPLIER * (y - center)))
            newP = base.camera.getP() - (LOOK_MULTIPLIER * (y - center))
            #keep within +- 90 degrees
            newP = max(min(newP, 80), -80)
            base.camera.setP(newP)
            #make sure lifter continues to point straight down
            angle = radians(self.tron.getP())
            #self.lifterRay.setDirection(Vec3(0,-sin(angle), -cos(angle)))
        
