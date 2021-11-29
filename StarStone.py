# Version 8
'''This takes a base MineCraft level and adds boulders and craters.

Written by Paul Spooner, with God's help.
See more at: http://www.peripheralarbor.com/minecraft/minecraftscripts.html
'''

# Here are the variables you can edit.

# This is the name of the map to edit.
# Make a backup if you are experimenting!
LOADNAME = "TestWorld"

# How many boulders and/or craters do you want?
FEATURENUM = 7

# Where do you want the boulders/craters?
# X, and Z are the map coordinates
X = 295
Z = 396
# How large an area do you want them to be in?
# for example, RADIUS = 10 will place them randomly in
# a circular area 20 blocks wide.
RADIUS = 20
# NOTE: density will be higher in the center than at the edges.

# If you want boulders, set this to True, otherwise, set it to False
# If CRATERS is also True, the boulders will each be sitting in a crater
# defaults to obsidian, change material in the "Advanced options" section
BOULDERS = True

# How big do you want the boulders to be?
BOULDERSIZE = 7

# How much would you like the size of the boulders to vary?
# This value is a +- value, so with BOULDERSIZE = 5
# and BOULDERRANDOMIZATION = 3, the boulder size will range
# from 2 to 8
BOULDERRANDOMIZATION = 3

# Should boulders occasionally have treasure inside?  Ore, gold, diamond?
# Set to a number between 0 and 1 for some treasure.  Larger numbers creates
# more chance of exotic treasure
# for normal old boulders set to 0
BOULDERTREASURE = 0

# Should the boulders be scattered thruought the level vertically as well?
# Frees the boulders from the surface and makes them appear randomly in the 
# y axis as well.  This can result in boulders underground BURRIEDBOULDERS
# or floating in the air FLYINGBOULDERS
# If either is set to true, this will force CRATERS to turn off.
FLYINGBOULDERS = False
BURRIEDBOULDERS = False

# If you want craters set this to True, otherwise, set it to False.
# If BOULDERS is set, there will be a boulder in the middle of each crater.
CRATERS = True

# How deep should the craters be?
# Note, deeper is wider, and craters on level ground are generally
# 3 times wider than they are tall
# On uneven ground, however, this may vary
# NOTE: larger values take MUCH longer to process.
CRATERDEPTH = 10

# How much should the crater size vary?
# same principle as BOULDERRANDOMIZATION
DEPTHRANDOMIZATION = 5

#####################
# Advanced options! #
#####################

# What material would you like the boulders to be?
# Uses the minecraft index number.
# Default is 49 (Obsidian)
BOULDERMAT = 49

# what data value should the boulders have?
# defaults to 0
BOULDERDATA = 0

# In order, what do you want the common contents of the boulders to be?
# only used when BOULDERTREASURE is greater than zero
# default: [16,15,14] (coal ore, iron ore, gold ore)
TREASURELIST = [16,15,14]

# A list of the rare contents of boulders.
# The longer TREASURELIST is, the less often you will get one of these.
# default: [11,49,41,42,57,56,56,74,89,87]
# (lava, obsidian, gold block, iron block, diamond block,
# diamond ore (2x), redstone ore, glowstone, netherrack) 
TREASURERARE = [11,49,41,42,57,56,56,74,89,87]

# What size should the crater excavation sphere be?
# A multiple of the crater impact depth.
# Larger values result in wider craters.
# any positive value will work.
# examples:
# 0.5 will make a fully underground sphere hollowed out of the rock.
# 1.0 will make a "crater" cavity that just barely reaches the surface.
# 5.0 makes a pretty decent crater
# 8.0 will make a wide crater
# 100.0 will make a crater so wide, it's not even funny.
# NOTE: okay, maybe a little funny. Heh. Heheh; Such a big crater.
# NOTE: larger values take MUCH longer to process.
# Default 5
CRATERDEPTHDIAMETERMULTIPLE = 5

# Keep track of crater ejecta?
# This option can take a while on larger craters, but looks really cool!
# True displace blocks from inside the crater.
# False merely delete the blocks in the crater.
CRATEREJECTA = True

# How far should the ejecta be flung?
# This is a multiplier of the crater sphere diameter.
# Examples:
# 0.2 moves the material outward a bit, like hitting mud
# 1.0 makes a nice rim around the crater
# 3.0 scatters the material far and wide, like an explosion
# Default 1.1
EJECTADISTANCE = 1.1

# Add surface blocks? How Much? (intended for fire)
# any fractional value works here.
# Examples:
# 0 do not add surface blocks
# 0.1 adds to 1/10th of the blocks (sparse)
# 0.5 adds to half the blocks (thick)
# 1.0 (or more) adds to all of the blocks (complete)
SURFACEFRACTION = 0

# What block type should the surface blocks be?
# be sure to set SURFACEFRACTION above as well.
# Default is 51 (fire, makes a flaming crater!)
SURFACEMAT = 51

# What data value should the surface blocks have?
# defaults to 0
SURFACEDATA = 0

# Fill the crater with stuff?
# the value is the fraction of the crater depth (at the impact point)
# 0 do not fill the crater
# 0.4 fill the crater almost half full.
# 1.0 fill the crater up to the brim (may overflow on slopes)
# CRATERDEPTHDIAMETERMULTIPLE make a full sphere of fill material
# Default 0 (no fill)
CRATERFILL = 0.3
# NOTE: fill will be overwritten by ejecta if fill material is
# in the CRATERDESTROYS list.

# What material should the crater be filled with?
# Defaults to 11 (lava!)
FILLMAT = 11

# What data value should the fill blocks have?
# defaults to 0
FILLDATA = 0

# What materials should be ignored by craters?
# These materials will be destroyed rather than displaced.
# a list of material index types.
# default: [0,6,8,9,10,11,18,20,37,38,39,40,50,51,59,90]

CRATERDESTROYS = [0,6,8,9,10,11,18,20,37,38,39,40,50,51,59,90]

# Do you want something to look at while the script is running?
# True turns on lots of printouts on what the script is doing
# False leaves the extra data out
VERBOSE = False

##############################################################
#  Don't edit below here unless you know what you are doing  #
##############################################################

# input filtering
if FEATURENUM < 0:
    print("If you wanted less than one, you wouldn't have run the script.")
    print("Assuming one feature")
    FEATURENUM = 1
    
if BOULDERS:
    if BOULDERSIZE < 1:
        BOULDERSIZE = 1
    if BOULDERRANDOMIZATION < 0:
        BOULDERRANDOMIZATION = 0
    if BOULDERRANDOMIZATION > BOULDERSIZE:
        BOULDERRANDOMIZATION = BOULDERSIZE
    if BOULDERTREASURE < 0:
        BOULDERTREASURE = 0
    elif BOULDERTREASURE > 1:
        BOULDERTREASURE = 1
    if FLYINGBOULDERS or BURRIEDBOULDERS:
        CRATERS = False

if CRATERS:
    if CRATERDEPTH < 1:
        CRATERDEPTH = 1
    if DEPTHRANDOMIZATION < 0:
        DEPTHRANDOMIZATION = 0
    if DEPTHRANDOMIZATION > CRATERDEPTH:
        DEPTHRANDOMIZATION = CRATERDEPTH

if not (BOULDERS or CRATERS):
    print("wait, you want neither boulders nor craters?")
    print("Um, okay... doing nothing")

# assemble the material dictionaries
BOULDERINFO = {'B':BOULDERMAT,'D':BOULDERDATA}
SURFACEINFO = {'B':SURFACEMAT,'D':SURFACEDATA}
FILLINFO = {'B':FILLMAT,'D':FILLDATA}

# The following is an interface class for .mclevel data for minecraft savefiles.
# The following also includes a useful coordinate to index convertor and several
# other useful functions.

import mcInterface

# This is the end of the MCLevel interface.

# Now, on to the actual code.

from random import random, choice, sample
from math import sqrt, sin, cos, pi

def find_surface(x,y,z,mclevel):
    # move the block up or down until you hit something permiable
    # as defined in CRATERDESTROYS
    get_block = mclevel.block
    direction = 0
    while True:
        info = get_block(x,y,z)
        if info is None: return None
        if info in CRATERDESTROYS:
            if direction == 1:
                break
            direction = -1
            y += direction
            if y == -1: return None
        else:
            if direction == -1:
                y += 1
                break
            direction = 1
            y += direction
            if y == 128: return None
    return y

class PostEffect(object):
    '''keep track of which squares need to be relit, and then PostEffect them'''
    def add(self,x,z):
        coords = (x,z)
        self.all_columns.add(coords)
    def add_surface(self):
        mclevel = self.save_file
        get_height = mclevel.retrieve_heightmap
        set_block = mclevel.set_block
        for column_coords in self.all_columns:
            # randomly skip a fraction of the blocks
            if random() > SURFACEFRACTION: continue
            # add surface blocks above the top block
            x = column_coords[0]
            z = column_coords[1]
            # get the current heightmap
            cur_height = get_height(x,z)
            # find the true surface
            y = find_surface(x,cur_height,z,mclevel)
            if y is None: continue
            # set the block
            set_block(x,y,z,SURFACEINFO)
    def __init__(self):
        self.all_columns = set()
        self.save_file = None
    
PostEffect_master = PostEffect()

class SphereObject(object):
    '''A spherical object.
    
    It has a method to create itself.
    Designed for subclassing.
    '''
    def create(self,mclevel,log=False):
        locx = self.loc[0]
        locy = self.loc[1]
        locz = self.loc[2]
        diameter = self.size
        radius = self.size*0.5
        set_block = mclevel.set_block
        if log == True:
            block_list = []
        y_start = int(locy + self.bottom_offset)
        # cut off the sphere at the bottom
        if y_start < 0: y_start = 0
        y_end = int(locy + diameter + 1 - self.top_offset)
        # cut the sphere off at the top too.
        if y_end > 128: y_end = 128
        mat = self.mat
        for y in range(y_start,y_end):
            # pre-calculate the squared y distance
            sqr_dist_y = (locy + radius - y) **2
            if VERBOSE:
                print("Sphere processing y level " + str(y) )
            for x in range(int(locx - radius),
                       int(locx + radius + 1)
                        ):
                dist_2d = sqrt(
                        (locx - x)**2 + 
                        sqr_dist_y
                        )
                if dist_2d > radius:
                        continue
                sqr_dist_2d = dist_2d**2
                for z in range(int(locz - radius),
                       int(locz + radius + 1)
                        ):
                    dist = sqrt(
                        sqr_dist_2d + 
                        (locz - z)**2
                        )
                    if dist > radius:
                        continue
                    if log==True:
                        block_value = mclevel.block(x,y,z,'BD')
                        if block_value == None: continue
                        if block_value not in CRATERDESTROYS:
                            data = {'x':x, 'y':y,'z':z,'data':block_value}
                            block_list += [data]
                    set_block(x,y,z,mat)
        # set the columns to add post effects
        if SURFACEFRACTION:
            for x in range(int(locx - radius),
                           int(locx + radius + 1)):
                for z in range(int(locz - radius),
                           int(locz + radius + 1)):
                    dist = sqrt((locx - x)**2 + (locz - z)**2)
                    if dist > radius: continue
                    PostEffect_master.add(x,z)
        if log==True:
            return block_list
        else:
            return None
    
    def __init__(self, location=[0,0,0], mat={'B':0,'D':0}, size=-1):
        # self.loc is the location of the bottom of the sphere
        self.loc = location
        # self.size is the diameter of the sphere
        self.size = size
        # self.mat is the material dict to use for this object
        self.mat = mat
        # initialize the top and bottom offsets
        self.bottom_offset = 0
        self.top_offset = 0

class Boulder(SphereObject):
    '''A large roundish stone object.
    
    Has some material properties, and a method to create itself.
    '''
    def create(self,mclevel):
        SphereObject.create(self,mclevel)
        if BOULDERTREASURE:
            coresize = (0.618 + random())*self.size*0.5
            coreloc = self.loc[:]
            coreloc[1] += (self.size - coresize)* 0.5
            i = -1
            num_treasure = len(TREASURELIST)
            while True:
                if random() < BOULDERTREASURE:
                    i += 1
                else:
                    break
                if i == num_treasure:
                    break
            if i == -1: return
            elif i < num_treasure:
                coremat = TREASURELIST[i]
            else:
                coremat = choice(TREASURERARE)
            
            core = SphereObject(coreloc,{'B':coremat,'D':0},coresize)
            core.create(mclevel)       
            
    def __init__(self, location=[0,0,0], mat=BOULDERINFO, size=-1):
        SphereObject.__init__(self, location=location, mat = mat, size=size)
        # if size is not initialized, randomize it!
        if self.size == -1:
            sizemin = BOULDERSIZE - BOULDERRANDOMIZATION
            sizevary = BOULDERRANDOMIZATION * 2.
            size = sizemin + random()*sizevary
            self.size = size
    
class Crater(SphereObject):
    '''A large roundish hole in the ground.
    
    Has a method to create itself.
    '''
    
    def __init__(self, location=[0,0,0], depth=None):
        if depth is None:
            sizemin = CRATERDEPTH - DEPTHRANDOMIZATION
            sizevary = DEPTHRANDOMIZATION * 2.
            depth = (sizemin + random()*sizevary)
        self.depth = depth
        # set the size of the crater to a multiple of the depth
        size = depth * CRATERDEPTHDIAMETERMULTIPLE
        SphereObject.__init__(self, location=location, size=size)
    def toss_block(self,block,mclevel):
        # throw the block out of the crater
        x = block['x']
        y = block['y']
        z = block['z']
        #find the planar distance from the block to the center of the crater
        dist_x = x - self.loc[0]
        dist_z = z - self.loc[2]
        # if the block is right under the stone, ignore it and move on
        if dist_x == 0 and dist_z == 0: return None
        # how far is this, in a straight line?
        dist_mag = sqrt(dist_x**2 + dist_z**2)
        # how far should the block move?
        throw_distance = (self.size * 0.5 - dist_mag) * EJECTADISTANCE
        # it should move at least 1.5
        if throw_distance < 1.5: throw_distance = 1.5
        # how far should the block end up from the crater center,
        # compared to where it was before?
        difference_multiple = (dist_mag + throw_distance) / dist_mag
        # Multiply the distances, get the offsets from the block location
        offset_x = int( difference_multiple * dist_x )
        offset_z = int( difference_multiple * dist_z )
        # assign the new x and z
        x = self.loc[0] + offset_x
        z = self.loc[2] + offset_z
        # randomize the location, based on how far it moved
        random_dist = throw_distance * .618
        random_locs = [i for i in range(-int(random_dist),
                                        int(random_dist+1))]
        x += choice(random_locs)
        z += choice(random_locs)
        # Find the location on the surface
        y = find_surface(x,y,z,mclevel)
        if y is None: return None
        # slide downhill, away from the center of the crater
        # set up the kick values
        if dist_x == 0:
            x_kick = 0
        else:
            x_kick = int(dist_x / abs(dist_x))
        if dist_z == 0:
            z_kick = 0
        else:
            z_kick = int(dist_z / abs(dist_z))
        # find which is larger, x or z
        dist_ratio = abs(dist_x / (dist_z+.001))
        if dist_ratio > 2:
            # x is much larger, offset only x
            z_kick = 0
        elif dist_ratio < .5:
            # z is much larger, offset only z
            x_kick = 0
        # otherwise its about the same, offset both
        # keep kicking the block downhill
        new_x = x
        new_z = z
        while True:
            new_x += x_kick
            new_z += z_kick
            new_y = find_surface(new_x,y,new_z,mclevel)
            if new_y is None: return None
            if new_y >= y: break
            x = new_x
            y = new_y
            z = new_z
        # assign the block
        result = mclevel.set_block(x,y,z,block['data'])
        if SURFACEFRACTION:
            PostEffect_master.add(x,z)
        return result
        
    def create(self,mclevel):
        # excevate the crater
        # log the materials displaced if necessary
        block_log = SphereObject.create(self,mclevel,log=CRATEREJECTA)
        # fill the crater, if necessary
        if CRATERFILL:
            if VERBOSE: print('filling crater')
            fillsize = self.size
            fillloc = self.loc[:]
            filldepth = self.depth * CRATERFILL
            fill_object = SphereObject(fillloc,FILLINFO,fillsize)
            # the top offset will equal the sphere size (diameter)
            # minus the intended depth
            offset = int(fillsize - filldepth)
            fill_object.top_offset = offset
            fill_object.create(mclevel)
        # displace each block in the log
        if CRATEREJECTA:
            if VERBOSE: print('Displacing', len(block_log), 'blocks from a crater.')
            for block in block_log:
                self.toss_block(block, mclevel)

def selectlocations(mcmap):
    '''return a list of locations to put the objects on the surface of the map.
    '''
    assert isinstance(mcmap, mcInterface.SaveFile)
    featurelocs = []
    if VERBOSE: print('Locations: x, y, z')
    while len(featurelocs) < FEATURENUM:
        rad_fraction = random()
        # this is linear interpolation.
        # add other interpolation modes later
        rad = rad_fraction * RADIUS
        ang = random() * pi * 2
        x = X + int(rad * sin(ang) + .5)
        z = Z + int(rad * cos(ang) + .5)
        # check to see if this location is suitable
        y_top = mcmap.surface_block(x, z)
        if y_top is None:
            # this location is off the map!
            # Try somewhere else
            continue
        
        ychoices = [y_top["y"]]
        if BURRIEDBOULDERS:
            ychoices += [i for i in range(0, y_top['y'])]
        if FLYINGBOULDERS:
            ychoices += [i for i in range(y_top['y']+1, 128)]
        y = choice(ychoices)
        if CRATERS:
            y = find_surface(x,y,z,mcmap)
            depth = CRATERDEPTH + 2 * DEPTHRANDOMIZATION * (0.5 - random())
            y += -depth
        else:
            depth = 0
        if VERBOSE: print(x,y,z)
        featurelocs += [[x,y,z,depth]]
    return featurelocs
        

def main(the_map):
    '''create the craters and boulders.
    '''
    
    print("Selecting locations")
    locations = selectlocations(the_map)
    
    if CRATERS:
        print('Making craters')
        for loc in locations:
            print('Excavating' + str(loc))
            thiscrater = Crater(loc[:3],loc[3])
            thiscrater.create(the_map)
    
    if BOULDERS:
        print('Making boulders ')
        for loc in locations:
            thisboulder = Boulder(loc)
            thisboulder.create(the_map)
        print(' done')
    return None

def standalone():
    '''Load the file, call main, and save the new file'''
    if not (BOULDERS or CRATERS):
        print("wait, you want neither boulders nor craters?")
        print("Um, okay... doing nothing")
        return None
    print("Importing the map")
    try:
        the_map = mcInterface.SaveFile(LOADNAME)
    except IOError:
        print('File name invalid or save file otherwise corrupted. Aborting')
        return None
    main(the_map)
    PostEffect_master.save_file = the_map
    if SURFACEFRACTION:
        print("Adding surface blocks")
        PostEffect_master.add_surface()
    print("Saving the map (takes a bit)")
    the_map.write()
    if VERBOSE:
        print("finished")
        input('press Enter to close')
    return None
    

if __name__ == '__main__':
    standalone()
    
# Needed updates:
# make boulders able to be LUMPY (should be easy)
# 
