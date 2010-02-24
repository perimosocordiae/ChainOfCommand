MODEL_PATH = "../../models"
#Constants for motion and rotation
MOTION_MULTIPLIER = 3.0
STRAFE_MULTIPLIER = 2.0
TURN_MULTIPLIER = 3.0

import direct.directbase.DirectStart
from direct.task import Task
from direct.actor import Actor
from pandac.PandaModules import Point3
from direct.interval.IntervalGlobal import Parallel
import random
from math import pi, sin, cos


class Drone(object):

   def __init__(self):
       self.panda = Actor.Actor("models/panda-model", {"walk":"models/panda-walk4"})
       self.panda.reparentTo(render)
       self.panda.setScale(0.05)
       self.panda.setHpr(0,0,0)
       self.panda.setPos(0,0,0)
       self.walk = self.panda.actorInterval("walk")
       self.walking = False
      
       taskMgr.add(self.WalkTask, "WalkTask")
       
   def WalkTask(self, task):
       if not(self.walking):
           self.walking = True
           self.MoveForwards()
       return Task.cont
   
   def MoveForwards(self):
       random.seed()
       moveSpeed = random.randint(1,1)
       moveDir = random.randint(-10,10)
       self.panda.setHpr(self.panda.getH() + moveDir, self.panda.getP(), 0)
       self.panda.setX(self.panda.getX() + moveSpeed * sin(self.panda.getH()*(pi/180.0)))
       self.panda.setY(self.panda.getY() - moveSpeed * cos(self.panda.getH()*(pi/180.0)))
       self.walking = False
   
   
   