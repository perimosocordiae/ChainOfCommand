MODEL_PATH = "../../models"

import math
import direct.directbase.DirectStart
from direct.task import Task
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import Point3
from pandac.PandaModules import Vec3
from pandac.PandaModules import Filename,Buffer,Shader

class Game(object):

    def __init__(self):
        base.disableMouse()
        base.camera.setPos(-80, -80, 15)
        base.camera.setHpr(-45, -10, 0)
        self.load_env(30)
        
    def add_player(self,p):
        return None
        
    def load_env(self,num_tiles):
        environ = loader.loadModel("%s/yellow_floor.egg"%MODEL_PATH)
        environ.reparentTo(render)
        environ.setScale(8.0, 8.0, 8.0)
        environ.setPos(0, 0, 0)
                
        center = num_tiles/2
        for i in range(num_tiles):
            for j in range(num_tiles):
                if i < center and j < center:
                    fl = "%s/blue_floor.egg"%MODEL_PATH
                elif i < center:
                    fl = "%s/green_floor.egg"%MODEL_PATH
                elif j < center:
                    fl = "%s/red_floor.egg"%MODEL_PATH
                else:
                    fl = "%s/yellow_floor.egg"%MODEL_PATH
                #end if
              
                #bottom center is already done
                if i != center or j != center:  
                    tile = loader.loadModel(fl)
                    tile.reparentTo(environ)
                    tile.setScale(1.0, 1.0, 1.0)
                    tile.setPos(2*(i - center), 2*(j - center), 0)
                #end if
                
                #ceiling
                tile = loader.loadModel(fl)
                tile.reparentTo(environ)
                tile.setScale(1.0, 1.0, 1.0)
                tile.setPos(-2*(1 + i - center), -2*(1 + j - center), 2 * num_tiles)
                tile.setHpr(0, 0, 180)
                
                #wall 1
                tile = loader.loadModel(fl)
                tile.reparentTo(environ)
                tile.setScale(1.0, 1.0, 1.0)
                tile.setPos(-1 - (2 * center), 2*(j - center), 2*(num_tiles - i) - 1)
                tile.setHpr(0, 0, 90)
                
                #wall 2
                tile = loader.loadModel(fl)
                tile.reparentTo(environ)
                tile.setScale(1.0, 1.0, 1.0)
                tile.setPos(-2*(1 + i - center), -1 - (2 * center), 2*(num_tiles - j) - 1)
                tile.setHpr(0, -90, 0)
                
                #wall 3
                tile = loader.loadModel(fl)
                tile.reparentTo(environ)
                tile.setScale(1.0, 1.0, 1.0)
                tile.setPos(2 * center - 1, 2*(j - center), (2 * i) + 1)
                tile.setHpr(0, 0, -90)
                
                #wall 4
                tile = loader.loadModel(fl)
                tile.reparentTo(environ)
                tile.setScale(1.0, 1.0, 1.0)
                tile.setPos(-2*(1 + i - center), (2 * center) - 1, (2 * j) + 1)
                tile.setHpr(0, 90, 0)
    
            
            blue_egg = "%s/blue_floor.egg"%MODEL_PATH
            for z in range(center / 2):
              tile = loader.loadModel(blue_egg)
              tile.reparentTo(environ)
              tile.setScale(1.0, 1.0, 1.0)
              tile.setPos(center, center, (2 * z) + 1)
              tile.setHpr(0,90,0)
              
              tile = loader.loadModel(blue_egg)
              tile.reparentTo(environ)
              tile.setScale(1.0, 1.0, 1.0)
              tile.setPos(center + 1, center + 1, (2 * z) + 1)
              tile.setHpr(90,90,0)
              
              tile = loader.loadModel(blue_egg)
              tile.reparentTo(environ)
              tile.setScale(1.0, 1.0, 1.0)
              tile.setPos(center, center + 2, (2 * z) + 1)
              tile.setHpr(180,90,0)
              
              tile = loader.loadModel(blue_egg)
              tile.reparentTo(environ)
              tile.setScale(1.0, 1.0, 1.0)
              tile.setPos(center - 1, center + 1, (2 * z) + 1)
              tile.setHpr(270,90,0)
            #next z