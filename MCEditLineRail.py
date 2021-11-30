'''MCEditLineRail.py 
   Powered Rail script by dudecon
   http://www.minecraftforum.net/viewtopic.php?f=1022&t=345491

   Needs mcInterface.py Version 6 or newer,
   and LineRail.py Version 2 or newer,
   all in the "/filters/" directory.
   http://www.peripheralarbor.com/minecraft/minecraftscripts.html
'''

from pymclevel.materials import alphaMaterials
import LineRail
import mcInterface

displayName="Line Rail"

inputs = (
    ("Line Rail script by dudecon", "label"),
    ("Tunnel Height", 3),
    
    ("To disable feature, set Spacing to 0", "label"),
    ("Pillar Spacing", 8),
    ("Light Spacing", 8),
    ("Powered Rail Spacing", 26),

    ("Rail Bed", alphaMaterials.Stone),
    ("Pillars", alphaMaterials.Stone),
    ("Lights", alphaMaterials.Torch), 
)
        
def perform(level, box, options):
    '''Load the file, lay the rails, and save the new file.
    '''
    # set up the non 1 to 1 mappings of options to LineRail global names
    optmap = {
        "Powered Rail Spacing":"POWERSPACING",
    }
    # automatically set the options that map 1 to 1 from options to LineRail
    def setOption(opt):
        OPT = optmap.get(opt, opt.replace(" ", "").upper())
        if OPT in dir(LineRail):
            val = options[opt]
            if isinstance(val, str):
                val = val.replace(" ", "").lower()
                
            setattr(LineRail,OPT,val)
    # set all of the options
    for option in options:
        setOption(option)
    # set the top and bottom of the box
    LineRail.MAPTOP = box.maxy - 1
    LineRail.MAPBTM = box.miny

    # set the materials
    bed = options["Rail Bed"]
    pillar = options["Pillars"]
    lights = options["Lights"]
    
    LineRail.BEDINFO = {"B":bed.ID, "D":bed.blockData}
    LineRail.PILLARINFO = {"B":pillar.ID, "D":pillar.blockData}
    LineRail.LIGHTINFO = {"B":lights.ID, "D":lights.blockData}

    # calculate the center
    x_center = int(box.minx + (box.width / 2))
    z_center = int(box.minz + (box.length / 2))
    # find the longest box dimension
    if box.width > box.length:
        # x is the primary direction
        x_start = box.minx
        z_start = z_center
        LineRail.DIRECTION = '+X'
        LineRail.DISTANCE = box.width
    else:
        # z is the primary direction
        z_start = box.minz
        x_start = x_center
        LineRail.DIRECTION = '+Z'
        LineRail.DISTANCE = box.length
    # set the start position
    Tunnel_Depth = LineRail.TUNNELHEIGHT
    y_start = int(box.maxy - 1 - Tunnel_Depth)
    LineRail.X = x_start
    LineRail.Y = y_start
    LineRail.Z = z_start
    
    # Set the settings which do not accept inputs
    # Turn off map re-lighting
    LineRail.LIGHTINGFIX = False
    
    # create the dummy map object
    mcmap = mcInterface.MCLevelAdapter(level, box)
    # call LineRail's main function on the map object.
    LineRail.main(mcmap)
    
    level.markDirtyBox(box)
