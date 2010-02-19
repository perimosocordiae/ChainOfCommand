MODEL_PATH = "../../models"

from math import pi,sin,tan,cos
import direct.directbase.DirectStart
from direct.task import Task
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import Point3
from pandac.PandaModules import Vec3
from pandac.PandaModules import Filename,Buffer,Shader
from direct.showbase.InputStateGlobal import inputState

class Player(object):

    def __init__(self):
        glowShader=Shader.load("%s/glowShader.sha"%MODEL_PATH)
        tron = Actor.Actor("%s/tron"%MODEL_PATH, {"running":"%s/tron_anim"%MODEL_PATH})
        tron.reparentTo(render)
        tron.setScale(0.4, 0.4, 0.4)
        tron.setHpr(30, 12, 0)
        tron.setPos(-4, 34, 10)
        
        runInterval = tron.actorInterval("running", startFrame=0, endFrame = 46)

        #Calculate how far to move in (x,y); 30 degrees is pi/12 radians
        dx = 7.2
        dy = (-dx * (1/tan(pi / 6)))
        shortRun = tron.actorInterval("running", startFrame=25, endFrame = 46)
        
        inputState.watch('forward', 'w', 'w-up') 
        inputState.watch('backward', 's', 's-up')
        inputState.watch('moveleft', 'a', 'a-up')
        inputState.watch('moveright', 'd', 'd-up')
        inputState.watch('left', 'arrow_left', 'arrow_left-up')
        inputState.watch('right', 'arrow_right', 'arrow_right-up')
        inputState.watch('up', 'arrow_up', 'arrow_up-up')
        inputState.watch('down', 'arrow_down', 'arrow_down-up')
        
        taskMgr.add(updateCameraTask, "updateCameraTask")
        
   # def turn_left(self,amt):
        
   # def turn_right(self,amt):
        
   # def jump(self):
    
        
#Task to move the camera
def updateCameraTask(task):
    if inputState.isSet('forward') or inputState.isSet('backward') or \
    inputState.isSet('left') or inputState.isSet('right') or inputState.isSet('up') \
    or inputState.isSet('down') or inputState.isSet('moveleft') or inputState.isSet('moveright') :
        if inputState.isSet('forward') :
            MoveForwards()
        elif inputState.isSet('backward') :
            MoveBackwards()
        if inputState.isSet('moveleft') :
            MoveLeft()
        elif inputState.isSet('moveright') :
            MoveRight()
        if inputState.isSet('left') :
            LookLeft()
        elif inputState.isSet('right') :
            LookRight()
        if inputState.isSet('up') :
            LookUp()
        elif inputState.isSet('down') :
            LookDown()
    return Task.cont

def MoveForwards():
    base.camera.setX(base.camera.getX() - sin(base.camera.getH()*(pi/180.0)))
    base.camera.setY(base.camera.getY() + cos(base.camera.getH()*(pi/180.0)))

def MoveBackwards():
    base.camera.setX(base.camera.getX() + sin(base.camera.getH()*(pi/180.0)))
    base.camera.setY(base.camera.getY() - cos(base.camera.getH()*(pi/180.0)))
    
def MoveLeft():
    base.camera.setX(base.camera.getX() - sin((base.camera.getH() + 90)*(pi/180.0)))
    base.camera.setY(base.camera.getY() + cos((base.camera.getH() + 90)*(pi/180.0)))
    
def MoveRight():
    base.camera.setX(base.camera.getX() + sin((base.camera.getH() + 90)*(pi/180.0)))
    base.camera.setY(base.camera.getY() - cos((base.camera.getH() + 90)*(pi/180.0)))
    
def LookLeft():
    base.camera.setHpr(base.camera.getH()+1, base.camera.getP(), 0)

def LookRight():
    base.camera.setHpr(base.camera.getH()-1, base.camera.getP(), 0)

def LookUp():
    base.camera.setHpr(base.camera.getH(), base.camera.getP()+1, 0)

def LookDown():
    base.camera.setHpr(base.camera.getH(), base.camera.getP()-1, 0)

