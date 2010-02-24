MODEL_PATH = "../../models"

import direct.directbase.DirectStart
from direct.task import Task
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import Point3
from pandac.PandaModules import Vec3
from pandac.PandaModules import Filename,Buffer,Shader

class Program(object):

    def __init__(self,name,pos=(0,0)):
        self.name = name
        self.pos = pos
        self.load_model()

    def load_model(self):
        actor = loader.loadModel("%s/terminal_window.egg"%MODEL_PATH)
        actor.setScale(2, 2, 2)
        actor.setPos(self.pos[0], self.pos[1], 10)
        actor.reparentTo(render)
		# TODO: draw program name on the terminal
        
        #Create the intervals needed to spin and expand/contract
        hpr1 = actor.hprInterval(1.5, Point3(180, 0, 0), startHpr=Point3(0, 0, 0))
        hpr2 = actor.hprInterval(1.5, Point3(360, 0, 0), startHpr=Point3(180, 0, 0))
        scale1 = actor.scaleInterval(1.5, Point3(4, 4, 4), startScale=Point3(2, 2, 2), blendType='easeInOut')
        scale2 = actor.scaleInterval(1.5, Point3(2, 2, 2), startScale=Point3(4, 4, 4), blendType='easeInOut')
        
        #Create and play the sequence that coordinates the intervals  
        Sequence(Parallel(scale1, hpr1), Parallel(scale2, hpr2)).loop()
    
    # modifiers: generic program has no effect
    def damage_mod(self,d):
        return d
    def shield_mod(self,s):
        return s

class Rm(Program):
	
    def __init__(self,pos=(0,0)):
        super(Rm,self).__init__('rm',pos)
	
    def damage_mod(self,d):
        return d*2 # double the player's damage

class Chmod(Program):

    def __init__(self,pos=(0,0)):
        super(Chmod,self).__init__('chmod',pos)
	
    def shield_mod(self,s):
        return s*2 # double the player's shield strength

