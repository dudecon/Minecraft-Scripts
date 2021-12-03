# Version 1.18
"""an interface module to allow read/write access to Minecraft save files
"""

# Read and write are implemented now.
# Works with the Minecraft 1.13 and later file format
# 
# Paul Spooner
# www.peripheralarbor.com

# Tell minecraft to re-calc the lighting when you change something
# True or False
RELIGHT = True

##############################################################
#  Don't edit below here unless you know what you are doing  #
##############################################################

import gzip
import time
import zlib
from struct import pack, unpack

COORD_MAP = {'x': 0, 'y': 1, 'z': 2}
ROT_MAP = {'yaw': 0, 'pitch': 1}


def raw_readout(raw_data, cap=144, start=0):
    """Print the raw data of the string, for debugging purposes.
    Includes line numbers, character print, and character value.
    raw_data : the string to read
    cap : the maximum number of characters to display, defaults to 144
    start : the starting offset, defaults to 0 (beginning)"""
    loc = 0
    for val in raw_data[start:start + cap]:
        print(str(loc + start) + " " + chr(val) + " " + str(val))
        loc += 1


class NbtTagBase(object):
    """This is the base tag, used as a base class for other tags."""
    # the number of bytes to read in for the payload
    payload_length = 0
    # used for decoding, this is the struct.unpack code
    payload_type = ''
    # used for encoding, this is the NBT tag id number, should be an int
    tag_type = 0

    def getName(self):
        """read in the name of the tag"""
        # get the byte code for the string length
        raw_length = self.data_ob.get_data(2)
        # decode the bytes into an integer, representing the length of the name
        name_length = unpack('>h', raw_length)[0]
        # retrieve the bytecode for the name
        name = self.data_ob.get_data(name_length)
        # decode into a string, and store
        self.name = str(name, 'utf_8')
        return

    def encodeName(self):
        """output the length and name, encoded in NBT format"""
        # get the encoded name
        raw_name = bytes(self.name, 'utf_8')
        # get the length of the name
        length = len(raw_name)
        # encode the length
        output = pack('>h', length)
        # encode the name
        output += raw_name
        return output

    def getPayload(self):
        """read in the payload of the tag."""
        # read in the number of bytes indicated in payload_length
        payload_raw = self.data_ob.get_data(self.payload_length)
        # decode the bytes assuming the payload_type format, store in payload
        self.payload = unpack(self.payload_type, payload_raw)[0]
        return

    def encodePayload(self):
        """output the payload, encoded in NBT format"""
        raw_payload = pack(self.payload_type, self.payload)
        return raw_payload

    def __init__(self, data_ob, named=True):
        """Read in the data for this tag.
        data_ob : the NbtData object which stores the methods
        to access the raw data. Strange, but it works.
        named : bool, if True this tag will import a name, otherwise not
        """
        # store the parent scheme thingy
        self.data_ob = data_ob
        # if this is a named tag, read in the name
        if named:
            self.getName()
            self.named = True
        # otherwise, set to an empty string
        else:
            self.name = ''
            self.named = False
        # read in the payload
        self.getPayload()

    def __str__(self):
        """Return a nice string representing the tag contents."""
        output = self.name + ": " + str(self.payload)
        return output

    def encode(self, tagged=True):
        """Return a byte string containing the encoded contents."""
        # initialize the byte string with the identifier byte
        if tagged:
            output = pack('>B', self.tag_type)
        else:
            # unless the tag isn't tagged (lists)
            output = b''
        # if the tag is named, output the name
        if self.named:
            output += self.encodeName()
        # finally, output the payload data
        output += self.encodePayload()
        return output


class NbtTag0(NbtTagBase):
    """TAG_End"""

    def __init__(self, data_ob, named=False):
        # store the parent scheme thingy
        self.data_ob = data_ob
        self.name = ''
        self.named = named
        self.payload = ''

    def encode(self, tagged=True):
        output = pack('>B', 0)
        return output


class NbtTag1(NbtTagBase):
    """TAG_Byte"""
    payload_length = 1
    payload_type = '>b'
    tag_type = 1


class NbtTag2(NbtTagBase):
    """TAG_Short"""
    payload_length = 2
    payload_type = '>h'
    tag_type = 2


class NbtTag3(NbtTagBase):
    """TAG_Int"""
    payload_length = 4
    payload_type = '>i'
    tag_type = 3


class NbtTag4(NbtTagBase):
    """TAG_Long"""
    payload_length = 8
    payload_type = '>q'
    tag_type = 4


class NbtTag5(NbtTagBase):
    """TAG_Float"""
    payload_length = 4
    payload_type = '>f'
    tag_type = 5


class NbtTag6(NbtTagBase):
    """TAG_Double"""
    payload_length = 8
    payload_type = '>d'
    tag_type = 6


class NbtTag7(NbtTagBase):
    """TAG_Byte_Array,
    also used as a base class for TAG_String and TAG_Int_Array"""
    tag_type = 7
    Element_Byte_Size = 1
    payload_type = '>B'

    def get_payload_length(self):
        """get the length of the payload data"""
        # the byte array length is four bytes long
        raw_payload_length = self.data_ob.get_data(4)
        # interpret as an unsigned int (why would length be negative?)
        self.payload_length = unpack('>I', raw_payload_length)[0] * self.Element_Byte_Size

    def encode_payload_length(self):
        """encode the payload length"""
        length = len(self.payload)  # *self.Element_Byte_Size
        raw_length = pack('>I', length)
        return raw_length

    def getPayload(self):
        """read in the payload of the byte array."""
        EBS = self.Element_Byte_Size
        # read in the raw data
        payload_raw = self.data_ob.get_data(self.payload_length)
        # this is a list which stores the payload as integers
        payload = []
        # because of the way that byte code works, Python automatically
        # converts individual bytes to integers.
        # we would store them, but instead we want to make this function
        # modular, so we skip by element byte size
        if len(payload_raw) % EBS != 0:
            # delete this whole check if we don't have problems
            print("array size failed to sync")
        for idx in range(len(payload_raw) // EBS):
            start = idx * EBS
            end = start + EBS
            this_piece = payload_raw[start:end]
            val = unpack(self.payload_type, this_piece)[0]
            payload += [val]
        self.payload = payload
        return

    def encodePayload(self):
        """output the payload, encoded in NBT format"""
        output = b''
        for val in self.payload:
            output += pack(self.payload_type, val)
        return output

    def __init__(self, data_ob, named=True):
        """initialize the byte array"""
        # this crazy thing again, see notes in NbtTagBase
        self.data_ob = data_ob
        if named:
            self.getName()
            self.named = True
        else:
            self.name = ''
            self.named = False
        # we must read in the length of the array first
        self.get_payload_length()
        # then read in the actual data
        self.getPayload()

    def __str__(self):
        """Return a nice string representing the tag byte array contents.
        If the array is longer than sixteen characters (and it often is)
        truncate the readout and indicate the total number of entries."""
        # map the payload to the local namespace
        payload = self.payload
        # initialize the output with the name of the tag
        output = self.name + ": "
        # if the array is too long, list how many entries there are total.
        payload_size = len(payload)
        if payload_size > 16:
            printed_size = 16
            appendix = '... total ' + str(payload_size) + ' entries'
        else:
            printed_size = payload_size
            appendix = ''
        # add the entries to the output string
        for c in range(printed_size):
            output += str(payload[c]) + ' '
        # add the appendix onto the end... where it belongs!
        output += appendix
        return output

    def encode(self, tagged=True):
        # initialize the byte string with the identifier byte
        if tagged:
            output = pack('>B', self.tag_type)
        # unless the tag isn't tagged (lists)
        else:
            output = b''
        if self.named:
            output += self.encodeName()
        output += self.encode_payload_length()
        output += self.encodePayload()
        return output


class NbtTag8(NbtTag7):
    """TAG_String"""
    tag_type = 8

    def get_payload_length(self):
        """get the length of the payload data"""
        # the string length is two bytes long
        raw_payload_length = self.data_ob.get_data(2)
        # interpret as an unsigned short (why would length be negative?)
        self.payload_length = unpack('>H', raw_payload_length)[0]
        return

    def encode_payload_length(self):
        """encode the payload length"""
        # calculate the raw payload length, since utf_8 characters
        # may not correspond 1 to 1 with byte characters
        raw_payload = bytes(self.payload, 'utf_8')
        # cache the raw bytes for use in encodePayload
        self.raw_payload = raw_payload
        # find the length
        length = len(raw_payload)
        # pack it up
        raw_length = pack('>H', length)
        return raw_length

    def getPayload(self):
        """read in the payload of the string tag."""
        # read in the string data
        payload_raw = self.data_ob.get_data(self.payload_length)
        # convert to string and store
        self.payload = str(payload_raw, 'utf_8')
        return

    def encodePayload(self):
        """output the payload, encoded in NBT format"""
        # since encode_payload_length() should have already been called
        # use the cached raw output
        return self.raw_payload

    def __str__(self):
        """Return a nice string representing the tag string contents."""
        # easy enough
        payload = self.payload
        # combine and we're done
        output = self.name + ": " + payload
        return output


class NbtTag9(NbtTagBase):
    """TAG_List, this tag can contain other tags!"""
    tag_type = 9

    # Aiugh! Nightmare! Actually, not so bad once it's working properly.
    def getPayload(self):
        """read in all sub-tags into a list"""
        # map the get_data method for easy access
        get_data = self.data_ob.get_data
        # get the type of tag stored in the list
        contents_type = get_data(1)[0]
        self.contents_type = contents_type
        # map the appropriate tag constructor
        sub_tag = tag_list[contents_type]
        # get the number of elements in the list
        contents_length = unpack('>I', get_data(4))[0]
        payload = []
        for c in range(contents_length):
            # import the tags
            new_tag = sub_tag(self.data_ob, named=False)
            payload += [new_tag]
        self.payload = payload

    def encodePayload(self):
        # first, encode the contents type
        output = pack('>B', self.contents_type)
        # then encode the number of elements
        output += pack('>I', len(self.payload))
        # now encode each sub-tag
        for c in self.payload:
            output += c.encode(tagged=False)
        return output

    def __str__(self):
        """make a string representation of the list"""
        # the starting line of the list
        output = self.name + ": List\n"
        # indent the string representation of sub-elements
        for tag in self.payload:
            this_str = tag.__str__()
            # split and indent each line, since results may have multiple lines
            str_list = this_str.splitlines()
            for idx in range(len(str_list)):
                str_list[idx] = '  ' + str_list[idx]
            str_result = '\n'.join(str_list) + '\n'
            output += str_result
        return output


class NbtTag10(NbtTagBase):
    """TAG_Compound, this tag can contain other tags also! The Horror!"""
    tag_type = 10

    # this one turned to be easier than the TAG_List
    def getPayload(self):
        """read in all sub-tags into a dict"""
        # map the get_data method for easy access
        get_data = self.data_ob.get_data
        # store tags keyed by name
        payload = {}
        # import the tags
        while True:
            # get the key value
            key = get_data(1)[0]
            # generate a new tag
            new_tag = tag_list[key](self.data_ob)
            # if the tag is TAG_End, we're done
            if isinstance(new_tag, NbtTag0): break
            # otherwise, store the new tag in the dictionary
            payload.update({new_tag.name: new_tag})
        # store the payload
        self.payload = payload

    def encodePayload(self):
        # initialize the output string
        output = b''
        # string together all the sub tags
        payload = self.payload
        for key in payload:
            tag = payload[key]
            output += tag.encode()
        # add the stop-byte at the end
        output += pack('>B', 0)
        return output

    def __str__(self):
        """make a string representation of the compound"""
        # the starting line of the list
        output = self.name + ": Compound\n"
        # get the string representations of the sub-tags
        for key in self.payload:
            # the key is the name of the tag, the tag is the object
            tag = self.payload[key]
            # get the string representation of the tag
            this_str = str(tag)
            # since results may have multiple lines,
            # split and indent each line.
            str_list = this_str.splitlines()
            for idx in range(len(str_list)):
                str_list[idx] = '  ' + str_list[idx]
            # join the resulting strings back together
            str_result = '\n'.join(str_list) + '\n'
            # add it to the output
            output += str_result
        # When all the strings are added together, return it
        return output


class NbtTag11(NbtTag7):
    """TAG_Int_Array"""
    tag_type = 11
    Element_Byte_Size = 4
    payload_type = '>i'


class NbtTag12(NbtTag7):
    """TAG_Long_Array"""
    tag_type = 12
    Element_Byte_Size = 8
    payload_type = '>q'


# switch list for selecting the correct tag
# keyed by integer
tag_list = [
    NbtTag0,
    NbtTag1,
    NbtTag2,
    NbtTag3,
    NbtTag4,
    NbtTag5,
    NbtTag6,
    NbtTag7,
    NbtTag8,
    NbtTag9,
    NbtTag10,
    NbtTag11,
    NbtTag12
]


class NbtData(object):
    """NbtData is designed to parse and store NBT format files."""

    # tags are individual objects, and may store other tag objects
    def get_data(self, length):
        """Extract and return the specified number of bytes from
        the raw data source.
        This behaves much like file.read() but, different?"""
        prev_loc = self.loc
        self.loc += length
        data = self.raw[prev_loc:self.loc]
        return data

    def __init__(self, source_data, current_location=0):
        """Read in and parse all the data.
        source_data : a byte string containing the raw NBT format data.
        current_location : an integer offset, in case you want to start
        in the middle of a file."""
        # the raw source
        self.raw = source_data
        # the current location in the file
        self.loc = current_location
        # the method for incrementally reading in data
        get_data = self.get_data
        # how much data do we have?
        raw_length = len(source_data)
        # a list to store the tags in.
        all_tags = []
        # keep reading in tags until you reach the end of the data
        while self.loc < raw_length:
            # what kind of tag is it?
            key = get_data(1)[0]
            # here is the new tag, all parsed and ready to go!
            new_tag = tag_list[key](self)
            # store the tag in the list
            all_tags += [new_tag]
        # store the list of tags internally
        self.tags = all_tags

    def __str__(self):
        """make a clean string representation of the NBT file contents"""
        # an empty string to start with
        output = ''
        # string all the output strings together
        for tag in self.tags:
            output += str(tag) + '\n'
        # and spit it out, easy as pie!
        return output

    def encode_data(self):
        output = b''
        for tag in self.tags:
            output += tag.encode()
        return output


class NbtNew(NbtData):
    """a dummy data ob for making new tags, so we can clobber them"""

    def get_data(self, length):
        nothing = pack('>B', 0)
        result = nothing * length
        return result

    def __init__(self):
        pass


class Region(object):
    """Parse a region file into usable containers."""
    # Python 3.2 supports gzip.decompress
    # compression_types = {1:gzip.decompress, 2:zlib.decompress}
    # Python 3.1 does not... so I have excluded it
    compression_types = {2: zlib.decompress}

    def get_chunk(self, num):
        """Return the parsed NBT file containing the chunk.
        Cache already extracted chunks for quick access."""
        # check if the chunk is cached.
        try:
            cached_chunk = self.cached_chunks[num]
            return cached_chunk
        except:
            pass
        # if it's not cached...
        # check to see if it is populated
        try:
            raw_offset = self.active_chunks_offsets[num]
        # if the chunk is not populated, return None
        except:
            return None
        # the offset is stored as the distance from the beginning of the file
        # subtract 2 to get from the beginning of raw_block
        offset = (raw_offset - 2) * (2 ** 12)
        # decode the length of the data
        length = unpack('>I', self.raw_block[offset:offset + 4])[0]
        # decode the compression type
        compression_type = unpack('>b', self.raw_block[offset + 4:offset + 5])[0]
        # get the compressed chunk data. Note it is one shorter than normal
        compressed_chunk = self.raw_block[offset + 5:offset + 4 + length]
        # find the appropriate decompress method
        decompressor = self.compression_types[compression_type]
        # decompress the data
        expanded_data = decompressor(compressed_chunk)
        # parse the data into an NbtData container
        this_nbt = NbtData(expanded_data)
        # cache and return the container
        self.cached_chunks.update({num: this_nbt})
        return this_nbt

    def encode_chunk(self, num):
        """save the specified chunk to the internal data,
        must be cached already."""
        # localize active_chunks_offsets and active_chunks_lengths
        offsets = self.active_chunks_offsets
        lengths = self.active_chunks_lengths
        # retrieve the chunk to save
        chunk = self.cached_chunks[num]
        # encode the chunk data in NBT byte format
        encoded_chunk = chunk.encode_data()
        # compress the data
        compressed_chunk = zlib.compress(encoded_chunk)
        # calculate the length of the compressed data,
        # plus the length bytes (4)
        # plus the encoding (1)
        data_length = len(compressed_chunk) + 5
        # calculate the new length in 4 kiB chunks
        # round up (floor division, then add 1)
        new_length = (data_length // (2 ** 12)) + 1
        # calculate how much to pad the data, to make it fit properly
        pad_length = (new_length * (2 ** 12)) - data_length
        padding_bytes = b'\x00' * pad_length
        # encode the length, subtract the four bytes for the length
        # that we added earlier
        length_bytes = pack('>I', (data_length - 4))
        # encode the compression byte, should be 2 to indicate zlib
        compression_id_byte = pack('>B', 2)
        # compile the whole block of data for insertion
        full_data_block = (length_bytes +
                           compression_id_byte +
                           compressed_chunk +
                           padding_bytes)
        # retrieve the offset distance
        offset = offsets[num]
        # retrieve the old length
        old_length = lengths[num]
        # find the difference between the old and new lengths
        length_difference = new_length - old_length
        # update the other file offsets to reflect the new block length
        if length_difference != 0:
            # update this internal length value
            lengths[num] = new_length
            # print('altering offsets for ',num ,' at ',offset,' delta length: ', length_difference)
            # print('new length', new_length)
            # go through the active chunks
            for key in offsets:
                # get this chunk's offset
                chunk_offset = offsets[key]
                # if it is later in the file, alter it
                if chunk_offset > offset:
                    # find the new offset
                    new_offset = chunk_offset + length_difference
                    # assign it
                    offsets[key] = new_offset
                    # print('chunk:', key, ' was offset ', chunk_offset, ' but is now at ', new_offset)
        # update the raw data block
        # map the block to a local
        raw = self.raw_block
        # the internal offset will be two less (missing headers)
        # and converted to 4 kiB
        start = (offset - 2) * (2 ** 12)
        end = (offset + old_length - 2) * (2 ** 12)
        # slice off the front
        front = raw[:start]
        # slice off the back
        back = raw[end:]
        # paste the new data together
        new_raw = front + full_data_block + back
        # map it back into the internal raw_block data
        self.raw_block = new_raw
        # map back the offsets and lengths too
        self.active_chunks_offsets = offsets
        self.active_chunks_lengths = lengths
        # Aaaaaand we're done.
        print('.', end='', flush=True)
        return

    def encode_locations(self):
        """Encode the chunk locations and offsets into self.raw_locations"""
        # localize active_chunks_offsets and active_chunks_lengths
        offsets = self.active_chunks_offsets
        lengths = self.active_chunks_lengths
        # generate a new raw_locations string
        new_locs = b''
        # initialize an empty data block, for insertion for non-existent chunks
        blank_chunk = pack('>I', 0)
        # generate new data for each chunk
        for idx in range(2 ** 10):
            # compile the new 4 byte chunk
            if idx in offsets:
                # only three bytes for the offset
                offset = pack('>I', offsets[idx])[1:]
                # and one byte for the length
                length = pack('>B', lengths[idx])
                this_chunk = offset + length
                new_locs += this_chunk
            else:
                new_locs += blank_chunk
        # store the data
        self.raw_locations = new_locs

    def encode_timestamps(self):
        """Encode the chunk changed timestamp with the current time."""
        # map the timestamp string
        timestamps = self.raw_timestamps
        # get the current timestamp
        timestamp = int(time.time())
        # pack it as a 4 byte int
        raw_timestamp = pack('>I', timestamp)
        # update all the cached chunks
        for idx in self.cached_chunks:
            start = idx * 4
            end = start + 4
            front = timestamps[:start]
            back = timestamps[end:]
            timestamps = front + raw_timestamp + back
        # re-store the timestamp list
        self.raw_timestamps = timestamps

    def __init__(self, file_path):
        """parse the region file"""
        # save the file path internally
        self.file_path = file_path
        # read in the file data, and close the file
        # don't catch an exception if it occurs!
        region_file = open(file_path, 'rb')
        region_locations = region_file.read(2 ** 12)
        region_timestamps = region_file.read(2 ** 12)
        region_chunks_raw = region_file.read()
        region_file.close()
        # active_chunks_offsets is a dict with:
        # index number : offset (in 4kiB chunks)
        active_chunks_offsets = {}
        # active_chunks_lengths is a dict with:
        # index number : length (in 4kiB chunks)
        active_chunks_lengths = {}
        # read in the offsets
        for num in range(2 ** 10):
            pos = num * 4
            data = region_locations[pos:pos + 4]
            # offset from the beginning of the file is 2 greater than
            # the offset from the beginning of the region_chunks_raw block
            offset = unpack('>I', b'\x00' + data[:3])[0]
            if offset > 0:
                active_chunks_offsets.update({num: offset})
                length = unpack('>B', data[3:])[0]
                active_chunks_lengths.update({num: length})
        # now we have a dict of all the active chunks.
        # save the raw data later, for writing out
        self.raw_locations = region_locations
        self.raw_timestamps = region_timestamps
        self.raw_block = region_chunks_raw
        # save the active chunks, these are important!
        self.active_chunks_offsets = active_chunks_offsets
        self.active_chunks_lengths = active_chunks_lengths
        # initialize a cached_chunks dict,
        # for when chunks are extracted from the raw_block
        self.cached_chunks = {}

    def write(self):
        """Save all cached chunks to the region file."""
        debug = self.file_path + " saving (dots are chunks)"
        print(debug)
        # map the cached chunk dictionary to the local namespace
        chunks = self.cached_chunks
        # print(len(chunks),chunks)
        # write out each of the chunks to internal data
        for key in chunks:
            self.encode_chunk(key)
        # write the offset data to internal data
        self.encode_locations()
        # write the current timestamp on all chunks changed to internal data
        self.encode_timestamps()
        # write the internal data to a file
        region_file = open(self.file_path, 'wb')
        region_file.write(self.raw_locations)
        region_file.write(self.raw_timestamps)
        region_file.write(self.raw_block)
        region_file.close()
        print(" completed")
        return True


class SaveFile(object):
    """Interface object for a minecraft save file.
    Methods:
    block(x,y,z): returns relevant block data. Accepts options.
    surface(x,z): returns the surface block data. Accepts options.
    Instance Variables:
    save_file: string with file name
    """

    # the top height of the map
    # note that the user-facing y height is this -65 since the height now goes down to -64
    # all the map data and scripts use y starting at 0
    map_height: int = 384

    def __init__(self, foldername):
        """Initialize and read in basic file data."""
        # The file name is the save file that this object is pointed to.
        self.save_folder = foldername
        # the region objects are stored in a dict by filename.
        self.regions = {}
        # import the dat file
        self.dat = None
        self.read_dat()
        self.lock = None
        self.write_lock()

    def block_to_idx(self, blk_x, blk_y, blk_z):
        """Convert absolute block cords to an intra-section index."""
        if blk_y > self.map_height or blk_y < 0:
            raise IndexError
        idx = (blk_y % 16) * 16 * 16 + (blk_z % 16) * 16 + (blk_x % 16)
        return idx

    def get_region(self, reg_x, reg_z):
        """Return a Region object.
        If the region is loaded, get the object from the cache.
        Otherwise, load the data and cache it."""
        # map self.regions
        regions = self.regions
        # derive the appropriate file name
        file_name = 'r.' + str(reg_x) + '.' + str(reg_z) + '.mca'
        if file_name in regions:
            return regions[file_name]
        else:
            # compose the path to the file
            file_path = self.save_folder + '/region/' + file_name
            try:
                new_region = Region(file_path)
            except IOError:
                new_region = None
            self.regions.update({file_name: new_region})
            return new_region

    @staticmethod
    def block_to_chunk(blk_x, blk_z):
        """Convert block to chunk coordinates, return tuple."""
        chunk_x = blk_x // 16
        chunk_z = blk_z // 16
        return chunk_x, chunk_z

    @staticmethod
    def chunk_to_region(chk_x, chk_z):
        """Convert chunk to region coordinates, return tuple."""
        reg_x = chk_x // 32
        reg_z = chk_z // 32
        return reg_x, reg_z

    @staticmethod
    def chunk_to_num(chk_x, chk_z):
        """Convert chunk coordinates to an intra-region index."""
        num = (chk_x % 32) + (chk_z % 32) * 32
        return num

    def get_chunk(self, chk_x, chk_z):
        """Return the chunk at the chunk coordinates (x,z).
        If the chunk is not present int the save file, return None."""
        # find the region the chunk is stored in, and retrieve it.
        reg_x, reg_z = self.chunk_to_region(chk_x, chk_z)
        reg = self.get_region(reg_x, reg_z)
        # check to see if the region actually exists.
        # if it doesn't return None
        if reg is None:
            return None
        # calculate the chunk numeric index
        chunk_idx = self.chunk_to_num(chk_x, chk_z)
        # retrieve the chunk from the region
        # if it isn't in the region, this "chunk" will be None
        chunk = reg.get_chunk(chunk_idx)
        return chunk

    def get_chunk_from_cord(self, blk_x, blk_z):
        """Return the chunk containing the block coordinates (x,z)."""
        chu_x, chu_z = self.block_to_chunk(blk_x, blk_z)
        chunk = self.get_chunk(chu_x, chu_z)
        return chunk

    @staticmethod
    def get_half_byte_data(data_list, idx):
        """Take a list and return data at idx/2.
        Assume the list is a list of integers derived from bytes.
        The value you are looking for is in nibbles.
        Go go go!"""
        # the raw value has twice as much information as you want
        raw_value = data_list[idx // 2]
        # If idx is even, the data lies at the top (msb)
        if idx % 2 == 1:
            value = raw_value // 16
        # If idx is odd, the data lies at the bottom (lsb)
        else:
            value = raw_value % 16
        # that's it, value extracted, mission completed!
        return value

    def block(self, blk_x, blk_y, blk_z, options=''):
        """Return relevant block data in a dict.
        The keys to the dict are the option key characters.
        If no options are selected, return the block id as a raw int
        because why do we need all this noise about block dictionaries?
        x, y, z : coordinates of target block.
        options : string containing option key characters (below) in any order.
        'B' = Blocks, the integer identifier of the block type.
        'D' = Data, the integer block data value.
        'S' = SkyLight, the amount of light from the sky hitting the block.
        'L' = BlockLight, the amount of light from other blocks.
        """
        # get the chunk
        chunk = self.get_chunk_from_cord(blk_x, blk_z)
        # if the chunk doesn't exist, return None
        if chunk is None:
            return None
        # get the intra-section index
        idx = self.block_to_idx(blk_x, blk_y, blk_z)
        # map the dict storing the relevant tag data
        data_dict = chunk.tags[0].payload["Level"].payload
        # map the method to retrieve half-bytes
        get_half_byte_data = self.get_half_byte_data
        if len(options) > 0: output = {}
        section = None
        secidx = blk_y // 16
        for sec in data_dict['Sections'].payload:
            if sec.payload['Y'].payload == secidx:
                section = sec.payload
        # add the block type to the output
        if ('B' in options) or (len(options) == 0):
            # Get the appropriate list
            # get the section index
            if section is None:
                value = 0
            else:
                data_list = section['Blocks'].payload
                # extract the value
                value = data_list[idx]
            if len(options) == 0: return value
            # add it to the output
            output['B'] = value
        # same as above, but with half bytes
        if 'D' in options:
            if section is None:
                value = 0
            else:
                data_list = section['Data'].payload
                value = get_half_byte_data(data_list, idx)
            output.update({'D': value})
        if 'S' in options:
            if section is None:
                value = 0
            else:
                data_list = section['SkyLight'].payload
                value = get_half_byte_data(data_list, idx)
            output.update({'S': value})
        if 'L' in options:
            if section is None:
                value = 0
            else:
                data_list = section['BlockLight'].payload
                value = get_half_byte_data(data_list, idx)
            output.update({'L': value})

        # spit it out
        return output

    def get_heightmap(self, blk_x, blk_z):
        """Return the y value of the heightmap at coordinates x, z."""
        # get the chunk
        chunk = self.get_chunk_from_cord(blk_x, blk_z)
        # if the chunk doesn't exist, return None
        if chunk is None:
            return None
        # map the list storing the height map
        data_list = chunk.tags[0].payload["Heightmaps"].payload['WORLD_SURFACE'].payload
        # find the location index, based on the coordinates
        # note the reversed coordinate ordering
        offset = (blk_x % 16) + (blk_z % 16) * 16
        pld_idx = offset // 7
        bin_str = bin(data_list[pld_idx])[2:]
        bin_idx = offset % 7
        if bin_idx == 0:
            start = '-9'
            end = ''
        elif bin_idx == 6:
            start = ''
            end = '-54'
        else:
            start = str((bin_idx + 1) * -9)
            end = str(bin_idx * -9)
        # the data value stores the highest non-air block
        y_ht = int(eval(f'bin_str[{start}:{end}]'), base=2)
        return y_ht

    def get_map_data(self):
        """returns a dictionary which is the mutable map data. Change and save to update."""
        map_payload = self.dat.tags[0].payload['Data'].payload
        # print(map_payload)
        return map_payload

    def get_player(self):
        """returns a dictionary which is the mutable player data. Change and save to update."""
        player_payload = self.get_map_data()['Player'].payload
        # print(player_payload)
        return player_payload

    def get_player_pos(self):
        pos_data = self.get_player()['Pos'].payload
        pos = [pos_data[i].payload for i in range(3)]
        return pos

    def set_player_pos(self, pos):
        pos_data = self.get_player()['Pos'].payload
        for k in COORD_MAP:
            if k in pos:
                pos_data[COORD_MAP[k]].payload = pos[k]

    def get_player_rot(self):
        """Rotation is [yaw(-180:180), pitch(-90:90)]
        yaw is 0 pointing in +z
        yaw is 90 pointing in -x
        yaw is 180 pointing in -z
        yaw is -90 pointing in +x
        pitch is -90 pointing up
        pitch is 0 pointing horizontal
        pitch is 90 pointing down
        """
        rot_data = self.get_player()['Rotation'].payload
        rot = [rot_data[i].payload for i in range(2)]
        return rot

    def set_player_rot(self, rot):
        rot_data = self.get_player()['Rotation'].payload
        for k in ROT_MAP:
            if k in rot:
                rot_data[ROT_MAP[k]].payload = rot[k]

    def set_heightmap(self, blk_x, blk_y, blk_z):
        """Set the x, z value in the heightmap to y"""
        # get the chunk
        chunk = self.get_chunk_from_cord(blk_x, blk_z)
        # if the chunk doesn't exist, return None
        if chunk is None:
            return None
        # map the list storing the height map
        data_list = chunk.tags[0].payload["Level"].payload['HeightMap'].payload
        # find the location index, based on the coordinates
        # note the reversed coordinate ordering
        idx = (blk_x % 16) + (blk_z % 16) * 16
        # the data value stores the lowest block where light is at full strength
        data_list[idx] = blk_y
        return True

    @staticmethod
    def set_half_byte_data(data_list, idx, value):
        """Take a list and set the data at idx/2.
        Assume the list is a list of integers derived from bytes.
        The value you are looking for is in nibbles.
        Go go go!"""
        # the raw value has twice as much information as you want
        raw_value = data_list[idx // 2]
        # If idx is even, the data lies at the top (msb)
        if idx % 2 == 1:
            encoded_value = value << 4
            other_value = raw_value % 16
            new_value = encoded_value + other_value
        # If idx is odd, the data lies at the bottom (lsb)
        else:
            other_value = (raw_value >> 4) << 4
            new_value = value + other_value
        # set the data to the new value
        data_list[idx // 2] = new_value
        # do we need to return the new data list?
        # I think not!

    @staticmethod
    def new_section(secidx):
        """generates a section that is all air"""
        # generate a new section
        newsec = NbtTag10(NbtNew())
        newsec.named = False
        gen_air_names = {'Blocks': 4096, 'Data': 2048, 'BlockLight': 2048, 'SkyLight': 2048}
        newY_tag = NbtTag1(NbtNew())
        newY_tag.name = 'Y'
        newY_tag.payload = secidx
        newsec.payload['Y'] = newY_tag
        for new_name in gen_air_names:
            new_tag = NbtTag7(NbtNew())
            new_tag.name = new_name
            new_tag.payload = [0] * gen_air_names[new_name]
            new_tag.payload_length = gen_air_names[new_name]
            newsec.payload[new_name] = new_tag
        return newsec

    def set_block(self, blk_x, blk_y, blk_z, settings):
        """Set the block data to settings.
        x, y, z : coordinates of target block
        settings : dict of data to set, keys are the
        same as in retrieve_block_data, values are the value to set.
        """
        # get the chunk
        chunk = self.get_chunk_from_cord(blk_x, blk_z)
        # if the chunk doesn't exist, return False
        if chunk is None:
            return None
        # get the intra-chunk index
        idx = self.block_to_idx(blk_x, blk_y, blk_z)
        # set the data
        # map the dict storing the relevant tag data
        data_dict = chunk.tags[0].payload["Level"].payload
        # map the method to retrieve half-bytes
        set_half_byte_data = self.set_half_byte_data
        # make a default writer for non-block data.
        # use set_half_byte_data(data_list, idx, value)
        # make a writer for block data.
        # just assign at the index on the appropriate list
        # do an if-then to execute the changes
        section = None
        secidx = blk_y // 16
        for sec in data_dict['Sections'].payload:
            if sec.payload['Y'].payload == secidx:
                section = sec.payload
        if section is None:
            sectionTag = self.new_section(secidx)
            data_dict['Sections'].payload.append(sectionTag)
            section = sectionTag.payload
        # change the block type data
        if 'B' in settings:
            # Get the appropriate list
            data_list = section['Blocks'].payload
            # set the value
            data_list[idx] = settings['B']
        # same as above, but with half bytes
        if 'D' in settings:
            data_list = section['Data'].payload
            set_half_byte_data(data_list, idx, settings['D'])
        if 'S' in settings:
            data_list = section['SkyLight'].payload
            set_half_byte_data(data_list, idx, settings['S'])
        if 'L' in settings:
            data_list = section['BlockLight'].payload
            set_half_byte_data(data_list, idx, settings['L'])
        # and we're done
        cur_max_y = self.get_heightmap(blk_x, blk_z)
        # this block is higher than the current limit, and isn't air
        cur_blk_type = self.block(blk_x, blk_y, blk_z)
        if (blk_y > cur_max_y) and (cur_blk_type != 0):
            self.set_heightmap(blk_x, blk_y, blk_z)
            # print(f"updated heightmap at {blk_x}, {blk_z} from {cur_max_y} to {blk_y}")
        elif (blk_y == cur_max_y) and (cur_blk_type == 0):
            check_y = blk_y
            while check_y > 0:
                check_y -= 1
                check_type = self.block(blk_x, check_y, blk_z)
                if check_type != 0: break
            self.set_heightmap(blk_x, check_y, blk_z)
        if RELIGHT:
            # Dirty the lighting, because it's easier to have Minecraft do it
            chunk.tags[0].payload["Level"].payload['LightPopulated'].payload = 0
        return True

    def surface_block(self, blk_x, blk_z, options='B'):
        """Return a dict of the highest block at the x, z cords.
        Similar to block() but finds the highest block in the column.
        x, z : coordinates of target column
        options : same as for retrieve_block_data()
        Except! Add the y value to the dict, under the key 'y'
        """
        # get the y coordinate of the heightmap
        # this should be the block above the surface of the map
        y_ht = self.get_heightmap(blk_x, blk_z)
        # if the chunk containing the x, z cords has not been generated
        # then return None
        if y_ht is None:
            return None
        # if you got a good value, subtract one to get the surface block
        y_ht += -1
        if y_ht == -1: y_ht = 0
        # get the block data
        output = self.block(blk_x, y_ht, blk_z, options)
        # add the y value, so we have it later if we want.
        output.update({'y': y_ht})
        # spit it out
        return output

    def read_dat(self):
        """Read in the dat file.

        Called on initialization, access the nbt wrapper object from
        self.dat
        Call read_dat again if you need to re-read the dat file from
        the hard drive."""
        # the location of the level.dat file
        dat_file_path = self.save_folder + "/" + "level.dat"
        # open the file
        dat_file = gzip.open(dat_file_path)
        # read in all the contents
        dat_data = dat_file.read()
        # close the file
        dat_file.close()
        # print the raw file contents, this is a byte string
        # print(dat_data)
        # do a readout of the file contents,
        # with character index, appearance, and character values
        # raw_readout(dat_data)
        # parse the data into an NbtData container
        this_data = NbtData(dat_data)
        # print out the tags for debug. This should give a readable result.
        # print(this_data)
        # store the container with the parsed data.
        # The raw data can be reached by self.dat.raw
        self.dat = this_data
        return this_data

    def write_dat(self):
        """Write out self.dat to the hard drive"""
        # the location of the level.dat file
        dat_file_path = self.save_folder + "/" + "level.dat"
        # get the output string
        output = self.dat.encode_data()
        # raw_readout(output)
        # raw_readout(self.dat.raw)
        # open the file
        dat_file = gzip.open(dat_file_path, 'w')
        # write the data
        dat_file.write(output)
        # close the file
        dat_file.close()

    def read_lock(self):
        """Read in the lock file"""
        # the location of the lock file
        lock_file_path = self.save_folder + "/" + "session.lock"
        lock_file = open(lock_file_path, 'rb')
        raw_lock = lock_file.read()
        lock_file.close()
        lock_time = unpack('>q', raw_lock)[0]
        return lock_time

    def write_lock(self):
        """write the lock file"""
        # the location of the lock file
        lock_file_path = self.save_folder + "/" + "session.lock"
        current_time = int(time.time() * 1000)
        raw_time = pack('>q', current_time)
        lock_file = open(lock_file_path, 'wb')
        lock_file.write(raw_time)
        lock_file.close()
        self.lock = current_time

    def check_lock(self):
        """check to see if the lock has updated since we wrote it, if it has,
        return True, otherwise return False."""
        prev_lock = self.lock
        current_lock = self.read_lock()
        if current_lock > prev_lock:
            return True
        else:
            return False

    def write_blocks(self):
        """Save the block data to the regions.
        Only saves chunks that have been cached, since if it
        hasn't been loaded, it's not likely that it was changed."""
        regions = self.regions
        for region_name in regions:
            region = regions[region_name]
            if region is None: continue
            region.write()
        return True

    def write(self):
        """Save all data to the hard drive, return True if successful."""
        # check the lock, if it has been updated since we started, abort.
        if self.check_lock(): return False
        # write out the dat file
        self.write_dat()
        # again, check the lock
        if self.check_lock(): return False
        # write out the blocks
        self.write_blocks()
        return True


# some test functions
savefile_to_load = "Test"
mc_level = SaveFile(savefile_to_load)
# print the dat file
# print(mc_level.dat)
# change the spawn location
## mc_level.dat.tags[0].payload['Data'].payload['SpawnX'].payload = -250
## mc_level.dat.tags[0].payload['Data'].payload['SpawnY'].payload = 70
## mc_level.dat.tags[0].payload['Data'].payload['SpawnZ'].payload = 142
## mc_level.write_dat()


x = 84
y = 319+65
z = -35

# print(f'chunk at {x}, {z}')
# print(mc_level.get_chunk_from_cord(x, z))
print('heightmap ', mc_level.get_heightmap(x, z))
print(f'y val {y} and block value', mc_level.block(x, y, z), "which should be leaves")

# for i in mc_level.get_chunk_from_cord(x, z).tags[0].payload["Level"].payload: print(i)
# sects = mc_level.get_chunk_from_cord(x, z).tags[0].payload["Level"].payload['Sections']

# mc_level.set_block(x, y, z, {'B':17, 'D':1})
# print('y is', y, 'and block value', mc_level.block(x, y, z))

# for y in range(0,80):
##    ##y = mc_level.retrieve_heightmap(x, z)
#    mc_level.set_block(x, y, z, {'B':20})


# savefile_to_load = "Test"
# mc_level = SaveFile(savefile_to_load)
# # Set the player Y height position
# mc_level.set_player_pos({'y': 91.1})
# mc_level.set_player_rot({'pitch': 12.1, 'yaw': -110.3})
#
# # save the file
# print("saving")
# mc_level.write()


# To Do
# Support the "Add" array for extended block types
