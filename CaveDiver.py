# Version 7
"""This takes a MineCraft level and opens its caves.

Instead of shoving the landscape around, it finds existing underground
cave systems near the player, then:
- cuts hillside cave mouths into caves that already sit close to the surface
- digs procedural access shafts down to deeper systems
- tunnels between nearby cave systems that do not already connect

Import and call main(the_map, origin=..., **settings) to use as a module;
main does not save. standalone() loads, runs, and writes.

Written by Paul Spooner, with God's help.
See more at: http://www.peripheralarbor.com/minecraft/minecraftscripts.html
"""

# Here are the variables you can edit.

# This is the name of the map to edit.
# Make a backup if you are experimenting!
LOAD_NAME = "TestB"

# Work is centered on the player's location.

# How large an area do you want to search for caves?
# for example, RADIUS = 10 will search a circular area 20 blocks wide.
# Larger values find more caves, and take longer.
# Default 48
RADIUS = 48

# How many hillside cave mouths do you want to open?
# These are sloping openings cut into hillsides that lead into
# shallow cave systems nearby.
# Set to 0 to skip mouths entirely.
MOUTH_COUNT = 4

# How many access shafts do you want to dig?
# Shafts drop from the surface down to deeper cave systems that
# did not get a mouth (or are too deep for one).
# Set to 0 to skip shafts entirely.
SHAFT_COUNT = 3

# How many underground connections do you want to dig?
# Nearby but separate cave systems will be joined by winding tunnels.
# Set to 0 to skip connections entirely.
CONNECT_COUNT = 6

# How wide should the dug passages be?
# This is a radius. Comfortable walking is about 1.5 to 2.
# Examples:
# 1.0 is a tight crawl
# 1.618 is a comfortable player-sized tunnel (default)
# 2.5 is a spacious passage
TUNNEL_RADIUS = 1.618

# How wide should cave mouths be at the opening?
# Should generally be a little larger than TUNNEL_RADIUS.
# Default 2.618
MOUTH_RADIUS = 2.618

# What style of access shaft?
# "winding" a sloping, wandering tunnel
# "spiral" a corkscrew descent
# "stair" a stepped passage that drops slowly
# "drop" a mostly vertical shaft with landings
# "procedural" picks among the above based on how deep the cave is
SHAFT_STYLE = "procedural"

# Do you want ladders in the steep parts of shafts?
# True place ladders on one wall of vertical drops (default)
# False never place ladders
LADDERS = True

#####################
# Advanced options! #
#####################

# The following is an interface class for .mclevel data for minecraft savefiles.
# The following also includes a useful coordinate to index convertor and several
# other useful functions.

import mcInterface
from random import random, choice
from math import sqrt, sin, cos, pi


# How far apart should cave samples be, in the x and z directions?
# Smaller values find thinner caves, and take longer.
# 2 is thorough, 4 is faster, 3 is a decent balance.
# Default 3
SAMPLE_SPACING = 3

# How far apart should cave samples be vertically?
# 1 will not miss thin caves. 2 is faster and still pretty good.
# Default 2
SAMPLE_Y = 2

# Ignore air pockets smaller than this many sample points.
# Filters out tiny gaps and single-block holes.
# Default 6
MIN_CAVE_SIZE = 6

# How close to the surface can a cave be and still get a mouth?
# If the cave ceiling is deeper than this, a shaft is used instead.
# Default 14
MOUTH_MAX_DEPTH = 14

# How steep must the hillside be to qualify for a cave mouth?
# This is rise-over-run of the surface.
# 0.0 would allow mouths on flat ground (they look like sinkholes).
# 0.25 needs a modest slope. 0.5 wants a real hillside.
# Default 0.25
MOUTH_MIN_SLOPE = 0.25

# How far below the surface should a cave be before it gets a shaft?
# Shallower than this, and a mouth is preferred.
# Default 10
SHAFT_MIN_DEPTH = 10

# Refuse to dig a shaft deeper than this.
# The shaft will target the upper part of a deep system instead.
# Default 96
SHAFT_MAX_DEPTH = 96

# How far apart may two cave systems be and still get a connecting tunnel?
# Distance is measured between representative points in each system.
# Default 40
CONNECT_RANGE = 40

# How much stone cover should underground tunnels keep?
# Connecting tunnels will be pushed down to stay at least this far
# below the surface, so they do not break through as random holes.
# Default 5
MIN_COVER = 5

# How twisty should the dug passages be?
# 0.0 is a straight line.
# 0.382 is a gentle wander.
# 0.618 is quite snaky (default).
# 1.0 is drunken.
WANDER = 0.618

# How far apart should shaft landings be, for "drop" style shafts?
# Default 8
LANDING_SPACING = 8

# Minimum distance between mouths and shaft tops, so they do not clump.
# Default 16
MIN_FEATURE_SPACING = 16

# How many times do you want to try to find a good site?
# It will stop searching after MAX_TRIES has been exceeded.
# Default 800
MAX_TRIES = 800

# Keep this many blocks of solid ground above a cave sample
# before we believe it is underground (not a ravine or canyon).
# Default 3
MIN_SURFACE_COVER = 3

# Treat flooded caves as cave systems to open and connect?
# True include water-filled caves.
# False ignore water (default). Dry access only.
INCLUDE_WATER_CAVES = False

# Place mouths and shafts under oceans and lakes?
# True allow underwater openings.
# False skip flooded surface columns (default).
ALLOW_UNDERWATER = False

# Seal off lava so new passages do not dump you into a lake of it?
# True replace neighboring lava with cobble / cobbled deepslate (default).
# False carve blindly. Brave, but toasty.
SEAL_LAVA = True

# Scatter moss, rubble, and roots around cave mouths?
# True makes the openings look like they belong there (default).
# False leaves bare cut stone.
PLACE_MOSS = True

# Place a torch at each mouth and shaft top?
# True a little light so you can find the opening.
# False no extra lights (default).
LIGHTS = False

# What material should the passages be carved as?
# cave_air looks like a natural cave. air is fine too.
CARVE_INFO = {"B": "minecraft:cave_air"}
SURFACE_CARVE_INFO = {"B": "minecraft:air"}

# What should lava seals be made of?
SEAL_INFO = {"B": "minecraft:cobblestone"}
DEEP_SEAL_INFO = {"B": "minecraft:cobbled_deepslate"}

# Ladder block. The facing is filled in when placed.
LADDER_INFO = {"B": "minecraft:ladder", "facing": "west"}

# Light block, if LIGHTS is True.
LIGHT_INFO = {"B": "minecraft:torch"}

# What blocks should never be carved away?
PROTECTED_BLOCKS = (
    "bedrock", "barrier",
    "command_block", "chain_command_block", "repeating_command_block",
    "structure_block", "jigsaw",
    "spawner", "trial_spawner",
    "chest", "ender_chest", "trapped_chest", "barrel",
    "end_portal", "end_portal_frame", "end_gateway",
    "budding_amethyst", "reinforced_deepslate",
    "ancient_debris", "nether_portal",
)

# Do you want lots of text telling you what is going on?
# True lots of text. Good for debugging. Waits at the end.
# False less text, a little faster.
VERBOSE = False

# Do you want to hear about each mouth, shaft, and connection?
# True some text describing each feature.
# False no text for individual features.
VERBOSEINDIVIDUALS = False

##############################################################
#  Don't edit below here unless you know what you are doing  #
##############################################################

def _validate():
    global RADIUS, MOUTH_COUNT, SHAFT_COUNT, CONNECT_COUNT, TUNNEL_RADIUS
    global MOUTH_RADIUS, SHAFT_STYLE, SAMPLE_SPACING, SAMPLE_Y, MIN_CAVE_SIZE
    global MOUTH_MAX_DEPTH, MOUTH_MIN_SLOPE, SHAFT_MIN_DEPTH, SHAFT_MAX_DEPTH
    global CONNECT_RANGE, MIN_COVER, WANDER, LANDING_SPACING
    global MIN_FEATURE_SPACING, MAX_TRIES, MIN_SURFACE_COVER, LADDERS
    global INCLUDE_WATER_CAVES, ALLOW_UNDERWATER, SEAL_LAVA, PLACE_MOSS
    global LIGHTS, VERBOSE, VERBOSEINDIVIDUALS
    RADIUS = int(RADIUS)
    if RADIUS < 8:
        if VERBOSE:
            print("RADIUS is too small, setting it to 8")
        RADIUS = 8
    MOUTH_COUNT = int(MOUTH_COUNT)
    if MOUTH_COUNT < 0:
        MOUTH_COUNT = 0
    SHAFT_COUNT = int(SHAFT_COUNT)
    if SHAFT_COUNT < 0:
        SHAFT_COUNT = 0
    CONNECT_COUNT = int(CONNECT_COUNT)
    if CONNECT_COUNT < 0:
        CONNECT_COUNT = 0
    if TUNNEL_RADIUS < 1.0:
        TUNNEL_RADIUS = 1.0
    if MOUTH_RADIUS < TUNNEL_RADIUS:
        MOUTH_RADIUS = TUNNEL_RADIUS
    if SHAFT_STYLE not in ("winding", "spiral", "stair", "drop", "procedural"):
        if VERBOSE:
            print("SHAFT_STYLE not set correctly, using 'procedural'.")
        SHAFT_STYLE = "procedural"
    if SAMPLE_SPACING < 1:
        SAMPLE_SPACING = 1
    if SAMPLE_Y < 1:
        SAMPLE_Y = 1
    if MIN_CAVE_SIZE < 1:
        MIN_CAVE_SIZE = 1
    if MOUTH_MAX_DEPTH < 4:
        MOUTH_MAX_DEPTH = 4
    if MOUTH_MIN_SLOPE < 0:
        MOUTH_MIN_SLOPE = 0
    if SHAFT_MIN_DEPTH < 4:
        SHAFT_MIN_DEPTH = 4
    if SHAFT_MAX_DEPTH < SHAFT_MIN_DEPTH:
        SHAFT_MAX_DEPTH = SHAFT_MIN_DEPTH
    if CONNECT_RANGE < 8:
        CONNECT_RANGE = 8
    if MIN_COVER < 2:
        MIN_COVER = 2
    if WANDER < 0:
        WANDER = 0
    if LANDING_SPACING < 4:
        LANDING_SPACING = 4
    if MIN_FEATURE_SPACING < 4:
        MIN_FEATURE_SPACING = 4
    if MAX_TRIES < 10:
        MAX_TRIES = 10
    if MIN_SURFACE_COVER < 1:
        MIN_SURFACE_COVER = 1
    if LADDERS not in (True, False):
        LADDERS = True
    if INCLUDE_WATER_CAVES not in (True, False):
        INCLUDE_WATER_CAVES = False
    if ALLOW_UNDERWATER not in (True, False):
        ALLOW_UNDERWATER = False
    if SEAL_LAVA not in (True, False):
        SEAL_LAVA = True
    if PLACE_MOSS not in (True, False):
        PLACE_MOSS = True
    if LIGHTS not in (True, False):
        LIGHTS = False
    if VERBOSE not in (True, False):
        VERBOSE = False
    if VERBOSEINDIVIDUALS not in (True, False):
        VERBOSEINDIVIDUALS = False

_validate()

# Map height limits
# gets clobbered from the map height data on map import
MAPTOP = mcInterface.SaveFile.map_height
MAPBTM = mcInterface.SaveFile.map_bottom

# This is the end of the MCLevel interface.

# Now, on to the actual code.

AIR_BLOCKS = ("air", "cave_air", "void_air", "light")
WATER_BLOCKS = ("water", "flowing_water", "bubble_column", "kelp",
                "kelp_plant", "seagrass", "tall_seagrass")
LAVA_BLOCKS = ("lava", "flowing_lava")
RUBBLE_CHOICES = (
    {"B": "minecraft:cobblestone"},
    {"B": "minecraft:mossy_cobblestone"},
    {"B": "minecraft:gravel"},
    {"B": "minecraft:moss_block"},
)
MOSS_CARPET = {"B": "minecraft:moss_carpet"}
HANGING_ROOTS = {"B": "minecraft:hanging_roots"}
NEIGHBOR_6 = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
LADDER_OFFSETS = (
    (1, 0, "west"),
    (-1, 0, "east"),
    (0, 1, "north"),
    (0, -1, "south"),
)


def blockstr(block_data):
    """Return the bare block name, or None if there is no block."""
    if block_data is None:
        return None
    return block_data["B"].replace("minecraft:", "")


def is_cave_space(name):
    """True if this block counts as open cave."""
    if name is None:
        return False
    if name in AIR_BLOCKS:
        return True
    if INCLUDE_WATER_CAVES and name in WATER_BLOCKS:
        return True
    return False


def is_protected(name):
    """True if this block must not be carved."""
    if name is None:
        return True
    return name in PROTECTED_BLOCKS


def assign_value(x, y, z, values, save_file):
    """Assign a block to a location in mcmap.

    If the index is outside the bounds of the map, return None.
    If the assignment succeeds, return True.
    """
    result = save_file.set_block(x, y, z, values)
    return result


def surface_air_y(mcmap, x, z):
    """Return the heightmap Y (first air above solid) at x, z."""
    hmnl = mcmap.get_heightmap(x, z, "MOTION_BLOCKING_NO_LEAVES")
    hmof = mcmap.get_heightmap(x, z, "OCEAN_FLOOR")
    if (hmnl is None) or (hmof is None):
        return None
    return min(hmnl, hmof)


def solid_surface_y(mcmap, x, z):
    """Return the Y of the highest solid-ish surface block at x, z."""
    air_y = surface_air_y(mcmap, x, z)
    if air_y is None:
        return None
    return air_y - 1


def is_underwater(mcmap, x, z):
    """True if this column has a body of water on the surface."""
    ws = mcmap.get_heightmap(x, z, "WORLD_SURFACE")
    of = mcmap.get_heightmap(x, z, "OCEAN_FLOOR")
    if (ws is None) or (of is None):
        return False
    return (ws - of) > 3


def vec_len(v):
    return sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)


def vec_norm(v):
    length = vec_len(v)
    if length < 1e-9:
        return [0.0, 1.0, 0.0]
    return [v[i] / length for i in range(3)]


def vec_cross(a, b):
    return [a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]]


def dist3(a, b):
    return sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)


def dist2(a, b):
    return sqrt((a[0] - b[0]) ** 2 + (a[2] - b[2]) ** 2)


class BlockCache(object):
    """Memoize block name lookups while scanning the map."""

    def __init__(self, mcmap):
        self.mcmap = mcmap
        self.cache = {}
        self._block = mcmap.block

    def name(self, x, y, z):
        key = (x, y, z)
        cached = self.cache.get(key, 0)
        if cached != 0:
            return cached
        info = self._block(x, y, z)
        name = blockstr(info)
        self.cache[key] = name
        return name


def find_floor(mcmap, x, y, z, limit=8):
    """Find a solid floor at or below y. Return the walk-center Y."""
    get_block = mcmap.block
    for depth in range(limit + 1):
        cy = y - depth
        if cy <= MAPBTM:
            break
        info = get_block(x, cy, z)
        name = blockstr(info)
        if name is None:
            break
        if not is_cave_space(name) and name not in WATER_BLOCKS:
            # stand two blocks above the solid floor
            return min(cy + 2, y)
    return y


def surface_gradient(mcmap, x, z, span=3):
    """Return (slope magnitude, downhill unit vector) of the surface."""
    h = solid_surface_y(mcmap, x, z)
    hx1 = solid_surface_y(mcmap, x + span, z)
    hx0 = solid_surface_y(mcmap, x - span, z)
    hz1 = solid_surface_y(mcmap, x, z + span)
    hz0 = solid_surface_y(mcmap, x, z - span)
    if None in (h, hx1, hx0, hz1, hz0):
        return 0.0, [0.0, -1.0, 0.0]
    dx = (hx1 - hx0) / float(2 * span)
    dz = (hz1 - hz0) / float(2 * span)
    mag = sqrt(dx * dx + dz * dz)
    if mag < 0.01:
        return mag, [0.0, -1.0, 0.0]
    # downhill in xz is opposite the height gradient
    return mag, [-dx / mag, -1.0, -dz / mag]


def perpendiculars(direction):
    """Return two unit vectors perpendicular to direction."""
    d = vec_norm(direction)
    if abs(d[1]) < 0.9:
        up = [0.0, 1.0, 0.0]
    else:
        up = [1.0, 0.0, 0.0]
    p1 = vec_norm(vec_cross(d, up))
    p2 = vec_norm(vec_cross(d, p1))
    return p1, p2


def make_path(start, end, wander=WANDER, downward=False, max_depth=4):
    """Build a winding list of [x,y,z] points from start to end.

    Midpoint displacement, with an optional bias that never climbs
    above the starting Y (used for shafts).
    """
    start = [float(start[0]), float(start[1]), float(start[2])]
    end = [float(end[0]), float(end[1]), float(end[2])]

    def displace(a, b, depth):
        if depth >= max_depth or dist3(a, b) < 4:
            return [a, b]
        mid = [(a[i] + b[i]) * 0.5 for i in range(3)]
        length = dist3(a, b)
        p1, p2 = perpendiculars([b[i] - a[i] for i in range(3)])
        mag = wander * length * (0.5 ** depth)
        offset = (random() - 0.5) * 2.0 * mag
        offset2 = (random() - 0.5) * 2.0 * mag * 0.618
        mid = [mid[i] + p1[i] * offset + p2[i] * offset2 for i in range(3)]
        if downward:
            top = max(a[1], b[1])
            bot = min(a[1], b[1])
            # keep the midpoint between the ends, trending down
            mid[1] = bot + abs(top - bot) * (0.382 + random() * 0.236)
            if mid[1] > top:
                mid[1] = top
        left = displace(a, mid, depth + 1)
        right = displace(mid, b, depth + 1)
        return left[:-1] + right

    raw = displace(start, end, 0)
    points = []
    last = None
    for p in raw:
        ipt = [int(p[0] + 0.5), int(p[1] + 0.5), int(p[2] + 0.5)]
        if ipt != last:
            points.append(ipt)
            last = ipt
    if not points:
        points = [[int(start[i] + 0.5) for i in range(3)],
                  [int(end[i] + 0.5) for i in range(3)]]
    return points


def spiral_path(start, end, radius=4.0):
    """A corkscrew of points from start down to end."""
    dy = max(1.0, abs(start[1] - end[1]))
    turns = max(1.0, dy / 8.0)
    n = max(int(dy), 8)
    points = []
    last = None
    phase = random() * 2 * pi
    for i in range(n + 1):
        t = i / float(n)
        ang = phase + t * turns * 2 * pi
        r = radius * (1.0 - 0.236 * t)
        x = (1 - t) * start[0] + t * end[0] + r * sin(ang)
        z = (1 - t) * start[2] + t * end[2] + r * cos(ang)
        y = (1 - t) * start[1] + t * end[1]
        ipt = [int(x + 0.5), int(y + 0.5), int(z + 0.5)]
        if ipt != last:
            points.append(ipt)
            last = ipt
    return points


def stair_path(start, end):
    """A stepped descent: drop one block of Y per two steps of travel."""
    x0, y0, z0 = [float(c) for c in start]
    x1, y1, z1 = [float(c) for c in end]
    dy = y0 - y1
    horiz = sqrt((x1 - x0) ** 2 + (z1 - z0) ** 2)
    needed = max(horiz, dy * 2.0, 4.0)
    n = int(needed + 0.5)
    # if the ends are too close horizontally, sweep in a wide arc
    sweep = 0.0
    if horiz < dy:
        sweep = max(3.0, dy * 0.25)
    points = []
    last = None
    phase = random() * 2 * pi
    for i in range(n + 1):
        t = i / float(n)
        ang = phase + t * pi
        x = (1 - t) * x0 + t * x1 + sweep * sin(ang) * sin(t * pi)
        z = (1 - t) * z0 + t * z1 + sweep * cos(ang) * sin(t * pi)
        y = y0 + (y1 - y0) * t
        ipt = [int(x + 0.5), int(y + 0.5), int(z + 0.5)]
        if ipt != last:
            points.append(ipt)
            last = ipt
    return points


def drop_path(start, end):
    """Mostly vertical, with a little wander and regular landings."""
    points = []
    last = None
    y_top = int(start[1])
    y_bot = int(end[1])
    if y_bot > y_top:
        y_top, y_bot = y_bot, y_top
    n = max(1, y_top - y_bot)
    wander_x = 0.0
    wander_z = 0.0
    for i in range(n + 1):
        t = i / float(n)
        y = int(y_top + (y_bot - y_top) * t + 0.5)
        if i > 0 and i % LANDING_SPACING == 0:
            wander_x += choice((-2, -1, 1, 2))
            wander_z += choice((-2, -1, 1, 2))
        x = (1 - t) * start[0] + t * end[0] + wander_x
        z = (1 - t) * start[2] + t * end[2] + wander_z
        ipt = [int(x + 0.5), y, int(z + 0.5)]
        if ipt != last:
            points.append(ipt)
            last = ipt
    if not points:
        points = [[int(start[i] + 0.5) for i in range(3)],
                  [int(end[i] + 0.5) for i in range(3)]]
    return points


def keep_path_covered(points, mcmap, cover=MIN_COVER):
    """Push any point that would break the surface back underground."""
    covered = []
    for p in points:
        x, y, z = p
        air_y = surface_air_y(mcmap, x, z)
        if air_y is None:
            continue
        max_y = air_y - cover
        if y > max_y:
            y = max_y
        if y < MAPBTM + 2:
            y = MAPBTM + 2
        covered.append([x, y, z])
    return covered


def carve_block(mcmap, x, y, z, at_surface=False):
    """Carve one block to air, sealing lava and skipping protected blocks."""
    if y > MAPTOP or y < MAPBTM:
        return None
    info = mcmap.block(x, y, z)
    name = blockstr(info)
    if name is None:
        return None
    if is_protected(name):
        return None
    if name in AIR_BLOCKS and not at_surface:
        # already open underground; still may need a lava seal around it
        pass
    else:
        mat = SURFACE_CARVE_INFO if at_surface else CARVE_INFO
        if name not in AIR_BLOCKS:
            assign_value(x, y, z, mat, mcmap)
            air_y = surface_air_y(mcmap, x, z)
            if air_y is not None and y >= air_y - 2:
                mcmap.decrease_all_heightmaps(x, y, z)
    if SEAL_LAVA:
        get_block = mcmap.block
        for dx, dy, dz in NEIGHBOR_6:
            nx, ny, nz = x + dx, y + dy, z + dz
            ninfo = get_block(nx, ny, nz)
            nname = blockstr(ninfo)
            if nname in LAVA_BLOCKS:
                seal = DEEP_SEAL_INFO if ny < 0 else SEAL_INFO
                assign_value(nx, ny, nz, seal, mcmap)
    return True


def crossection(center, radius, diraxis, mcmap):
    """Carve a round section of air, perpendicular to diraxis.

    diraxis: 0 is x, 1 is y, 2 is z.
    """
    rad = int(radius + 0.618)
    if rad < 1:
        rad = 1
    secidx1 = (diraxis - 1) % 3
    secidx2 = (1 + diraxis) % 3
    coord = [0, 0, 0]
    air_y = surface_air_y(mcmap, int(center[0]), int(center[2]))
    for off1 in range(-rad, rad + 1):
        for off2 in range(-rad, rad + 1):
            thisdist = sqrt((abs(off1) + 0.5) ** 2 + (abs(off2) + 0.5) ** 2)
            if thisdist > radius:
                continue
            coord[diraxis] = center[diraxis]
            coord[secidx1] = center[secidx1] + off1
            coord[secidx2] = center[secidx2] + off2
            x, y, z = int(coord[0]), int(coord[1]), int(coord[2])
            at_surface = (air_y is not None) and (y >= air_y - 2)
            carve_block(mcmap, x, y, z, at_surface=at_surface)


def taperedcylinder(start, end, startsize, endsize, mcmap):
    """Carve a tapered cylinder of air from start to end."""
    delta = [int(end[i] - start[i]) for i in range(3)]
    maxdist = max(delta, key=abs)
    if maxdist == 0:
        crossection(start, max(startsize, endsize), 1, mcmap)
        return None
    primidx = delta.index(maxdist)
    secidx1 = (primidx - 1) % 3
    secidx2 = (1 + primidx) % 3
    primsign = int(delta[primidx] / abs(delta[primidx]))
    secfac1 = float(delta[secidx1]) / delta[primidx]
    secfac2 = float(delta[secidx2]) / delta[primidx]
    coord = [0, 0, 0]
    endoffset = delta[primidx] + primsign
    primdist = abs(delta[primidx])
    for primoffset in range(0, endoffset, primsign):
        coord[primidx] = start[primidx] + primoffset
        coord[secidx1] = int(start[secidx1] + primoffset * secfac1)
        coord[secidx2] = int(start[secidx2] + primoffset * secfac2)
        radius = endsize + (startsize - endsize) * abs(delta[primidx] - primoffset) / primdist
        # a little irregularity so it does not look drilled
        radius *= 0.9 + random() * 0.2
        if radius < 1.0:
            radius = 1.0
        crossection(coord, radius, primidx, mcmap)


def carve_sphere(center, radius, mcmap):
    """Carve a rough sphere of air around center."""
    r = int(radius + 0.618)
    r2 = radius * radius
    cx, cy, cz = int(center[0]), int(center[1]), int(center[2])
    air_y = surface_air_y(mcmap, cx, cz)
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if dx * dx + dy * dy + dz * dz > r2:
                    continue
                y = cy + dy
                at_surface = (air_y is not None) and (y >= air_y - 2)
                carve_block(mcmap, cx + dx, y, cz + dz, at_surface=at_surface)


def carve_along_path(points, startsize, endsize, mcmap):
    """Carve overlapping cylinders along a list of points."""
    if not points:
        return 0
    if len(points) == 1:
        carve_sphere(points[0], startsize, mcmap)
        return 1
    n = len(points) - 1
    carved = 0
    for i in range(n):
        t0 = i / float(n)
        t1 = (i + 1) / float(n)
        r0 = startsize + (endsize - startsize) * t0
        r1 = startsize + (endsize - startsize) * t1
        a = points[i]
        b = points[i + 1]
        if a[0] == b[0] and a[1] == b[1] and a[2] == b[2]:
            continue
        taperedcylinder(a, b, r0, r1, mcmap)
        carved += 1
    return carved


def place_ladder_column(mcmap, points):
    """Put ladders on one wall of the steep parts of a path."""
    if not LADDERS or len(points) < 2:
        return 0
    dx, dz, facing = choice(LADDER_OFFSETS)
    placed = 0
    get_block = mcmap.block
    for i, p in enumerate(points):
        # skip shallow, mostly-horizontal stretches
        if i + 1 < len(points):
            if abs(points[i + 1][1] - p[1]) < 1 and dist2(p, points[i + 1]) > 1.5:
                continue
        x, y, z = p[0] + dx, p[1], p[2] + dz
        # the ladder sits in air, attached to a solid block further out
        wall = get_block(x + dx, y, z + dz)
        wall_name = blockstr(wall)
        if wall_name is None or is_cave_space(wall_name) or wall_name in WATER_BLOCKS:
            continue
        if is_protected(wall_name):
            continue
        here = get_block(x, y, z)
        here_name = blockstr(here)
        if here_name is not None and not is_cave_space(here_name):
            continue
        info = LADDER_INFO.copy()
        info["facing"] = facing
        assign_value(x, y, z, info, mcmap)
        placed += 1
    return placed


def decorate_mouth(mcmap, opening, downhill):
    """Scatter rubble, moss, and hanging roots around a cave mouth."""
    if not PLACE_MOSS and not LIGHTS:
        return None
    ox, oy, oz = int(opening[0]), int(opening[1]), int(opening[2])
    get_block = mcmap.block
    # a handful of spots around the opening, biased downhill / outside
    for _ in range(14):
        rx = ox + int((random() - 0.35) * 5 + downhill[0] * 2)
        rz = oz + int((random() - 0.35) * 5 + downhill[2] * 2)
        floor = solid_surface_y(mcmap, rx, rz)
        if floor is None:
            continue
        if PLACE_MOSS and random() < 0.618:
            above = get_block(rx, floor + 1, rz)
            above_name = blockstr(above)
            if above_name in AIR_BLOCKS or above_name is None:
                if random() < 0.5:
                    assign_value(rx, floor, rz, choice(RUBBLE_CHOICES), mcmap)
                else:
                    assign_value(rx, floor + 1, rz, MOSS_CARPET, mcmap)
        if PLACE_MOSS and random() < 0.3:
            # hanging roots under a dirt-ish ceiling near the mouth
            cx = ox + int((random() - 0.5) * 4)
            cz = oz + int((random() - 0.5) * 4)
            cy = oy + int(random() * 3)
            ceiling = get_block(cx, cy, cz)
            below = get_block(cx, cy - 1, cz)
            cname = blockstr(ceiling)
            bname = blockstr(below)
            if cname in mcInterface.blocktype_soils and bname in AIR_BLOCKS:
                assign_value(cx, cy - 1, cz, HANGING_ROOTS, mcmap)
    if LIGHTS:
        # torch on a wall just inside
        wx = ox - int(downhill[0] * 2)
        wz = oz - int(downhill[2] * 2)
        assign_value(wx, oy, wz, LIGHT_INFO, mcmap)
    return True


class UnionFind(object):
    """Disjoint set of sample points, used to cluster cave air."""

    def __init__(self):
        self.parent = {}
        self.rank = {}

    def add(self, x):
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0

    def find(self, x):
        parent = self.parent
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return None
        if self.rank[ra] < self.rank[rb]:
            self.parent[ra] = rb
        elif self.rank[ra] > self.rank[rb]:
            self.parent[rb] = ra
        else:
            self.parent[rb] = ra
            self.rank[ra] += 1


class CaveSystem(object):
    """A cluster of underground air samples.

    Designed as a bag of points plus a few cached stats, similar in
    spirit to how Forester keeps a Tree around before carving it.
    """

    def __init__(self, points):
        self.points = points
        n = float(len(points))
        self.centroid = [
            int(sum(p[i] for p in points) / n + 0.5)
            for i in range(3)
        ]
        self.highest = max(points, key=lambda p: p[1])
        self.lowest = min(points, key=lambda p: p[1])
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        zs = [p[2] for p in points]
        self.reps = [
            self.centroid,
            self.highest,
            self.lowest,
            (min(xs), self.centroid[1], self.centroid[2]),
            (max(xs), self.centroid[1], self.centroid[2]),
            (self.centroid[0], self.centroid[1], min(zs)),
            (self.centroid[0], self.centroid[1], max(zs)),
        ]
        self.has_mouth = False
        self.has_shaft = False

    def nearest_rep(self, other):
        """Return (distance, self_point, other_point) for the closest reps."""
        best = None
        for a in self.reps:
            for b in other.reps:
                d = dist3(a, b)
                if best is None or d < best[0]:
                    best = (d, a, b)
        return best


class CaveFeature(object):
    """Set up the interface for cave access features. Designed for subclassing."""

    def prepare(self, mcmap):
        """Build the path and any extra geometry."""
        return None

    def carve(self, mcmap):
        """Carve the feature into mcmap."""
        return 1

    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.path = []


class CaveMouth(CaveFeature):
    """A sloping hillside opening that leads into a shallow cave."""

    def __init__(self, opening, cave_point, downhill):
        CaveFeature.__init__(self, opening, cave_point)
        self.downhill = downhill
        self.opening_radius = MOUTH_RADIUS

    def prepare(self, mcmap):
        start = list(self.start)
        end = list(self.end)
        end[1] = find_floor(mcmap, end[0], end[1], end[2])
        # a mid point just inside the hill, slightly down
        mid = [
            int((start[0] * 0.382 + end[0] * 0.618) + 0.5),
            int((start[1] * 0.618 + end[1] * 0.382) + 0.5),
            int((start[2] * 0.382 + end[2] * 0.618) + 0.5),
        ]
        inward = make_path(start, mid, wander=WANDER * 0.5, downward=True, max_depth=3)
        inner = make_path(mid, end, wander=WANDER * 0.382, downward=True, max_depth=3)
        self.path = inward[:-1] + inner
        if not self.path:
            self.path = [start, end]
        return len(self.path)

    def carve(self, mcmap):
        # flare the opening, then taper to a walking tunnel
        carve_sphere(self.start, self.opening_radius, mcmap)
        carve_along_path(self.path, self.opening_radius, TUNNEL_RADIUS, mcmap)
        carve_sphere(self.end, TUNNEL_RADIUS, mcmap)
        decorate_mouth(mcmap, self.start, self.downhill)
        if VERBOSEINDIVIDUALS:
            print("Cave mouth from {0} into {1}".format(self.start, self.end))
        return 1


class AccessShaft(CaveFeature):
    """A procedural shaft from the surface down to a deeper cave."""

    def __init__(self, top, cave_point, style=None):
        CaveFeature.__init__(self, top, cave_point)
        self.style = style or SHAFT_STYLE
        self.landings = []

    def pick_style(self):
        if self.style != "procedural":
            return self.style
        depth = abs(self.start[1] - self.end[1])
        if depth < 16:
            return "winding"
        if depth < 36:
            return choice(("winding", "spiral", "stair"))
        return choice(("spiral", "drop", "stair"))

    def prepare(self, mcmap):
        start = list(self.start)
        end = list(self.end)
        end[1] = find_floor(mcmap, end[0], end[1], end[2])
        self.end = end
        style = self.pick_style()
        self.style = style
        if style == "spiral":
            path = spiral_path(start, end, radius=3.0 + random() * 2.0)
        elif style == "stair":
            path = stair_path(start, end)
        elif style == "drop":
            path = drop_path(start, end)
        else:
            path = make_path(start, end, wander=WANDER, downward=True, max_depth=4)
        # do not punch random skylights on the way down
        self.path = keep_path_covered(path, mcmap, cover=max(2, MIN_COVER - 2))
        if self.path:
            # keep the actual top at the surface so the shaft is enterable
            self.path[0] = [start[0], start[1], start[2]]
            self.path[-1] = [end[0], end[1], end[2]]
        else:
            self.path = [start, end]
        if style == "drop":
            y0 = self.path[0][1]
            self.landings = [p for p in self.path
                             if (y0 - p[1]) > 0 and (y0 - p[1]) % LANDING_SPACING == 0]
        return len(self.path)

    def carve(self, mcmap):
        # a small sinkhole / lip at the top
        carve_sphere(self.start, TUNNEL_RADIUS + 0.6, mcmap)
        carve_along_path(self.path, TUNNEL_RADIUS + 0.2, TUNNEL_RADIUS, mcmap)
        for landing in self.landings:
            carve_sphere(landing, TUNNEL_RADIUS + 0.8, mcmap)
        carve_sphere(self.end, TUNNEL_RADIUS + 0.4, mcmap)
        if self.style in ("drop", "spiral") or abs(self.start[1] - self.end[1]) > 24:
            place_ladder_column(mcmap, self.path)
        if LIGHTS:
            assign_value(self.start[0], self.start[1], self.start[2], LIGHT_INFO, mcmap)
        if VERBOSEINDIVIDUALS:
            print("Access shaft ({0}) from {1} down to {2}".format(
                self.style, self.start, self.end))
        return 1


class CaveConnector(CaveFeature):
    """A winding underground tunnel between two cave systems."""

    def prepare(self, mcmap):
        start = list(self.start)
        end = list(self.end)
        start[1] = find_floor(mcmap, start[0], start[1], start[2])
        end[1] = find_floor(mcmap, end[0], end[1], end[2])
        path = make_path(start, end, wander=WANDER, downward=False, max_depth=4)
        self.path = keep_path_covered(path, mcmap, cover=MIN_COVER)
        if len(self.path) < 2:
            self.path = [start, end]
            self.path = keep_path_covered(self.path, mcmap, cover=MIN_COVER)
        return len(self.path)

    def carve(self, mcmap):
        # slightly roomier at the joins, snug in the middle
        if not self.path:
            return 0
        mid_r = max(1.0, TUNNEL_RADIUS * 0.85)
        n = len(self.path)
        if n < 2:
            carve_sphere(self.path[0], TUNNEL_RADIUS, mcmap)
            return 1
        third = max(1, n // 3)
        carve_along_path(self.path[:third + 1], TUNNEL_RADIUS, mid_r, mcmap)
        carve_along_path(self.path[third:n - third + 1], mid_r, mid_r, mcmap)
        carve_along_path(self.path[n - third:], mid_r, TUNNEL_RADIUS, mcmap)
        if VERBOSEINDIVIDUALS:
            print("Connection from {0} to {1} ({2} steps)".format(
                self.start, self.end, n))
        return 1


def find_caves(mcmap, origin=None):
    """Sample the volume around origin and cluster roofed-in air.

    Returns a list of CaveSystem objects.
    """
    assert isinstance(mcmap, mcInterface.SaveFile)
    origin = mcmap.resolve_origin(origin)
    px, pz = origin[0], origin[2]
    spacing = SAMPLE_SPACING
    rad = int(RADIUS)
    rad_sqr = rad * rad
    x0 = (px - rad) - ((px - rad) % spacing)
    z0 = (pz - rad) - ((pz - rad) % spacing)
    cache = BlockCache(mcmap)
    air_points = []
    if VERBOSE:
        print("Scanning for caves in radius {0}".format(rad))
    columns = 0
    for x in range(x0, px + rad + 1, spacing):
        dx = x - px
        for z in range(z0, pz + rad + 1, spacing):
            if dx * dx + (z - pz) ** 2 > rad_sqr:
                continue
            ground = solid_surface_y(mcmap, x, z)
            if ground is None:
                continue
            columns += 1
            # Walk the column from the surface down. Air only counts as cave
            # after we have passed a solid roof, so ravines and canyons
            # are skipped and the pockets under them are kept.
            seen_roof = False
            for y in range(ground, MAPBTM + 1, -1):
                name = cache.name(x, y, z)
                if name is None:
                    break
                if not is_cave_space(name):
                    seen_roof = True
                    continue
                if (seen_roof
                        and (ground - y) >= MIN_SURFACE_COVER
                        and (y % SAMPLE_Y) == 0):
                    air_points.append((x, y, z))
    if VERBOSE:
        print("Sampled {0} columns, found {1} cave air samples".format(
            columns, len(air_points)))
    if not air_points:
        return []

    point_set = set(air_points)
    uf = UnionFind()
    sx, sy = SAMPLE_SPACING, SAMPLE_Y
    for p in air_points:
        uf.add(p)
        x, y, z = p
        for dx in (-sx, 0, sx):
            for dy in (-sy, 0, sy):
                for dz in (-sx, 0, sx):
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    n = (x + dx, y + dy, z + dz)
                    if n in point_set:
                        uf.add(n)
                        uf.union(p, n)

    groups = {}
    for p in air_points:
        root = uf.find(p)
        groups.setdefault(root, []).append(p)
    systems = []
    for pts in groups.values():
        if len(pts) >= MIN_CAVE_SIZE:
            systems.append(CaveSystem(pts))
    systems.sort(key=lambda s: len(s.points), reverse=True)
    if VERBOSE:
        print("Clustered into {0} cave systems (min size {1})".format(
            len(systems), MIN_CAVE_SIZE))
    return systems


def too_close(pos, taken, spacing):
    """True if pos is within spacing of any xz in taken."""
    for other in taken:
        if dist2(pos, other) < spacing:
            return True
    return False


def mouth_site_for_system(system, mcmap):
    """Pick a hillside opening that can reach this system, or None."""
    # try the highest samples first; they are the ones nearest the surface
    ranked = sorted(system.points, key=lambda p: p[1], reverse=True)
    tries = 0
    best = None
    best_score = -1.0
    for cave in ranked[:24]:
        if tries >= MAX_TRIES:
            break
        cx, cy, cz = cave
        for ox in range(-6, 7, 3):
            for oz in range(-6, 7, 3):
                tries += 1
                sx, sz = cx + ox, cz + oz
                if not ALLOW_UNDERWATER and is_underwater(mcmap, sx, sz):
                    continue
                ground = solid_surface_y(mcmap, sx, sz)
                if ground is None:
                    continue
                depth = ground - cy
                if depth < 3 or depth > MOUTH_MAX_DEPTH:
                    continue
                slope, downhill = surface_gradient(mcmap, sx, sz)
                if slope < MOUTH_MIN_SLOPE:
                    continue
                # opening sits a couple of blocks downhill, at walking height
                open_x = int(sx + downhill[0] * 3 + 0.5)
                open_z = int(sz + downhill[2] * 3 + 0.5)
                open_ground = solid_surface_y(mcmap, open_x, open_z)
                if open_ground is None:
                    continue
                if not ALLOW_UNDERWATER and is_underwater(mcmap, open_x, open_z):
                    continue
                opening = [open_x, open_ground + 2, open_z]
                cave_pt = [cx, find_floor(mcmap, cx, cy, cz), cz]
                score = slope * (1.0 - depth / float(MOUTH_MAX_DEPTH)) * 1.618
                # prefer openings that actually face into the hill toward the cave
                into = (cx - open_x) * (-downhill[0]) + (cz - open_z) * (-downhill[2])
                if into > 0:
                    score += 0.3
                if score > best_score:
                    best_score = score
                    best = (opening, cave_pt, downhill, score)
    return best


def shaft_site_for_system(system, mcmap, origin=None):
    """Pick a surface top and an underground target for a shaft, or None."""
    # aim for a high, roomy-looking sample, but still deep enough
    ranked = sorted(system.points, key=lambda p: p[1], reverse=True)
    origin = mcmap.resolve_origin(origin)
    player = origin
    for cave in ranked[:20]:
        cx, cy, cz = cave
        # search a small neighborhood on the surface for a dry column
        for _ in range(12):
            ox = int((random() - 0.5) * 8)
            oz = int((random() - 0.5) * 8)
            sx, sz = cx + ox, cz + oz
            if not ALLOW_UNDERWATER and is_underwater(mcmap, sx, sz):
                continue
            ground = solid_surface_y(mcmap, sx, sz)
            if ground is None:
                continue
            depth = ground - cy
            if depth < SHAFT_MIN_DEPTH:
                continue
            target_y = cy
            if depth > SHAFT_MAX_DEPTH:
                target_y = ground - SHAFT_MAX_DEPTH
                # make sure we still land in this system, or close
                if target_y - system.lowest[1] < 4:
                    continue
            top = [sx, ground + 1, sz]
            cave_pt = [cx, find_floor(mcmap, cx, target_y, cz), cz]
            # slightly prefer closer to the player
            score = len(system.points) / (1.0 + dist2(top, player) * 0.02)
            return top, cave_pt, score
    return None


def select_mouths(systems, mcmap):
    """Choose up to MOUTH_COUNT hillside mouths, one per system."""
    taken = []
    mouths = []
    scored = []
    for system in systems:
        site = mouth_site_for_system(system, mcmap)
        if site is None:
            continue
        scored.append((site[3], system, site))
    scored.sort(key=lambda t: t[0], reverse=True)
    for _, system, site in scored:
        if len(mouths) >= MOUTH_COUNT:
            break
        opening, cave_pt, downhill, _ = site
        if too_close(opening, taken, MIN_FEATURE_SPACING):
            continue
        mouths.append(CaveMouth(opening, cave_pt, downhill))
        system.has_mouth = True
        taken.append(opening)
    if VERBOSE:
        print("Selected {0} cave mouths".format(len(mouths)))
    return mouths, taken


def select_shafts(systems, mcmap, taken, origin=None):
    """Choose up to SHAFT_COUNT shafts for systems that did not get a mouth."""
    shafts = []
    scored = []
    for system in systems:
        if system.has_mouth:
            continue
        site = shaft_site_for_system(system, mcmap, origin)
        if site is None:
            continue
        top, cave_pt, score = site
        scored.append((score, system, top, cave_pt))
    scored.sort(key=lambda t: t[0], reverse=True)
    for _, system, top, cave_pt in scored:
        if len(shafts) >= SHAFT_COUNT:
            break
        if too_close(top, taken, MIN_FEATURE_SPACING):
            continue
        shafts.append(AccessShaft(top, cave_pt))
        system.has_shaft = True
        taken.append(top)
    if VERBOSE:
        print("Selected {0} access shafts".format(len(shafts)))
    return shafts


def select_connections(systems):
    """Kruskal-style tunnels between nearby cave systems."""
    if CONNECT_COUNT <= 0 or len(systems) < 2:
        return []
    edges = []
    n = len(systems)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = systems[i], systems[j]
            # cheap reject on centroids
            if dist3(a.centroid, b.centroid) > CONNECT_RANGE + 24:
                continue
            nearest = a.nearest_rep(b)
            if nearest is None:
                continue
            d, pa, pb = nearest
            if d < 4 or d > CONNECT_RANGE:
                continue
            edges.append((d, pa, pb, i, j))
    edges.sort(key=lambda t: t[0])
    uf = UnionFind()
    for i in range(n):
        uf.add(i)
    connectors = []
    for d, pa, pb, i, j in edges:
        if len(connectors) >= CONNECT_COUNT:
            break
        if uf.find(i) == uf.find(j):
            continue
        uf.union(i, j)
        connectors.append(CaveConnector(list(pa), list(pb)))
    if VERBOSE:
        print("Selected {0} underground connections".format(len(connectors)))
    return connectors


def configure(**settings):
    """Permanently set this script's options (the uppercase names above)."""
    mcInterface.apply_settings(globals(), settings)


def main(the_map, origin=None, **settings):
    """Find caves, open mouths and shafts, and connect systems.

    Runs on an open save. Does not load or save.
    origin: None (player), (x, z), or (x, y, z)
    **settings: temporary overrides for this call, restored afterward
    Returns a dict with origin and feature counts.
    """
    with mcInterface.temporary_settings(globals(), settings):
        origin = the_map.resolve_origin(origin)
        if VERBOSE:
            print("Surveying cave systems")
        systems = find_caves(the_map, origin)
        if not systems:
            print("No cave systems found in radius {0}. Nothing to do.".format(RADIUS))
            print("Try a larger RADIUS, a smaller MIN_CAVE_SIZE, or stand over some caves.")
            return {'origin': origin, 'systems': 0, 'mouths': 0, 'shafts': 0, 'connections': 0}

        mouths = []
        shafts = []
        if MOUTH_COUNT:
            if VERBOSE:
                print("Choosing cave mouths")
            mouths, taken = select_mouths(systems, the_map)
        else:
            taken = []
        if SHAFT_COUNT:
            if VERBOSE:
                print("Choosing access shafts")
            shafts = select_shafts(systems, the_map, taken, origin)
        connectors = []
        if CONNECT_COUNT:
            if VERBOSE:
                print("Choosing cave connections")
            connectors = select_connections(systems)

        features = mouths + shafts + connectors
        if not features:
            print("Found {0} cave systems, but no mouths, shafts, or connections to dig.".format(
                len(systems)))
            print("They may already open to the surface, be underwater, or sit too far apart.")
            return {'origin': origin, 'systems': len(systems),
                    'mouths': 0, 'shafts': 0, 'connections': 0}

        if VERBOSE:
            print("Preparing {0} features".format(len(features)))
        for feature in features:
            feature.prepare(the_map)

        if VERBOSE or not VERBOSEINDIVIDUALS:
            print("Carving {0} mouths, {1} shafts, {2} connections".format(
                len(mouths), len(shafts), len(connectors)))
        for feature in features:
            feature.carve(the_map)
        print("Opened {0} mouths, dug {1} shafts, linked {2} cave systems.".format(
            len(mouths), len(shafts), len(connectors)))
        return {'origin': origin, 'systems': len(systems),
                'mouths': len(mouths), 'shafts': len(shafts),
                'connections': len(connectors)}


def standalone():
    """Load the file, do the stuff, and save the new file.
    """
    print("Importing the map")
    try:
        the_map = mcInterface.SaveFile(LOAD_NAME)
    except IOError:
        print("File name invalid or save file otherwise corrupted. Aborting")
        return None
    main(the_map)
    print("Saving the map (takes a bit)")
    if the_map.write():
        print("finished")
    else:
        print("saving went sideways somehow")
    if VERBOSE:
        input("press Enter to close")


if __name__ == "__main__":
    standalone()
