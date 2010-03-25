from time import time, sleep
from platform import uname
import sys
from random import randint, choice, seed
#from itertools import product as iproduct
import direct.directbase.DirectStart
from eventHandler import GameEventHandler
from pandac.PandaModules import CollisionTraverser, CollisionTube, BitMask32
from pandac.PandaModules import CollisionNode, CollisionPolygon, CollisionPlane, Plane
from pandac.PandaModules import AmbientLight,DirectionalLight, Vec4, Vec3, Point3, VBase3
from direct.gui.OnscreenText import OnscreenText
from direct.task import Task
from direct.interval.IntervalGlobal import Parallel, Func, Sequence, Wait
from direct.showbase.InputStateGlobal import inputState
from player import Player,LocalPlayer
from drone import Drone
from wall import Wall,Tower
from networking import Client
from program import DashR, Rm, Chmod, RAM
from constants import *



class Game(object):

    def __init__(self,ip,port_num,shell,map_size=320,tile_size=16, tower_size=16, gameLength=180):
        self.shell = shell
        self.players, self.programs,self.drones,self.walls,self.towers = {},{},{},{},[]
        self.map_size,self.tile_size, self.tower_size, self.gameLength = map_size,tile_size, tower_size, gameLength
        self.client = Client(ip,port_num)
        self.load_models()
    
    def rest_of_init(self):
        base.cTrav = CollisionTraverser()
        base.cTrav.setRespectPrevTransform(True)
        #wsbase.cTrav.showCollisions(render)
        base.disableMouse()
        self.load_env()
        self.timer = OnscreenText(text="Time:", pos=(0,0.9), scale=(0.08), fg=(0,0,1,0.8), bg=(1,1,1,0.8), mayChange=True)
        self.startTime = time()
        self.endTime = self.startTime + self.gameLength
        self.gameTime = self.endTime - time()
        taskMgr.doMethodLater(0.01, self.timerTask, 'timerTask')
        self.font = loader.loadFont('%s/FreeMono.ttf'%MODEL_PATH)
        for pname in self.players:
            self.add_player(pname)
        self.network_listener = Sequence(Wait(SERVER_TICK), Func(self.network_listen))
        self.add_local_player()
        self.add_event_handler()
        print "game initialized"
        for _ in range(4):
            self.add_program(Rm)
            self.add_program(Chmod)
            self.add_program(DashR)
            self.add_program(RAM)
        print "programs added"
        self.shell.hide_shell()
        self.drone_adder = Sequence(Wait(5.0), Func(self.add_drone))
        self.drone_adder.loop()
        
    def load_models(self): # asynchronous
        LocalPlayer.setup_sounds() # sound effects and background music
        models = ["/blue_floor.egg","/green_floor.egg","/red_floor.egg","/yellow_floor.egg",
                  "/terminal_window_-r.egg","/terminal_window_chmod.egg","/terminal_window_rm.egg",
                  "/RAM.egg","/laser.egg","/tron_anim_updated.egg","/capacitor.egg"]
        print "loading models now"
        loader.loadModel(map(lambda p: MODEL_PATH + p, models), callback=self.load_callback)
    
    def load_callback(self, models):
        print "models loaded, starting handshake"
        taskMgr.add(self.handshakeTask, 'handshakeTask')
        self.shell.load_finished()
        
    def rand_point(self): # get a random point that's also a valid play location
        return (randint(-self.map_size + 1,self.map_size - 2),randint(-self.map_size + 1,self.map_size -2))

    def add_event_handler(self):
        self.eventHandle = GameEventHandler(self)
        for player in self.players.itervalues():
            self.eventHandle.addPlayerHandler(player)
            player.initialize_camera()
            
    def add_local_player(self):
        name = uname()[1]
        print "adding local player:",name
        self.players[name] = LocalPlayer(self,name)
            
    def add_player(self,pname):
        print "making player: %s"%pname
        self.players[pname] = Player(self,pname)
        
    def add_program(self,ptype):
        prog = ptype(self)
        self.readd_program(prog)
    
    def readd_program(self,prog):
        self.programs[prog.unique_str()] = prog
        self.eventHandle.addProgramHandler(self.programs[prog.unique_str()])
    
    def add_drone(self):
        d = Drone(self)
        self.drones[str(hash(d))] = d 
        self.eventHandle.addDroneHandler(d)
    
    def add_wall(self, name, parent, p1, p2, p3, p4):
        self.walls[name] = Wall(self, name, parent, p1, p2, p3, p4, WALL_COLLIDER_MASK)
        #self.eventHandle.addWallHandler(self.walls[name])

    def load_env(self):
        #Note: using glow slows down frame rate SIGNIFICANTLY... I don't know of a way around it either
        eggs = map(lambda s:"%s/%s_floor.egg"%(MODEL_PATH,s),['yellow','blue','green','red'])
        #num_tiles = self.map_size/self.tile_size
        num_tiles = 2
        self.tile_size = self.map_size / num_tiles
        colscale = 0.01
        #scale = colscale * self.tile_size
        #environ = loader.loadModel('%s/special_floor.egg'%MODEL_PATH)
        self.environ = render.attachNewNode("Environment Scale")
        self.environ.reparentTo(render)
        self.environ.setScale(self.tile_size, self.tile_size, self.tile_size)
        self.environ.setPos(0, 0, 0)
        
        center = num_tiles/2
        #wall_height = 10
        wall_height = num_tiles
        
        #for i,j in iproduct(range(num_tiles),repeat=2):
        for i in range(num_tiles):
          for j in range(num_tiles):
            egg = eggs[egg_index(i,j,center)]
            self.make_tile(self.environ,egg,(-2*(i-center) - 1,-2*(j-center) - 1, 2*wall_height), (0, 0, 180), colscale) #ceiling
            #if i == center and j == center: continue #bottom center is already done
            self.make_tile(self.environ,egg,(2*(i-center) + 1, 2*(j-center) + 1, 0),(0, 0, 0), colscale) #floor
        
        #for i,j in iproduct(range(num_tiles),range(wall_height)):
        for i in range(num_tiles):
          for j in range(wall_height):
            egg = eggs[egg_index(i,j,center)]
            #TODO: try removing these in kill_everything
            self.make_tile(self.environ,egg,(-2*center,    -2*(i-center)-1,  2*(wall_height-j)-1),(0, 0, 90), colscale)  #wall 1
            self.make_tile(self.environ,egg,(-2*(i-center)-1, -2*center,  2*(wall_height-j)-1),(0,-90,0), colscale)   #wall 2
            self.make_tile(self.environ,egg,( 2*center,     2*(i-center) + 1, 2*j+1),            (0, 0, -90), colscale) #wall 3
            self.make_tile(self.environ,egg,(-2*(i-center) - 1, 2*center,   2*j+1),            (0, 90,0), colscale)   #wall 4
        
        #add collision handlers for walls
        self.add_wall("wall1", self.environ,
                      Point3(-2*center, -2*center, 2*wall_height + 1),
                      Point3(-2*center, -2*center, 0),
                      Point3(-2*center, 2*center, 0),
                      Point3(-2*center, 2*center, 2*wall_height + 1))
        self.add_wall("wall2", self.environ,
                      Point3(2*center, 2*center, 2*wall_height + 1),
                      Point3(2*center, 2*center, 0),
                      Point3(2*center, -2*center, 0),
                      Point3(2*center, -2*center, 2*wall_height + 1))
        self.add_wall("wall3", self.environ,
                      Point3(-2*center, 2*center, 2*wall_height + 1),
                      Point3(-2*center, 2*center, 0),
                      Point3(2*center, 2*center, 0),
                      Point3(2*center, 2*center, 2*wall_height + 1))
        self.add_wall("wall4", self.environ,
                      Point3(2*center, -2*center, 2*wall_height + 1),
                      Point3(2*center, -2*center, 0),
                      Point3(-2*center, -2*center, 0),
                      Point3(-2*center, -2*center, 2*wall_height + 1))
        
        #The reason this is different is because walls have their own event collision
        #handler method... floors don't need one (so no need for a dictionary of them)
        self.floor = Wall(self, "floor", self.environ, Point3(-2*center, -2*center, 0),
                Point3(2*center, -2*center, 0), Point3(2*center, 2*center, 0),
                Point3(-2*center, 2*center, 0), FLOOR_COLLIDER_MASK)
        
        # make some random bunkers
        
        for _ in range(4):
            pos = self.rand_point()
            self.towers.append(Tower(render, pos[0], pos[1], 
                                     randint(2,2*wall_height*self.tower_size), 
                                     colscale,self.tile_size))
    
    def timerTask(self, task):
        self.gameTime = self.endTime - time()
        self.timer.setText("Time: %.2f seconds"%(self.gameTime))
        if 0 < self.gameTime < 10:
            self.timer.setFg((1,0,0,0.8))
        elif self.gameTime <= 0:
            print "Game over"
            p = self.local_player()
            p.tron.hide()
            p.handleEvents = False
            p.show_scores()
            Sequence(Wait(5),Func(self.kill_everything),
                     Func(self.shell.resume_shell)).start()
            return task.done
        return task.again
    
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
        self.local_player().destroy_HUD()
        self.timer.destroy()
        for d in self.drones.values():
            taskMgr.remove(d.walkTask)
            d.walk.finish()
            d.die()
        for k in self.players.keys():
            self.players[k].tron.cleanup()
            self.players[k].tron.removeNode()
            del self.players[k]
        for k in self.programs.keys():
            self.programs[k].die()
            del self.programs[k]
        for t in self.towers:
            t.destroy()
        for w in self.walls.itervalues():
            w.destroy()
        self.floor.destroy()
            
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
                print "seed",self.rand_seed
            elif ds[0] == 'player' and ds[1] != uname()[1]: # don't add yourself
                self.players[ds[1]] = None
                print "added",ds[1]
            elif ds[0] == 'start':
                print "starting"
                self.rest_of_init()
                return task.done # ends task
        return task.cont
    
    def network_listen(self):
        if taskMgr.hasTaskNamed("handshakeTask"): return
        data = self.client.getData()
        if len(data) == 0: return
        for d in data:
            ds = d.split(':')
            if len(ds) != 7: continue
            name,strs = ds[0],ds[1:]
            vel,hpr,anim,firing,collecting,dropping = map(eval,strs)
            if name in self.players:
                self.players[name].move(vel,hpr,anim,firing,collecting,dropping)
        base.cTrav.traverse(render)
        
    def make_tile(self, parent,fname,pos,hpr, scale=1.0):
        tile = loader.loadModel(fname)
        tile.reparentTo(parent)
        tile.setScale(scale, scale, scale)
        tile.setPos(pos)
        tile.setHpr(*hpr)
    
    def local_player(self):
        return self.players[uname()[1]]

def egg_index(i,j,center):
    if i < center and j < center: return 1
    if i < center: return 2
    if j < center: return 3
    return 0
