import math

#window options
DYNAMIC_WINDOW_SCALING = True

#frame view options
FRAME_MARGIN_TOP = 0
FRAME_MARGIN_BOTTOM = 45
FRAME_MARGIN_LEFT = 0
FRAME_MARGIN_RIGHT = 0

#statusbar options
STATUSBAR_HEIGHT = 45

#default main window options
DEFAULT_WINDOW_WIDTH = 512
DEFAULT_WINDOW_HEIGHT = 365

#tiles window options
TILES_MARGIN_LEFT = 5
TILES_MARGIN_TOP = 5

TILES_WINDOW_WIDTH = 1000
TILES_WINDOW_HEIGHT = 600

TILE_LABLE_SIZE = 10

GRID_SIZE = 5

TILE_WIDTH = math.floor((TILES_WINDOW_WIDTH - (GRID_SIZE + 1) * TILES_MARGIN_LEFT)/GRID_SIZE)
TILE_HEIGHT = math.floor((TILES_WINDOW_HEIGHT - (GRID_SIZE + 1) * TILES_MARGIN_TOP)/GRID_SIZE)

def reconfig_tile_geometery(window_width, window_height, grid_size):
    width = math.floor((window_width - (grid_size + 1) * TILES_MARGIN_LEFT) / grid_size)
    height = math.floor((window_height - (grid_size + 1) * TILES_MARGIN_TOP) / grid_size)
    return (width, height)

#Main Window Slider settings

SLIDER_MARGINS = 5
SLIDER_HEIGHT = 10

# overlay settings
ALPHA = 0.2

# classes and lable settings
DEFAULT_COLOR = (0, 255, 0)
CLASS_COLOR_MAPPING = {
    "Green": (0, 255, 0),
    "Red": (0, 0, 255),
    "Blue": (255, 0, 0),
    "Yellow": (0, 255, 255)
}

CONFIGURED_CLASSES = [key for key in CLASS_COLOR_MAPPING.keys()]
CONFIGURED_CLASSES.sort()

TCP_IP = '172.26.72.216'
TCP_PORT = 9001
BUFFER_SIZE = 2048