'''This takes a base MineCraft level and adds a
fortress plus some randomly placed towers (edit number below)
'''

# this is the name of the map to load in
LOADNAME = "CastleBase.mclevel"

# this is the name of the map to save out when it is done
SAVENAME = "Castle.mclevel"

#set PLACEMENT to "auto" if you want the fortress on the highest point of rock.
#otherwise, set the coordinates as follows
#if you want it on the surface with coordinates x,z, set PLACEMENT = [x,z]
#if you want to fully specify the coordinates, set PLACEMENT = [x,y,z]
PLACEMENT = "auto"

#set FORTSIZE to "auto" if you want the fortress to be sized automatically based
#on the environment.
#otherwise, set the x, y and z size as FORTSIZE = [x,y,z]
#NOTE!
#it is highly recomended that you set the size manually if you
#have set PLACEMENT to something other than "auto"
FORTSIZE = "auto"

# how many small watchtowers do you want spread around?
WATCHTOWERCOUNT = 0

# what material index would you like the walls to be made of?
PRIMEMAT = 4

# What material would you like the floors and stairs to be made of?
SECMAT = 5

# What material would you like the doors to be made of?
DOORMAT = 17

# What material would you like the interior doors to be made of?
INTDOORMAT = 3

# Makes taller towers on narrow peaks
SLOPEMULTIPLYER = 3.0

##############################################################
#  Don't edit below here unless you know what you are doing  #
##############################################################

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
    '''take horizontal position and index, return y value of first occurance.
    
    Search the column from the top down.
    It also needs a MCLevel object, hopefully with data already loaded.'''
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

'''now the setup classes for the castle itself
'''
from random import random


class DfBlockSolid(object):
    '''encapsulate material and shape information, and yeild it on request

    material is the base material index.  DfBlock objects use MineCraft
    material indexes.
    Width, length, and height specify how many MineCraft blocks per
    DF block.  width = x, length = z, height = y
    wallmat is the index value for the wall material.
    wallmat is the index value for the window material.
    walls is a bitcode array in the following format:
    [x,z]
    for both x and z: 0 = none 1 = negative side, 2 = positive side, 3 = both
    '''
    width = 3
    length = 3
    height = 3
    def get_wallmat(self,xoff,y,zoff):
        if y == 0:
            return self.wallmat
        if abs(xoff) + abs(zoff) == 2:
            return self.wallmat
        else:
            return self.windowmat
    
    def check_walls(self,x,y,z):
        '''take the local cords and return material index for walls or None'''
        walls = self.walls
        if self.walls[0] == 0 and self.walls[1] == 0:
            return None
        
        
        offx = x - 1
        offz = z - 1
        if offx == -(walls[0]%2) and offx != 0:
            return self.get_wallmat(offx,y,offz)
        elif offx == ((walls[0]/2)%2) and offx != 0:
            return self.get_wallmat(offx,y,offz)
        elif offz == -(walls[1]%2) and offz != 0:
            return self.get_wallmat(offx,y,offz)
        elif offz == ((walls[1]/2)%2) and offz != 0:
            return self.get_wallmat(offx,y,offz)
        if self.material == 0:
            torchy = 0
        else:
            torchy = 1
        if walls[0] > 0 and walls[1] > 0 and offx==0 and offz==0 and y==torchy:
            return 50
        return None
    
    def get_material(self,x,y,z):
        '''return the material index

        The coordinates x,y,z are local and reference MineCraft orientation.
        Override this method for non-uniform blocks.
        '''
        wallnum = self.check_walls(x,y,z)
        if wallnum != None:
            return wallnum
        return self.material
    def __init__(self):
        self.material = 0
        '''Initialize the DF block.'''
        self.walls = [0,0]
        self.wallmat = 0
        self.windowmat = 20

class DfBlockFloor(DfBlockSolid):
    def get_material(self,x,y,z):
        wallnum = self.check_walls(x,y,z)
        if wallnum != None:
            return wallnum
        if y == 0: return self.material
        else: return 0

    def __init__(self):
        DfBlockSolid.__init__(self)

class DfBlockStairUpDown(DfBlockSolid):
    matmap = [[[-1,-1,-1],[-1,-1,0],[-1,0,0]],
              [[-1,-1,-1],[0,0,0],[50,0,0]],
              [[0,0,0],[0,0,0],[0,0,0]]
              ]
    
    
    def get_material(self,x,y,z):
        '''Return material value for locations where stair exists.
        
        Otherwise, return index for air.
        Allows sub-classing for only up and only down staircases.
        '''
        newx = x
        newy = y
        newz = z
        if self.flip == True:
            newx = self.width-x-1
            newz = self.length-z-1
        idx = self.matmap[newx][newy][newz]
        if idx == -1:
            matindex = self.material
        else:
            matindex = idx
        return matindex
        
    def __init__(self):
        DfBlockSolid.__init__(self)
        self.flip = False

class DfBlockStairUp(DfBlockStairUpDown):
    def get_material(self,x,y,z):
        if y > 0:
            return DfBlockStairUpDown.get_material(self,x,y,z)
        else:
            return self.material

class DfBlockStairDown(DfBlockStairUpDown):
    def get_material(self,x,y,z):
        if y == 0:
            return DfBlockStairUpDown.get_material(self,x,y,z)
        else:
            return 0

class DfBlockRamp(DfBlockSolid):
    '''default ramp ascending to the right

    subclass to change the direction?
    '''
    def get_material(self,x,y,z):
        if x == y : return self.material
        else: return 0

def setup_dfblocks(dims):
    dfblocklist = []
    dflength = dims[2]/3 + 1
    dfwidth = dims[0]/3 + 1
    dfheight = dims[1]/3 + 1
    #print(dfwidth, dfheight, dflength)
    
    for z in range(dfwidth):
        row = []
        for y in range(dfheight):
            column = []
            for x in range(dflength):
                column += [None]
            row += [column]
        dfblocklist += [row]
    dfblocklist += [[dfwidth,dfheight,dflength]]
    return dfblocklist

def assign_dfblocks(x,y,z,value,blocklist):
    if x < 0 or y < 0 or z < 0:
        return None
    try:
        blocklist[x][y][z] = value
    except IndexError:
        return None
    return True

def exterior_walls(x,y,z,blocklist):
    '''Take a coordinate and make exterior walls
    
    Only make the exerior walls on the sides where interior walls are
    specified for the indicated block
    x,y,z indicates the block to make the external walls around'''
    try:
        existingblock = blocklist[x][y][z]
    except IndexError:
        return None
    if existingblock == None:
        return None
    walls = existingblock.walls
    if walls[0] != 0 or walls[1] != 0:
        for xoff in [-1,0,1]:
            for zoff in [-1,0,1]:
                if xoff != 0 and zoff != 0: continue
                if xoff == 0 and zoff == 0: continue
                xloc = xoff + 1
                yloc = 1
                zloc = zoff + 1
                val = existingblock.check_walls(xloc,yloc,zloc)
                if val != None:
                    try:
                        exteriorblock = blocklist[x + xoff][y][z + zoff]
                    except IndexError:
                        continue
                    if exteriorblock == None:
                        noneblock = DfBlockSolid()
                        noneblock.material = None
                        exteriorblock = noneblock
                        assign_dfblocks(x + xoff,y,z+zoff,
                                        exteriorblock,blocklist)
                    exteriorblock.wallmat = existingblock.wallmat
                    exteriorblock.windowmat = existingblock.windowmat
                    if xoff != 0:
                        wallaxis = 0
                        if xoff > 0:
                            wallside = 1
                        else:
                            wallside = 2
                    else:
                        wallaxis = 1
                        if zoff > 0:
                            wallside = 1
                        else:
                            wallside = 2
                    extdigit = exteriorblock.walls[wallaxis]
                    if (extdigit/wallside)%2 != 1:
                        exteriorblock.walls[wallaxis] += wallside
        existingblock.walls = [0,0]

class Tower(object):
    '''A basic fortification.

    Used in the larger Fortress and Castle classes.
    Call create to generate the geometry.
    '''
    def entrance(self,pos,side,blocklist):
        x = pos[0]
        y = pos[1]
        z = pos[2]
        '''make the outside step'''
        step = DfBlockFloor()
        exterior_walls(x,y,z,blocklist)
        assign_dfblocks(x,y,z,step,blocklist)
        '''make the door'''
        if side == 0:
            x += -1
        if side == 1:
            z += -1
        exterior_walls(x,y,z,blocklist)
        step.material = self.primemat
        step.wallmat = self.primemat
        step.windowmat = self.doormat
        
        

    def place_entrance(self,blocklist,mcmap):
        '''find the best location, and return the position and side
        
        Only searches on the positive x and positive z sides.
        '''
        
        def place_on_x(y):
            '''only place doors in the center of the wall'''
            if self.size[2] > 2:
                offset = (self.size[2])/2
            else:
                offset = 1
            x = self.center[0] + (self.size[0] + 1)/2
            z = self.center[2] - self.size[2]/2 + offset
            '''find the distance thru the air here'''
            curcords = [i*3 + 1 for i in [x,y,z]]
            offset_thru_air = dist_to_mat(curcords,[0,-1,0],0,mcmap,True)
            if offset_thru_air > 0:
                self.entrance([x,y,z],0,blocklist)
                return True
            return False

        def place_on_z(y):
            '''only place doors off of corners in larger towers'''
            if self.size[0] > 2:
                offset = (self.size[0])/2
            else:
                offset = 0
            z = self.center[2] + (self.size[2] + 1)/2
            x = self.center[0] - self.size[0]/2 + offset
            '''find the distance thru the air here'''
            curcords = [i*3 + 1 for i in [x,y,z]]
            offset_thru_air = dist_to_mat(curcords,[0,-1,0],0,mcmap,True)
            if offset_thru_air > 0:
                self.entrance([x,y,z],1,blocklist)
                return True
            return False
        
        size = self.size
        for yoff in range(self.size[1]+1):
            y = self.center[1] + yoff
            if size[2] <= size[0]:
                made_entrance = place_on_z(y)
                if made_entrance:
                    return None
            elif size[2] > 1:
                made_entrance = place_on_x(y)
                if made_entrance:
                    return None
        
    
    def clearspace(self,blocklist):
        '''fill the space the fortress will need with air'''
        for xoff in range(self.size[0]):
            x = self.center[0] + xoff - self.size[0]/2
            for yoff in range(self.size[1]+1):
                y = self.center[1] + yoff
                for zoff in range(self.size[2]):
                    z = self.center[2] + zoff - self.size[2]/2
                    airblock = DfBlockSolid()
                    assign_dfblocks(x,y,z,airblock,blocklist)

    def stairwell(self,ybot,ytop,x,z,blocklist):
        '''edit blocklist in place to make a stairwell

        Center the stairwell at x and z.
        Start at ybot and go to ytop.
        '''
        if ytop - ybot < 1 : return None
        for i in range(ybot,ytop+1):
            if i == ybot:
                stair = DfBlockStairUp()
            elif i == ytop:
                stair = DfBlockStairDown()
            else:
                stair = DfBlockStairUpDown()
            if i%2 == 1:
                stair.flip = True
            stair.material = self.secondarymat
            exterior_walls(x,i,z,blocklist)
            "make the staircase"
            assign_dfblocks(x,i,z,stair,blocklist)

    def foundation(self,blocklist):
        for xoff in range(self.size[0]):
            for zoff in range(self.size[2]):
                foundationblock = DfBlockSolid()
                foundationblock.material = self.primemat
                x = self.center[0] + xoff - self.size[0]/2
                y = self.center[1] - 1
                z = self.center[2] + zoff - self.size[2]/2
                assign_dfblocks(x,y,z,foundationblock,blocklist)

    def floors(self,blocklist,mcmap):
        '''generate floors and walls for the tower'''
        for xoff in range(self.size[0]):
            x = self.center[0] + xoff - self.size[0]/2
            for zoff in range(self.size[2]):
                z = self.center[2] + zoff - self.size[2]/2
                for yoff in range(self.size[1]+1):
                    y = self.center[1] + yoff
                    floorblock = DfBlockFloor()
                    '''make walls on the outside'''
                    
                    '''alternate floors inside, for high ceilings'''
                    if yoff%2 == 1:
                        floorblock.material = 0
                    else:
                        floorblock.material = self.secondarymat
                    '''set the walls to the primary material'''
                    floorblock.wallmat = self.primemat
                    '''by default the walls are not 
                    shunted to the next exterior block'''
                    extflag = 0
                    '''if it is hollow, only make floors along the periphery'''
                    if self.hollow == True:
                        makeit = False
                    '''at the top, make overhung crennelations'''
                    if yoff == self.size[1]:
                        floorblock.material = self.secondarymat
                        floorblock.windowmat = 0
                        extflag = 1
                    '''at the bottom, always make the floor'''
                    if yoff == 0:
                        #floorblock.windowmat = self.primemat
                        makeit = True
                    '''start checking if there need to be walls on the block
                    make the walls along the edges'''
                    if xoff == 0:
                        floorblock.walls[0] += 1
                        makeit = True
                    if zoff == 0:
                        floorblock.walls[1] += 1
                        makeit = True
                    '''for these two, make walls, but also set the
                    windows to be doors if it is flush with another floor'''
                    if xoff == self.size[0] - 1:
                        floorblock.walls[0] += 2
                        try:
                            otherblock = blocklist[x+1][y][z]
                            if self.interior == True and (
                                    type(otherblock) == type(floorblock)
                                    ) and floorblock.material != 0:
                                floorblock.windowmat = INTDOORMAT
                        except IndexError:
                            "do nothing"
                        makeit = True
                    if zoff == self.size[2] - 1:
                        floorblock.walls[1] += 2
                        try:
                            otherblock = blocklist[x][y][z+1]
                            if self.interior == True and (
                                type(otherblock) == type(floorblock)
                                ) and floorblock.material != 0:
                                floorblock.windowmat = INTDOORMAT
                        except IndexError:
                            "do nothing"
                        makeit = True
                    '''if, indeed, the floor should be made(only
                    false if hollow == True)'''
                    if makeit == True:
                        '''if the ground is above the mid of this block,
                        close the windows'''
                        curcords = [i*3 + 1 for i in [x,y,z]]
                        offset_thru_air = dist_to_mat(curcords,[0,-1,0],
                                                      0,mcmap,True)
                        curcords[1] += -(offset_thru_air)
                        offset_thru_water = dist_to_mat(curcords,[0,-1,0],
                                                        9,mcmap,True)
                        offset_to_ground = offset_thru_air + offset_thru_water
                        if offset_to_ground < 1 and floorblock.windowmat == 20:
                            floorblock.windowmat = self.primemat
                        '''add the floorblock to the blocklist'''
                        val = assign_dfblocks(x,y,z,floorblock,blocklist)
                        if val != True:
                            continue
                        '''if the tower is small, make the walls exterior'''
                        if (self.size[0] < 2) or (self.size[2] < 2):
                            extflag += 1
                        '''if the exterior flag is set, shunt the walls to the
                        outside of the block'''
                        if extflag > 0:
                            exterior_walls(x,y,z,blocklist)
                            
                            blocklist[x][y][z].walls = [0,0]

    def create(self,blocklist,mcmap):
        '''alter blocklist in-place to generate the tower'''

        '''set minimum size'''
        for i in range(3):
            if self.size[i] < 1: self.size[i] = 1
        topy = self.size[1] + self.center[1]
        maptop = blocklist[-1][1]
        if topy >= maptop - 2:
            height = maptop - 2 - self.center[1]
            self.size[1] = height

        '''fill the area with air'''
        self.clearspace(blocklist)
        '''make the foundation and floors'''
        self.foundation(blocklist)
        self.floors(blocklist,mcmap)
        '''Create the stairwell(s)'''
        if self.makestairs == True:
            x = self.center[0] - self.size[0]/2
            ybot = self.center[1]
            ytop = self.center[1] + self.size[1]
            z = self.center[2] - self.size[2]/2
            self.stairwell(ybot,ytop,x,z,blocklist)
            '''if this is an exterior section, and the tower is large enough
            make the stairs in all four corners'''
            if self.interior == False and self.size[2] > 3 and self.size[0] > 3:
                x += self.size[0]-1
                self.stairwell(ybot,ytop,x,z,blocklist)
                x += -self.size[0]+1
                z += self.size[2]-1
                self.stairwell(ybot,ytop,x,z,blocklist)
                x += self.size[0]-1
                self.stairwell(ybot,ytop,x,z,blocklist)
        '''make the entrance'''
        if self.interior == False:
            self.place_entrance(blocklist,mcmap)
            
    def copy(self):
        newtower = Tower()
        newtower.primemat = self.primemat
        newtower.secondarymat = self.secondarymat
        newtower.doormat = self.doormat
        newtower.center = self.center
        newtower.size = self.size
        newtower.makestairs = self.makestairs
        newtower.hollow = self.hollow
        newtower.interior = self.interior
        return newtower
        
    def __init__(self):
        self.primemat = 0
        self.secondarymat = 0
        self.doormat = 0
        self.center = [0,0,0]
        self.size = [0,0,0]
        self.makestairs = True
        self.hollow = False
        self.interior = False

class Fortress(Tower):

    def entrance(self,pos,side,blocklist):
        x = pos[0]
        y = pos[1]
        z = pos[2]
        y += -2
        '''make the gatehouses only if the fortress is large enough'''
        if self.size[0] > 2 and self.size[2] > 2:
            gatehouse = Tower()
            gatehouse.size = [1,4,1]
            if self.size[1] > 2:
                add = self.size[1] - 2
                gatehouse.size[1] += add
            
            gatehouse.interior = True
            gatehouse.primemat = self.primemat
            gatehouse.secondarymat = self.secondarymat
            gatehouse.doormat = self.doormat
            mcmap = self.mainmap
            if side == 0:
                gatehouse.size[0] = 2
                z += 1
                gatehouse.center = [x,y,z]
                gatehouse.create(blocklist,mcmap)
                z += -2
                gatehouse.center = [x,y,z]
                gatehouse.create(blocklist,mcmap)
                print("madeonz")
                
            if side == 1:
                gatehouse.size[2] = 2
                x += 1
                gatehouse.center = [x,y,z]
                gatehouse.create(blocklist,mcmap)
                x += -2
                gatehouse.center = [x,y,z]
                gatehouse.create(blocklist,mcmap)
                print("madeonx")
            
        Tower.entrance(self,pos,side,blocklist)
                    
    def create(self,blocklist,mcmap):
        '''create a tower in the middle and walls all around'''
        
        '''set minimum size'''
        for i in range(3):
            if self.size[i] < 2: self.size[i] = 2            
        
        centerheight = self.size[1] + 2
        outerheight = int(self.size[1]*0.382)
        if outerheight > 3:
            outerheight = int(3 + (self.size[1] - 3*1.618)**0.383)
        self.size[1] = outerheight
        self.mainmap = mcmap
        Tower.create(self,blocklist,mcmap)
        centertower = Tower()
        centertower.interior = True
        center = [self.center[i] - self.size[i] / 2 for i in [0,1,2]]
        center[1] = self.center[1] - 2
        centertower.center = center
        avesize = int((self.size[0] + self.size[2])*0.382)
        if avesize < 2:
            if self.size[0] < 3 or self.size[2] < 3:
                avesize = 1
            else:
                avesize = 2
        if avesize > 5:
            avesize = 5
        size = [avesize,centerheight,avesize]
        centertower.size = size
        centertower.primemat = self.primemat
        centertower.secondarymat = self.secondarymat
        centertower.doormat = self.doormat
        centertower.create(blocklist,mcmap)
        if self.size[0] > 6 and self.size[2] > 6:
            cornertower = Tower()
            cornertower.interior = True
            corner = [self.center[i] + self.size[i] / 2 - 1 + (self.size[i]%2)
                      for i in [0,1,2]]
            corner[1] = self.center[1] - 2
            cornertower.center = corner
            cornertower.size = [3,centerheight-2,3]
            cornertower.primemat = self.primemat
            cornertower.secondarymat = self.secondarymat
            cornertower.doormat = self.doormat
            cornertower.create(blocklist,mcmap)
            othercenter = corner[:]
            othercenter[0] = self.center[0] - self.size[0] / 2
            cornertower.center = othercenter
            cornertower.create(blocklist,mcmap)
            othercenter = corner[:]
            othercenter[2] = self.center[2] - self.size[2] / 2
            cornertower.center = othercenter
            cornertower.create(blocklist,mcmap)
            if self.size[0] < 11 or self.size[2] < 11:
                return None
            if self.size[0] > 14 and self.size[2] > 14:
                cornertower.size = [3,centerheight-2,3]
            else:
                cornertower.size = [1,centerheight-2,1]
            othercenter = self.center[:]
            othercenter[1] = self.center[1] - 2
            othercenter[0] = self.center[0] - self.size[0] / 2
            cornertower.center = othercenter
            cornertower.create(blocklist,mcmap)
            othercenter = self.center[:]
            othercenter[1] = self.center[1] - 2
            othercenter[2] = self.center[2] - self.size[2] / 2
            cornertower.center = othercenter
            cornertower.create(blocklist,mcmap)
            othercenter = self.center[:]
            othercenter[1] = self.center[1] - 2
            if self.size[0] >= self.size[2]:
                othercenter[0] = (self.center[0] + self.size[0] / 2 
                                  - 1 + (self.size[0]%2))
            else:
                othercenter[2] = (self.center[2] + self.size[2] / 2 
                                  - 1 + (self.size[2]%2))
            cornertower.center = othercenter
            cornertower.create(blocklist,mcmap)
            
        
        

    def __init__(self):
        Tower.__init__(self)
        #self.makestairs = False
        self.hollow = True
    

def addfort():

    print("Importing map data")

    the_map = McLevel()
    the_map.import_map(LOADNAME)
    blocktypes = the_map.blocktypelist()
    mapsize = the_map.mapdims()

    dfblocklist = setup_dfblocks(mapsize)

    print("Placing the watchtowers")
    for i in range(WATCHTOWERCOUNT):
        outpost = Tower()
        outpost.primemat = PRIMEMAT
        outpost.secondarymat = SECMAT
        outpost.doormat = DOORMAT
        xsize = int(random()*2 + .5)
        zsize = int(random()*2 + .5)
        size = [xsize,1,zsize]
        location = rnd_surface_point(1,the_map)
        toploc = location[:]
        toploc[1] = location[1] + size[1]*3
        topidx = coord_to_idx(toploc,the_map)
        topmat = blocktypes[topidx]
        while ord(topmat) != 0:
            size[1] += 1
            toploc[1]+= 3
            topidx = coord_to_idx(toploc,the_map)
            topmat = blocktypes[topidx]

        size[1] += 2
        
        center = [i/3 for i in location]
        outpost.size = size
        outpost.center = center
        print("Outpost center and size ", center, size)
        outpost.create(dfblocklist,the_map)
    
    fort = Fortress()
    fort.primemat = PRIMEMAT
    fort.secondarymat = SECMAT
    fort.doormat = DOORMAT
    
    '''find the approximate highest point of solid stone'''
    print("Placing the fortress")
    if PLACEMENT == "auto":
        highspot = highestpoint(1,the_map)
        '''center it on the local ground'''
        curcent = highspot[:]
        for i in range(3):
            xplus = dist_to_mat(curcent,[1,0,0],0,the_map)/3
            xminus = dist_to_mat(curcent,[-1,0,0],0,the_map)/3
            zplus = dist_to_mat(curcent,[0,0,1],0,the_map)/3
            zminus = dist_to_mat(curcent,[0,0,-1],0,the_map)/3
            centx = curcent[0] + int(xplus*1.618 - xminus*1.618)
            print(xplus , xminus , zplus , zminus)
            centy = curcent[1]
            centz = curcent[2] + int(zplus*1.618 - zminus*1.618)
            curcent = [centx,centy,centz]
        disttodirt = dist_to_mat(curcent,[0,-1,0],3,the_map)
        if disttodirt <= 4:
            curcent[1] += -disttodirt
        else:
            curcent[1] += -4
        fort.center = [(x + 1)/3 for x in curcent]
    elif len(PLACEMENT) == 2:
        x = PLACEMENT[0]
        z = PLACEMENT[1]
        spot = search_column(x,z,1,the_map)
        curcent = [x,spot,z]
        fort.center = [(x + 1)/3 for x in curcent]
    elif len(PLACEMENT) == 3:
        curcent = PLACEMENT[:]
        fort.center = [(x + 1)/3 for x in curcent]
    else:
        print("PLACEMENT was not in the correct format")
        return None
        
    if FORTSIZE == "auto":
        if PLACEMENT != "auto":
            xplus = dist_to_mat(curcent,[1,0,0],0,the_map)/3
            xminus = dist_to_mat(curcent,[-1,0,0],0,the_map)/3
            zplus = dist_to_mat(curcent,[0,0,1],0,the_map)/3
            zminus = dist_to_mat(curcent,[0,0,-1],0,the_map)/3
            
        xslope = dist_to_mat(curcent,[3,-1,0],0,the_map)
        xslope += dist_to_mat(curcent,[-3,-1,0],0,the_map)
        zslope = dist_to_mat(curcent,[0,-1,3],0,the_map)
        zslope += dist_to_mat(curcent,[0,-1,-3],0,the_map)
        xsize = int((xplus + xminus)*0.618)
        zsize = int((zplus + zminus)*0.618)
        slopefactor = int((10* SLOPEMULTIPLYER - (xslope + zslope)))
        if slopefactor < 0: slopefactor = 0
        if slopefactor > 5: slopefactor = 5
        ysize = int((xsize + zsize)/2.618 + slopefactor)
        fort.size = [xsize,ysize,zsize]
    elif len(FORTSIZE) == 3:
        fort.size = FORTSIZE
    else:
        print("FORTSIZE was not in the correct format")
        return None
    
    maxdim = max(fort.size)
    pad = maxdim/2
    if not in_bounds(curcent,the_map,pad) and PLACEMENT == "auto":
        print("castle was too close to the edge, centering on the map")
        x = mapsize[0]/2
        z = mapsize[2]/2
        y = search_column(x,z,1,the_map)
        if y != None:
            curcent = [x,y,z]
            fort.center = [(x + 1)/3 for x in curcent]
        else:
            print("The center of the map had no stone for a foundation!  Fail!")
            return None
        
    print("Fort center and size ", curcent, fort.size)
    fort.create(dfblocklist,the_map)
    
    print("Generating the new map (takes a while)")
    minecraftblocks = ''
    i = 0
    for y in range(mapsize[1]):
        if y%4 == 0: print(".")
        for z in range(mapsize[2]):
            for x in range(mapsize[0]):
                thisblock = dfblocklist[x/3][y/3][z/3]
                if thisblock == None:
                    minecraftblocks += blocktypes[i]
                    i += 1
                else:
                    mat = thisblock.get_material(x%3,y%3,z%3)
                    if mat == None:
                        minecraftblocks += blocktypes[i]
                        i += 1
                        continue
                    minecraftblocks += chr(mat)
                    i += 1

#    minecraftdata = chr(15)*totalmcblocks

    print("Saving (takes a bit)")
    the_map.setblocktypes(minecraftblocks)
    the_map.export_map(SAVENAME)
    print("Finished!")

if __name__ == '__main__':
    addfort()

#make entrance on the exterior square that is open to the air.
