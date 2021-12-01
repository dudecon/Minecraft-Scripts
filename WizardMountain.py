# Version 5
"""This takes a MineCraft level and rends some landscape up into the sky.

Written by Paul Spooner, with God's help.
See more at: http://www.peripheralarbor.com/minecraft/minecraftscripts.html
"""

# Here are the variables you can edit.

# This is the name of the map to edit.
# Make a backup if you are experimenting!

LOAD_NAME = "Test"

# Where do you want the mountain centered?
# X, and Z are the map coordinates of the center tower
X = 13
Z = 274

# How large (maximum) do you want the mountain?
# for example, RADIUS = 10 will make a 21 block diameter mountain
# on level ground.
# The script tries to match the mountain to the terrain, 
# so the size will be much smaller on slopes.
RADIUS = 25

# How far into the sky do you want to move it?
# default 15
HEIGHT = 57

# How thick do you want the mountain?
# This is a scalar
# 1.0 is the default
# 2.0 will make a very thick shard
# 0.2 will make a thin shell, just a bit off the surface really
DEPTH_SCALE = 2.7

#####################
# Advanced options! #
#####################

# To find "ground level" the script needs to know what to consider "ground".
# This is a list of material indexes that are considered "ground" by the script.
GROUND_LIST = [1, 2, 3, 4, 7, 12, 13, 24, 48, 49, 82]

# What is the maximum vertical distance the mountain zome should jump over?
# If there's a ditch or cliff higher than MAXVERTICALGAP
# the mountain will not extend beyond it.
# Set higher if you don't mind large vertical cliffs on your mountain.
# You may also need to set RADIUS high, in order to push it over the edge.
# default 3
MAXVERTICALGAP = 3

# What is the thickness offset?
# This is in addition to the 1 thick required
# 0 is the default
# -2 will make it very thin at the edges, probably no dirt at all
# 3 will ensure that at least 4 blocks are picked up, if any.
DEPTHOFFSET = 0

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
if len(GROUND_LIST) < 1:
    print("There is nothing in GROUND_LIST, you may encounter problems.")
if DEPTH_SCALE < 0:
    print("DEPTH_SCALE is negative, setting to zero")
    DEPTH_SCALE = 0
DEPTHOFFSET = int(DEPTHOFFSET)

# The following is an interface class for .mclevel data for minecraft savefiles.
import mcInterface

# Map height limits
MAPTOP = 255
MAPBTM = 0

# Now, on to the actual code.

from random import random
from math import sqrt


def find_surface(x, y, z, search, mclevel: mcInterface.SaveFile, invert=False):
    """return the y position on top of blocks you are searching for."""
    # moves down if not in search, up if in search.
    # x, y, z int, The starting location for the search
    # search, list, the data values you are searching for
    # mclevel, an mcInterface.SaveFile object
    # invert, search for anything except values in "search"
    Block = mclevel.block
    direction = 0
    # check to see if this block exists
    # print('find surface cords', x, y, z)
    info = Block(x, y, z)
    if info is None: return None
    while True:
        info = Block(x, y, z)
        # find if the block is in the search list
        void_check = info not in search
        # flip the truth value if invert is True
        if invert: void_check = not void_check
        # if we found what we were looking for
        if void_check:
            # and we are moving up
            if direction == 1:
                # we're done
                break
            direction = -1
            y += direction
            # check if you just went off the bottom of the map
            if y == MAPBTM - 1: return None
        else:
            # and we are moving down
            if direction == -1:
                # add one (you just left the position you wanted)
                y += 1
                # and we're done
                break
            direction = 1
            y += direction
            # check if you just went off the top of the map
            if y > MAPTOP:
                y = MAPTOP
                break
    return y


class Square(object):
    """a single square that knows about itself"""

    def __init__(self, mclevel, x, y, z):
        self.x = x
        self.y = find_surface(x, y, z, GROUND_LIST, mclevel)
        self.z = z
        # what is the current weight of the square?
        # Squares grow when they reach zero weight
        self.weight = -1.0
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

    @staticmethod
    def loc_to_coords(loc):
        """Take a location string and return the x z location"""
        loc_list = loc.split()
        x = int(loc_list[0])
        z = int(loc_list[1])
        return x, z

    @staticmethod
    def coords_to_loc(coords):
        """Take an x,z coordinate pair and return the location string"""
        x = str(coords[0])
        z = str(coords[1])
        loc_str = x + ' ' + z
        return loc_str

    def add_adjacent(self, center_square):
        x = center_square.x
        y = center_square.y
        z = center_square.z
        for cur_x in (x - 1, x, x + 1):
            for cur_z in (z - 1, z, z + 1):
                # don't update the center square
                if cur_x == x and cur_z == z: continue
                # find the key string for this square
                loc_string = self.coords_to_loc((cur_x, cur_z))
                if loc_string in self.interior:
                    # if it's already in the interior,
                    square = self.interior[loc_string]
                elif loc_string in self.outside:
                    square = self.outside[loc_string]
                # or it's not listed in the dictionary, and needs to be created
                else:
                    # this square is not in any square lists
                    # make a new square and add it to the outside
                    square = Square(self.save_file, cur_x, y, cur_z)
                    self.outside.update({loc_string: square})
                square.adjacent += 1
                cur_y = square.y
                if cur_y is None:
                    # this square does not exist in the map!
                    # don't add growth or anything
                    continue
                height_diff = abs(y - cur_y)
                if height_diff == 0:
                    # if the heights are nearly the same, 
                    # one step will grow along this direction.
                    added_growth = 1
                elif height_diff > MAXVERTICALGAP:
                    # the heights are too far apart, don't contribute to growth
                    # at all.
                    added_growth = 0
                else:
                    # this is a magic value!
                    # larger differences in height mean smaller growth
                    # contributed by this square
                    added_growth = 1 / (height_diff * 8.0)
                # add the extra growth to this square
                square.growth += added_growth

    def grow_square(self, square):
        upgrade_to_interior = square.grow()
        # if the square doesn't graduate, skip the rest
        if not upgrade_to_interior: return None
        # if you got here, the square belongs inside!
        # find the location string for this square
        x = square.x
        z = square.z
        loc_string = self.coords_to_loc((x, z))
        # add the square to the appropriate list
        self.interior.update({loc_string: square})
        # remove the current square from the exterior
        del self.outside[loc_string]
        # update the adjacent squares
        self.add_adjacent(square)

    def grow_all(self):
        """Grow each of the squares"""
        # make a static list of the border squares
        ext_squares = [sqr for sqr in self.outside.values()]
        # for each border square, grow it
        for square in ext_squares:
            self.grow_square(square)
        # grow all the squares inside as well
        for square in self.interior.values():
            square.grow()

    def origin_square(self, x, y, z):
        """Add a square to the map as a fullly weighted square"""
        # check to see if this square is already in the lists
        loc_string = self.coords_to_loc((x, z))
        if loc_string in self.interior:
            square = self.interior[loc_string]
        elif loc_string in self.outside:
            square = self.outside[loc_string]
        else:
            # insert a new square
            square = Square(self.save_file, x, y, z)
            # add the square to the outside list
            self.outside.update({loc_string: square})
            # check if adjacent squares are weighted
            # if so, add adjacency to this one
            for cur_x in (x - 1, x, x + 1):
                for cur_z in (z - 1, z, z + 1):
                    # don't update the center square
                    if cur_x == x and cur_z == z: continue
                    # find the key string for this square
                    loc_string = self.coords_to_loc((cur_x, cur_z))
                    if loc_string in self.interior:
                        square.adjacent += 1
        # set a positive weight, forcing this square to grow
        square.weight = -.1
        square.growth = .11
        # grow the square
        # this should move it to the border or interior list
        self.grow_square(square)
        self.origin = square

    def __init__(self, save_file: mcInterface.SaveFile):
        self.save_file = save_file
        # the squares outside the border
        self.outside = {}
        # the squares fully enclosed inside
        self.interior = {}

    def create(self):
        Block = self.save_file.block
        set_block = self.save_file.set_block
        origin_weight = self.origin.weight
        # the scaling factor is based on the origin_weight
        depth_scale = 6 / origin_weight
        # print(len(self.interior))
        # print(len(self.outside))
        # Default "air" block
        air_block_data: dict[str, int] = {'B': 0, 'D': 0, 'S': 0, 'L': 2}
        for square in self.interior.values():
            y = square.y
            if y is None: continue
            x = square.x
            z = square.z
            # check that it is within RADIUS
            delta_x = abs(x - X)
            delta_z = abs(z - Z)
            this_radius = sqrt(delta_x ** 2 + delta_z ** 2)
            if this_radius == 0: this_radius = 1.0
            if this_radius > (RADIUS + 1):
                # the square is too far from the center
                continue
            # make the appropriate depth
            this_depth = int(DEPTH_SCALE * (depth_scale * square.weight +
                                            (RADIUS - this_radius) * 0.618 + 1.5 + random() * 3))
            # add one for the vertical offset of find_surface
            # add one for the missing endpiece in range()
            # add DEPTHOFFSET for the people who want it
            this_depth += 2 + DEPTHOFFSET
            start_y = y - this_depth
            if start_y < MAPBTM: start_y = MAPBTM
            end_y = MAPTOP
            # go from top to bottom, offseting all the blocks
            for this_y in range(end_y, start_y, -1):
                new_y = this_y + HEIGHT
                if new_y > MAPTOP:
                    set_block(x, this_y, z, air_block_data)
                    continue
                block_data = Block(x, this_y, z, 'BDSL')
                if block_data is None:
                    block_data = air_block_data
                set_block(x, new_y, z, block_data)
                set_block(x, this_y, z, air_block_data)
            # correct the height map
            old_height = self.save_file.get_heightmap(x, z)
            new_height = old_height + this_depth - 1
            if new_height > MAPTOP: new_height = MAPTOP
            self.save_file.set_heightmap(x, new_height, z)
            if VERBOSE:
                print("Raised " + str(this_depth) + "blocks at " + str((x, z)))


def main(the_map: mcInterface.SaveFile):
    """Load the file, do the stuff, and save the new file.
    """
    print("Finding the mountain")
    mont = FlyingMountain(the_map)
    mont.origin_square(X, MAPTOP, Z)
    for i in range(RADIUS):
        mont.grow_all()
        if VERBOSE:
            print("Expansion " + str(i + 1) + " of " + str(RADIUS) + " done")
    num_of_squares = len(mont.interior)
    print("found " + str(num_of_squares) + " included block columns")
    print("Lifting the mountain into the sky!")
    mont.create()
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
    global MAPTOP
    MAPTOP = the_map.map_height
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
