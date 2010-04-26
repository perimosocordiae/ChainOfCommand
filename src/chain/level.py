from room import *
from program import *
from random import choice

class Level(Obstacle):
    def __init__(self, game, parent):
        self.rooms = {}
        self.bases = {}
        self.obstacles = {}
        self.tower_size = 16 #hard coded for now
        self.game = game
        self.parent = parent
        
    def destroy(self):
        for room in self.rooms.itervalues():
            room.destroy()
        for obstacle in self.obstacles.itervalues():
            obstacle.destroy()
        self.rooms.clear() 
        self.obstacles.clear()
        self.bases.clear()
    
    def create_ln_at(self, pos, ln):
        for room in self.rooms.itervalues():
            if room.has_point(pos):
                room.create_ln_at(pos, ln)
                return
        #next room
    
    def south_bridge_pos(self):
        return Point3(0,0,0)
    
    def default_environment(self):
        #Sets up the good old classic 5 sticks of RAM, 5 capacitors, 4 of each program
        #Notes: 1. Requires room called "Cube_Room"
        #       2. Doesn't add "Locate" - these are on sniper platforms (cuz they're special)
        for _ in range(4):
            self.rooms["Cube_Room"].add_program(self.game, Rm)
            self.rooms["Cube_Room"].add_program(self.game, Chmod)
            self.rooms["Cube_Room"].add_program(self.game, DashR)
            #self.rooms["Cube_Room"].add_program(self.game, RAM)
            self.rooms["Cube_Room"].add_program(self.game, Gdb)
            #self.rooms["Cube_Room"].add_program(self.game, Locate)
            self.rooms["Cube_Room"].add_program(self.game, Ls)
            self.rooms["Cube_Room"].add_program(self.game, Sudo)
            
        for slot in range(5):
            pos = self.rooms["Cube_Room"].rand_point()
            name = "RAM_slot_%d"%slot
            scale = randint(5,10) * 0.75
            self.rooms["Cube_Room"].add_ram(self.game, name, Point3(pos[0], pos[1], pos[2]), scale, Point3(0, 0, 0))
        
        for tower in range(4):
            pos = self.rooms["Cube_Room"].rand_point()
            name = "tower_%d"%tower
            self.rooms["Cube_Room"].obstacles[name] = Tower(render, pos[0], pos[1], 
                                     randint(10,4*self.tower_size))
    
    def point_for(self, color):
        if color in self.bases.iterkeys():
            #We found their base - send them there
            return self.bases[color].rand_point()
        elif len(self.rooms) > 0:
            #Just pick a random room - it's the best we can do
            return choice(self.rooms.values()).rand_point()
        else:
            #no rooms available - the best we can do is the origin
            return (0,0,0)
    
    def readd_flag(self, flag):
        if flag:
            color = flag.color
            if color in self.bases and self.bases[color]:
                self.bases[color].readd_flag(flag) 
        
class CubeLevel(Level):
    def __init__(self, game, parent):
        super(CubeLevel, self).__init__(game, parent)
        self.rooms["Cube_Room"] = CubeRoom("Cube_Room", self.parent, (0,0,0),
                        (0,0,0), 1.0, "white", holes=(0,0,0,0,0,0,0,0))
        self.default_environment()
        
class BasicBaseLevel(Level):
    def __init__(self, game, parent, hallwayAngle = 20):
        super(BasicBaseLevel, self).__init__(game, parent)
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
        self.default_environment()
        self.rooms["Blue_Base"].add_program(self.game, Flag, "blue")
        self.rooms["Red_Base"].add_program(self.game, Flag, "red")
        
class SniperLevel(Level):
    def __init__(self, game, parent, team1="blue", team2="red"):
        super(SniperLevel, self).__init__(game, parent)
        t1 = team1.capitalize()
        t2 = team2.capitalize()
        hallwayAngle = 14.47751219 #arcsin(0.25)
        self.rooms["Cube_Room"] = CubeRoom("Cube_Room", self.parent, (0,0,0),
                    (0,0,0), 1.0, "white", holes=(2,0,2,0,100,0,100,0))
        self.rooms["%s_Hall"%t1] = Hallway("%s_Hall"%t1, self.parent, (-1.5,3,0),
                    (0,0,0), (0.5,3.0,0.5), team1, hallwayAngle)
        self.rooms["%s_Hall"%t2] = Hallway("%s_Hall"%t2, self.parent, (1.5,-3,0),
                    (180,0,0), (0.5,3.0,0.5), team2, hallwayAngle)
        radAng = radians(hallwayAngle)
        basey = (cos(radAng) * 6.0) + 3.75
        basez = sin(radAng) * 6.0
        self.rooms["%s_Base"%t1] = CubeRoom("%s_Base"%t1, self.parent, (0,basey,basez),
                    (180,0,0), (1.0,0.25,1.0), team1, holes=(27,0,0,0,0,0,0,0))
        self.bases[team1] = self.rooms["%s_Base"%t1]
        self.rooms["%s_Base"%t2] = CubeRoom("%s_Base"%t2, self.parent, (0,-basey,basez),
                    (0,0,0), (1.0,0.25,1.0), team2, holes=(27,0,0,0,0,0,0,0))
        self.bases[team2] = self.rooms["%s_Base"%t2]
        
        self.rooms["%s_Ramp"%t1] = Hallway("%s_Ramp"%t1, self.parent, (1.5,basey-.75,basez),
                    (180,0,0), (0.5,3.0,0.5), team1, hallwayAngle)
        self.rooms["%s_Ramp"%t2] = Hallway("%s_Ramp"%t2, self.parent, (-1.5,-basey+.75,basez),
                    (0,0,0), (0.5,3.0,0.5), team2, hallwayAngle)
        
        self.rooms["%s_Platform"%t1] = Platform("%s_Platform"%t1, self.parent, (1.5,3,3),
                    (180,0,0), (0.5,0.25,0.125), team1)
        self.rooms["%s_Platform"%t2] = Platform("%s_Platform"%t2, self.parent, (-1.5,-3,3),
                    (0,0,0), (0.5,0.25,0.125), team2)
        
        self.rooms["%s_Platform2"%t1] = Platform("%s_Platform2"%t1, self.parent, (0,0,3),
                    (0,0,0), (0.8,0.5,0.125), team1)
        self.rooms["%s_Platform2"%t2] = Platform("%s_Platform2"%t2, self.parent, (0,0,3),
                    (180,0,0), (0.8,0.5,0.125), team2)
        
        self.default_environment()
        self.rooms["%s_Platform"%t1].add_program(self.game, Locate)
        self.rooms["%s_Platform"%t2].add_program(self.game, Locate)
        self.rooms["%s_Base"%t1].add_program(self.game, Flag, team1)
        self.rooms["%s_Base"%t2].add_program(self.game, Flag, team2)
        for i in range(1,10):
            self.rooms["Cube_Room"].add_program(self.game, Ln)
        
class Beaumont(Level):
    def __init__(self, game, parent, team1="blue", team2="red"):
        super(Beaumont, self).__init__(game, parent)
        t1 = team1.capitalize()
        t2 = team2.capitalize()
        z = 4 #All rooms on the top floor have this z
        
        #****************************** team1 side ******************************
        #************* Start of Symmetry *************
        self.rooms["room_116"] = CubeRoom("room_116", self.parent, (-21, 7.4, z),
                    (0,0,0), (1.0, 0.8, 1.0), team1, (0,0,1,0,0,0,0,0))
        
        room = StandardHall(self.parent, (-18.5,5,z), 180, 0.5, team1)
        self.rooms[room.name] = room
        room = StandardIntersection(self.parent, (-18,3.5,z), 90, team1, 1)
        self.rooms[room.name] = room
        room = StandardHall(self.parent, (-16,3.5,z), 90, 1.0, team1)
        self.rooms[room.name] = room
        room = StandardIntersection(self.parent, (-15.5,3,z), 0, team1, 3)
        self.rooms[room.name] = room
        
        #Stair area
        room = StandardIntersection(self.parent, (-16,2.5,z), 270, team1, 3)
        self.rooms[room.name] = room
        room = StandardHall(self.parent, (-16,2.5,z), 90, 0.5, team1)
        self.rooms[room.name] = room
        room = StandardIntersection(self.parent, (-17.5,2,z), 0, team1, 1)
        self.rooms[room.name] = room
        self.rooms["upper_stairs_1"] = Hallway("upper_stairs_1", self.parent,
                    (-17.5,-1.4641,2),(0,0,0),(0.5,2,0.5), team1, 30)
        room = StandardIntersection(self.parent, (-17.5,-1.4641,2), 180, team1, 2)
        self.rooms[room.name] = room
        room = StandardIntersection(self.parent, (-16.5,-1.4641,2), 180, team1, 1)
        self.rooms[room.name] = room
        self.rooms["lower_stairs_1"] = Hallway("lower_stairs_1", self.parent,
                    (-16.5,2,0),(180,0,0),(0.5,2,0.5), team1, 30)
        
        #Bathroom area
        room = StandardHall(self.parent, (-15.5,2,z), 180, 1.5, team1)
        self.rooms[room.name] = room
        room = StandardIntersection(self.parent, (-15,-1.5,z), 90, team1, 3)
        self.rooms[room.name] = room
        self.rooms["mens_room"] = CubeRoom("mens_room", self.parent, (-9, 0, z),
                    (0,0,0), (2.0, 1.0, 1.0), team1, (0,2,0,0,0,0,0,0))
        
        #Below (and left of) bathroom
        room = StandardHall(self.parent, (-15.5,-2,z), 180, 0.5, team1)
        self.rooms[room.name] = room
        room = StandardIntersection(self.parent, (-15.5,-3,z), 180, team1, 1)
        self.rooms[room.name] = room
        room = StandardHall(self.parent, (-16,-3.5,z), 90, 1.0, team1)
        self.rooms[room.name] = room
        room = StandardIntersection(self.parent, (-18,-3.5,z), 90, team1, 3)
        self.rooms[room.name] = room
        self.rooms["room_114"] = CubeRoom("room_114", self.parent, (-21, 0, z),
                    (0,0,0), 1.0, team1, (0,0,1,0,0,0,0,0))
        self.bases[team1] = self.rooms["room_114"]
        
        room = StandardHall(self.parent, (-18.5,-4,z), 180, 0.5, team1)
        self.rooms[room.name] = room
        self.rooms["room_112"] = CubeRoom("room_112", self.parent, (-21, -7.4, z),
                    (0,0,0), (1.0, 0.8, 1.0), team1, (50,0,0,0,0,0,0,0))
        
        #upper hallway (RA room area)
        room = StandardHall(self.parent, (-6,3.5,z), 90, 4.5, team1)
        self.rooms[room.name] = room
        room = StandardIntersection(self.parent, (-5.5,4,z), 180, team1, 3)
        self.rooms[room.name] = room
        room = StandardHall(self.parent, (-3,3.5,z), 90, 1.0, team1)
        self.rooms[room.name] = room
        #TODO - the turn
        #************* End of Symmetry *************
        
        #****************************** team2 side ******************************
        #************* Start of Symmetry *************
        self.rooms["room_125"] = CubeRoom("room_125", self.parent, (21, 7.4, z),
                    (0,0,0), (1.0, 0.8, 1.0), team2, (0,0,50,0,0,0,0,0))
        
        room = StandardHall(self.parent, (18.5,5,z), 180, 0.5, team2)
        self.rooms[room.name] = room
        room = StandardIntersection(self.parent, (18,3.5,z), 270, team2, 2)
        self.rooms[room.name] = room
        room = StandardHall(self.parent, (16,3.5,z), 270, 1.0, team2)
        self.rooms[room.name] = room
        room = StandardIntersection(self.parent, (15.5,3,z), 0, team2, 3)
        self.rooms[room.name] = room
        
        #Stair area
        room = StandardIntersection(self.parent, (16,2.5,z), 90, team2, 3)
        self.rooms[room.name] = room
        room = StandardHall(self.parent, (16,2.5,z), 270, 0.5, team2)
        self.rooms[room.name] = room
        room = StandardIntersection(self.parent, (17.5,2,z), 0, team2, 2)
        self.rooms[room.name] = room
        self.rooms["upper_stairs_3"] = Hallway("upper_stairs_3", self.parent,
                    (17.5,-1.4641,2),(0,0,0),(0.5,2,0.5), team2, 30)
        room = StandardIntersection(self.parent, (17.5,-1.4641,2), 180, team2, 1)
        self.rooms[room.name] = room
        room = StandardIntersection(self.parent, (16.5,-1.4641,2), 180, team2, 2)
        self.rooms[room.name] = room
        self.rooms["lower_stairs_3"] = Hallway("lower_stairs_3", self.parent,
                    (16.5,2,0),(180,0,0),(0.5,2,0.5), team2, 30)
        
        #Bathroom area
        room = StandardHall(self.parent, (15.5,2,z), 180, 1.5, team2)
        self.rooms[room.name] = room
        room = StandardIntersection(self.parent, (15,-1.5,z), 270, team2, 3)
        self.rooms[room.name] = room
        self.rooms["womens_room"] = CubeRoom("womens_room", self.parent, (9, 0, z),
                    (0,0,0), (2.0, 1.0, 1.0), team2, (0,0,0,25,0,0,0,0))
        
        #Below (and left of) bathroom
        room = StandardHall(self.parent, (15.5,-2,z), 180, 0.5, team2)
        self.rooms[room.name] = room
        room = StandardIntersection(self.parent, (15.5,-3,z), 180, team2, 2)
        self.rooms[room.name] = room
        room = StandardHall(self.parent, (16,-3.5,z), 270, 1.0, team2)
        self.rooms[room.name] = room
        room = StandardIntersection(self.parent, (18,-3.5,z), 270, team2, 3)
        self.rooms[room.name] = room
        
        self.rooms["room_101"] = CubeRoom("room_101", self.parent, (21, 0, z),
                    (0,0,0), 1.0, team2, (0,0,50,0,0,0,0,0))
        self.bases[team2] = self.rooms["room_101"]
        
        room = StandardHall(self.parent, (18.5,-4,z), 180, 0.5, team2)
        self.rooms[room.name] = room
        self.rooms["room_103"] = CubeRoom("room_103", self.parent, (21, -7.4, z),
                    (0,0,0), (1.0, 0.8, 1.0), team2, (1,0,0,0,0,0,0,0))
        
        #upper hallway (RA room area)
        room = StandardHall(self.parent, (6,3.5,z), 270, 4.5, team1)
        self.rooms[room.name] = room
        room = StandardIntersection(self.parent, (5.5,4,z), 180, team1, 3)
        self.rooms[room.name] = room
        room = StandardHall(self.parent, (3,3.5,z), 270, 1.0, team1)
        self.rooms[room.name] = room
        #TODO - the turn
        #************* End of Symmetry *************