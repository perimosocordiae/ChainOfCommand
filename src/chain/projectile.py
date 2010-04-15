#how much faster than a unit vector should it travel? 
SPEED_SCALE = 6.0

from pandac.PandaModules import Vec3, Point3, TextureStage
from direct.interval.IntervalGlobal import *
from constants import *

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
            moveIt = self.model.posInterval(3.0, lookAt)
            Sequence(moveIt, Func(self.kill)).start()
    
    def kill(self):
        #self.model.stash()
        self.model.removeNode()
        
class Laser(Projectile):
    def __init__(self):
        self.load_model("%s/laser.bam"%MODEL_PATH)
        self.tex = loader.loadTexture("%s/laser_Cube.tga"%TEXTURE_PATH)
        self.model.setTexture(self.tex)
        self.ts = TextureStage('ts')
        self.ts.setMode(TextureStage.MGlow)
        self.glow = loader.loadTexture("%s/laser_Cube_texture_glow.jpg"%TEXTURE_PATH)
        self.model.setTexture(self.tex)
        self.set_glow(False)
        
    def set_glow(self, glow):
        if glow:
            self.model.setTexture(self.ts, self.glow)
        else:
            self.model.clearTexture(self.ts)
