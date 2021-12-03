# Version 1
"""This takes a MineCraft level and changes the amount of materials present.
It is designed to shrink the amount of ore underground, but you can use it for
other things too.
"""

# Here are the variables you can edit.

# This is the name of the map to edit.
# Make a backup if you are experimenting!
LOADNAME = "Test"

# Where do you want to start the search?
# X, and Z are the map coordinates of the lower corner.
X = 70
Z = 40

# How large an area do you want to search?
# The x and z dimensions of the search box (positive values only).
SIZEX = 100
SIZEZ = 100

# What block types do you want to affect, and by how much?
# This is a dictionary. The format is:
# {block id #:multiple fraction, other id:other fraction}
# 
# For example:
# ALTER = {14:0.5, 49:0.1}
# will reduce gold ore (id 14) by one half (0.5) of the current quantity,
# and reduces obsidian (id 49) by one tenth (0.1) the current quantity.
# quantity
#
# Default: {14: 0.4, 15: 0.4, 16: 0.4, 21: 0.4, 56: 0.4, 73: 0.4}
# which reduces gold, iron, coal, lapis, diamond, and redstone ores to 40% of their original quantity
ALTER = {14: 0.4, 15: 0.4, 16: 0.4, 21: 0.4, 56: 0.4, 73: 0.4}

# What block type is the environment of the altered blocks?
# If an increase is indicated, only this type of blocks will be replaced
# if a decrease is indicated, this block type will replace it.
# Default: 1 (stone)
ENVIRONMENT = 1

# Do you want to do a quick search?
# Sets the spacing of the search.
# larger numbers mean a more coarse search
# so they go faster, but also may miss small deposits
# default 3
# set to 1 to search every single block
SEARCH_CADENCE = 3
# Technical note, the cadence applies to both the horizontal plane, as well as the vertical column
# so cadence = 3 will be 9 times faster than searching every block

##############################################################
#  Don't edit below here unless you know what you are doing  #
##############################################################

# input filtering

if SIZEX < 1:
    print("SIZEX was less than one, setting to 1 and continuing on")
    SIZEX = 1
if SIZEZ < 1:
    print("SIZEX was less than one, setting to 1 and continuing on")
    SIZEZ = 1
if len(ALTER) < 1:
    print("There is nothing in ALTER, aborting!")
    raise IOError("ALTER empty, not looking for anything")

# The following is an interface class for .mclevel data for minecraft savefiles.

import mcInterface

# Now, on to the actual code.

from random import random


def is_in_pattern(x, z):
    """If this column is in the search pattern, return True, otherwise False
    x and z are the RELATIVE coordinates of the column (relative to X and Z)
    """
    if SEARCH_CADENCE == 1: return True
    value = (z + x) % SEARCH_CADENCE
    if value == 0:
        return True
    else:
        return False


def search_column(x, z, map_object: mcInterface.SaveFile):
    """Return a list of blocks found in this column.
    """
    # get the HeightMap value
    hmnl = map_object.get_heightmap(x, z, "MOTION_BLOCKING_NO_LEAVES")
    hmof = map_object.get_heightmap(x, z, "OCEAN_FLOOR")
    if (hmnl is None) or (hmof is None): return []
    end_y = min(hmnl, hmof)
    # the list of the locations
    location_list = []
    search_range = end_y // SEARCH_CADENCE
    # map the get_block function
    block = map_object.block
    # search the column below this value
    for search_index in range(search_range):
        y = (search_index * SEARCH_CADENCE) + (x % SEARCH_CADENCE)
        block_type = block(x, y, z)
        if block_type in ALTER:
            location = {"x": x, "y": y, "z": z, 'B': block_type}
            location_list += [location]
    return location_list


def find_mats(map_object: mcInterface.SaveFile):
    """Search the map for blocks in ALTER and return them as a list.
    """
    # the list of the locations
    found_locations = set()
    # big search loop
    for x_offset in range(SIZEX):
        cur_x = X + x_offset
        for z_offset in range(SIZEZ):
            cur_z = Z + z_offset
            # check if we want to even search this column
            if not is_in_pattern(x_offset, z_offset): continue
            found_this_column = search_column(cur_x, cur_z, map_object)
            found_locations += found_this_column
    return found_locations


# init the search vectors
search_offsets = {(0, 0, 0), }
for off in range(1, SEARCH_CADENCE):
    search_offsets.add((off, 0, 0))
    search_offsets.add((0, off, 0))
    search_offsets.add((0, 0, off))


def replace_location(map_object: mcInterface.SaveFile, loc):
    """Replace the materials in the current location
    """
    # localize the get and set functions
    block = map_object.block
    set_block = map_object.set_block

    for off in search_offsets:
        x = off[0] + loc[0]
        y = off[1] + loc[1]
        z = off[2] + loc[2]
        if off == (0, 0, 0):
            block_info = loc[3]
        else:
            block_info = block(x, y, z)
            if block_info is None: continue
        if block_info in ALTER:
            fraction = ALTER[block_info]
            if random() > fraction:
                set_block(x, y, z, {'B': ENVIRONMENT})
    return True


def replace_mats(map_object, locations):
    """Enact the change in materials.
    Replace the material indicated with the ENVIRONMENT material,
    or grow the material into the ENVIRONMENT material.
    """
    # loop through each location
    for loc in locations:
        replace_location(map_object, loc)


def main():
    """Load the file, do the stuff, and save the new file.
    """
    print("Importing the map")
    try:
        the_map = mcInterface.SaveFile(LOADNAME)
    except IOError:
        print('File name invalid or save file otherwise corrupted. Aborting')
        return None
    print("Finding the materials")
    loc_list = find_mats(the_map)
    print_string = str(len(loc_list)) + ' samples found'
    print(print_string)
    print("Replacing the materials")
    replace_mats(the_map, loc_list)
    # print("Saving the map (takes a bit)")
    # the_map.write()
    print("finished")
    return None


if __name__ == '__main__':
    main()
