'''This takes a base MineCraft level and adds boulders and craters.
It then saves the new map.
'''

# Here are the variables you can edit.

# this is the name of the map to load in
LOADNAME = "Landscape.mclevel"

# this is the name of the map to save out when it is done
SAVENAME = "CrateredLandscape.mclevel"

# How many boulders and/or craters do you want?
# NOTE: features are created on the surface of the rock, so small features may
# be buried underground.
FEATURENUM = 25

# If you want boulders, set this to True, otherwise, set it to False
# If CRATERS is also True, the boulders will each be sitting in a crater
BOULDERS = True

# How big do you want the boulders to be?
BOULDERSIZE = 5

# How much would you like the size of the boulders to vary?
# This value is a +- value, so with BOULDERSIZE = 5
# and BOULDERRANDOMIZATION = 3, the boulder size will range
# from 2 to 8
BOULDERRANDOMIZATION = 3

# What material would you like the boulders to be?
# Uses the minecraft index number.
BOULDERMAT = 4

# Should boulders occasionally have treasure inside?  Ore, gold, diamond?
# Set to a number between 0 and 1 for some treasure.  Larger numbers creates
# more chance of exotic treasure
# for normal old boulders set to 0
BOULDERTREASURE = 0.3

# Should the boulders be scattered thruought the level vertically as well?
# Frees the boulders from the surface and makes them appear randomly in the 
# y axis as well.  This can result in boulders underground or floating
# in the middle of the air.
# If set to true, this will force CRATERS to turn off.
FLYINGBOULDERS = False

# If you want craters set this to True, otherwise, set it to False.
# If BOULDERS is set, there will be a boulder in the middle of each crater.
CRATERS = True

# How wide should the craters be?
CRATERSIZE = 21

# How much should the crater size vary?
# same principle as BOULDERRANDOMIZATION
CRATERRANDOMIZATION = 5

# Fill the craters with water at sea level?
# Good for island maps where you don't want to have water flooding
# into seabed craters.
# Set True to enable, set False to disable
CRATERFLOOD = True

# Fill the bottom of the craters with lava?
# Good for simulating recent impacts.
# Set to 0 to disable
# the value is the fraction of the crater, where 1 makes a semi-sphere
# of lava.  Values can go up to 2.0, which will make a full sphere of lava.
# suggested values are between 0.05 and 0.6
CRATERLAVA = .15


##############################################################
#  Don't edit below here unless you know what you are doing  #
##############################################################

# input filtering
if FEATURENUM < 0:
    FEATURENUM = 1
    
if BOULDERS:
    if BOULDERSIZE < 1:
        BOULDERSIZE = 1
    if BOULDERRANDOMIZATION < 0:
        BOULDERRANDOMIZATION = 0
    if BOULDERTREASURE < 0:
        BOULDERTREASURE = 0
    elif BOULDERTREASURE > 1:
        BOULDERTREASURE = 1
    if FLYINGBOULDERS:
        CRATERS = False

if CRATERS:
    if CRATERSIZE < 1:
        CRATERSIZE = 1
    if CRATERRANDOMIZATION < 0:
        CRATERRANDOMIZATION = 0
    if CRATERLAVA < 0:
        CRATERLAVA = 0
    elif CRATERLAVA > 2.0:
        CRATERLAVA = 2.0


# The following is an interface class for .mclevel data for minecraft savefiles.
# The following also includes a useful coordinate to index convertor and several
# other useful functions.


import gzip


class McLevel(object):
    '''An interface object to alow loading and saving of map data from
    a minecraft save file of extension '.mclevel'
    '''
    
    def mapsealevel(self):
        '''Return the y coordinate of the sea level of the map
        
        Cache the sea level for quicker access.
        '''
        if self.sealevel == None:
            mapdata = self.filecontents
            idx = mapdata.find(chr(22) + 'SurroundingWaterHeight') + 23
            firstbyte = ord(mapdata[idx])
            secondbyte = ord(mapdata[idx+1])
            sea_level = firstbyte * 256 + secondbyte
            self.sealevel = sea_level
        else:
            sea_level = self.sealevel
        return sea_level
            
        
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
        self.sealevel = None

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
    Initialize the values with False.  This value indicates no replacement of
    the current map data.
    '''
    assert isinstance(mcmap, McLevel)
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

class SphereObject(object):
    '''A spherical object.
    
    It has a method to create itself in blocklist.
    Designed for subclassing.
    '''
    def create(self,blocklist):
        locx = self.loc[0]
        locy = self.loc[1]
        locz = self.loc[2]
        radius = self.size*0.5
        for y in range(int(locy),
                       int(locy + radius*2 + 1)
                       ):
            if y < locy + radius * 0.25:
                mat = self.fillmat
            else:
                mat = self.mat
            for x in range(int(locx - radius),
                       int(locx + radius + 1)
                        ):
                for z in range(int(locz - radius),
                       int(locz + radius + 1)
                        ):
                    dist = sqrt(
                        (locx - x)**2 + 
                        (locy + radius - y)**2 + 
                        (locz - z)**2
                        )
                    if dist > radius:
                        continue
                    set_blocklist(x,y,z,mat,blocklist)
        return None
    
    def __init__(self, location=[0,0,0], mat=0, size=-1):
        # self.loc is the location of the bottom of the object
        self.loc = location
        # self.size is the radius of the object
        self.size = size
        # self.mat is the material index to use for this object
        self.mat = mat
        self.fillmat = mat

class Boulder(SphereObject):
    '''A large roundish stone object.
    
    Has some material properties, and a method to create itself in blocklist.
    '''
    Treasurelist = [16,15,14]
    TreasureRare = [10,53,49,41,57,42,41,42,57]
    def create(self,blocklist):
        SphereObject.create(self,blocklist)
        if BOULDERTREASURE:
            coresize = (0.618 + random())*self.size*0.5
            coreloc = self.loc[:]
            coreloc[1] += (self.size - coresize)* 0.5
            coremat = self.mat
            i = -1
            while True:
                if random() < BOULDERTREASURE:
                    i += 1
                else:
                    break
                if i == 3:
                    break
            if i in [0,1,2]:
                coremat = self.Treasurelist[i]
            elif i == 3:
                coremat = choice(self.TreasureRare)
            
            core = SphereObject(coreloc,coremat,coresize)
            core.create(blocklist)       
            
    def __init__(self, location=[0,0,0], size=-1):
        mat = BOULDERMAT
        SphereObject.__init__(self, location=location, mat = mat, size=size)
        if self.size == -1:
            sizemin = BOULDERSIZE - BOULDERRANDOMIZATION
            sizevary = BOULDERRANDOMIZATION * 2.
            size = sizemin + random()*sizevary
            self.size = size

class Crater(SphereObject):
    '''A large roundish hole in the ground.
    
    Has a method to create itself in blocklist.
    '''
    def create(self,blocklist):
        if CRATERLAVA:
            self.fillmat = 10
        SphereObject.create(self,blocklist)
    
    def __init__(self, location=[0,0,0], size=-1):
        SphereObject.__init__(self, location=location, size=size)
        if self.size == -1:
            sizemin = CRATERSIZE - CRATERRANDOMIZATION
            sizevary = CRATERRANDOMIZATION * 2.
            size = sizemin + random()*sizevary
            self.size = size


def selectlocations(mcmap):
    '''return a list of locations to put the objects on the surface of the map.
    '''
    assert isinstance(mcmap, McLevel)
    maxsize = max(BOULDERSIZE,CRATERSIZE)
    pad = int(maxsize/2)
    xchoices = range(mcmap.dims[0])[pad:-pad]
    ychoices = range(mcmap.dims[1])[pad:-pad]
    zchoices = range(mcmap.dims[2])[pad:-pad]
    featurelocs = []
    while len(featurelocs) < FEATURENUM:
        x = choice(xchoices)
        z = choice(zchoices)
        if FLYINGBOULDERS:
            y = choice(ychoices)
            featurelocs += [[x,y,z]]
            continue
        
        yrock = search_column(x,z,1,mcmap)
        if yrock is None:
            continue
        if CRATERS:
            y = yrock - int(sqrt(CRATERSIZE/2.))
        else:
            y = yrock
        featurelocs += [[x,y,z]]
    return featurelocs
        

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
    locations = selectlocations(the_map)
    
    if CRATERS:
        print('Making craters')
        for loc in locations:
            thiscrater = Crater(loc)
            thiscrater.create(blocklist)
    
    if BOULDERS:
        print('Making boulders')
        for loc in locations:
            thisboulder = Boulder(loc)
            thisboulder.create(blocklist)
    
    print("making the new map (takes much longer for larger maps)")
    newblockstring = ""
    if CRATERFLOOD:
        sealevel = the_map.mapsealevel()
        for y in range(mapsize[1]):
            if y%4 == 0: print(".")
            for z in range(mapsize[2]):
                for x in range(mapsize[0]):
                    thismat = blocklist[x][y][z]
                    if sealevel > y and thismat == 0:
                            thismat = 9
                    elif thismat == -1:
                        idx = coord_to_idx([x,y,z],the_map)
                        newblockstring += fileblockstring[idx]
                        continue
                    newblockstring += chr(thismat)
                    
    else:
        for y in range(mapsize[1]):
            if y%4 == 0: print(".")
            for z in range(mapsize[2]):
                for x in range(mapsize[0]):
                    thismat = blocklist[x][y][z]
                    if thismat == -1:
                        idx = coord_to_idx([x,y,z],the_map)
                        newblockstring += fileblockstring[idx]
                    else:
                        newblockstring += chr(thismat)
                    
                    
    
    print("Saving the map (takes a bit)")
    the_map.setblocktypes(newblockstring)
    the_map.export_map(SAVENAME)
    print("finished")
    return None


if __name__ == '__main__':
    main()
    
# Needed updates:
# magma in the bottom of fresh craters
# Not removing water for old craters