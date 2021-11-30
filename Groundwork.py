'''This takes a base MineCraft level and adds city infrastructure.
It then saves the new map.
'''

# Here are the variables you can edit.

# this is the name of the map to load in
LOADNAME = "test.mclevel"

# this is the name of the map to save out when it is done
SAVENAME = "testresult.mclevel"

# If you want roads, set this to True, otherwise, set it to False
ROADS = True

# How wide(in blocks) do you want the roads to be?
# Also sets the width of the stairwells.
ROADWIDTH = 3

# The map will be divided into a grid of roads.  How many roads do you want
# on each axis?  There will be a border at the edges of the map.
# Note, this will produce (ROADNUM - 1) squared plots, so for 12 roads,
# there will be 11 by 11 plots, for a total of 121 plots.
# Subways will make a staircase in the middle of road intersections
# so this value affects subways as well.
ROADNUM = 6

# What is the maximum slope you would like the road to ascend?
# Higher numbers generally ensure that roads will be made everywhere,
# but they may be steeper.
# Lower numbers will eliminate more roads and ensure less slope.
# The value 0.5 is a 1:2 rise over run, and ensures that all roads
# will be easily walkable.
# A value of 1.0 will ensure that all roads can be jumped up, like staircases.
ROADSLOPE = 0.5

# How deep would you like the cuts to be before making tunnels?
# Larger numbers will make deeper cuts through hills, and fewer tunnels.
# ROADCUT can be an integer, like 6 or decimal, like 6.7
ROADCUT = 5.4

# How tall would you like the tunnels to be?
# Larger numbers will make taller tunnels.  Tunnel width will be
# the same width as the road.
# ROADTUNNEL can also be an integer or decimal
# This also sets the height of streetlamps
ROADTUNNEL = 3.2

# How tall would you like the fills to be before making bridges?
# Larger numbers will make taller columns of dirt under the road,
# and fewer bridges.
# ROADFILL can also be an integer or decimal
ROADFILL = 4.4

# How thick (excluding the roadway) would you like the bridges to be?
# Larger numbers will make thicker bridges.
# ROADBRIDGE can also be an integer or decimal
ROADBRIDGE = 1.2

# Do you want street lamps?
# set to 0 to disable
# set to a number to indicate the spacing of the torches
# 3 will make torches every three blocks
ROADLIGHTING = 6

# What material would you like the lamp posts made of?
LAMPMAT = 5

# What material would you like the lamp shades made of?
LAMPSHADEMAT = 20

# Do you want subways?
# Subways will make a staircase in the middle every other road intersection,
# and subways between the bottoms of the stairs.
# set True for yes, otherwise set False
SUBWAYS = True

# At what height would you like the subways to be centered?
# This is the y height, so larger is higher and closer to the surface.
# For normal maps, 15 - 20 is generally good range, for deep maps try 90 or so.
SUBWAYPOSITION = 15

# How wide would you like the subway tunnels?
SUBWAYWIDTH = 5

# What material would you like the subways made of?
# Try 20 for glass subways!
SUBWAYMAT = 4

# Do you want torches in the subways?
# set to 0 to disable
# set to a number to indicate the spacing of the torches
# 3 will make torches every three blocks
SUBWAYLIGHTING = 5

# Do you want water mains (pipes carying water) under the roads?
# If so, how big do you want the inside to be?
# 1 is a good value, but numbers larger will work as well.
# To disable water mains, set to 0
WATERSISZE = 1

# what material do you want the water mains made of?
WATERMAT = 42

# Do you want lava mains (pipes carying lava) under the roads?
# Same stuff as WATERSIZE above.
LAVASIZE = 1

# What material do you want the lava mains to be made of?
# Suggestion, set this different from WATERMAT so you can tell them apart.
LAVAMAT = 41

# Do you want sewer lines under the roads?
# If so, how big do you want the insides of the sewers to be?
# Make this at least 3 if you want to be able to walk in them
# the extra size is to allow headspace on the steps
# to disable sewers set to 0
SEWERSIZE = 3

# What material would you like the sewers made of?
SEWERMAT = 4

# Do you want torches in the sewers?
# set to 0 to disable
# set to a number to indicate the spacing of the torches
# 3 will make torches every three blocks
SEWERLIGHTING = 9

# Do you want buildings?
BUILDINGS = True

# How deep do you want the foundations to go?
# Positive numbers only:
# 0 is no foundations
# 2 makes a foundation two blocks deep.
FOUNDATIONDEPTH = 3

# How tall do you want each story of the buildings to be?
# You should really make this at least 3, so you can walk inside the buildings
# Set it to 1 to make a the buildings a solid block, for carving
# your own buildings!
STORYHEIGHT = 4

# How frequent do you want buildings to be?
# 0.0 is no buildings.
# 1.0 is a building in every plot.
# 0.5 is a building in half of the plots.
BUILDINGDENSITY = 0.6

# What is the min and max number of stories you want the building to be?
BUILDINGHEIGHTMIN = 1
BUILDINGHEIGHTMAX = 4

# What material would you like the buildings and foundations made of?
# Currently, the buildings are a solid block.
# To prepare a foundation, set BUILDINGMAT = 0 and FOUNDATIONMAT = 1
BUILDINGMAT = 1
FOUNDATIONMAT = 1



##############################################################
#  Don't edit below here unless you know what you are doing  #
##############################################################

# input filtering
if ROADS == True:
    if ROADWIDTH < 1:
        ROADWIDTH = 1
    if ROADNUM < 1:
        ROADNUM = 1


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
        if self.dims == None:
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
        if self.blocktypes == None:
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
        if self.blockdata == None:
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
    if ystart == None:
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
    if y == None: y = 8 + int(random()*(dims[1]-16))
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


def set_blocklist(x,y,z,val,blocklist):
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


def fillblock(startcoord,endcoord,blocklist,matidx = 0):
    '''fills the area with corners at startcoord and endcoord with matidx.
    
    matidx defaults to air
    endcoord is exclusive.
    '''
    for x in range(startcoord[0],endcoord[0]):
        for y in range(startcoord[1],endcoord[1]):
            for z in range(startcoord[2],endcoord[2]):
                set_blocklist(x,y,z,matidx,blocklist)

                
def shellblock(startcoord,endcoord,blocklist,matidx = 0):
    '''makes walls one unit thick of matidx from startcoord to endcoord.
    
    matidx defaults to air
    endcoord is exclusive
    '''
    # Fill the bottom
    lowcorner = startcoord[:]
    upcorner = endcoord[:]
    upcorner[1] = startcoord[1] + 1
    fillblock(lowcorner,upcorner,blocklist,matidx)
    # Fill the negative x side
    upcorner = endcoord[:]
    upcorner[0] = startcoord[0] + 1
    fillblock(lowcorner,upcorner,blocklist,matidx)
    # Fill the negative z side
    upcorner = endcoord[:]
    upcorner[2] = startcoord[2] + 1
    fillblock(lowcorner,upcorner,blocklist,matidx)
    # Fill the positive x side
    upcorner = endcoord[:]
    lowcorner[0] = endcoord[0] - 1
    fillblock(lowcorner,upcorner,blocklist,matidx)
    # Fill the positive z side
    lowcorner = startcoord[:]
    lowcorner[2] = endcoord[2] - 1
    fillblock(lowcorner,upcorner,blocklist,matidx)
    # Fill the top
    lowcorner = startcoord[:]
    lowcorner[1] = endcoord[1] - 1
    fillblock(lowcorner,upcorner,blocklist,matidx)
    

class Staircase(object):
    '''Makes a square spiral staircase, following the right-hand rule.
    
    Note: does not empty the area inside, or make a wall around the outside.
    self.width is the total width, in blocks, of the staircase.
    self.pos is the [x,y,z] coordinate of the center bottom of the staircase
    self.height is the y height of the staircase
    '''
    # These are the functions for incrementing x and z around the staircase.
    def left(x,z):
        '''when you are on the left, move down'''
        z += 1
        return x,z
    
    def bottom(x,z):
        '''when you are on the bottom, move right'''
        x += 1
        return x,z
    
    def right(x,z):
        '''when you are on the right, move up'''
        z += -1
        return x,z
    
    def top(x,z):
        '''when you are on the top, move left'''
        x += -1
        return x,z
    
    # Here is the lookup table for moving 
    movement_lookup = {0:left, 1:bottom, 2:right, 3:top}
    
    def create(self,blocklist):
        starty = self.pos[1]
        endy = starty + self.height
        if starty > endy:
            starty,endy = endy,starty
        
        curx = self.pos[0] - self.width/2
        # add 0.01 to avoid float errors
        cury = starty + 0.01
        curz = self.pos[2] - self.width/2
        while cury < endy:
            # Set the correct step block type
            if cury%1 < 0.5:
                curblock = 44
            else:
                curblock = 43
            # Make the step
            set_blocklist(curx,int(cury),curz,curblock,blocklist)
            # Increment the curx and curz variables.
            # Use a hash table.
            idx = (int((cury-starty)*2) / (self.width - 1))%4
            move = self.movement_lookup[idx]
            curx, curz = move(curx, curz)
            #increment the other essential variables
            cury += 0.5
            
            
            
    
    def __init__(self, width=3, position=[0,0,0], height=1.0):
        self.width = width
        self.pos = position
        self.height = height
        
        
def findintersections(blocklist,mcmap):
    '''Find the average heights of the intersections and return intersections.
    
    Designed for finding the road intersections, but also used for subways.
    '''
    def averageheight(centerx,centerz):
        divisor = 0.
        heightsum = 0.
        #iterate over all of the squares
        maptop = mcmap.dims[1] - 1
        for xoffset in range(ROADWIDTH):
            x = centerx + xoffset - ROADWIDTH/2
            for zoffset in range(ROADWIDTH):
                z = centerz + zoffset - ROADWIDTH/2
                # Find the ground height
                coord = [x,maptop,z]
                groundheight = (0.714159 + mcmap.dims[1] - 1 - 
                                dist_to_mat(coord,[0,-1,0],0,mcmap,invert=True))
                # Add it to the sum
                heightsum += groundheight
                # Add one to the divisor
                divisor += 1
        # Calculate the average;  Use float math.
        averageheight = heightsum/divisor
        return averageheight
    
    # Set up the list of intersection heights
    intersections = []
    # Set up the distance between each road
    xoffset = mcmap.dims[0] / (ROADNUM + 1)
    zoffset = mcmap.dims[2] / (ROADNUM + 1)
    # Make each intersection, and record the height of each
    for zidx in range(ROADNUM):
        z = zoffset * (zidx + 1)
        for xidx in range(ROADNUM):
            x = xoffset * (xidx + 1)
            intersectionheight = averageheight(x,z)
            intersections += [[x,intersectionheight,z]]
            
    return intersections

class SquareExtrusion(object):
    indexlist = [(2,1),(0,2),(0,1)]
    
    def squaresection(self,center,size,diraxis,matidx,blocklist,
                      hollow=False, torches = False):
        '''Create a square section of type matidx in blocklist.
        
        Passed values:
        center = [x,y,z] for the coordinates of the center block
        radius = <number> as the radius of the section.  May be a float or int.
        diraxis: The list index for the axis to make the section
        perpendicular to.  0 indicates the x axis, 1 the y, 2 the z.  The
        section will extend along the other two axies.
        matidx = <int> the integer value to make the section out of.
        blocklist = the array generated by make_blocklist
        hollow designates whether the section will be filled or just a shell
        '''
        start = -int(size/2.)
        end = int(start + size)
        secidx1, secidx2 = self.indexlist[diraxis]
        coord = [0,0,0]
        for off1 in range(start,end):
            for off2 in range(start,end):
                a = (off1 in [start,end-1])
                b = (off2 in [start,end-1])
                if (not ((a or b) and not (a and b))) and hollow:
                    continue
                pri = center[diraxis]
                sec1 = center[secidx1] + off1
                sec2 = center[secidx2] + off2
                coord[diraxis] = int(pri)
                coord[secidx1] = int(sec1)
                coord[secidx2] = int(sec2)
                if off1 in [start,end-1] and off2 == 0 and torches:
                    mat = 50
                else:
                    mat = matidx
                set_blocklist(coord[0],coord[1],coord[2],mat,blocklist)
    
    def makeextrusion(self,matidx,blocklist,hollow=False,
                      capped=True, lights=False):
        '''Create a square crossection extrusion in blocklist.
        
        start and end are the beginning and ending coordinates of form [x,y,z].
        size is the size of the square section.
        matidx is the material to make the segment out of
        hollow indicates whether or not the sgement should be hollow
        '''
        
        start = self.start
        end = self.end
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
        secidx1, secidx2 = self.indexlist[primidx]
        # primsign is the digit 1 or -1 depending on whether the limb is headed
        # along the positive or negative primidx axis.
        primsign = int(delta[primidx]/abs(delta[primidx]))
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
        endoffset = int(delta[primidx] + primsign)
        if hollow and capped:
            # Cap the starting end
            primloc = start[primidx] - primsign
            secloc1 = start[secidx1]
            secloc2 = start[secidx2]
            coord[primidx] = primloc
            coord[secidx1] = secloc1
            coord[secidx2] = secloc2
            self.squaresection(coord, self.size - 2, primidx,matidx,blocklist)
            # Cap the ending end
            primloc = start[primidx] + endoffset
            secloc1 = start[secidx1] + endoffset*secfac1
            secloc2 = start[secidx2] + endoffset*secfac2
            coord[primidx] = primloc
            coord[secidx1] = secloc1
            coord[secidx2] = secloc2
            self.squaresection(coord, self.size - 2, primidx,matidx,blocklist)
            
        for primoffset in range(0, endoffset, primsign):
            primloc = start[primidx] + primoffset
            secloc1 = start[secidx1] + primoffset*secfac1
            secloc2 = start[secidx2] + primoffset*secfac2
            coord[primidx] = primloc
            coord[secidx1] = secloc1
            coord[secidx2] = secloc2
            if lights and primoffset%lights == 0:
                torches = True
            else:
                torches = False
            self.squaresection(coord,self.size,primidx,matidx,blocklist,
                               hollow,torches)
                
                
        
    def __init__(self, start=[0,0,0], end=[0,0,0], size=2):
        # These are the two points to connect with the square extrusion
        self.start = start
        self.end = end
        # This is the dimension of extrusion.  The outer dimension will
        # be size + 2 .
        self.size = size

        
class Tunnel(SquareExtrusion):
    '''Makes a square tunnel, open on both ends.
    
    Takes starting and ending coordinates.
    
    Has three main methods:
    makewalls, and makefill
    '''
                
    def makewalls(self,blocklist):
        '''make the walls outside of the tunnel'''
        realsize = self.size
        self.size += 2
        mat = self.mat
        self.makeextrusion(mat,blocklist,hollow=True,capped=self.capped)
        self.size = realsize
    
    def makefill(self,blocklist):
        '''clear the center of the tunnel'''
        mat = self.fillmat
        self.makeextrusion(mat,blocklist,lights=self.lights)
    
    def __init__(self, start=[0,0,0], end=[0,0,0], size=2, mat=4, fillmat=0,
                 capped=True, lights=False):
        SquareExtrusion.__init__(self, start, end, size)
        self.mat = mat
        self.fillmat = fillmat
        self.capped = capped
        self.lights = lights
        

def makesubways(intersections, blocklist, mcmap):
    '''Generate the subways and the stairs leading up from them.
    '''
    assert isinstance(mcmap, McLevel)
    
    # Which road indexes should we make subways for?
    indexlist = [0,ROADNUM-1,ROADNUM*(ROADNUM-1),ROADNUM**2 - 1]
    # What are the positions of those subways?
    positions = []
    subwayoffset = int(SUBWAYWIDTH / 2) + 1
    stairwidth = max(ROADWIDTH,3)
    stairoffset = int((ROADWIDTH + stairwidth)*0.5)
    wallmaterial = SUBWAYMAT
    # Populate the positions list
    for idx in indexlist:
        thispos = intersections[idx]
        x = thispos[0]
        y = thispos[1]
        z = thispos[2]
        # The first position is in the center of the road
        positions += [{"road":[x,y,z]}]
        # Offset so the risers are not on top of the roads
        if x < mcmap.dims[0]/2:
            x += stairoffset + 1
        else:
            x += -stairoffset - 1
        if z < mcmap.dims[0]/2:
            z += stairoffset + 1
        else:
            z += -stairoffset - 1
        # The second position is in the center of the staircase
        positions[-1].update({"stairs":[x,SUBWAYPOSITION,z]})
        subwaymid = SUBWAYPOSITION - SUBWAYWIDTH/2 + SUBWAYWIDTH - SUBWAYWIDTH%2
        positions[-1].update({"subway":[x,subwaymid,z]})
    
    # Make a list of tunnels
    tunnellist = []
    # make the shells for the stairs and enter the subway corner data
    for pos in positions:
        start = pos["stairs"][:]
        end = start[:]
        end[1] = pos["road"][1]+stairwidth
        stairwell = Tunnel(start,end,stairwidth,wallmaterial,
                           lights=SUBWAYLIGHTING)
        tunnellist += [stairwell]
        # Re-set the start and end to make shelters over the stairs
        sheltstart = end[:]
        sheltstart[1] += -stairwidth/2 + 1
        sheltstart[0] += -stairwidth/2 -1*(1 - stairwidth%2)
        sheltend = sheltstart[:]
        sheltend[0] += stairwidth + 1
        stairshelter = Tunnel(sheltstart,sheltend,stairwidth,wallmaterial,
                              capped=False)
        tunnellist += [stairshelter]
        sheltstart = end[:]
        sheltstart[1] += -stairwidth/2 + 1
        sheltstart[2] += -stairwidth/2 -1*(1 - stairwidth%2)
        sheltend = sheltstart[:]
        sheltend[2] += stairwidth + 1
        stairshelter = Tunnel(sheltstart,sheltend,stairwidth,wallmaterial,
                              capped=False)
        tunnellist += [stairshelter]
    
    # Make the subway tunnels
    start = positions[0]["subway"][:]
    end = positions[1]["subway"][:]
    subwaytunnel = Tunnel(start,end,SUBWAYWIDTH,wallmaterial,
                          lights=SUBWAYLIGHTING)
    tunnellist += [subwaytunnel]
    end = positions[2]["subway"][:]
    subwaytunnel = Tunnel(start,end,SUBWAYWIDTH,wallmaterial,
                          lights=SUBWAYLIGHTING)
    tunnellist += [subwaytunnel]
    start = positions[3]["subway"][:]
    end = positions[1]["subway"][:]
    subwaytunnel = Tunnel(start,end,SUBWAYWIDTH,wallmaterial,
                          lights=SUBWAYLIGHTING)
    tunnellist += [subwaytunnel]
    end = positions[2]["subway"][:]
    subwaytunnel = Tunnel(start,end,SUBWAYWIDTH,wallmaterial,
                          lights=SUBWAYLIGHTING)
    tunnellist += [subwaytunnel]
    
    for tunnel in tunnellist:
        tunnel.makewalls(blocklist)
    
    for tunnel in tunnellist:
        tunnel.makefill(blocklist)
    
    # make the stairs
    for pos in positions:
        stairposition = pos["stairs"][:]
        stairheight = pos["road"][1] - SUBWAYPOSITION
        stairs = Staircase(stairwidth,stairposition,stairheight)
        stairs.create(blocklist)

def makeroads(intersections,blocklist,mcmap):
    '''Generate roads on the surface and enter them into blocklist.
    
    Also make the sewers
    '''
    assert isinstance(mcmap, McLevel)
                    
    def pave(x,z,height):
        '''Pave at height and return the ground height.
        
        Cut, fill, tunnel, and bridge as required.        
        Only affects the column at coordinates x,z.
        '''
        assert isinstance(mcmap, McLevel)
        maptop = mcmap.dims[1] - 1
        coord = [x,maptop,z]
        # Search for the highest block in the column which is not air
        groundheight = maptop - dist_to_mat(coord,[0,-1,0],0,mcmap,invert=True)
        coord = [x,groundheight,z]
        idx = coord_to_idx(coord,mcmap)
        groundmat = ord(mcmap.blocktypelist()[idx])
        while groundmat in [6,8,9,10,11,37,38,39,
                            40,50,51,52,53,54,55,58,59,60]:
            coord[1] += -1
            groundheight += -1
            groundheight += -dist_to_mat(coord,[0,-1,0],groundmat,
                                         mcmap,invert=True)
            coord = [x,groundheight,z]
            idx = coord_to_idx(coord,mcmap)
            groundmat = ord(mcmap.blocktypelist()[idx])
        
        if groundheight > height:
            if groundheight - height <= ROADCUT:
                #cut
                for y in range(int(height)+1,groundheight+1):
                    set_blocklist(x,y,z,0,blocklist)
            else:
                #tunnel
                for y in range(int(height)+1,int(height + ROADTUNNEL) + 1):
                    set_blocklist(x,y,z,0,blocklist)
                
        else:
            if int(height) - groundheight <= ROADFILL:
                #fill
                for y in range(groundheight,int(height)):
                    set_blocklist(x,y,z,groundmat,blocklist)
            else:
                #bridge
                for y in range(int(height-ROADBRIDGE),int(height)):
                    set_blocklist(x,y,z,43,blocklist)
        #pave the spot itself
        if height%1 > 0.5:
            pavemat = 43
        else:
            pavemat = 44
        set_blocklist(x,int(height),z,pavemat,blocklist)
        return groundheight
    
    def roadonaxis(axisidx, axisloc, axisstart, axisend, starty, endy):
        '''Make a road along the axis specified.
        
        axisidx is 0 for x or 2 for z
        axisloc is the value of the other axis.  For instance
        If axisidx is 2, then the road will be made along the z axis, and
        axisloc will give the x value of the road.
        '''
        otheridx = 2 - axisidx
        coord = [0,0,0]
        yoffperstep = float(endy - starty)/float(axisend - axisstart)
        y = starty
        for primaxisloc in range(axisstart,axisend + 1):
            #axisloc is x
            #offset goes from 0 to raodwidth - 1
            coord[axisidx] = primaxisloc
            for offset in range(ROADWIDTH):
                coord[otheridx] = axisloc + offset - ROADWIDTH/2
                coord[1] = y
                pave(coord[0],coord[2],coord[1])
            #make the lamp post
            if ROADLIGHTING and primaxisloc%ROADLIGHTING == 0:
                lampcoord = coord[:]
                lampcoord[1] = int(lampcoord[1] - 1 - ROADBRIDGE)
                lampcoord[otheridx] += 1
                while lampcoord[1] <= y + ROADTUNNEL:
                    lampcoord[1] += 1
                    set_blocklist(lampcoord[0],lampcoord[1],lampcoord[2],
                                  LAMPMAT,blocklist)
                while lampcoord[otheridx] > axisloc + 2:
                    lampcoord[otheridx] += -1
                    set_blocklist(lampcoord[0],lampcoord[1],lampcoord[2],
                                  LAMPMAT,blocklist)
                #make the torch
                lampcoord[otheridx] += -1
                set_blocklist(lampcoord[0],lampcoord[1],lampcoord[2],
                              50,blocklist)
                #make the shading
                sidecoord = lampcoord[:]
                sidecoord[1] = sidecoord[1] + 1
                set_blocklist(sidecoord[0],sidecoord[1],sidecoord[2],
                              LAMPSHADEMAT,blocklist)
                sidecoord = lampcoord[:]
                sidecoord[axisidx] += 1
                set_blocklist(sidecoord[0],sidecoord[1],sidecoord[2],
                              LAMPSHADEMAT,blocklist)
                sidecoord = lampcoord[:]
                sidecoord[axisidx] += -1
                set_blocklist(sidecoord[0],sidecoord[1],sidecoord[2],
                              LAMPSHADEMAT,blocklist)
                sidecoord = lampcoord[:]
                sidecoord[otheridx] += -1
                set_blocklist(sidecoord[0],sidecoord[1],sidecoord[2],
                              LAMPSHADEMAT,blocklist)
                
            y += yoffperstep
    
    def makeintersection(centerx,height,centerz):
        '''Find and pave the height of the intersection, and return the height.
        
        The height of the node is the average of all the ground heights.
        '''
        # pave all of the squares in the intersection at the average height
        for xoffset in range(ROADWIDTH):
            x = centerx + xoffset - ROADWIDTH/2
            for zoffset in range(ROADWIDTH):
                z = centerz + zoffset - ROADWIDTH/2
                pave(x,z,height)
    
    def makeutilities(startpos,endpos,pipelist):
        '''Make the water, lava, and sewer service lines under the road.
        '''
        # make copies of the original positions, so they aren't contaminated.
        start = startpos[:]
        end = endpos[:]
        if WATERSISZE:
            for vec in [start,end]:
                vec[1] += -WATERSISZE - 2
            waterline = Tunnel(start[:],end[:],WATERSISZE,WATERMAT,52)
            pipelist += [waterline]
        if LAVASIZE:
            for vec in [start,end]:
                vec[1] += -LAVASIZE - 2
            lavaline = Tunnel(start[:],end[:],LAVASIZE,LAVAMAT,53)
            pipelist += [lavaline]
        if SEWERSIZE:
            for vec in [start,end]:
                vec[1] += -SEWERSIZE - 2
            sewerline = Tunnel(start[:],end[:],SEWERSIZE,SEWERMAT,
                               lights=SEWERLIGHTING)
            pipelist += [sewerline]
        
    # Set up the distance between each road
    xoffset = mcmap.dims[0] / (ROADNUM + 1)
    zoffset = mcmap.dims[2] / (ROADNUM + 1)
    # For each intersection, pave it, and 
    # make roads to the two adjacent intersections
    pipelist = []
    for idx in range(len(intersections)):
        xidxnext = idx + 1
        zidxnext = (idx + ROADNUM)
        thispos = intersections[idx]
        x = thispos[0]
        y = thispos[1]
        z = thispos[2]
        # Pave the intersecion
        makeintersection(x,y,z)
        # make a road along x, if you aren't at the end of an x row.
        if (idx+1) % ROADNUM != 0:
            nextpos = intersections[xidxnext]
            nextheight = nextpos[1]
            thisx = x + ROADWIDTH - ROADWIDTH/2
            nextx = nextpos[0] - ROADWIDTH/2 - 1
            slope = abs(y - nextheight) / (nextx - thisx)
            if slope <= ROADSLOPE:
                if ROADS:
                    roadonaxis(0, z, thisx, nextx, y, nextheight)
                start = [x,y,z]
                end = [nextpos[0],nextheight,z]
                makeutilities(start,end,pipelist)
                
        # make a road along z, if you aren't at the end of a z row.
        if (idx/ROADNUM) + 1 != ROADNUM:
            nextpos = intersections[zidxnext]
            nextheight = nextpos[1]
            thisz = z + ROADWIDTH - ROADWIDTH/2
            nextz = nextpos[2] - ROADWIDTH/2 - 1
            slope = abs(y - nextheight) / (nextz - thisz)
            if slope <= ROADSLOPE:
                if ROADS:
                    roadonaxis(2, x, thisz, nextz, y, nextheight)
                start = [x,y,z]
                end = [x,nextheight,nextpos[2]]
                makeutilities(start,end,pipelist)
            
    for line in pipelist:
        line.makewalls(blocklist)
    for line in pipelist:
        line.makefill(blocklist)

class Building(object):
    def place(self, mcmap, blocklist):
        assert isinstance(mcmap, McLevel)
        corner = self.position
        for x in range(corner[0], corner[0] + self.size[0]):
            for z in range(corner[2], corner[2] + self.size[1]):
                for y in range(int(corner[1] - FOUNDATIONDEPTH), int(corner[1]) + self.stories * STORYHEIGHT):
                    if y < int(corner[1]): mat = FOUNDATIONMAT
                    else: mat = BUILDINGMAT
                    set_blocklist(x,y,z,mat,blocklist)
        
    
    def __init__(self, corner = [0,0,0], footprint = [1,1], height=1):
        self.position = corner[:]
        self.size = footprint[:]
        self.stories = height
        
def place_buildings(intersections, blocklist, mcmap):
    assert isinstance(mcmap, McLevel)
    for idx in range(len(intersections)):
        corneridx = idx + ROADNUM + 1
        if ( ((corneridx) % ROADNUM == 0) or 
             (corneridx > ROADNUM**2 ) ):
            continue
        if random() > BUILDINGDENSITY: continue
        thispos = intersections[idx]
        otherpos = intersections[corneridx]
        allheights = [intersections[id][1] for id in [idx,idx+1,idx+ROADNUM,
                                                   idx+ROADNUM+1] ]
        
        x = thispos[0] + ROADWIDTH
        y = min(allheights) + 1
        z = thispos[2] + ROADWIDTH
        
        x_size = otherpos[0] - ROADWIDTH - x
        z_size = otherpos[2] - ROADWIDTH - z
        
        size_reduction = choice(range(int(min([x_size,z_size])*0.618)))
        if size_reduction:
            x += choice(range(size_reduction))
            z += choice(range(size_reduction))
            x_size += -size_reduction
            z_size += -size_reduction
        
        stories = choice(range(BUILDINGHEIGHTMIN, BUILDINGHEIGHTMAX + 1))
        thisbuilding = Building([x,y,z], [x_size, z_size], stories)
        thisbuilding.place(mcmap, blocklist)
        
        

def main():
    '''Load the file, create the infrastructure, and save the new file.
    '''
    print("Importing the map")
    the_map = McLevel()
    the_map.import_map(LOADNAME)
    fileblockstring = the_map.blocktypelist()
    mapsize = the_map.mapdims()
    print("generating the blocklist")
    blocklist = make_blocklist(the_map)
    
    print("Finding the intersections")
    intersections = findintersections(blocklist,the_map)
    
    print("Laying the roads and utilities")
    makeroads(intersections, blocklist, the_map)
    
    if BUILDINGS:
        print("making the buildings")
        place_buildings(intersections, blocklist, the_map)
    
    if SUBWAYS:
        print("Digging subways")
        makesubways(intersections, blocklist, the_map)
    
    print("making the new map (takes much longer for larger maps)")
    newblockstring = ""
    idx = 0
    for y in range(mapsize[1]):
        if y%4 == 0: print(".")
        for z in range(mapsize[2]):
            for x in range(mapsize[0]):
                thismat = blocklist[x][y][z]
                if thismat == -1:
                    thismat = ord(fileblockstring[idx])
                newblockstring += chr(thismat)
                idx += 1
                    
    print("Saving the map (takes a bit)")
    the_map.setblocktypes(newblockstring)
    the_map.export_map(SAVENAME)
    print("finished")
    return None


if __name__ == '__main__':
    main()