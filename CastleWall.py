# Version 2
"""This takes a MineCraft level and builds a castle wall around the player.

The wall follows the terrain, with crenellated battlements, a walkway
along the inside, and occasional stairs up from the courtyard.

Written by Paul Spooner, with God's help.
See more at: http://www.peripheralarbor.com/minecraft/minecraftscripts.html
"""

# Here are the variables you can edit.

# This is the name of the map to edit.
# Make a backup if you are experimenting!

LOAD_NAME = "TestB"

# The walled area is centered on the player

# How large (maximum) do you want the walled area?
# for example, RADIUS = 10 will make a 21 block diameter walled area
# on level ground.
# The script tries to match the wall to the terrain,
# so the size will be much smaller on slopes.
RADIUS = 19.5

# How tall do you want the wall, up to the walkway?
# Crenellations sit on top of this.
# default 5
HEIGHT = 5

# How thick should the wall be?
# 1 is a single row of blocks (tight, walk in the crenels)
# 2 is an outer battlement plus an inner walkway (default)
# 3 is a spacious rampart
WALL_THICKNESS = 2

# How much do you want the courtyard flattened?
# the height differences in the terrain inside the
# wall will be divided by FLATTENING
# This does not flatten the walls; they still follow the land.
# for no flattening, set to 1
# default is 2.618
FLATTENING = 2.618

# What material should the wall be made from?
WALL_INFO = {'B': 'minecraft:' + 'stone_bricks'}

# if you need more blocks, what should you fill with?
# Used under the wall as a foundation, and under stair runs.
FILL_INFO = {'B': 'minecraft:' + 'stone'}

# What stairs should lead up to the walkway?
# facing is filled in when they are placed.
STAIR_INFO = {'B': 'minecraft:stone_brick_stairs', 'half': 'bottom', 'facing': 'east'}


#####################
# Advanced options! #
#####################

# What is the maximum vertical distance the walled zone should jump over?
# If there's a ditch or cliff higher than MAXVERTICALGAP
# the wall will not extend beyond it.
# Set higher if you don't mind large vertical cliffs inside your base.
# You may also need to set RADIUS high, in order to push it over the edge.
# default 3
MAXVERTICALGAP = 3

# Do you want crenellations (merlons and crenels) on top of the wall?
# True makes a battlement (default)
# False leaves a solid parapet
CRENELLATED = True

# How wide should each merlon (the raised bit) be, in blocks?
# default 2
MERLON_WIDTH = 2

# How wide should each crenel (the gap you look through) be, in blocks?
# default 2
CRENEL_WIDTH = 2

# How tall should the merlons be, above the walkway?
# 2 is a full-height merlon you can take cover behind (default)
MERLON_HEIGHT = 2

# How tall should the parapet be in the crenels, above the walkway?
# 1 is a chest-high wall you can see over (default)
# 0 is an open gap
CRENEL_HEIGHT = 1

# How often do you want stairs from the courtyard up to the walkway?
# This is a spacing around the perimeter, in wall columns.
# 8 is frequent, 16 is occasional, 24 is sparse.
# default 12
STAIR_SPACING = 12

# How deep should the foundation go below the local ground?
# Helps the wall not hover over little dips.
# default 2
FOUNDATION = 2

# How much should the walkway height be smoothed along the wall?
# 0 follows every bump in the land.
# 2 is a gentle rampart that still follows hills (default)
# 5 is a very even walkway
WALL_SMOOTHING = 2

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
    print("HEIGHT is less than 1, setting it to 5")
    HEIGHT = 5
if FLATTENING < 1:
    print("FLATTENING is less than one, setting to one")
    FLATTENING = 1
WALL_THICKNESS = int(WALL_THICKNESS)
if WALL_THICKNESS < 1:
    WALL_THICKNESS = 1
if MERLON_WIDTH < 1:
    MERLON_WIDTH = 1
if CRENEL_WIDTH < 0:
    CRENEL_WIDTH = 0
if MERLON_HEIGHT < 0:
    MERLON_HEIGHT = 0
if CRENEL_HEIGHT < 0:
    CRENEL_HEIGHT = 0
if STAIR_SPACING < 4:
    STAIR_SPACING = 4
if FOUNDATION < 0:
    FOUNDATION = 0
if WALL_SMOOTHING < 0:
    WALL_SMOOTHING = 0
if CRENELLATED not in (True, False):
    CRENELLATED = True
if VERBOSE not in (True, False):
    VERBOSE = False


# The following is an interface class for .mclevel data for minecraft savefiles.
import mcInterface

# Map height limits
# gets clobbered from the map height data on map import
MAPTOP = mcInterface.SaveFile.map_height
MAPBTM = mcInterface.SaveFile.map_bottom

# Now, on to the actual code.

from math import sqrt, atan2

AIR_INFO = {'B': 'minecraft:air'}
CARDINAL = ((1, 0), (-1, 0), (0, 1), (0, -1))
DIR_FACING = {(1, 0): 'east', (-1, 0): 'west', (0, 1): 'south', (0, -1): 'north'}


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


class WallColumn(object):
    """One column of the castle wall, including walkway height."""

    def __init__(self, x, z, orig_y):
        self.x = x
        self.z = z
        # orig_y is the heightmap value (first air above the ground)
        self.orig_y = orig_y
        self.walk_top = orig_y + HEIGHT
        self.is_outer = False
        self.is_inner = False
        self.is_corner = False
        self.inwards = []


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

    def lookup_square(self, x, z):
        """Return the Square at x, z from interior or outside, or None."""
        loc = coords_to_loc((x, z))
        if loc in self.interior:
            return self.interior[loc]
        if loc in self.outside:
            return self.outside[loc]
        return None

    def column_orig_y(self, x, z):
        """Original heightmap Y at x, z, before courtyard flattening."""
        square = self.lookup_square(x, z)
        if square is not None and square.y is not None:
            return square.y
        return self.save_file.get_heightmap(x, z, "MOTION_BLOCKING_NO_LEAVES")

    def cardinal_inward(self, x, z):
        """Directions from this wall square into the courtyard."""
        dirs = []
        for dx, dz in CARDINAL:
            loc = coords_to_loc((x + dx, z + dz))
            if loc in self.interior:
                dirs.append((dx, dz))
        if dirs:
            return dirs
        # fallback: step toward the origin
        ox = self.origin.x - x
        oz = self.origin.z - z
        if ox == 0 and oz == 0:
            return [(0, 1)]
        if abs(ox) >= abs(oz):
            return [(1 if ox > 0 else -1, 0)]
        return [(0, 1 if oz > 0 else -1)]

    def gather_wall_columns(self):
        """Build the thick wall ring from the outside perimeter, inward."""
        columns = {}

        def add_col(x, z, orig_y, outer=False, inner=False, inward=None):
            if orig_y is None:
                return None
            key = (x, z)
            col = columns.get(key)
            if col is None:
                col = WallColumn(x, z, orig_y)
                columns[key] = col
            if outer:
                col.is_outer = True
            if inner:
                col.is_inner = True
            if inward is not None and inward not in col.inwards:
                col.inwards.append(inward)
            return col

        for square in self.outside.values():
            if square.y is None:
                continue
            dirs = self.cardinal_inward(square.x, square.z)
            corner = len(dirs) != 1
            for d in dirs:
                dx, dz = d
                for offset in range(WALL_THICKNESS):
                    x = square.x + dx * offset
                    z = square.z + dz * offset
                    orig_y = self.column_orig_y(x, z)
                    add_col(x, z, orig_y,
                            outer=(offset == 0),
                            inner=(offset == WALL_THICKNESS - 1),
                            inward=d)
            key = (square.x, square.z)
            if corner and key in columns:
                columns[key].is_corner = True
        return columns

    def smooth_walkway(self, columns):
        """Ease the walkway along the wall so it ramps with the land."""
        keys = list(columns.keys())
        for _ in range(int(WALL_SMOOTHING)):
            new_tops = {}
            for key in keys:
                col = columns[key]
                ys = [col.walk_top]
                for dx, dz in CARDINAL:
                    nb = columns.get((col.x + dx, col.z + dz))
                    if nb is not None:
                        ys.append(nb.walk_top)
                new_tops[key] = int(sum(ys) / float(len(ys)) + 0.5)
            for key, top in new_tops.items():
                floor_min = columns[key].orig_y + 2
                columns[key].walk_top = max(top, floor_min)
        # keep neighboring walkway heights a 1-block step apart
        for _ in range(WALL_THICKNESS + 4):
            changed = False
            for col in columns.values():
                for dx, dz in CARDINAL:
                    nb = columns.get((col.x + dx, col.z + dz))
                    if nb is None:
                        continue
                    if nb.walk_top > col.walk_top + 1:
                        col.walk_top = nb.walk_top - 1
                        changed = True
            if not changed:
                break
        for col in columns.values():
            if col.walk_top > MAPTOP - MERLON_HEIGHT - 1:
                col.walk_top = MAPTOP - MERLON_HEIGHT - 1

    def merlon_at(self, col):
        """True if this outer column should get a raised merlon."""
        if not CRENELLATED:
            return True
        if col.is_corner:
            return True
        period = MERLON_WIDTH + CRENEL_WIDTH
        if period < 1:
            return True
        if col.inwards:
            dx, dz = col.inwards[0]
            along = col.z if dx != 0 else col.x
        else:
            along = col.x + col.z
        return (along % period) < MERLON_WIDTH

    def clear_above(self, x, y_start, z):
        """Clear existing blocks from y_start up to the current surface."""
        top = self.save_file.get_heightmap(x, z, "WORLD_SURFACE")
        if top is None:
            return None
        set_block = self.save_file.set_block
        if y_start < top:
            for this_y in range(y_start, top):
                set_block(x, this_y, z, AIR_INFO)
            self.save_file.decrease_all_heightmaps(x, y_start, z)
        return True

    def flatten_courtyard(self, wall_keys):
        """Flatten the bailey, leaving wall-thickness columns alone."""
        origin_y = self.origin.y
        set_block = self.save_file.set_block
        for square in self.interior.values():
            y = square.y
            if y is None:
                continue
            x = square.x
            z = square.z
            if (x, z) in wall_keys:
                continue
            original_y_diff = origin_y - y
            scaled_y_diff = int(0.5 + original_y_diff / FLATTENING)
            new_y = origin_y - scaled_y_diff
            y_change = new_y - y
            if y_change < 0:
                top_y = self.save_file.get_heightmap(x, z)
                for this_y in range(new_y, top_y):
                    set_block(x, this_y, z, AIR_INFO)
                self.save_file.decrease_all_heightmaps(x, new_y, z)
            elif y_change > 0:
                for this_y in range(y, new_y):
                    set_block(x, this_y, z, FILL_INFO)
                self.save_file.increase_all_heightmaps(x, new_y, z)
            square.y = new_y
            if VERBOSE:
                print("change was " + str(y_change) + " at coordinates " + str((x, z)),
                      'with a final y value of', new_y)

    def build_column(self, col, columns):
        """Place foundation, wall body, walkway, and battlement for one column."""
        x = col.x
        z = col.z
        walk_top = col.walk_top
        set_block = self.save_file.set_block
        low = col.orig_y
        for dx, dz in CARDINAL:
            nb = columns.get((x + dx, z + dz))
            if nb is not None:
                low = min(low, nb.orig_y)
        bottom = low - FOUNDATION
        if bottom < MAPBTM:
            bottom = MAPBTM
        surface = col.orig_y
        # solid body: foundation up through the walkway floor
        for this_y in range(bottom, walk_top):
            if this_y < surface - 1:
                set_block(x, this_y, z, FILL_INFO)
            else:
                set_block(x, this_y, z, WALL_INFO)
        self.clear_above(x, walk_top, z)
        if col.is_outer:
            parapet = CRENEL_HEIGHT
            if self.merlon_at(col):
                parapet = max(parapet, MERLON_HEIGHT)
            for i in range(parapet):
                set_block(x, walk_top + i, z, WALL_INFO)
            self.save_file.increase_all_heightmaps(x, walk_top + parapet, z)
        else:
            # inner walkway: headroom so you can walk it
            for this_y in range(walk_top, walk_top + 3):
                set_block(x, this_y, z, AIR_INFO)
            self.save_file.increase_all_heightmaps(x, walk_top, z)

    def place_walkway_steps(self, columns):
        """Turn 1-block walkway height changes into stairs."""
        set_block = self.save_file.set_block
        for col in columns.values():
            if col.is_outer and WALL_THICKNESS > 1:
                # keep the outer battlement as full blocks
                continue
            for dx, dz in CARDINAL:
                nb = columns.get((col.x + dx, col.z + dz))
                if nb is None:
                    continue
                if nb.walk_top == col.walk_top + 1:
                    info = STAIR_INFO.copy()
                    info['facing'] = DIR_FACING[(dx, dz)]
                    set_block(col.x, col.walk_top - 1, col.z, info)
                    break

    def place_access_stairs(self, columns):
        """Build occasional stair runs from the courtyard up to the walkway."""
        ox = self.origin.x
        oz = self.origin.z
        inners = [c for c in columns.values()
                  if c.is_inner and len(c.inwards) == 1]
        inners.sort(key=lambda c: atan2(c.z - oz, c.x - ox))
        placed = 0
        set_block = self.save_file.set_block
        for i, col in enumerate(inners):
            if STAIR_SPACING > 0 and (i % STAIR_SPACING) != 0:
                continue
            dx, dz = col.inwards[0]
            loc = coords_to_loc((col.x + dx, col.z + dz))
            if loc not in self.interior:
                continue
            if (col.x + dx, col.z + dz) in columns:
                continue
            court = self.interior[loc]
            if court.y is None:
                continue
            court_y = court.y
            rise = col.walk_top - court_y
            if rise < 2:
                continue
            # make sure the whole run stays in the courtyard
            blocked = False
            for k in range(1, rise + 1):
                px = col.x + dx * k
                pz = col.z + dz * k
                if (px, pz) in columns:
                    blocked = True
                    break
                ploc = coords_to_loc((px, pz))
                if ploc not in self.interior:
                    blocked = True
                    break
            if blocked:
                continue
            facing = DIR_FACING[(-dx, -dz)]
            info = STAIR_INFO.copy()
            info['facing'] = facing
            for k in range(1, rise + 1):
                px = col.x + dx * k
                pz = col.z + dz * k
                py = col.walk_top - 1 - k
                # fill under the stair so it does not float
                for fy in range(court_y - 1, py):
                    set_block(px, fy, pz, FILL_INFO)
                set_block(px, py, pz, info)
                for ay in range(py + 1, py + 4):
                    set_block(px, ay, pz, AIR_INFO)
                self.save_file.decrease_all_heightmaps(px, py + 1, pz)
                self.save_file.increase_all_heightmaps(px, py + 1, pz)
            placed += 1
            if VERBOSE:
                print("Stairs up to walkway at", col.x, col.z, "rise", rise)
        return placed

    def create(self):
        if VERBOSE:
            print(len(self.interior), 'interior squares')
            print(len(self.outside), 'perimeter squares')
        columns = self.gather_wall_columns()
        if VERBOSE:
            print(len(columns), 'wall columns (thickness', WALL_THICKNESS, ')')
        self.smooth_walkway(columns)
        self.flatten_courtyard(set(columns.keys()))
        if VERBOSE:
            print("Building crenellated walls")
        for col in columns.values():
            self.build_column(col, columns)
        self.place_walkway_steps(columns)
        n_stairs = self.place_access_stairs(columns)
        print("Built {0} wall columns, {1} stair runs to the walkway".format(
            len(columns), n_stairs))

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
    print("Flattening courtyard and raising crenellated walls")
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
