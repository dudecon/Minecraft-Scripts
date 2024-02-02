# Version 4
"""This takes a base MineCraft level and adds a powered rail.

Written by Paul Spooner, with God's help.
See more at: http://www.peripheralarbor.com/minecraft/minecraftscripts.html
"""

# Here are the variables you can edit.

# This is the name of the map to edit.
# Make a backup if you are experimenting!
LOADNAME = "TestB"

# starts at the player's location

# What direction do you want it to go from the starting block?
# '+X' will go in the positive x direction
# '-X' will go in the negative x direction
# '+Z' will go in the positive z direction
# '-Z' will go in the negative z direction
DIRECTION = '+X'

# How far do you want the rail to go?
DISTANCE = 20

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
bedname = 'stone_bricks'
BEDINFO = {"B":'minecraft:'+ bedname}

# How far apart do you want support pillars?
# These will be used to "support" the rail bed over valleys.
# Example: 5 will put four blank blocks between each pillar.
# if set to 0, it will make no pillars.
# Default, 8
PILLARSPACING = 4

# What material do you want the support pillars made of?
pillarname = 'quartz_pillar'
PILLARINFO = {"B":'minecraft:'+ pillarname, "axis":'y'}


# How far apart do you want the lights?
# like PILLARSPACING
# if set to 0, will make no lights
# Default, 8
LIGHTSPACING = 8

# What block do you want for the lights?
# Default, 50 (torches)
lightname = 'soul_torch'
LIGHTINFO = {"B":'minecraft:'+ lightname}

# what blocks do you want to wall out?
# leave empty to not check the walls for block types
WALLOUTTHESE = ['water', 'lava', 'milk']

# What block do you want for the tunnel walls?
wallname = 'glass'
WALLINFO = {"B":'minecraft:'+ wallname}


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
    print("Setting to +X and continuing")
    DIRECTION = '+X'
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


# assemble the material dictionaries

POWERINFO = {'B': 'redstone_block'}
AIRINFO = {'B': 'minecraft:air'}

# The following is an interface class for .mclevel data for minecraft savefiles.
# The following also includes a useful coordinate to index convertor and several
# other useful functions.

import mcInterface

# absolute vertical limits of the map
MAPBTM = mcInterface.SaveFile.map_bottom

# This is the end of the MCLevel interface.

# Now, on to the actual code.

NON_SUPPORTING_BLOCKS = (('air', 'water', 'lava', 'pointed_dripstone') + mcInterface.blocktype_shrooms +
                         mcInterface.blocktype_all_plants + mcInterface.blocktype_crops +
                         mcInterface.blocktype_crops + mcInterface.blocktype_leaves + mcInterface.blocktype_sands)

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
        blockstr = info['B'].replace('minecraft:', '')
        if blockstr not in NON_SUPPORTING_BLOCKS: break
        y -= 1
    return y


def lay_the_rail(mclevel):
    """Increment over the rail positions and call the appropriate create functions when needed."""
    # some more useful globals
    RAIL_DATA_DICT = {'Z': 'north_south', 'X': 'east_west'}
    RAIL_DATA = RAIL_DATA_DICT[DIRECTION[1]]
    rail_info = {'shape': RAIL_DATA, 'powered':'true'}

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
    position = [int(i) for i in mclevel.get_player_block()]
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
        #if BEDMAT in LUMINANCE_DICT: light_emit_list += [(x, y, z)]

        # place the rail
        if POWERSPACING and total_dist % POWERSPACING == 0:
            # set the rail value
            rail_value = 'minecraft:powered_rail'
            # turn the rail on
            side_pos = position[:]
            # place the redstone
            set_block(side_pos[0], side_pos[1] - 1, side_pos[2], POWERINFO)
        else:
            # place a normal rail block
            rail_value = 'minecraft:rail'
        rail_info['B'] = rail_value
        # actually place the rail block
        set_block(x, y, z, rail_info)
        # always clear the area above the rails
        for cur_y in range(y + 1, y + TUNNELHEIGHT):
            set_block(x, cur_y, z, AIRINFO)

        # place the tunnel walls
        if len(WALLOUTTHESE) > 0:
            # make a tunnel
            if VERBOSE:
                print("Position " + str(position) + " is a tunnel")
            # check the top
            coords_to_check = [(x,y+TUNNELHEIGHT,z)]
            # check the sides
            side_pos = position[:]
            side_pos[SIDE_DIRECTION_AXIS] += -INCREMENT
            coords_to_check += [(side_pos[0],iy,side_pos[2]) for iy in range(y, y + TUNNELHEIGHT)]
            side_pos[SIDE_DIRECTION_AXIS] += INCREMENT * 2
            coords_to_check += [(side_pos[0], iy, side_pos[2]) for iy in range(y, y + TUNNELHEIGHT)]

            wallit = False
            get_block = mclevel.block
            for c in coords_to_check:
                # get the block data
                info = get_block(c[0],c[1],c[2])
                if info is None: return None
                blockstr = info['B'].replace('minecraft:', '')
                if blockstr in WALLOUTTHESE:
                    wallit = True
                    break
            # if you find anything that needs walling out
            # build a tunnel
            if wallit:
                for c in coords_to_check:
                    set_block(c[0],c[1],c[2],WALLINFO)

        # place the pillars
        if surface_height > y:
            pass
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

        # place the lighting
        if LIGHTSPACING and (total_dist % LIGHTSPACING == 0):
            # copy the current position
            side_pos = position[:]
            # put it on the opposite side as the rail power
            side_pos[SIDE_DIRECTION_AXIS] += -INCREMENT
            # set the light block
            set_block(side_pos[0], side_pos[1], side_pos[2], LIGHTINFO)
            # add the light block to the light emit list
            # light_emit_list += [(side_pos[0], side_pos[1], side_pos[2])]
            # move the position to the block below the light
            side_pos[1] += -1
            # and add a light support block
            set_block(side_pos[0], side_pos[1], side_pos[2], BEDINFO)

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
