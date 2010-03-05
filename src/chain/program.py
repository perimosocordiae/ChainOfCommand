MODEL_PATH = "../../models"

from direct.task import Task
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import Point3,Filename,Buffer,Shader, CollisionNode, CollisionSphere, BitMask32
from agent import Agent
from pandac.PandaModules import TextNode, NodePath
from constants import *

class Program(Agent):
    
    def __init__(self,game,name,desc,pos):
        super(Program, self).__init__(game)
        self.game = game
        if not pos:
            pos = game.rand_point()
        self.name = name
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
        self.collider.removeNode()
        self.pusher.removeNode()
        self.desc.removeNode()
        #self.model.stash()
        self.model.removeNode()
        #self.collider.stash()
        #self.pusher.stash()
        
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
        self.setup_collider()
        self.game.readd_program(self)

    def load_model(self):
        self.model = loader.loadModel("%s/terminal_window_%s.egg"%(MODEL_PATH,self.name))
        self.model.setScale(2, 2, 2)
        self.model.setPos(self.pos[0], self.pos[1], 10)
        self.model.reparentTo(render)
    
    def setup_interval(self):
        #Create the intervals needed to spin and expand/contract
        hpr1 = self.model.hprInterval(1.5, Point3(180, 0, 0), startHpr=Point3(0, 0, 0))
        hpr2 = self.model.hprInterval(1.5, Point3(360, 0, 0), startHpr=Point3(180, 0, 0))
        scale1 = self.model.scaleInterval(1.5, Point3(4, 4, 4), startScale=Point3(2, 2, 2), blendType='easeInOut')
        scale2 = self.model.scaleInterval(1.5, Point3(2, 2, 2), startScale=Point3(4, 4, 4), blendType='easeInOut')
        
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
        self.desc.setScale(0.2)
        self.desc.setPos(0,0,1.5)
        self.desc.setBillboardPointEye()
        
    def show_desc(self):
        self.desc.unstash()

    def hide_desc(self):
        self.desc.stash()

    # modifiers: generic program has no effect
    def damage_mod(self,d):
        return d
    def shield_mod(self,s):
        return s
    def rapid_fire_mod(self, a):
        return a
    
class Rm(Program):
    DESC = "Damage x 2"
    def __init__(self,game,pos=None):
        super(Rm,self).__init__(game,'rm',self.DESC,pos)
    
    def damage_mod(self,d):
        return d*2 # double the player's damage
    def get_description(self):
        return self.DESC

class Chmod(Program):
    DESC = "Shield x 2"
    def __init__(self,game,pos=None):
        super(Chmod,self).__init__(game,'chmod',self.DESC,pos)
    
    def shield_mod(self,s):
        return s*2.0 # double the player's shield strength
    def get_description(self):
        return self.DESC

class DashR(Program):
    DESC = "Rapid Fire"
    def __init__(self,game,pos=None):
        super(DashR,self).__init__(game,'-r',self.DESC,pos)
    
    def rapid_fire_mod(self,a):
        return True # allow rapid-fire
    def get_description(self):
        return self.DESC