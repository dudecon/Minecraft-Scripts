#Change the height of a .mclevel map.
#
#The new map should be the same but with a higher (or lower) cieling.


# source file 1
FILEIN = "test.mclevel"

# output file
FILEOUT = "testresult.mclevel"

# How much taller do you want the map to be?
# Positive numbers make the map taller.
# Negative numbers make the map shorter.
# Warning!  Multiples of 16 seem to be safe.  Other values may not
# render correctly.
HEIGHT_CHANGE = 64

# What do you want to fill with?
# Examples
# 0 is default, and fills with air. Good for the "top" setting below
# 1 is fills with stone, good for the "bottom" setting below
FILL_BLOCK = 0

# Do you want to modify the bottom or the top?
# "top" adds or subtracts blocks on the top of the map
# "bottom" adds or subtracts blocks on the bottom of the map
SIDE = "top"

##############################################################
#  Don't edit below here unless you know what you are doing  #
##############################################################

HEIGHT_CHANGE = int(HEIGHT_CHANGE)

'''interface class for .mclevel data for minecraft
'''

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

    def setblockdata(self,blockdata):
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
    
    def __init__(self):
        self.filecontents = ""
        self.dims = None
        self.totalblocks = None
        self.blocktypes = None
        self.blockdata = None

# This is the end of the MCLevel interface.

# Now, on to the actual code.


#from mclevel_interface import *

'''the main code'''

def main():
    print("Opening the map file")
    this_map = McLevel()
    this_map.import_map(FILEIN)
    current_types = this_map.blocktypelist()
    current_data = this_map.blockdatalist()
    current_dims = this_map.mapdims()
    change_multiplyer = current_dims[0] * current_dims[2]
    
    print("Applying changes")
    if HEIGHT_CHANGE > 0:
        "make the map taller"
        extra_characters = chr(FILL_BLOCK)*change_multiplyer*HEIGHT_CHANGE
        if SIDE == "top":
            current_types = current_types + extra_characters
        elif SIDE == "bottom":
            current_types = extra_characters + current_types
        extra_characters = chr(0)*change_multiplyer*HEIGHT_CHANGE
        if SIDE == "top":
            current_data = current_data + extra_characters
        elif SIDE == "bottom":
            current_data = extra_characters + current_data
        
    elif HEIGHT_CHANGE < 0:
        "make the map shorter"
        shorten_length = HEIGHT_CHANGE * change_multiplyer
        if SIDE == "top":
            current_types = current_types[:shorten_length]
            current_data = current_data[:shorten_length]
        elif SIDE == "bottom":
            current_types = current_types[shorten_length:]
            current_data = current_data[shorten_length:]
    else:
        return
    
    new_height = current_dims[1] + HEIGHT_CHANGE
    new_dims = [current_dims[0], new_height, current_dims[2]]
    this_map.setmapdims(new_dims)
    this_map.setblockdata(current_data)
    this_map.setblocktypes(current_types)
    
    print("Saving the map (takes a bit)")
    this_map.export_map(FILEOUT)
    print("Finished!")

if __name__ == '__main__':
    main()