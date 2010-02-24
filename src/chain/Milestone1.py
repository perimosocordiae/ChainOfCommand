
import direct.directbase.DirectStart
from game import Game
from program import Rm,Chmod

if __name__ == '__main__':
    g = Game(360,12)
    g.add_player('player_1')
    g.add_program(Rm)
    g.add_program(Chmod)
    for _ in range(5):
        g.add_drone()
    run()
