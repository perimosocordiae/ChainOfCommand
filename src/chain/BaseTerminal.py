from agent import Agent
from constants import *
from pandac.PandaModules import TextureStage, Point3, TextNode, NodePath
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
        self.load_text()
        self.setup_collider()
        self.initialize_flash_sequence()
        self.health = self.get_max_health()
        self.debug("server_debug", 10, -1)
        
    def get_max_health(self):
        return 5000.0
    
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
    
    def load_text(self):
        self.text = TextNode('TerminalText')
        self.text.setText("\Corruption 0%%\nroot@%s:~$"%self.color)
        self.text.setTextColor(1, 1, 1, 1)
        self.text.setFont(self.game.shell.font)
        self.text.setAlign(TextNode.ACenter)
        self.consoleText = NodePath(self.text)
        self.consoleText.setShaderOff()
        self.consoleText.reparentTo(self.parent)
        self.consoleText.setScale(0.11)
        self.consoleText.setHpr(180,0,0)
        self.consoleText.setPos(self.parent.getRelativePoint(self.model, Point3(0, -0.1, 0.65)))
        
    
    def setup_collider(self):
        self.wall = QuadWall(self.name, self.model, Point3(0.65,-0.05,1), Point3(-0.65,-0.05,1),
                             Point3(-0.65,-0.05,0), Point3(0.65,-0.05,0), DRONE_COLLIDER_MASK)
    
    def hit(self, amt, damager=None):
        super(BaseTerminal, self).hit(amt, damager)
        self.update_text()
        
    def heal(self, amt):
        super(BaseTerminal, self).heal(amt)
        self.update_text()
    
    def update_text(self):
        percent = 100 - (100 * (self.health / self.get_max_health()))
        if percent < 20:
            status = "Status:\nnormal"
        elif percent < 40:
            status = "Status:\nwarning"
        elif percent < 60:
            status = "Status:\nsevere"
        elif percent < 80:
            status = "Status:\ncritical"
        elif percent < 100:
            status = "Status:\nfatal"
        else:
            status = "Segmentation Fault"
        self.text.clearText()
        #calling clear unfortunately clears all settings - reset them here:
        self.text.clear()
        self.text.setFont(self.game.shell.font)
        self.text.setAlign(TextNode.ACenter)
        self.text.setTextColor(1,1,1,1)
        self.text.setText("Corruption %d%%\n%s\nroot@%s:~#"%(percent, status, self.color))
    
    def die(self):
        for debugger in self.debuggers.keys():
            del self.debuggers[debugger]
        #TODO do some point updating stuff here - use self.color
        self.destroy()
    
    def destroy(self):
        self.wall.destroy()
        #self.consoleText.removeNode()
        #self.consoleText = None
        #self.text = None
        #self.model.removeNode()