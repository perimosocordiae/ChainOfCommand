from pandac.PandaModules import BitMask32

#masks
DRONE_COLLIDER_MASK = BitMask32.bit(1)
WALL_COLLIDER_MASK = BitMask32.bit(0)
FLOOR_COLLIDER_MASK = BitMask32.bit(4)
DRONE_PUSHER_MASK = BitMask32.bit(2)
PROGRAM_PUSHER_MASK = BitMask32.bit(8)