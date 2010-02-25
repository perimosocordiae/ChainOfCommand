from direct.showbase.DirectObject import DirectObject
#from player import Player

#Handle all key events that involve pressing a key once...
#For now that's just "f" to switch perspective
class PlayerEventHandler(DirectObject):
    
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

class GameEventHandler(DirectObject):
    
    def __init__(self, game):
        self.game = game
        drones = ["dronecnode_%d"%i for i in range(len(self.game.drones))]
        trons  = ["troncnode_%d"%i  for i in range(len(self.game.players))]
        progs  = ["progcnode_%d"%i  for i in range(len(self.game.programs))]
        for d in drones:
            for t in trons:
                self.accept("%s-into-%s"%(d,t),  self.droneHitsTron)
                self.accept("%s-repeat-%s"%(d,t),self.droneHitsTron)
            for d2 in drones:
                self.accept("%s-into-%s"%(d,d2), self.droneHitsDrone)
        for t in trons:
            for p in progs:
                self.accept("%s-into-%s"%(t,p),   self.tronHitsProg)
    
    def droneHitsTron(self,entry):
        di = get_index_from_name(entry.getFromNodePath().getName())
        ti = get_index_from_name(entry.getIntoNodePath().getName())
        drone = self.game.drones[di]
        tron = self.game.players[ti]
        tron.hit(drone.damage())
        
    def tronHitsProg(self,entry):
        ti = get_index_from_name(entry.getFromNodePath().getName())
        pi = get_index_from_name(entry.getIntoNodePath().getName())
        tron = self.game.players[ti]
        prog = self.game.programs[pi]
        tron.collect(prog)
    
    def droneHitsDrone(self,entry):
        d1 = get_index_from_name(entry.getFromNodePath().getName())
        d2 = get_index_from_name(entry.getIntoNodePath().getName())
        drone1 = self.game.drones[d1]
        drone2 = self.game.drones[d2]
        print "drones hit"
        
def get_index_from_name(name):
    return int(name.split('_')[-1])
