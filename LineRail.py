# Version 3
"""This takes a base MineCraft level and adds a powered rail.

Written by Paul Spooner, with God's help.
See more at: http://www.peripheralarbor.com/minecraft/minecraftscripts.html
"""

# Here are the variables you can edit.

# This is the name of the map to edit.
# Make a backup if you are experimenting!
LOADNAME = "TestWorld"

# Where do you want to start the rail?
# X, Y, and Z are the map coordinates
# This is the position of the first rail block
X = 282
Y = 103
Z = 271

# What direction do you want it to go from the starting block?
# '+X' will go in the positive x direction
# '-X' will go in the negative x direction
# '+Z' will go in the positive z direction
# '-Z' will go in the negative z direction
DIRECTION = '-Z'

# How far do you want the rail to go?
DISTANCE = 144

# How tall do you want the tunnels?
# This includes the rail block.
# Should probably be at least 2.
# Default, 3
TUNNELHEIGHT = 3

#####################
# Advanced options! #
#####################

# How far apart do you want the powered rail blocks?
# Default, 26
POWERSPACING = 26

# What material do you want the rail-bed made of?
# This will be placed under every rail block.
BEDMAT = 1

# What data value do you want for the rail-bed?
BEDDATA = 0

# How far apart do you want support pillars?
# These will be used to "support" the rail bed over valleys.
# Example: 5 will put four blank blocks between each pillar.
# if set to 0, it will make no pillars.
# Default, 8
PILLARSPACING = 8

# What material do you want the support pillars made of?
PILLARMAT = 1

# What data value do you want for the support pillars?
PILLARDATA = 0

# How far apart do you want the lights?
# like PILLARSPACING
# if set to 0, will make no lights
# Default, 8
LIGHTSPACING = 8

# What block do you want for the lights?
# Default, 50 (torches)
LIGHTMAT = 50

# What data value do you want for the lights?
# Default, 5 (torch placed on the ground)
LIGHTDATA = 5

# Do you want a bunch of info on what the script is doing?
# True enables verbose data output
# False minimal text info, and a slight speed increase
VERBOSE = False

##############################################################
#  Don't edit below here unless you know what you are doing  #
##############################################################

# input filtering
DIRECTION = DIRECTION.upper()
if DIRECTION not in ('+X', '-X', '+Z', '-Z'):
    print("DIRECTION value '" + str(DIRECTION) + "' is not a valid choice, please use '+X', '-X', '+Z', or '-Z'")
if DISTANCE < 1:
    DISTANCE = 1
    print('DISTANCE was less than 1. Setting to 1 and continuing.')
if POWERSPACING < 1:
    POWERSPACING = 1
    print('POWERSPACING was less than 1. Setting to 1 and continuing.')
if TUNNELHEIGHT < 1:
    TUNNELHEIGHT = 1
    print('TUNNELHEIGHT was less than 1. Setting to 1 and continuing.')
if PILLARSPACING < 1:
    PILLARSPACING = 0
    print('PILLARSPACING was less than 1. Building no pillars')
if LIGHTSPACING < 1:
    LIGHTSPACING = 0
    print('LIGHTSPACING was less than 1. Adding no lights')

if BEDMAT in (0, 6, 8, 9, 10, 11, 12, 13, 18, 20, 26, 27, 28, 30, 37, 38, 39, 40, 44,
              50, 51, 52, 53, 55, 59, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 75, 76,
              77, 78, 80, 81, 83, 85, 90, 92, 93, 94):
    print("a BEDMAT value of '" + str(BEDMAT) + "' is not generally a good idea. Just saying.")

# assemble the material dictionaries
BEDINFO = {'B': BEDMAT, 'D': BEDDATA}
PILLARINFO = {'B': PILLARMAT, 'D': PILLARDATA}
LIGHTINFO = {'B': LIGHTMAT, 'D': LIGHTDATA}
POWERINFO = {'B': 76, 'D': 5}
AIRINFO = {'B': 0, 'D': 0}

LIGHT_REDUCTION_DICT = {0: 0, 8: 2, 18: 1, 20: 0, 27: 0, 28: 0, 37: 0, 38: 0, 39: 0, 40: 0,
                        50: 0, 51: 0, 52: 0, 63: 0, 64: 0, 65: 0, 66: 0, 68: 0, 69: 0,
                        70: 0, 71: 0, 72: 0, 75: 0, 76: 0, 77: 0, 78: 1, 79: 2, 83: 1, 85: 0}
LUMINANCE_DICT = {51: 15, 91: 15, 10: 15, 11: 15, 89: 15, 95: 15, 50: 14, 62: 13,
                  90: 11, 74: 9, 94: 9, 76: 7}

# absolute vertical limits of the map
MAPBTM = 0
# user-facing coordinates go down to -64, so add 65 to compensate
Y += 65

# The following is an interface class for .mclevel data for minecraft savefiles.
# The following also includes a useful coordinate to index convertor and several
# other useful functions.

import mcInterface


# This is the end of the MCLevel interface.

# Now, on to the actual code.

NON_SUPPORTING_BLOCKS = {0, 6, 8, 9, 10, 11, 18, 20, 37, 38, 39, 40, 50, 51, 59, 90}

def get_surface(x, y, z, mclevel: mcInterface.SaveFile):
    """Return the Y position of the highest 'solid' block at or below x,y,z."""
    hmnl = mclevel.get_heightmap(x, z, "MOTION_BLOCKING_NO_LEAVES")
    hmof = mclevel.get_heightmap(x, z, "OCEAN_FLOOR")
    if (hmnl is None) or (hmof is None): return None
    surf_height = min(hmnl, hmof)
    if y > surf_height: return surf_height
    get_block = mclevel.block
    while y > MAPBTM:
        info = get_block(x, y, z)
        if info is None: return None
        if info not in NON_SUPPORTING_BLOCKS: break
        y -= 1
    return y


def lay_the_rail(mclevel):
    """Increment over the rail positions and call the appropriate create functions when needed."""
    # some more useful globals
    RAIL_DATA_DICT = {'X': 1, 'Z': 0}
    RAIL_DATA = RAIL_DATA_DICT[DIRECTION[1]]
    INCREMENT_DICT = {'-': -1, '+': 1}
    INCREMENT = INCREMENT_DICT[DIRECTION[0]]
    # the position vector is [x, y, z]
    DIRECTION_AXIS_DICT = {'X': 0, 'Z': 2}
    DIRECTION_AXIS = DIRECTION_AXIS_DICT[DIRECTION[1]]
    SIDE_DIRECTION_AXIS_DICT = {'X': 2, 'Z': 0}
    SIDE_DIRECTION_AXIS = SIDE_DIRECTION_AXIS_DICT[DIRECTION[1]]
    # localize set block
    set_block = mclevel.set_block
    # make a lighting update list
    light_emit_list = []
    # x is 0 and z is 2 in the position list
    position = [X, Y, Z]
    for total_dist in range(DISTANCE):
        x, y, z = position
        # find the existing height of the land
        top_y = y + TUNNELHEIGHT - 1
        surface_height = get_surface(x, top_y, z, mclevel)
        if surface_height is None:
            print("The rail ran off the edge of the map or something!")
            break
        # place the rail bed
        set_block(x, y - 1, z, BEDINFO)
        # if the rail bed emits light, add it to the light_emit_list
        if BEDMAT in LUMINANCE_DICT: light_emit_list += [(x, y, z)]
        # place the lighting
        if LIGHTSPACING and (total_dist % LIGHTSPACING == 0):
            # copy the current position
            side_pos = position[:]
            # put it on the opposite side as the rail power
            side_pos[SIDE_DIRECTION_AXIS] += -INCREMENT
            # set the light block
            set_block(side_pos[0], side_pos[1], side_pos[2], LIGHTINFO)
            # add the light block to the light emit list
            light_emit_list += [(side_pos[0], side_pos[1], side_pos[2])]
            # move the position to the block below the light
            side_pos[1] += -1
            # and add a light support block
            set_block(side_pos[0], side_pos[1], side_pos[2], BEDINFO)
        # place the rail
        this_rail_data = RAIL_DATA
        if POWERSPACING and total_dist % POWERSPACING == 0:
            # set the rail value
            rail_value = 27
            # turn the rail on
            this_rail_data += 8
            side_pos = position[:]
            # place the redstone torch
            side_pos[SIDE_DIRECTION_AXIS] += INCREMENT
            set_block(side_pos[0], side_pos[1], side_pos[2], POWERINFO)
            # add the torch to the lighting update list
            light_emit_list += [(side_pos[0], side_pos[1], side_pos[2])]
            # place the block supporting the redstone torch
            side_pos[1] += -1
            set_block(side_pos[0], side_pos[1], side_pos[2], BEDINFO)
        else:
            # place a normal rail block
            rail_value = 66
        rail_info = {'B': rail_value, 'D': this_rail_data}
        # actually place the rail block
        set_block(x, y, z, rail_info)
        # place the tunnel or pillars
        if surface_height > y:
            # make a tunnel
            if VERBOSE:
                print("Position " + str(position) + " is a tunnel")
            for cur_y in range(y + 1, y + TUNNELHEIGHT):
                set_block(x, cur_y, z, AIRINFO)
        # if you don't make a tunnel, check if you need supports
        elif (surface_height < y - 2 and
              PILLARSPACING and
              (total_dist % PILLARSPACING == 0)):
            # make pillars
            if VERBOSE:
                print("Position " + str(position) + " has a pillar")
            for cur_y in range(surface_height, y - 1):
                set_block(x, cur_y, z, PILLARINFO)
        else:
            if VERBOSE:
                print("Position " + str(position) + " is just normal")
        # increment position
        position[DIRECTION_AXIS] += INCREMENT
    # when we're all done, return the list of blocks that emit light
    return light_emit_list


def main(the_map):
    """Load the file, create the rail line, and save the new file.
    """
    print("Laying the rail")
    lights = lay_the_rail(the_map)
    return lights


def standalone():
    print("Importing the map")
    try:
        the_map = mcInterface.SaveFile(LOADNAME)
    except IOError:
        print('File name invalid or save file otherwise corrupted. Aborting')
        return None
    main(the_map)
    print("Saving the map (can also take a while)")
    the_map.write()
    if VERBOSE:
        print("finished")
        input("press Enter to close")


if __name__ == '__main__':
    standalone()
