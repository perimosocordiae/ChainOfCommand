MODEL_PATH = "../../models"

from random import randint
from itertools import product as iproduct
import direct.directbase.DirectStart
from direct.task import Task
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import Point3
from pandac.PandaModules import Vec3
from pandac.PandaModules import Filename,Buffer,Shader
from player import Player
from drone import Drone

class Game(object):

    def __init__(self,map_size=320,tile_size=16):
        self.players, self.programs,self.drones = [],[],[]
        self.map_size,self.tile_size = map_size,tile_size
        base.disableMouse()
        self.load_env()
        
    def rand_point(self): # get a random point that's also a valid play location
        return (randint(-self.map_size+1,self.map_size-1),randint(-self.map_size+1,self.map_size-1))

    def add_player(self,pname):
        self.players.append(Player(self,pname))
        
    def add_program(self,ptype):
        self.programs.append(ptype(self))

    def add_drone(self):
        self.drones.append(Drone(self))

    def load_env(self):
        num_tiles = self.map_size/self.tile_size
        environ = loader.loadModel("%s/yellow_floor.egg"%MODEL_PATH)
        environ.reparentTo(render)
        environ.setScale(self.tile_size, self.tile_size, self.tile_size)
        environ.setPos(0, 0, 0)
                
        center = num_tiles/2
        for i,j in iproduct(range(num_tiles),repeat=2):
            if i < center and j < center:
                fl = "%s/blue_floor.egg"%MODEL_PATH
            elif i < center:
                fl = "%s/green_floor.egg"%MODEL_PATH
            elif j < center:
                fl = "%s/red_floor.egg"%MODEL_PATH
            else:
                fl = "%s/yellow_floor.egg"%MODEL_PATH
            #end if
              
            if i != center or j != center: #bottom center is already done
                make_tile(environ,fl,(2*(i-center), 2*(j-center), 0),(0, 0, 0)) #floor

            make_tile(environ,fl,(-2*(1+i-center),-2*(1+j-center), 2*num_tiles),    (0, 0, 190)) #ceiling
            make_tile(environ,fl,(-1-2*center,    2*(j-center),  2*(num_tiles-i)-1),(0, 0, 90))  #wall 1
            make_tile(environ,fl,(-2*(1+i-center), -1-2*center,  2*(num_tiles-j)-1),(0,-90,0))   #wall 2
            make_tile(environ,fl,( 2*center-1,     2*(j-center), 2*i+1),            (0, 0, -90)) #wall 3
            make_tile(environ,fl,(-2*(1+i-center), 2*center-1,   2*j+1),            (0, 90,0))   #wall 4

		# random column TODO: abstract this out
        blue_egg = "%s/blue_floor.egg"%MODEL_PATH
        for z in range(center / 2):
            make_tile(environ,blue_egg,(center,   center,   2*z+1),(0,  90,0))
            make_tile(environ,blue_egg,(center+1, center+1, 2*z+1),(90, 90,0))
            make_tile(environ,blue_egg,(center,   center+2, 2*z+1),(180,90,0))
            make_tile(environ,blue_egg,(center-1, center+1, 2*z+1),(270,90,0))
            #next z

# static function, not in the game class
def make_tile(parent,fname,pos,hpr):
	tile = loader.loadModel(fname)
	tile.reparentTo(parent)
	tile.setScale(1.0, 1.0, 1.0)
	tile.setPos(*pos)
	tile.setHpr(*hpr)

