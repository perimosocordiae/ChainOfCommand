import direct.directbase.DirectStart
from direct.task import Task
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import Point3
from pandac.PandaModules import Vec3
from pandac.PandaModules import Filename,Buffer,Shader

class Program(object):

    def __init__(self):
        actor = loader.loadModel("../../models/terminal_window.egg")
        actor.setScale(2.0, 2.0, 2.0)
        actor.setPos(0, 0, 10)
        actor.reparentTo(render)
        
        #Create the intervals needed to spin and expand/contract
        posInterval1 = actor.posInterval(3,
                                    Point3(0, -20, 10),
                                    startPos=Point3(0, 20, 10))
        posInterval2 = actor.posInterval(3,
                                    Point3(0, 20, 10),
                                    startPos=Point3(0, -20, 10))
        
        hprInterval1 = actor.hprInterval(1.5,
                                    Point3(180, 0, 0),
                                    startHpr=Point3(0, 0, 0))
        hprInterval2 = actor.hprInterval(1.5,
                                    Point3(360, 0, 0),
                                    startHpr=Point3(180, 0, 0))
        
        scaleInterval1 = actor.scaleInterval(1.5,
                                    Point3(4.0, 4.0, 4.0),
                                    startScale=Point3(2.0, 2.0, 2.0),
                                    blendType='easeInOut')
        scaleInterval2 = actor.scaleInterval(1.5,
                                    Point3(2.0, 2.0, 2.0),
                                    startScale=Point3(4.0, 4.0, 4.0),
                                    blendType='easeInOut')
        
        #Create and play the sequence that coordinates the intervals  
        flex = Sequence(Parallel(scaleInterval1, hprInterval1),
                             Parallel(scaleInterval2, hprInterval2))
        flex.loop()
        