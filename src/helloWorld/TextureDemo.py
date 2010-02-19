from math import pi, sin, cos
import math
 
import direct.directbase.DirectStart
from direct.task import Task
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import Point3
from pandac.PandaModules import Vec3
from pandac.PandaModules import Filename,Buffer,Shader
from direct.showbase.InputStateGlobal import inputState
 
 
#Load the first environment model
#environ = loader.loadModel("models/environment")
environ = loader.loadModel("../../models/yellow_floor.egg")
environ.reparentTo(render)
environ.setScale(8.0, 8.0, 8.0)
environ.setPos(0, 0, 0)

#******************* Change this to get more/less tiles *******************
rng = 30
#**************************************************************************

#Floor
center = rng/2
for i in range(0, rng):
  for j in range(0, rng):
    #if (i+j) % 3 == 0:
    if i < center and j < center:
      fl = "../../models/blue_floor.egg"
    elif i < center:
    #elif (i+j) % 3 == 1:
      fl = "../../models/green_floor.egg"
    elif j < center:
      fl = "../../models/red_floor.egg"
    else:
      fl = "../../models/yellow_floor.egg"
    #end if
      
    #bottom center is already done
    if i != center or j != center:  
      #floor
      tile = loader.loadModel(fl)
      tile.reparentTo(environ)
      tile.setScale(1.0, 1.0, 1.0)
      tile.setPos(2*(i - center), 2*(j - center), 0)
    #end if
    
    #ceiling
    tile = loader.loadModel(fl)
    tile.reparentTo(environ)
    tile.setScale(1.0, 1.0, 1.0)
    tile.setPos(-2*(1 + i - center), -2*(1 + j - center), 2 * rng)
    tile.setHpr(0, 0, 180)
    
    #wall 1
    tile = loader.loadModel(fl)
    tile.reparentTo(environ)
    tile.setScale(1.0, 1.0, 1.0)
    tile.setPos(-1 - (2 * center), 2*(j - center), 2*(rng - i) - 1)
    tile.setHpr(0, 0, 90)
    
    #wall 2
    tile = loader.loadModel(fl)
    tile.reparentTo(environ)
    tile.setScale(1.0, 1.0, 1.0)
    tile.setPos(-2*(1 + i - center), -1 - (2 * center), 2*(rng - j) - 1)
    tile.setHpr(0, -90, 0)
    
    #wall 3
    tile = loader.loadModel(fl)
    tile.reparentTo(environ)
    tile.setScale(1.0, 1.0, 1.0)
    tile.setPos(2 * center - 1, 2*(j - center), (2 * i) + 1)
    tile.setHpr(0, 0, -90)
    
    #wall 4
    tile = loader.loadModel(fl)
    tile.reparentTo(environ)
    tile.setScale(1.0, 1.0, 1.0)
    tile.setPos(-2*(1 + i - center), (2 * center) - 1, (2 * j) + 1)
    tile.setHpr(0, 90, 0)
    
  #next j
#next i

blue_egg = "../../models/blue_floor.egg"
for z in range(0, center / 2):
  tile = loader.loadModel(blue_egg)
  tile.reparentTo(environ)
  tile.setScale(1.0, 1.0, 1.0)
  tile.setPos(center, center, (2 * z) + 1)
  tile.setHpr(0,90,0)
  
  tile = loader.loadModel(blue_egg)
  tile.reparentTo(environ)
  tile.setScale(1.0, 1.0, 1.0)
  tile.setPos(center + 1, center + 1, (2 * z) + 1)
  tile.setHpr(90,90,0)
  
  tile = loader.loadModel(blue_egg)
  tile.reparentTo(environ)
  tile.setScale(1.0, 1.0, 1.0)
  tile.setPos(center, center + 2, (2 * z) + 1)
  tile.setHpr(180,90,0)
  
  tile = loader.loadModel(blue_egg)
  tile.reparentTo(environ)
  tile.setScale(1.0, 1.0, 1.0)
  tile.setPos(center - 1, center + 1, (2 * z) + 1)
  tile.setHpr(270,90,0)
#next z
inputState.watch('forward', 'w', 'w-up') 
inputState.watch('backward', 's', 's-up')
inputState.watch('moveleft', 'a', 'a-up')
inputState.watch('moveright', 'd', 'd-up')
inputState.watch('left', 'arrow_left', 'arrow_left-up')
inputState.watch('right', 'arrow_right', 'arrow_right-up')
inputState.watch('up', 'arrow_up', 'arrow_up-up')
inputState.watch('down', 'arrow_down', 'arrow_down-up')
        
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
    #base.camera.setZ(base.camera.getZ() + sin(base.camera.getP()*(pi/180.0)))

def MoveBackwards():
    base.camera.setX(base.camera.getX() + sin(base.camera.getH()*(pi/180.0)))
    base.camera.setY(base.camera.getY() - cos(base.camera.getH()*(pi/180.0)))
    #base.camera.setZ(base.camera.getZ() - sin(base.camera.getP()*(pi/180.0)))
    
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
    
taskMgr.add(updateCameraTask, "updateCameraTask")
base.disableMouse()
base.camera.setPos(-80, -80, 15)
base.camera.setHpr(-45, -10, 0)
#base.enableMouse()

actor = loader.loadModel("../../models/terminal_window.egg")
actor.setScale(2.0, 2.0, 2.0)
actor.setPos(0, 0, 10)
actor.reparentTo(render)

#actor.loop("walk")
#Load the panda actor, and loop its animation
#pandaActor = Actor.Actor("models/panda-model", {"walk": "models/panda-walk4"})
#pandaActor.setScale(0.05, 0.05, 0.05)
#pandaActor.reparentTo(render)
#pandaActor.loop("walk")

#******************** Uncomment this when in a class ********************
#def getIntervals(self):

#Create the intervals needed to spin and expand/contract
posInterval1 = actor.posInterval(3,
                            Point3(0, -20, 10),
                            startPos=Point3(0, 20, 10))
posInterval2 = actor.posInterval(3,
                            Point3(0, 20, 10),
                            startPos=Point3(0, -20, 10))

hprInterval1 = actor.hprInterval(1.5,
                            Point3(180, 0, 0),
                            startHpr=Point3(0, 0, 0))
hprInterval2 = actor.hprInterval(1.5,
                            Point3(360, 0, 0),
                            startHpr=Point3(180, 0, 0))

scaleInterval1 = actor.scaleInterval(1.5,
                            Point3(4.0, 4.0, 4.0),
                            startScale=Point3(2.0, 2.0, 2.0),
                            blendType='easeInOut')
scaleInterval2 = actor.scaleInterval(1.5,
                            Point3(2.0, 2.0, 2.0),
                            startScale=Point3(4.0, 4.0, 4.0),
                            blendType='easeInOut')

#Create and play the sequence that coordinates the intervals
pace = Sequence(posInterval1,
                 #hprInterval1,
                 posInterval2,
                 #hprInterval2,
                 name="Pace")

flex = Sequence(Parallel(scaleInterval1, hprInterval1),
                     Parallel(scaleInterval2, hprInterval2))
#pace.loop()
flex.loop()


#************************** Add in Tron **************************
def moveTron(actr, deltaX, deltaY, isDelta):
  if isDelta == 1:
    actr.setPos(actr.getX() + deltaX, actr.getY() + deltaY, 10)
  else:
    actr.setPos(deltaX, deltaY, 10)

def startLoop(seq):
  seq.loop();

glowShader=Shader.load("../../models/glowShader.sha")
tron = Actor.Actor("../../models/tron", {"running":"../../models/tron_anim"})
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
#tron.pose("running", 46)

#tron2 = Actor.Actor("./tron", {"running":"tron_anim"})
#tron2.reparentTo(render)
#tron2.setScale(0.4, 0.4, 0.4)
#tron2.setHpr(30, 12, 0)
#tron2.setPos(-4, 24, 10)
#tron2.pose("running", 25)

run()