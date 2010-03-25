import sys
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import CollisionHandlerEvent, CollisionTraverser, CollisionHandlerPusher
from pandac.PandaModules import WindowProperties

class PlayerEventHandler(DirectObject):
    
    def __init__(self, playr):
        self.player = playr
        # local effect keys
        self.accept('f',playr.switchPerspective)
        self.accept('wheel_up',playr.zoomIn)
        self.accept('wheel_down',playr.zoomOut)
        #self.accept('escape',playr.die) # hack, for now
        self.accept('escape',sys.exit)
        self.accept('p',self.pause_menu)
        self.accept('m',playr.toggle_background_music)
        self.accept('n',playr.toggle_sound_effects)
        self.accept('e',playr.jump)
        self.accept('tab',playr.show_scores)
        self.accept('tab-up',playr.hide_scores)
        
        # networked events
        self.accept('mouse1',playr.click)
        self.accept('mouse1-up',playr.clickRelease)
        self.accept('space',playr.collectOn)
        self.accept('space-repeat',playr.collectOn)
        self.accept('space-up',playr.collectOff)
        
        #drop program i; if we go past 9 programs, we'll need another key system anyway
        for i in range(9):
            self.accept('%d'%(i+1),playr.set_dropping,[i])
        
        self.timeout = False
        
        #set up the mouse handling properly
        self.wp = WindowProperties()
        self.wp.setCursorHidden(True)
        self.wp.setMouseMode(WindowProperties.MRelative)
        base.win.requestProperties(self.wp)
        base.win.movePointer(0, base.win.getXSize()/2, base.win.getYSize()/2)
    
    def pause_menu(self):
        self.timeout = not self.timeout
        if self.timeout:
            #stop handling key/mouse events, etc.
            self.wp.setCursorHidden(False)
            self.player.handleEvents = False
            base.win.requestProperties(self.wp)
            print "Time out! Come on guys, please?!"
        else:
            #start handling key/mouse events, etc.
            self.wp.setCursorHidden(True)
            self.wp.setMouseMode(WindowProperties.MRelative)
            self.player.handleEvents = True
            base.win.requestProperties(self.wp)
            base.win.movePointer(0, base.win.getXSize()/2, base.win.getYSize()/2)
            print "Okay, okay... time in!"

class GameEventHandler(DirectObject):
    
    def __init__(self, game):
        self.game = game
        self.pusherHandler = CollisionHandlerPusher()
        self.pusherHandler.setHorizontal(True)
        self.collisionHandler = CollisionHandlerEvent()
        self.collisionHandler.addInPattern('%fn-into-%in')
        self.collisionHandler.addAgainPattern('%fn-repeat-%in')
        self.collisionHandler.addOutPattern('%fn-out-%in')
        for t in game.players.itervalues():
            base.cTrav.addCollider(t.collider,self.collisionHandler)
            #base.cTrav.addCollider(t.pusher,self.collisionHandler)
            base.cTrav.addCollider(t.pusher,self.pusherHandler)
            self.pusherHandler.addCollider(t.pusher, t.tron)
        for d in game.drones.itervalues():
            base.cTrav.addCollider(d.pusher,self.pusherHandler)
            #base.cTrav.addCollider(d.collider,self.collisionHandler)
            self.pusherHandler.addCollider(d.pusher, d.panda)
        for p in game.programs.itervalues():
            base.cTrav.addCollider(p.pusher, self.pusherHandler)
            self.pusherHandler.addCollider(p.pusher, p.model)
        
        drones = game.drones.keys()
        progs  = game.programs.keys()
        walls = game.walls.keys()
            
        for t in game.players.iterkeys():
            for p in progs:
                self.accept("%s-into-%s"%(t,p),  self.tronHitsProg)
                self.accept("%s-repeat-%s"%(t,p),  self.tronHitsProg)
                self.accept("%s-out-%s"%(t,p), self.tronOutProg)
            for d in drones:
                self.accept("%s-into-%s"%(t,d),  self.tronHitsDrone)
                self.accept("%s-repeat-%s"%(t,d),self.tronRepeatsDrone)
            #for w in walls:
            #    self.accept("%s_wall-into-%s"%(t,w),  self.tronHitsWall)
            #    self.accept("%s_wall-repeat-%s"%(t,w),  self.tronHitsWall)
            #self.accept("%s_wall-into-%s"%(t,"tower_base"),  self.tronHitsWall)
            #self.accept("%s_wall-repeat-%s"%(t,"tower_base"),  self.tronHitsWall)
    
    def addProgramHandler(self, p):
        base.cTrav.addCollider(p.pusher, self.pusherHandler)
        self.pusherHandler.addCollider(p.pusher, p.model)
        for t in self.game.players.iterkeys():
            self.accept("%s-into-%s"%(t,p.unique_str()),  self.tronHitsProg)
            self.accept("%s-out-%s"%(t,p.unique_str()), self.tronOutProg)
    
    def addDroneHandler(self, d):
        base.cTrav.addCollider(d.pusher,self.pusherHandler)
        self.pusherHandler.addCollider(d.pusher, d.panda)
        dName = str(hash(d))
        for t in self.game.players.iterkeys():
            self.accept("%s-into-%s"%(t,dName),  self.tronHitsDrone)
            self.accept("%s-repeat-%s"%(t,dName),self.tronRepeatsDrone)
    
    def addPlayerHandler(self, t):
        base.cTrav.addCollider(t.collider,self.collisionHandler)
        #base.cTrav.addCollider(t.pusher,self.collisionHandler)
        base.cTrav.addCollider(t.pusher,self.pusherHandler)
        self.pusherHandler.addCollider(t.pusher, t.tron)
        drones = self.game.drones.keys()
        progs  = self.game.programs.keys()
        #walls = self.game.walls.keys()
        tName = t.name
        for p in progs:
            self.accept("%s-into-%s"%(tName,p),  self.tronHitsProg)
            self.accept("%s-out-%s"%(tName,p), self.tronOutProg)
        for d in drones:
            self.accept("%s-into-%s"%(tName,d),  self.tronHitsDrone)
            self.accept("%s-repeat-%s"%(tName,d),self.tronRepeatsDrone)
        #for w in walls:
        #    self.accept("%s_wall-into-%s"%(tName,w),  self.tronHitsWall)
        #    self.accept("%s_wall-repeat-%s"%(tName,w),  self.tronHitsWall)
        #self.accept("%s_wall-into-%s"%(tName,"tower_base"),  self.tronHitsWall)
        #self.accept("%s_wall-repeat-%s"%(tName,"tower_base"),  self.tronHitsWall)
        t.initialize_camera()
    
    def addWallHandler(self, w):
        print "NO THANKS!"
        #for t in self.game.players.iterkeys():
        #    self.accept("%s_wall-into-%s"%(t,w.name),  self.tronHitsWall)
        #    self.accept("%s_wall-repeat-%s"%(t,w.name),  self.tronHitsWall)
    
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
        if pn in self.game.programs.keys():
            tron,prog = self.game.players[tn], self.game.programs[pn]
            #tron.collect(prog)
            tron.canCollect = prog
            prog.show_desc()
            
    def tronOutProg(self,entry):
        tn,pn = entry.getFromNodePath().getName(),entry.getIntoNodePath().getName()
        if pn in self.game.programs.keys():
            tron,prog = self.game.players[tn], self.game.programs[pn]
            tron.canCollect = None
            prog.hide_desc()
    
    def tronHitsWall(self, entry):
        tn = entry.getFromNodePath().getName()
        tn = tn.replace("_wall", "")
        tron = self.game.players[tn]
        penetration = entry.getSurfacePoint(render) - entry.getInteriorPoint(render)
        newPos = tron.tron.getPos() + penetration
        #newPos.setZ(tron.tron.getZ())
        tron.tron.setFluidPos(newPos)
