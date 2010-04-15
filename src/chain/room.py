from math import sin, cos, tan, radians, sqrt
from random import randint
from obstacle import *
from constants import *
from program import RAM

class Room(Obstacle):
    def __init__(self, name, parent, pos, rot, scale):
        self.walls = {}
        self.obstacles = {}
        self.name = name
        self.scale = scale
        self.environ = parent.attachNewNode("%s_root"%name)
        self.environ.setScale(scale)
        self.environ.setPos(pos)
        self.environ.setHpr(rot)
    
    def add_wall(self, name, model, parent, p1, p2, p3, p4, colliderMask):
        self.walls[name] = (model, QuadWall(name, parent, p1, p2, p3, p4, colliderMask))
    
    def add_ram(self, game, name, pos, scale, hpr):
        self.obstacles[name] = RAMSlot(name, render, pos, scale, hpr)
        ram = RAM(game, self, pos, scale * 7.0)
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
        return render.getRelativePoint(self.environ, self.relative_rand_point())
    
    def relative_rand_point(self):
        return (0,0,0)
    
    def add_program(self,game,ptype,color=None):
        if color:
            prog = ptype(game, self, color)
        else:
            prog = ptype(game, self)
        game.readd_program(prog)
    
    def addWallSection(self, name, parent, pos, color, divisor=1, total=0):
        if total >= divisor:
            rotation = (6-(total//divisor)) % 4
            if rotation % 2 == 1:
                egg = "L_wall.bam"
            else:
                egg = "Reverse_L_wall.bam"
        else:
            rotation = 0
            egg = "white_wall.bam"
        model = make_tile(parent,egg,color,pos,(0,0,90 * rotation))
        if total >= divisor:
            wall = LWall(name, model, Point3(1,0,1), Point3(-1,0,1),
                    Point3(-1,0,-1), Point3(1,0,-1), WALL_COLLIDER_MASK)
        else:
            wall = QuadWall(name, model, Point3(1,0,1), Point3(-1,0,1),
                    Point3(-1,0,-1), Point3(1,0,-1), WALL_COLLIDER_MASK)
        self.walls[name] = (model,wall)
    
    def addRightTriangle(self, name, parent, pos, color):
        model = make_tile(parent,"right_triangle.bam",color,pos,(0,0,0))
        wall = TriangleWall(name, model, Point3(2,0,0), Point3(0,2,0),
                            Point3(0,0,0), WALL_COLLIDER_MASK)
        self.walls[name] = (model, wall)
    
    def has_point(self, pos):
        mypt = self.environ.getRelativePoint(render,Point3(pos[0],pos[1],pos[2]))
        x1,x2,y1,y2,z1,z2 = self.get_bounds()
        return mypt[0] > x1 and mypt[0] < x2 and mypt[1] > y1 and mypt[1] < y2 and mypt[2] > z1 and mypt[2] < z2
    
    def get_bounds(self):
        return 0,0,0,0,0,0
    
class CubeRoom(Room):
    def __init__(self, name, parent, pos, rot, scale, color, holes=(0,0,0,0,0,0,0,0)):
        super(CubeRoom, self).__init__(name, parent, pos, rot, scale)
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
        self.walls["floor"] = (make_tile(self.environ,"white_floor.bam",color,(0,0,0),(0,0,0),3.0),
                QuadWall("floor", self.environ, Point3(3,3,0), Point3(-3,3,0),
                         Point3(-3,-3,0), Point3(3,-3,0), FLOOR_COLLIDER_MASK))
        self.walls["ceiling"] = (make_tile(self.environ,"white_floor.bam",color,(0,0,4),(0,180,0),3.0),
                QuadWall("ceiling", self.environ, Point3(3,-3,4), Point3(-3,-3,4),
                         Point3(-3,3,4), Point3(3,3,4), WALL_COLLIDER_MASK))
        
    
    def relative_rand_point(self):
        return (randint(-25,25) / 10, randint(-25,25)/10, 0)
    
    def get_bounds(self):
        return -3,3,-3,3,-0.1,4
    
class Hallway(Room):
    def __init__(self, name, parent, pos, rot, scale, color, angle):
        super(Hallway, self).__init__(name, parent, pos, rot, scale)
        
        #Calculate how much shear, scale, and rotation is needed for the angle:
        origZ = self.environ.getSz();
        radAng = radians(angle)
        self.environ.setSz(origZ * cos(radAng))
        self.environ.setShyz(2 * origZ * tan(radAng))
        self.environ.setP(self.environ.getP() + angle)
        
        #Add the 2 walls
        wall = self.environ.attachNewNode("wall_1")
        wall.setH(90)
        self.addWallSection("wall_1_1", wall, (1,1,1), color)
        
        wall = self.environ.attachNewNode("wall_2")
        wall.setH(270)
        self.addWallSection("wall_2_1", wall, (-1,1,1), color)
        
        #Add the floor & ceiling
        self.walls["floor"] = (make_tile(self.environ,"white_floor.bam",color,(0,1,0),(0,0,0),1.0),
                QuadWall("floor", self.environ, Point3(1,2,0), Point3(-1,2,0),
                         Point3(-1,0,0), Point3(1,0,0), FLOOR_COLLIDER_MASK))
        self.walls["ceiling"] = (make_tile(self.environ,"white_floor.bam",color,(0,1,2),(0,180,0),1.0),
                QuadWall("ceiling", self.environ, Point3(1,0,2), Point3(-1,0,2),
                         Point3(-1,2,2), Point3(1,2,2), WALL_COLLIDER_MASK))
        
    def relative_rand_point(self):
        return (randint(-8,8) / 10,randint(2,18)/10, 0)
    
    def get_bounds(self):
        return -1,1,0,2,0,2
    
class HallwayIntersection(Room):
    #types are: 0: dead end, 1: angle right, 2: angle left, 3: T-intersection, 4: 4-way
    def __init__(self, name, parent, pos, rot, scale, color, type):
        super(HallwayIntersection, self).__init__(name, parent, pos, rot, scale)
        
        #Add the (up to 2) walls
        if type != 4:
            #Not a 4-way intersection - the opposite wall exists
            wall = self.environ.attachNewNode("wall_1")
            wall.setH(0)
            self.addWallSection("wall_1_1", wall, (0,2,1), color)
        
            if type != 3:
                #Not a T - there's another wall
                if type < 2:
                    wall = self.environ.attachNewNode("wall_2")
                    #dead end or right turn - add left wall
                    wall.setH(90)
                    self.addWallSection("wall_2_1", wall, (1,1,1), color)
                if type != 1:
                    wall = self.environ.attachNewNode("wall_3")
                    #dead end or left turn - add right wall
                    wall.setH(270)
                    self.addWallSection("wall_3_1", wall, (-1,1,1), color)
                
        
        #Add the floor & ceiling
        self.walls["floor"] = (make_tile(self.environ,"white_floor.bam",color,(0,1,0),(0,0,0),1.0),
                QuadWall("floor", self.environ, Point3(1,2,0), Point3(-1,2,0),
                         Point3(-1,0,0), Point3(1,0,0), FLOOR_COLLIDER_MASK))
        self.walls["ceiling"] = (make_tile(self.environ,"white_floor.bam",color,(0,1,2),(0,180,0),1.0),
                QuadWall("ceiling", self.environ, Point3(1,0,2), Point3(-1,0,2),
                         Point3(-1,2,2), Point3(1,2,2), WALL_COLLIDER_MASK))
        
    def relative_rand_point(self):
        return (randint(-8,8) / 10,randint(2,18)/10, 0)
    
    def get_bounds(self):
        return -1,1,0,2,0,2
    
class Platform(Room):
    def __init__(self, name, parent, pos, rot, scale, color):
        super(Platform, self).__init__(name, parent, pos, rot, scale)
        
        #Add the floor & ceiling
        self.walls["floor"] = (make_tile(self.environ,"white_floor.bam",color,(0,1,0),(0,0,0),1.0),
                QuadWall("floor", self.environ, Point3(1,2,0), Point3(-1,2,0),
                         Point3(-1,0,0), Point3(1,0,0), FLOOR_COLLIDER_MASK))
        self.walls["ceiling"] = (make_tile(self.environ,"white_floor.bam",color,(0,1,-1),(0,225,0),(1.0,sqrt(2),sqrt(2))),
                QuadWall("ceiling", self.environ, Point3(1,0,-2), Point3(-1,0,-2),
                         Point3(-1,2,0), Point3(1,2,0), WALL_COLLIDER_MASK))
        
        wall = self.environ.attachNewNode("wall_1")
        wall.setR(90)
        self.addRightTriangle("wall_1_1", wall, (0,0,1), color)
        
        wall = self.environ.attachNewNode("wall_2")
        wall.setHpr(90,-90,0)
        self.addRightTriangle("wall_2_1", wall, (0,0,1), color)
    
    def relative_rand_point(self):
        return (randint(-8,8) / 10,randint(2,18)/10, 0)
    
    def get_bounds(self):
        return -1,1,0,2,0,2
    
class StandardHall(Hallway):
    #Assume it's a flat hallway, no pitch or roll, 1 x 2*y x 1 (y is essentially
    #half of the hallway's length, width==height==1), with a standard, unique name
    def __init__(self, parent, pos, hrot, yscale, color):
        super(StandardHall, self).__init__("Hall_" + str(hash(self)), parent,
                                pos, (hrot,0,0), (0.5,yscale,0.5), color, 0)

class StandardIntersection(HallwayIntersection):
    #Like StandardHall, but for intersections
    def __init__(self, parent, pos, hrot, color, type):
        super(StandardIntersection, self).__init__("Corner_" + str(hash(self)),
                                parent, pos, (hrot,0,0), 0.5, color, type)
    