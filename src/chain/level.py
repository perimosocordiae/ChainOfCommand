from room import *

class Level(Obstacle):
    def __init__(self):
        self.rooms = {}
        
    def destroy(self):
        for room in self.rooms.itervalues():
            room.destroy()
        self.rooms.clear() 