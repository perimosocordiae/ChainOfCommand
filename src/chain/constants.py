from pandac.PandaModules import BitMask32

#The lowest point imaginable - if below this, you fell!
BOTTOM_OF_EVERYTHING = -100

#masks
DRONE_COLLIDER_MASK = BitMask32.bit(1)
WALL_COLLIDER_MASK = BitMask32.bit(0)
FLOOR_COLLIDER_MASK = BitMask32.bit(4)
DRONE_PUSHER_MASK = BitMask32.bit(2)
PROGRAM_PUSHER_MASK = BitMask32.bit(8)

#gravity-related
GRAVITATIONAL_CONSTANT = -7 # = -9.81 m/s^2 in theory! (not necessarily in computer world, but it's what's familiar)
SAFE_FALL = -300.0 #fall velocity after which damage is induced
FALL_DAMAGE_MULTIPLIER = 0.4 #How much to damage Tron per 1 over safe fall
TERMINAL_VELOCITY = -450.0

#agent-y things
STARTING_HEALTH = 100

MODEL_PATH = "../../models"
TEXTURE_PATH = "../../textures"
COLOR_PATH = "%s/colors"%TEXTURE_PATH
SOUND_PATH = "../../sounds"
NO_GLOW = "%s/no_glow.jpg"%TEXTURE_PATH
USE_GLOW = True

SERVER_TICK = 0.01