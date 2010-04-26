from pandac.PandaModules import CollisionHandlerQueue, CollisionNode, CollisionRay
from pandac.PandaModules import TextNode, Vec3, TextureStage, NodePath
from direct.interval.IntervalGlobal import *
from itertools import ifilter
from constants import *

#Constants
MAX_PROGRAMS = 5
BASE_CAMERA_FOCAL_LENGTH = 1.39951908588

class Agent(object):

    def __init__(self,game,name,setup_mcs=True):
        self.game = game
        self.name = name
        #basic agent only gets 1 program
        self.programs = [None]
        self.debuggers = {}
        self.canCollect = None
        self.invincible = False
        self.health = STARTING_HEALTH
        self.velocity = Vec3(0, 0, 0)
        if setup_mcs:
            self.load_model()
            self.setup_floor_collider()
            self.initialize_flash_sequence()
            #self.initialize_debug_text()
    
    def initialize_flash_sequence(self):
        self.redTex = loader.loadTexture("%s/red_screen.png" % TEXTURE_PATH)
        self.texStg = TextureStage('redTexStg')
        self.flashSequence = Sequence(Func(NodePath(self.get_model()).setTexture, self.texStg, self.redTex), Wait(0.25), Func(NodePath(self.get_model()).clearTexture, self.texStg))    
    
    def get_shield_sphere(self):
        #override to show some kind of shield
        return self.lifter
        
    def setup_floor_collider(self):
        self.floorQueue = CollisionHandlerQueue()
        
        self.lifterRay = CollisionRay(0, 0, (20.0 / self.get_model().getScale().getZ())-self.get_origin_height(), 0, 0, -1) #ray pointing down
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
        return self.get_model().getZ() > floorZ + self.get_origin_height() + 0.5
    
    def handleGravity(self):
        #in the future, have 2 rays - one above, one below, so he can't jump
        #through things?  Or let him jump through things.  If he can't, adapt
        #2nd half of if statement to include 2nd ray.
        z_vel = self.velocity.getZ()
        if self.in_air() or z_vel > 0:
            self.velocity.setZ(max(z_vel + GRAVITATIONAL_CONSTANT, TERMINAL_VELOCITY)) # jump / fall
            #self.velocity.setZ(0)
        else:
            #We hit (or stayed on) the ground...
            #how fast are we falling now? Use that to determine potential damage
            if z_vel < SAFE_FALL:
                damage = (-z_vel + SAFE_FALL) * FALL_DAMAGE_MULTIPLIER
                self.hit(damage)
            floorZ = self.floorQueue.getEntry(0).getSurfacePoint(render).getZ()
            if not self.get_model().isEmpty():
                self.get_model().setZ(floorZ + self.get_origin_height())
            self.velocity.setZ(0)
    
    def jump(self):
        if not self.in_air():
            self.velocity.setZ(self.get_jump_speed())  # he's on the ground - let him jump
    
    def toggle_god(self):
        self.invincible = not self.invincible
        print "Toggling God-mode"
    
    def updateGodModeTask(self, task):
        pass
    
    def stopGodModeTask(self, task):
        self.toggle_god()
        
    def load_model(self): pass
    def get_model(self): pass
    def add_radar(self): pass
    def remove_radar(self): pass
    def show_scopehairs(self): pass
    def hide_scopehairs(self): pass    
    def set_laser_glow(self, glow): pass
    def set_glow(self, glow): pass
    def die(self): pass
    def show_locate_hint(self): pass
    
    def act(self):
        self.do_debug()
    
    #Per is the amount to heal per tick... times is the number of ticks to heal for
    def debug(self, name, per, times):
        self.debuggers[name] = (per, times)
        if hasattr(self, "hud") and self.hud is not None:
            self.hud.healthBAR['text'] = "Debugging ..."
            print "Debugging %s: (%d, %d)"%(name, per, times)
    
    def do_debug(self):
        for name, debugger in self.debuggers.items():
            self.heal(debugger[0])
            if debugger[1] == -1:
                #Heal forever (eg. base terminals)
                continue
            if debugger[1] <= 1 or self.health == self.get_max_health():
                del self.debuggers[name]
            else:
                self.debuggers[name] = (debugger[0], debugger[1] - 1)
        if len(self.debuggers) == 0:
            if hasattr(self, "hud") and self.hud and self.hud.healthBAR:
                self.hud.healthBAR['text'] = ""
    
    def collect(self):
        prog = self.canCollect
        if not prog: return -1, None
        if prog.unique_str() not in self.game.programs: return -1, None
        if prog.name == "RAM" and len(self.programs) == MAX_PROGRAMS: return -1, None
        #if basic, have it do its effect and return. fails for non-effectful gdb
        if not prog.pick_up(self): return -1, prog
        
        for i,p in enumerate(self.programs):
            if not p: break
        else: # didn't break, there are no slots open
            return i, False
        
        # ok, pick it up
        alreadyHave = any(True for p in self.programs if p and p.name == prog.name)
        self.programs[i] = prog
        prog.disappear()
        #del self.game.programs[prog.unique_str()]
        if not alreadyHave:
            prog.add_effect(self)  
        self.canCollect = None
        return i, prog

    def warp(self):
        if self.canCollect:
            prog = self.canCollect
            if prog.warps():
                self.get_model().setPos(self.game.mode.level.south_bridge_pos())
    
    def drop(self, i):
        if 0 > i >= len(self.programs) or not self.programs[i]: return False
        pos = self.get_model().getPos()
        self.programs[i].reappear((pos[0], pos[1], pos[2] - self.get_origin_height()))

        # see if any of this type are left
        for j,p in enumerate(self.programs):
            if i != j and p != None and p.name == self.programs[i].name:
                break # yep, there's at least one left
        else: # nope, it was the last one
            self.programs[i].remove_effect(self)
          
        self.programs[i] = None
        return True
    
    def add_slot(self):
        self.programs.append(None)
    
    def hit(self,amt,hitter=None):
        if self.is_dead(): return False# semi-hack
        self.health -= amt/self.shield()
        self.flashSequence.start()
        if self.is_dead():
            self.health = 0 # hax
            self.die()
        return True
    
    def is_dead(self):
        return self.health <= 0

    def heal(self,amt):
        self.health = min(self.health + amt, self.get_max_health())
        
    def get_max_health(self):
        return 100
        
    def get_base_damage(self):
        return 10
    
    def get_base_shield(self):
        return 1.0 # no shield
        
    def damage(self):
        d = self.get_base_damage()
        for p in ifilter(lambda p: p != None, self.programs):
            d = p.damage_mod(d)
        return d

    def shield(self):
        s = self.get_base_shield()
        for p in ifilter(lambda p: p != None, self.programs):
            s = p.shield_mod(s)
        return s
    
    def rapid_fire(self):
        a = 0.5
        for p in ifilter(lambda p: p != None, self.programs):
            a = p.rapid_fire_mod(a)
        return a
