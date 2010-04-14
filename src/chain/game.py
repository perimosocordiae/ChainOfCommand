from time import time
from os import listdir
from os.path import splitext
import sys
from random import randint, seed
import direct.directbase.DirectStart
from eventHandler import GameEventHandler
from pandac.PandaModules import CollisionTraverser, CollisionTube, BitMask32
from pandac.PandaModules import CollisionNode, CollisionPolygon, CollisionPlane, Plane
from pandac.PandaModules import Vec4, Vec3, Point3, VBase3, TextureStage
from direct.gui.OnscreenText import OnscreenText
from direct.task import Task
from direct.interval.IntervalGlobal import Parallel, Func, Sequence, Wait
from direct.showbase.InputStateGlobal import inputState
from player import Player,LocalPlayer
from drone import Drone
from obstacle import Wall, Tower, RAMSlot, CopperWire, QuadWall
from networking import Client
from program import DashR, Rm, Chmod, RAM, Gdb, Locate, Ls
from constants import *
from level import *

class Game(object):

    def __init__(self,ip,port_num,shell,tile_size=100, tower_size=16, gameLength=180):
        self.shell = shell
        self.players, self.programs,self.drones,self.obstacles,self.startPoints = {},{},{},{},{}
        self.tile_size, self.tower_size, self.gameLength = tile_size, tower_size, gameLength
        self.type = 'deathmatch' # just a default value, can be changed from the staging shell
        
        #The size of a cube
        num_tiles = 3
        self.map_size = (self.tile_size * num_tiles) / 8.0
        self.player_set = set()
        self.end_sequence = None
        self.client = Client(ip,port_num)
        self.load_models()
    
    def rest_of_init(self):
        base.cTrav = CollisionTraverser()
        base.cTrav.setRespectPrevTransform(True)
        base.disableMouse()
        self.startTime = time()
        self.endTime = self.startTime + self.gameLength
        self.gameTime = self.endTime - time()
        self.font = loader.loadFont('%s/FreeMono.ttf'%MODEL_PATH)
        for pname in self.players:
            self.add_player(pname)
        self.network_listener = Sequence(Wait(SERVER_TICK), Func(self.network_listen))
        self.add_local_player()
        self.add_event_handler()
        self.load_env()
        
        #Some player stuff just shouldn't be done until we have a world
        for pname in self.players:
            self.players[pname].post_environment_init()
        print "game initialized"
        self.shell.hide_shell()
        self.drone_adder = Sequence(Wait(5.0), Func(self.add_drone))
        self.drone_adder.loop()
        self.local_player().add_background_music()
        self.startTime = time() # reset the start and end times
        self.endTime = self.startTime + self.gameLength
        self.local_player().hud.start_timer()
        
    def load_models(self): # asynchronous
        LocalPlayer.setup_sounds() # sound effects and background music
        # just load all the eggs in the MODEL_PATH
        models = filter(lambda p: splitext(p)[-1] == '.egg', listdir(MODEL_PATH))
        print "loading models now:",models
        loader.loadModel(map(lambda p: "%s/%s"%(MODEL_PATH,p), models), callback=self.load_callback)
    
    def load_callback(self, models):
        print "models loaded, starting handshake"
        taskMgr.add(self.handshakeTask, 'handshakeTask')
        self.shell.load_finished()
    
    def point_for(self, color):
        return self.level.point_for(color)

    def add_event_handler(self):
        self.eventHandle = GameEventHandler(self)
        for player in self.players.itervalues():
            self.eventHandle.addPlayerHandler(player)
            player.initialize_camera()
            
    def add_local_player(self):
        print "adding local player:",self.shell.name
        self.players[self.shell.name] = LocalPlayer(self,self.shell.name,None,"blue")
        self.players[self.shell.name].shoot(False)
            
    def add_player(self,pname):
        print "making player: %s"%pname
        self.players[pname] = Player(self,pname,None,"blue")
        
    def readd_program(self,prog):
        self.programs[prog.unique_str()] = prog
        self.eventHandle.addProgramHandler(self.programs[prog.unique_str()])
    
    def add_drone(self):
        d = Drone(self)
        self.drones[str(hash(d))] = d 
        self.eventHandle.addDroneHandler(d)
    
    def load_env(self):
        self.environ = render.attachNewNode("Environment Scale")
        self.environ.reparentTo(render)
        self.environ.setScale(self.tile_size, self.tile_size, self.tile_size)
        self.environ.setPos(0, 0, 0)
        
        #self.level = CubeLevel(self, self.environ)
        self.level = SniperLevel(self, self.environ)
        #self.level = Beaumont(self, self.environ)

    def game_over(self):
        print "Game over"
        p = self.local_player()
        p.hide()
        p.handleEvents = False
        p.invincible = True
        p.hud.display_gray()
        p.hud.show_scores()
        taskMgr.remove('timerTask')
        if not self.end_sequence:
            self.end_sequence = Sequence(Wait(5),
                     Func(self.kill_everything),
                     Func(self.shell.resume_shell,[(p.name,p.stats) for p in self.players.itervalues()]))
            self.end_sequence.start()
                
    def kill_everything(self):
        base.enableMusic(False)
        base.enableSoundEffects(False)
        self.network_listener.finish()
        self.drone_adder.finish()
        self.eventHandle.ignoreAll()
        self.local_player().eventHandle.ignoreAll()
        for t in self.local_player().input_tokens:
            t.release()
        self.local_player().get_camera().reparentTo(render)
        self.local_player().hud.destroy_HUD()
        for d in self.drones.values():
            d.die() # should we be del'ing the drones?
        for k in self.players.keys():
            self.players[k].tron.cleanup()
            self.players[k].tron.removeNode()
            del self.players[k]
        for k in self.programs.keys():
            self.programs[k].die()
            del self.programs[k]
        self.level.destroy()
            
        self.client.close_connection()
        base.enableMouse()
        base.cTrav = None
    
    def handshakeTask(self,task):
        data = self.client.getData()
        if len(data) == 0: return task.cont
        print "handshake:",data
        for d in data:
            ds = d.split()
            if ds[0] == 'seed':
                self.rand_seed = int(ds[1])
                seed(self.rand_seed)
            elif ds[0] == 'player':
                if ds[1] not in self.player_set:
                    self.player_set.add(ds[1])
                    self.shell.refresh_staging()
            elif ds[0] == 'staging':
                self.shell.refresh_staging()
            elif ds[0] == 'start':
                print "handshake over, starting game"
                for player in self.player_set:
                    if player != self.shell.name: # don't add yourself
                        self.players[player] = None
                Sequence(Func(self.shell.finish_staging), Wait(0.05), Func(self.rest_of_init)).start()
                return task.done # ends task
        return task.cont
    
    def network_listen(self):
        if taskMgr.hasTaskNamed("handshakeTask"): return
        data = self.client.getData()
        if len(data) == 0: return
        for d in data:
            ds = d.split(':')
            if len(ds) != 9: continue # maybe we should not silently ignore this?
            name,strs = ds[0],ds[1:]
            pos,rot,vel,hpr,anim,firing,collecting,dropping = map(eval,strs)
            if name in self.players:
                self.players[name].move(pos,rot,vel,hpr,anim,firing,collecting,dropping)
        for drone in self.drones.values():
            drone.act()
        base.cTrav.traverse(render)
        
    def make_tile(self, parent,fname,pos,hpr, scale=1.0):
        tile = loader.loadModel("%s/white_floor.egg"%MODEL_PATH)
        tile.reparentTo(parent)
        tile.setScale(scale, scale, scale)
        tile.setPos(pos)
        tile.setHpr(*hpr)
        ts = TextureStage('ts')
        tex = loader.loadTexture(fname)
        ts.setMode(TextureStage.MModulate)
        tile.setTexture(ts, tex)
    
    def local_player(self):
        return self.players[self.shell.name]

