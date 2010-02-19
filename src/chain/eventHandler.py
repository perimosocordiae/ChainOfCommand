from direct.showbase.DirectObject import DirectObject
#from player import Player

#Handle all key events that involve pressing a key once...
#For now that's just "f" to switch perspective
class KeyHandler(DirectObject):
    
    def __init__(self, playr):
        self.playr = playr
        self.accept('f',self.playr.switchPerspective)
        self.accept('wheel_up',self.playr.zoomIn)
        self.accept('wheel_down',self.playr.zoomOut)