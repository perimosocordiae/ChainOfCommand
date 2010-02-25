from direct.task import Task
from direct.actor import Actor
from pandac.PandaModules import CollisionNode, CollisionSphere, BitMask32
from random import randint
from math import pi, sin, cos
from agent import Agent

#Scale factor for panda speed - bigger makes them faster
CHASE_SCALE = 1.0
DRONE_COLLIDER_MASK = BitMask32.bit(1)
DRONE_PUSHER_MASK = BitMask32.bit(2)


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
        # Get the size of the object for the collision sphere.
        bounds = self.panda.getChild(0).getBounds()
        center = bounds.getCenter()
        radius = bounds.getRadius() * 0.8
        # Create a collision sphere and name it something understandable.
        cNode = CollisionNode('dronecnode_%d'%i)
        cNode.addSolid(CollisionSphere(center, radius))
        self.collider = self.panda.attachNewNode(cNode)
        self.collider.node().setFromCollideMask(DRONE_COLLIDER_MASK)
        self.collider.node().setIntoCollideMask(DRONE_COLLIDER_MASK)
        
        # Create a second slightly smaller collision sphere for 
        radius2 = bounds.getRadius() * 0.7
        cNode2 = CollisionNode('dronecnode_%d2'%i)
        cNode2.addSolid(CollisionSphere(center, radius2))
        self.pusher = self.panda.attachNewNode(cNode2)
        self.pusher.node().setFromCollideMask(DRONE_PUSHER_MASK)
        self.pusher.node().setIntoCollideMask(DRONE_PUSHER_MASK)
        
        self.collider.show()
        self.pusher.show()

    def WalkTask(self, task):
        if not self.walking:
            self.walking = True
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
        self.panda.setFluidPos(newPos.getX(), newPos.getY(), 0)
        self.walking = False

   
