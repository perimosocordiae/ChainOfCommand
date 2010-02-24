
import direct.directbase.DirectStart
from direct.task import Task
from direct.actor import Actor
from pandac.PandaModules import Point3
from random import randint
from math import pi, sin, cos
from agent import Agent

class Drone(Agent):

   def __init__(self,game,pos=None):
       super(Drone,self).__init__(game)
       if not pos:
           pos = game.rand_point()
       self.load_model(pos)
  
   def damage(self):
       return 20

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
           #self.MoveForwardsRand()
           self.follow_tron()
       return Task.cont
   
   def follow_tron(self):
       tron = self.game.players[0].tron
       self.panda.lookAt(tron)
       #TODO walk forward
       self.walking = False

   def MoveForwardsRand(self):
       moveSpeed = randint(1,1) #um.. why?
       moveDir = randint(-10,10)
       self.panda.setHpr(self.panda.getH() + moveDir, self.panda.getP(), 0)
       self.panda.setX(self.panda.getX() + moveSpeed * sin(self.panda.getH()*(pi/180.0)))
       self.panda.setY(self.panda.getY() - moveSpeed * cos(self.panda.getH()*(pi/180.0)))
       self.walking = False
   
