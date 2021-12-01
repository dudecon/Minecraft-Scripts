# Version 8
"""This takes a base MineCraft level and adds boulders and craters.

Written by Paul Spooner, with God's help.
See more at: http://www.peripheralarbor.com/minecraft/minecraftscripts.html
"""

# Here are the variables you can edit.

# This is the name of the map to edit.
# Make a backup if you are experimenting!

LOAD_NAME = "Test"

# How many boulders and/or craters do you want?
FEATURE_NUM = 3

# Where do you want the boulders/craters?
# X, and Z are the map coordinates
X = 260
Z = 163

# How large an area do you want them to be in?
# for example, RADIUS = 10 will place them randomly in
# a circular area 20 blocks wide.
RADIUS = 20
# NOTE: density will be higher in the center than at the edges.

# If you want boulders, set this to True, otherwise, set it to False
# If CRATERS is also True, the boulders will each be sitting in a crater
# defaults to obsidian, change material in the "Advanced options" section
BOULDERS = True

# How big do you want the boulders to be?
BOULDER_SIZE = 7

# How much would you like the size of the boulders to vary?
# This value is a +- value, so with BOULDER_SIZE = 5
# and BOULDER_RANDOMIZATION = 3, the boulder size will range
# from 2 to 8
BOULDER_RANDOMIZATION = 3

# Should boulders occasionally have treasure inside?  Ore, gold, diamond?
# Set to a number between 0 and 1 for some treasure.  Larger numbers creates
# more chance of exotic treasure
# for normal old boulders set to 0
BOULDER_TREASURE = 0.5

# Should the boulders be scattered throughout the level vertically as well?
# Frees the boulders from the surface and makes them appear randomly in the 
# y axis as well.  This can result in boulders underground BURIED_BOULDERS
# or floating in the air FLYING_BOULDERS
# If either is set to true, this will force CRATERS to turn off.
FLYING_BOULDERS = False
BURIED_BOULDERS = False

# If you want craters set this to True, otherwise, set it to False.
# If BOULDERS is set, there will be a boulder in the middle of each crater.
CRATERS = True

# How deep should the craters be?
# Note, deeper is wider, and craters on level ground are generally
# 3 times wider than they are tall
# On uneven ground, however, this may vary
# NOTE: larger values take MUCH longer to process.
CRATER_DEPTH = 10

# How much should the crater size vary?
# same principle as BOULDER_RANDOMIZATION
DEPTH_RANDOMIZATION = 5

#####################
# Advanced options! #
#####################

# What material would you like the boulders to be?
# Uses the minecraft index number.
# Default is 49 (Obsidian)
BOULDER_MAT = 49

# what data value should the boulders have?
# defaults to 0
BOULDER_DATA = 0

# In order, what do you want the common contents of the boulders to be?
# only used when BOULDER_TREASURE is greater than zero
# default: [16,15,14] (coal ore, iron ore, gold ore)
TREASURE_LIST: list[int] = [16, 15, 14]

# A list of the rare contents of boulders.
# The longer TREASURE_LIST is, the less often you will get one of these.
# default: [11,49,41,42,57,56,56,74,89,87]
# (lava, obsidian, gold block, iron block, diamond block,
# diamond ore (2x), redstone ore, glowstone, netherrack) 
TREASURE_RARE: list[int] = [11, 49, 41, 42, 57, 56, 56, 74, 89, 87]

# What size should the crater excavation sphere be?
# A multiple of the crater impact depth.
# Larger values result in wider craters.
# any positive value will work.
# examples:
# 0.5 will make a fully underground sphere hollowed out of the rock.
# 1.0 will make a "crater" cavity that just barely reaches the surface.
# 5.0 makes a pretty decent crater
# 8.0 will make a wide crater
# 100.0 will make a crater so wide, it's not even funny.
# NOTE: okay, maybe a little funny. Heh. Heheh; Such a big crater.
# NOTE: larger values take MUCH longer to process.
# Default 5
CRATER_DEPTH_DIAMETER_MULTIPLE = 5

# Keep track of crater ejecta?
# This option can take a while on larger craters, but looks really cool!
# True displace blocks from inside the crater.
# False merely delete the blocks in the crater.
CRATER_EJECTA = True

# How far should the ejecta be flung?
# This is a multiplier of the crater sphere diameter.
# Examples:
# 0.2 moves the material outward a bit, like hitting mud
# 1.0 makes a nice rim around the crater
# 3.0 scatters the material far and wide, like an explosion
# Default 1.1
EJECTA_DISTANCE = 1.1

# Add surface blocks? How Much? (intended for fire)
# any fractional value works here.
# Examples:
# 0 do not add surface blocks
# 0.1 adds to 1/10th of the blocks (sparse)
# 0.5 adds to half the blocks (thick)
# 1.0 (or more) adds to all of the blocks (complete)
SURFACE_FRACTION = 0

# What block type should the surface blocks be?
# be sure to set SURFACE_FRACTION above as well.
# Default is 51 (fire, makes a flaming crater!)
SURFACE_MAT = 51

# What data value should the surface blocks have?
# defaults to 0
SURFACE_DATA = 0

# Fill the crater with stuff?
# the value is the fraction of the crater depth (at the impact point)
# 0 do not fill the crater
# 0.4 fill the crater almost half full.
# 1.0 fill the crater up to the brim (may overflow on slopes)
# CRATER_DEPTH_DIAMETER_MULTIPLE make a full sphere of fill material
# Default 0 (no fill)
CRATER_FILL = 0.3
# NOTE: fill will be overwritten by ejecta if fill material is
# in the CRATER_DESTROYS list.

# What material should the crater be filled with?
# Defaults to 11 (lava!)
FILL_MAT = 11

# What data value should the fill blocks have?
# defaults to 0
FILL_DATA = 0

# What materials should be ignored by craters?
# These materials will be destroyed rather than displaced.
# a list of material index types.
# default: [0,6,8,9,10,11,18,20,37,38,39,40,50,51,59,90]

CRATER_DESTROYS = [0, 6, 8, 9, 10, 11, 18, 20, 37, 38, 39, 40, 50, 51, 59, 90]

# Do you want something to look at while the script is running?
# True turns on lots of printouts on what the script is doing
# False leaves the extra data out
VERBOSE = False

##############################################################
#  Don't edit below here unless you know what you are doing  #
##############################################################

# input filtering
if FEATURE_NUM < 0:
    print("If you wanted less than one, you wouldn't have run the script.")
    print("Assuming one feature")
    FEATURE_NUM = 1

if BOULDERS:
    if BOULDER_SIZE < 1:
        BOULDER_SIZE = 1
    if BOULDER_RANDOMIZATION < 0:
        BOULDER_RANDOMIZATION = 0
    if BOULDER_RANDOMIZATION > BOULDER_SIZE:
        BOULDER_RANDOMIZATION = BOULDER_SIZE
    if BOULDER_TREASURE < 0:
        BOULDER_TREASURE = 0
    elif BOULDER_TREASURE > 1:
        BOULDER_TREASURE = 1
    if FLYING_BOULDERS or BURIED_BOULDERS:
        CRATERS = False

if CRATERS:
    if CRATER_DEPTH < 1:
        CRATER_DEPTH = 1
    if DEPTH_RANDOMIZATION < 0:
        DEPTH_RANDOMIZATION = 0
    if DEPTH_RANDOMIZATION > CRATER_DEPTH:
        DEPTH_RANDOMIZATION = CRATER_DEPTH

if not (BOULDERS or CRATERS):
    print("wait, you want neither boulders nor craters?")
    print("Um, okay... doing nothing")

# assemble the material dictionaries
BOULDER_INFO = {'B': BOULDER_MAT, 'D': BOULDER_DATA}
SURFACE_INFO = {'B': SURFACE_MAT, 'D': SURFACE_DATA}
FILL_INFO = {'B': FILL_MAT, 'D': FILL_DATA}

MAP_HEIGHT = 256

# The following is an interface class for .mclevel data for minecraft save files.
# The following also includes a useful coordinate to index convertor and several
# other useful functions.

import mcInterface

# This is the end of the MCLevel interface.

# Now, on to the actual code.

from random import random, choice
from math import sqrt, sin, cos, pi


def find_surface(x, y, z, mclevel: mcInterface.SaveFile):
    # move the block up or down until you hit something permeable
    # as defined in CRATER_DESTROYS
    get_block = mclevel.block
    direction = 0
    while True:
        info = get_block(x, y, z)
        if info is None: return None
        if info in CRATER_DESTROYS:
            if direction == 1:
                break
            direction = -1
            y += direction
            if y == -1: return None
        else:
            if direction == -1:
                y += 1
                break
            direction = 1
            y += direction
            if y == MAP_HEIGHT: return None
    return y


class PostEffect(object):
    """keep track of which squares need to be re-lit, and then PostEffect them"""
    save_file: mcInterface.SaveFile

    def add(self, x, z):
        coords = (x, z)
        self.all_columns.add(coords)

    def add_surface(self):
        mclevel = self.save_file
        get_height = mclevel.get_heightmap
        set_block = mclevel.set_block
        for column_coords in self.all_columns:
            # randomly skip a fraction of the blocks
            if random() > SURFACE_FRACTION: continue
            # add surface blocks above the top block
            x = column_coords[0]
            z = column_coords[1]
            # get the current heightmap
            cur_height = get_height(x, z)
            # find the true surface
            y = find_surface(x, cur_height, z, mclevel)
            if y is None: continue
            # set the block
            set_block(x, y, z, SURFACE_INFO)

    def __init__(self):
        self.all_columns = set()


PostEffect_master = PostEffect()


def log_set_block(mclevel, x, y, z, log, block_list, set_block, mat):
    if log:
        block_value = mclevel.block(x, y, z, 'BD')
        if block_value is None: return
        if block_value not in CRATER_DESTROYS:
            data = {'x': x, 'y': y, 'z': z, 'data': block_value}
            block_list += [data]
    set_block(x, y, z, mat)


def log_set_column(mclevel, x, y_start, y_end, z, log, block_list, set_block, mat):
    # print(f"setting column at {x}, {z} from {y_start} to {y_end}")
    for y in range(int(y_start), int(y_end + 1)):
        log_set_block(mclevel, x, y, z, log, block_list, set_block, mat)


def log_set_to_surface(mclevel, x, y_start, y_end, z, log, block_list, set_block, mat):
    y_ht = mclevel.get_heightmap(x, z) + 1
    if y_ht is None: return
    y_ht = find_surface(x, y_ht, z, mclevel)
    if y_ht is None: return
    y_ht += 1
    if y_start > y_ht: return
    # print(f"setting column to surface at {x}, {z} from {y_start} to {y_ht}")
    for y in range(int(y_start), y_ht):
        log_set_block(mclevel, x, y, z, log, block_list, set_block, mat)


class SphereObject(object):
    """A spherical object.
    
    It has a method to create itself.
    Designed for subclassing.
    """

    # initialize the top and bottom offsets
    bottom_offset = 0
    top_offset = 0

    def create(self, mclevel: mcInterface.SaveFile, log=False):
        loc_x = self.loc[0]
        loc_y = self.loc[1]
        loc_z = self.loc[2]
        radius = self.size * 0.5
        rad_sqr = radius ** 2
        set_block = mclevel.set_block
        block_list = []
        mat = self.mat
        for z_off in range(int(radius + 1)):
            # pre-calculate the squared z distance
            sqr_dist_z = z_off ** 2
            if VERBOSE:
                print(f"Sphere processing z offset {z_off}")
            for x_off in range(int(radius + 1)):
                sqr_dist_2d = (x_off ** 2 + sqr_dist_z)
                if sqr_dist_2d > rad_sqr:
                    continue
                sqrt_dist = sqrt(rad_sqr - sqr_dist_2d)
                y_start = max(loc_y + radius - sqrt_dist,
                              loc_y + self.bottom_offset, 0)
                y_end = min(loc_y + radius + sqrt_dist,
                              loc_y + radius*2 - self.top_offset + 1, MAP_HEIGHT)
                x = loc_x + x_off
                z = loc_z + z_off
                self.set_col(mclevel, x, y_start, y_end, z, log, block_list, set_block, mat)
                if x_off > 0:
                    x = loc_x - x_off
                    self.set_col(mclevel, x, y_start, y_end, z, log, block_list, set_block, mat)
                if z_off > 0:
                    z = loc_z - z_off
                    self.set_col(mclevel, x, y_start, y_end, z, log, block_list, set_block, mat)
                if x_off > 0:
                    x = loc_x + x_off
                    self.set_col(mclevel, x, y_start, y_end, z, log, block_list, set_block, mat)

        # set the columns to add post effects
        if SURFACE_FRACTION:
            for x in range(int(loc_x - radius),
                           int(loc_x + radius + 1)):
                for z in range(int(loc_z - radius),
                               int(loc_z + radius + 1)):
                    sqr_dist_2d = sqrt((loc_x - x) ** 2 + (loc_z - z) ** 2)
                    if sqr_dist_2d > radius: continue
                    PostEffect_master.add(x, z)
        if log:
            return block_list
        else:
            return None

    def __init__(self, location=None, mat=None, size=-1):
        # self.loc is the location of the bottom of the sphere
        if location is None:
            location = [0, 0, 0]
        if mat is None:
            mat = {'B': 0, 'D': 0}
        self.loc = location
        # self.size is the diameter of the sphere
        self.size = size
        # self.mat is the material dict to use for this object
        self.mat = mat
        self.set_col = log_set_column


class Boulder(SphereObject):
    """A large roundish stone object.
    
    Has some material properties, and a method to create itself.
    """

    def create(self, mclevel):
        SphereObject.create(self, mclevel)
        if BOULDER_TREASURE:
            coresize = (0.618 + random()) * self.size * 0.5
            coreloc = self.loc[:]
            coreloc[1] += (self.size - coresize) * 0.5
            i = -1
            num_treasure = len(TREASURE_LIST)
            while True:
                if random() < BOULDER_TREASURE:
                    i += 1
                else:
                    break
                if i == num_treasure:
                    break
            if i == -1:
                return
            elif i < num_treasure:
                coremat = TREASURE_LIST[i]
            else:
                coremat = choice(TREASURE_RARE)

            core = SphereObject(coreloc, {'B': coremat, 'D': 0}, coresize)
            core.create(mclevel)

    def __init__(self, location=None, mat=None, size=-1):
        SphereObject.__init__(self, location=location, mat=mat, size=size)
        if mat is None:
            mat = BOULDER_INFO
        self.mat = mat
        if location is None:
            location = [0, 0, 0]
        self.loc = location
        # if size is not initialized, randomize it!
        if self.size == -1:
            sizemin = BOULDER_SIZE - BOULDER_RANDOMIZATION
            sizevary = BOULDER_RANDOMIZATION * 2.
            size = sizemin + random() * sizevary
            self.size = size


class Crater(SphereObject):
    """A large roundish hole in the ground.
    
    Has a method to create itself.
    """

    def __init__(self, location=None, depth=None):
        if location is None:
            location = [0, 0, 0]
        if depth is None:
            sizemin = CRATER_DEPTH - DEPTH_RANDOMIZATION
            sizevary = DEPTH_RANDOMIZATION * 2.
            depth = (sizemin + random() * sizevary)
        self.depth = depth
        # set the size of the crater to a multiple of the depth
        size = depth * CRATER_DEPTH_DIAMETER_MULTIPLE
        SphereObject.__init__(self, location=location, size=size)
        self.set_col = log_set_to_surface

    def toss_block(self, block, mclevel):
        # throw the block out of the crater
        x = block['x']
        y = block['y']
        z = block['z']
        # find the planar distance from the block to the center of the crater
        dist_x = x - self.loc[0]
        dist_z = z - self.loc[2]
        # if the block is right under the stone, ignore it and move on
        if dist_x == 0 and dist_z == 0: return None
        # how far is this, in a straight line?
        dist_mag = sqrt(dist_x ** 2 + dist_z ** 2)
        # how far should the block move?
        throw_distance = (self.size * 0.5 - dist_mag) * EJECTA_DISTANCE
        # it should move at least 1.5
        if throw_distance < 1.5: throw_distance = 1.5
        # how far should the block end up from the crater center,
        # compared to where it was before?
        difference_multiple = (dist_mag + throw_distance) / dist_mag
        # Multiply the distances, get the offsets from the block location
        offset_x = int(difference_multiple * dist_x)
        offset_z = int(difference_multiple * dist_z)
        # assign the new x and z
        x = self.loc[0] + offset_x
        z = self.loc[2] + offset_z
        # randomize the location, based on how far it moved
        random_dist = throw_distance * .618
        random_locs = [i for i in range(-int(random_dist),
                                        int(random_dist + 1))]
        x += choice(random_locs)
        z += choice(random_locs)
        # Find the location on the surface
        y = find_surface(x, y, z, mclevel)
        if y is None: return None
        # slide downhill, away from the center of the crater
        # set up the kick values
        if dist_x == 0:
            x_kick = 0
        else:
            x_kick = int(dist_x / abs(dist_x))
        if dist_z == 0:
            z_kick = 0
        else:
            z_kick = int(dist_z / abs(dist_z))
        # find which is larger, x or z
        dist_ratio = abs(dist_x / (dist_z + .001))
        if dist_ratio > 2:
            # x is much larger, offset only x
            z_kick = 0
        elif dist_ratio < .5:
            # z is much larger, offset only z
            x_kick = 0
        # otherwise its about the same, offset both
        # keep kicking the block downhill
        new_x = x
        new_z = z
        while True:
            new_x += x_kick
            new_z += z_kick
            new_y = find_surface(new_x, y, new_z, mclevel)
            if new_y is None: return None
            if new_y >= y: break
            x = new_x
            y = new_y
            z = new_z
        # assign the block
        result = mclevel.set_block(x, y, z, block['data'])
        if SURFACE_FRACTION:
            PostEffect_master.add(x, z)
        return result

    def create(self, mclevel):
        # excevate the crater
        # log the materials displaced if necessary
        block_log = SphereObject.create(self, mclevel, log=CRATER_EJECTA)
        # fill the crater, if necessary
        if CRATER_FILL:
            if VERBOSE: print('filling crater')
            fillsize = self.size
            fillloc = self.loc[:]
            filldepth = self.depth * CRATER_FILL
            fill_object = SphereObject(fillloc, FILL_INFO, fillsize)
            # the top offset will equal the sphere size (diameter)
            # minus the intended depth
            offset = int(fillsize - filldepth)
            fill_object.top_offset = offset
            fill_object.create(mclevel)
        # displace each block in the log
        if CRATER_EJECTA:
            if VERBOSE: print('Displacing', len(block_log), 'blocks from a crater.')
            for block in block_log:
                self.toss_block(block, mclevel)


def selectlocations(mcmap):
    """return a list of locations to put the objects on the surface of the map.
    """
    assert isinstance(mcmap, mcInterface.SaveFile)
    featurelocs = []
    if VERBOSE: print('Locations: x, y, z')
    while len(featurelocs) < FEATURE_NUM:
        rad_fraction = random()
        # this is linear interpolation.
        # add other interpolation modes later
        rad = rad_fraction * RADIUS
        ang = random() * pi * 2
        x = X + int(rad * sin(ang) + .5)
        z = Z + int(rad * cos(ang) + .5)
        # check to see if this location is suitable
        y_top = mcmap.surface_block(x, z)
        if y_top is None:
            # this location is off the map!
            # Try somewhere else
            continue

        ychoices = [y_top["y"]]
        if BURIED_BOULDERS:
            ychoices += [i for i in range(0, y_top['y'])]
        if FLYING_BOULDERS:
            ychoices += [i for i in range(y_top['y'] + 1, MAP_HEIGHT)]
        y = choice(ychoices)
        if CRATERS:
            y = find_surface(x, y, z, mcmap)
            if y is None: continue
            depth = CRATER_DEPTH + 2 * DEPTH_RANDOMIZATION * (0.5 - random())
            y += -depth
        else:
            depth = 0
        if VERBOSE: print(x, y, z)
        featurelocs += [[x, y, z, depth]]
    return featurelocs


def main(the_map):
    """create the craters and boulders.
    """

    print("Selecting locations")
    locations = selectlocations(the_map)

    if CRATERS:
        print('Making craters')
        for loc in locations:
            print(f'Excavating {loc}')
            thiscrater = Crater(loc[:3], loc[3])
            thiscrater.create(the_map)

    if BOULDERS:
        print('Making boulders ')
        for loc in locations:
            if not CRATERS: print(f'Boulder at {loc}')
            thisboulder = Boulder(loc)
            thisboulder.create(the_map)
        print(' done')
    return None


def standalone():
    """Load the file, call main, and save the new file"""
    if not (BOULDERS or CRATERS):
        print("wait, you want neither boulders nor craters?")
        print("Um, okay... doing nothing")
        return None
    print("Importing the map")
    try:
        the_map = mcInterface.SaveFile(LOAD_NAME)
    except IOError:
        print('File name invalid or save file otherwise corrupted. Aborting')
        return None
    global MAP_HEIGHT
    MAP_HEIGHT = the_map.map_height + 1
    main(the_map)
    PostEffect_master.save_file = the_map
    if SURFACE_FRACTION:
        print("Adding surface blocks")
        PostEffect_master.add_surface()
    print("Saving the map (takes a bit)")
    the_map.write()
    if VERBOSE:
        print("finished")
        input('press Enter to close')
    return None


if __name__ == '__main__':
    standalone()

# Needed updates:
# make boulders able to be LUMPY (should be easy)
#
