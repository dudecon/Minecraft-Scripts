#Combine two or more .mclevel maps into a single map
#
#The new map will have all of the settings of source file #1
#Currently, the maps must be the same size


# source file 1
FILE1 = "test1.mclevel"

# source file 2
FILE2 = "test2.mclevel"

# output file
FILEOUT = "testresult.mclevel"

# MERGESTYLE specifies how to combine the maps.  The options are:
# "adjacent" to place them next to eachother, along the z axis, FILE1 first
# "stacked" to place them stacked on top of eachother, FILE1 on the bottom
# "collision" to meld the two maps, with blocks picked randomly, crazy effect!
# "column_collision" like collision, but maintain contiguous columns
# "union" any 'air' blocks from FILE1 are filled with the blocks from FILE2

MERGESTYLE = "adjacent"


##############################################################
#  Don't edit below here unless you know what you are doing  #
##############################################################

'''interface class for .mclevel data for minecraft

also includes a useful coordinate to index convertor
'''

import gzip

def coord_to_idx(coord,size):
        '''take the coordinates and return the index location of that data byte

        coord is [x,y,z] in minecraft coordinates
        size is [x_size,y_size,z_size] for the whole map
        returns the index location for that coordinate
        '''
        x = coord[0]
        y = coord[1]
        z = coord[2]
        idx = x + (y * size[2] + z) * size[0]
        return idx

class McLevel(object):
        

    def mapdims(self):
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
        
        return dims

    def setmapdims(self,dims):
        '''warning, sets all block types and data to zero'''
        mapdata = self.filecontents[:]
        x = dims[0]
        y = dims[1]
        z = dims[2]
        idx = mapdata.find(chr(5) + 'Width') + 6
        firstbyte = chr(x/256)
        secondbyte = chr(x%256)
        width = firstbyte + secondbyte
        mapdata = mapdata[:idx] + width + mapdata[idx+2:]

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

        self.filecontents = mapdata
        tempblocktotal = x*y*z
        fillerdata = chr(2)*tempblocktotal
        self.setblocktypes(fillerdata)
        self.setblockdata(fillerdata)
        self.dims = [x,y,z]
        self.totalblocks = tempblocktotal
        

    def blocktypelist(self):
        mapdata = self.filecontents
        start = mapdata.find(chr(6) + 'Blocks') + 11
        end = start + self.totalblocks
        source = self.filecontents[start:end]
        return source

    def setblocktypes(self,blockdata):
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

    def blockdatalist(self):
        mapdata = self.filecontents
        start = mapdata.find(chr(4) + 'Data') + 9
        end = start + self.totalblocks
        source = self.filecontents[start:end]
        return source

    def setblockdata(self,blockdata):
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
    
    def __init__(self):
        self.filecontents = ""
        self.dims = None
        self.totalblocks = None

    def copy(self):
        '''return a copy of this object'''
        newobject = McLevel()
        newobject.filecontents = self.filecontents[:]
        newobject.dims = self.dims[:]
        newobject.totalblocks = self.totalblocks
        return newobject


#from mclevel_interface import *
from random import random

'''the main code'''
class UnifyMaps(object):
    def unify(self):
        '''do the work and return the combined map'''
        self.mapout = self.map1.copy()
        dims1 = self.map1.mapdims()
        dims2 = self.map2.mapdims()
        newdims = self.newdims[:]
        newdims = [0,0,0]
        for i in range(3):
            if dims1[i] > dims2[i]:
                newdims[i] = dims1[i]
            else:
                newdims[i] = dims2[i]
        self.dims1 = dims1
        self.dims2 = dims2
        self.newdims = newdims
        self.indata1 = self.map1.blockdatalist()
        self.indata2 = self.map2.blockdatalist()
        self.intype1 = self.map1.blocktypelist()
        self.intype2 = self.map2.blocktypelist()
        return self.mapout
    def __init__(self,map1,map2):
        self.map1 = map1
        self.map2 = map2
        self.mapout = McLevel()
        self.newdims = [0,0,0]

class AdjacentUnity(UnifyMaps):
    def unify(self):
        '''do the work and return the combined map'''
        mapout = UnifyMaps.unify(self)
        self.newdims[2] = self.dims1[2] + self.dims2[2]
        mapout.setmapdims(self.newdims)
        
        outdata = ""
        outtype = ""
        blocksize = (self.newdims[0] * self.newdims[2])/2
        for i in range(mapout.dims[1]):
            start = i * blocksize
            end = (i+1) * blocksize
            outdata += self.indata1[start:end]
            outtype += self.intype1[start:end]
            
            outdata += self.indata2[start:end]
            outtype += self.intype2[start:end]
        
        mapout.setblockdata(outdata)
        mapout.setblocktypes(outtype)
        
        return mapout

class StackedUnity(UnifyMaps):
    def unify(self):
        '''do the work and return the combined map'''
        mapout = UnifyMaps.unify(self)
        self.newdims[1] = self.dims1[1] + self.dims2[1]
        mapout.setmapdims(self.newdims)

        outdata = ""
        outtype = ""
        
        outdata = self.indata1
        outdata += self.indata2
        outtype = self.intype1
        outtype += self.intype2
                
        
        mapout.setblockdata(outdata)
        mapout.setblocktypes(outtype)
        
        return mapout

class CollisionUnity(UnifyMaps):
    def unify(self):
        '''do the work and return the combined map'''
        mapout = UnifyMaps.unify(self)
        mapout.setmapdims(self.newdims)

        outdata = ""
        outtype = ""        
        for i in range(mapout.totalblocks):
            if random() > 0.5:
                outdata += self.indata1[i]
                outtype += self.intype1[i]
            else:
                outdata += self.indata2[i]
                outtype += self.intype2[i]
                
        
        mapout.setblockdata(outdata)
        mapout.setblocktypes(outtype)
        
        return mapout

class ColumnCollisionUnity(UnifyMaps):
    def unify(self):
        '''do the work and return the combined map'''
        mapout = UnifyMaps.unify(self)
        mapout.setmapdims(self.newdims)

        outdata = ""
        outtype = ""
        rndtablelen = self.newdims[0] * self.newdims[2]
        rndtable = []
        for i in range(rndtablelen):
            rndtable += [random()]
        
        for i in range(mapout.totalblocks):
            tableidx = i%rndtablelen
            if rndtable[tableidx] > 0.5:
                outdata += self.indata1[i]
                outtype += self.intype1[i]
            else:
                outdata += self.indata2[i]
                outtype += self.intype2[i]
                
        
        mapout.setblockdata(outdata)
        mapout.setblocktypes(outtype)
        
        return mapout

class UnionUnity(UnifyMaps):
    def unify(self):
        '''do the work and return the combined map'''
        mapout = UnifyMaps.unify(self)
        mapout.setmapdims(self.newdims)

        outdata = ""
        outtype = ""
        for i in range(mapout.totalblocks):
            thisblocktype = ord(self.intype1[i])
            if thisblocktype == 0:
                outdata += self.indata2[i]
                outtype += self.intype2[i]
            else:
                outdata += self.indata1[i]
                outtype += self.intype1[i]
                
        
        mapout.setblockdata(outdata)
        mapout.setblocktypes(outtype)
        
        return mapout

def choose_style(map1,map2,style):
    styles_allowed = ["adjacent","stacked","collision","column_collision","union"]
    if style not in styles_allowed:
        errorstring = "MERGESTYLE is not a valid style. "
        errorstring += "You entered '" + style + "'. "
        errorstring += "The valid options are: "
        errorstring += str(styles_allowed)[1:-1]
        raise(TypeError(errorstring))
    elif style == "adjacent":
        return AdjacentUnity(map1,map2)
    elif style == "stacked":
        return StackedUnity(map1,map2)
    elif style == "collision":
        return CollisionUnity(map1,map2)
    elif style == "column_collision":
        return ColumnCollisionUnity(map1,map2)
    elif style == "union":
        return UnionUnity(map1,map2)

print("Running Mine Craft Unity utility") 
print("Loading files") 
map1 = McLevel()
map1.import_map(FILE1)
map2 = McLevel()
map2.import_map(FILE2)
print("Setting up merge") 
this_merge = choose_style(map1,map2,MERGESTYLE)
print("Unifying maps") 
newmap = this_merge.unify()
print("Saving") 
newmap.export_map(FILEOUT)
print("Done!") 
