from direct.task import Task
from direct.actor import Actor
from pandac.PandaModules import CollisionNode, CollisionSphere, CollisionTube, BitMask32
from pandac.PandaModules import DirectionalLight, VBase4, NodePath
from direct.interval.IntervalGlobal import *
from agent import Agent
from random import random
from constants import *

#Scale factor for panda speed - bigger makes them faster
CHASE_SCALE = 1.0

class Drone(Agent):
    def __init__(self,game,pos=None):
        super(Drone,self).__init__(game,str(hash(self)))
        if not pos: pos = game.point_for("white")
        self.hittables = {}
        self.parent.setPos(pos[0],pos[1],pos[2] + self.get_origin_height())
        self.setup_collider()
        self.speed = (random()+0.5)*2 + 15
        
    def get_text_pos(self):
        return (0,0,5)
    
    def damage(self):
        return 20
     
    def repeat_damage(self):
        return 0.1

    def die(self):
        #taskMgr.remove(self.walkTask)
        del self.game.drones[str(hash(self))]
        self.collider.removeNode()
        self.pusher.removeNode()
        self.hitter.removeNode()
        self.model.cleanup()
        self.model.removeNode()
        self.parent.removeNode()

    def load_model(self):
        self.parent = render.attachNewNode("%s_Parent"%str(hash(self)))
        
        self.model = Actor.Actor("../../models/cyborg_newer.egg", {"sword": "../../models/cyborg_swing_sword.egg"})
        self.model.reparentTo(self.parent)
        #self.model.setScale(max(0.01,random()*2))
        self.model.setScale(0.7)
        self.model.setHpr(0,90,0)
        #self.walk = self.model.actorInterval("sword")
        #self.walk.loop()
        self.pose = 1
        self.model.pose("sword", 1)
        
        dlight = DirectionalLight('dlight')
        dlight.setColor(VBase4(1, 1, 0.9, 1))
        self.light = self.model.attachNewNode(dlight)
        self.light.setHpr(90,-60,60) 
        self.model.setLight(self.light)
        #self.walkTask = taskMgr.add(self.WalkTask, "WalkTask")
    
    def get_model(self):
        return self.parent
    
    def get_origin_height(self):
        return 10
    
    def setup_collider(self):
        key = str(hash(self))
        # Get the size of the object for the collision sphere.
        bounds = self.model.getChild(0).getBounds()
        center = bounds.getCenter()
        center.setZ(center.getZ() - 0.5)
        radius = bounds.getRadius() * 0.4
        radius2 = bounds.getRadius() * 0.15
        x = center.getX()
        y = center.getY()
        posZ = center.getZ() + radius - radius2
        negZ = center.getZ() - radius + radius2
        
        # Create a collision tube
        cNode = CollisionNode(key)
        cNode.addSolid(CollisionTube(x, y, posZ, x, y, negZ, radius2))
        self.collider = self.parent.attachNewNode(cNode)
        self.collider.node().setFromCollideMask(DRONE_COLLIDER_MASK)
        self.collider.node().setIntoCollideMask(DRONE_COLLIDER_MASK)
            
        # Create a pusher sphere
        cNode2 = CollisionNode(key+'donthitthis')
        cNode2.addSolid(CollisionSphere((center.getX(), center.getY() - 3.5, center.getZ()), radius*2.4))
        self.hitter = self.parent.attachNewNode(cNode2)
        self.hitter.node().setFromCollideMask(DRONE_COLLIDER_MASK)
        self.hitter.node().setIntoCollideMask(DRONE_COLLIDER_MASK)
        
        cNode3 = CollisionNode(key+'_wall_donthitthis')
        cNode3.addSolid(CollisionSphere(center, radius * .05))
        self.pusher = self.parent.attachNewNode(cNode3)
        self.pusher.node().setFromCollideMask(WALL_COLLIDER_MASK)
        self.pusher.node().setIntoCollideMask(WALL_COLLIDER_MASK)
        
    def get_shield_sphere(self):
        return self.pusher
    
    #def WalkTask(self, task):
    #    self.follow_tron()
    #    return Task.cont
    
    def act(self):
        self.follow_tron()
    
    def canHitPlayer(self, player, canHit):
        if canHit != (player.name in self.hittables.keys()):
            #if in and can't hit or not in but can hit
            if canHit:
                self.hittables[player.name] = player
            else:
                del self.hittables[player.name]
    
    def follow_tron(self):
        # get closest player
        dist_to = lambda p: (p.tron.getPos()-self.model.getPos()).lengthSquared()
        tron = sorted(self.game.players.values(),key=dist_to)[0].tron
        self.parent.lookAt(tron)
        self.parent.setH(self.parent.getH() + 180)
        self.parent.setP(0)
        #move one "unit" towards tron
        tronVec = tron.getPos() - self.parent.getPos()
        tronVec.setZ(0)
        tronVec.normalize()
        tronVec *= self.speed
        self.handleGravity()
        self.velocity.setX(tronVec.getX())
        self.velocity.setY(tronVec.getY())
        self.parent.setFluidPos(self.parent.getPos() + (self.velocity*self.speed*SERVER_TICK))
        #Kill any pandas that somehow manage to slip through the cracks
        if self.parent.getZ() < BOTTOM_OF_EVERYTHING:
            self.die()
            
        if self.pose != 52 or len(self.hittables) > 0:
            self.pose += 1
            if self.pose == 65:
                for tron in self.hittables.itervalues():
                    tron.hit(self.damage())
            elif self.pose == 73:
                self.pose = 52
            self.model.pose("sword", self.pose)
            
        