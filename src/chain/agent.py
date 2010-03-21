from pandac.PandaModules import CollisionHandlerQueue, CollisionNode, CollisionRay, Vec3
from itertools import ifilter
from constants import *

class Agent(object):

    def __init__(self,game,name,setup_mc=True):
        self.game = game
        self.name = name
        #basic agent only gets 1 program
        self.programs = [None]
        self.canCollect = None
        self.health = 100
        self.velocity = Vec3(0, 0, 0)
        if setup_mc:
            self.load_model()
            self.setup_floor_collider()
    
    def load_model(self):
        return
    
    def get_shield_sphere(self):
        #override to show some kind of shield
        return self.lifter
        
    def setup_floor_collider(self):
        self.floorQueue = CollisionHandlerQueue()
        
        self.lifterRay = CollisionRay(0, 0, 10-self.get_origin_height(), 0, 0, -1) #ray pointing down
        self.lifter = self.attach_collision_node("%s_floor" % self.name, self.lifterRay, FLOOR_COLLIDER_MASK)
        self.lifter.node().setIntoCollideMask(0)
        
        base.cTrav.addCollider(self.lifter, self.floorQueue)
    
    def attach_collision_node(self, name, solid, mask):
        c = self.get_model().attachNewNode(CollisionNode(name))
        c.node().addSolid(solid)
        c.node().setFromCollideMask(mask)
        c.node().setIntoCollideMask(mask)
        return c
    
    def in_air(self):
        base.cTrav.traverse(render)
        if self.floorQueue.getNumEntries() == 0: return True # technically
        self.floorQueue.sortEntries()
        floorZ = self.floorQueue.getEntry(0).getSurfacePoint(render).getZ()
        return self.get_model().getZ() > floorZ + self.get_origin_height()
    
    def handleGravity(self):
        #in the future, have 2 rays - one above, one below, so he can't jump
        #through things?  Or let him jump through things.  If he can't, adapt
        #2nd half of if statement to include 2nd ray.
        z_vel = self.velocity.getZ()
        if self.in_air() or z_vel > 0:
            self.velocity.setZ(max(z_vel + GRAVITATIONAL_CONSTANT, TERMINAL_VELOCITY)) # jump / fall
        else:
            #We hit (or stayed on) the ground...
            #how fast are we falling now? Use that to determine potential damage
            if z_vel < SAFE_FALL:
                damage = (-z_vel + SAFE_FALL) * FALL_DAMAGE_MULTIPLIER
                self.hit(damage)
            else:
                floorZ = self.floorQueue.getEntry(0).getSurfacePoint(render).getZ()
                self.get_model().setZ(floorZ + self.get_origin_height())
            self.velocity.setZ(0)
    
    def jump(self):
        if not self.in_air():
            self.velocity.setZ(self.get_jump_speed())  # he's on the ground - let him jump
    
    def get_model(self):
        return None
    
    def collect(self):
        if self.canCollect:
            prog = self.canCollect
            
            #if basic, have it do its effect and return
            if not prog.pick_up(self):
                return -1, prog
            
            for i,p in enumerate(self.programs):
                if not p: break
            if p:
                return i, False
            
            self.programs[i] = prog
            prog.disappear()
            del self.game.programs[prog.unique_str()]  
            self.canCollect = None
            prog.add_effect(self)
            return i, prog
        else:
            return -1, None
    
    def drop(self, i):
        prog = self.programs[i]
        if prog != None:
            prog.reappear(self.tron.getPos())
            noneLeft = True
            for j,p in enumerate(self.programs):
                if i != j and p != None and p.name == prog.name:
                    noneLeft = False
                    break
            if noneLeft:
                #have the program remove any of its visual effects
                prog.remove_effect(self)
                
            self.programs[i] = None
            return True
        else:
            return False
    
    def add_slot(self):
        self.programs.append(None)
    
    def set_laser_glow(self, glow):
        return
    
    def set_glow(self, glow):
        return
    
    def hit(self,amt):
        self.health -= amt/self.shield()
        if self.health <= 0:
            self.die()
    
    def die(self):
        print "Agent is dead"
    
    def is_dead(self):
        return self.health <= 0

    def heal(self,amt):
        self.health += amt
        
    def get_base_damage(self):
        return 10
        
    def damage(self):
        d = self.get_base_damage()
        for p in ifilter(lambda p: p != None, self.programs):
            d = p.damage_mod(d)
        return d

    def shield(self):
        s = 1.0 # no shield
        for p in ifilter(lambda p: p != None, self.programs):
            s = p.shield_mod(s)
        return s
    
    def rapid_fire(self):
        a = 1.0
        for p in ifilter(lambda p: p != None, self.programs):
            a = p.rapid_fire_mod(a)
        return a
    

