# Version 1
'''This takes a MineCraft level and changes the amount of materials present.
It is designed to shrink the amount of ore underground, but you can use it for
other things too.
'''

# Here are the variables you can edit.

# This is the name of the map to edit.
# Make a backup if you are experimenting!
LOADNAME = "LevelSave"

# Where do you want to start the search?
# X, and Z are the map coordinates of the lower corner.
X = -120
Z = -364

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
# Default: {14:0.5 , 15:0.5 , 16:0.5 , 21:0.5 , 56:0.5 , 73:0.5}
# which reduces gold, iron, coal, lapis, diamond, and redstone ores by 50%
ALTER = {14:0.5 , 15:0.5 , 16:0.5 , 21:0.5 , 56:0.5 , 73:0.5}

# What block type is the environment of the altered blocks?
# If an increase is indicated, only this type of blocks will be replaced
# if a decrease is indicated, this block type will replace it.
# Default: 1 (stone)
ENVIRONMENT = 1

# Do you want to do a quick search?
# True will only search every 15th block, in an intelligent pattern.
# False will search every block.
# Set to True if you are looking for clumps in a vast area.
# THIS FEATURE IS IGNORED AT THIS POINT
# QUICKSEARCH = True

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

def is_in_pattern(x,z):
    '''If this column is in the search pattern, return True, otherwise False
    x and z are the RELATIVE coordinates of the column (relative to X and Z)
    '''
    #if not QUICKSEARCH: return True
    apparent_z = z + x*2
    value = apparent_z % 5
    if value == 0: return True
    else: return False

def search_column(x, z, map_object):
    '''Return a list of blocks found in this column.
    '''
    # the list of the locations
    location_list = []
    # get the HeightMap value
    surface_data = map_object.surface_block(x, z, options='')
    if surface_data is None: return []
    end_y = surface_data['y']
    search_range = end_y // 2
    # map the get_block function
    block = map_object.block
    # search the column below this value
    for search_index in range(search_range):
        y = search_index * 2
        block_type = block(x, y, z)['B']
        if block_type in ALTER:
            location = (x, y, z, block_type)
            location_list += [location]
    return location_list

def find_mats(map_object):
    '''Search the map for blocks in ALTER and return them as a list.
    '''
    # the list of the locations
    found_locations = []
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

def replace_location(map_object, loc):
    '''Replace the materials in the current location
    '''
    # localize the get and set functions
    block = map_object.block
    set_block = map_object.set_block
    for x_offset in range(3):
        x = x_offset + loc[0] - 1
        for y_offset in range(3):
            y = y_offset + loc[1] - 1
            for z_offset in range(3):
                z = z_offset + loc[2] - 1
                if x_offset == 0 and y_offset == 0 and z_offset == 0:
                    block_info = loc[3]
                else:
                    block_raw = block(x, y, z)
                    if block_raw is None: continue
                    block_info = block_raw['B']
                if block_info in ALTER:
                    fraction = ALTER[block_info]
                    if random() < fraction:
                        set_block(x, y, z, {'B':ENVIRONMENT})
    return True

def replace_mats(map_object, locations):
    '''Enact the change in materials.
    Replace the material indicated with the ENVIRONMENT material,
    or grow the material into the ENVIRONMENT material.
    '''
    #loop through each location
    for loc in locations:
        replace_location(map_object, loc)

def main():
    '''Load the file, do the stuff, and save the new file.
    '''
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
    print("Saving the map (takes a bit)")
    the_map.write()
    print("finished")
    return None


if __name__ == '__main__':
    main()
    
# Needed updates:
# make it work
