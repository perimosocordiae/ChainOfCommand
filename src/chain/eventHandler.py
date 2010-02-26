from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import CollisionHandlerEvent, CollisionTraverser, CollisionHandlerPusher
from pandac.PandaModules import WindowProperties

class PlayerEventHandler(DirectObject):
    
    def __init__(self, playr):
        self.player = playr
        self.accept('f',playr.switchPerspective)
        self.accept('wheel_up',playr.zoomIn)
        self.accept('wheel_down',playr.zoomOut)
        self.accept('mouse1',playr.shoot)
        self.accept('escape',self.pause_menu)
        self.accept('p',self.pause_menu)
        self.accept('i',self.invert_control)
        self.timeout = False
        
        #set up the mouse handling properly
        self.wp = WindowProperties()
        self.wp.setCursorHidden(True)
        self.wp.setMouseMode(WindowProperties.MRelative)
        base.win.requestProperties(self.wp)
    
    def pause_menu(self):
        self.timeout = not self.timeout
        if self.timeout:
            #stop handling key/mouse events, etc.
            self.wp.setCursorHidden(False)
            self.player.handle_events(False)
            base.win.requestProperties(self.wp)
            print "Time out! Come on guys, please?!"
        else:
            #start handling key/mouse events, etc.
            self.wp.setCursorHidden(True)
            self.wp.setMouseMode(WindowProperties.MRelative)
            self.player.handle_events(True)
            base.win.requestProperties(self.wp)
            base.win.movePointer(0, base.win.getXSize()/2, base.win.getYSize()/2)
            print "Okay, okay... time in!"

    def invert_control(self):
        if self.player.handleEvents:
            print "Inverting up/down look controls..."
            self.player.inverted = not self.player.inverted

class GameEventHandler(DirectObject):
    
    def __init__(self, game):
        self.game = game
        self.pusherHandler = CollisionHandlerPusher()
        self.collisionHandler = CollisionHandlerEvent()
        self.collisionHandler.addInPattern('%fn-into-%in')
        self.collisionHandler.addAgainPattern('%fn-repeat-%in')
        for t in game.players.itervalues():
            base.cTrav.addCollider(t.collider,self.collisionHandler)
            base.cTrav.addCollider(t.pusher,self.pusherHandler)
            self.pusherHandler.addCollider(t.pusher, t.tron)
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
                self.accept("%s-repeat-%s"%(t,d),self.tronRepeatsDrone)
    
    def addProgramHandler(self, p):
        for t in self.game.players.iterkeys():
            self.accept("%s-into-%s"%(t,p.unique_str()),  self.tronHitsProg)
    
    def addDroneHandler(self, d):
        base.cTrav.addCollider(d.pusher,self.pusherHandler)
        #base.cTrav.addCollider(d.collider,self.collisionHandler)
        self.pusherHandler.addCollider(d.pusher, d.panda)
        dName = str(hash(d))
        for t in self.game.players.iterkeys():
            self.accept("%s-into-%s"%(t,dName),  self.tronHitsDrone)
            self.accept("%s-repeat-%s"%(t,dName),self.tronRepeatsDrone)
    
    def addPlayerHandler(self, t):
        base.cTrav.addCollider(t.collider,self.collisionHandler)
        base.cTrav.addCollider(t.pusher,self.pusherHandler)
        self.pusherHandler.addCollider(t.pusher, t.tron)
        drones = self.game.drones.keys()
        progs  = self.game.programs.keys()
        tName = t.name
        for p in progs:
            self.accept("%s-into-%s"%(tName,p),  self.tronHitsProg)
        for d in drones:
            self.accept("%s-into-%s"%(tName,d),  self.tronHitsDrone)
            self.accept("%s-repeat-%s"%(tName,d),self.tronRepeatsDrone)
        t.initialize_camera()
    
    def tronHitsDrone(self,entry):
        tn,dn = entry.getFromNodePath().getName(),entry.getIntoNodePath().getName()
        try:
            drone,tron = self.game.drones[dn], self.game.players[tn]
        except KeyError: return
        tron.hit(drone.damage())
        
    def tronRepeatsDrone(self, entry):
        tn,dn = entry.getFromNodePath().getName(),entry.getIntoNodePath().getName()
        try:
            drone,tron = self.game.drones[dn], self.game.players[tn]
        except KeyError: return
        tron.hit(drone.repeat_damage())
        
    def tronHitsProg(self,entry):
        tn,pn = entry.getFromNodePath().getName(),entry.getIntoNodePath().getName()
        tron,prog = self.game.players[tn], self.game.programs[pn]
        tron.collect(prog)
