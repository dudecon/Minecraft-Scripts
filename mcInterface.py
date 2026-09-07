# Version 1.20
"""an interface module to allow read/write access to Minecraft save files
"""

# Read and write are implemented now.
# Works with Minecraft 1.13 and later, including the 26.1+ save layout
# (players/data, dimensions/minecraft/<dim>/region)
# Block entities (chests and other tile NBT) can be read and written.
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
import os
import time
import zlib
from struct import pack, unpack

COORD_MAP = {'x': 0, 'y': 1, 'z': 2}
ROT_MAP = {'yaw': 0, 'pitch': 1}


def uuid_from_int_array(int_array):
    """Convert a Minecraft UUID int array into a dashed UUID string."""
    parts = [i & 0xFFFFFFFF for i in int_array]
    return '{:08x}-{:04x}-{:04x}-{:04x}-{:012x}'.format(
        parts[0],
        (parts[1] >> 16) & 0xFFFF,
        parts[1] & 0xFFFF,
        (parts[2] >> 16) & 0xFFFF,
        ((parts[2] & 0xFFFF) << 32) | parts[3]
    )


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
        length = len(self.payload) # * self.Element_Byte_Size
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
        # We must encode the payload first
        # because the payload length may change during encoding
        # for example, when encoding the block position array
        temp_payload_output = self.encodePayload()
        output += self.encode_payload_length()
        output += temp_payload_output
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
        # find the length
        length = len(self.raw_payload)
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
        # calculate the raw payload length, since utf_8 characters
        # may not correspond 1 to 1 with byte characters
        raw_payload = bytes(self.payload, 'utf_8')
        # cache the raw bytes for use in encodePayload
        self.raw_payload = raw_payload
        return raw_payload

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
    payload_type = '>Q'

    def encodePayload(self):
        # check if this is a dirty block data array
        if hasattr(self, "unpacked"):
            # re-pack the integers
            bit_length = max(len(bin(len(self.palette)-1))-2,4)
            stride = (64 - (64 % bit_length))
            ids_per_int = 64 // bit_length

            # Collect binary representations of indices
            binary_chunks = [format(index, f'0{bit_length}b') for index in self.unpacked]

            # Reverse the order within each 64-bit chunk and concatenate
            binary_string = ''.join(
                ''.join(reversed(binary_chunks[i:i + ids_per_int]))
                for i in range(0, len(binary_chunks), ids_per_int)
            )

            # Convert to 64-bit integers
            self.payload = [int(binary_string[i:i + stride], 2) for i in range(0, len(binary_string), stride)]

        return NbtTag7.encodePayload(self)


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


# 21w43a / 1.18: TileEntities renamed to block_entities
DATAVERSION_BLOCK_ENTITIES = 2844
# 1.20.5: item Count/tag became count/components
DATAVERSION_ITEM_COMPONENTS = 3837


def namespaced_id(name):
    """Return a namespaced id, defaulting to minecraft:"""
    if name is None or name == '':
        return name
    name = str(name)
    if ':' in name:
        return name
    return 'minecraft:' + name


def new_tag(tag_type, name='', payload=None, named=None, contents_type=None):
    """Create a new NBT tag.
    tag_type : integer NBT id (1-12)
    name : tag name; empty for unnamed list entries
    payload : native python value for this tag
    named : whether the tag encodes a name; defaults to True when name is set
    contents_type : for TAG_List, the contained tag id
    """
    tag = tag_list[tag_type](NbtNew(), named=False)
    if named is None:
        named = name != ''
    tag.name = name
    tag.named = named
    if payload is not None:
        tag.payload = payload
    if tag_type == 9:
        if contents_type is not None:
            tag.contents_type = contents_type
        elif tag.payload:
            tag.contents_type = tag.payload[0].tag_type
    return tag


def nbt_to_python(tag):
    """Unwrap an NBT tag into plain python (dicts, lists, and primitives)."""
    if tag is None:
        return None
    if isinstance(tag, NbtTag10):
        return {k: nbt_to_python(v) for k, v in tag.payload.items()}
    if isinstance(tag, NbtTag9):
        return [nbt_to_python(v) for v in tag.payload]
    if isinstance(tag, NbtTagBase):
        return tag.payload
    return tag


def infer_tag_type(value):
    """Guess an NBT tag id from a python value."""
    if isinstance(value, NbtTagBase):
        return value.tag_type
    if isinstance(value, bool):
        return 1
    if isinstance(value, int):
        if value > 2147483647 or value < -2147483648:
            return 4
        return 3
    if isinstance(value, float):
        return 6
    if isinstance(value, str):
        return 8
    if isinstance(value, dict):
        return 10
    if isinstance(value, (list, tuple)):
        return 9
    if isinstance(value, (bytes, bytearray)):
        return 7
    raise TypeError('Cannot infer NBT type for %r' % (type(value),))


def python_to_nbt(value, name='', named=True, tag_type=None, contents_type=None):
    """Build an NBT tag from a python value.
    dict -> TAG_Compound, list -> TAG_List (or array if tag_type is 7/11/12),
    str -> TAG_String, bool -> TAG_Byte, int -> TAG_Int (or TAG_Long if huge),
    float -> TAG_Double. Pass an existing NBT tag to use it as-is.
    """
    if isinstance(value, NbtTagBase):
        value.name = name
        value.named = named
        return value
    if tag_type is None:
        tag_type = infer_tag_type(value)
    if tag_type == 10:
        payload = {}
        for k, v in value.items():
            payload[k] = python_to_nbt(v, name=k, named=True)
        return new_tag(10, name, payload, named)
    if tag_type == 9:
        items = []
        inferred_ct = contents_type
        for v in value:
            child = python_to_nbt(v, name='', named=False)
            items.append(child)
            if inferred_ct is None:
                inferred_ct = child.tag_type
        if inferred_ct is None:
            inferred_ct = 0
        return new_tag(9, name, items, named, contents_type=inferred_ct)
    if tag_type in (7, 11, 12):
        return new_tag(tag_type, name, list(value), named)
    if tag_type == 8:
        return new_tag(8, name, str(value), named)
    if tag_type in (1, 2, 3, 4) and not isinstance(value, bool):
        return new_tag(tag_type, name, int(value), named)
    if tag_type in (5, 6):
        return new_tag(tag_type, name, float(value), named)
    if tag_type == 1 and isinstance(value, bool):
        return new_tag(1, name, 1 if value else 0, named)
    return new_tag(tag_type, name, value, named)


# block name (no namespace) -> block entity id (no namespace)
# None means the block is not a block entity
BLOCK_TO_ENTITY = {
    'chest': 'chest',
    'trapped_chest': 'trapped_chest',
    'barrel': 'barrel',
    'hopper': 'hopper',
    'dispenser': 'dispenser',
    'dropper': 'dropper',
    'furnace': 'furnace',
    'blast_furnace': 'blast_furnace',
    'smoker': 'smoker',
    'brewing_stand': 'brewing_stand',
    'campfire': 'campfire',
    'soul_campfire': 'soul_campfire',
    'chiseled_bookshelf': 'chiseled_bookshelf',
    'crafter': 'crafter',
    'decorated_pot': 'decorated_pot',
    'jukebox': 'jukebox',
    'lectern': 'lectern',
    'beacon': 'beacon',
    'spawner': 'mob_spawner',
    'trial_spawner': 'trial_spawner',
    'vault': 'vault',
    'bee_nest': 'beehive',
    'beehive': 'beehive',
    'enchanting_table': 'enchanting_table',
    'end_gateway': 'end_gateway',
    'end_portal': 'end_portal',
    'ender_chest': 'ender_chest',
    'command_block': 'command_block',
    'chain_command_block': 'command_block',
    'repeating_command_block': 'command_block',
    'structure_block': 'structure_block',
    'jigsaw': 'jigsaw',
    'daylight_detector': 'daylight_detector',
    'comparator': 'comparator',
    'sculk_sensor': 'sculk_sensor',
    'calibrated_sculk_sensor': 'calibrated_sculk_sensor',
    'sculk_catalyst': 'sculk_catalyst',
    'sculk_shrieker': 'sculk_shrieker',
    'bell': 'bell',
    'conduit': 'conduit',
    'suspicious_sand': 'brushable_block',
    'suspicious_gravel': 'brushable_block',
    'creaking_heart': 'creaking_heart',
    'moving_piston': 'piston',
    'test_block': 'test_block',
    'test_instance_block': 'test_instance_block',
    'shelf': 'shelf',
    'copper_golem_statue': 'copper_golem_statue',
    'copper_chest': 'chest',
    'shulker_box': 'shulker_box',
}

CONTAINER_ENTITY_IDS = {
    'minecraft:chest',
    'minecraft:trapped_chest',
    'minecraft:barrel',
    'minecraft:shulker_box',
    'minecraft:hopper',
    'minecraft:dispenser',
    'minecraft:dropper',
    'minecraft:furnace',
    'minecraft:blast_furnace',
    'minecraft:smoker',
    'minecraft:brewing_stand',
    'minecraft:campfire',
    'minecraft:soul_campfire',
    'minecraft:chiseled_bookshelf',
    'minecraft:crafter',
}

# well-known block-entity field types (used when building NBT from python)
BLOCK_ENTITY_FIELD_TYPES = {
    'id': 8, 'x': 3, 'y': 3, 'z': 3, 'keepPacked': 1,
    'LootTable': 8, 'LootTableSeed': 4,
    'Command': 8, 'LastOutput': 8, 'auto': 1, 'powered': 1,
    'conditionMet': 1, 'TrackOutput': 1, 'SuccessCount': 3,
    'UpdateLastExecution': 1, 'LastExecution': 4,
    'Delay': 2, 'MaxNearbyEntities': 2, 'RequiredPlayerRange': 2,
    'SpawnCount': 2, 'MaxSpawnDelay': 2, 'MinSpawnDelay': 2, 'SpawnRange': 2,
    'primary_effect': 8, 'secondary_effect': 8,
    'is_waxed': 1, 'TransferCooldown': 3, 'OutputSignal': 3, 'Page': 3,
    'lit_time_remaining': 2, 'cooking_time_spent': 2,
    'cooking_total_time': 2, 'lit_total_time': 2,
    'BrewTime': 2, 'Fuel': 1,
    'flower_pos': 11, 'exit_portal': 11, 'Target': 11,
    'CookingTimes': 11, 'CookingTotalTimes': 11, 'disabled_slots': 11,
    'creaking': 11, 'last_interacted_slot': 3,
    'ExactTeleport': 1, 'Age': 4,
}


def block_entity_id_for_block(block_name):
    """Return the namespaced block-entity id for a block, or None."""
    if not block_name:
        return None
    name = str(block_name).split(':')[-1]
    if name in BLOCK_TO_ENTITY:
        eid = BLOCK_TO_ENTITY[name]
        if eid is None:
            return None
        return 'minecraft:' + eid
    if name.endswith('_shulker_box'):
        return 'minecraft:shulker_box'
    if name.endswith('_hanging_sign'):
        return 'minecraft:hanging_sign'
    if name.endswith('_sign'):
        return 'minecraft:sign'
    if name.endswith('_banner'):
        return 'minecraft:banner'
    if name.endswith('_skull') or name.endswith('_head'):
        return 'minecraft:skull'
    if name.endswith('_copper_chest'):
        return 'minecraft:chest'
    if name.endswith('_shelf'):
        return 'minecraft:shelf'
    if 'copper_golem_statue' in name:
        return 'minecraft:copper_golem_statue'
    return None


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
        if num in self.cached_chunks:
            cached_chunk = self.cached_chunks[num]
            return cached_chunk

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
        this_chunk = self.cached_chunks[num]
        # encode the chunk data in NBT byte format
        encoded_chunk = this_chunk.encode_data()
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


# noinspection PyTypeChecker
class SaveFile(object):
    """Interface object for a minecraft save file.
    Methods:
    block(x,y,z): returns relevant block data. Accepts options.
    surface_block(x,z): returns the surface block data. Accepts options.
    get_block_entity(x,y,z): mutable NBT payload of a block entity, or None.
    get_container_items / set_container_items: chest and other container contents.
    Instance Variables:
    save_file: string with file name
    """

    # the top height of the map
    # note that the y height goes down to -64
    map_height: int = 320
    map_bottom: int = -64

    def __init__(self, foldername):
        """Initialize and read in basic file data."""
        # The file name is the save file that this object is pointed to.
        self.save_folder = foldername
        # the region objects are stored in a dict by filename.
        self.regions = {}
        # import the dat file
        self.dat = None
        self.read_dat()
        # player data may live in level.dat (pre-26.1) or a separate player file
        self.player_dat = None
        self.player_file_path = None
        self._player_payload = None
        # region folder depends on the save layout and the player's dimension
        self.region_folder = None
        self.lock = None
        self.write_lock()

    def block_to_idx(self, blk_x, blk_y, blk_z):
        """Convert absolute block cords to an intra-section index."""
        if blk_y > self.map_height or blk_y < self.map_bottom:
            return None
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
            # compose the path to the file (26.1+ uses dimensions/<ns>/<path>/region)
            file_path = self.get_region_folder() + '/' + file_name
            try:
                new_region = Region(file_path)
            except IOError:
                new_region = None
            self.regions.update({file_name: new_region})
            return new_region

    @staticmethod
    def block_to_chunk(blk_x, blk_z):
        """Convert block to chunk coordinates, return tuple."""
        chunk_x = int(blk_x // 16)
        chunk_z = int(blk_z // 16)
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
        this_chunk = reg.get_chunk(chunk_idx)
        return this_chunk

    def get_chunk_from_cord(self, blk_x, blk_z):
        """Return the chunk containing the block coordinates (x,z)."""
        chu_x, chu_z = self.block_to_chunk(blk_x, blk_z)
        this_chunk = self.get_chunk(chu_x, chu_z)
        return this_chunk

    def get_block_data(self, blk_x, blk_y, blk_z):
        this_chunk = self.get_chunk_from_cord(blk_x, blk_z)
        # if the chunk doesn't exist, return None
        if this_chunk is None:
            return None, None, None
        # map the dict storing the relevant tag data
        sections = this_chunk.tags[0].payload['sections'].payload
        # +64 or +63? what is the proper offset?
        idx = (blk_y+64) // 16
        if idx < len(sections):
            section = sections[idx].payload
        else:
            # no section means the block is air
            return 0, sections, None
        # Grab the pallete, we need it later, and also now
        if 'block_states' in section:
            block_states = section['block_states'].payload
            palette = block_states['palette'].payload
            if 'data' in block_states:
                data = block_states['data']
            else: data = None
        else:
            block_states = None
            data = None
            palette = None

        return palette, data, block_states

    def block(self, blk_x, blk_y, blk_z, fetch_properties=False):
        """Return relevant block data in a dict.
        The keys to the dict are the option key characters.
        If no options are selected, return the block id as a raw int
        because why do we need all this noise about block dictionaries?
        x, y, z : coordinates of target block.
        options : string containing option key characters (below) in any order.
        It's all in flux
        """
        palette, data, block_states = self.get_block_data(blk_x, blk_y, blk_z)
        if palette is None:
            # No chunk!
            return None
        if data is None:
            # No chunk!
            return {'B': 'minecraft:air'}
        if palette == 0:
            # Unpopulated section
            return {'B': 'minecraft:air'}
        if len(palette) == 1:
            # There's just one block type in this section, so we know what it has to be
            palette_data = palette[0].payload
            block_data = {'B': palette_data['Name'].payload}
            if not fetch_properties:
                return block_data
            if 'Properties' in palette_data:
                props = palette_data['Properties'].payload
                for propert in props:
                    block_data[propert] = props[propert].payload
            return block_data
        # just do something like this?
        blkidx = self.block_to_idx(blk_x, blk_y, blk_z)
        if blkidx is None: return None
        if not hasattr(data, "unpacked"):
            self.unpack_block_states(data, palette)
        foundpltid = data.unpacked[blkidx]
        # don't need any of this?
        # keep for readability in the future
        '''idx_offset = self.block_to_idx(blk_x, blk_y, blk_z)
        # 64 bit
        bit_stride = max(4, len(f'{len(palette) - 1:b}'))
        ids_per_int = 64 // bit_stride
        int_idx = idx_offset // ids_per_int
        bin_int = f'{data[int_idx]:064b}'
        int_offset = idx_offset % ids_per_int
        start = str((int_offset + 1) * -bit_stride)
        if int_offset == 0: end = ''
        else: end = str(int_offset * -bit_stride)
        block_ID = int(eval(f'bin_int[{start}:{end}]'), base=2)'''
        palette_data = palette[foundpltid].payload
        block_data = {'B': palette_data['Name'].payload}
        if not fetch_properties:
            return block_data
        if 'Properties' in palette_data:
            props = palette_data['Properties'].payload
            for propert in props:
                block_data[propert] = props[propert].payload
        return block_data


    def get_map_data(self):
        """returns a dictionary which is the mutable map data. Change and save to update."""
        map_payload = self.dat.tags[0].payload['Data'].payload
        # print(map_payload)
        return map_payload

    def _player_file_from_uuid(self, uuid_str):
        """Return the player .dat path for a UUID, or None if it is missing."""
        candidates = [
            self.save_folder + '/players/data/' + uuid_str + '.dat',
            self.save_folder + '/playerdata/' + uuid_str + '.dat',
        ]
        for path in candidates:
            if os.path.isfile(path):
                return path
        return None

    def _newest_player_file(self):
        """Return the most recently modified player .dat, or None."""
        folders = [
            self.save_folder + '/players/data',
            self.save_folder + '/playerdata',
        ]
        newest_path = None
        newest_mtime = -1
        for folder in folders:
            if not os.path.isdir(folder):
                continue
            for name in os.listdir(folder):
                if not name.endswith('.dat'):
                    continue
                path = folder + '/' + name
                if not os.path.isfile(path):
                    continue
                mtime = os.path.getmtime(path)
                if mtime > newest_mtime:
                    newest_mtime = mtime
                    newest_path = path
        return newest_path

    def get_player(self):
        """returns a dictionary which is the mutable player data. Change and save to update."""
        if self._player_payload is not None:
            return self._player_payload
        map_data = self.get_map_data()
        # Pre-26.1 singleplayer stores the player inside level.dat
        if 'Player' in map_data:
            self._player_payload = map_data['Player'].payload
            return self._player_payload
        # 26.1+ stores a UUID in level.dat and the player in players/data/<uuid>.dat
        player_path = None
        if 'singleplayer_uuid' in map_data:
            uuid_str = uuid_from_int_array(map_data['singleplayer_uuid'].payload)
            player_path = self._player_file_from_uuid(uuid_str)
        if player_path is None:
            player_path = self._newest_player_file()
        if player_path is None:
            raise KeyError('Player data not found in level.dat or player files')
        player_file = gzip.open(player_path)
        player_raw = player_file.read()
        player_file.close()
        self.player_dat = NbtData(player_raw)
        self.player_file_path = player_path
        self._player_payload = self.player_dat.tags[0].payload
        return self._player_payload

    def get_player_dimension(self):
        """Return the namespaced dimension id the player is currently in."""
        player = self.get_player()
        if 'Dimension' not in player:
            return 'minecraft:overworld'
        dim = player['Dimension'].payload
        if dim in (0, '0'):
            return 'minecraft:overworld'
        if dim in (-1, '-1'):
            return 'minecraft:the_nether'
        if dim in (1, '1'):
            return 'minecraft:the_end'
        return dim

    def get_region_folder(self):
        """Return the folder that stores region files for the player's dimension."""
        if self.region_folder is not None:
            return self.region_folder
        dim = self.get_player_dimension()
        if ':' in str(dim):
            namespace, path = dim.split(':', 1)
        else:
            namespace, path = 'minecraft', str(dim)
        candidates = [self.save_folder + '/dimensions/' + namespace + '/' + path + '/region']
        if dim == 'minecraft:overworld':
            candidates.append(self.save_folder + '/region')
        elif dim == 'minecraft:the_nether':
            candidates.append(self.save_folder + '/DIM-1/region')
            candidates.append(self.save_folder + '/DIM-1')
        elif dim == 'minecraft:the_end':
            candidates.append(self.save_folder + '/DIM1/region')
            candidates.append(self.save_folder + '/DIM1')
        for folder in candidates:
            if os.path.isdir(folder):
                self.region_folder = folder
                return folder
        self.region_folder = candidates[0]
        return self.region_folder

    def get_player_pos(self):
        pos_data = self.get_player()['Pos'].payload
        pos = [pos_data[i].payload for i in range(3)]
        return pos

    def get_player_block(self):
        pos_float =  self.get_player_pos()
        for k,i in enumerate(pos_float):
            if i < 0:
                pos_float[k] -= 1
        pos_int = [int(i) for i in pos_float]
        return pos_int


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

    def get_data_version(self):
        """Return the world DataVersion from level.dat, or 0 if unknown."""
        cached = getattr(self, '_data_version', None)
        if cached is not None:
            return cached
        root = self.dat.tags[0].payload
        if 'DataVersion' in root:
            self._data_version = root['DataVersion'].payload
        elif 'Data' in root and 'DataVersion' in root['Data'].payload:
            self._data_version = root['Data'].payload['DataVersion'].payload
        else:
            self._data_version = 0
        return self._data_version

    def _item_uses_components(self):
        return self.get_data_version() >= DATAVERSION_ITEM_COMPONENTS

    def _block_entities_key(self, chunk):
        payload = chunk.tags[0].payload
        if 'block_entities' in payload:
            return 'block_entities'
        if 'TileEntities' in payload:
            return 'TileEntities'
        return None

    def _block_entities_list_tag(self, chunk):
        key = self._block_entities_key(chunk)
        if key is None:
            return None
        return chunk.tags[0].payload[key]

    def _ensure_block_entities_list(self, chunk):
        list_tag = self._block_entities_list_tag(chunk)
        if list_tag is not None:
            return list_tag
        key = 'block_entities'
        if self.get_data_version() and self.get_data_version() < DATAVERSION_BLOCK_ENTITIES:
            key = 'TileEntities'
        list_tag = new_tag(9, key, [], named=True, contents_type=10)
        chunk.tags[0].payload[key] = list_tag
        return list_tag

    def get_blockentity_from_pos(self, coords):
        """Return the mutable NBT payload dict of the block entity at coords (x, y, z),
        or None if there isn't one. Change the returned tags and save to update."""
        blk_x, blk_y, blk_z = int(coords[0]), int(coords[1]), int(coords[2])
        this_chunk = self.get_chunk_from_cord(blk_x, blk_z)
        if this_chunk is None:
            return None
        list_tag = self._block_entities_list_tag(this_chunk)
        if list_tag is None:
            return None
        for ent_tag in list_tag.payload:
            ent = ent_tag.payload
            if (ent['x'].payload == blk_x and
                    ent['y'].payload == blk_y and
                    ent['z'].payload == blk_z):
                return ent
        return None

    def get_block_entity(self, blk_x, blk_y, blk_z):
        """Return the mutable NBT payload of the block entity at x, y, z, or None."""
        return self.get_blockentity_from_pos((blk_x, blk_y, blk_z))

    def iter_block_entities(self, blk_x, blk_z):
        """Yield (x, y, z, payload) for each block entity in the chunk containing x, z."""
        this_chunk = self.get_chunk_from_cord(blk_x, blk_z)
        if this_chunk is None:
            return
        list_tag = self._block_entities_list_tag(this_chunk)
        if list_tag is None:
            return
        for ent_tag in list_tag.payload:
            ent = ent_tag.payload
            yield (ent['x'].payload, ent['y'].payload, ent['z'].payload, ent)

    def _create_block_entity_tag(self, blk_x, blk_y, blk_z, entity_id):
        entity_id = namespaced_id(entity_id)
        payload = {
            'id': new_tag(8, 'id', entity_id),
            'x': new_tag(3, 'x', int(blk_x)),
            'y': new_tag(3, 'y', int(blk_y)),
            'z': new_tag(3, 'z', int(blk_z)),
            'keepPacked': new_tag(1, 'keepPacked', 0),
        }
        if self._item_uses_components():
            payload['components'] = new_tag(10, 'components', {})
        if entity_id in CONTAINER_ENTITY_IDS:
            payload['Items'] = new_tag(9, 'Items', [], named=True, contents_type=10)
        return new_tag(10, '', payload, named=False)

    def ensure_block_entity(self, blk_x, blk_y, blk_z, entity_id=None):
        """Get the block entity at x, y, z, creating one if needed.
        entity_id is inferred from the block type when omitted.
        Returns the mutable NBT payload dict, or None if this block has no entity."""
        existing = self.get_block_entity(blk_x, blk_y, blk_z)
        if entity_id is None:
            blk = self.block(blk_x, blk_y, blk_z)
            if blk is not None and 'B' in blk:
                entity_id = block_entity_id_for_block(blk['B'])
        if entity_id is not None:
            entity_id = namespaced_id(entity_id)
        if existing is not None:
            if entity_id is None or existing['id'].payload == entity_id:
                return existing
            self.remove_block_entity(blk_x, blk_y, blk_z)
        if entity_id is None:
            return None
        this_chunk = self.get_chunk_from_cord(blk_x, blk_z)
        if this_chunk is None:
            return None
        list_tag = self._ensure_block_entities_list(this_chunk)
        ent_tag = self._create_block_entity_tag(blk_x, blk_y, blk_z, entity_id)
        list_tag.payload.append(ent_tag)
        list_tag.contents_type = 10
        return ent_tag.payload

    def set_block_entity_data(self, blk_x, blk_y, blk_z, data, entity_id=None):
        """Merge python dict `data` into the block entity at x, y, z (creating it if needed).
        Values may be primitives, nested dicts/lists, or NBT tags.
        Position tags x, y, z are kept in sync with the coordinates.
        Returns the mutable NBT payload, or None on failure."""
        ent = self.ensure_block_entity(blk_x, blk_y, blk_z, entity_id)
        if ent is None:
            return None
        for key, value in data.items():
            if key in ('x', 'y', 'z'):
                continue
            if key == 'Items':
                item_tags = []
                for i, it in enumerate(value):
                    if it is None:
                        continue
                    if isinstance(it, NbtTagBase):
                        item_tags.append(it)
                    else:
                        d = dict(it)
                        if 'Slot' not in d and 'slot' not in d:
                            d['Slot'] = i
                        item_tags.append(self.item_from_dict(d))
                ent['Items'] = new_tag(9, 'Items', item_tags, named=True, contents_type=10)
                continue
            if isinstance(value, NbtTagBase):
                value.name = key
                value.named = True
                ent[key] = value
            else:
                field_type = BLOCK_ENTITY_FIELD_TYPES.get(key)
                ent[key] = python_to_nbt(value, name=key, named=True, tag_type=field_type)
        ent['x'].payload = int(blk_x)
        ent['y'].payload = int(blk_y)
        ent['z'].payload = int(blk_z)
        return ent

    def remove_block_entity(self, blk_x, blk_y, blk_z):
        """Remove the block entity at x, y, z. Return True if one was removed."""
        this_chunk = self.get_chunk_from_cord(blk_x, blk_z)
        if this_chunk is None:
            return False
        list_tag = self._block_entities_list_tag(this_chunk)
        if list_tag is None:
            return False
        blk_x, blk_y, blk_z = int(blk_x), int(blk_y), int(blk_z)
        new_payload = []
        removed = False
        for ent_tag in list_tag.payload:
            ent = ent_tag.payload
            if (ent['x'].payload == blk_x and
                    ent['y'].payload == blk_y and
                    ent['z'].payload == blk_z):
                removed = True
                continue
            new_payload.append(ent_tag)
        list_tag.payload = new_payload
        if not new_payload:
            list_tag.contents_type = 0
        return removed

    def _sync_block_entity_for_block(self, blk_x, blk_y, blk_z, block_name):
        """Create or remove the block entity to match the block type at this position."""
        new_eid = block_entity_id_for_block(block_name)
        existing = self.get_block_entity(blk_x, blk_y, blk_z)
        if existing is not None:
            old_eid = existing['id'].payload
            if new_eid == old_eid:
                return existing
            self.remove_block_entity(blk_x, blk_y, blk_z)
        if new_eid:
            return self.ensure_block_entity(blk_x, blk_y, blk_z, new_eid)
        return None

    def item_from_dict(self, item, named=False):
        """Build an unnamed TAG_Compound for an item stack from a python dict.
        Keys: id (or B), count, Slot (optional), components (optional).
        Extra keys are converted with python_to_nbt.
        """
        if item is None:
            return None
        if isinstance(item, NbtTagBase):
            item.named = named
            return item
        payload = {}
        item_id = item.get('id', item.get('B'))
        if item_id is None:
            raise ValueError('item dict needs an id')
        payload['id'] = new_tag(8, 'id', namespaced_id(item_id))
        if self._item_uses_components():
            count = item.get('count', item.get('Count', 1))
            payload['count'] = new_tag(3, 'count', int(count))
            comps = item.get('components')
            if comps:
                payload['components'] = python_to_nbt(comps, name='components', tag_type=10)
        else:
            count = item.get('Count', item.get('count', 1))
            payload['Count'] = new_tag(1, 'Count', int(count))
            old_tag = item.get('tag')
            if old_tag:
                payload['tag'] = python_to_nbt(old_tag, name='tag', tag_type=10)
        slot = item.get('Slot', item.get('slot'))
        if slot is not None:
            payload['Slot'] = new_tag(1, 'Slot', int(slot))
        known = {'id', 'B', 'count', 'Count', 'Slot', 'slot', 'components', 'tag'}
        for key, value in item.items():
            if key in known or key in payload:
                continue
            payload[key] = python_to_nbt(value, name=key, named=True)
        return new_tag(10, '', payload, named=named)

    def item_to_dict(self, item_tag):
        """Convert an item TAG_Compound (or its payload dict) to a python dict."""
        if item_tag is None:
            return None
        raw = item_tag.payload if isinstance(item_tag, NbtTagBase) else item_tag
        result = {}
        if 'id' in raw:
            result['id'] = raw['id'].payload
        if 'count' in raw:
            result['count'] = raw['count'].payload
        elif 'Count' in raw:
            result['count'] = raw['Count'].payload
        if 'Slot' in raw:
            result['Slot'] = raw['Slot'].payload
        if 'components' in raw:
            result['components'] = nbt_to_python(raw['components'])
        if 'tag' in raw:
            result['tag'] = nbt_to_python(raw['tag'])
        skip = {'id', 'count', 'Count', 'Slot', 'components', 'tag'}
        for key, value in raw.items():
            if key not in skip:
                result[key] = nbt_to_python(value)
        return result

    def _ensure_items_list(self, ent):
        if 'Items' in ent:
            tag = ent['Items']
            if tag.payload:
                tag.contents_type = 10
            return tag
        tag = new_tag(9, 'Items', [], named=True, contents_type=10)
        ent['Items'] = tag
        return tag

    def _clear_container_loot(self, ent):
        for key in ('LootTable', 'LootTableSeed'):
            if key in ent:
                del ent[key]

    def get_container_items(self, blk_x, blk_y, blk_z):
        """Return the items in the container at x, y, z as a list of dicts.
        Each dict has id, count, Slot, and components when present.
        Empty containers return []. No block entity returns None.
        """
        ent = self.get_block_entity(blk_x, blk_y, blk_z)
        if ent is None:
            return None
        if 'Items' not in ent:
            return []
        return [self.item_to_dict(it) for it in ent['Items'].payload]

    def set_container_items(self, blk_x, blk_y, blk_z, items, entity_id=None):
        """Replace all items in the container at x, y, z.
        items : list of item dicts (Slot defaults to list index),
                or a dict mapping slot number -> item dict (or None to skip).
        Also creates the block entity when the block is a container.
        Setting items clears any loot table so the items actually appear.
        """
        ent = self.ensure_block_entity(blk_x, blk_y, blk_z, entity_id)
        if ent is None:
            return None
        if isinstance(items, dict) and ('id' in items or 'B' in items):
            items = [items]
        item_tags = []
        if isinstance(items, dict):
            for slot, it in items.items():
                if it is None:
                    continue
                if isinstance(it, NbtTagBase):
                    if 'Slot' not in it.payload:
                        it.payload['Slot'] = new_tag(1, 'Slot', int(slot))
                    item_tags.append(it)
                else:
                    d = dict(it)
                    d['Slot'] = int(slot)
                    item_tags.append(self.item_from_dict(d))
        else:
            for i, it in enumerate(items):
                if it is None:
                    continue
                if isinstance(it, NbtTagBase):
                    item_tags.append(it)
                else:
                    d = dict(it)
                    if 'Slot' not in d and 'slot' not in d:
                        d['Slot'] = i
                    item_tags.append(self.item_from_dict(d))
        ent['Items'] = new_tag(9, 'Items', item_tags, named=True, contents_type=10)
        self._clear_container_loot(ent)
        return True

    def set_container_item(self, blk_x, blk_y, blk_z, slot, item, entity_id=None):
        """Set a single container slot. item is a dict, NBT tag, or None to clear.
        Returns True on success, None if there is no container block entity.
        """
        ent = self.ensure_block_entity(blk_x, blk_y, blk_z, entity_id)
        if ent is None:
            return None
        items_tag = self._ensure_items_list(ent)
        slot = int(slot)
        kept = []
        for it in items_tag.payload:
            this_slot = it.payload.get('Slot')
            if this_slot is not None and this_slot.payload == slot:
                continue
            kept.append(it)
        items_tag.payload = kept
        if item is not None:
            if isinstance(item, NbtTagBase):
                item.payload['Slot'] = new_tag(1, 'Slot', slot)
                items_tag.payload.append(item)
            else:
                d = dict(item)
                d['Slot'] = slot
                items_tag.payload.append(self.item_from_dict(d))
            items_tag.contents_type = 10
        elif not items_tag.payload:
            items_tag.contents_type = 0
        self._clear_container_loot(ent)
        return True

    def get_chest_items_from_pos(self, coords):
        """Return chest/container items at coords (x, y, z) as a list of dicts."""
        return self.get_container_items(int(coords[0]), int(coords[1]), int(coords[2]))

    def set_chest_items_from_pos(self, coords, items):
        """Replace chest/container items at coords (x, y, z). See set_container_items."""
        return self.set_container_items(int(coords[0]), int(coords[1]), int(coords[2]), items)


    def all_height_data(self, blk_x, blk_z):
        # get the chunk
        this_chunk = self.get_chunk_from_cord(blk_x, blk_z)
        # if the chunk doesn't exist, return None
        if this_chunk is None:
            return None
        data_list = this_chunk.tags[0].payload["Heightmaps"].payload
        return data_list

    @staticmethod
    def heightmap_pli_st_ed(blk_x, blk_z, stride=9):
        # find the location index, based on the coordinates
        # note the reversed coordinate ordering
        offset = (blk_x % 16) + (blk_z % 16) * 16
        pld_idx = offset // 7
        bin_idx = offset % 7
        if bin_idx == 0:
            start = '-9'
            end = ''
        elif bin_idx == 6:
            start = ''
            end = '-54'
        else:
            start = str((bin_idx + 1) * -stride)
            end = str(bin_idx * -stride)
        return pld_idx, start, end


    valid_heightmaps = {"WORLD_SURFACE",
                        "MOTION_BLOCKING",
                        "MOTION_BLOCKING_NO_LEAVES",
                        "OCEAN_FLOOR"}

    def get_heightmap(self, blk_x, blk_z, map_name='WORLD_SURFACE'):
        """Return the y value of the heightmap at coordinates x, z.
        """
        assert map_name in self.valid_heightmaps
        # map the list storing the height map
        heightdata = self.all_height_data(blk_x, blk_z, )
        if heightdata is None: return None
        if map_name in heightdata:
            data_list = heightdata[map_name].payload
        else:
            return None
        pld_idx, start, end = self.heightmap_pli_st_ed(blk_x, blk_z)
        bin_str = f'{data_list[pld_idx]:064b}'
        # the data value stores the highest non-air block
        y_ht = int(eval(f'bin_str[{start}:{end}]'), base=2) - 64
        return y_ht

    def set_heightmap(self, blk_x, blk_y, blk_z, map_name='WORLD_SURFACE'):
        """Set the x, z value in the heightmap to y"""
        assert map_name in self.valid_heightmaps
        heightdata = self.all_height_data(blk_x, blk_z, )
        if map_name in heightdata:
            data_list = heightdata[map_name].payload
        else:
            return False
        pld_idx, start, end = self.heightmap_pli_st_ed(blk_x, blk_z)
        old_bin = f'{data_list[pld_idx]:064b}'
        heightmap_y = int(blk_y + 64)
        bin_ins = f'{heightmap_y:09b}'
        if start == '': new_bin = bin_ins + eval(f'old_bin[{end}:]')
        elif end == '': new_bin = eval(f'old_bin[:{start}]') + bin_ins
        else: new_bin = eval(f'old_bin[:{start}]') + bin_ins + eval(f'old_bin[{end}:]')
        data_list[pld_idx] = int(new_bin, base=2)
        return True

    def set_all_heightmaps(self,blk_x, blk_y, blk_z):
        # don't use this particularly often, it lends itself to abuse
        for heightmap_name in self.valid_heightmaps:
            self.set_heightmap(blk_x, blk_y, blk_z, heightmap_name)


    def offset_all_heightmaps(self,blk_x, blk_z, offset):
        """offsets all the heightmap values by the offset value in the y direction"""
        for heightmap_name in self.valid_heightmaps:
            old_y = self.get_heightmap(blk_x, blk_z, heightmap_name)
            if old_y is None: return None
            new_y = old_y + offset
            self.set_heightmap(blk_x, new_y, blk_z, heightmap_name)

    def increase_all_heightmaps(self,blk_x, blk_y, blk_z):
        """sets all the heightmap values only if blk_y is greater than the current value"""
        for heightmap_name in self.valid_heightmaps:
            old_y = self.get_heightmap(blk_x, blk_z, heightmap_name)
            if old_y is None: return None
            if old_y < blk_y:
                self.set_heightmap(blk_x, blk_y, blk_z, heightmap_name)

    def decrease_all_heightmaps(self,blk_x, blk_y, blk_z):
        """sets all the heightmap values only if blk_y is less than the current value"""
        for heightmap_name in self.valid_heightmaps:
            old_y = self.get_heightmap(blk_x, blk_z, heightmap_name)
            if old_y is None: return None
            if old_y > blk_y:
                self.set_heightmap(blk_x, blk_y, blk_z, heightmap_name)

    @staticmethod
    def new_palette_item(blocktype: str):
        plttg = NbtTag10(NbtNew())
        nmtg = NbtTag8(NbtNew())
        nmtg.payload = blocktype
        nmtg.name = "Name"
        plttg.payload['Name'] = nmtg
        plttg.named = False
        return plttg

    def add_block_data(self, palette : list, data):
        item = self.new_palette_item(data['B'])
        if len(data) > 1:
            proptg = NbtTag10(NbtNew())
            proptg.named = True
            proptg.name = 'Properties'
            item.payload['Properties'] = proptg
            props = data.copy()
            del(props['B'])
            for propert in props:
                subproptg = NbtTag8(NbtNew())
                subproptg.name = propert
                subproptg.named = True
                subproptg.payload = props[propert]
                proptg.payload[propert] = subproptg
        palette.append(item)

    @staticmethod
    def new_section(idx, filltype='minecraft:air'):
        """generates a section that is all air, or whatever the filltype is"""
        # generate a new section
        newsec = NbtTag10(NbtNew())
        newsec.named = False
        newY_tag = NbtTag1(NbtNew())
        newY_tag.name = 'Y'
        newY_tag.payload = idx - 4
        newsec.payload['Y'] = newY_tag
        newBlocks_tag = NbtTag10(NbtNew())
        newBlocks_tag.name = 'block_states'
        newsec.payload['block_states'] = newBlocks_tag
        palnm = 'palette'
        paltg = NbtTag9(NbtNew())
        newBlocks_tag.payload[palnm] = paltg
        paltg.name = palnm
        paltg.contents_type = 10
        fill_tag = SaveFile.new_palette_item(filltype)
        paltg.payload.append(fill_tag)
        return newsec

    @staticmethod
    def new_block_data():
        """generates a block data object that is all zeroes"""
        data = NbtTag12(NbtNew())
        data.named = True
        data.name = 'data'
        data.payload = [0,]*256
        return data

    @staticmethod
    def unpack_block_states(data, palette):
        data.palette = palette
        # actually unpack the data
        bit_length = max(len(bin(len(palette) - 1)) - 2, 4)
        stride = 64 - (64 % bit_length)
        binary_chunks = [
            [(format(number, f'0{stride}b'))[i:i + bit_length] for i in range(0, stride, bit_length)][::-1]
            for number in data.payload
        ]
        binary_string = ''.join(''.join(c for c in subchunk) for subchunk in binary_chunks)
        data.unpacked = [int(binary_string[i:i + bit_length], 2) for i in range(0, bit_length * 4096, bit_length)]


    def set_block(self, blk_x, blk_y, blk_z, sett):
        """Set the block data to settings.
        x, y, z : coordinates of target block
        settings : dict of data to set, keys are:
        'B' for block type
        all other values are the block property to set.
        """
        blkidx = self.block_to_idx(blk_x, blk_y, blk_z)
        if blkidx is None: return None
        palette, data, block_states = self.get_block_data(blk_x, blk_y, blk_z)
        if palette is None:
            # No chunk!
            return None
        if isinstance(palette, int):
            # Unpopulated section, make a new one?
            if sett["B"] == 'minecraft:air':
                # it's already air! act like you did something
                return True
            sections = data
            idx = palette
            while len(sections) <= idx:
                newsection = self.new_section(len(sections))
                sections.append(newsection)
            section = sections[idx].payload
            block_states = section['block_states'].payload
            palette = block_states['palette'].payload
            data = None

        found = False
        # search the palette for the item we're looking for
        for i in range(len(palette)):
            if sett['B'] == palette[i].payload["Name"].payload:
                found = True
                if ("Properties" not in palette[i].payload
                    ) and ( len(sett) == 1 ):
                    # we found it
                    found = i
                    break
                props = palette[i].payload["Properties"].payload
                for propert in sett:
                    if propert == "B": continue
                    if propert in props:
                        this_propert = props[propert].payload
                        if this_propert != sett[propert]:
                            found = False
                            break
                if found:
                    found = i
                    break
        if not isinstance(found, int) or isinstance(found, bool):
            # unpack the block data before altering the palette
            if data is None:
                data = self.new_block_data()
                block_states['data'] = data
            if not hasattr(data, "unpacked"):
                self.unpack_block_states(data, palette)
            # now we can mess with the palette, since we have unpacked the data
            # generate a new palette entry
            self.add_block_data(palette, sett)
            found = len(palette) - 1

        if data is None:
            data = self.new_block_data()
            block_states['data'] = data
        if not hasattr(data, "unpacked"):
            self.unpack_block_states(data, palette)
        # actually set the block value
        data.unpacked[blkidx] = found

        if RELIGHT:
            # Dirty the lighting, because it's easier to have Minecraft do it
            this_chunk = self.get_chunk_from_cord(blk_x, blk_z)
            chunkdata = this_chunk.tags[0].payload
            if "isLightOn" in chunkdata:
                chunkdata["isLightOn"].payload = 0
        # Keep block-entity NBT in sync with the block type (chests, signs, etc.)
        self._sync_block_entity_for_block(blk_x, blk_y, blk_z, sett['B'])
        return True

    def surface_block(self, blk_x, blk_z, options='B'):
        """Return a dict of the highest non-air block at the x, z cords.
        Similar to block() but finds the highest block in the column.
        x, z : coordinates of target column
        options : same as for retrieve_block_data()
        Except! Add the y value to the dict, under the key 'y'
        """
        # get the y coordinate of the heightmap not including leaves
        # this should be the block at the surface of the map
        blk_x = int(blk_x)
        blk_z = int(blk_z)
        y_ht = self.get_heightmap(blk_x, blk_z, 'MOTION_BLOCKING_NO_LEAVES')
        # if the chunk containing the x, z cords has not been generated
        # then return None
        if y_ht is None:
            return None
        # if you got a good value, subtract one to get the surface block
        if y_ht != self.map_bottom: y_ht -= 1
        # get the block data
        output = self.block(blk_x, y_ht, blk_z)
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

    def write_player(self):
        """Write player data when it was loaded from a separate .dat file."""
        if self.player_dat is None or self.player_file_path is None:
            return
        output = self.player_dat.encode_data()
        player_file = gzip.open(self.player_file_path, 'w')
        player_file.write(output)
        player_file.close()

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
        # write player data if it lives in a separate file (26.1+)
        self.write_player()
        # again, check the lock
        if self.check_lock(): return False
        # write out the blocks
        self.write_blocks()
        return True

    def resolve_origin(self, origin=None):
        """Return [x, y, z] int coordinates for a script to work around.

        origin:
            None -- the player's current block position
            (x, z) -- that column, y from the MOTION_BLOCKING_NO_LEAVES heightmap
            (x, y, z) -- used as given
        """
        if origin is None:
            return list(self.get_player_block())
        origin = list(origin)
        if len(origin) == 2:
            x = int(origin[0])
            z = int(origin[1])
            y = self.get_heightmap(x, z, 'MOTION_BLOCKING_NO_LEAVES')
            if y is None:
                y = self.get_player_block()[1]
            return [x, int(y), z]
        if len(origin) < 3:
            raise ValueError('origin must be None, (x, z), or (x, y, z)')
        return [int(origin[0]), int(origin[1]), int(origin[2])]


def _setting_names(namespace):
    """Uppercase, non-callable names in a script module: the user settings."""
    names = []
    for key, val in list(namespace.items()):
        if key != key.upper() or key.startswith('_'):
            continue
        if callable(val):
            continue
        names.append(key)
    return names


def apply_settings(namespace, settings):
    """Copy settings onto a script module, then run its _validate() if present.

    Unknown names raise TypeError. Returns a dict of previous values for
    every uppercase setting (so a caller can restore the whole set).
    """
    if not settings:
        previous = {key: namespace[key] for key in _setting_names(namespace)}
        return previous
    unknown = []
    for key in settings:
        if key not in namespace or key != key.upper() or callable(namespace.get(key)):
            unknown.append(key)
    if unknown:
        raise TypeError("Unknown setting(s): %s" % ", ".join(unknown))
    previous = {key: namespace[key] for key in _setting_names(namespace)}
    namespace.update(settings)
    validate = namespace.get('_validate')
    if callable(validate):
        validate()
    return previous


class temporary_settings(object):
    """Apply settings to a script module for the duration of a with-block.

    Restores every uppercase setting afterward, so one call cannot leak
    into the next. Used by each script's main(..., **settings).
    """

    def __init__(self, namespace, settings=None):
        self.namespace = namespace
        self.settings = dict(settings) if settings else {}
        self.previous = None

    def __enter__(self):
        self.previous = apply_settings(self.namespace, self.settings)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.previous is not None:
            self.namespace.update(self.previous)
        return False


# some helper lists of block types

# Natural Blocks
blocktype_soils = ('grass_block', 'dirt', 'coarse_dirt', 'podzol', 'mycelium', 'rooted_dirt', 'mud')
blocktype_sands = ('gravel', 'sand', 'red_sand')

# Stone Blocks
blocktype_stones = ('stone', 'cobblestone', 'mossy_cobblestone', 'deepslate', 'granite', 'diorite', 'andesite', 'sandstone', 'red_sandstone',
                    'calcite', 'tuff', 'dripstone_block', 'prismarine', 'obsidian', 'crying_obsidian',
                    'netherrack', 'blackstone', 'basalt', 'smooth_basalt', 'end_stone')
# stairs
# slabs
# walls
# polished blocks
# polished stairs
# polished slabs

# wood blocks
base_woods = ('oak', 'spruce', 'birch', 'jungle', 'acacia', 'dark_oak', 'mangrove', 'cherry')
blocktype_bark_logs = tuple(i+'_log' for i in base_woods)
blocktype_stripped_logs = tuple('stripped_' + i + '_log' for i in base_woods)
blocktype_all_logs = blocktype_bark_logs + blocktype_stripped_logs
# also need the "wood" blocks

# leaf blocks
blocktype_leaves = tuple(i+'_leaves' for i in base_woods + ('azalea', 'flowering_azalea'))

# Plank Blocks
blocktype_planks = tuple(i+'_planks' for i in base_woods + ('bamboo', 'crimson', 'warped'))
# slabs
# stairs
# fences
# gates
# doors
# pressure plates
# buttons


# Ore Blocks
base_metals = ('iron', 'gold', 'copper')
base_ores = ('coal', 'redstone', 'lapis', 'diamond', 'emerald') + base_metals
blocktype_ores = tuple( i+'_ore' for i in base_ores + tuple('deepslate_'+i for i in base_ores) + ('nether_gold', 'nether_quartz'))
blocktype_raw_metals = tuple('raw_'+i+'_block' for i in base_metals)
blocktype_extractable = blocktype_ores + blocktype_raw_metals

# Construction Blocks
blocktype_bricks = tuple(i+'bricks' for i in ('', 'mossy_stone_', 'stone_', 'cracked_stone_', 'chiseled_stone_', 'nether_', 'cracked_nether_', 'chiseled_nether_', 'red_nether_', 'deepslate_', 'cracked_deepslate_', 'mud_', 'prismarine_', 'polished_blackstone_', 'cracked_polished_blackstone_', 'end_stone_', 'quartz_'))


# Redstone Blocks
redstones = ('redstone_block', 'redstone_lamp', 'redstone_torch', 'repeater', 'comparator', 'observer', 'piston', 'sticky_piston')

# Utility Blocks
utilities = ('crafting_table', 'furnace', 'blast_furnace', 'smoker', 'anvil', 'grindstone', 'loom', 'cartography_table', 'enchanting_table', 'stonecutter')

# Plants & Food
farmland = {'B':'farmland','moisture':'7'}
# these crops need to be planted on farmland
# set the "age" flag for crop growth. crops are grouped by maturity
blocktype_crop_blocks   = ('pumpkin', 'melon')
blocktype_crops_vines   = ('pumpkin_stem', 'melon_stem')
blocktype_crops_7mature = ('wheat', 'potatoes', 'carrots') + blocktype_crops_vines
blocktype_crops_3mature = ('beetroots',)
blocktype_crops = blocktype_crops_7mature + blocktype_crops_3mature

# the berry bush does not need to be planted on farmland
blocktype_berry_bush = {'B':'sweet_berry_bush','age':'3'}
# the sugarcane must be planted by water
blocktype_sugarcane  = {'B':'sugar_cane','age':'14'}

# Passable Cosmetic Plants
# The tall plants below have a 'half' property which should be set to 'upper' or 'lower'
blocktype_tallplants = ('tall_grass', 'large_fern')
blocktype_tallflowers = ('sunflower', 'pitcher_plant', 'lilac', 'rose_bush', 'peony')
blocktype_tall_plants = blocktype_tallplants + blocktype_tallflowers

blocktype_plants = ('short_grass', 'fern')
blocktype_tulips = tuple(i+'_tulip' for i in ('white','pink','red','orange'))
blocktype_flowers = ('poppy', 'torchflower', 'cornflower', 'dandelion', 'blue_orchid', 'allium', 'azure_bluet',
                     'oxeye_daisy', 'lily_of_the_valley', '') + blocktype_tulips
blocktype_short_plants = blocktype_plants + blocktype_flowers
blocktype_all_plants = blocktype_short_plants + blocktype_tall_plants

blocktype_pink_petals = {'B':'pink_petals', 'flower_amount': '4', 'facing':'north'}

# mushrooms can only be planted
blocktype_shrooms = tuple(i+'_mushroom' for i in ('brown', 'red'))


facing_options = ('north','east','south','west')

# vines on positive Z side of a block are "north":"true"
# vines on positive X side of a block are "west":"true"

# twisting vines age goes up to 25
# plant part has no properties

itemtype_foods = ['bread', 'pumpkin_pie', 'cake', 'cookie', 'cooked_porkchop', 'steak', 'cooked_chicken', 'cooked_mutton', 'cooked_rabbit']

# Lights
light_sources = (
    'torch',
    'lantern',
    'sea_lantern',
    'glowstone',
    'shroomlight',
    'campfire',
    'soul_campfire',
    'redstone_lamp',
    'beacon',
    'end_rod',
    'jack_o_lantern',
    'conduit',
    'fire',
    'soul_fire',
    'soul_torch',
    'soul_lantern',
    'magma_block',  # emits a small amount of light
    'lava',
    'end_portal_frame',  # emits a small amount of light
    'brown_mushroom',  # emits a small amount of light
    'end_gateway',  # emits a strong light
    'end_portal',  # emits a strong light
    'chorus_plant',  # emits a small amount of light
    'ochre_froglight',
    'pearlescent_froglight',
    'verdant_froglight',
    
)

# Note that some blocks like magma block and brown mushroom emit a low light level compared to others like torches and lanterns.


if __name__ == '__main__':
    # some test functions
    savefile_to_load = "TestB"
    mc_level = SaveFile(savefile_to_load)
    # print the dat file
    # print(mc_level.dat)
    # change the spawn location
    ## mc_level.dat.tags[0].payload['Data'].payload['SpawnX'].payload = -250
    ## mc_level.dat.tags[0].payload['Data'].payload['SpawnY'].payload = 70
    ## mc_level.dat.tags[0].payload['Data'].payload['SpawnZ'].payload = 142
    ## mc_level.write_dat()

    x, y, z = tuple(int(i) for i in mc_level.get_player_pos())

    secidx = (y + 64) // 16

    chunk = mc_level.get_chunk_from_cord(x, z)
    sec = chunk.tags[0].payload['sections'].payload[secidx].payload
    lowersec = chunk.tags[0].payload['sections'].payload[secidx-1].payload
    pal = sec['block_states'].payload['palette'].payload
    lowerpal = lowersec['block_states'].payload['palette'].payload
    pass
    # sections = chunk.tags[0].payload['sections'].payload
    # for i in range(9):
    #     newsec = mc_level.new_section(i)
    #     sections[i] = newsec

    # chest = mc_level.get_chest_items_from_pos((51,71,-39))
    # mc_level.set_chest_items_from_pos((51, 71, -39), [
    #     {'id': 'minecraft:diamond', 'count': 64, 'Slot': 0},
    #     {'id': 'minecraft:diamond_sword', 'count': 1, 'Slot': 1,
    #      'components': {'minecraft:enchantments': {'minecraft:sharpness': 5}}},
    # ])
    # # or: mc_level.set_container_item(x, y, z, 0, {'id': 'minecraft:apple', 'count': 16})
    # # raw block-entity NBT: ent = mc_level.get_block_entity(x, y, z)

    # print(f'chunk at {x}, {z}')
    # print(mc_level.get_chunk_from_cord(x, z))
    # print('heightmap ', mc_level.get_heightmap(x, z))
    # print(f'setting to {y}')
    # mc_level.set_heightmap(x, y, z)
    # print('new heightmap ', mc_level.get_heightmap(x, z))

    # sbd = mc_level.surface_block(x, z)
    # print(sbd)
    # y = sbd['y']
    # print(f'y val {y} and block value', mc_level.block(x, y, z), "which should be leaves")
    # mc_level.set_block(x, y, z, {'B':1, 'D':1})
    # print('y is', y, 'and block value', mc_level.block(x, y, z))

    # 51 ends up at x=60
    # 61 ends up at x=50

    # y values seem to be always correct

    '''x = 60
    z = -39
    for y in range(62, 80):
        #    ##y = mc_level.retrieve_heightmap(x, z)
        mc_level.set_block(x, y, z, {'B': 'minecraft:air'})'''

    '''for y in range(80, 99):
        #    ##y = mc_level.retrieve_heightmap(x, z)
        mc_level.set_block(x, y, z, {'B': 'minecraft:diamond_block'})

    print(mc_level.block(52, 70, -39))'''
    # should be spruce wood

    # # Set the player Y height position and rotation
    # mc_level.set_player_pos({'y': 91.1})
    # mc_level.set_player_rot({'pitch': 12.1, 'yaw': -110.3})

    # save the file
    print("saving")
    mc_level.write()


# To Do
# investigate the NbtTag10 code. Seems to be nesting recursively. 4 lvls down in the player position code. in data_ob?
# actually not a problem, but maybe could remove the source data pointer from each object?

