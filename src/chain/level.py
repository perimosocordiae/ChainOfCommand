from room import *
from math import sin, cos, radians

class Level(Obstacle):
    def __init__(self, parent):
        self.rooms = {}
        self.bases = {}
        self.obstacles = {}
        self.parent = parent
        
    def destroy(self):
        for room in self.rooms.itervalues():
            room.destroy()
        for obstacle in self.obstacles.itervalues():
            obstacle.destroy()
        self.rooms.clear() 
        self.obstacles.clear()
        self.bases.clear()
        
class CubeLevel(Level):
    def __init__(self, parent):
        super(CubeLevel, self).__init__(parent)
        self.rooms["Cube_Room"] = CubeRoom("Cube_Room", self.parent, (0,0,0),
                        (0,0,0), 1.0, "white", holes=(0,0,0,0,0,0,0,0))
        
class BasicBaseLevel(Level):
    def __init__(self, parent, hallwayAngle = 20):
        super(BasicBaseLevel, self).__init__(parent)
        self.rooms["Cube_Room"] = CubeRoom("Cube_Room", self.parent, (0,0,0),
                        (0,0,0), 1.0, "white", holes=(5,0,5,0,0,0,0,0))
        self.rooms["Blue_Hall"] = Hallway("Blue_Hall", self.parent, (-0.5,3,0),
                        (0,0,0), (0.5,4.0,0.5), "blue", hallwayAngle)
        self.rooms["Red_Hall"] = Hallway("Red_Hall", self.parent, (0.5,-3,0),
                        (180,0,0), (0.5,4.0,0.5), "red", hallwayAngle)
        radAng = radians(hallwayAngle)
        basey = (cos(radAng) * 8.0) + 3.75
        basez = sin(radAng) * 8.0
        self.rooms["Blue_Base"] = CubeRoom("Blue_Base", self.parent, (0,basey,basez),
                    (180,0,0), (1.0,0.25,1.0), "blue", holes=(10,0,0,0,0,0,0,0))
        self.bases["blue"] = self.rooms["Blue_Base"]
        self.rooms["Red_Base"] = CubeRoom("Red_Base", self.parent, (0,-basey,basez),
                    (0,0,0), (1.0,0.25,1.0), "red", holes=(10,0,0,0,0,0,0,0))
        self.bases["red"] = self.rooms["Red_Base"]
        
class SniperLevel(Level):
    def __init__(self, parent):
        super(SniperLevel, self).__init__(parent)
        hallwayAngle = 14.47751219 #arcsin(0.25)
        self.rooms["Cube_Room"] = CubeRoom("Cube_Room", self.parent, (0,0,0),
                    (0,0,0), 1.0, "white", holes=(2,0,2,0,100,0,100,0))
        self.rooms["Blue_Hall"] = Hallway("Blue_Hall", self.parent, (-1.5,3,0),
                    (0,0,0), (0.5,3.0,0.5), "blue", hallwayAngle)
        self.rooms["Red_Hall"] = Hallway("Red_Hall", self.parent, (1.5,-3,0),
                    (180,0,0), (0.5,3.0,0.5), "red", hallwayAngle)
        radAng = radians(hallwayAngle)
        basey = (cos(radAng) * 6.0) + 3.75
        basez = sin(radAng) * 6.0
        self.rooms["Blue_Base"] = CubeRoom("Blue_Base", self.parent, (0,basey,basez),
                    (180,0,0), (1.0,0.25,1.0), "blue", holes=(27,0,0,0,0,0,0,0))
        self.bases["blue"] = self.rooms["Blue_Base"]
        self.rooms["Red_Base"] = CubeRoom("Red_Base", self.parent, (0,-basey,basez),
                    (0,0,0), (1.0,0.25,1.0), "red", holes=(27,0,0,0,0,0,0,0))
        self.bases["red"] = self.rooms["Red_Base"]
        
        self.rooms["Blue_Ramp"] = Hallway("Blue_Ramp", self.parent, (1.5,basey-.75,basez),
                    (180,0,0), (0.5,3.0,0.5), "blue", hallwayAngle)
        self.rooms["Red_Ramp"] = Hallway("Red_Ramp", self.parent, (-1.5,-basey+.75,basez),
                    (0,0,0), (0.5,3.0,0.5), "red", hallwayAngle)
        
        self.rooms["Blue_Platform"] = Platform("Blue_Platform", self.parent, (1.5,3,3),
                    (180,0,0), (0.5,0.25,0.125), "blue")
        self.rooms["Red_Platform"] = Platform("Red_Platform", self.parent, (-1.5,-3,3),
                    (0,0,0), (0.5,0.25,0.125), "red")
        
        self.rooms["Blue_Platform2"] = Platform("Blue_Platform2", self.parent, (0,0,3),
                    (0,0,0), (0.8,0.5,0.125), "blue")
        self.rooms["Red_Platform2"] = Platform("Red_Platform2", self.parent, (0,0,3),
                    (180,0,0), (0.8,0.5,0.125), "red")
        