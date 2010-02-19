MODEL_PATH = "../../models"

import math
import direct.directbase.DirectStart
from direct.task import Task
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import Point3
from pandac.PandaModules import Vec3
from pandac.PandaModules import Filename,Buffer,Shader

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
        dy = (-dx * (1/math.tan(math.pi / 6)))
        #turnX = 14
        #turnY = -28
        #(12, -24)
        shortRun = tron.actorInterval("running", startFrame=25, endFrame = 46)
        rotateInterval = tron.hprInterval(0.7, Point3(120, 12, 0), startHpr=Point3(30,12,0), blendType='easeInOut')
        rotateInterval2 = tron.hprInterval(0.7, Point3(210, 12, 0), blendType='easeInOut')
        rotateInterval3 = tron.hprInterval(0.7, Point3(300, 12, 0), blendType='easeInOut')
        rotateInterval4 = tron.hprInterval(0.7, Point3(390, 12, 0), blendType='easeInOut')
        
        #elliptical run - unfortunately he has to be moved each time to account
        #for animation displacement, and the calculation isn't very straightforward
        #Important note - each moveTron call is actually accounting for the DIFFERENCE
        #BETWEEN THE PREVIOUS ANIMATION'S EFFECTS AND THE CURRENT ONE.  So they can't
        #just be copy-pasted to achieve the same desired effect in a different scenario
        runLoop = Sequence(Parallel(shortRun, Func(moveTron, tron, 4, 20, 0)),
                           Parallel(shortRun, Func(moveTron, tron, dx, dy, 1)),
                           Parallel(shortRun, rotateInterval, Func(moveTron, tron, dx, dy, 1)),
                           Parallel(shortRun, rotateInterval2, Func(moveTron, tron, 12, 8, 1)),
                           Parallel(shortRun, Func(moveTron, tron, -8, 12, 1)),
                           Parallel(shortRun, Func(moveTron, tron, -dx, -dy, 1)),
                           Parallel(shortRun, rotateInterval3, Func(moveTron, tron, -dx, -dy, 1)),
                           Parallel(shortRun, rotateInterval4, Func(moveTron, tron, -12, -8, 1)))
        
        #Long, straight line run
        runLoop2 = Sequence(Parallel(shortRun, Func(moveTron, tron, 4, 20, 0)),
                           Parallel(shortRun, Func(moveTron, tron, dx, dy, 1)),
                           Parallel(shortRun, Func(moveTron, tron, dx, dy, 1)),
                           Parallel(shortRun, Func(moveTron, tron, dx, dy, 1)),
                           Parallel(shortRun, Func(moveTron, tron, dx, dy, 1)),
                           Parallel(shortRun, Func(moveTron, tron, dx, dy, 1)))
        
        overallLoop = Sequence(runInterval, Func(startLoop, runLoop))
        overallLoop.start()
        
   # def turn_left(self,amt):
        
   # def turn_right(self,amt):
        
   # def jump(self):
    
    
    
#************************** Add in Tron **************************
def moveTron(actr, deltaX, deltaY, isDelta):
  if isDelta == 1:
    actr.setPos(actr.getX() + deltaX, actr.getY() + deltaY, 10)
  else:
    actr.setPos(deltaX, deltaY, 10)

def startLoop(seq):
  seq.loop();





