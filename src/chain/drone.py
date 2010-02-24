
import direct.directbase.DirectStart
from direct.task import Task
from direct.actor import Actor
from pandac.PandaModules import Point3
from random import randint
from math import pi, sin, cos

class Drone(object):

   def __init__(self,game,pos=None):
       self.game = game
       if not pos:
           pos = game.rand_point()
       self.load_model(pos)
    
   def load_model(self,pos):
       self.panda = Actor.Actor("models/panda-model", {"walk":"models/panda-walk4"})
       self.panda.reparentTo(render)
       self.panda.setScale(0.05)
       self.panda.setHpr(0,0,0)
       self.panda.setPos(pos[0],pos[1],0)
       self.walk = self.panda.actorInterval("walk")
       self.walking = False
       taskMgr.add(self.WalkTask, "WalkTask")

   def WalkTask(self, task):
       if not self.walking:
           self.walking = True
           self.MoveForwardsRand()
       return Task.cont
   
   def follow(self,leader):
       self.panda.lookAt(leader)
       #TODO walk forward

   def MoveForwardsRand(self):
       moveSpeed = randint(1,1) #um.. why?
       moveDir = randint(-10,10)
       self.panda.setHpr(self.panda.getH() + moveDir, self.panda.getP(), 0)
       self.panda.setX(self.panda.getX() + moveSpeed * sin(self.panda.getH()*(pi/180.0)))
       self.panda.setY(self.panda.getY() - moveSpeed * cos(self.panda.getH()*(pi/180.0)))
       self.walking = False
   
   
   
