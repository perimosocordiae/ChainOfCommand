#Scale factor for panda speed - bigger makes them faster
CHASE_SCALE = 1.0

import direct.directbase.DirectStart
from direct.task import Task
from direct.actor import Actor
from pandac.PandaModules import CollisionNode, CollisionSphere
from random import randint
from math import pi, sin, cos
from agent import Agent

class Drone(Agent):

    def __init__(self,game,pos=None):
       super(Drone,self).__init__(game)
       if not pos:
           pos = game.rand_point()
       self.load_model(pos)
       self.setup_collision(len(self.game.drones))
  
    def damage(self):
       return 20

    def load_model(self,pos):
       self.panda = Actor.Actor("models/panda-model", {"walk":"models/panda-walk4"})
       self.panda.reparentTo(render)
       self.panda.setScale(0.05)
       self.panda.setHpr(0,0,0)
       self.panda.setPos(pos[0],pos[1],0)
       self.walk = self.panda.actorInterval("walk")
       self.walk.loop()
       self.walking = False
       taskMgr.add(self.WalkTask, "WalkTask")

    def setup_collision(self,i):
        self.collider = self.panda.attachNewNode(CollisionNode('dronecnode_%d'%i))
        self.collider.node().addSolid(CollisionSphere(0,0,300,300)) # sphere for now
        self.collider.show()

    def WalkTask(self, task):
        if not self.walking:
            self.walking = True
            #self.MoveForwardsRand()
            self.follow_tron()
        return Task.cont
   
    def follow_tron(self):
        tron = self.game.players[0].tron
        self.panda.lookAt(tron)
        self.panda.setH(self.panda.getH() + 180)
        #move one "unit" towards tron
        tronVec = tron.getPos() - self.panda.getPos()
        tronVec.normalize()
        newPos = self.panda.getPos() + tronVec*CHASE_SCALE
        self.panda.setPos(newPos.getX(), newPos.getY(), 0)
        self.walking = False

    def MoveForwardsRand(self):
        moveSpeed = 1
        moveDir = randint(-10,10)
        self.panda.setHpr(self.panda.getH() + moveDir, self.panda.getP(), 0)
        self.panda.setX(self.panda.getX() + moveSpeed * sin(self.panda.getH()*(pi/180.0)))
        self.panda.setY(self.panda.getY() - moveSpeed * cos(self.panda.getH()*(pi/180.0)))
        self.walking = False
   
