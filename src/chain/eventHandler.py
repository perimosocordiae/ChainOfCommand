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
        self.accept('escape',playr.game.game_over)
        #self.accept('escape',sys.exit)
        self.accept('p',self.pause_menu)
        self.accept('m',playr.toggle_background_music)
        self.accept('n',playr.toggle_sound_effects)
        self.accept('space',playr.jump)
        self.accept('tab',playr.hud.show_scores)
        self.accept('tab-up',playr.hud.hide_scores)
        
        # networked events
        self.accept('mouse1',playr.click)
        self.accept('mouse1-up',playr.clickRelease)
        self.accept('mouse3', playr.scopeZoomOn)
        self.accept('mouse3-up', playr.scopeZoomOff)
        self.accept('e',playr.collectOn)
        self.accept('e-repeat',playr.collectOn)
        self.accept('e-up',playr.collectOff)
        
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
            self.player.hud.display_gray("Process Stopped.")
            #stop handling key/mouse events, etc.
            self.wp.setCursorHidden(False)
            self.player.handleEvents = False
            base.win.requestProperties(self.wp)
            print "Time out! Come on guys, please?!"
        else:
            #start handling key/mouse events, etc.
            self.wp.setCursorHidden(True)
            self.wp.setMouseMode(WindowProperties.MRelative)
            base.win.requestProperties(self.wp)
            base.win.movePointer(0, base.win.getXSize()/2, base.win.getYSize()/2)
            self.player.handleEvents = True
            self.player.hud.destroy_gray()
            self.player.sendUpdate()
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
            self.pusherHandler.addCollider(d.pusher, d.parent)
        for p in game.programs.itervalues():
            base.cTrav.addCollider(p.pusher, self.pusherHandler)
            self.pusherHandler.addCollider(p.pusher, p.model)
        
        drones = game.drones.keys()
        progs  = game.programs.keys()
        #walls = game.walls.keys()
            
        for t in game.players.iterkeys():
            for p in progs:
                self.accept("%s-into-%s_donthitthis"%(t,p),  self.tronHitsProg)
                self.accept("%s-out-%s_donthitthis"%(t,p), self.tronOutProg)
            for d in drones:
                self.accept("%s-into-%sdonthitthis"%(t,d),  self.tronHitsDrone)
                self.accept("%s-out-%sdonthitthis"%(t,d),self.tronOutDrone)
            #for w in walls:
            #    self.accept("%s_wall-into-%s"%(t,w),  self.tronHitsWall)
            #    self.accept("%s_wall-repeat-%s"%(t,w),  self.tronHitsWall)
            #self.accept("%s_wall-into-%s"%(t,"tower_base"),  self.tronHitsWall)
            #self.accept("%s_wall-repeat-%s"%(t,"tower_base"),  self.tronHitsWall)
    
    def addProgramHandler(self, p):
        base.cTrav.addCollider(p.pusher, self.pusherHandler)
        self.pusherHandler.addCollider(p.pusher, p.model)
        for t in self.game.players.iterkeys():
            self.accept("%s-into-%s_donthitthis"%(t,p.unique_str()),  self.tronHitsProg)
            self.accept("%s-out-%s_donthitthis"%(t,p.unique_str()), self.tronOutProg)
    
    def addDroneHandler(self, d):
        base.cTrav.addCollider(d.pusher,self.pusherHandler)
        self.pusherHandler.addCollider(d.pusher, d.parent)
        dName = str(hash(d))
        for t in self.game.players.iterkeys():
            self.accept("%s-into-%sdonthitthis"%(t,dName),  self.tronHitsDrone)
            self.accept("%s-out-%sdonthitthis"%(t,dName),self.tronOutDrone)
    
    def addPlayerHandler(self, t):
        base.cTrav.addCollider(t.collider,self.collisionHandler)
        base.cTrav.addCollider(t.pusher,self.pusherHandler)
        self.pusherHandler.addCollider(t.pusher, t.tron)
        drones = self.game.drones.keys()
        progs  = self.game.programs.keys()
        tName = t.name
        for p in progs:
            self.accept("%s-into-%s_donthitthis"%(tName,p),  self.tronHitsProg)
            self.accept("%s-out-%s_donthitthis"%(tName,p), self.tronOutProg)
        for d in drones:
            self.accept("%s-into-%sdonthitthis"%(tName,d),  self.tronHitsDrone)
            self.accept("%s-out-%sdonthitthis"%(tName,d),self.tronOutDrone)
        t.initialize_camera()
    
    def tronHitsDrone(self,entry):
        tn,dn = entry.getFromNodePath().getName(),entry.getIntoNodePath().getName()
        dn = dn.rstrip("donthitthis")
        try:
            drone,tron = self.game.drones[dn], self.game.players[tn]
        except KeyError: return
        drone.canHitPlayer(tron, True)
        
    def tronOutDrone(self, entry):
        tn,dn = entry.getFromNodePath().getName(),entry.getIntoNodePath().getName()
        dn = dn.rstrip("donthitthis")
        try:
            drone,tron = self.game.drones[dn], self.game.players[tn]
        except KeyError: return
        drone.canHitPlayer(tron, False)
        
    def tronHitsProg(self,entry):
        tn,pn = entry.getFromNodePath().getName(),entry.getIntoNodePath().getName()
        pn = pn.rstrip("_donthitthis")
        if pn in self.game.programs.keys():
            tron,prog = self.game.players[tn], self.game.programs[pn]
            #tron.collect(prog)
            tron.canCollect = prog
            prog.show_desc()
            
    def tronOutProg(self,entry):
        tn,pn = entry.getFromNodePath().getName(),entry.getIntoNodePath().getName()
        pn = pn.rstrip("_donthitthis")
        if pn in self.game.programs.keys():
            tron,prog = self.game.players[tn], self.game.programs[pn]
            tron.canCollect = None
            prog.hide_desc()
