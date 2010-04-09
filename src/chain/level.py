from room import *
from math import sin, cos, radians

class Level(Obstacle):
    def __init__(self, parent):
        self.rooms = {}
        self.bases = {}
        self.parent = parent
        
    def destroy(self):
        for room in self.rooms.itervalues():
            room.destroy()
        self.rooms.clear() 
        
class CubeLevel(Level):
    def __init__(self, parent):
        super(CubeLevel, self).__init__(parent)
        self.rooms["Cube_Room"] = CubeRoom("Cube_Room", self.parent, (0,0,0),
                        (0,0,0), 1.0, "white", holes=(0,0,0,0,0,0,0,0))
        
class BasicBaseLevel(Level):
    def __init__(self, parent, hallwayAngle = 20):
        super(BasicBaseLevel, self).__init__(parent)
        self.rooms["Cube_Room"] = CubeRoom("Cube_Room", self.parent, (0,0,0),
                        (0,0,0), 1.0, "white", holes=(5,0,0,0,0,0,0,0))
        self.rooms["Hall"] = Hallway("Hall", self.parent, (-0.5,3,0),
                        (0,0,0), (0.5,4.0,0.5), "blue", hallwayAngle)
        radAng = radians(hallwayAngle)
        basey = (cos(radAng) * 8.0) + 3.75
        basez = sin(radAng) * 8.0
        self.rooms["Blue_Base"] = CubeRoom("Blue_Base", self.parent, (0,basey,basez),
                    (180,0,0), (1.0,0.25,1.0), "blue", holes=(10,0,0,0,0,0,0,0))