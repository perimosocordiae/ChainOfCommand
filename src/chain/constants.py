from pandac.PandaModules import BitMask32

#masks
DRONE_COLLIDER_MASK = BitMask32.bit(1)
WALL_COLLIDER_MASK = BitMask32.bit(0)
FLOOR_COLLIDER_MASK = BitMask32.bit(4)
DRONE_PUSHER_MASK = BitMask32.bit(2)
PROGRAM_PUSHER_MASK = BitMask32.bit(8)

#gravity-related
GRAVITATIONAL_CONSTANT = -35 # = -9.81 m/s^2 in theory! (not necessarily in computer world, but it's what's familiar)
SAFE_FALL = -800.0 #fall velocity after which damage is induced
FALL_DAMAGE_MULTIPLIER = 1.0 #How much to damage Tron per 1 over safe fall
TERMINAL_VELOCITY = -5000.0

#agent-y things
STARTING_HEALTH = 100

MODEL_PATH = "../../models"
SOUND_PATH = "../../sounds"
NO_GLOW = "%s/no_glow.jpg"%MODEL_PATH

SERVER_TICK = 0.01