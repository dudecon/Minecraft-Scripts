'''This takes a base MineCraft level and adds or edits trees.  It then saves
the new map.
'''

# Here are the variables you can edit.

# this is the name of the map to load in
LOADNAME = "TreeBase.mclevel"

# this is the name of the map to save out when it is done
SAVENAME = "Trees.mclevel"

# What kind of operation would you like the forester to do?
# "clearcut" remove all logs (including ones not in trees!) and foliage.
# "conserve" re-form the existing trees, keeping the existing locations
# "replant" Erase the existing trees and plant new ones.
# "add" adds new trees to the existing ones, does not remove any trees
OPERATION = "replant"

# How many trees do you want, total?
# Set to 0 for no limit to existing trees, but no new trees will be added.
# To remove all trees, set OPERATION = "clearcut" above
# If more than TREECOUNT trees already exist, trees will be removed
# until TREECOUNT trees are left.
# Example:
# TREECOUNT = 15 will make sure only 15 trees are on the map
# NOTE: trees may be placed on top of eachother, so actual number of trees
# may be less for large values of TREECOUNT
# Also, if SHAPE = "rainforest" this is the number of tries.
# for rainforest, try large numbers, greater than 10000
TREECOUNT = 15

# Which shapes would you like the trees to be?
# these first three are best suited for small heights, from 5 - 10
# "normal" is the normal minecraft shape, it only gets taller and shorter
# "bamboo" a trunk with foliage, it only gets taller and shorter
# "palm" a trink with a fan at the top, only gets taller and shorter
# "stickly" selects randomly from "normal", "bamboo" and "palm"
# these last two are best suited for very large trees, heights greater than 8
# "round" procedural spherical shaped tree, can scale up to immense size
# "cone" procedural, like a pine tree, also can scale up to immense size
# "procedural" selects randomly from "round" and "conical"
# "rainforest" many slender trees, most at the lower range of the height,
# with a few at the upper end.
# "mangrove" makes mangrove trees in the water.
SHAPE = "procedural"


# What height should the trees be?
# Specifies the average height of the tree
# Examples:
# 5 is normal minecraft tree
# 3 is minecraft tree with foliage flush with the ground
# 10 is very tall trees, they will be hard to chop down
# NOTE: for round and conical, this affects the foliage size as well.
# NOTE:
# if OPERATION is "conserve" you can set this to "auto" to maintain
# the height of existing trees
HEIGHT = 25

# What should the variation in HEIGHT be?
# if HEIGHT is set to "auto" this only affects new trees
# actual value +- variation
# default is 1
# Example:
# HEIGHT = 8 and HEIGHTVARIATION = 3 will result in
# trunk heights from 5 to 11
# value is clipped to a max of HEIGHT, or for "auto", 5
# for a good rainforest, set this value not more than 1/2 of HEIGHT
HEIGHTVARIATION = 15


# Do you want branches, trunk, and roots?
# True makes all of that
# False does not create the trunk and branches, or the roots (even if they are
# enabled further down)
WOOD = True

# Trunk thickness multiplyer
# from zero (super thin trunk) to whatever huge number you can think of.
# Only works if SHAPE is "round" or "cone" or "procedural"
# Example:
# 1.0 is the default, it makes decently normal sized trunks
# 0.3 makes very thin trunks
# 3.0 makes a very thick trunk.
# 10.0 will make a huge thick trunk.  Not even kidding.  At this size
# you may as well just make an ugly brown cone instead of a tree.
TRUNKTHICKNESS = 1.0

# Trunk height, as a fraction of the tree
# Only works on "round" shaped trees
# Sets the height of the crown, where the trunk ends and splits
# Examples:
# 0.7 the default value, a bit more than half of the height
# 0.3 good for a fan-like tree
# 1.0 the trunk will extend to the top of the tree, and there will be no crown
# 2.0 the trunk will extend out the top of the foliage, making the tree appear
# like a cluster of green grapes impaled on a spike.
TRUNKHEIGHT = 0.7


# How many branches should there be?
# General multiplyer for the number of branches
# However, it will not make more branches than foliage clusters
# so to garuntee a branch to every foliage cluster, set it very high, like 10000
# this also affects the number of roots, if they are enabled.
# Examples:
# 1.0 is normal
# 0.5 will make half as many branches
# 2.0 will make twice as mnay branches
# 10000 will make a branch to every foliage cluster (I'm pretty sure)
BRANCHDENSITY = 1.0

# do you want roots from the bottom of the tree?
# Only works if SHAPE is "round" or "cone" or "procedural"
# "yes" roots will penetrate anything, and may enter underground caves.
# "tostone" roots will be stopped by stone.  There may be some penetration
# "hanging" will hang downward in air.  Good for "floating" type maps
# "no" roots will not be generated
ROOTS = "hanging"

# Do you want root buttresses?
# These make the trunk not-round at the base, seen in tropical or old trees.
# This option generally makes the trunk larger.
# Only works if SHAPE is "round" or "cone" or "procedural"
# Options:
# True makes root butresses
# False leaves them out
ROOTBUTTRESSES = True

# Do you want leaves on the trees?
# True there will be leaves
# False there will be no leaves
FOLIAGE = True

# How thick should the foliage be
# General multiplyer for the number of foliage clusters
# Examples:
# 1.0 is normal
# 0.3 will make very sparse spotty trees, half as many foliage clusters
# 2.0 will make dense foliage, better for the "rainforests" SHAPE
FOLIAGEDENSITY = 1.0


# Limit the tree height to the top of the map?
# True the trees will not grow any higher than the top of the map
# False the trees may be cut off by the top of the map
MAPHEIGHTLIMIT = True

# add torches in the middle of foliage clusters
# for those huge trees that get so dark underneath
# or for enchanted forests that should glow and stuff
# Only works if SHAPE is "round" or "cone" or "procedural"
# 0 makes just normal trees
# 1 adds one torch inside the foliage clusters for a bit of light
# 2 adds two torches around the base of each cluster, for more light
# 4 adds torches all around the base of each cluster for lots of light
LIGHTTREE = 0

# What kind of block should the trees be planted on?
# Use the Minecraft index.
# Examples
# 2 is grass (the default)
# 1 is stone (an odd choice)
# 12 is sand (for paradise levels)
# 9 is water (if you want an aquatic forest)
PLANTON = 2

##############################################################
#  Don't edit below here unless you know what you are doing  #
##############################################################

# input filtering
TREECOUNT = int(TREECOUNT)
if TREECOUNT < 0: TREECOUNT = 0
if SHAPE not in ["normal","bamboo","palm","stickly",
                 "round","cone","procedural",
                 "rainforest","mangrove"]:
    print("SHAPE not set correctly, using 'normal'.")
    SHAPE = "normal"
if HEIGHT < 1 and HEIGHT != "auto":
    HEIGHT = 1
if HEIGHTVARIATION > HEIGHT:
    HEIGHTVARIATION = HEIGHT
if WOOD not in [True,False]:
    print("WOOD not set correctly, using True")
    WOOD = True
if TRUNKTHICKNESS < 0.0:
    TRUNKTHICKNESS = 0.0
if TRUNKHEIGHT < 0.0:
    TRUNKHEIGHT = 0.0
if ROOTS not in ["yes","tostone","hanging","no"]:
    print("ROOTS not set correctly, using 'no' and creating no roots")
    ROOTS = "no"
if ROOTBUTTRESSES not in [True,False]:
    print("ROOTBUTTRESSES not set correctly, using False")
    ROOTBUTTRESSES = False
if FOLIAGE not in [True,False]:
    print("FOLIAGE not set correctly, using True")
    ROOTBUTTRESSES = True
if FOLIAGEDENSITY < 0.0:
    FOLIAGEDENSITY = 0.0
if BRANCHDENSITY < 0.0:
    BRANCHDENSITY = 0.0
if MAPHEIGHTLIMIT not in [True,False]:
    print("MAPHEIGHTLIMIT not set correctly, using False")
    MAPHEIGHTLIMIT = False
if LIGHTTREE not in [0,1,2,4]:
    print("LIGHTTREE not set correctly, using 0 for no torches")
    LIGHTTREE = 0


# The following is an interface class for .mclevel data for minecraft savefiles.
# The following also includes a useful coordinate to index convertor and several
# other useful functions.


import gzip


class McLevel(object):
    '''An interface object to alow loading and saving of map data from
    a minecraft save file of extension '.mclevel'
    '''
        
    def mapdims(self):
        '''Return a list of dimensions of the map, in format [x,y,z].
        
        Cache the dimensions in the McLevel object for quicker access.
        '''
        if self.dims is None:
            mapdata = self.filecontents
            idx = mapdata.find(chr(5) + 'Width') + 6
            firstbyte = ord(mapdata[idx])
            secondbyte = ord(mapdata[idx+1])
            width = firstbyte * 256 + secondbyte
            
            idx = mapdata.find(chr(6) + 'Height') + 7
            firstbyte = ord(mapdata[idx])
            secondbyte = ord(mapdata[idx+1])
            height = firstbyte * 256 + secondbyte

            idx = mapdata.find(chr(6) + 'Length') + 7
            firstbyte = ord(mapdata[idx])
            secondbyte = ord(mapdata[idx+1])
            length = firstbyte * 256 + secondbyte

            dims = [width, height, length]
            self.dims = dims
        else:
            dims = self.dims
        return dims

    def setmapdims(self,dims):
        '''Change the dimensions of the map to dims.
        
        dims = [x,y,z] for the dimensions of the map.
        
        WARNING!  This method sets all block types and data to zero.'''
        mapdata = self.filecontents[:]
        # x, y, and z are the new dimensions of the map.
        x = dims[0]
        y = dims[1]
        z = dims[2]
        # Find the location which stores the width, or x value
        idx = mapdata.find(chr(5) + 'Width') + 6
        # Convert x into a two byte integer
        firstbyte = chr(x/256)
        secondbyte = chr(x%256)
        width = firstbyte + secondbyte
        # Write the two byte value into the map data.
        mapdata = mapdata[:idx] + width + mapdata[idx+2:]
        
        # Do the same for y and z
        idx = mapdata.find(chr(6) + 'Height') + 7
        firstbyte = chr(y/256)
        secondbyte = chr(y%256)
        height = firstbyte + secondbyte
        mapdata = mapdata[:idx] + height + mapdata[idx+2:]

        idx = mapdata.find(chr(6) + 'Length') + 7
        firstbyte = chr(z/256)
        secondbyte = chr(z%256)
        length = firstbyte + secondbyte
        mapdata = mapdata[:idx] + length + mapdata[idx+2:]
        
        # now re-assign the new string to storage in self
        self.filecontents = mapdata
        # make a new string of the correct length to use to fill out the data
        tempblocktotal = x*y*z
        fillerdata = chr(2)*tempblocktotal
        # inser the filler data into the file
        self.setblocktypes(fillerdata)
        self.setblockdata(fillerdata)
        # set the new correct dimensions and number of blocks
        self.dims = [x,y,z]
        self.totalblocks = tempblocktotal

    def blocktypelist(self):
        '''Return a string containing all of the block types.
        
        Each character in the string indicates a block in the map.
        see coord_to_idx below to locate the index for a given x,y,z coordinate.
        '''
        if self.blocktypes is None:
            mapdata = self.filecontents
            idx = mapdata.find(chr(6) + 'Blocks') + 11
            start = idx
            end = start + self.totalblocks
            source = self.filecontents[start:end]
            self.blocktypes = source
        else:
            source = self.blocktypes
        return source

    def setblocktypes(self,blockdata):
        '''Take a string and asign it to the blocktype section in the map.
        '''
        mapdata = self.filecontents
        start = mapdata.find(chr(6) + 'Blocks') + 7
        end = start + 4
        rawlength = mapdata[start:end]
        arraylength = 0
        for i in range(4):
            arraylength += ord(rawlength[3-i]) * (2**(8*i))
        end = start + arraylength + 4
        newlength = len(blockdata)
        lengthbits = ''
        for i in range(4):
            byteshift = 3-i
            placevalue = 2**(8*byteshift)
            lengthbits += chr((newlength / placevalue)%256 )
        mapout = mapdata[:start] + lengthbits + blockdata + mapdata[end:]
        self.filecontents = mapout
        self.blocktypes = blockdata

    def blockdatalist(self):
        '''Return a string containing all of the block data.
        
        Each character in the string indicates a block in the map.
        see coord_to_idx below to locate the index for a given x,y,z coordinate.
        '''
        if self.blockdata is None:
            mapdata = self.filecontents
            idx = mapdata.find(chr(4) + 'Data') + 10
            start = idx 
            end = start + self.totalblocks
            source = self.filecontents[start:end]
            self.blockdata = source
        else:
            source = self.blockdata
        return source

    def setblockdata(mapdata,blockdata):
        '''Take a string and asign it to the blockdata section in the map.
        '''
        mapdata = self.filecontents
        start = mapdata.find(chr(4) + 'Data') + 5
        end = start + 4
        rawlength = mapdata[start:end]
        arraylength = 0
        for i in range(4):
            arraylength += ord(rawlength[3-i]) * (2**(8*i))
        end = start + arraylength + 4
        newlength = len(blockdata)
        lengthbits = ''
        for i in range(4):
            byteshift = 3-i
            placevalue = 2**(8*byteshift)
            lengthbits += chr((newlength / placevalue)%256 )
        mapout = mapdata[:start] + lengthbits + blockdata + mapdata[end:]
        self.filecontents = mapout
        self.blockdata = blockdata

    def import_map(self,filepath):
        '''unzip the raw data from the file and store it internally'''
        filein = gzip.open(filepath,'rb')
        self.filecontents = filein.read()
        filein.close()
        dims = self.mapdims()
        self.dims = dims
        self.totalblocks = dims[0] * dims[1] * dims[2]
        return None

    def export_map(self,filepath):
        '''export the contained map data to the file in filepath'''
        fileout = gzip.open(filepath,'wb')
        fileout.write(self.filecontents)
        fileout.close()

    def copy(self):
        '''return a copy of this object'''
        newobject = McLevel()
        newobject.filecontents = self.filecontents[:]
        newobject.dims = self.dims[:]
        newobject.totalblocks = self.totalblocks
        return newobject
    
    def __init__(self):
        self.filecontents = ""
        self.dims = None
        self.totalblocks = None
        self.blocktypes = None
        self.blockdata = None

#some handy functions

def coord_to_idx(coord,mcmap):
    '''take the coordinates and return the index location of that data byte

    coord is [x,y,z] in minecraft coordinates
    size is [x_size,y_size,z_size] for the whole map
    returns the index location for that coordinate
    '''
    size = mcmap.mapdims()
    x = coord[0]
    y = coord[1]
    z = coord[2]
    idx = x + (y * size[2] + z) * size[0]
    return idx

def in_bounds(coordinate,mcmap,border = 0):
    '''return False if the coordinate lies outside mcmap, else return True
    '''
    assert isinstance(mcmap, McLevel)
    dims = mcmap.mapdims()
    x = coordinate[0]
    if x < border or x >= dims[0]-border: return False
    y = coordinate[1]
    if y < border or y >= dims[1]-border: return False
    z = coordinate[2]
    if z < border or z >= dims[2]-border: return False
    return True

def search_column(x,z,matidx,mcmap,ystart = None):
    '''take horizontal position and index, return y value of first occurance.
    
    Search the column from the top down.
    It also needs a MCLevel object, hopefully with data already loaded.
    If no block of matidx is found, return None'''
    assert isinstance(mcmap, McLevel)
    matdata = mcmap.blocktypelist()
    dims = mcmap.mapdims()
    if ystart is None:
        ystart = dims[1] - 1
    y = ystart
    while y > 0:
        idx = coord_to_idx([x,y,z],mcmap)
        if ord(matdata[idx]) == matidx:
            return y
        else:
            y += -1
    return None

def rnd_surface_point(matidx,mcmap):
    '''picks a random location on the surface of the map
    
    finds the highest point of type matidx in a random location
    the random location is padded by eight squares on every side
    '''
    assert isinstance(mcmap, McLevel)
    dims = mcmap.mapdims()
    x = 8 + int(random()*(dims[0]-16))
    z = 8 + int(random()*(dims[2]-16))
    y = search_column(x,z,matidx,mcmap)
    if y is None:
        y = 8 + int(random()*(dims[1]-16))
    return [x,y,z]

def dist_to_mat(cord,vec,matidx,mcmap,invert = False):
    '''travel from cord along vec and return how far it was to a point of matidx

    the distance is returned in number of iterations.  If the edge of the map
    is reached, then return the number of iterations as well.
    if invert == True, search for anything other than matidx
    '''
    assert isinstance(mcmap, McLevel)
    matdata = mcmap.blocktypelist()
    curcord = [i + .5 for i in cord]
    iterations = 0
    while in_bounds(curcord,mcmap):
        x = int(curcord[0])
        y = int(curcord[1])
        z = int(curcord[2])
        idx = coord_to_idx([x,y,z],mcmap)
        if (ord(matdata[idx]) == matidx) and invert == False:
            break
        elif (ord(matdata[idx]) != matidx) and invert:
            break
        else:
            curcord = [curcord[i] + vec[i] for i in range(3)]
            iterations += 1
    return iterations

def highestpoint(matidx,mcmap):
    '''Find the highest point of matidx and return coords.
    
    Search every other square.  
    '''
    assert isinstance(mcmap, McLevel)
    dims = mcmap.mapdims()
    bestx = 0
    bestz = 0
    besty = 0
    for x in range(dims[0]/2):
        for z in range(dims[2]/2):
            thisx = x*2
            thisz = z*2
            val = search_column(thisx,thisz,matidx,mcmap)
            if val > besty:
                besty = val
                bestx = thisx
                bestz = thisz
    
    return [bestx,besty,bestz] 

# This is the end of the MCLevel interface.

# Now, on to the actual code.

from random import random, choice, sample
from math import sqrt, sin, cos, pi


def make_blocklist(mcmap):
    '''Take a McLevel object and Return a 3 dimensional matrix of integers.
    
    The blocklist is in the form such that blocklist[x][y][z] will return the
    integer value of the material index for that x,y,z coordinate in the map.
    Initialize the values with -1.  This value indicates no replacement of the
    current map data.
    '''
    dims = mcmap.mapdims()
    xsize = dims[0]
    ysize = dims[1]
    zsize = dims[2]
    blocklist = []
    for x in range(xsize):
        row = []
        for y in range(ysize):
            column = []
            for z in range(zsize):
                column += [-1]
            row += [column]
        blocklist += [row]
    return blocklist


def assign_value(x,y,z,val,blocklist):
    '''Assign an index value to a location in blocklist.
    
    If the index is outside the bounds of the map, return None.  If the
    assignment succeeds, return True.
    '''
    if x < 0 or y < 0 or z < 0:
        return None
    try:
        blocklist[x][y][z] = val
    except IndexError:
        return None
    return True


class Tree(object):
    '''Set up the interface for tree objects.  Designed for subclassing.
    '''
    def prepare(self):
        '''initialize the internal values for the Tree object.
        '''
        return None
    
    def maketrunk(self,blocklist,mcmap):
        '''Generate the trunk and enter it in blocklist.
        '''
        return None
    
    def makefoliage(self,blocklist):
        """Generate the foliage and enter it in blocklist.
        
        Note, foliage will disintegrate if there is no foliage below, or
        if there is no "log" block within range 2 (square) at the same level or 
        one level below"""
        return None
    
    def copy(self,other):
        '''Copy the essential values of the other tree object into self.
        '''
        self.pos = other.pos
        self.height = other.height
        
    def __init__(self,pos = [0,0,0],height = 1):
        '''Accept values for the position and height of a tree.
        
        Store them in self.
        '''
        self.pos = pos
        self.height = height


class StickTree(Tree):
    '''Set up the trunk for trees with a trunk width of 1 and simple geometry.
    
    Designed for sublcassing.  Only makes the trunk.
    '''
    def maketrunk(self,blocklist,mcmap):
        x = self.pos[0]
        y = self.pos[1]
        z = self.pos[2]
        
        for i in range(self.height):
            assign_value(x,y,z,17,blocklist)
            y += 1
        

class NormalTree(StickTree):
    '''Set up the foliage for a 'normal' tree.
    
    This tree will be a single bulb of foliage above a single width trunk.
    This shape is very similar to the default Minecraft tree.
    '''
    def makefoliage(self,blocklist):
        """note, foliage will disintegrate if there is no foliage below, or
        if there is no "log" block within range 2 (square) at the same level or 
        one level below"""
        topy = self.pos[1] + self.height - 1
        start = topy - 2
        end = topy + 2
        for y in range(start,end):
            if y > start + 1:
                rad = 1
            else:
                rad = 2
            for xoff in range(-rad,rad+1):
                for zoff in range(-rad,rad+1):
                    if (random() > 0.618
                        and abs(xoff) == abs(zoff)
                        and abs(xoff) == rad
                        ):
                        continue
                    
                    x = self.pos[0] + xoff
                    z = self.pos[2] + zoff
                    
                    assign_value(x,y,z,18,blocklist)
                    

class BambooTree(StickTree):
    '''Set up the foliage for a bamboo tree.
    
    Make foliage sparse and adjacent to the trunk.
    '''
    def makefoliage(self,blocklist):
        start = self.pos[1]
        end = self.pos[1] + self.height + 1
        for y in range(start,end):
            for i in [0,1]:
                xoff = choice([-1,1])
                zoff = choice([-1,1])
                x = self.pos[0] + xoff
                z = self.pos[2] + zoff
                assign_value(x,y,z,18,blocklist)


class PalmTree(StickTree):
    '''Set up the foliage for a palm tree.
    
    Make foliage stick out in four directions from the top of the trunk.
    '''
    def makefoliage(self,blocklist):
        y = self.pos[1] + self.height
        for xoff in range(-2,3):
            for zoff in range(-2,3):
                if abs(xoff) == abs(zoff):
                    x = self.pos[0] + xoff
                    z = self.pos[2] + zoff
                    assign_value(x,y,z,18,blocklist)


class ProceduralTree(Tree):
    '''Set up the methods for a larger more complicated tree.
    
    This tree type has roots, a trunk, and branches all of varying width, 
    and many foliage clusters.
    MUST BE SUBCLASSED.  Specifically, self.foliage_shape must be set.
    Subclass 'prepare' and 'shapefunc' to make different shaped trees.
    '''
    
    def crossection(self,center,radius,diraxis,matidx,blocklist):
        '''Create a round section of type matidx in blocklist.
        
        Passed values:
        center = [x,y,z] for the coordinates of the center block
        radius = <number> as the radius of the section.  May be a float or int.
        diraxis: The list index for the axis to make the section
        perpendicular to.  0 indicates the x axis, 1 the y, 2 the z.  The
        section will extend along the other two axies.
        matidx = <int> the integer value to make the section out of.
        blocklist = the array generated by make_blocklist
        '''
        rad = int(radius + .618)
        secidx1 = (diraxis - 1)%3
        secidx2 = (1 + diraxis)%3
        coord = [0,0,0]
        for off1 in range(-rad,rad+1):
            for off2 in range(-rad,rad+1):
                thisdist = sqrt((abs(off1)+ .5)**2 + (abs(off2) + .5)**2)
                if thisdist > radius:
                    continue
                pri = center[diraxis]
                sec1 = center[secidx1] + off1
                sec2 = center[secidx2] + off2
                coord[diraxis] = pri
                coord[secidx1] = sec1
                coord[secidx2] = sec2
                assign_value(coord[0],coord[1],coord[2],matidx,blocklist)
    
    def shapefunc(self,y):
        '''Take y and return a radius for the location of the foliage cluster.
        
        If no foliage cluster is to be created, return None
        Designed for sublcassing.  Only makes clusters close to the trunk.
        '''
        if random() < 100./((self.height)**2) and y < self.trunkheight:
            return self.height * .12
        return None
    
    def foliagecluster(self,center,blocklist):
        '''generate a round cluster of foliage at the location center.
        
        The shape of the cluster is defined by the list self.foliage_shape.
        This list must be set in a subclass of ProceduralTree.
        '''
        level_radius = self.foliage_shape
        x = center[0]
        y = center[1]
        z = center[2]
        for i in level_radius:
            self.crossection([x,y,z],i,1,18,blocklist)
            y += 1
    
    def taperedlimb(self,start,end,startsize,endsize,blocklist):
        '''Create a tapered cylinder in blocklist.
        
        start and end are the beginning and ending coordinates of form [x,y,z].
        startsize and endsize are the beginning and ending radius.
        The material of the cylinder is 17, which indicates wood in Minecraft.
        '''
        
        # delta is the coordinate vector for the difference between
        # start and end.
        delta = [end[i] - start[i] for i in range(3)]
        # primidx is the index (0,1,or 2 for x,y,z) for the coordinate
        # which has the largest overall delta.
        maxdist = max(delta,key=abs)
        if maxdist == 0:
            return None
        primidx = delta.index(maxdist)
        # secidx1 and secidx2 are the remaining indicies out of [0,1,2].
        secidx1 = (primidx - 1)%3
        secidx2 = (1 + primidx)%3
        # primsign is the digit 1 or -1 depending on whether the limb is headed
        # along the positive or negative primidx axis.
        primsign = delta[primidx]/abs(delta[primidx])
        # secdelta1 and ...2 are the amount the associated values change
        # for every step along the prime axis.
        secdelta1 = delta[secidx1]
        secfac1 = float(secdelta1)/delta[primidx]
        secdelta2 = delta[secidx2]
        secfac2 = float(secdelta2)/delta[primidx]
        # Initialize coord.  These values could be anything, since 
        # they are overwritten.
        coord = [0,0,0]
        # Loop through each crossection along the primary axis,
        # from start to end.
        endoffset = delta[primidx] + primsign
        for primoffset in range(0, endoffset, primsign):
            primloc = start[primidx] + primoffset
            secloc1 = int(start[secidx1] + primoffset*secfac1)
            secloc2 = int(start[secidx2] + primoffset*secfac2)
            coord[primidx] = primloc
            coord[secidx1] = secloc1
            coord[secidx2] = secloc2
            primdist = abs(delta[primidx])
            radius = endsize + (startsize-endsize) * abs(delta[primidx]
                                - primoffset) / primdist
            self.crossection(coord,radius,primidx,17,blocklist)
    
    def makefoliage(self,blocklist):
        '''Generate the foliage for the tree in blocklist.
        '''
        """note, foliage will disintegrate if there is no foliage below, or
        if there is no "log" block within range 2 (square) at the same level or 
        one level below"""
        foliage_coords = self.foliage_cords
        for coord in foliage_coords:
            self.foliagecluster(coord,blocklist)
        for cord in foliage_coords:
            assign_value(cord[0],cord[1],cord[2],17,blocklist)
            if LIGHTTREE == 1:
                assign_value(cord[0],cord[1]+1,cord[2],50,blocklist)
                assign_value(cord[0],cord[1]+2,cord[2],17,blocklist)
            elif LIGHTTREE in [2,4]:
                assign_value(cord[0]+1,cord[1],cord[2],50,blocklist)
                assign_value(cord[0]-1,cord[1],cord[2],50,blocklist)
                if LIGHTTREE == 4:
                    assign_value(cord[0],cord[1],cord[2]+1,50,blocklist)
                    assign_value(cord[0],cord[1],cord[2]-1,50,blocklist)
                    
    def makebranches(self,blocklist):
        '''Generate the branches and enter them in blocklist.
        '''
        treeposition = self.pos
        height = self.height
        topy = treeposition[1]+int(self.trunkheight + 0.5)
        endrad = self.trunkradius * (1 - self.trunkheight/height)
        if endrad < 1.0:
            endrad = 1.0
        for coord in self.foliage_cords:
            dist = (sqrt(float(coord[0]-treeposition[0])**2 +
                            float(coord[2]-treeposition[2])**2))
            ydist = coord[1]-treeposition[1]
            value = (self.branchdensity * 220 * height)/((ydist + dist) ** 3)
            if value < random():
                continue
            
            posy = coord[1]
            slope = self.branchslope + (0.5 - random())*.16
            if coord[1] - dist*slope > topy:
                threshhold = 1 / float(height)
                if random() < threshhold:
                    continue
                branchy = topy
                basesize = endrad
            else:
                branchy = posy-dist*slope
                basesize = (endrad + (self.trunkradius-endrad) * 
                         (topy - branchy) / self.trunkheight)
            startsize = (basesize * (1 + random()) * .618 * 
                         (dist/height)**0.618)
            rndr = sqrt(random())*basesize*0.618
            rndang = random()*2*pi
            rndx = int(rndr*sin(rndang) + 0.5)
            rndz = int(rndr*cos(rndang) + 0.5)
            startcoord = [treeposition[0]+rndx,
                          int(branchy),
                          treeposition[2]+rndz]
            if startsize < 1.0:
                startsize = 1.0
            endsize = 1.0
            self.taperedlimb(startcoord,coord,startsize,endsize,blocklist)
    
    def makeroots(self,rootbases,blocklist,mcmap):
        '''generate the roots and enter them in blocklist.
        
        rootbases = [[x,z,base_radius], ...] and is the list of locations
        the roots can originate from, and the size of that location.
        '''
        treeposition = self.pos
        height = self.height
        for coord in self.foliage_cords:
            # First, set the threshhold for randomly selecting this 
            # coordinate for root creation.
            dist = (sqrt(float(coord[0]-treeposition[0])**2 +
                            float(coord[2]-treeposition[2])**2))
            ydist = coord[1]-treeposition[1]
            value = (self.branchdensity * 220 * height)/((ydist + dist) ** 3)
            # Randomly skip roots, based on the above threshold
            if value < random():
                continue
            # initialize the internal variables from a selection of 
            # starting locations.
            rootbase = choice(rootbases)
            rootx = rootbase[0]
            rootz = rootbase[1]
            rootbaseradius = rootbase[2]
            # Offset the root origin location by a random amount
            # (radialy) from the starting location.
            rndr = (sqrt(random())*rootbaseradius*.618)
            rndang = random()*2*pi
            rndx = int(rndr*sin(rndang) + 0.5)
            rndz = int(rndr*cos(rndang) + 0.5)
            rndy = int(random()*rootbaseradius*0.5)
            startcoord = [rootx+rndx,treeposition[1]+rndy,rootz+rndz]
            # offset is the distance from the root base to the root tip.
            offset = [startcoord[i]-coord[i] for i in range(3)]
            # If this is a mangrove tree, make the roots longer.
            if SHAPE == "mangrove":
                offset = [int(val * 1.618 - 1.5) for val in offset]
            endcoord = [startcoord[i]+offset[i] for i in range(3)]
            rootstartsize = (rootbaseradius*0.618* abs(offset[1])/
                             (height*0.618))
            if rootstartsize < 1.0:
                rootstartsize = 1.0
            endsize = 1.0
            # If ROOTS is set to "tostone" or "hanging" we need to check
            # along the distance for collision with existing materials.
            if ROOTS in ["tostone","hanging"]:
                offlength = sqrt(float(offset[0])**2 + 
                                 float(offset[1])**2 + 
                                 float(offset[2])**2)
                if offlength < 1:
                    continue
                rootmid = endsize
                # vec is a unit vector along the direction of the root.
                vec = [offset[i]/offlength for i in range(3)]
                if ROOTS == "tostone":
                    searchindex = 1
                elif ROOTS == "hanging":
                    searchindex = 0
                # startdist is how many steps to travel before starting to
                # search for the material.  It is used to ensure that large
                # roots will go some distance before changing directions
                # or stopping.
                startdist = int(random()*6*sqrt(rootstartsize) + 2.8)
                # searchstart is the coordinate where the search should begin
                searchstart = [startcoord[i] + startdist*vec[i] 
                               for i in range(3)]
                # dist stores how far the search went (including searchstart) 
                # before encountering the expected marterial.
                dist = startdist + dist_to_mat(searchstart,vec,
                                               searchindex,mcmap)
                # If the distance to the materila is less than the length
                # of the root, change the end point of the root to where
                # the search found the material.
                if dist < offlength:
                    # rootmid is the size of the crossection at endcoord.
                    rootmid +=  (rootstartsize - 
                                         endsize)*(1-dist/offlength)
                    # endcoord is the midpoint for hanging roots, 
                    # and the endpoint for roots stopped by stone.
                    endcoord = [startcoord[i]+int(vec[i]*dist) 
                                for i in range(3)]
                    if ROOTS == "hanging":
                        # remaining_dist is how far the root had left
                        # to go when it was stopped.
                        remaining_dist = offlength - dist
                        # Initialize bottomcord to the stopping point of
                        # the root, and then hang straight down
                        # a distance of remaining_dist.
                        bottomcord = endcoord[:]
                        bottomcord[1] += -int(remaining_dist)
                        # Make the hanging part of the hanging root.
                        self.taperedlimb(endcoord,bottomcord,
                             rootmid,endsize,blocklist)
                
                # make the beginning part of hanging or "tostone" roots
                self.taperedlimb(startcoord,endcoord,
                     rootstartsize,rootmid,blocklist)
        
            # If you aren't searching for stone or air, just make the root.
            else:
                self.taperedlimb(startcoord,endcoord,
                             rootstartsize,endsize,blocklist)
    
    def maketrunk(self,blocklist,mcmap):
        '''Generate the trunk, roots, and branches in blocklist.
        '''
        height = self.height
        trunkheight = self.trunkheight
        trunkradius = self.trunkradius
        treeposition = self.pos
        starty = treeposition[1]
        midy = treeposition[1]+int(trunkheight*.382)
        topy = treeposition[1]+int(trunkheight + 0.5)
        # In this method, x and z are the position of the trunk.
        x = treeposition[0]
        z = treeposition[2]
        midrad = trunkradius * .8
        endrad = trunkradius * (1 - trunkheight/height)
        if endrad < 1.0:
            endrad = 1.0
        if midrad < endrad:
            midrad = endrad
        # Make the root buttresses, if indicated
        if ROOTBUTTRESSES or SHAPE == "mangrove":
            # The start radius of the trunk should be a little smaller if we
            # are using root buttresses.
            startrad = trunkradius * .8
            # rootbases is used later in self.makeroots(...) as
            # starting locations for the roots.
            rootbases = [[x,z,startrad]]
            buttress_radius = trunkradius * 0.382
            # posradius is how far the root buttresses should be offset
            # from the trunk.
            posradius = trunkradius
            # In mangroves, the root buttresses are much more extended.
            if SHAPE == "mangrove":
                posradius = posradius *2.618
            num_of_buttresses = int(sqrt(trunkradius) + 3.5)
            for i in range(num_of_buttresses):
                rndang = random()*2*pi
                thisposradius = posradius * (0.9 + random()*.2)
                # thisx and thisz are the x and z position for the base of
                # the root buttress.
                thisx = x + int(thisposradius * sin(rndang))
                thisz = z + int(thisposradius * cos(rndang))
                # thisbuttressradius is the radius of the buttress.
                # Currently, root buttresses do not taper.
                thisbuttressradius = buttress_radius * (0.618 + random())
                if thisbuttressradius < 1.0:
                    thisbuttressradius = 1.0
                # Make the root buttress.
                self.taperedlimb([thisx,starty,thisz],[x,midy,z],
                                 thisbuttressradius,thisbuttressradius,
                                 blocklist)
                # Add this root buttress as a possible location at
                # which roots can spawn.
                rootbases += [[thisx,thisz,thisbuttressradius]]
        else:
            # If root buttresses are turned off, set the trunk radius
            # to normal size.
            startrad = trunkradius
            rootbases = [[x,z,startrad]]
        # Make the lower and upper sections of the trunk.
        self.taperedlimb([x,starty,z],[x,midy,z],startrad,midrad,blocklist)
        self.taperedlimb([x,midy,z],[x,topy,z],midrad,endrad,blocklist)
        #Make the branches
        self.makebranches(blocklist)
        #Make the roots, if indicated.
        if ROOTS in ["yes","tostone","hanging"]:
            self.makeroots(rootbases,blocklist,mcmap)
        
    def prepare(self):
        '''Initialize the internal values for the Tree object.
        
        Primarily, sets up the foliage cluster locations.
        '''
        self.trunkradius = sqrt(self.height * TRUNKTHICKNESS)
        if self.trunkradius < 1:
            self.trunkradius = 1
        self.trunkheight = self.height * 0.618
        self.branchdensity = BRANCHDENSITY / FOLIAGEDENSITY
        foliage_coords = []
        ystart = self.pos[1]
        yend = int(self.pos[1] + self.height)
        num_of_clusters_per_y = int(1.5 + (FOLIAGEDENSITY * 
                                           self.height / 19.)**2)
        if num_of_clusters_per_y < 1:
            num_of_clusters_per_y = 1
        for y in range(yend,ystart,-1):
            for i in range(num_of_clusters_per_y):
                shapefac = self.shapefunc(y-ystart)
                if shapefac is None:
                    continue
                r = (sqrt(random()) + .328)*shapefac
                
                theta = random()*2*pi
                x = int(r*sin(theta)) + self.pos[0]
                z = int(r*cos(theta)) + self.pos[2]
                foliage_coords += [[x,y,z]]

        self.foliage_cords = foliage_coords


class RoundTree(ProceduralTree):
    '''This kind of tree is designed to resemble a deciduous tree.
    '''
    def prepare(self):
        ProceduralTree.prepare(self)
        self.branchslope = 0.382
        self.foliage_shape = [2,3,3,2.5,1.6]
        self.trunkradius = self.trunkradius * 0.8
        self.trunkheight = TRUNKHEIGHT * self.height
        
    def shapefunc(self,y):
        twigs = ProceduralTree.shapefunc(self,y)
        if twigs is not None:
            return twigs
        if y < self.height * (.282 + .1*sqrt(random())) :
            return None
        radius = self.height / 2.
        adj = self.height/2. - y
        if adj == 0 :
            dist = radius
        elif abs(adj) >= radius:
            dist = 0
        else:
            dist = sqrt( ((radius)**2) - ((adj)**2) )
        dist = dist * .618
        return dist
            

class ConeTree(ProceduralTree):
    '''this kind of tree is designed to resemble a conifer tree.
    '''
    def prepare(self):
        ProceduralTree.prepare(self)
        self.branchslope = 0.15
        self.foliage_shape = [3,2.6,2,1]
        self.trunkradius = self.trunkradius * 0.618
        self.trunkheight = self.height
        
    def shapefunc(self,y):
        twigs = ProceduralTree.shapefunc(self,y)
        if twigs is not None:
            return twigs
        if y < self.height * (.25 + .05*sqrt(random())) :
            return None
        radius = (self.height - y )*0.382
        if radius < 0:
            radius = 0
        return radius


class RainforestTree(ProceduralTree):
    '''This kind of tree is designed to resemble a rainforest tree.
    '''
    def prepare(self):
        self.foliage_shape = [3.4,2.6]
        ProceduralTree.prepare(self)
        self.branchslope = 1.0
        self.trunkradius = self.trunkradius * 0.382
        self.trunkheight = self.height * .9
    
    def shapefunc(self,y):
        if y < self.height * 0.8:
            if HEIGHT < self.height:
                twigs = ProceduralTree.shapefunc(self,y)
                if (twigs is not None) and random() < 0.05:
                    return twigs
            return None
        else:
            width = self.height * .382
            topdist = (self.height - y)/(self.height*0.2)
            dist = width * (0.618 + topdist) * (0.618 + random()) * 0.382
            return dist


class MangroveTree(RoundTree):
    '''This kind of tree is designed to resemble a mangrove tree.
    '''
    def prepare(self):
        RoundTree.prepare(self)
        self.branchslope = 1.0
        self.trunkradius = self.trunkradius * 0.618
    
    def shapefunc(self,y):
        val = RoundTree.shapefunc(self,y)
        if val is None:
            return val
        val = val * 1.618
        return val
        

def findtrees(mcmap,treelist):
    '''Take a map mcmap and add the existing trees from mcmap to treelist.
    
    Only designed to work with the default trees.
    Also detect the height of the existing tree.  If indicated
    record this height in the tree, otherwise generate a random height.
    '''
    assert isinstance(mcmap, McLevel)
    dims = mcmap.mapdims()
    if HEIGHT == "auto":
        treeheight = 5
    else:
        treeheight = HEIGHT
    height_choices = range(int(treeheight-HEIGHTVARIATION),
                           int(treeheight+HEIGHTVARIATION+1))
    for x in range(dims[0]):
        for z in range(dims[2]):
            y = dims[1]-1
            while True:
                foliagetop = search_column(x,z,18,mcmap,ystart = y)
                if foliagetop is None: break
                y = foliagetop
                trunktop = [x,y-1,z]
                height = dist_to_mat(trunktop,[0,-1,0],17,mcmap,invert = True)
                if height == 0:
                    y += -1
                    continue
                y += -height
                
                if HEIGHT != "auto":
                    height = choice(height_choices)
                
                newtree = Tree([x,y,z],height)
                treelist += [newtree]
                y += -1
                
                
def planttrees(mcmap,treelist):
    '''Take mcmap and add trees to random locations on the surface to treelist.
    '''
    assert isinstance(mcmap, McLevel)
    dims = mcmap.mapdims()
    if HEIGHT == "auto":
        treeheight = 5
    else:
        treeheight = HEIGHT
    height_choices = range(int(treeheight-HEIGHTVARIATION),
                           int(treeheight+HEIGHTVARIATION+1))
    while len(treelist) < TREECOUNT:
        height = choice(height_choices)
        padding = int(height/3.) + 1
        mindim = min([dims[0],dims[2]])
        if (padding > mindim/2.2):
            padding = int(mindim/2.2)
        x = choice(range(dims[0])[padding:-padding])
        z = choice(range(dims[2])[padding:-padding])
        y = search_column(x,z,PLANTON,mcmap)
        if y is None:
            continue
        else:
            y += 1
        newtree = Tree([x,y,z],height)
        treelist += [newtree]

        
def plantrainforesttrees(mcmap,treelist):
    '''Take mcmap and add rain forest trees to treelist.
    
    Do not place trees close enough that they will overlap by a great amount.
    '''
    assert isinstance(mcmap, McLevel)
    dims = mcmap.mapdims()
    def randomtreeloc(height):
        padding = int(height/3.) + 1
        mindim = min([dims[0],dims[2]])
        if (padding > mindim/2.2):
            padding = int(mindim/2.2)
        x = choice(range(dims[0])[padding:-padding])
        z = choice(range(dims[2])[padding:-padding])
        y = search_column(x,z,PLANTON,mcmap)
        return x,y,z
    if HEIGHT == "auto":
        treeheight = 5
    else:
        treeheight = HEIGHT
    existingtreenum = len(treelist)
    remainingtrees = TREECOUNT - existingtreenum
    # One in short_tree_fraction trees will be tall trees, 
    # near the upper limit of height.  All the rest will be
    # shorter, near the lower limit.
    short_tree_fraction = 6
    for i in range(remainingtrees):
        randomfac = (sqrt(random())*1.618 - 0.618)*HEIGHTVARIATION + 0.5
        if i%short_tree_fraction == 0:
            height = int(treeheight + randomfac)
        else:
            height = int(treeheight - randomfac)
        # Get a random tree location.  If there was no grass at
        # this location, continue with the next loop iteration.
        x,y,z = randomtreeloc(height)
        if y is None:
            continue
        # y should be one larger, since the random location finder finds
        # the ground, and we want the location just above the ground.
        y += 1
        # This loop searches all the other trees to see if this location is
        # too close to any of them.  If it is too close, try over with a
        # new random location.
        displaced = False
        for othertree in treelist:
            other_loc = othertree.pos
            otherheight = othertree.height
            tallx = other_loc[0]
            tallz = other_loc[2]
            dist = sqrt((tallx - x + .5)**2 + (tallz - z + .5)**2)
            threshold = ((otherheight + height) * .193)
            if dist < threshold:
                displaced = True
                break
        if displaced:
            continue
        newtree = RainforestTree([x,y,z],height)
        treelist += [newtree]
    
        
def plantmangroves(mcmap,treelist):
    '''Place mangroves in the surface water.
    
    Do not place the trees in water that is too deep for them.
    Do not place trees underground.
    '''
    assert isinstance(mcmap, McLevel)
    dims = mcmap.mapdims()
    if HEIGHT == "auto":
        treeheight = 5
    else:
        treeheight = HEIGHT
    height_choices = range(int(treeheight-HEIGHTVARIATION),
                           int(treeheight+HEIGHTVARIATION+1))
    # Short trees will NOT be planted in deep water.
    # Tall trees WILL be planted in shallow water.
    # Thus, if heights are randomly generated inside the
    # while loop, the distribution will favor tall trees.
    # Because of this, we will generate a height list first, 
    # so an even height distribution is achieved.
    # This assumes that there is water shallow enough for short trees.
    # If there is not, the program will hang here.
    heights = []
    numtreesleft = TREECOUNT - len(treelist)
    for i in range(numtreesleft):
        heights += [choice(height_choices)]
    # i is the index for heights.
    i = 0
    while len(treelist) < TREECOUNT:
        height = heights[i]
        padding = int(height/3.) + 1
        mindim = min([dims[0],dims[2]])
        if (padding > mindim/2.2):
            padding = int(mindim/2.2)
        x = choice(range(dims[0])[padding:-padding])
        z = choice(range(dims[2])[padding:-padding])
        top = dims[1] - 1
        # y is the highest point of non air at this x z coordinate.
        # If the whole column is air, y will be 0
        y = top - dist_to_mat([x,top,z],[0,-1,0],0,mcmap,invert = True)
        # dist is the distance through the water at this x z location.
        # If there is no water here, dist will be 0
        dist = dist_to_mat([x,y,z],[0,-1,0],9,mcmap,invert = True)
        # If the distance through the water too great, 
        # or if there is no water at all, try again with
        # a new random location.
        if dist > height * 0.618 or dist == 0:
            continue
        # offset the tree upward based on the height of the tree
        # and the depth of the water.
        y += int(sqrt(height - dist) + 2)
        newtree = Tree([x,y,z],height)
        i += 1
        treelist += [newtree]
        
        
def processtrees(mcmap,treelist):
    '''Initalize all of the trees in treelist.
    
    Set all of the trees to the right type, and run prepare.  If indicated
    limit the height of the trees to the top of the map.
    '''
    assert isinstance(mcmap, McLevel)
    if SHAPE == "stickly":
        shape_choices = ["normal","bamboo","palm"]
    elif SHAPE == "procedural":
        shape_choices = ["round","cone"]
    else:
        shape_choices = [SHAPE]
    
    for i in range(len(treelist)):
        newshape = choice(shape_choices)
        if newshape == "normal":
            newtree = NormalTree()
        elif newshape == "bamboo":
            newtree = BambooTree()
        elif newshape == "palm":
            newtree = PalmTree()
        elif newshape == "round":
            newtree = RoundTree()
        elif newshape == "cone":
            newtree = ConeTree()
        elif newshape == "rainforest":
            newtree = RainforestTree()
        elif newshape == "mangrove":
            newtree = MangroveTree()
        
        # Get the height and position of the existing trees in
        # the list.
        newtree.copy(treelist[i])
        # Now check each tree to ensure that it doesn't stick
        # out the top of the map.  If it does, shorten it until
        # the top of the foliage just touches the top of the map.
        if MAPHEIGHTLIMIT:
            height = newtree.height
            ybase = newtree.pos[1]
            mapheight = mcmap.mapdims()[1]
            if SHAPE == "rainforest":
                foliageheight = 2
            else:
                foliageheight = 4
            if ybase + height + foliageheight > mapheight:
                newheight = mapheight - ybase - foliageheight
                newtree.height = newheight
        # Even if it sticks out the top of the map, every tree
        # should be at least one unit tall.
        if newtree.height < 1:
            newtree.height = 1
        newtree.prepare()
        treelist[i] = newtree

        
def main():
    '''Load the file, create the trees, and save the new file.
    '''
    print("Importing the map")
    the_map = McLevel()
    the_map.import_map(LOADNAME)
    fileblockstring = the_map.blocktypelist()
    mapsize = the_map.mapdims()
    print("generating the blocklist")
    blocklist = make_blocklist(the_map)
    treelist = []
    
    if OPERATION == "clearcut":
        print("Cutting down all of the trees.")
        print("The forester is probably making a killing in the lumber market.")
        
    if OPERATION in ["conserve"]:
        print("Importing the existing trees")
        findtrees(the_map,treelist)
    
    if TREECOUNT > 0 and len(treelist) > TREECOUNT:
        treelist = sample(treelist,TREECOUNT)
        
    if OPERATION in ['replant','add']:
        if SHAPE == "rainforest":
            print("Planting the rainforest (should take a bit)")
            plantrainforesttrees(the_map,treelist)
        elif SHAPE == "mangrove":
            print("Planting mangroves")
            plantmangroves(the_map,treelist)
        else:
            print("Planting new trees")
            planttrees(the_map,treelist)
    
    if OPERATION != "clearcut":
        print("Processing tree changes")
        processtrees(the_map,treelist)
        
        if FOLIAGE:
            print("Generating foliage")
            for i in treelist:
                i.makefoliage(blocklist)
        if WOOD:
            print("Generating trunks, roots, and branches")
            for i in treelist:
                i.maketrunk(blocklist,the_map)
    
    print("making the new map (takes much longer for larger maps)")
    newblockstring = ""
    # There are two loops here to optimize for performance.
    # If "add" is selected, there is no need to filter existing
    # blocks for foliage and logs.
    idx = 0
    if OPERATION == "add":
        for y in range(mapsize[1]):
            if y%4 == 0: print(".")
            for z in range(mapsize[2]):
                for x in range(mapsize[0]):
                    thismat = blocklist[x][y][z]
                    if thismat == -1:
                        newblockstring += fileblockstring[idx]
                    else:
                        newblockstring += chr(thismat)
                    idx += 1
    # However, if "add" is not selected, change existing
    # foliage and logs into air.
    else:
        for y in range(mapsize[1]):
            if y%4 == 0: print(".")
            for z in range(mapsize[2]):
                for x in range(mapsize[0]):
                    thismat = blocklist[x][y][z]
                    if thismat == -1:
                        thismat = ord(fileblockstring[idx])
                        if (thismat == 17 or thismat == 18):
                            thismat = 0
                    newblockstring += chr(thismat)
                    idx += 1
    
    print("Saving the map (takes a bit)")
    the_map.setblocktypes(newblockstring)
    the_map.export_map(SAVENAME)
    print("finished")
    return None


if __name__ == '__main__':
    main()