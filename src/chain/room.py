from obstacle import *
from constants import *

class Room(Obstacle):
    def __init__(self, name, parent):
        self.walls = {}
    
    def add_wall(self, name, model, parent, p1, p2, p3, p4, colliderMask):
        self.walls[name] = (model, QuadWall(name, parent, p1, p2, p3, p4, colliderMask))
    
    def add_triangle(self, name, model, parent, p1, p2, p3, colliderMask):
        self.walls[name] = (model, TriangleWall(name, parent, p1, p2, p3, colliderMask))
        
    def destroy(self):
        for wall in self.walls.itervalues():
            wall[0].removeNode()
            wall[1].destroy()
        self.walls.clear()
    
class CubeRoom(Room):
    def __init__(self, name, parent, scale, eggs):
        super(CubeRoom, self).__init__(name, parent)
        
class Hallway(Room):
    def __init__(self, name, parent):
        super(Hallway, self).__init__(name, parent)
        