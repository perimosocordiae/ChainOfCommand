from random import randint
from obstacle import *
from constants import *

class Room(Obstacle):
    def __init__(self, name, parent, pos, rot, scale):
        self.walls = {}
        self.hasRand = False
        self.scale = scale
        self.environ = parent.attachNewNode("%s_root"%name)
        self.environ.setScale(scale)
        self.environ.setPos(pos)
        self.environ.setHpr(rot)
    
    def add_wall(self, name, model, parent, p1, p2, p3, p4, colliderMask):
        self.walls[name] = (model, QuadWall(name, parent, p1, p2, p3, p4, colliderMask))
    
    def add_triangle(self, name, model, parent, p1, p2, p3, colliderMask):
        self.walls[name] = (model, TriangleWall(name, parent, p1, p2, p3, colliderMask))
        
    def destroy(self):
        for wall in self.walls.itervalues():
            wall[0].removeNode()
            wall[1].destroy()
        self.walls.clear()
    
    def rand_point(self):
        return (0,0,0)
    
    def addWallSection(self, name, parent, pos, color, divisor, total):
        if total >= divisor:
            rotation = (6-(total//divisor)) % 4
            egg = "L_wall.egg"
        else:
            rotation = 0
            egg = "white_wall.egg"
        model = make_tile(parent,egg,color,pos,(0,0,90 * rotation))
        if total >= divisor:
            wall = LWall(name, model, Point3(1,0,1), Point3(-1,0,1),
                    Point3(-1,0,-1), Point3(1,0,-1), WALL_COLLIDER_MASK)
        else:
            wall = QuadWall(name, model, Point3(1,0,1), Point3(-1,0,1),
                    Point3(-1,0,-1), Point3(1,0,-1), WALL_COLLIDER_MASK)
        self.walls[name] = (model,wall)
    
class CubeRoom(Room):
    def __init__(self, name, parent, pos, rot, scale, color, holes=(0,0,0,0,0,0,0,0)):
        super(CubeRoom, self).__init__(name, parent, pos, rot, scale)
        self.hasRand = True
        for i in range(8):
            h = (i * 90) % 360
            z = ((i // 4) * 2) + 1
            wall = self.environ.attachNewNode("wall_%s"%i)
            wall.setH(h)
            total = holes[i]
            self.addWallSection("wall_%s_1"%i, wall, (2,3,z), color, 25, total)
            total = total % 25
            self.addWallSection("wall_%s_2"%i, wall, (0,3,z), color, 5, total)
            total = total % 5
            self.addWallSection("wall_%s_3"%i, wall, (-2,3,z), color, 1, total)
            
        #Now add the floor & ceiling
        self.walls["floor"] = (make_tile(self.environ,"white_floor.egg",color,(0,0,0),(0,0,0),3.0),
                QuadWall("floor", self.environ, Point3(3,3,0), Point3(-3,3,0),
                         Point3(-3,-3,0), Point3(3,-3,0), FLOOR_COLLIDER_MASK))
        self.walls["ceiling"] = (make_tile(self.environ,"white_floor.egg",color,(0,0,4),(0,180,0),3.0),
                QuadWall("floor", self.environ, Point3(3,-3,4), Point3(-3,-3,4),
                         Point3(-3,3,4), Point3(3,3,4), WALL_COLLIDER_MASK))
        
    
    def rand_point(self):
        return (randint(-self.map_size + 1,self.map_size - 2),randint(-self.map_size + 1,self.map_size -2))
    
class Hallway(Room):
    def __init__(self, name, parent):
        super(Hallway, self).__init__(name, parent)
        