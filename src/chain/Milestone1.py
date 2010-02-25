from direct.interval.IntervalGlobal import *
import direct.directbase.DirectStart
from game import Game
from program import Rm,Chmod

def hit_demo():
    #Cause player to be hit - FOR DEMO PURPOSES ONLY! WHEN ENEMIES CAN
    #ACTUALLY HIT YOU, DELETE THESE LINES
    #Basic idea - if you're hit before it stops flashing, it just
    #continues flashing... this sequence is proof
    Sequence(Wait(2.0), Func(g.players[0].hit),
             Wait(0.4), Func(g.players[0].hit),
             Wait(0.1), Func(g.players[0].hit),
             Wait(0.2), Func(g.players[0].hit),
             Wait(0.2), Func(g.players[0].hit),
             Wait(0.3), Func(g.players[0].hit)).start()

if __name__ == '__main__':
    g = Game(360,12)
    g.add_player('player_1')
    g.add_program(Rm)
    g.add_program(Chmod)
    for _ in range(5):
        g.add_drone()
    run()

