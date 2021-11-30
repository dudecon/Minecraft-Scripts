'''interface class for .mclevel data for minecraft

also includes a useful coordinate to index convertor
'''

import gzip

class McLevel(object):
        
    def mapdims(self):
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

'''some handy functions'''

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
    '''return False if the coordinate lies outside the bounds, else return True

    dims is [x,y,z] dimensions for area to be checked
    '''
    dims = mcmap.mapdims()
    x = coordinate[0]
    if x < border or x >= dims[0]-border: return False
    y = coordinate[1]
    if y < border or y >= dims[1]-border: return False
    z = coordinate[2]
    if z < border or z >= dims[2]-border: return False
    return True


def search_column(x,z,matidx,mcmap,ystart = None):
    '''take horizontal position and index, return y value of first occurance from top down'''
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
    '''chooses a random point on the surface of the world
    if the point is over empty space, it returns a random height as well
    '''
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
    if invert == True, find anything other than matidx
    
    example: to search through air for anything non-air,
    set matidx = 0 and invert = True
    '''
    matdata = mcmap.blocktypelist()
    curcord = cord[:]
    iterations = 0
    while in_bounds(curcord,mcmap):
        x = curcord[0]
        y = curcord[1]
        z = curcord[2]
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
    '''find the highest point of matidx and return coords'''
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
