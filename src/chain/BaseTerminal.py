from agent import Agent
from constants import *
from pandac.PandaModules import TextureStage

class BaseTerminal(Agent):
    def __init__(self, game, name, parent, pos, hpr, scale, color):
        super(BaseTerminal, self).__init__(game, name, False)
        self.pos = pos
        self.hpr = hpr
        self.scale = scale
        self.color = color
        self.parent = parent
        self.load_model()
        self.setup_collider()
    
    def load_model(self):
        self.model = loader.loadModel("%s/base_terminal.bam"%MODEL_PATH)
        ts = TextureStage('ts')
        ts.setMode(TextureStage.MReplace)
        ts.setSort(5)
        self.model.setTexture(ts, loader.loadTexture("%s/base_terminal_%s.jpg"%(TEXTURE_PATH,self.color)))
        self.model.setPos(self.pos)
        self.model.setHpr(self.hpr)
        self.model.setScale(self.scale)
        self.model.reparentTo(self.parent)
    
    def setup_collider(self):
        pass
    
    def die(self):
        #TODO do some point updating stuff here - use self.color
        self.destroy()
    
    def destroy(self):
        self.model.removeNode()