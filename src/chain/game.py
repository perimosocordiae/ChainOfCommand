MODEL_PATH = "../../models"

from random import randint, choice
#from itertools import product as iproduct
import direct.directbase.DirectStart
from eventHandler import GameEventHandler
from pandac.PandaModules import CollisionTraverser, CollisionSphere, BitMask32
from pandac.PandaModules import CollisionNode, CollisionPolygon, CollisionPlane, Plane
from player import Player
from drone import Drone
from direct.gui.OnscreenText import OnscreenText
from direct.task import Task
from time import time
from pandac.PandaModules import Vec3, Point3
import sys

FLOOR_COLLIDER_MASK = BitMask32.bit(4)
WALL_COLLIDER_MASK = BitMask32.bit(0)

class Game(object):

    def __init__(self,map_size=320,tile_size=16, gameLength=180):
        base.cTrav = CollisionTraverser()
        #wsbase.cTrav.showCollisions(render)
        self.players, self.programs,self.drones = {},{},{}
        self.map_size,self.tile_size = map_size,tile_size
        base.disableMouse()
        self.load_env()
        self.timer = OnscreenText(text="Time:", pos=(0,0.9), scale=(0.08), fg=(0,0,1,0.8), bg=(1,1,1,0.8), mayChange=True)
        self.startTime = time()
        self.endTime = self.startTime + gameLength
        self.gameTime = self.endTime - time()
        self.add_event_handler()
        self.add_background_music()
        taskMgr.doMethodLater(0.01, self.timerTask, 'timerTask')

    def rand_point(self): # get a random point that's also a valid play location
        return (randint(-self.map_size+1,self.map_size-2),randint(-self.map_size+1,self.map_size-2))

    def add_event_handler(self):
        self.eventHandle = GameEventHandler(self)
        for player in self.players.itervalues():
            player.initialize_camera()
    
    def add_player(self,pname):
        self.players[pname] = Player(self,pname)
        self.eventHandle.addPlayerHandler(self.players[pname])
        
    def add_program(self,ptype):
        prog = ptype(self)
        self.programs[prog.unique_str()] = prog
        self.eventHandle.addProgramHandler(self.programs[prog.unique_str()])
        
    def add_drone(self):
        d = Drone(self)
        self.drones[str(hash(d))] = d 
        self.eventHandle.addDroneHandler(d)
    
    def add_background_music(self):
        # from http://www.newgrounds.com/audio/listen/287442
        backgroundMusic = loader.loadSfx("../../sounds/City_in_Flight.mp3")
        backgroundMusic.setVolume(0.3)
        backgroundMusic.setTime(35)  # music automatically starts playing when this command is issued
        print "Track: City in Flight in Neon Light" # attribution
        print "Author: Trevor Dericks"

    def load_env(self):
        eggs = map(lambda s:"%s/%s_floor.egg"%(MODEL_PATH,s),['yellow','blue','green','red'])
        num_tiles = self.map_size/self.tile_size
        environ = loader.loadModel(eggs[0])
        environ.reparentTo(render)
        environ.setScale(self.tile_size, self.tile_size, self.tile_size)
        environ.setPos(0, 0, 0)
                
        center = num_tiles/2
        wall_height = 10
        #for i,j in iproduct(range(num_tiles),repeat=2):
        for i in range(num_tiles):
          for j in range(num_tiles):
            egg = eggs[egg_index(i,j,center)]
            make_tile(environ,egg,(-2*(1+i-center),-2*(1+j-center), 2*wall_height), (0, 0, 180)) #ceiling
            if i == center and j == center: continue #bottom center is already done
            make_tile(environ,egg,(2*(i-center), 2*(j-center), 0),(0, 0, 0),True) #floor
        
        #for i,j in iproduct(range(num_tiles),range(wall_height)):
        for i in range(num_tiles):
          for j in range(wall_height):
            egg = eggs[egg_index(i,j,center)]
            make_tile(environ,egg,(-1-2*center,    2*(i-center),  2*(wall_height-j)-1),(0, 0, 90))  #wall 1
            make_tile(environ,egg,(-2*(1+i-center), -1-2*center,  2*(wall_height-j)-1),(0,-90,0))   #wall 2
            make_tile(environ,egg,( 2*center-1,     2*(i-center), 2*j+1),            (0, 0, -90)) #wall 3
            make_tile(environ,egg,(-2*(1+i-center), 2*center-1,   2*j+1),            (0, 90,0))   #wall 4
        
        #Walls are at planes (x=-1-2*CENTER), (x=2*center-1), (y=-1-2*center), and (y=2*center-1) 
        self.wallCollider1 = environ.attachNewNode(CollisionNode("wall1"))
        self.wallCollider2 = environ.attachNewNode(CollisionNode("wall2"))
        self.wallCollider3 = environ.attachNewNode(CollisionNode("wall3"))
        self.wallCollider4 = environ.attachNewNode(CollisionNode("wall4"))
        self.wallCollider5 = environ.attachNewNode(CollisionNode("wall5"))
        self.wallCollider1.node().addSolid(CollisionPlane(Plane(Vec3(1, 0, 0), Point3(-2*center, 0, 0))))
        self.wallCollider2.node().addSolid(CollisionPlane(Plane(Vec3(-1, 0, 0), Point3(2*center, 0, 0))))
        self.wallCollider3.node().addSolid(CollisionPlane(Plane(Vec3(0, -1, 0), Point3(0, 2*center, 0))))
        self.wallCollider4.node().addSolid(CollisionPlane(Plane(Vec3(0, 1, 0), Point3(0, -2*center, 0))))
        self.wallCollider5.node().addSolid(CollisionPolygon(Point3(-2*center-1, -2*center-1, 0),
                Point3(2*center+1, -2*center-1, 0), Point3(2*center+1, 2*center+1, 0), Point3(-2*center-1, 2*center+1, 0)))
        self.wallCollider1.node().setFromCollideMask(WALL_COLLIDER_MASK)
        self.wallCollider2.node().setFromCollideMask(WALL_COLLIDER_MASK)
        self.wallCollider3.node().setFromCollideMask(WALL_COLLIDER_MASK)
        self.wallCollider4.node().setFromCollideMask(WALL_COLLIDER_MASK)
        self.wallCollider5.node().setFromCollideMask(FLOOR_COLLIDER_MASK)
        self.wallCollider1.node().setIntoCollideMask(WALL_COLLIDER_MASK)
        self.wallCollider2.node().setIntoCollideMask(WALL_COLLIDER_MASK)
        self.wallCollider3.node().setIntoCollideMask(WALL_COLLIDER_MASK)
        self.wallCollider4.node().setIntoCollideMask(WALL_COLLIDER_MASK)
        self.wallCollider5.node().setIntoCollideMask(FLOOR_COLLIDER_MASK)
        
        # make some random bunkers
        for _ in range(4):
            make_column(environ, choice(eggs), randint(-num_tiles,num_tiles), randint(-num_tiles,num_tiles), randint(2,wall_height))
        
    def timerTask(self, task):
        self.gameTime = self.endTime - time()
        self.timer.setText("Time: %.2f seconds"%(self.gameTime))
        if 0 < self.gameTime < 10:
            self.timer.setFg((1,0,0,0.8))
        elif self.gameTime <= 0:
            print "Game over"
            sys.exit()
        return task.again
        
def make_column(parent,egg,x,y,h):
    for z in range(h):
        make_tile(parent,egg,(x,   y,   2*z+1),(0,  90,0))
        make_tile(parent,egg,(x,   y+2, 2*z+1),(180,90,0))
        make_tile(parent,egg,(x+1, y+1, 2*z+1),(90, 90,0))
        make_tile(parent,egg,(x-1, y+1, 2*z+1),(270,90,0))
    # add a pusher for the bottom of the tower - do INSIDE the loop if
    #Tron can jump... for now this is more esfficient
    towerCollider = parent.attachNewNode(CollisionNode("tower_base"))
    towerCollider.node().addSolid(CollisionSphere(Point3(x, y, 1.0), 2.0))
    towerCollider.node().setFromCollideMask(WALL_COLLIDER_MASK)
    
# static functions, not in the game class
def make_tile(parent,fname,pos,hpr, addCollider=False):
    tile = loader.loadModel(fname)
    tile.reparentTo(parent)
    tile.setScale(1.0, 1.0, 1.0)
    tile.setPos(*pos)
    tile.setHpr(*hpr)
    #if addCollider:
    #    tileCollider = tile.attachNewNode(CollisionNode("tile"))
    #    tileCollider.node().addSolid(CollisionPolygon(Point3(-1.2,-1.2,0),
    #                Point3(1.2,-1.2,0), Point3(1.2,1.2,0), Point3(-1.2,1.2,0))) 
    #    tileCollider.node().setIntoCollideMask(FLOOR_COLLIDER_MASK)

def egg_index(i,j,center):
    if i < center and j < center: return 1
    if i < center: return 2
    if j < center: return 3
    return 0
