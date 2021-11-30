'''MCEditWizardMountain.py 
   Mountain Uprooting script by dudecon
   http://www.minecraftforum.net/viewtopic.php?f=1022&t=258100

   Needs mcInterface.py Version 6 or newer,
   and WizardMountain.py Version 3 or newer,
   all in the "/filters/" directory.
   http://www.peripheralarbor.com/minecraft/minecraftscripts.html
'''

import WizardMountain
import mcInterface

displayName="Wizard Mountain"

inputs = (
    ("Wizard Mountain script by dudecon", "label"),
               
    ("Radius", 7),
    ("Height", 20),
    ("Depth Scale", 1.5),
    ("Max Vertical Gap", 3),
    ("Depth Offset", 1),  
    
)
        
def perform(level, box, options):
    '''Load the file, lift the mountain, and save the new file.
    '''
    # set up the non 1 to 1 mappings of options to Forester global names
    optmap = {
        "Max Vertical Gap":"MAXVERTICALGAP",
    }
    # automatically set the options that map 1 to 1 from options to Forester
    def setOption(opt):
        OPT = optmap.get(opt, opt.replace(" ", "").upper())
        if OPT in dir(WizardMountain):
            val = options[opt]
            if isinstance(val, str):
                val = val.replace(" ", "").lower()
                
            setattr(WizardMountain,OPT,val)
    # set all of the options
    for option in options:
        setOption(option)
    # set the top and bottom of the box
    WizardMountain.MAPTOP = box.maxy - 1
    WizardMountain.MAPBTM = box.miny

    # calculate the center
    x_center = int(box.minx + (box.width / 2))
    z_center = int(box.minz + (box.length / 2))
    # set the center position
    WizardMountain.X = x_center
    WizardMountain.Z = z_center
    
    # create the dummy map object
    mcmap = mcInterface.MCLevelAdapter(level, box)
    # call WizardMountain's main function on the map object.
    WizardMountain.main(mcmap)
    
    level.markDirtyBox(box)
