from direct.task import Task
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import (Point3, Filename, Buffer, Shader, CollisionNode,
        CollisionTube, CollisionSphere, BitMask32, TextNode, NodePath, CollisionPolygon,
        TextureStage)
from agent import Agent
from constants import *

BASE_SCALE = 2
DESCRIPTION_SCALE = 0.2

#********************************** BASE CLASS **********************************

class Program(Agent):
    
    def __init__(self, game, room, name, prefix, desc, scale, pos):
        super(Program, self).__init__(game, name, False)
        self.game = game
        if not pos:
            pos = room.rand_point()
        self.prefix = prefix
        self.scale = scale
        self.pos = pos
        self.load_model()
        self.initialize_flash_sequence()
        #self.initialize_debug_text()
        self.load_desc(desc)
        self.setup_interval()
        self.setup_collider()
    
    def unique_str(self):
        return self.name + str(hash(self))
    
    def die(self):
        #maybe explode instead if killed?
        self.disappear()
        #TODO: see if we should remove from list
    
    def disappear(self):
        if hasattr(self, "seq") and self.seq:
            self.seq.finish()
        if self.desc:
            self.desc.removeNode()
        if self.collider:
            self.collider.removeNode()
        if self.pusher:
            self.pusher.removeNode()
        if self.hitter:
            self.hitter.removeNode()
        if self.model:
            #self.model.stash()
            self.model.removeNode()
        self.desc = None
        self.collider = None
        self.pusher = None
        self.hitter = None
        self.model = None
        #self.collider.stash()
        #self.pusher.stash()
    
    def load_model(self):
        self.model = loader.loadModel("%s/%s%s.bam" % (MODEL_PATH, self.prefix, self.name))
        self.model.setScale(self.scale)
        self.model.reparentTo(render)
        self.model.setPos(Point3(self.pos[0], self.pos[1], self.pos[2] + 10))
        if self.name != "RAM":
            textFront = TextNode("NameFront")
            textFront.setText("%s" % self.name)
            textFront.setTextColor(1,0,0,1)
            textFront.setFont(self.game.shell.font)
            textFront.setAlign(TextNode.ACenter)
            textNodeFront = self.model.attachNewNode(textFront)
            textNodeFront.setScale(3.4 / len(self.name))
            textNodeFront.setPos(-0.42/len(self.name),-0.14,-0.6/len(self.name))
            textBack = TextNode("NameFront")
            textBack.setText("%s" % self.name)
            textBack.setTextColor(1,0,0,1)
            textBack.setFont(self.game.shell.font)
            textBack.setAlign(TextNode.ACenter)
            textNodeBack = self.model.attachNewNode(textBack)
            textNodeBack.setScale(3.4 / len(self.name))
            textNodeBack.setPos(0.42/len(self.name),0.119,-0.6/len(self.name))
            textNodeBack.setHpr(180,0,0)
        
    def get_model(self):
        return self.model
    
    def setup_interval(self):
        #Create the intervals needed to spin and expand/contract
        hpr1 = self.model.hprInterval(1.5, Point3(180, 0, 0), startHpr=Point3(0, 0, 0))
        hpr2 = self.model.hprInterval(1.5, Point3(360, 0, 0), startHpr=Point3(180, 0, 0))
        scale1 = self.model.scaleInterval(1.5, self.scale * 2, startScale=self.scale, blendType='easeInOut')
        scale2 = self.model.scaleInterval(1.5, self.scale, startScale=self.scale * 2, blendType='easeInOut')
        
        #Create and play the sequence that coordinates the intervals  
        self.seq = Sequence(Parallel(scale1, hpr1), Parallel(scale2, hpr2))
        self.seq.loop()
    
    def setup_collider(self):
        self.setup_collider_solid(CollisionSphere(0, 0, 0, 8),
                CollisionSphere(0, 0, 0, 4), CollisionPolygon(Point3(-1, 0, -0.877),
                Point3(1, 0, -0.877), Point3(1, 0, 0.877), Point3(-1, 0, 0.877)))
    
    def setup_collider_solid(self, solid, pusherSolid, hitterSolid):
        self.collider = self.model.attachNewNode(CollisionNode(self.unique_str() + "_donthitthis"))
        self.collider.node().addSolid(solid)
        self.collider.node().setIntoCollideMask(DRONE_COLLIDER_MASK)
        self.collider.node().setFromCollideMask(0)
        
        self.pusher = self.model.attachNewNode(CollisionNode(self.unique_str() + "_pusher_donthitthis"))
        self.pusher.node().addSolid(pusherSolid)
        self.pusher.node().setIntoCollideMask(PROGRAM_PUSHER_MASK)
        self.pusher.node().setFromCollideMask(PROGRAM_PUSHER_MASK)
        
        self.hitter = self.model.attachNewNode(CollisionNode(self.unique_str()))
        self.hitter.node().addSolid(hitterSolid)
        self.hitter.node().setIntoCollideMask(DRONE_COLLIDER_MASK)
        self.hitter.node().setFromCollideMask(0)
        
    def load_desc(self, desc):
        text = TextNode(self.name + 'Desc')
        text.setText(desc)
        text.setTextColor(0, 0, 0, 1)
        text.setFont(self.game.shell.font)
        text.setAlign(TextNode.ACenter)
        text.setFrameColor(0, 0, 0, 1)
        text.setFrameAsMargin(0, 0, 0, 0)
        text.setCardColor(1, 1, 1, 1)
        text.setCardAsMargin(0, 0, 0, 0)
        text.setCardDecal(True)
        self.desc = NodePath(text)
        self.desc.stashTo(self.model)
        self.desc.setScale(DESCRIPTION_SCALE)
        self.desc.setPos(0, 0, 1.5)
        self.desc.setBillboardPointEye()
        
    def show_desc(self):
        if self.desc:
            self.desc.unstash()

    def hide_desc(self):
        if self.desc:
            self.desc.stash()
    
    #return true if the player should try to put the program in a slot
    def pick_up(self, player):
        return True
#******************************** BASIC PROGRAMS ********************************

#Programs that have an immediate effect and then disappear
class Basic(Program):
    
    def __init__(self, game, room, name, desc, scale, pos, prefix=''):
        super(Basic, self).__init__(game, room, name, prefix, desc, scale, pos)
    
    #do effect and make it disappear; return false so player doesn't add it to a slot
    def pick_up(self, player):
        self.do_effect(player)
        self.disappear()
        del self.game.programs[self.unique_str()]
        return False
    
    def get_description(self):
        return self.description

    def do_effect(self, player):
        return
    
class RAM(Basic):
    def __init__(self, game, room, pos=None, scale=4.0):
        super(RAM, self).__init__(game, room, 'RAM', "Add Program Slot", scale, pos)
        self.desc.setZ(0.5)
        self.desc.setScale(0.1)
    
    def do_effect(self, agent):
        agent.add_slot()
        
    def setup_interval(self):
        #do nothing - the interval doesn't exist for RAM
        pass
    
    #RAM is in slots - it collides differently
    def setup_collider(self):
        self.setup_collider_solid(CollisionTube(-1, 0, 0, 1, 0, 0, 0.6),
                            CollisionTube(-1, 0, 0, 1, 0, 0, 0.6),
                            CollisionPolygon(Point3(-1, 0, -0.25), Point3(1, 0, -0.25),
                            Point3(1, 0, 0.25), Point3(-1, 0, 0.25)))

class Debug(Basic):
    #Per is the amount to heal per tick... times is the number of ticks to heal for
    def __init__(self, game, room, name, desc, scale, pos, prefix='', per=0.8, times=125):
        super(Debug, self).__init__(game, room, name, desc, scale, pos, prefix)
        self.per = per
        self.times = times
    
    def pick_up(self, player):
        if player.health < player.get_max_health(): # no effect if full health
            super(Debug, self).pick_up(player)
        else:
            print "Already at full health"
        return False

    def do_effect(self, agent):
        agent.debug(self.unique_str(), self.per, self.times)

class Gdb(Debug):
    def __init__(self, game, room, pos=None):
        super(Gdb, self).__init__(game, room, 'gdb', "Restore Health", BASE_SCALE, pos, 'terminal_window_')

#***************************** ACHIEVEMENT PROGRAMS *****************************

#The "Achievement" Programs that take up a slot
class Achievement(Program):
    
    def __init__(self, game, room, name, desc, scale, pos):
         super(Achievement, self).__init__(game, room, name, 'terminal_window_', desc, scale, pos)
         self.description = desc
        
    def reappear(self, pos):
        self.load_model()
        self.load_desc(self.description)
        #self.model.unstash()
        #self.collider.unstash()
        #self.pusher.unstash()
        self.model.setPos(pos)
        #self.collider.node().setIntoCollideMask(DRONE_COLLIDER_MASK)
        #self.pusher.node().setIntoCollideMask(PROGRAM_PUSHER_MASK)
        #self.pusher.node().setFromCollideMask(PROGRAM_PUSHER_MASK)
        self.setup_interval()
        self.setup_collider()
        self.game.readd_program(self)
    
    # modifiers: generic program has no effect
    def damage_mod(self, d):
        return d
    def shield_mod(self, s):
        return s
    def rapid_fire_mod(self, a):
        return a
    def scope_zoom_mod(self, d):
        return d
    def radar_mod(self, d):
        return d
    #override these methods to create/remove visual effects when you have programs
    def add_effect(self, agent):
        return
    def remove_effect(self, agent):
        return

class Flag(Achievement):
    def __init__(self, game, room, color, pos=None):
        super(Flag, self).__init__(game, room, '--flag', "%s flag" % color, BASE_SCALE, pos)
        self.color = color
        self.load_texture()
    
    def reappear(self, pos):
        super(Flag, self).reappear(pos)
        self.load_texture()
        for color,base in self.game.level.bases.iteritems():
            if color != self.color and base.has_point(pos):
                self.game.ctf_scores[color] += 1
                self.game.add_point_for(color)
                break
    
    def load_texture(self):
        tex = loader.loadTexture("%s/%s_flag.jpg"%(TEXTURE_PATH, self.color))
        ts = TextureStage('ts')
        ts.setMode(TextureStage.MReplace)
        self.model.setTexture(ts, tex)
    
    def damage_mod(self, d):
        return d * 0.1 # double the player's damage
    
    def shield_mod(self, s):
        return s * 1.5
    
    def rapid_fire_mod(self, a):
        return a * 4 # 4x the shooting delay
    
class Rm(Achievement):
    def __init__(self, game, room, pos=None):
        super(Rm, self).__init__(game, room, 'rm', "Damage x 2", BASE_SCALE, pos)
    
    def damage_mod(self, d):
        return d * 2 # double the player's damage
    
    def add_effect(self, agent):
        agent.set_laser_glow(True)
        agent.set_glow(True)
    
    def remove_effect(self, agent):
        agent.set_laser_glow(False)
        agent.set_glow(False)

class Chmod(Achievement):
    def __init__(self, game, room, pos=None):
        super(Chmod, self).__init__(game, room, 'chmod', "Shield x 2", BASE_SCALE, pos)
    
    def shield_mod(self, s):
        return s * 2 # double the player's shield strength
    
    def add_effect(self, agent):
        agent.get_shield_sphere().show()
    def remove_effect(self, player):
        player.get_shield_sphere().hide()

class DashR(Achievement):
    def __init__(self, game, room, pos=None):
        super(DashR, self).__init__(game, room, '-r', "Fire Speed x 2", BASE_SCALE, pos)
    
    def rapid_fire_mod(self, a):
        return a / 2 # half the shooting delay
    
class Locate(Achievement):
    def __init__(self, game, room, pos=None):
        super(Locate, self).__init__(game, room, 'locate', "Scope Zoom x 2", BASE_SCALE, pos)
        
    def scope_zoom_mod(self, d):
        return d * 2
    
    def add_effect(self, agent):
        agent.show_scopehairs()
        if not self.game.had_locate :
            agent.show_locate_hint()
        
    def remove_effect(self, agent):
        agent.hide_scopehairs()        
    
class Ls(Achievement):
    def __init__(self, game, room, pos=None):
        super(Ls, self).__init__(game, room, 'ls', "Radar x 1.5", BASE_SCALE, pos)
    
    def radar_mod(self, r):
        return r * 1.5
    
    def add_effect(self, agent):
        print "add radar"
        agent.add_radar()
    def remove_effect(self, agent):
        print "remove radar"
        agent.remove_radar()
