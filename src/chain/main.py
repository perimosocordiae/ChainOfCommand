from game import Game
from program import Rm,Chmod,Ls
from direct.interval.IntervalGlobal import *


def add_drone(g):
	if len(g.drones) < 20:
		g.add_drone()

if __name__ == '__main__':
    g = Game(360,12,120)
    g.add_player('player_1')
    for _ in range(4):
        g.add_program(Rm)
        g.add_program(Chmod)
        g.add_program(Ls)
    for _ in range(5):
        g.add_drone()
    #g.add_event_handler()
    #g.add_background_music()
    Sequence(Wait(2.0), Func(lambda:add_drone(g))).loop()
    run()