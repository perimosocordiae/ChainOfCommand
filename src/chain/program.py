MODEL_PATH = "../../models"

from direct.task import Task
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import Point3,Filename,Buffer,Shader, CollisionNode, CollisionSphere, BitMask32
from agent import Agent

DRONE_COLLIDER_MASK = BitMask32.bit(1)

class Program(Agent):

    def __init__(self,game,name,pos):
        super(Program, self).__init__(game)
        self.game = game
        if not pos:
            pos = game.rand_point()
        self.name = name
        self.pos = pos
        self.load_model()
        self.setup_collider()
    
    def unique_str(self):
        return self.name+str(hash(self))
    
    def die(self):
        #maybe explode instead if killed?
        self.disappear()
    
    def disappear(self):
        self.model.stash()
        self.collider.stash()

    def load_model(self):
        self.model = loader.loadModel("%s/terminal_window_%s.egg"%(MODEL_PATH,self.name))
        self.model.setScale(2, 2, 2)
        self.model.setPos(self.pos[0], self.pos[1], 10)
        self.model.reparentTo(render)
        #TODO: draw program name on the terminal
        
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

    # modifiers: generic program has no effect
    def damage_mod(self,d):
        return d
    def shield_mod(self,s):
        return s
    def accuracy_mod(self, a):
        return a

class Rm(Program):
    
    def __init__(self,game,pos=None):
        super(Rm,self).__init__(game,'rm',pos)
    
    def damage_mod(self,d):
        return d*2 # double the player's damage

class Chmod(Program):

    def __init__(self,game,pos=None):
        super(Chmod,self).__init__(game,'chmod',pos)
    
    def shield_mod(self,s):
        return s*2.0 # double the player's shield strength

class Ls(Program):

    def __init__(self,game,pos=None):
        super(Ls,self).__init__(game,'ls',pos)
    
    def accuracy_mod(self,a):
        return a/2 # double the player's accuracy