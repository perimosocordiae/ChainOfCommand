from time import time
from os import listdir
from os.path import splitext
from random import seed
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
from networking import Client
from constants import *
from level import *

class Game(object):

    def __init__(self,ip,port_num,shell,tile_size=100, tower_size=16, gameLength=180):
        self.shell = shell
        self.players, self.programs,self.drones,self.obstacles,self.startPoints = {},{},{},{},{}
        self.tile_size, self.tower_size, self.gameLength = tile_size, tower_size, gameLength
        self.type_idx = 0 # index into GAME_TYPES, can be changed from the staging shell
        
        #The size of a cube
        num_tiles = 3
        self.map_size = (self.tile_size * num_tiles) / 8.0
        self.end_sequence = None
        self.client = Client(ip,port_num)
        self.load_models()
    
    def rest_of_init(self):
        base.cTrav = CollisionTraverser()
        base.cTrav.setRespectPrevTransform(True)
        base.disableMouse()
        self.network_listener = Sequence(Wait(SERVER_TICK), Func(self.network_listen))
        self.startTime = time()
        self.endTime = self.startTime + self.gameLength
        self.gameTime = self.endTime - time()
        self.font = loader.loadFont('%s/FreeMono.ttf'%MODEL_PATH)
        [self.add_player(pname,i) for pname,i in self.players.iteritems() if pname != self.shell.name]
        self.add_local_player(self.players[self.shell.name]) # yay python and loose typing
        self.add_event_handler()
        self.load_env()        
        #Some player stuff just shouldn't be done until we have a world
        for pname in self.players:
            self.players[pname].post_environment_init()
        self.drone_adder = Sequence(Wait(5.0), Func(self.add_drone))
        print "game initialized, synchronizing"
        self.client.send("ready")
        
    def rest_of_rest_of_init(self):
        print "starting for real"
        for pname in self.players:
            self.players[pname].handleEvents = True
        self.local_player().sendUpdate()
        self.shell.output.setText("\n"*24)
        self.shell.hide_shell()
        self.network_listener.loop()
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
            
    def add_local_player(self,col_idx):
        print "making local player:",self.shell.name
        col_str = TEAM_COLORS.keys()[col_idx]
        self.players[self.shell.name] = LocalPlayer(self,self.shell.name,None,col_str)
        self.players[self.shell.name].shoot(False)
            
    def add_player(self,pname,col_idx):
        print "making player: %s"%pname
        col_str = TEAM_COLORS.keys()[col_idx]
        self.players[pname] = Player(self,pname,None,col_str)
        
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
        
        # simply change the level based on game type, for now
        if GAME_TYPES[self.type_idx][0] == 'deathmatch':
            self.level = CubeLevel(self, self.environ)
        elif GAME_TYPES[self.type_idx][0] == 'team deathmatch':
            self.level = SniperLevel(self, self.environ)
        else:
            self.level = Beaumont(self, self.environ)

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
                if ds[1] not in self.players:
                    self.players[ds[1]] = 0 # default color index == blue?
                    self.shell.refresh_staging()
            elif ds[0] == 'staging':
                assert ds[1] in self.players
                assert len(ds) == 4
                if ds[2] == 'color':
                    print ds[1],' (should be) changing color:',ds[3]
                    if ds[3] == '+':
                        i = self.players[ds[1]]+1
                        self.players[ds[1]] = i if i < len(TEAM_COLORS) else 0
                    else:
                        i = self.players[ds[1]]-1
                        self.players[ds[1]] = i if i >= 0 else len(TEAM_COLORS)-1
                elif ds[2] == 'type':
                    if ds[3] == '+':
                        i = self.type_idx+1
                        self.type_idx = i if i < len(GAME_TYPES) else 0
                    else:
                        i = self.type_idx-1
                        self.type_idx = i if i >= 0 else len(GAME_TYPES)-1
                self.shell.refresh_staging()
            elif ds[0] == 'start':
                print "handshake over, starting game"
                # don't add yourself
                Sequence(Func(self.shell.finish_staging), Wait(0.05), Func(self.rest_of_init),
                         Func(self.shell.show_sync)).start()
            elif ds[0] == 'go':
                self.rest_of_rest_of_init()
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

