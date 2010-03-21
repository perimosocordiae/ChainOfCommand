from pandac.PandaModules import CollisionNode, CollisionPolygon

class Wall(object):
    #params: Game, Wall ID, parent PathNode, 4 counterclockwise points,
    #        collision mask, tile scale size, HPR rotation of the wall
    def __init__(self, game, name, parent, p1, p2, p3, p4, mask, tileSize=1.0, rotPoint=0):
        self.game = game
        self.name = name
        self.node = parent.attachNewNode(CollisionNode(name))
        self.node.node().addSolid(CollisionPolygon(p1,p2,p3,p4))
        self.node.node().setFromCollideMask(mask)
        self.node.node().setIntoCollideMask(mask)
        vec1 = p2-p1
        vec2 = p4-p1
        self.normal = vec1.cross(vec2)
        #for now, tile size and rotation don't affect this... goal is for this
        #to tessellate the wall with models of the given tileSize
        
    def getNormal(self):
        return self.normal