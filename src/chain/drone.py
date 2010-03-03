from direct.task import Task
from direct.actor import Actor
from pandac.PandaModules import CollisionNode, CollisionSphere, CollisionTube, BitMask32
from agent import Agent
from random import random

#Scale factor for panda speed - bigger makes them faster
CHASE_SCALE = 1.0
DRONE_COLLIDER_MASK = BitMask32.bit(1)
DRONE_PUSHER_MASK = BitMask32.bit(2)


class Drone(Agent):

    def __init__(self,game,pos=None):
        super(Drone,self).__init__(game)
        if not pos: pos = game.rand_point()
        self.load_model(pos)
        self.setup_collider()
        self.speed = random()+0.5
  
    def damage(self):
        return 10
     
    def repeat_damage(self):
        return 2

    def die(self):
        #self.panda.stash()
        #self.collider.stash()
        #self.pusher.stash()
        taskMgr.remove(self.walkTask)
        del self.game.drones[str(hash(self))]
        self.collider.removeNode()
        self.pusher.removeNode()
        self.panda.cleanup()
        self.panda.removeNode()

    def load_model(self,pos):
        self.panda = Actor.Actor("models/panda-model", {"walk":"models/panda-walk4"})
        self.panda.reparentTo(render)
        self.panda.setScale(max(0.01,random()*0.05))
        self.panda.setHpr(0,0,0)
        self.panda.setPos(pos[0],pos[1],0)
        self.walk = self.panda.actorInterval("walk")
        self.walk.loop()
        self.walking = False
        self.walkTask = taskMgr.add(self.WalkTask, "WalkTask")

    def setup_collider(self):
        key = str(hash(self))
        # Get the size of the object for the collision sphere.
        bounds = self.panda.getChild(0).getBounds()
        center = bounds.getCenter()
        radius = bounds.getRadius() * 0.85
        radius2 = bounds.getRadius() * 0.43
        x = center.getX()
        z = center.getZ()
        posY = center.getY() + radius - radius2
        negY = center.getY() - radius + radius2
        
        # Create a collision tube
        cNode = CollisionNode(key)
        cNode.addSolid(CollisionTube(x, posY, z, x, negY, z, radius2))
        self.collider = self.panda.attachNewNode(cNode)
        self.collider.node().setFromCollideMask(DRONE_COLLIDER_MASK)
        self.collider.node().setIntoCollideMask(DRONE_COLLIDER_MASK)
            
        # Create a pusher sphere
        cNode2 = CollisionNode(key+'donthitthis')
        cNode2.addSolid(CollisionSphere(center, radius))
        self.pusher = self.panda.attachNewNode(cNode2)
        self.pusher.node().setFromCollideMask(DRONE_PUSHER_MASK)
        self.pusher.node().setIntoCollideMask(DRONE_PUSHER_MASK)
        
        #self.collider.show()
        #self.pusher.show()

    def WalkTask(self, task):
        if not self.walking:
            self.walking = True
            self.follow_tron()
        return Task.cont
   
    def follow_tron(self):
        tron = self.game.players['player_1'].tron
        self.panda.lookAt(tron)
        self.panda.setH(self.panda.getH() + 180)
        #move one "unit" towards tron
        tronVec = tron.getPos() - self.panda.getPos()
        tronVec.normalize()
        newPos = self.panda.getPos() + tronVec*self.speed
        self.panda.setFluidPos(newPos.getX(), newPos.getY(), 0)
        self.walking = False

   
