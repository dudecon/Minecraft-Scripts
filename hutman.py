'''This takes a base MineCraft level and adds little huts.
It then saves the new map.
'''

# Here are the variables you can edit.

# this is the name of the map to load in
LOADNAME = "test.mclevel"

# this is the name of the map to save out when it is done
SAVENAME = "testresult.mclevel"

# How many huts would you like?
HUTNUM = 64

# How large (generally) do you want the huts to be?
# Larger numbers result in larger huts.
LOWERITERATIONS = 1
UPPERITERATIONS = 5



##############################################################
#  Don't edit below here unless you know what you are doing  #
##############################################################

# input filtering
LOWERITERATIONS = int(LOWERITERATIONS)
UPPERITERATIONS = int(UPPERITERATIONS)
if LOWERITERATIONS < 0:
    LOWERITERATIONS = 0
if UPPERITERATIONS < LOWERITERATIONS:
    UPPERITERATIONS = LOWERITERATIONS


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

class Hut(object):
    
    offsetlist = [[0,-1],[-1,0],[0,1],[1,0]]
    
    def expand(self):
        floorcordlength = len(self.floorcoords)
        for posidx in range(floorcordlength):
            for diridx in range(4):
                if random() > 0.4:
                    position = self.floorcoords[posidx]
                    generation = self.floorgeneration[posidx]
                    newpos = [position[x] + self.offsetlist[diridx][x] 
                              for x in [0,1]]
                    if newpos not in self.floorcoords:
                        self.floorcoords += [newpos]
                        self.floorgeneration += [generation+1]
                    
    def makewalls(self):
        for idx in range(len(self.floorcoords)):
            position = self.floorcoords[idx]
            for diridx in range(4):
                newpos = [position[x] + self.offsetlist[diridx][x] 
                          for x in [0,1]]
                if ((newpos not in self.floorcoords) and 
                    (newpos not in self.wallcoords)):
                    self.wallcoords += [newpos]
                    self.wallgeneration += [self.floorgeneration[idx]]
    
    def place(self, blocklist, mclevel): 
        # Generate the walls
        self.makewalls()
        # Build the floors, interiors, and roof
        for idx in range(len(self.floorcoords)):
            floorpos = self.floorcoords[idx]
            x = floorpos[0]
            y = self.origin[1] - 1
            z = floorpos[1]
            assign_value(x,y,z,1,blocklist)
            thisheight = self.height - self.floorgeneration[idx]
            if thisheight < 2: thisheight = 2
            for yoff in range(thisheight):
                y += 1
                assign_value(x,y,z,0,blocklist)
            y += 1
            assign_value(x,y,z,5,blocklist)
        
        # Build the walls
        for idx in range(len(self.wallcoords)):
            wallpos = self.wallcoords[idx]
            x = wallpos[0]
            y = self.origin[1] - 1
            z = wallpos[1]
            assign_value(x,y,z,1,blocklist)
            thisheight = self.height - self.wallgeneration[idx]
            if thisheight < 2: thisheight = 2
            for yoff in range(thisheight - 1):
                y += 1
                assign_value(x,y,z,3,blocklist)
            y += 1
            assign_value(x,y,z,2,blocklist)
        
        # Build the door
        doorpos = self.wallcoords[0]
        x = doorpos[0]
        y = self.origin[1]
        z = doorpos[1]
        assign_value(x,y,z,0,blocklist)
        y += 1
        assign_value(x,y,z,0,blocklist)
    
    def __init__(self, position = [65,50,71]):
        self.wallcoords = []
        self.wallgeneration = []
        self.height = 2
        self.origin = position
        self.floorcoords = [ [position[0], position[2]] ]
        self.floorgeneration = [0]
        


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
    
    print("Making the huts")
    for throwaway in range(HUTNUM):
        # Get a random position
        pos = rnd_surface_point(2,the_map)
        pos[1] += 1
        # Genearte the object
        thishut = Hut(pos)
        # Expand it
        thisiter = choice(range(LOWERITERATIONS,UPPERITERATIONS+1))
        for iteration in range(thisiter):
            thishut.expand()
        # Set the height
        if thisiter > 3:
            maxheight = thisiter
        else:
            maxheight = 3
        theheight = choice(range(3,maxheight+1))
        thishut.height = theheight
        # Place the hut
        thishut.place(blocklist, the_map)
    
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