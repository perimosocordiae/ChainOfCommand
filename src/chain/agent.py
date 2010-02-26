

class Agent(object):

    def __init__(self,game):
        self.game = game
        self.health = 100

    def hit(self,amt):
        self.health -= amt/self.shield()
        if self.health <= 0:
            self.die()
    
    def die(self):
        print "Agent is dead"
    
    def is_dead(self):
        return self.health <= 0

    def heal(self,amt):
        self.health += amt

    def shield(self):
        return 1
    def damage(self):
        return 0

