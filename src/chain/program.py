MODEL_PATH = "../../models"

import direct.directbase.DirectStart
from direct.task import Task
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import Point3,Filename,Buffer,Shader, CollisionNode, CollisionSphere

class Program(object):

    def __init__(self,game,name,pos):
        self.game = game
        if not pos:
            pos = game.rand_point()
        self.name = name
        self.pos = pos
        self.load_model()
        self.setup_collider(len(self.game.programs))

    def load_model(self):
        self.model = loader.loadModel("%s/terminal_window.egg"%MODEL_PATH)
        self.model.setScale(2, 2, 2)
        self.model.setPos(self.pos[0], self.pos[1], 10)
        self.model.reparentTo(render)
		# TODO: draw program name on the terminal
        
        #Create the intervals needed to spin and expand/contract
        hpr1 = self.model.hprInterval(1.5, Point3(180, 0, 0), startHpr=Point3(0, 0, 0))
        hpr2 = self.model.hprInterval(1.5, Point3(360, 0, 0), startHpr=Point3(180, 0, 0))
        scale1 = self.model.scaleInterval(1.5, Point3(4, 4, 4), startScale=Point3(2, 2, 2), blendType='easeInOut')
        scale2 = self.model.scaleInterval(1.5, Point3(2, 2, 2), startScale=Point3(4, 4, 4), blendType='easeInOut')
        
        #Create and play the sequence that coordinates the intervals  
        Sequence(Parallel(scale1, hpr1), Parallel(scale2, hpr2)).loop()
    
    def setup_collider(self,i):
        self.collider = self.model.attachNewNode(CollisionNode('progcnode_%d'%i))
        self.collider.node().addSolid(CollisionSphere(0, 0, 0, 2))
        self.collider.show()

    # modifiers: generic program has no effect
    def damage_mod(self,d):
        return d
    def shield_mod(self,s):
        return s

class Rm(Program):
	
    def __init__(self,game,pos=None):
        super(Rm,self).__init__(game,'rm',pos)
	
    def damage_mod(self,d):
        return d*2 # double the player's damage

class Chmod(Program):

    def __init__(self,game,pos=None):
        super(Chmod,self).__init__(game,'chmod',pos)
	
    def shield_mod(self,s):
        return s*2 # double the player's shield strength

