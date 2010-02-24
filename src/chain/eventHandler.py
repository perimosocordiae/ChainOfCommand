from direct.showbase.DirectObject import DirectObject
#from player import Player

#Handle all key events that involve pressing a key once...
#For now that's just "f" to switch perspective
class KeyHandler(DirectObject):
    
    def __init__(self, playr):
        self.player = playr
        self.accept('f',playr.switchPerspective)
        self.accept('wheel_up',playr.zoomIn)
        self.accept('wheel_down',playr.zoomOut)
        self.accept('space',playr.shoot)
        self.accept('escape',self.pause_menu)
        self.accept('p',self.pause_menu)
        self.accept('i',self.invert_control)

    def pause_menu(self):
        print "Time out! Come on guys, please?!"
        #TODO: actually make this happen

    def invert_control(self):
        print "Inverting up/down look controls..."
        self.player.inverted = not self.player.inverted

