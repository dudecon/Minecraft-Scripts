# Version 1
"""This takes a MineCraft level and builds a castle wall around the player.

Written by Paul Spooner, with God's help.
See more at: http://www.peripheralarbor.com/minecraft/minecraftscripts.html
"""

# Here are the variables you can edit.

# This is the name of the map to edit.
# Make a backup if you are experimenting!

LOAD_NAME = "TestB"

# The mountain is centered on the player

# How large (maximum) do you want the walled area?
# for example, RADIUS = 10 will make a 21 block diameter walled area
# on level ground.
# The script tries to match the wall to the terrain,
# so the size will be much smaller on slopes.
RADIUS = 19.5

# How tall do you want the wall?
# default 5
HEIGHT = 5

# How much do you want the area flattened?
# the height differences in the terrain inside the
# wall will be divided by FLATTENING
# for no flattening, set to 1
# default is 2.618
FLATTENING = 2.618

# What material should the wall be made from?
WALL_INFO = {'B':'minecraft:' + 'stone_bricks'}

# if you need more blocks, what should you fill with?
FILL_INFO = {'B':'minecraft:' + 'stone'}


#####################
# Advanced options! #
#####################

# What is the maximum vertical distance the walled zome should jump over?
# If there's a ditch or cliff higher than MAXVERTICALGAP
# the wall will not extend beyond it.
# Set higher if you don't mind large vertical cliffs inside your base.
# You may also need to set RADIUS high, in order to push it over the edge.
# default 3
MAXVERTICALGAP = 3

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
    HEIGHT = 5
    print("This script doesn't put stuff lower than it already is.",
          "Try StarStone with craters turned on.")
if FLATTENING < 1:
    print("FLATTENING is less than one, setting to one")
    FLATTENING = 1


# The following is an interface class for .mclevel data for minecraft savefiles.
import mcInterface

# Map height limits
# gets clobbered from the map height data on map import
MAPTOP = mcInterface.SaveFile.map_height
MAPBTM = mcInterface.SaveFile.map_bottom

# Now, on to the actual code.

from random import random
from math import sqrt

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
        self.adj_sqares = (tuple(coords_to_loc((x,zi)) for zi in (z-1,z+1)) +
                           tuple(coords_to_loc((xi,z)) for xi in (x-1,x+1)) +
                           tuple(coords_to_loc(c) for c in ((x-1,z+1), (x-1,z-1), (x+1,z+1), (x+1,z-1) ) ))
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
        # If the weight has passed zero, it has grown enough
        if new_weight >= 0 > self.weight:
            flag = True
        else:
            flag = False
        self.weight = new_weight
        return flag


class WalledArea(object):
    """A walled area.
    Contains a 2d map of contiguous square objects that
    conform to the surface."""
    save_file: mcInterface.SaveFile

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
            if square.adjacent == 6:
                # automatically upgrade squares that are almost fully enclosed
                square.growth += 1
            if square.a_log:
                # clobber the y value with the center square's y
                square.y = y
            cur_y = square.y
            if cur_y is None:
                # this square does not exist in the map!
                # don't add growth or anything
                continue
            height_diff = abs(y - cur_y)
            if height_diff == 0:
                # if the heights are the same,
                # one step will grow along this direction.
                added_growth = 0.4714
            elif height_diff > MAXVERTICALGAP:
                # the heights are too far apart, don't contribute to growth
                # at all.
                added_growth = 0
            else:
                # this is a magic value!
                # larger differences in height mean smaller growth
                # contributed by this square
                added_growth = (1 + MAXVERTICALGAP - height_diff) / (1 + MAXVERTICALGAP * 4.5)
            # add the extra growth to this square
            if (x != cur_x) and (z != cur_z):
                added_growth /= 1.41421
            square.growth += added_growth

    def grow_square(self, square):
        upgrade_to_interior = square.grow()
        # if the square doesn't graduate, skip the rest
        if not upgrade_to_interior: return None
        # find the location string for this square
        x = square.x
        z = square.z
        # check that it is within RADIUS
        if square.this_radius > RADIUS:
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
        # make a static tuple of the border squares
        ext_squares = tuple(sqr for sqr in self.outside.values())
        # for each border square, grow it
        for square in ext_squares:
            self.grow_square(square)
        # grow all the squares inside as well
        for square in self.interior.values():
            square.grow()

    def find_max_adjacent(self):
        """for each exterior square, find the max y of the adjacent squares"""
        all_squares = {**self.outside, **self.interior}
        for center_square in self.outside.values():
            max_y = center_square.y
            for loc_string in center_square.adj_sqares:
                if loc_string not in all_squares: continue
                cur_x, cur_z = loc_to_coords(loc_string)
                adj_square = all_squares[loc_string]
                max_y = max(max_y,adj_square.y)
            center_square.max_adj_y = max_y

    def origin_square(self, x, z):
        """Add a square to the map as a fully weighted square"""
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

    def create(self):
        Block = self.save_file.block
        set_block = self.save_file.set_block
        origin_weight = self.origin.weight
        origin_y = self.origin.y
        # the scaling factor is based on the origin_weight
        # depth_scale = 6 / origin_weight
        if VERBOSE:
            print(len(self.interior), 'interior squares')
            print(len(self.outside), 'wall squares')
        # Default "air" block
        air_block_data = {'B': 'minecraft:air'}
        for square in self.interior.values():
            y = square.y
            if y is None: continue
            x = square.x
            z = square.z
            # make it the appropriate depth
            original_y_diff = origin_y - y
            scaled_y_diff = int( 0.5 + original_y_diff / FLATTENING)
            new_y = origin_y - scaled_y_diff
            y_change = new_y - y
            if y_change < 0:
                # cut it down
                top_y = self.save_file.get_heightmap(x,z)
                for this_y in range(new_y, top_y):
                    set_block(x,this_y,z,air_block_data)
                self.save_file.decrease_all_heightmaps(x, new_y, z)
            elif y_change > 0:
                # fill it
                for this_y in range(y, new_y):
                    set_block(x, this_y, z, FILL_INFO)
                self.save_file.increase_all_heightmaps(x, new_y, z)
            square.y = new_y
            if VERBOSE:
                print("change was " + str(y_change) + " at coordinates " + str((x, z)),
                      'with a final y value of', new_y)
        self.find_max_adjacent()
        for wall_square in self.outside.values():
            y = wall_square.y
            if y is None: continue
            x = wall_square.x
            z = wall_square.z
            top_y = wall_square.max_adj_y + HEIGHT
            # y-1 to give the walls a foundation
            for this_y in range(y-1, top_y):
                set_block(x, this_y, z, WALL_INFO)
            self.save_file.increase_all_heightmaps(x, top_y, z)

def main(the_map: mcInterface.SaveFile):
    """Load the file, do the stuff, and save the new file.
    """
    print("Finding the walled area")
    position = the_map.get_player_block()
    plot = WalledArea(the_map)
    plot.origin_square(position[0], position[2])
    for i in range(int(RADIUS)+2):
        plot.grow_all()
        if VERBOSE:
            print("Expansion " + str(i + 1) + " of " + str(RADIUS) + " done")
    num_of_squares = len(plot.interior)
    print("found " + str(num_of_squares) + " included block columns")
    print("Flattening and walling")
    plot.create()
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