#how much faster than a unit vector should it travel? 
SPEED_SCALE = 6.0
MODEL_PATH = "../../models"

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
    
    def fire(self, trajectory):
        fullTrajec = trajectory
        lookAt = self.model.getPos() + fullTrajec
        trajectory.normalize()
        self.model.setPos(self.model.getPos() + (trajectory * 18))
        if fullTrajec.length > 0.005: 
            moveIt = self.model.posInterval(10.4, lookAt)
            Sequence(moveIt, Func(self.kill)).start()
    
    def kill(self):
        #self.model.stash()
        self.model.removeNode()
        
class Laser(Projectile):
    def __init__(self):
        self.load_model("%s/laser.egg"%MODEL_PATH)
        tex = loader.loadTexture("%s/laser_Cube.tga"%MODEL_PATH, "%s/laser_Cube_texture.jpg"%MODEL_PATH)
        self.model.setTexture(tex)
