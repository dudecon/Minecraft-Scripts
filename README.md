# Minecraft-Scripts
Python scripts for modifying Minecraft save files

NOTE: these scripts currently only work on the Anvil file format, from Minecraft Alpha to V 1.12, 1.13 and later save formats are not yet supported.

Instructions:
- You must have Python (3.x) installed, go get it if you don't http://www.python.org/download/.
- Save (or copy) the script and interface module to the folder where your maps are (usually .../.minecraft/saves).
- Get the in-world coordinates for the modifications you want to make
  - You can do this from within Minecraft by:
    - using the F3 menu
    - or by pressing TAB thrice while highlighting a block with a coordinate command active (like "fill" or "tp") This method is preferred because you can copy the coordinate text directly with CTRL-C
  - exit out of the world before running the script to avoid corrupting your save file with caching errors.
- Edit the script
  - Open the script with a text editor.
  - Change the settings at the top of the file to your liking (each script file includes extensive instructions in the comments).
  - Save it!
- Make a backup of your world (just in case!)
- Run the script
  - Double click the script (for debugging run it in IDLE or from a terminal).
  - Wait for it to finish.
    - This can take anywhere from a fraction of a second, to several minutes for very large features.
    - There will be progress updates displayed while it is running.
  - NOTE: The interface module does not do lighting updates. Optional: update the lighting in your favorite level editor.
- Load up the map in Minecraft and and enjoy!


NOTE: If you want to use these scripts inside MCEdit, you now can! Download the MCEdit filter along with the script and the interface module and place them all in the "MCEdit\MCEditData\filters" folder. You can then use them as a filter with an interactive GUI! No more editing the script to change settings! Running them like this is about 5 times slower though, so if you want to make big changes, the standalone script is probably the way to go.
