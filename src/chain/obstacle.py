from pandac.PandaModules import CollisionNode, CollisionPolygon, CollisionTube, Point3, TextureStage
from constants import *

#Basically an abstract base class that provides "destroy"
class Obstacle(object):
    def __init__(self):
        pass
        
    def destroy(self):
        pass

class Wall(Obstacle):
    def __init__(self, name, parent, mask, collisionSolid):
        self.name = name
        self.node = parent.attachNewNode(CollisionNode(name))
        self.node.node().addSolid(collisionSolid)
        self.node.node().setFromCollideMask(mask)
        self.node.node().setIntoCollideMask(mask)
        #for now, tile size and rotation don't affect this... goal is for this
        #to tessellate the wall with models of the given tileSize
        
    def getNormal(self):
        return self.normal
    
    def destroy(self):
        self.node.removeNode()

class QuadWall(Wall):
    #params: Game, Wall ID, parent PathNode, 4 counterclockwise points,
    #        collision mask, tile scale size, HPR rotation of the wall
    def __init__(self, name, parent, p1, p2, p3, p4, mask):
        super(QuadWall, self).__init__(name, parent, mask, CollisionPolygon(p1,p2,p3,p4))
        vec1 = p2-p1
        vec2 = p4-p1
        self.normal = vec1.cross(vec2)

class TriangleWall(Wall):
    def __init__(self, name, parent, p1, p2, p3, mask):
        super(TriangleWall, self).__init__(name, parent, mask, CollisionPolygon(p1,p2,p3))
        vec1 = p2-p1
        vec2 = p3-p1
        self.normal = vec1.cross(vec2)

class LWall(Obstacle):
    def __init__(self, name, parent, p1, p2, p3, p4, mask):
        self.name = name
        p5 = p2 + (p3-p2)*0.5
        p7 = p1 + (p4-p1)*0.5
        p6 = p5 + (p7-p5)*0.5
        p8 = p3 + (p4-p3)*0.5
        self.node1 = parent.attachNewNode(CollisionNode(name))
        self.node1.node().addSolid(CollisionPolygon(p3,p8,p6,p5))
        self.node1.node().setFromCollideMask(mask)
        self.node1.node().setIntoCollideMask(mask)
        
        self.node2 = parent.attachNewNode(CollisionNode(name))
        self.node2.node().addSolid(CollisionPolygon(p1,p2,p5,p7))
        self.node2.node().setFromCollideMask(mask)
        self.node2.node().setIntoCollideMask(mask)
        
    def getNormal(self):
        return self.normal
    
    def destroy(self):
        self.node1.removeNode()
        self.node2.removeNode()
        
class Tower(Obstacle):
    
    def __init__(self, parent, x,y,h):
        self.tower = loader.loadModel("%s/capacitor.bam"%MODEL_PATH)
        self.tower.reparentTo(parent)
        self.tower.setScale(h  / 4, h / 4, h)
        self.tower.setPos(Point3(x,y,0))
        self.tower.setHpr(0,0,0)
        self.towerCollider = parent.attachNewNode(CollisionNode("tower_base"))
        self.towerCollider.node().addSolid(CollisionTube(x, y, 0, x, y, h * 0.8, h / 4))
        self.towerCollider.node().setIntoCollideMask(WALL_COLLIDER_MASK)
        self.towerCollider.node().setFromCollideMask(WALL_COLLIDER_MASK)
    
    def destroy(self):
        self.tower.removeNode()
        self.towerCollider.removeNode()

#A box whose top uses FLOOR_COLLIDER_MASK, and whose sides use WALL_COLLIDER_MASK
class Box(Obstacle):
    #The points represent, in counter-clockwise order (as seen from the top), the
    #bottom of the box.  The last parameter is height of the box 
    def __init__(self, name, parent, p1, p2, p3, p4, h):
        p5 = Point3(p1[0], p1[1], p1[2] + h)
        p6 = Point3(p2[0], p2[1], p2[2] + h)
        p7 = Point3(p3[0], p3[1], p3[2] + h)
        p8 = Point3(p4[0], p4[1], p4[2] + h)
        #Make the 4 walls
        self.wall1 = QuadWall(name + "_wall1", parent,
                          p1, p2, p6, p5, WALL_COLLIDER_MASK)
        self.wall2 = QuadWall(name + "_wall1", parent,
                          p2, p3, p7, p6, WALL_COLLIDER_MASK)
        self.wall3 = QuadWall(name + "_wall1", parent,
                          p3, p4, p8, p7, WALL_COLLIDER_MASK)
        self.wall4 = QuadWall(name + "_wall1", parent,
                          p4, p1, p5, p8, WALL_COLLIDER_MASK)
        #Make the ceiling
        self.ceiling = QuadWall(name + "_ceiling", parent,
                          p5, p6, p7, p8, FLOOR_COLLIDER_MASK)
    
    def destroy(self):
        self.wall1.destroy()
        self.wall2.destroy()
        self.wall3.destroy()
        self.wall4.destroy()
        self.ceiling.destroy()
        
class RAMSlot(Obstacle):
    
    def __init__(self, name, parent, pos, scale, hpr):
        self.slot = loader.loadModel("%s/DDR2_slot.bam"%MODEL_PATH)
        self.slot.reparentTo(parent)
        self.slot.setScale(scale)
        self.slot.setHpr(hpr)
        self.slot.setPos(pos)
        self.colliderBox = Box(name, self.slot, Point3(-7.5, 0.5, 0),
                Point3(-7.5, -0.5, 0), Point3(7.5, -0.5, 0), Point3(7.5, 0.5, 0), 1.0)
    
    def destroy(self):
        self.colliderBox.destroy()
        self.slot.removeNode()

class CopperWire(Obstacle):
    def __init__(self, name, parent, pos, hpr, scale):
        self.wire = loader.loadModel("%s/copper_wire.bam"%MODEL_PATH)
        self.name = name
        ts = TextureStage('ts')
        ts.setMode(TextureStage.MGlow)
        glow = loader.loadTexture("%s/all_glow.jpg"%TEXTURE_PATH)
        self.wire.setTexture(ts, glow)
        self.wire.reparentTo(parent)
        #it's a plane - z scale is erroneous
        self.wire.setScale(scale[0], scale[1], 1.0)
        self.wire.setPos(pos)
        self.wire.setHpr(hpr)
        
    def destroy(self):
        self.wire.removeNode()
        
def make_tile(parent,modelFile,color,pos, hpr=(0,0,0), scale=1.0):
    tile = loader.loadModel("%s/%s"%(MODEL_PATH, modelFile))
    tile.reparentTo(parent)
    tile.setScale(scale)
    tile.setPos(pos)
    tile.setHpr(*hpr)
    if color != "white":
        ts = TextureStage('ts')
        tex = loader.loadTexture("%s/%s1040.jpg"%(COLOR_PATH,color))
        ts.setMode(TextureStage.MModulate)
        tile.setTexture(ts, tex)
    return tile