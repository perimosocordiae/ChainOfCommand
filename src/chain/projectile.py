#how much faster than a unit vector should it travel? 
SPEED_SCALE = 6.0

from pandac.PandaModules import Vec3, Point3
from direct.interval.IntervalGlobal import *

class Projectile(object):
    
    def __init__(self, model_file):
        self.load_model(model_file)
    
    def load_model(self, model_file):
        self.model = loader.loadModel(model_file)
        self.model.reparentTo(render)
        
    def set_pos(self, pos):
        self.model.setPos(pos)
    
    def set_trajectory(self, trajectory):
        fullTrajec = trajectory
        lookAt = self.model.getPos() + fullTrajec
        trajectory.normalize()
        self.model.setPos(self.model.getPos() + (trajectory * 18))
        if fullTrajec.length > 0.005: 
            moveIt = self.model.posInterval(0.4, lookAt)
            Sequence(moveIt, Func(self.kill)).start()
    
    def kill(self):
        self.model.stash()