from agent import Agent
from constants import *
from pandac.PandaModules import TextureStage, Point3
from obstacle import QuadWall

class BaseTerminal(Agent):
    def __init__(self, game, room, parent, pos, hpr, scale, color):
        super(BaseTerminal, self).__init__(game, "%s_Terminal"%color, False)
        room.obstacles["terminal"] = self
        self.pos = pos
        self.hpr = hpr
        self.scale = scale
        self.color = color
        self.parent = parent
        self.load_model()
        self.setup_collider()
        self.initialize_flash_sequence()
        self.health = 5000
        self.debug("server_debug", 10, -1)
        
    def get_max_health(self):
        return 5000
    
    def get_model(self):
        return self.model
    
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
        self.wall = QuadWall(self.name, self.model, Point3(0.65,-0.05,1), Point3(-0.65,-0.05,1),
                             Point3(-0.65,-0.05,0), Point3(0.65,-0.05,0), DRONE_COLLIDER_MASK)
    
    def die(self):
        for debugger in self.debuggers.keys():
            del self.debuggers[debugger]
        #TODO do some point updating stuff here - use self.color
        self.destroy()
    
    def destroy(self):
        self.wall.destroy()
        self.model.removeNode()