
import direct.directbase.DirectStart
from direct.task import Task
from direct.actor import Actor
from pandac.PandaModules import Point3
from random import randint
from math import pi, sin, cos

class Agent(object):

    def __init__(self,game):
        self.game = game
        self.health = 100

    def hit(self,amt):
        self.health -= amt/self.shield()

    def is_dead(self):
        return self.health <= 0

    def heal(self,amt):
        self.health += amt

    def shield(self):
        return 1
    def damage(self):
        return 0

