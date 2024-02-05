# Version 6
"""This takes a MineCraft level and makes a big cave around the player.

Written by Paul Spooner, with God's help.
See more at: http://www.peripheralarbor.com/minecraft/minecraftscripts.html
"""

# Here are the variables you can edit.

# This is the name of the map to edit.
# Make a backup if you are experimenting!

LOAD_NAME = "TestB"

# The mountain is centered on the player

# How large (maximum) do you want the cave to be?
# for example, RADIUS = 10 will make a 21 block diameter cave
RADIUS = 79

# do you want a clear center section?
# if so, set this to more than 1, this will also add to the ultimate radius
CENTER_OFFSET = 12

# How far into the sky do you want to move it?
# center height for the cave
HEIGHT = 33

# Approximate feature size
# for stalactite and stalagmite feature dimensions
FEATURE_SIZE = 9

# How many features do you want?
FEATURE_NUM = 63

# How thick do you want the top of the cave?
# This is a scalar
# 1.0 is a pretty thin cave
# 2.0 is the default
DEPTH_SCALE = 2.0

# stalactite depth
# so you don't end up with a bunch of holes everywhere
# currently seems broken
SLTC_DPT = 18

#####################
# Advanced options! #
#####################


# Do you want a bunch of info on what's going on?
# True will print a lot of stuff, slows it down a little
# False will print a little, makes it a little faster
VERBOSE = False

##############################################################
#  Don't edit below here unless you know what you are doing  #
##############################################################

# input filtering

if RADIUS < 1:
    print("RADIUS is less than 1, setting it to 5")
    RADIUS = 5
if HEIGHT < 1:
    print("HEIGHT is less than 1, setting it to 15")
    HEIGHT = 15
    print("This script doesn't put stuff lower than it already is.",
          "Try StarStone with craters turned on.")
if DEPTH_SCALE < 0:
    print("DEPTH_SCALE is negative, setting to zero")
    DEPTH_SCALE = 0


# The following is an interface class for .mclevel data for minecraft savefiles.
import mcInterface

# Map height limits
# gets clobbered from the map height data on map import
MAPTOP = mcInterface.SaveFile.map_height
MAPBTM = mcInterface.SaveFile.map_bottom

# Now, on to the actual code.

from random import random, choice
from math import sqrt, sin, cos, pi

def loc_to_coords(loc):
    """Take a location string and return the x z location"""
    loc_list = loc.split()
    x = int(loc_list[0])
    z = int(loc_list[1])
    return x, z

def coords_to_loc(coords):
    """Take an x,z coordinate pair and return the location string"""
    x = str(coords[0])
    z = str(coords[1])
    loc_str = x + ' ' + z
    return loc_str

class Square(object):
    """a single square that knows about itself"""

    def __init__(self, mclevel, x, z, origin = None):
        self.x = x
        self.y = mclevel.get_heightmap(x, z, "MOTION_BLOCKING_NO_LEAVES")
        self.z = z
        self.adj_sqares = (tuple(coords_to_loc((x, zi)) for zi in (z - 1, z + 1)) +
                           tuple(coords_to_loc((xi, z)) for xi in (x - 1, x + 1)) +
                           tuple(coords_to_loc(c) for c in
                                 ((x - 1, z + 1), (x - 1, z - 1), (x + 1, z + 1), (x + 1, z - 1))))
        # precompute the radius, since it should never change
        if origin is None:
            self.this_radius = 0
        else:
            delta_x = abs(x - origin.x)
            delta_z = abs(z - origin.z)
            self.this_radius = sqrt(delta_x ** 2 + delta_z ** 2)
        # what is the current weight of the square?
        # Squares grow when they reach zero weight
        self.weight = -1.0
        blocktype = mclevel.block(x, self.y-1, z)
        blockstr = blocktype['B'].replace('minecraft:', '')
        if blockstr in mcInterface.blocktype_bark_logs:
            self.a_log = True
        else:
            self.a_log = False
        # How much should the weight grow each step?
        self.growth = 0
        # How many squares are adjacent to this one?
        self.adjacent = 0

    def __str__(self):
        output = 'Square: '
        output += str(self.x) + ' '
        output += str(self.y) + ' '
        output += str(self.z) + ' '
        output += 'weight: ' + str(self.weight) + ' '
        output += 'growth: ' + str(self.growth) + ' '
        output += 'adj: ' + str(self.adjacent)
        return output

    def grow(self):
        """Increase the weight of the square, return if it has grown enough."""
        new_weight = self.weight + self.growth
        # If the weight has reached zero, it has grown enough
        if new_weight >= 0 > self.weight:
            flag = True
        else:
            flag = False
        self.weight = new_weight
        return flag


class FlyingMountain(object):
    """A mountain, floating in the sky.
    Contains a 2d map of contiguous square objects that
    conform to the surface."""
    save_file: mcInterface.SaveFile

    def add_all_squares(self, othercanvas):
        for loc in othercanvas.interior:
            othersquare = othercanvas.interior[loc]
            if loc in self.interior:
                this_square = self.interior[loc]
                this_square.weight += othersquare.weight
                this_square.growth += othersquare.growth
                this_square.this_radius = min(othersquare.this_radius, this_square.this_radius)
            elif loc in self.outside:
                self.interior.update({loc: othersquare})
                # remove the current square from the exterior
                del self.outside[loc]
            else:
                self.interior.update({loc: othersquare})
        for loc in othercanvas.outside:
            othersquare = othercanvas.outside[loc]
            if loc in self.interior:
                continue
            elif loc in self.outside:
                this_square = self.outside[loc]
                this_square.weight += othersquare.weight
                this_square.growth += othersquare.growth
                this_square.this_radius = min(othersquare.this_radius, this_square.this_radius)
            else:
                self.outside.update({loc: othersquare})


    def add_adjacent(self, center_square):
        x = center_square.x
        y = center_square.y
        z = center_square.z
        for loc_string in center_square.adj_sqares:
            cur_x, cur_z = loc_to_coords(loc_string)
            if loc_string in self.interior:
                # if it's already in the interior,
                square = self.interior[loc_string]
            elif loc_string in self.outside:
                # if it's already in the outside list
                square = self.outside[loc_string]
            # or it's not listed in the dictionary, and needs to be created
            else:
                # this square is not in any square lists
                # make a new square and add it to the outside
                square = Square(self.save_file, cur_x, cur_z, self.origin)
                self.outside.update({loc_string: square})
            square.adjacent += 1
            square.growth += 1.1

    def grow_square(self, square):
        upgrade_to_interior = square.grow()
        # if the square doesn't graduate, skip the rest
        if not upgrade_to_interior: return None
        # find the location string for this square
        x = square.x
        z = square.z
        # check that it is within RADIUS
        if square.this_radius > FEATURE_SIZE:
            # the square is too far from the center
            return None
        # if you got here, the square belongs inside!
        loc_string = coords_to_loc((x, z))
        # add the square to the appropriate list
        self.interior.update({loc_string: square})
        # remove the current square from the exterior
        del self.outside[loc_string]
        # update the adjacent squares
        self.add_adjacent(square)

    def grow_all(self):
        """Grow each of the squares"""
        # make a static list of the border squares
        ext_squares = tuple(sqr for sqr in self.outside.values())
        # for each border square, grow it
        for square in ext_squares:
            self.grow_square(square)
        # grow all the squares inside as well
        for square in self.interior.values():
            square.grow()

    def origin_square(self, x, z):
        """Add a square to the map as a fullly weighted square"""
        # check to see if this square is already in the lists
        loc_string = coords_to_loc((x, z))
        if loc_string in self.interior:
            square = self.interior[loc_string]
        elif loc_string in self.outside:
            square = self.outside[loc_string]
        else:
            # insert a new square
            square = Square(self.save_file, x, z)
            # add the square to the outside list
            self.outside.update({loc_string: square})
            # check if adjacent squares are weighted
            # if so, add adjacency to this one
            for loc_string in square.adj_sqares:
                cur_x, cur_z = loc_to_coords(loc_string)
                if loc_string in self.interior:
                    square.adjacent += 1
        # set a positive weight, forcing this square to grow
        square.weight = -.1
        square.growth = .11
        # grow the square
        # this should move it to the border or interior list
        self.origin = square
        self.grow_square(square)

    def __init__(self, save_file: mcInterface.SaveFile):
        self.save_file = save_file
        # the squares outside the border
        self.outside = {}
        # the squares fully enclosed inside
        self.interior = {}

    def more_squares(self):
        player_pos = self.save_file.get_player_block()
        OriginX = player_pos[0]
        OriginZ = player_pos[2]
        radius = RADIUS + CENTER_OFFSET
        rad_sqr = (radius) ** 2
        cent_sqr = CENTER_OFFSET ** 2
        for z_off in range(int(radius + 1)):
            # pre-calculate the squared z distance
            sqr_dist_z = z_off ** 2
            for x_off in range(int(radius + 1)):
                sqr_dist_2d = (x_off ** 2 + sqr_dist_z)
                if sqr_dist_2d > rad_sqr:
                    break
                if cent_sqr > sqr_dist_2d:
                    continue
                sqrt_dist = sqrt(rad_sqr - sqr_dist_2d)
                x = OriginX + x_off
                z = OriginZ + z_off
                loc_string = coords_to_loc((x,z))
                square = Square(self.save_file, x, z)
                self.interior.update({loc_string: square})
                if x_off > 0:
                    x = OriginX - x_off
                    loc_string = coords_to_loc((x, z))
                    square = Square(self.save_file, x, z)
                    self.interior.update({loc_string: square})
                if z_off > 0:
                    z = OriginZ - z_off
                    loc_string = coords_to_loc((x, z))
                    square = Square(self.save_file, x, z)
                    self.interior.update({loc_string: square})
                if x_off > 0:
                    x = OriginX + x_off
                    loc_string = coords_to_loc((x, z))
                    square = Square(self.save_file, x, z)
                    self.interior.update({loc_string: square})

    def create(self):
        Block = self.save_file.block
        set_block = self.save_file.set_block
        origin_weight = FEATURE_SIZE * 9
        # the scaling factor is based on the origin_weight
        depth_scale = 6 / origin_weight
        # print(len(self.interior))
        # print(len(self.outside))
        # Default "air" block
        air_block_data = {'B': 'minecraft:air'}
        player_pos = self.save_file.get_player_block()
        OriginX = player_pos[0]
        OriginZ = player_pos[2]
        for square in self.interior.values():
            y = square.y
            if y is None: continue
            x = square.x
            z = square.z
            # make the appropriate depth
            this_depth = int(DEPTH_SCALE * (
                    (depth_scale * square.weight * (RADIUS - square.this_radius)/RADIUS ) +
                    0.1 + random() * 3))
            # add one for the vertical offset of find_surface
            # add one for the missing endpiece in range()
            # add DEPTHOFFSET for the people who want it
            this_depth += 2
            start_y = y - this_depth
            if start_y < MAPBTM: start_y = MAPBTM
            end_y = self.save_file.get_heightmap(x, z, "WORLD_SURFACE")
            # go from top to bottom, offseting all the blocks
            height_set = False
            delta_x = abs(x - OriginX)
            delta_z = abs(z - OriginZ)
            absolute_radius = sqrt(delta_x ** 2 + delta_z ** 2)
            this_height = HEIGHT * (1 - (absolute_radius/(RADIUS + CENTER_OFFSET)))
            blank_depth = start_y - SLTC_DPT + this_depth
            for this_y in range(end_y, start_y, -1):
                new_y = int(this_y + this_height )
                if new_y > MAPTOP:
                    set_block(x, this_y, z, air_block_data)
                    continue
                block_data = Block(x, this_y, z, True)
                if block_data is None:
                    block_data = air_block_data
                elif not height_set:
                    height_set = True
                    old_height = self.save_file.get_heightmap(x, z)
                    new_height = old_height + this_depth - 1
                    if new_height > MAPTOP: new_height = MAPTOP
                    self.save_file.set_heightmap(x, new_height, z)
                set_block(x, new_y, z, block_data)
                if this_y > blank_depth:
                    set_block(x, this_y, z, air_block_data)
            # correct the height maps
            self.save_file.offset_all_heightmaps(x, z, this_height)
            if VERBOSE:
                print("Raised " + str(this_depth) + "blocks at " + str((x, z)))

def selectlocations(mcmap):
    """return a list of locations to put the objects on the surface of the map.
    """
    assert isinstance(mcmap, mcInterface.SaveFile)
    player_pos = mcmap.get_player_block()
    X = player_pos[0]
    Z = player_pos[2]
    featurelocs = []
    if VERBOSE: print('Locations: x, y, z')
    while len(featurelocs) < FEATURE_NUM:
        rad_fraction = random()
        # this is linear interpolation.
        # add other interpolation modes later
        rad = rad_fraction * RADIUS + CENTER_OFFSET
        ang = random() * pi * 2
        x = X + int(rad * sin(ang) + .5)
        z = Z + int(rad * cos(ang) + .5)
        # check to see if this location is suitable
        y_top = mcmap.get_heightmap(x, z, "MOTION_BLOCKING_NO_LEAVES")
        if y_top is None:
            # this location is off the map!
            # Try somewhere else
            continue
        if VERBOSE: print("feature location", x, z)
        featurelocs.append({'x': x, 'z': z, 'y': y_top})
    return featurelocs

def main(the_map: mcInterface.SaveFile):
    """Load the file, do the stuff, and save the new file.
    """
    print("Finding the cave")
    locations = selectlocations(the_map)
    master_canvas = FlyingMountain(the_map)
    for loc in locations:
        stalactite = FlyingMountain(the_map)
        stalactite.origin_square(loc['x'], loc['z'])
        for i in range(FEATURE_SIZE):
            stalactite.grow_all()
            if VERBOSE:
                print("Expansion " + str(i + 1) + " of " + str(RADIUS) + " done")
        num_of_squares = len(stalactite.interior)
        master_canvas.add_all_squares(stalactite)
    moresquares = FlyingMountain(the_map)
    moresquares.more_squares()
    master_canvas.add_all_squares(moresquares)
    master_canvas.create()
    return None


def standalone():
    """Load the file, do the stuff, and save the new file.
    """
    print("Importing the map")
    try:
        the_map = mcInterface.SaveFile(LOAD_NAME)
    except IOError:
        print('File name invalid or save file otherwise corrupted. Aborting')
        return None
    main(the_map)
    print("Saving the map (takes a bit)")
    if the_map.write():
        print("finished")
    else:
        print("saving went sideways somehow")
    if VERBOSE:
        input("press Enter to close")


if __name__ == '__main__':
    standalone()

# Needed updates:
# flood-fill trees and foliage