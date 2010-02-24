MODEL_PATH = "../../models"
#Constants for motion and rotation
MOTION_MULTIPLIER = 3.0
STRAFE_MULTIPLIER = 2.0
TURN_MULTIPLIER = 3.0

from math import pi,sin,tan,cos, sqrt
from itertools import ifilter
import direct.directbase.DirectStart
from direct.task import Task
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import Point3,Vec3,Filename,Buffer,Shader
from direct.showbase.InputStateGlobal import inputState
from eventHandler import KeyHandler
from agent import Agent

class Player(Agent):

    def __init__(self,game,name):
        super(Player,self).__init__(game)
        self.programs = [None,None,None]
        self.name = name
        self.inverted = True # look controls
        self.load_model()
        self.setup_camera()
        self.keyHandle = KeyHandler(self) 
	
    def shoot(self):
        print "pew pew!"
        #TODO: do all that collision stuff

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
	
    def hit(self,amt):
        super(Player,self).hit(amt)
        self.game.playerHit()
        # flash the screen red, maybe?

    def load_model(self):
        glowShader=Shader.load("%s/glowShader.sha"%MODEL_PATH)
        self.tron = Actor.Actor("%s/tron"%MODEL_PATH, {"running":"%s/tron_anim_updated"%MODEL_PATH})
        self.tron.reparentTo(render)
        self.tron.setScale(0.4, 0.4, 0.4)
        self.tron.setHpr(0, 12, 0)
        self.tron.setPos(-4, 34, 10)
        #maybe this does interpolation?
        #self.tron.setBlend(frameBlend = True)
        self.tron.pose("running",46)
        self.runInterval = self.tron.actorInterval("running", startFrame=0, endFrame = 46)

        self.shortRun = self.tron.actorInterval("running", startFrame=25, endFrame = 46)
        self.runLoop = Sequence(self.runInterval, Func(lambda i: i.loop(), self.shortRun))
        self.running = False

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

    def switchPerspective(self):
        #Switch between 3 perspectives
        if base.camera.getY() > 60:
            base.camera.setPos(0, 0, 10)
        elif base.camera.getY() > 20:
            base.camera.setPos(0, 100, 10)
        else:
            base.camera.setPos(0, 40, 10)
    
    def zoomIn(self):
        if base.camera.getY() > 0:
            base.camera.setY(base.camera.getY() - 2)
            
    def zoomOut(self):
        if base.camera.getY() < 100:
            base.camera.setY(base.camera.getY() + 2)
   # def jump(self):
        
    #Task to move the camera
    def updateCameraTask(self, task):
        moving = 0
        states = ['forward','backward','moveleft','moveright','left','right','up','down']
        if any(inputState.isSet(s) for s in states):
            if (inputState.isSet('forward') or inputState.isSet('backward')) and \
               (inputState.isSet('moveleft') or inputState.isSet('moveright')):
                const = sqrt(2.0) / 2.0
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
            if inputState.isSet('left') :
                self.LookLeft()
            elif inputState.isSet('right') :
                self.LookRight()
            if inputState.isSet('up') :
                self.LookDown() if self.inverted else self.LookUp()
            elif inputState.isSet('down') :
                self.LookUp() if self.inverted else self.LookDown()
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
    
    def MoveForwards(self, mult):
        self.tron.setX(self.tron.getX() + mult * sin(self.tron.getH()*(pi/180.0)))
        self.tron.setY(self.tron.getY() - mult * cos(self.tron.getH()*(pi/180.0)))

    def MoveBackwards(self, mult):
        self.tron.setX(self.tron.getX() - mult * sin(self.tron.getH()*(pi/180.0)))
        self.tron.setY(self.tron.getY() + mult * cos(self.tron.getH()*(pi/180.0)))
        
    def MoveLeft(self, mult):
        self.tron.setX(self.tron.getX() + mult * sin((self.tron.getH() + 90)*(pi/180.0)))
        self.tron.setY(self.tron.getY() - mult * cos((self.tron.getH() + 90)*(pi/180.0)))
        
    def MoveRight(self, mult):
        self.tron.setX(self.tron.getX() - mult * sin((self.tron.getH() + 90)*(pi/180.0)))
        self.tron.setY(self.tron.getY() + mult * cos((self.tron.getH() + 90)*(pi/180.0)))
        
    def LookLeft(self):
        self.tron.setHpr(self.tron.getH()+TURN_MULTIPLIER, self.tron.getP(), 0)
    
    def LookRight(self):
        self.tron.setHpr(self.tron.getH()-TURN_MULTIPLIER, self.tron.getP(), 0)
    
    def LookDown(self):
        p = min(90,self.tron.getP()+TURN_MULTIPLIER)
        self.tron.setHpr(self.tron.getH(), p, 0)
    
    def LookUp(self):
        p = max(-50,self.tron.getP()-TURN_MULTIPLIER)
        self.tron.setHpr(self.tron.getH(), p, 0)

