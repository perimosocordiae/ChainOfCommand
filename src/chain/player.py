from math import sin, cos, radians,  pi, sqrt
from direct.task import Task
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import (Shader, CollisionNode, CollisionRay, CollisionSphere,
    CollisionHandlerQueue, TransparencyAttrib, BitMask32, Vec2, Vec3, Point3, VBase3, TextureStage, NodePath)
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.InputStateGlobal import inputState
from itertools import ifilter
from eventHandler import PlayerEventHandler
from projectile import Laser
from agent import Agent
from hud import HUD
from constants import *

#Constants
BASE_CAMERA_Y = -4.0
BASE_CAMERA_FOCAL_LENGTH = 1.39951908588
HIDE_DIST = 10
MOTION_MULTIPLIER = 180.0
TURN_MULTIPLIER = 0.08
LOOK_MULTIPLIER = 0.08
MAX_TURN = 1.5
MAX_LOOK = 1.5
JUMP_SPEED = 180.0 #make sure this stays less than SAFE_FALL - he should be able to jump up & down w/o getting hurt!
TRON_ORIGIN_HEIGHT = 6.5
LASER_SPEED = 5000
BASE_DAMAGE = 10 #arbitrary

class Player(Agent):
    def __init__(self, game, name, startPos, color):
        super(Player, self).__init__(game, name)
        self.setup_color(color)
        self.programs = [None, None, None]
        self.stats = {'damage_taken': 0, 'deaths': 0, 'pickups':0, 'drops':0}
        self.laserGlow = False
        self.setup_camera()
        self.setup_collider()
        self.laserSound = base.sfxManagerList[0].getSound(SOUND_PATH + "/hilas.mp3")
        #add the camera collider:
        self.collisionQueue = CollisionHandlerQueue()
        self.invincible = False
        self.handleEvents = False
        #self.spawn(startPos, False)
    
    def post_environment_init(self):
        self.spawn(None, False)
        
    def setup_color(self,col_str):
        self.color = col_str
        ts = TextureStage('ts')
        tex = loader.loadTexture("%s/tron-color_%s.png"%(COLOR_PATH,self.color))
        ts.setMode(TextureStage.MModulate)
        self.tron.setTexture(ts, tex)
    
    def setup_collider(self):
        self.collider = self.attach_collision_node(self.name, CollisionSphere(0, 0, 0, 10), DRONE_COLLIDER_MASK)
        self.pusher = self.attach_collision_node("%s_wall_donthitthis" % self.name, CollisionSphere(0, 0, 0, 12), WALL_COLLIDER_MASK)
        #self.pusher.show()
    
    def get_text_pos(self):
        return (0,0,12)
    
    def get_text_scale(self):
        return 1.5
    
    def set_glow(self, glow):
        if glow:
            self.tron.setTexture(self.ts, self.glow)
        else:
            self.tron.clearTexture(self.ts)
    
    def get_shield_sphere(self):
        return self.collider
    
    def get_model(self):
        return self.tron
    
    def findCrosshairHit(self):
        base.cTrav.traverse(render)
        if self.collisionQueue.getNumEntries() == 0: return "",""
        # This is so we get the closest object
        self.collisionQueue.sortEntries()
        for i in range(self.collisionQueue.getNumEntries()):
            pickedObj = self.collisionQueue.getEntry(i).getIntoNodePath().getName()
            pickedSpot = self.collisionQueue.getEntry(i).getSurfacePoint(render)
            if 'donthitthis' in pickedObj: continue
            #if '_wall' in pickedObj: continue
            if '_pusher' in pickedObj: continue
            if pickedObj != self.name and pickedObj != "%s_wall_donthitthis"%self.name: break
        return pickedObj, pickedSpot
    
    def set_laser_glow(self, glow):
        self.laserGlow = glow
    
    def show(self):
        self.tron.show()
        
    def hide(self):
        self.tron.hide()
    
    def die(self):
        self.hide()
        self.handleEvents = False
        for i in range(len(self.programs)):
            if self.programs[i]:
                self.drop(i)
                break
        self.stats['deaths'] += 1
        print "%s died!"%self.name
        self.respawn()
        
    def spawn(self,pt=None,_=None):
        if not self.tron.isEmpty(): # and self.game.gameTime > 0
            self.show()
            self.handleEvents = True
            self.health = STARTING_HEALTH
            if pt == None : pt = self.game.point_for(self.color)
            self.tron.setPos(pt[0],pt[1],pt[2] + TRON_ORIGIN_HEIGHT)

    def respawn(self):
        Sequence(Func(self.toggle_god),Wait(4.0), Func(self.spawn),Wait(1.0),
                 Func(self.toggle_god)).start()
    
    def toggle_god(self):
        self.invincible = not self.invincible
        print "Toggling God-mode"
    
    def get_base_damage(self):
        return BASE_DAMAGE
    
    def jump(self):
        if self.handleEvents: super(Player, self).jump() 
    
    def get_origin_height(self):
        return TRON_ORIGIN_HEIGHT
    
    def get_jump_speed(self):
        return JUMP_SPEED
        
    def StartMovingAnim(self):
        if self.running: return
        self.running = True
        self.shortRun.loop()
        
    def StopMovingAnim(self):
        if not self.running: return
        self.tron.stop()
        if self.shortRun.isPlaying():
            self.shortRun.start(startT=self.shortRun.getT())
        self.running = False
        
    def load_model(self):
        #glowShader=Shader.load("%s/glowShader.sha"%MODEL_PATH)
        self.tron = Actor.Actor("%s/tron.bam" % MODEL_PATH, {"running":"%s/tron_anim_updated.bam" % MODEL_PATH})
        self.tron.reparentTo(render)
        self.tron.setScale(0.4, 0.4, 0.4)
        self.tron.setHpr(0, 0, 0)
        #self.tron.setPos(-4, 34, TRON_ORIGIN_HEIGHT)
        self.tron.pose("running", 46)
        self.shortRun = self.tron.actorInterval("running", startFrame=25, endFrame=46)
        self.running = False
        
        self.ts = TextureStage('ts')
        self.ts.setMode(TextureStage.MGlow)
        self.glow = loader.loadTexture("%s/tron-glow_on.png"%TEXTURE_PATH)
        self.ts.setSort(9)
        self.set_glow(False)
    
    def get_camera(self):
        if self.camera == None:
            self.camera = self.tron.attachNewNode("Camera")
        return self.camera
    
    def setup_camera(self):
        # the camera follows tron
        self.camera = None
        self.get_camera().reparentTo(self.tron)
        self.get_camera().setPos(10.5, 40, TRON_ORIGIN_HEIGHT)
        self.get_camera().setHpr(180, 0, 0)
        
    def initialize_camera(self):
        cameraNode = CollisionNode('cameracnode_%s'%self.name)
        cameraNP = self.get_camera().attachNewNode(cameraNode)
        cameraNP.node().setIntoCollideMask(0)
        self.cameraRay = CollisionRay(0, self.get_camera().getY(), 0, 0, 1, 0)
        cameraNode.addSolid(self.cameraRay)
        base.cTrav.addCollider(cameraNP, self.collisionQueue)
        #set all parameters correctly now that everything is available
        self.setCameraDist(40)
    
    def switchPerspective(self):
        #Switch between 3 perspectives
        if not self.handleEvents: return
        if self.get_camera().getY() > 60:
            self.setCameraDist(BASE_CAMERA_Y)
        elif self.get_camera().getY() > 20:
            self.setCameraDist(100)
        else:
            self.setCameraDist(40)
    
    def zoomIn(self):
        if not self.handleEvents: return
        if self.get_camera().getY() > BASE_CAMERA_Y:
            self.setCameraDist(self.get_camera().getY() - 2)
            
    def zoomOut(self):
        if not self.handleEvents: return
        if self.get_camera().getY() < 100:
            self.setCameraDist(self.get_camera().getY() + 2)
    
    def setCameraDist(self, dist):
        #use 'zeroed' to account for the negative first-person y value
        zeroed = dist - BASE_CAMERA_Y
        if dist > HIDE_DIST:
            self.get_camera().setPos(min(-sqrt(zeroed), -5), dist, 5 + (zeroed / 102) * TRON_ORIGIN_HEIGHT)
        else:
            self.get_camera().setPos(-max(dist/2,0), dist, 5 + (zeroed / 102) * TRON_ORIGIN_HEIGHT)
        self.cameraRay.setOrigin(Point3(0, 1 + self.get_camera().getY() / self.get_camera().getSy(), 0))
    
    def shoot(self, playSound=True):
        if not self.handleEvents: return
        #first get a ray coming from the camera and see what it first collides with
        objHit,spotHit = self.findCrosshairHit()
        if objHit in self.game.drones:
            d = self.game.drones[objHit]
            if not d.is_dead():
                d.hit(self.damage(),self.name)
                print "hit drone %s for %d damage" % (objHit, self.damage() / d.shield())
                if d.is_dead():
                    print "killed it!"
                    self.add_kill(d)
        elif objHit in self.game.programs:
            p = self.game.programs[objHit]
            if not p.is_dead():
                p.hit(self.damage(),self.name)
                print "hit program %s for %d damage" % (objHit, self.damage() / p.shield())
                if p.is_dead():
                    print "Oh no, you blew up a program!"
                    self.add_kill(p)
        elif objHit in self.game.players:
            p = self.game.players[objHit]
            #for friendly fire, use this instead of the if below:
            #if not (p.is_dead() or p.color == self.color)
            if not p.is_dead(): 
                p.hit(self.damage(),self.name)
                print "hit %s for %d damage" % (objHit, self.damage() / p.shield())
                if p.is_dead():
                    print "you killed %s!"%objHit
                    self.add_kill(p)
        #end if 
        self.fire_laser(objHit,spotHit,playSound)
    
    def add_kill(self, objKilled):
        key = objKilled.__class__.__name__+'_kill'
        if not key in self.stats:
            self.stats[key] = 1
            self.add_point()
        else:
            self.stats[key] += 1
            self.add_point()
        if self.score() >= self.game.fragLimit:
            self.game.game_over()
    
    def add_point(self):
        #do nothing in base class - this does HUD stuff
        pass
    
    def score(self):
        if self.game.type_idx < 2: # non-team matches
            return self.stats.get('LocalPlayer_kill',0)+self.stats.get('Player_kill',0)+self.stats.get('Drone_kill',0)
        if self.game.type_idx == 4: # ctf
            try:
                return self.game.ctf_scores[self.color]
            except: return 0
        # team matches
        return sum(p.stats.get('LocalPlayer_kill',0)+p.stats.get('Player_kill',0) for p in self.game.my_team())
    
    def hit(self, amt=0, hitter=None):
        pass
    
    def show_debug_hint(self):
        return
    
    def drop(self, i):
        succ=super(Player, self).drop(i)
        if succ: self.stats['drops'] += 1
        return succ
    
    def collect(self):
        succ=super(Player, self).collect()
        if succ[1]: self.stats['pickups'] += 1
        return succ
        
    def fire_laser(self, objHit, spotHit, playSound):
        startPos = self.tron.getPos()
        laser = Laser()
        laser.set_pos(startPos)
        laser.model.setScale(16.0)
        laser.model.setHpr(self.tron.getHpr())
        laser.model.setH(laser.model.getH())
        laser.model.setP(-self.get_camera().getP())
        h, p = radians(self.tron.getH()), radians(self.get_camera().getP())
        pcos = cos(p)
        if self.laserGlow:
            laser.set_glow(True)
        #the .005 is a fudge factor - it just makes things work better
        laser.fire(Vec3(sin(h) * pcos, -cos(h) * pcos, sin(p) + 0.005) * LASER_SPEED)
        distanceToCamera = ((startPos - self.game.local_player().tron.getPos()).length()-2)/180.0
        if playSound:
            if distanceToCamera <= 1 :
                self.laserSound.setVolume(0.3)
            else :
                self.laserSound.setVolume(0.3/pow(distanceToCamera, 2))
            self.laserSound.play()
    
    def move_to(self,pos,rot,vel,hpr,damage,damager):
        self.tron.setFluidPos(pos)
        self.tron.setH(rot.getX())
        self.get_camera().setP(rot.getY())
        if damage > 0:
            super(Player,self).hit(damage,damager)
        self.stats['damage_taken'] += damage
        if self.is_dead() and damager in self.game.players:
            self.game.players[damager].add_kill(self)
                
    
    def move(self,pos,rot,vel,hpr,anim,firing,collecting,dropping,damage,damager):
        self.move_to(pos,rot,vel,hpr,damage,damager)
        #print hpr
        if anim == 'start':  self.StartMovingAnim()
        elif anim == 'stop': self.StopMovingAnim()
        if collecting:
            self.collect()
        if firing:
            self.shoot()
        if dropping > -1:
            self.drop(dropping)
        self.do_debug()

class LocalPlayer(Player):
    def __init__(self, game, name, startPos, color):
        super(LocalPlayer, self).__init__(game, name, startPos, color)
        self.hpr = VBase3(0,0,0)
        self.collecting = False
        self.shooting = False
        self.scopeZoomed = False
        self.dropping = -1
        self.hud = HUD(self)
        self.current_damage_taken = 0
        self.damager = None
        #self.setup_shooting()
        self.eventHandle = PlayerEventHandler(self)
        self.debug_hint = None
        #self.game.network_listener.loop()
    
    def move(self,pos,rot,vel,hpr,anim,firing,collecting,dropping,damage,damager):
        super(LocalPlayer,self).move(pos,rot,vel,hpr,anim,firing,collecting,dropping,damage,damager)
        newP = self.get_camera().getP() + hpr.getY() 
        newP = max(min(newP, 80), -80)
        self.get_camera().setP(newP)
        self.sendUpdate()
        #self.shooting = False
        base.win.movePointer(0, base.win.getXSize() / 2, base.win.getYSize() / 2)
        if dropping > -1:
            #we dropped it - now we're not dropping anything
            self.dropping = -1
    
    def move_to(self,pos,rot,vel,hpr,damage,damager):
        self.tron.setFluidPos(self.tron.getPos() + (vel * SERVER_TICK))
        self.tron.setH(self.tron.getH() + hpr.getX())
        
    def initialize_camera(self):
        super(LocalPlayer,self).initialize_camera()
        #base.camLens.setNearFar(10, 3000)
    
    def get_camera(self):
        return base.camera
    
    def get_camera_lens(self):
        return base.camLens
    
    def setCameraDist(self, dist):
        super(LocalPlayer,self).setCameraDist(dist)
        if dist <= HIDE_DIST:
            self.hide()
        else:
            self.show()
    
    def show(self):
        if self.get_camera().getY() > HIDE_DIST and self.tron.isHidden():
            self.tron.show()
    
    def hide(self):
        if (self.get_camera().getY() <= HIDE_DIST or self.is_dead()) and not self.tron.isHidden():
            self.tron.hide()
        
    def die(self):
        super(LocalPlayer,self).die()
        if hasattr(self, "hud") and self.hud:
            self.hud.display_gray()
            self.hud.show_scores()
    
    def respawn(self):
        print "respawning"
        Sequence(Func(self.toggle_god),Wait(4.0), Func(self.spawn), Wait(1.0),
                 Func(self.hud.hide_scores), Func(self.hud.destroy_gray), Func(self.toggle_god)).start()
    
    def spawn(self,startPos=None,update=True):
        super(LocalPlayer,self).spawn(startPos)
        if hasattr(self, "hud") and self.hud:
            self.hud.heal()
        if update:
            self.sendUpdate()

    @staticmethod
    def setup_sounds():
        keys = ['laser', 'yes', 'grunt']
        fnames = ["%s/hilas.mp3", "%s/Collect_success.mp3", "%s/Grunt.wav"]
        LocalPlayer.sounds = dict(zip(keys, [base.sfxManagerList[0].getSound(f % SOUND_PATH) for f in fnames]))
        for s in LocalPlayer.sounds.itervalues():
            s.setVolume(0.3)
        LocalPlayer.backgroundMusic = base.musicManager.getSound("%s/City_in_Flight.mp3"%SOUND_PATH)
        base.enableMusic(True)
        base.enableSoundEffects(True)
            
    def add_background_music(self):
        # from http://www.newgrounds.com/audio/listen/287442
        LocalPlayer.backgroundMusic.setVolume(0.3)
        LocalPlayer.backgroundMusic.setTime(35)  # music automatically starts playing when this command is issued
        print "Track: City in Flight in Neon Light" # attribution
        print "Author: Trevor Dericks"
    
    def toggle_background_music(self):
        active = base.musicManager.getActive()
        base.enableMusic(not active)
        if active: LocalPlayer.backgroundMusic.setTime(35)
        self.hud.toggle_background_music()
        
    def toggle_sound_effects(self):
        base.enableSoundEffects(not base.sfxManagerList[0].getActive())
        self.hud.toggle_sound_effects()

    def click(self):
        #self.shoot()
        delay = self.rapid_fire()
        self.shooting = True
        taskMgr.doMethodLater(delay, self.updateShotTask, "updateShotTask")
        
    def clickRelease(self):
        self.shooting = False
        taskMgr.remove("updateShotTask")
    
    def add_radar(self):
        print "radar"
        if hasattr(self, "hud") and self.hud:
            self.hud.setup_radar()
        
    def remove_radar(self):
        print "radar remove"
        if hasattr(self, "hud") and self.hud:
            self.hud.destroy_radar()
        
    def radar_mod(self):
        d = 1
        for p in ifilter(lambda p: p != None, self.programs):
            d = p.radar_mod(d)
        return d
    
    def scopeZoomOn(self):
        d = BASE_CAMERA_FOCAL_LENGTH
        for p in ifilter(lambda p: p != None, self.programs):
            d = p.scope_zoom_mod(d)
        if d > BASE_CAMERA_FOCAL_LENGTH:
            self.get_camera_lens().setFocalLength(d)
            self.hud.scopeScreen.unstash()
    
    def scopeZoomOff(self):
        self.get_camera_lens().setFocalLength(BASE_CAMERA_FOCAL_LENGTH)
        if hasattr(self, "hud") and self.hud.scopeScreen:
            self.hud.scopeScreen.stash()
    
    def show_scopehairs(self):
        if hasattr(self, "hud") and self.hud.scopehairs:
            self.hud.scopehairs.unstash()
        
    def hide_scopehairs(self):
        if hasattr(self, "hud") and self.hud.scopehairs:
            self.hud.scopehairs.stash()
    
    def collectOn(self):
        self.collecting = True
        
    def collectOff(self):
        self.collecting = False
        
    def set_dropping(self, i):
        self.dropping = i
    
    def hit(self, amt=0, hitter=None):
        if self.invincible: return False
        if not super(Player, self).hit(amt,hitter): return
        self.damager = hitter
        self.stats['damage_taken'] += amt
        self.current_damage_taken += amt
        if LocalPlayer.sounds['grunt'].getTime() == 0.0 : LocalPlayer.sounds['grunt'].play()
        print "Hit"
        self.hud.hit()
    
    def heal(self, amt=0):
        super(LocalPlayer, self).heal(amt)
        self.hud.heal()
    
    def collect(self):
        #sound/message depends on status
        i, prog = super(LocalPlayer, self).collect()
        if prog:
            LocalPlayer.sounds['yes'].play()
            if i >= 0:
                self.hud.collect(i,prog.name)
    
    def drop(self, i):
        if (super(LocalPlayer, self).drop(i)):
            self.hud.drop(i)
        
    def add_slot(self):
        if len(self.programs) <= 5:
            self.programs.append(None)
            self.hud.add_slot()
        
    #def add_kill(self, objKilled):
    #    super(LocalPlayer, self).add_kill(objKilled)
    #    self.hud.add_kill()
        
    def add_point(self):
        self.hud.add_kill()
        
    def show_locate_hint(self):
        self.locate_hint = OnscreenText(text="Right click to scope", pos=(0,0.1), scale=0.06, fg=(0,0,0,0.8), bg=(1,1,1,0.8), font=self.hud.font)
        Sequence(Wait(3.0), Func(self.locate_hint.destroy)).start()
        self.game.had_locate = True
        
    def show_debug_hint(self):
        if self.debug_hint == None :
            self.debug_hint = OnscreenText(text="Already at full health", pos=(0,0.1), scale=0.06, fg=(0,0,0,0.8), bg=(1,1,1,0.8), font=self.hud.font)
            Sequence(Wait(3.0), Func(self.destroy_debug_hint)).start()
            
    def destroy_debug_hint(self):
        self.debug_hint.destroy()
        self.debug_hint = None
    
    def setup_camera(self):
        super(LocalPlayer,self).setup_camera()
        self.input_tokens = [inputState.watch('forward', 'w', 'w-up'),
                             inputState.watch('backward', 's', 's-up'),
                             inputState.watch('moveleft', 'a', 'a-up'),
                             inputState.watch('moveright', 'd', 'd-up')]
        taskMgr.add(self.updateCameraTask, "updateCameraTask")
    
    def updateShotTask(self, task):
        self.shooting = True
        return task.again
        
    #Task to move the camera
    def updateCameraTask(self, task):
        #print self.velocity * globalClock.getDt()
        #self.sendUpdate()
        return Task.cont
    
    def sendUpdate(self):
        if not self.handleEvents: return Task.cont
        self.hud.target()
        self.handleGravity()
        self.LookAtMouse()
        
        anim = '"a"' # placeholder
        if not self.in_air(): # no mid-air corrections!
            cmds = [ c for c in ['forward', 'backward', 'moveleft', 'moveright'] if inputState.isSet(c)]
            new_vel = self.get_xy_velocity(cmds)
            self.velocity.setX(new_vel.getX())
            self.velocity.setY(new_vel.getY())
            if not len(cmds)==0: anim = '"start"'
            else:                anim = '"stop"'
        pos = self.tron.getPos() + (self.velocity * SERVER_TICK)
        rot = Point3(self.tron.getH(), self.get_camera().getP(), 0)+self.hpr
        # send command to move tron, based on the values in self.velocity
        self.game.client.send(':'.join([self.name,str(pos),str(rot),str(self.velocity),str(self.hpr),anim,str(self.shooting),str(self.collecting),str(self.dropping),str(self.current_damage_taken),'"%s"'%self.damager]))
        self.shooting = False
        self.current_damage_taken = 0
        self.damager = None
    
    def get_xy_velocity(self, cmds):
        new_vel = Vec2(0, 0)
        for cmd in cmds:
            new_vel += self.get_partial_velocity(cmd)
        
        new_vel.normalize()
        new_vel *= MOTION_MULTIPLIER
        return new_vel
    
    def get_partial_velocity(self, dir):
        h = radians(self.tron.getH())
        if dir in ['moveleft', 'moveright']: h += pi / 2.0
        if dir in ['forward', 'moveleft']:
            return Vec2(sin(h), -cos(h))
        else:
            return Vec2(-sin(h), cos(h))
    
    def LookAtMouse(self):
        md = base.win.getPointer(0)
        x, y = md.getX(), md.getY()
        centerX = base.win.getXSize() / 2
        centerY = base.win.getYSize() / 2
        self.hpr.setX(-(TURN_MULTIPLIER * (x - centerX)))
        camP = base.camera.getP()
        newP = camP-(LOOK_MULTIPLIER * (y - centerY))
        #keep within +- 90 degrees
        newP = max(min(newP, 80), -80)
        self.hpr.setY(newP - camP)
        #make sure lifter continues to point straight down
        #angle = radians(self.tron.getP())
        #self.lifterRay.setDirection(Vec3(0,-sin(angle), -cos(angle)))
    
