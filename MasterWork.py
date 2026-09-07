# Version 2
"""Chain the other scripts into one build on a single open save.

The default recipe, around the player:
- lift a wizard mountain
- crater the ground beneath it (without chewing the peak)
- plant a ring of huge trees around the crater
- open and connect nearby caves
- crown the peak with a crenellated castle
- sweep the ores out of the mountain and stash them in courtyard chests
- throw powered-rail bridges out from the castle in the four cardinals

Each step is optional. Each step is just a call to that script's
main(the_map, origin=..., **settings). You can rearrange them or
write your own recipe the same way.

Import and call main(the_map, origin=..., **settings) to use as a module;
main does not save. standalone() loads, runs, and writes.

Written by Paul Spooner, with God's help.
See more at: http://www.peripheralarbor.com/minecraft/minecraftscripts.html
"""

# Here are the variables you can edit.

# This is the name of the map to edit.
# Make a backup if you are experimenting!
LOAD_NAME = "TestB"

# Which steps to run, in this order.
DO_MOUNTAIN = True
DO_CRATER = True
DO_TREES = True
DO_CAVES = True
DO_CASTLE = True
DO_ORE = True
DO_BRIDGES = True

# ---- WizardMountain ----
MOUNTAIN_RADIUS = 28
MOUNTAIN_HEIGHT = 29
MOUNTAIN_DEPTH_SCALE = 1.0

# ---- StarStone crater under the mountain ----
# Keep this modest so the blast stays below the floating peak.
# ON_SURFACE is forced False: the crater uses the original ground Y.
CRATER_DEPTH = 12
CRATER_WIDTH_MULTIPLE = 2.2
CRATER_EJECTA = False

# ---- Forester ring around the crater ----
TREE_COUNT = 12
TREE_SHAPE = "round"
TREE_CENTER_HEIGHT = 40
TREE_EDGE_HEIGHT = 24
# Plant outside the mountain footprint so they stand on the old ground.
TREE_CLEAR_RADIUS = 30
TREE_RING_WIDTH = 18

# ---- CaveDiver around the same area ----
CAVE_RADIUS = 48
CAVE_MOUTHS = 4
CAVE_SHAFTS = 3
CAVE_CONNECTIONS = 6

# ---- CastleWall on the peak ----
# Same XZ as the mountain; the heightmap is now the lifted summit.
CASTLE_RADIUS = 10
CASTLE_HEIGHT = 6
CASTLE_THICKNESS = 2

# ---- OreReduce, then chests in the courtyard ----
# SEARCHSIZE is in chunks around the origin (1 = 9 chunks, 2 = 25).
ORE_SEARCHSIZE = 2
ORE_FRACTION = 0.4

# ---- LineRail bridges out from the castle ----
# One bridge in each cardinal, starting just outside the wall.
BRIDGE_DISTANCE = 36
BRIDGE_HEIGHT = 3
BRIDGE_PILLAR_SPACING = 4
BRIDGE_LIGHT_SPACING = 8
BRIDGE_DIRECTIONS = ('+X', '-X', '+Z', '-Z')

# Do you want a bunch of info on what's going on?
VERBOSE = False

##############################################################
#  Don't edit below here unless you know what you are doing  #
##############################################################

import mcInterface
import WizardMountain
import StarStone
import Forester
import CaveDiver
import CastleWall
import OreReduce
import LineRail

CHEST_INFO = {'B': 'minecraft:chest', 'facing': 'south'}
BRIDGE_BED = {'B': 'minecraft:stone_bricks'}
BRIDGE_PILLAR = {'B': 'minecraft:stone_bricks'}


def _validate():
    global MOUNTAIN_RADIUS, MOUNTAIN_HEIGHT, CRATER_DEPTH, TREE_COUNT
    global CAVE_RADIUS, CASTLE_RADIUS, CASTLE_HEIGHT
    global ORE_SEARCHSIZE, ORE_FRACTION, BRIDGE_DISTANCE
    if MOUNTAIN_RADIUS < 1:
        MOUNTAIN_RADIUS = 1
    if MOUNTAIN_HEIGHT < 1:
        MOUNTAIN_HEIGHT = 1
    if CRATER_DEPTH < 1:
        CRATER_DEPTH = 1
    if TREE_COUNT < 0:
        TREE_COUNT = 0
    if CAVE_RADIUS < 8:
        CAVE_RADIUS = 8
    if CASTLE_RADIUS < 1:
        CASTLE_RADIUS = 1
    if CASTLE_HEIGHT < 1:
        CASTLE_HEIGHT = 1
    if ORE_SEARCHSIZE < 0:
        ORE_SEARCHSIZE = 0
    if ORE_FRACTION <= 0:
        ORE_FRACTION = 0.4
    if ORE_FRACTION > 1:
        ORE_FRACTION = 1
    if BRIDGE_DISTANCE < 1:
        BRIDGE_DISTANCE = 1

_validate()


def configure(**settings):
    """Permanently set this script's options (the uppercase names above)."""
    mcInterface.apply_settings(globals(), settings)


def extracted_to_items(extracted):
    """Turn {block_name: count} into a list of chest item stacks (64 max)."""
    items = []
    for name, count in sorted(extracted.items(), key=lambda kv: (-kv[1], kv[0])):
        left = int(count)
        while left > 0:
            stack = 64 if left > 64 else left
            items.append({'id': 'minecraft:' + name, 'count': stack})
            left -= stack
    return items


def chest_spots(ox, y, oz):
    """Courtyard chest positions around the origin, facing inward."""
    return [
        (ox + 2, y, oz, 'west'),
        (ox - 2, y, oz, 'east'),
        (ox, y, oz + 2, 'north'),
        (ox, y, oz - 2, 'south'),
        (ox + 2, y, oz + 2, 'west'),
        (ox - 2, y, oz + 2, 'east'),
        (ox + 2, y, oz - 2, 'west'),
        (ox - 2, y, oz - 2, 'east'),
        (ox + 3, y, oz, 'west'),
        (ox - 3, y, oz, 'east'),
        (ox, y, oz + 3, 'north'),
        (ox, y, oz - 3, 'south'),
    ]


def place_castle_chests(the_map, origin, extracted):
    """Fill courtyard chests with the ore OreReduce pulled out."""
    items = extracted_to_items(extracted)
    if not items:
        print("No ore to stash")
        return []
    ox, oz = origin[0], origin[2]
    cy = the_map.get_heightmap(ox, oz, "MOTION_BLOCKING_NO_LEAVES")
    if cy is None:
        print("Could not find the courtyard floor for chests")
        return []
    spots = chest_spots(ox, cy, oz)
    placed = []
    slots = 27
    n_chests = (len(items) + slots - 1) // slots
    if n_chests > len(spots):
        print("Too much ore for {0} chests, filling {1} and dropping the rest".format(
            n_chests, len(spots)))
        n_chests = len(spots)
        items = items[:n_chests * slots]
    for i in range(n_chests):
        x, y, z, facing = spots[i]
        info = CHEST_INFO.copy()
        info['facing'] = facing
        the_map.set_block(x, y, z, info)
        the_map.increase_all_heightmaps(x, y + 1, z)
        batch = items[i * slots:(i + 1) * slots]
        the_map.set_container_items(x, y, z, batch)
        placed.append((x, y, z))
    print("Stashed {0} stacks in {1} courtyard chests".format(len(items), len(placed)))
    return placed


def walkway_y(the_map, origin):
    """First-air Y of the inner walkway, or the courtyard if that fails."""
    ox, oz = origin[0], origin[2]
    r = int(CASTLE_RADIUS) - int(CASTLE_THICKNESS)
    if r < 1:
        r = 1
    samples = []
    for dx, dz in ((r, 0), (-r, 0), (0, r), (0, -r)):
        y = the_map.get_heightmap(ox + dx, oz + dz, "MOTION_BLOCKING_NO_LEAVES")
        if y is not None:
            samples.append(y)
    if samples:
        return min(samples)
    y = the_map.get_heightmap(ox, oz, "MOTION_BLOCKING_NO_LEAVES")
    if y is None:
        return origin[1]
    return y


def lay_castle_bridges(the_map, origin):
    """Four powered-rail bridges out from the castle walls."""
    ox, oz = origin[0], origin[2]
    rail_y = walkway_y(the_map, origin)
    start_r = int(CASTLE_RADIUS) + 1
    laid = []
    for direction in BRIDGE_DIRECTIONS:
        dx, dz = 0, 0
        if direction == '+X':
            dx = start_r
        elif direction == '-X':
            dx = -start_r
        elif direction == '+Z':
            dz = start_r
        elif direction == '-Z':
            dz = -start_r
        start = [ox + dx, rail_y, oz + dz]
        print("Bridge {0} from {1}".format(direction, start))
        result = LineRail.main(
            the_map,
            origin=start,
            DIRECTION=direction,
            DISTANCE=BRIDGE_DISTANCE,
            TUNNELHEIGHT=BRIDGE_HEIGHT,
            PILLARSPACING=BRIDGE_PILLAR_SPACING,
            LIGHTSPACING=BRIDGE_LIGHT_SPACING,
            BEDINFO=BRIDGE_BED,
            PILLARINFO=BRIDGE_PILLAR,
            WALLOUTTHESE=['water', 'lava'],
            VERBOSE=VERBOSE,
        )
        laid.append({'direction': direction, 'start': start, 'result': result})
    return laid


def main(the_map, origin=None, **settings):
    """Run the selected steps on an open save. Does not load or save.

    origin: None (player), (x, z), or (x, y, z). Every step uses this
    column. The mountain lifts it; the crater uses the original Y;
    the castle follows the new heightmap at the same XZ.
    **settings: temporary overrides for this call, restored afterward
    Returns a dict of per-step results.
    """
    with mcInterface.temporary_settings(globals(), settings):
        origin = the_map.resolve_origin(origin)
        results = {'origin': origin}

        if DO_MOUNTAIN:
            print("=== Wizard mountain ===")
            results['mountain'] = WizardMountain.main(
                the_map,
                origin=origin,
                RADIUS=MOUNTAIN_RADIUS,
                HEIGHT=MOUNTAIN_HEIGHT,
                DEPTH_SCALE=MOUNTAIN_DEPTH_SCALE,
                VERBOSE=VERBOSE,
                MOVE_PLAYER=True,
            )

        if DO_CRATER:
            print("=== Crater beneath ===")
            results['crater'] = StarStone.main(
                the_map,
                origin=origin,
                FEATURE_NUM=1,
                RADIUS=0,
                CRATERS=True,
                BOULDERS=False,
                CRATER_DEPTH=CRATER_DEPTH,
                CRATER_DEPTH_DIAMETER_MULTIPLE=CRATER_WIDTH_MULTIPLE,
                CRATER_EJECTA=CRATER_EJECTA,
                ON_SURFACE=False,
                VERBOSE=VERBOSE,
            )

        if DO_TREES:
            print("=== Tree ring ===")
            results['trees'] = Forester.main(
                the_map,
                origin=origin,
                TREECOUNT=TREE_COUNT,
                SHAPE=TREE_SHAPE,
                CENTERHEIGHT=TREE_CENTER_HEIGHT,
                EDGEHEIGHT=TREE_EDGE_HEIGHT,
                PLANT_CLEAR_RADIUS=TREE_CLEAR_RADIUS,
                PLANT_RING_WIDTH=TREE_RING_WIDTH,
                VERBOSE=VERBOSE,
            )

        if DO_CAVES:
            print("=== Caves ===")
            results['caves'] = CaveDiver.main(
                the_map,
                origin=origin,
                RADIUS=CAVE_RADIUS,
                MOUTH_COUNT=CAVE_MOUTHS,
                SHAFT_COUNT=CAVE_SHAFTS,
                CONNECT_COUNT=CAVE_CONNECTIONS,
                VERBOSE=VERBOSE,
            )

        if DO_CASTLE:
            print("=== Castle on the peak ===")
            results['castle'] = CastleWall.main(
                the_map,
                origin=origin,
                RADIUS=CASTLE_RADIUS,
                HEIGHT=CASTLE_HEIGHT,
                WALL_THICKNESS=CASTLE_THICKNESS,
                VERBOSE=VERBOSE,
            )

        if DO_ORE:
            print("=== Ore into the keep ===")
            results['ore'] = OreReduce.main(
                the_map,
                origin=origin,
                SEARCHSIZE=ORE_SEARCHSIZE,
                FRACTION=ORE_FRACTION,
            )
            extracted = results['ore'].get('extracted') or {}
            results['chests'] = place_castle_chests(the_map, origin, extracted)

        if DO_BRIDGES:
            print("=== Bridges from the walls ===")
            results['bridges'] = lay_castle_bridges(the_map, origin)

        print("Master work complete")
        return results


def standalone():
    """Load the file, run every enabled step, and save once."""
    print("Importing the map")
    try:
        the_map = mcInterface.SaveFile(LOAD_NAME)
    except IOError:
        print("File name invalid or save file otherwise corrupted. Aborting")
        return None
    main(the_map)
    print("Saving the map (takes a bit)")
    if the_map.write():
        print("finished")
    else:
        print("saving went sideways somehow")
    if VERBOSE:
        input("press Enter to close")


if __name__ == "__main__":
    standalone()
