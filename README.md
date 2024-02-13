# Minecraft-Scripts
Python scripts for modifying Minecraft Java Edition save files

NOTE: The main branch is for 1.13 and later Minecraft save formats. For earlier map formats, check the other branches.

Instructions:
- You must have Python (3.x) installed, go get it if you don't: http://www.python.org/download/
- Save (or copy) the script and interface module to the folder where your maps are (usually .../.minecraft/saves).
- Travel in-game to the location you want to modify.
- Edit the script
  - Open the script with a text editor.
  - Change the "LOAD_NAME" variable at the top of the file to be the name of the folder that the Minecraft Java Edition World is in. Usually this is just the name of the World, but it may be different if you have multiple save files with the same name. If in doubt, the folder name is the grey text in the load menu. For safety (to prevent typos) you can copy the folder name directly from the folder rename method in your OS.
  - Change any other settings at the top of the file to your liking (each script file includes extensive instructions in the comments).
  - Save it!
- Make a backup of your world (just in case!)
- Run the script
  - Double click the script (for debugging run it in IDLE or from a terminal).
  - Wait for it to finish.
    - This can take anywhere from a fraction of a second, to several hours for very large features.
    - There will be progress updates displayed while it is running.
  - NOTE: The interface module does not do lighting updates. Optional: update the lighting in your favorite level editor.
- Load up the map in Minecraft and and enjoy!


NOTE: If you want to use these scripts inside MCEdit, you now can! Download the MCEdit filter along with the script and the interface module from the "Anvil" branch and place them all in the "MCEdit\MCEditData\filters" folder. You can then use them as a filter with an interactive GUI! No more editing the script to change settings! Running them like this is about 5 times slower though, so if you want to make big changes, the standalone script is probably the way to go.
