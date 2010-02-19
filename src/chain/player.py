MODEL_PATH = "../../models"
#Constants for motion and rotation
MOTION_MULTIPLIER = 3.0
STRAFE_MULTIPLIER = 2.0
TURN_MULTIPLIER = 3.0

from math import pi,sin,tan,cos, sqrt
import direct.directbase.DirectStart
from direct.task import Task
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import Point3
from pandac.PandaModules import Vec3
from pandac.PandaModules import Filename,Buffer,Shader
from direct.showbase.InputStateGlobal import inputState
from eventHandler import KeyHandler

class Player(object):

    def __init__(self):
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

        #Calculate how far to move in (x,y); 30 degrees is pi/12 radians
        #dx = 7.2
        #dy = (-dx * (1/tan(pi / 6)))
        self.shortRun = self.tron.actorInterval("running", startFrame=25, endFrame = 46)
        self.runLoop = Sequence(self.runInterval, Func(self.startLoop, self.shortRun))
        self.running = False
        
        inputState.watch('forward', 'w', 'w-up') 
        inputState.watch('backward', 's', 's-up')
        inputState.watch('moveleft', 'a', 'a-up')
        inputState.watch('moveright', 'd', 'd-up')
        inputState.watch('left', 'arrow_left', 'arrow_left-up')
        inputState.watch('right', 'arrow_right', 'arrow_right-up')
        inputState.watch('up', 'arrow_up', 'arrow_up-up')
        inputState.watch('down', 'arrow_down', 'arrow_down-up')
        taskMgr.add(self.updateCameraTask, "updateCameraTask")
        
        base.camera.reparentTo(self.tron)
        #base.camera.setPos(-80, -80, 15)
        #base.camera.setPos(80, 60, 10)
        base.camera.setPos(0, 40, 10)
        #base.camera.setHpr(-45, -10, 0)
        base.camera.setHpr(180, 0, 0)
        
        #Listen for changing perspective
        self.keyHandle = KeyHandler(self) 
   
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
    
    #Start looping an interval as a function so it can
    #occur inside of a sequence or parallel
    def startLoop(self, interv): 
        interv.loop()
        
    #Task to move the camera
    def updateCameraTask(self, task):
        moving = 0
        if inputState.isSet('forward') or inputState.isSet('backward') or \
        inputState.isSet('left') or inputState.isSet('right') or inputState.isSet('up') \
        or inputState.isSet('down') or inputState.isSet('moveleft') or inputState.isSet('moveright') :
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
                self.LookUp()
            elif inputState.isSet('down') :
                self.LookDown()
            #end if
        #end if
        if moving == 1:
            self.StartMoving()
        else:
            self.StopMoving()
        return Task.cont
    
    def StartMoving(self):
        #if not already animating, start the loop
        if self.running == False:
            self.running = True
            #self.runLoop.start()
            self.shortRun.loop()
        #end if
        
    def StopMoving(self):
        #if an animation is running, stop them all
        if self.running == True:
            #self.runLoop.finish()
            self.tron.stop()
            run = None
            if self.shortRun.isPlaying():
                run = self.shortRun
            #elif self.runInterval.isPlaying():
            #    run = self.runInterval
            
            if not (run == None):
                #finish the run and let it go to completion
                t = run.getT()
                #run.finish()
            
            #self.runLoop.finish()
            
            if not (run == None):
                #run = self.shortRun
                #run.finish()
            #    print t, " ", run.getDuration()
                run.start(startT=t)
            #end if
            #self.runLoop.finish()
            self.running = False
        #end if
    
    def MoveForwards(self, mult):
        self.tron.setX(self.tron.getX() + mult * sin(self.tron.getH()*(pi/180.0)))
        self.tron.setY(self.tron.getY() - mult * cos(self.tron.getH()*(pi/180.0)))
        #base.camera.setX(base.camera.getX() - sin(base.camera.getH()*(pi/180.0)))
        #base.camera.setY(base.camera.getY() + cos(base.camera.getH()*(pi/180.0)))

    def MoveBackwards(self, mult):
        self.tron.setX(self.tron.getX() - mult * sin(self.tron.getH()*(pi/180.0)))
        self.tron.setY(self.tron.getY() + mult * cos(self.tron.getH()*(pi/180.0)))
        #base.camera.setX(base.camera.getX() + sin(base.camera.getH()*(pi/180.0)))
        #base.camera.setY(base.camera.getY() - cos(base.camera.getH()*(pi/180.0)))
        
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
    
    def LookUp(self):
        self.tron.setHpr(self.tron.getH(), self.tron.getP()+TURN_MULTIPLIER, 0)
    
    def LookDown(self):
        self.tron.setHpr(self.tron.getH(), self.tron.getP()-TURN_MULTIPLIER, 0)

