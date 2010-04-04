import direct.directbase.DirectStart
from direct.task import Task
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import DirectionalLight, VBase4

def doSword(drone):
    drone.setPlayRate(1, 'sword')
    drone.play("sword", fromFrame = 1)

def putAway(drone):
    drone.setPlayRate(-1, 'sword')
    drone.play("sword", fromFrame = 52)

environ = loader.loadModel("models/environment")
environ.reparentTo(render)
environ.setScale(0.25, 0.25, 0.25)
environ.setPos(-8, 42, 0)

drone = Actor.Actor("../../models/cyborg_newer.egg", {"sword": "../../models/cyborg_swing_sword.egg"})
drone.setScale(0.2, 0.2, 0.2)
drone.setPos(0,0,2.5)
drone.setHpr(0,90,0)
drone.reparentTo(render)
#drone.loop("sword")

dlight = DirectionalLight('dlight')
dlight.setColor(VBase4(1, 1, 0.9, 1))
dlnp = drone.attachNewNode(dlight)
dlnp.setHpr(90,-60,60)
drone.setLight(dlnp)

#Unsheathe sword, swing 4 times, then sheathe it.
seq = Sequence(drone.actorInterval("sword"),
               drone.actorInterval("sword", startFrame=52, endFrame=76),
               drone.actorInterval("sword", startFrame=52, endFrame=76),
               drone.actorInterval("sword", startFrame=52, endFrame=76),
               drone.actorInterval("sword", startFrame=52, endFrame=1))
seq.loop()

run()
    