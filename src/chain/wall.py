from pandac.PandaModules import CollisionNode, CollisionPolygon, CollisionTube, Point3
from constants import MODEL_PATH,WALL_COLLIDER_MASK

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
    
    def destroy(self):
        self.node.removeNode()

class Tower(object):
    
    def __init__(self, parent, x,y,h, scale, tile_size):
        self.tower = loader.loadModel("%s/capacitor.egg"%MODEL_PATH)
        self.tower.reparentTo(parent)
        overall = scale * tile_size
        self.tower.setScale(h * overall / 4, h * overall / 4, h * overall)
        self.tower.setPos(Point3(x,y,0))
        self.tower.setHpr(0,0,0)
        self.towerCollider = parent.attachNewNode(CollisionNode("tower_base"))
        self.towerCollider.node().addSolid(CollisionTube(x, y, 0, x, y, h * overall * 0.8, h * overall / 4))
        self.towerCollider.node().setIntoCollideMask(WALL_COLLIDER_MASK)
        self.towerCollider.node().setFromCollideMask(WALL_COLLIDER_MASK)
    
    def destroy(self):
        self.tower.removeNode()
        self.towerCollider.removeNode()