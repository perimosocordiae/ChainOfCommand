from time import time
from os import listdir
from os.path import splitext
from random import seed
import direct.directbase.DirectStart
from eventHandler import GameEventHandler
from pandac.PandaModules import CollisionTraverser, CollisionTube, BitMask32
from pandac.PandaModules import CollisionNode, CollisionPolygon, CollisionPlane, Plane
from pandac.PandaModules import Vec4, Vec3, Point3, VBase3, TextureStage, TextNode
from direct.gui.OnscreenText import OnscreenText
from direct.task import Task
from direct.interval.IntervalGlobal import Parallel, Func, Sequence, Wait
from direct.showbase.InputStateGlobal import inputState
from player import Player,LocalPlayer
from drone import Drone
from mode import CaptureTheFlag,Deathmatch,ForTheHoard,Pwnage,Tutorial
from constants import *

class Game(object):

    def __init__(self,client,shell,tile_size=100):
        self.shell, self.tile_size = shell, tile_size
        self.players, self.programs,self.drones = {},{},{}
        self.modes = [Deathmatch(self,False,False),Deathmatch(self,False,True),
                           Deathmatch(self,True,False), Deathmatch(self,True,True),
                           CaptureTheFlag(self), ForTheHoard(self),Pwnage(self),Tutorial(self)]
        self.mode_idx = 2 # index into game_modes, can be changed from the staging shell
        
        #The size of a cube
        num_tiles = 3
        self.map_size = (self.tile_size * num_tiles) / 8.0
        self.end_sequence = None
        self.client = client
        self.load_models()
        self.had_locate = False # used by Locate to figure out whether to add "Right click to scope"
        self.drone_spawner = False # indicates if I'm the assigned drone spawner
    
    def rest_of_init(self):
        base.cTrav = CollisionTraverser()
        base.cTrav.setRespectPrevTransform(True)
        base.disableMouse()
        self.mode = self.modes[self.mode_idx]
        delattr(self,'modes')
        delattr(self,'mode_idx')
        self.network_listener = Sequence(Wait(SERVER_TICK), Func(self.network_listen))
        [self.add_player(pname,i) for pname,i in self.players.iteritems() if pname != self.shell.name]
        self.add_local_player(self.players[self.shell.name]) # yay python and loose typing
        self.add_event_handler()
        self.load_env()
        #Some player stuff just shouldn't be done until we have a world
        for pname in self.players:
            self.players[pname].post_environment_init()
        self.mode.post_environment_init()
        print "game initialized, synchronizing"
        self.client.send("ready")
        
    def synced_init(self):
        print "starting for real"
        for pname in self.players:
            self.players[pname].handleEvents = True
        self.local_player().sendUpdate()
        self.shell.output.setText("\n"*24)
        self.shell.hide_shell()
        self.network_listener.loop()
        if self.drone_spawner: 
            self.mode.start_drones()
        self.local_player().add_background_music()
        if self.mode.gameLength > 0:
            self.startTime = time()
            self.endTime = self.startTime + self.mode.gameLength
            self.local_player().hud.start_timer()
        
    def load_models(self): # asynchronous
        LocalPlayer.setup_sounds() # sound effects and background music
        # just load all the eggs in the MODEL_PATH
        models = filter(lambda p: splitext(p)[-1] == '.bam', listdir(MODEL_PATH))
        print "loading models now:",models
        loader.loadModel(map(lambda p: "%s/%s"%(MODEL_PATH,p), models), callback=self.load_callback)
    
    def load_callback(self, models):
        print "models loaded, starting handshake"
        taskMgr.add(self.handshakeTask, 'handshakeTask')
        self.shell.load_finished()
    
    def get_mode(self):
        if hasattr(self,'mode'):
            return self.mode
        return self.modes[self.mode_idx]
    
    def point_for(self, color):
        return self.mode.level.point_for(color)

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
    
    def add_point_for(self, color):
        for p in self.players.itervalues():
            if p.color == color:
                p.add_point()
    
    def readd_program(self,prog):
        self.programs[prog.unique_str()] = prog
        self.eventHandle.addProgramHandler(self.programs[prog.unique_str()])
        
    def send_drone_signal(self):
        dronePos = self.point_for("white")
        self.client.send("AddaDrone: %s"%dronePos)
    
    def add_drone(self, pos, speed=10):
        print "Adding a drone at position",pos
        d = Drone(self, speed=speed, pos=pos)
        self.drones[d.name] = d 
        self.eventHandle.addDroneHandler(d)
    
    def load_env(self):
        self.environ = render.attachNewNode("Environment Scale")
        self.environ.reparentTo(render)
        self.environ.setScale(self.tile_size, self.tile_size, self.tile_size)
        self.environ.setPos(0, 0, 0)
        self.mode.load_level(self.environ) # simply change the level based on game type, for now

    def game_over(self):
        print "Game over"
        p = self.local_player()
        p.hide()
        p.handleEvents = False
        p.invincible = True
        p.hud.display_gray("Process Terminated.")
        p.hud.show_scores()
        taskMgr.remove('timerTask')
        taskMgr.remove('updateGodModeTask')
        taskMgr.remove('stopGodModeTask')
        if not self.end_sequence:
            winning_score = max(p.score() for p in self.players.itervalues())
            stats = [(p.name, p.score()==winning_score, p.stats) for p in self.players.itervalues()]
            self.end_sequence = Sequence(Wait(5),
                     Func(self.kill_everything),
                     Func(self.shell.resume_shell,stats))
            self.end_sequence.start()
    
    def kill_everything(self):
        base.enableMusic(False)
        base.enableSoundEffects(False)
        self.network_listener.finish()
        self.eventHandle.ignoreAll()
        self.local_player().eventHandle.ignoreAll()
        for t in self.local_player().input_tokens:
            t.release()
        self.mode.destroy()
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
        self.client.close_connection()
        base.enableMouse()
        base.cTrav = None
    
    def send_type_change(self, change):
        self.client.send('staging %s type %d'%(self.shell.name, (self.mode_idx+change) % len(self.modes)))
    
    def send_color_change(self, change):
        self.client.send('staging %s color %d'%(self.shell.name, (self.players[self.shell.name]+change) % len(TEAM_COLORS)))
    
    def handshakeTask(self,task):
        data = self.client.getData()
        if len(data) == 0: return task.cont
        tempData = list()
        for d in data:
            tempData.append(d[0])
        print "handshake:",tempData
        for d in tempData:
            ds = d.split()
            if ds[0] == 'seed':
                self.rand_seed = int(ds[1])
                seed(self.rand_seed)
            elif ds[0] == 'append_name':
                assert len(ds) == 2
                self.shell.name += ds[1]
            elif ds[0] == 'DroneSpawner':
                self.drone_spawner = True
            elif ds[0] == 'player':
                if ds[1] not in self.players:
                    self.players[ds[1]] = 0 # default color index == blue?
                    self.shell.refresh_staging()
            elif ds[0] == 'unreg':
                if ds[1] in self.players:
                    del self.players[ds[1]]
                    if ds[1] == self.shell.name:
                        self.client.close_connection()
                        return task.done
                    else:
                        self.shell.refresh_staging()
            elif ds[0] == 'staging':
                if ds[1] not in self.players : continue
                assert len(ds) == 4
                if ds[2] == 'color':
                    self.players[ds[1]] = int(ds[3])
                elif ds[2] == 'type':
                    self.mode_idx = int(ds[3])
                self.shell.refresh_staging()
            elif ds[0] == 'echo':
                assert len(ds) == 2
                if ds[1] == 'lobbyinfo' :
                    self.send_color_change(0)
                elif ds[1] == 'gametype' :
                    self.send_type_change(0)
            elif ds[0] == 'start':
                print "handshake over, starting game"
                Sequence(Func(self.shell.finish_staging), Wait(0.05), Func(self.rest_of_init),
                         Func(self.shell.show_sync)).start()
            elif ds[0] == 'go':
                self.synced_init()
                return task.done # ends task
        return task.cont
    
    def network_listen(self):
        if taskMgr.hasTaskNamed("handshakeTask"): return
        data = self.client.getData()
        if len(data) == 0: return
        for d in data:
            ds = d[0].split(':')
            if len(ds) >= 2 and ds[0] == "AddaDrone":
                self.add_drone(eval(ds[1]))
                continue
            if len(ds) != 12: continue # maybe we should not silently ignore this?
            name,strs = ds[0],ds[1:]
            pos,rot,vel,hpr,anim,firing,collecting,dropping,warping,damage,damager = map(eval,strs)
            if name in self.players:
                self.players[name].move(pos,rot,vel,hpr,anim,firing,collecting,
                                        dropping,warping,damage,damager)
        for drone in self.drones.values():
            drone.act()
        base.cTrav.traverse(render)
        
    def make_tile(self, parent,fname,pos,hpr, scale=1.0):
        tile = loader.loadModel("%s/white_floor.bam"%MODEL_PATH)
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