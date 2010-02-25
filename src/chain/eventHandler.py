from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import CollisionHandlerEvent, CollisionTraverser, CollisionHandlerPusher

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
        base.cTrav = CollisionTraverser()
        base.cTrav.showCollisions(render)
        self.pusherHandler = CollisionHandlerPusher()
        self.collisionHandler = CollisionHandlerEvent()
        self.collisionHandler.addInPattern('%fn-into-%in')
        self.collisionHandler.addAgainPattern('%fn-repeat-%in')
        for t in game.players.itervalues():
            base.cTrav.addCollider(t.collider,self.collisionHandler)
        for d in game.drones.itervalues():
            base.cTrav.addCollider(d.pusher,self.pusherHandler)
            #base.cTrav.addCollider(d.collider,self.collisionHandler)
            self.pusherHandler.addCollider(d.pusher, d.panda)
        
        drones = game.drones.keys()
        progs  = game.programs.keys()
        for t in game.players.iterkeys():
            for p in progs:
                self.accept("%s-into-%s"%(t,p),  self.tronHitsProg)
            for d in drones:
                self.accept("%s-into-%s"%(t,d),  self.tronHitsDrone)
                self.accept("%s-repeat-%s"%(t,d),self.tronHitsDrone)
    
    def tronHitsDrone(self,entry):
        tn,dn = entry.getFromNodePath().getName(),entry.getIntoNodePath().getName()
        try:
            drone,tron = self.game.drones[dn], self.game.players[tn]
        except KeyError: return
        tron.hit(drone.damage())
        
    def tronHitsProg(self,entry):
        tn,pn = entry.getFromNodePath().getName(),entry.getIntoNodePath().getName()
        tron,prog = self.game.players[tn], self.game.programs[pn]
        tron.collect(prog)