from math import sin, cos, tan, radians
from random import randint
from obstacle import *
from constants import *
from program import RAM

class Room(Obstacle):
    def __init__(self, name, parent, pos, rot, scale):
        self.walls = {}
        self.obstacles = {}
        self.hasRand = False
        self.scale = scale
        self.environ = parent.attachNewNode("%s_root"%name)
        self.environ.setScale(scale)
        self.environ.setPos(pos)
        self.environ.setHpr(rot)
    
    def add_wall(self, name, model, parent, p1, p2, p3, p4, colliderMask):
        self.walls[name] = (model, QuadWall(name, parent, p1, p2, p3, p4, colliderMask))
    
    def add_ram(self, game, name, pos, scale, hpr):
        self.obstacles[name] = RAMSlot(name, self.environ, pos, scale, hpr)
        ram = RAM(game, pos, scale * 7.0)
        game.readd_program(ram)
        
    def add_triangle(self, name, model, parent, p1, p2, p3, colliderMask):
        self.walls[name] = (model, TriangleWall(name, parent, p1, p2, p3, colliderMask))
        
    def destroy(self):
        for wall in self.walls.itervalues():
            wall[0].removeNode()
            wall[1].destroy()
        for obstacle in self.obstacles.itervalues():
            obstacle.destroy()
        self.walls.clear()
        self.obstacles.clear()
    
    def rand_point(self):
        return (0,0,0)
    
    def addWallSection(self, name, parent, pos, color, divisor=1, total=0):
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
                QuadWall("ceiling", self.environ, Point3(3,-3,4), Point3(-3,-3,4),
                         Point3(-3,3,4), Point3(3,3,4), WALL_COLLIDER_MASK))
        
    
    def rand_point(self):
        return (randint(-self.map_size + 1,self.map_size - 2),randint(-self.map_size + 1,self.map_size -2))
    
class Hallway(Room):
    def __init__(self, name, parent, pos, rot, scale, color, angle):
        super(Hallway, self).__init__(name, parent, pos, rot, scale)
        
        #Calculate how much shear, scale, and rotation is needed for the angle:
        origZ = self.environ.getSz();
        print origZ
        radAng = radians(angle)
        self.environ.setSz(origZ * cos(radAng))
        self.environ.setShyz(2 * origZ * tan(radAng))
        print self.environ.getShyz()
        self.environ.setP(self.environ.getP() + angle)
        
        #Add the 2 walls
        wall = self.environ.attachNewNode("wall_1")
        wall.setH(90)
        self.addWallSection("wall_1_1", wall, (1,1,1), color)
        
        wall = self.environ.attachNewNode("wall_2")
        wall.setH(270)
        self.addWallSection("wall_2_1", wall, (-1,1,1), color)
        
        #Add the floor & ceiling
        self.walls["floor"] = (make_tile(self.environ,"white_floor.egg",color,(0,1,0),(0,0,0),1.0),
                QuadWall("floor", self.environ, Point3(1,2,0), Point3(-1,2,0),
                         Point3(-1,0,0), Point3(1,0,0), FLOOR_COLLIDER_MASK))
        self.walls["ceiling"] = (make_tile(self.environ,"white_floor.egg",color,(0,1,2),(0,180,0),1.0),
                QuadWall("ceiling", self.environ, Point3(1,0,2), Point3(-1,0,2),
                         Point3(-1,2,2), Point3(1,2,2), WALL_COLLIDER_MASK))
        
class HallwayIntersection(Room):
    #types are: 1: angle right, 2: angle left, 3: T-intersection, 4: 4-way
    def __init__(self, name, parent, pos, rot, scale, color, type):
        super(HallwayIntersection, self).__init__(name, parent, pos, rot, scale)
        
        #Add the (up to 2) walls
        if type != 4:
            #Not a 4-way intersection - the opposite wall exists
            wall = self.environ.attachNewNode("wall_1")
            wall.setH(0)
            self.addWallSection("wall_1_1", wall, (0,1,1), color)
        
            if type != 3:
                #Not a T - there's another wall
                wall = self.environ.attachNewNode("wall_2")
                if type == 1:
                    wall.setH(90)
                    x = 1
                else:
                    wall.setH(270)
                    x = -1
                self.addWallSection("wall_2_1", wall, (x,1,1), color)
        
        #Add the floor & ceiling
        self.walls["floor"] = (make_tile(self.environ,"white_floor.egg",color,(0,1,0),(0,0,0),1.0),
                QuadWall("floor", self.environ, Point3(1,2,0), Point3(-1,2,0),
                         Point3(-1,0,0), Point3(1,0,0), FLOOR_COLLIDER_MASK))
        self.walls["ceiling"] = (make_tile(self.environ,"white_floor.egg",color,(0,1,2),(0,180,0),1.0),
                QuadWall("ceiling", self.environ, Point3(1,0,2), Point3(-1,0,2),
                         Point3(-1,2,2), Point3(1,2,2), WALL_COLLIDER_MASK))
        