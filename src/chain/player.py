from math import sin,cos,radians,sqrt
from itertools import ifilter
from direct.task import Task
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import Shader, CollisionNode, CollisionRay, CollisionSphere
from pandac.PandaModules import CollisionHandlerQueue, TransparencyAttrib, BitMask32
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.InputStateGlobal import inputState
from eventHandler import PlayerEventHandler
from projectile import Laser
from agent import Agent
from pandac.PandaModules import Vec3, Point3
import sys

MODEL_PATH = "../../models"
SOUND_PATH = "../../sounds"
#Constants for motion and rotation
MOTION_MULTIPLIER = 3.0
STRAFE_MULTIPLIER = 2.0
TURN_MULTIPLIER = 0.5
DRONE_COLLIDER_MASK = BitMask32.bit(1)
WALL_COLLIDER_MASK = BitMask32.bit(0)

class Player(Agent):

    def __init__(self,game,name):
        super(Player,self).__init__(game)
        self.programs = [None,None,None]
        self.name = name
        self.killcount = 0
        self.inverted = False # look controls
        self.load_model()
        self.setup_collider()
        self.setup_camera()
        self.setup_HUD()
        self.eventHandle = PlayerEventHandler(self)
        self.laserSound = loader.loadSfx(SOUND_PATH + "/hilas.mp3") # load laser sound
        self.laserSound.setVolume(0.3)
        self.collectSound = loader.loadSfx(SOUND_PATH + "/Collect_success.mp3") # load prog collect sound
        self.collectSound.setVolume(0.3)
        self.collectSoundFail = loader.loadSfx(SOUND_PATH + "/Collect_fail.mp3") # load prog collect sound
        self.collectSoundFail.setVolume(0.3)
        self.snarlSound = loader.loadSfx(SOUND_PATH + "/Snarl.mp3")
        self.handle_events(True)
        dummy = Laser() # no jerkiness on first shot
        #add the camera collider:
        self.collisionQueue = CollisionHandlerQueue()
    
    def initialize_camera(self):
        self.cameraNode = CollisionNode('cameracnode')
        self.cameraNP = base.camera.attachNewNode(self.cameraNode)
        self.cameraRay = CollisionRay(0,base.camera.getY(),0,0,1,0)
        self.cameraNode.addSolid(self.cameraRay)
        base.cTrav.addCollider(self.cameraNP, self.collisionQueue)
    
    def target(self):
        objHit = self.findCrosshairHit()
        if objHit in self.game.drones:
            #turn the crosshairs red
            self.crosshairs.setImage("%s/crosshairs_locked.tif"%MODEL_PATH)
            self.crosshairs.setTransparency(TransparencyAttrib.MAlpha)
        elif objHit in self.game.programs:
            self.crosshairs.setImage("%s/crosshairs_program.tif"%MODEL_PATH)
            self.crosshairs.setTransparency(TransparencyAttrib.MAlpha)
        else:
            self.crosshairs.setImage("%s/crosshairs.tif"%MODEL_PATH)
            self.crosshairs.setTransparency(TransparencyAttrib.MAlpha)
    
    def shoot(self):
        if self.handleEvents:
            #first get a ray coming from the camera and see what it first collides with
            objHit = self.findCrosshairHit()
            if objHit in self.game.drones:
                d = self.game.drones[objHit]
                d.hit(self.damage())
                print "hit drone %s for %d damage"%(objHit,self.damage())
                if d.is_dead():
                    print "killed it!"
                    self.killcount += 1
            elif objHit in self.game.programs:
                p = self.game.programs[objHit]
                p.hit(self.damage())
                print "hit program %s for %d damage"%(objHit,self.damage())
                if p.is_dead():
                    print "Oh no, you blew up a program!"
            #end if 
            self.fire_laser(None)
    
    def fire_laser(self, spot):
        #fire a laser at that spot in the world
        #sound from http://www.freesound.org/samplesViewSingle.php?id=18379
        self.laserSound.play()

        startPos = self.tron.getPos()
        startPos.setZ(startPos.getZ() + 2)
        laser = Laser()
        laser.set_pos(startPos)
        laser.model.setScale(16.0)
        laser.model.setHpr(self.tron.getHpr())
        
        mult = 500
        dx = mult*sin(radians(self.tron.getH()))
        dy = -mult*cos(radians(self.tron.getH()))
        dz = -mult*sin(radians(self.tron.getP()))
        laser.set_trajectory(Vec3(dx,dy,dz))
    
    def findCrosshairHit(self):
        base.cTrav.traverse(render)
        if self.collisionQueue.getNumEntries() == 0: return "", None
        # This is so we get the closest object
        self.collisionQueue.sortEntries()
        for i in range(self.collisionQueue.getNumEntries()):
            pickedObj = self.collisionQueue.getEntry(i).getIntoNodePath().getName()
            if 'donthitthis' in pickedObj: continue 
            if not (self.name in pickedObj): break
        
        return pickedObj

    def damage(self):
        d = 10 # arbitrary
        for p in ifilter(lambda p: p != None,self.programs):
            d = p.damage_mod(d)
        return d

    def shield(self):
        s = 1 # no shield
        for p in ifilter(lambda p: p != None,self.programs):
            s = p.shield_mod(s)
        return s
    
    def accuracy(self):
        a = 8; # arbitrary
        for p in ifilter(lambda p: p != None,self.programs):
            a = a.accuracy_mod(a)
        return a
    
    def die(self):
        #TODO something better here!
        sys.exit()    
    
    def hit(self,amt=0):
        super(Player,self).hit(amt)
        # sound from http://www.freesound.org/samplesViewSingle.php?id=41526
        self.snarlSound.play()
        self.flashRed.start() # flash the screen red
        print "hit! health = %d"%self.health
        self.healthHUD.setText("HP: %d"%self.health)
        if self.health <= 0:
            self.die()
    
    def collect(self,prog):
        for i,p in enumerate(self.programs):
            if not p: break
        else:
            # sound from http://www.freesound.org/samplesViewSingle.php?id=33109
            self.collectSoundFail.play() 
            print "No empty slots!"
            return
        # sound from http://www.freesound.org/samplesViewSingle.php?id=33108
        self.collectSound.play()
        print "Program get: %s"%prog.name
        self.programs[i] = prog
        self.programHUD[i].setText("|  %s  |"%prog.name)
        prog.disappear()
        del self.game.programs[prog.unique_str()]      
        
    def load_model(self):
        #glowShader=Shader.load("%s/glowShader.sha"%MODEL_PATH)
        self.tron = Actor.Actor("%s/tron"%MODEL_PATH, {"running":"%s/tron_anim_updated"%MODEL_PATH})
        self.tron.reparentTo(render)
        self.tron.setScale(0.4, 0.4, 0.4)
        self.tron.setHpr(0, 0, 0)
        self.tron.setPos(-4, 34, 10)
        self.tron.pose("running",46)
        self.runInterval = self.tron.actorInterval("running", startFrame=0, endFrame = 46)

        self.shortRun = self.tron.actorInterval("running", startFrame=25, endFrame = 46)
        self.runLoop = Sequence(self.runInterval, Func(lambda i: i.loop(), self.shortRun))
        self.running = False

    def setup_collider(self):
        self.collider = self.tron.attachNewNode(CollisionNode(self.name))
        self.collider.node().addSolid(CollisionSphere(0,0,0,10)) # sphere, for now
        self.collider.node().setFromCollideMask(DRONE_COLLIDER_MASK)
        self.collider.node().setIntoCollideMask(DRONE_COLLIDER_MASK)
        
        self.pusher = self.tron.attachNewNode(CollisionNode(self.name + "_wall"))
        self.pusher.node().addSolid(CollisionSphere(0,0,0,12)) # sphere, for now
        self.pusher.node().setFromCollideMask(WALL_COLLIDER_MASK)
        self.pusher.node().setIntoCollideMask(WALL_COLLIDER_MASK)
        #self.pusher.show()

    def setup_HUD(self):
        #show health, programs, crosshairs, etc. (some to come, some done now)
        base.setFrameRateMeter(True)
        #img_horiz = "%s/horiz_crosshair.jpg"%MODEL_PATH
        #img_vert  = "%s/vert_crosshair.jpg"%MODEL_PATH
        #self.crosshairs = [
        #    OnscreenImage(image = img_horiz, pos = (-0.025, 0, 0), scale = (0.02, 1, .005)),
        #    OnscreenImage(image = img_horiz, pos = ( 0.025, 0, 0), scale = (0.02, 1, .005)),
        #    OnscreenImage(image = img_vert,  pos = (0, 0, -0.025), scale = (0.005, 1, .02)),
        #    OnscreenImage(image = img_vert,  pos = (0, 0,  0.025), scale = (0.005, 1, .02))
        #]
        self.crosshairs = OnscreenImage(image = "%s/crosshairs.tif"%MODEL_PATH, pos = (-0.025, 0, 0), scale = 0.05)
        self.crosshairs.setTransparency(TransparencyAttrib.MAlpha)
        self.programHUD = [
            OnscreenText(text="|  None  |", pos=(-0.3,-0.9), scale=(0.08), fg=(0,0,0,0.8), bg=(1,1,1,0.8), mayChange=True),
            OnscreenText(text="|  None  |", pos=(   0,-0.9), scale=(0.08), fg=(0,0,0,0.8), bg=(1,1,1,0.8), mayChange=True),
            OnscreenText(text="|  None  |", pos=( 0.3,-0.9), scale=(0.08), fg=(0,0,0,0.8), bg=(1,1,1,0.8), mayChange=True)
		]
        
        # red flash for indicating hits
        self.redScreen = None
        self.flashRed = Sequence(Func(self.start_red), Wait(0.25), Func(self.stop_red))
        # health status
        self.healthHUD = OnscreenText(text="HP: %d"%self.health,pos=(-0.9,0.9),fg=(0,0,0,0.8), bg=(1,1,1,0.8),mayChange=True)
    
    def start_red(self):
        if not self.redScreen:
            self.redScreen = OnscreenImage(image = MODEL_PATH+'/red_screen.png', pos = (0, 0, 0), scale = (2,1,1))
            self.redScreen.setTransparency(TransparencyAttrib.MAlpha)

    def stop_red(self):
        if self.redScreen:
            self.redScreen.destroy()
            self.redScreen = None

    def setup_camera(self):
        inputState.watch('forward', 'w', 'w-up') 
        inputState.watch('backward', 's', 's-up')
        inputState.watch('moveleft', 'a', 'a-up')
        inputState.watch('moveright', 'd', 'd-up')
        inputState.watch('left', 'arrow_left', 'arrow_left-up')
        inputState.watch('right', 'arrow_right', 'arrow_right-up')
        inputState.watch('up', 'arrow_up', 'arrow_up-up')
        inputState.watch('down', 'arrow_down', 'arrow_down-up')
        taskMgr.add(self.updateCameraTask, "updateCameraTask")
        # the camerea follows tron
        base.camera.reparentTo(self.tron)
        base.camera.setPos(0, 40, 10)
        base.camera.setHpr(180, 0, 0)
    
    def handle_events(self, handle):
        self.handleEvents = handle
    
    def switchPerspective(self):
        #Switch between 3 perspectives
        if self.handleEvents:
            if base.camera.getY() > 60:
                base.camera.setPos(0, 0, 10)
            elif base.camera.getY() > 20:
                base.camera.setPos(0, 100, 10)
            else:
                base.camera.setPos(0, 40, 10)
            self.cameraRay.setOrigin(Point3(0,base.camera.getY(),0))
    
    def zoomIn(self):
        if self.handleEvents:
            if base.camera.getY() > 0:
                base.camera.setY(base.camera.getY() - 2)
            self.cameraRay.setOrigin(Point3(0,base.camera.getY(),0))
            
    def zoomOut(self):
        if self.handleEvents:
            if base.camera.getY() < 100:
                base.camera.setY(base.camera.getY() + 2)
            self.cameraRay.setOrigin(Point3(0,base.camera.getY(),0))
        
    #Task to move the camera
    def updateCameraTask(self, task):
        #if base.mouseWatcherNode.hasMouse():
        #    #use current mouse location
        #    x=base.mouseWatcherNode.getMouseX()
        #    y=base.mouseWatcherNode.getMouseY()
        #    self.lastX = x
        #    self.lastY = y
        #else:
        #    #use last known mouse location
        #    x = self.lastX
        #    y = self.lastY
        #    
        #if x < -0.1:
        #    self.LookLeft((0.1 - x) * TURN_MULTIPLIER)
        #elif x > 0.1:
        #    self.LookRight((x - 0.1) * TURN_MULTIPLIER)
        #if y < -0.1:
        #    self.LookDown((-0.1 - y) * TURN_MULTIPLIER)
        #elif y > 0.1:
        #    self.LookUp((y - 0.1) * TURN_MULTIPLIER)
        self.target()
        if self.handleEvents:
            self.LookAtMouse(TURN_MULTIPLIER)
            
            moving = 0
            states = ['forward','backward','moveleft','moveright','left','right','up','down']
            if any(inputState.isSet(s) for s in states):
                if (inputState.isSet('forward') or inputState.isSet('backward')) and \
                   (inputState.isSet('moveleft') or inputState.isSet('moveright')):
                    const = sqrt(0.5)
                    motionMult = const * MOTION_MULTIPLIER
                    strafeMult = const * STRAFE_MULTIPLIER
                else:
                    motionMult = MOTION_MULTIPLIER
                    strafeMult = STRAFE_MULTIPLIER
                    
                if inputState.isSet('forward') :
                    self.MoveForwards(motionMult)
                    moving = 1
                elif inputState.isSet('backward') :
                    self.MoveBackwards(motionMult)
                    moving = 1
                if inputState.isSet('moveleft') :
                    self.MoveLeft(strafeMult)
                    moving = 1
                elif inputState.isSet('moveright') :
                    self.MoveRight(strafeMult)
                    moving = 1
                #if inputState.isSet('left') :
                #    self.LookLeft()
                #elif inputState.isSet('right') :
                #    self.LookRight()
                #if inputState.isSet('up') :
                #    self.LookDown() if self.inverted else self.LookUp()
                #elif inputState.isSet('down') :
                #    self.LookUp() if self.inverted else self.LookDown()
                #end if
            #end if
            if moving == 1:
                self.StartMoving()
            else:
                self.StopMoving()
        return Task.cont
    
    def StartMoving(self):
        if self.running: return
        self.running = True
        self.shortRun.loop()
        
    def StopMoving(self):
        if not self.running: return
        self.tron.stop()
        if self.shortRun.isPlaying():
            run = self.shortRun
            t = run.getT()
            run.start(startT=t)
        self.running = False
    
    def move(self,dx,dy):
        self.tron.setFluidPos(self.tron.getX()+dx,self.tron.getY()+dy,10)
    
    def MoveForwards(self, mult):
        self.move(mult*sin(radians(self.tron.getH())),-mult*cos(radians(self.tron.getH())))

    def MoveBackwards(self, mult):
        self.move(-mult*sin(radians(self.tron.getH())),mult*cos(radians(self.tron.getH())))
        
    def MoveLeft(self, mult):
        self.move(mult*sin(radians(self.tron.getH()+90)),-mult*cos(radians(self.tron.getH()+90)))
        
    def MoveRight(self, mult):
        self.move(-mult*sin(radians(self.tron.getH()+90)),mult*cos(radians(self.tron.getH()+90)))
    
    def LookLeft(self, mult):
        self.tron.setHpr(self.tron.getH()+mult, self.tron.getP(), 0)
    
    def LookRight(self, mult):
        self.tron.setHpr(self.tron.getH()-mult, self.tron.getP(), 0)
    
    def LookDown(self, mult):
        p = min(90,self.tron.getP()+mult)
        self.tron.setHpr(self.tron.getH(), p, 0)
    
    def LookUp(self, mult):
        p = max(-50,self.tron.getP()-mult)
        self.tron.setHpr(self.tron.getH(), p, 0)
        
    def LookAtMouse(self, mult):
        md = base.win.getPointer(0)
        x = md.getX()
        y = md.getY()
        if base.win.movePointer(0, base.win.getXSize()/2, base.win.getYSize()/2):
            self.tron.setH(self.tron.getH() - (mult * (x - base.win.getXSize()/2)))
            self.tron.setP(self.tron.getP() + (mult * (y - base.win.getYSize()/2)))
    