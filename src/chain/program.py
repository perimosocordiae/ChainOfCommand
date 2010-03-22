MODEL_PATH = "../../models"

from direct.task import Task
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import Point3,Filename,Buffer,Shader, CollisionNode, CollisionSphere, BitMask32
from agent import Agent
from pandac.PandaModules import TextNode, NodePath
from constants import *

BASE_SCALE = 2
DESCRIPTION_SCALE = 0.2

#********************************** BASE CLASS **********************************

class Program(Agent):
    
    def __init__(self,game,name,prefix,desc,scale,pos):
        super(Program, self).__init__(game, name, False)
        self.game = game
        if not pos:
            pos = game.rand_point()
        self.prefix = prefix
        self.scale = scale
        self.pos = pos
        self.load_model()
        self.load_desc(desc)
        self.setup_interval()
        self.setup_collider()
    
    def unique_str(self):
        return self.name+str(hash(self))
    
    def die(self):
        #maybe explode instead if killed?
        self.disappear()
    
    def disappear(self):
        if self.desc:
            self.desc.removeNode()
        if self.collider:
            self.collider.removeNode()
        if self.pusher:
            self.pusher.removeNode()
        if self.model:
            #self.model.stash()
            self.model.removeNode()
        self.desc = None
        self.collider = None
        self.pusher = None
        self.model = None
        #self.collider.stash()
        #self.pusher.stash()
    
    def load_model(self):
        self.model = loader.loadModel("%s/%s%s.egg"%(MODEL_PATH,self.prefix,self.name))
        self.model.setScale(self.scale)
        self.model.setPos(self.pos[0], self.pos[1], 10)
        self.model.reparentTo(render)
    
    def setup_interval(self):
        #Create the intervals needed to spin and expand/contract
        hpr1 = self.model.hprInterval(1.5, Point3(180, 0, 0), startHpr=Point3(0, 0, 0))
        hpr2 = self.model.hprInterval(1.5, Point3(360, 0, 0), startHpr=Point3(180, 0, 0))
        scale1 = self.model.scaleInterval(1.5, self.scale*2, startScale=self.scale, blendType='easeInOut')
        scale2 = self.model.scaleInterval(1.5, self.scale, startScale=self.scale*2, blendType='easeInOut')
        
        #Create and play the sequence that coordinates the intervals  
        Sequence(Parallel(scale1, hpr1), Parallel(scale2, hpr2)).loop()
    
    def setup_collider(self):
        self.collider = self.model.attachNewNode(CollisionNode(self.unique_str()))
        self.collider.node().addSolid(CollisionSphere(0, 0, 0, 2))
        self.collider.node().setIntoCollideMask(DRONE_COLLIDER_MASK)
        #self.collider.show()
        
        self.pusher = self.model.attachNewNode(CollisionNode(self.unique_str() + "_pusher"))
        self.pusher.node().addSolid(CollisionSphere(0, 0, 0, 2))
        self.pusher.node().setIntoCollideMask(PROGRAM_PUSHER_MASK)
        self.pusher.node().setFromCollideMask(PROGRAM_PUSHER_MASK)
        
    def load_desc(self, desc):
        text = TextNode(self.name + 'Desc')
        text.setText(desc)
        text.setTextColor(1,1,1,1)
        text.setFont(self.game.font)
        text.setAlign(TextNode.ACenter)
        self.desc = NodePath(text)
        self.desc.stashTo(self.model)
        self.desc.setScale(DESCRIPTION_SCALE)
        self.desc.setPos(0,0,1.5)
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
    
    def __init__(self,game,name,desc,scale,pos):
        super(Basic, self).__init__(game, name, '', desc, scale, pos)
    
    #do effect and make it disappear; return false so player doesn't add it to a slot
    def pick_up(self, player):
        self.do_effect(player)
        self.disappear()
        return False
    
    def do_effect(self, player):
        return
    
class RAM(Basic):
    DESC = "Add Program Slot"
    
    def __init__(self,game,pos=None):
        super(RAM, self).__init__(game, 'RAM', self.DESC, 4, pos)
        self.desc.setZ(0.5)
        self.desc.setScale(0.1)
    
    def get_description(self):
        return self.DESC
    
    def do_effect(self, agent):
        agent.add_slot()

#***************************** ACHIEVEMENT PROGRAMS *****************************

#The "Achievement" Programs that take up a slot
class Achievement(Program):
    
    def __init__(self,game,name,desc,scale,pos):
         super(Achievement, self).__init__(game, name, 'terminal_window_', desc, scale, pos)
        
    def reappear(self, pos):
        self.load_model()
        self.load_desc(self.get_description())
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
    def damage_mod(self,d):
        return d
    def shield_mod(self,s):
        return s
    def rapid_fire_mod(self, a):
        return a
    #override these methods to create/remove visual effects when you have programs
    def add_effect(self, agent):
        return
    def remove_effect(self, agent):
        return
    
class Rm(Achievement):
    DESC = "Damage x 2"
    def __init__(self,game,pos=None):
        super(Rm,self).__init__(game,'rm',self.DESC,BASE_SCALE,pos)
    
    def damage_mod(self,d):
        return d*2 # double the player's damage
    
    def get_description(self):
        return self.DESC
    
    def add_effect(self, agent):
        agent.set_laser_glow(True)
        agent.set_glow(True)
    
    def remove_effect(self, agent):
        agent.set_laser_glow(False)
        agent.set_glow(False)

class Chmod(Achievement):
    DESC = "Shield x 2"
    def __init__(self,game,pos=None):
        super(Chmod,self).__init__(game,'chmod',self.DESC,BASE_SCALE,pos)
    
    def shield_mod(self,s):
        return s*2.0 # double the player's shield strength
    
    def get_description(self):
        return self.DESC
    
    def add_effect(self, agent):
        agent.get_shield_sphere().show()
    def remove_effect(self, player):
        player.get_shield_sphere().hide()

class DashR(Achievement):
    DESC = "Rapid Fire"
    def __init__(self,game,pos=None):
        super(DashR,self).__init__(game,'-r',self.DESC,BASE_SCALE,pos)
    
    def rapid_fire_mod(self,a):
        return a/2 # half the shooting delay
    def get_description(self):
        return self.DESC