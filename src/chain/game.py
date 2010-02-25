MODEL_PATH = "../../models"

from random import randint
#from itertools import product as iproduct
from eventHandler import GameEventHandler
from pandac.PandaModules import CollisionTraverser
from player import Player
from drone import Drone

class Game(object):

    def __init__(self,map_size=320,tile_size=16):
        base.cTrav = CollisionTraverser()
        self.players, self.programs,self.drones = {},{},{}
        self.map_size,self.tile_size = map_size,tile_size
        base.disableMouse()
        self.load_env()

    def rand_point(self): # get a random point that's also a valid play location
        return (randint(-self.map_size+1,self.map_size-2),randint(-self.map_size+1,self.map_size-2))

    def add_event_handler(self):
        self.eventHandle = GameEventHandler(self)
        for player in self.players.itervalues():
            player.initialize_camera()
    
    def add_player(self,pname):
        self.players[pname] = Player(self,pname)
        
    def add_program(self,ptype):
        prog = ptype(self)
        self.programs[prog.unique_str()] = prog

    def add_drone(self):
        d = Drone(self)
        self.drones[str(hash(d))] = d 

    def load_env(self):
        num_tiles = self.map_size/self.tile_size
        environ = loader.loadModel("%s/yellow_floor.egg"%MODEL_PATH)
        environ.reparentTo(render)
        environ.setScale(self.tile_size, self.tile_size, self.tile_size)
        environ.setPos(0, 0, 0)
                
        center = num_tiles/2
        wall_height = 10
        #for i,j in iproduct(range(num_tiles),repeat=2):
        for i in range(num_tiles):
          for j in range(num_tiles):
            egg = get_tile_egg(i,j,center)
            make_tile(environ,egg,(-2*(1+i-center),-2*(1+j-center), 2*wall_height), (0, 0, 180)) #ceiling
            if i == center and j == center: continue #bottom center is already done
            make_tile(environ,egg,(2*(i-center), 2*(j-center), 0),(0, 0, 0)) #floor

        #for i,j in iproduct(range(num_tiles),range(wall_height)):
        for i in range(num_tiles):
          for j in range(wall_height):
            egg = get_tile_egg(i,j,center)
            make_tile(environ,egg,(-1-2*center,    2*(i-center),  2*(wall_height-j)-1),(0, 0, 90))  #wall 1
            make_tile(environ,egg,(-2*(1+i-center), -1-2*center,  2*(wall_height-j)-1),(0,-90,0))   #wall 2
            make_tile(environ,egg,( 2*center-1,     2*(i-center), 2*j+1),            (0, 0, -90)) #wall 3
            make_tile(environ,egg,(-2*(1+i-center), 2*center-1,   2*j+1),            (0, 90,0))   #wall 4

		# random column 
		#TODO: abstract this out
        blue_egg = "%s/blue_floor.egg"%MODEL_PATH
        for z in range(center / 2):
            make_tile(environ,blue_egg,(center,   center,   2*z+1),(0,  90,0))
            make_tile(environ,blue_egg,(center+1, center+1, 2*z+1),(90, 90,0))
            make_tile(environ,blue_egg,(center,   center+2, 2*z+1),(180,90,0))
            make_tile(environ,blue_egg,(center-1, center+1, 2*z+1),(270,90,0))
    
# static functions, not in the game class
def make_tile(parent,fname,pos,hpr):
	tile = loader.loadModel(fname)
	tile.reparentTo(parent)
	tile.setScale(1.0, 1.0, 1.0)
	tile.setPos(*pos)
	tile.setHpr(*hpr)

def get_tile_egg(i,j,center):
	if i < center and j < center:
		return "%s/blue_floor.egg"%MODEL_PATH
	if i < center:
		return "%s/green_floor.egg"%MODEL_PATH
	if j < center:
		return "%s/red_floor.egg"%MODEL_PATH
	return "%s/yellow_floor.egg"%MODEL_PATH
