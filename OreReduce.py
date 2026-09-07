# Version 2
"""This takes a MineCraft level and changes the amount of materials present.
It is designed to shrink the amount of ore underground, but you can use it for
replacing any block type with any other block type.

Import and call main(the_map, origin=..., **settings) to use as a module;
main does not save. standalone() loads, runs, and writes.
"""

# The following is an interface class for .mclevel data for minecraft savefiles.
import mcInterface
from random import random


# Here are the variables you can edit.

# This is the name of the map to edit.
# Make a backup if you are experimenting!
LOADNAME = "TestB"

# the search will be around the player
# How large an area do you want to search?
# size is in chunks:
# 0 is just the chunk that the player is in
# 1 is the player's chunk + and - 1 chunk (so 9 total)
# 2 is 25 chunks centered on the player, etc
SEARCHSIZE = 1

# What block types do you want to affect, and by how much?
# This is a tuple or list of block types
# Default: mcInterface.blocktype_extractable
# which is all the ores
ALTER = mcInterface.blocktype_extractable

# What fraction of blocks do you want to replace?
# 1 will replace everything
# 0.5 will replace half
# Default: 0.4
FRACTION = 0.4

# What block type is the environment of the altered blocks?
# If an increase is indicated, only these types of blocks will be replaced
# if a decrease is indicated, these blocks will replace them.
# Default: mcInterface.blocktype_stones
# the script will attempt to use existing block types where they are already present
ENVIRONMENT = mcInterface.blocktype_stones

##############################################################
#  Don't edit below here unless you know what you are doing  #
##############################################################

def _validate():
    global SEARCHSIZE, FRACTION
    if SEARCHSIZE < 0:
        print("SEARCHSIZE was less than zero, setting to 0 and continuing on")
        SEARCHSIZE = 0
    if len(ALTER) < 1:
        print("There is nothing in ALTER, aborting!")
        raise IOError("ALTER empty, not looking for anything")
    if FRACTION <= 0:
        print("Please replace at least something!")
        raise IOError("FRACTION zero or less, not replacing anything")
    if FRACTION > 1:
        print("FRACTION greater than 1, setting to 1 and continuing on")
        FRACTION = 1

_validate()

# Now, on to the actual code.

def get_chunks(the_map, origin=None):
    all_chunks = []
    px, py, pz = the_map.resolve_origin(origin)
    locations = [(px,pz),]
    if SEARCHSIZE > 0:
        for i in range(SEARCHSIZE+1):
            xoff = i * 16
            for j in range(SEARCHSIZE+1):
                zoff = j * 16
                if xoff == zoff == 0:
                    continue

                locations += [(px+xoff,pz+zoff),]
                if xoff > 0:
                    locations += [(px - xoff, pz + zoff), ]
                if zoff > 0:
                    locations += [(px + xoff, pz - zoff), ]
                if xoff > 0 and zoff > 0:
                    locations += [(px - xoff, pz - zoff), ]
    for x,z in locations:
        possible_chunk = the_map.get_chunk_from_cord(x,z)
        if possible_chunk is None: continue
        all_chunks.append(possible_chunk)
    return all_chunks

def replace_section_materials(section, find, replace, fraction = 1):
    if 'block_states' not in section: return
    block_states = section['block_states'].payload
    palette = block_states['palette'].payload
    if 'data' in block_states:
        data = block_states['data']
    else:
        data = mcInterface.SaveFile.new_block_data()
        block_states['data'] = data
    # and unpack the block states if necessary
    if not hasattr(data, "unpacked"):
        mcInterface.SaveFile.unpack_block_states(data, palette)
    #search the pallete for the find values and make a list of indicies
    # search the pallete for the replace values, use the first one found
    find_indicies = []
    replaceidx = -1
    for i in range(len(palette)):
        block_name = palette[i].payload["Name"].payload.replace("minecraft:",'')
        if block_name in find:
            find_indicies.append(i)
        if replaceidx == -1 and block_name in replace:
            replaceidx = i
    # abort if there is nothing to find and replace
    if len(find_indicies) == 0: return
    if replaceidx == -1:
        # if no replacement material is found, add a new pallete entry
        mcInterface.SaveFile.add_block_data(mcInterface.SaveFile,palette, {'B':'minecraft:'+replace[0]})
        replaceidx = len(palette) - 1
    if fraction == 1:
        # if fraction is 1, do a pallete swap
        newpalletdata = palette[replaceidx]
        for i in find_indicies:
            palette[i] = newpalletdata
    else:
        # list comprehension find and replace and clobber the section block list
        data.unpacked = [replaceidx if (idx in find_indicies and random() < fraction)
                         else idx for idx in data.unpacked]

def replace_chunk_materials(chunk, find, replace, fraction):
    sections = chunk.tags[0].payload['sections'].payload
    for section in sections:
        replace_section_materials(section.payload, find, replace, fraction)

def configure(**settings):
    """Permanently set this script's options (the uppercase names above)."""
    mcInterface.apply_settings(globals(), settings)


def main(the_map, origin=None, **settings):
    """Replace materials on an open save. Does not load or save.

    origin: None (player), (x, z), or (x, y, z)
    **settings: temporary overrides for this call, restored afterward
    Returns a dict with origin and the number of chunks touched.
    """
    with mcInterface.temporary_settings(globals(), settings):
        origin = the_map.resolve_origin(origin)
        print("Finding the chunks")
        all_chunks = get_chunks(the_map, origin)
        print("Replacing the materials")
        for c in all_chunks:
            replace_chunk_materials(c, ALTER, ENVIRONMENT, FRACTION)
        return {'origin': origin, 'chunks': len(all_chunks)}


def standalone():
    """Load the file, do the stuff, and save the new file.
    """
    print("Importing the map")
    try:
        the_map = mcInterface.SaveFile(LOADNAME)
    except IOError:
        print('File name invalid or save file otherwise corrupted. Aborting')
        return None
    main(the_map)
    print("Saving the map (takes a bit)")
    the_map.write()
    print("finished")
    return None


if __name__ == '__main__':
    standalone()
