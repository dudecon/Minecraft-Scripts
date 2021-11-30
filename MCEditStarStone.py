'''MCEditStarStone.py 
   Crater and Boulder generating script by dudecon
   http://www.minecraftforum.net/viewtopic.php?f=1022&t=243901

   Needs mcInterface.py Version 4 or newer,
   and StarStone.py Version 5 or newer,
   all in the "/filters/" directory.
   http://www.peripheralarbor.com/minecraft/minecraftscripts.html
'''

from pymclevel.materials import alphaMaterials
import StarStone
import mcInterface

displayName="StarStone"

inputs = (
    ("StarStone script by dudecon", "label"),
               
    ("Number of features", 1),
    ("Placement Radius", 2),

    ("Boulders", True),
    ("Boulder Size", 5.0),
    ("Boulder Randomization", 2.0),
    ("Boulder Treasure", (0.3, 0.0, 1.0)),

    ("Craters", True),
    ("Crater Depth", 9.0),
    ("Depth Randomization", 3.0),
    ("Crater Fill", 0.0),
    ("Crater Depth Diameter Miltiple", 5.0),
    ("Crater Ejecta", True),
    ("Ejecta Distance", 1.1),
    
    ("Boulder Material", alphaMaterials.Obsidian),
    ("Crater Fill Material", alphaMaterials.Lava),
    ("Surface Fraction", (0.0, 1.0) ),
    ("Surface Material", alphaMaterials.Fire),
    
)
        
def perform(level, box, options):
    '''create the craters and/or boulders
    '''
    # set up the non 1 to 1 mappings of options to StarStone global names
    optmap = {
        "Number of ...":"FEATURENUM",
        "Placement Radius":"RADIUS",
    }
    # automatically set the options that map 1 to 1 from options to StarStone
    def setOption(opt):
        OPT = optmap.get(opt, opt.replace(" ", "").upper())
        if OPT in dir(StarStone):
            val = options[opt]
            if isinstance(val, str):
                val = val.replace(" ", "").lower()
                
            setattr(StarStone,OPT,val)
    # set all of the options
    for option in options:
        setOption(option)
    # set the materials
    boulder = options["Boulder Material"]
    fill = options["Crater Fill Material"]
    surface = options["Surface Material"]
    
    StarStone.BOULDERINFO = {"B":boulder.ID, "D":boulder.blockData}
    StarStone.SURFACEINFO = {"B":fill.ID, "D":fill.blockData}
    StarStone.FILLINFO = {"B":surface.ID, "D":surface.blockData}

    # calculate the center and radius
    x_center = int(box.minx + (box.width / 2))
    z_center = int(box.minz + (box.length / 2))
    # set the center position
    StarStone.X = x_center
    StarStone.Z = z_center

    # set the StarStone settings that are not in the inputs
    # and should be a specific value
    # take these out if added to settings
    StarStone.LIGHTINGFIX = False

    # create the dummy map object
    mcmap = mcInterface.MCLevelAdapter(level, box)
    # call StarStone's main function on the map object.
    StarStone.main(mcmap)
    
    level.markDirtyBox(box)
