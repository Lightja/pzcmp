# pzcmp
Compares Items between Project Zomboid builds. Made to compare Build 42 and Build 41 and made to be re-ran as build 42 gets updated.

to use it, you'll need to edit the last couple lines with the filepaths to the scripts folder for each build. I recommend going back to stable if not already, taking a copy of stable (b41), updating to unstable, then taking a copy of that script folder and putting it on your desktop or somewhere you can find it. The output by default is just to the console. On Windows, I would recommend outputting it to a txt file by running a command like:
```
Py pzcmp.py > pz_b42_updated_items.txt
```

Here is where the scripts folder is by default on Windows:
C:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid\media\scripts

optionally, print_weapons can be modified to change the sort order. Currently 2 sorts are commented out, leaving the sort by durability:
```
def print_weapons(weapons):
    for weapon in weapons:
        calculate_weapon_output(weapon)
    weapons = sorted(weapons, key=lambda x: int(x["stats"].get("Durability",0)), reverse=True)
    # weapons = sorted(weapons, key=lambda x: int(x["stats"].get("DPS",0)), reverse=True)
    # weapons = sorted(weapons, key=lambda x: int(x["stats"].get("DPSwgt",0)), reverse=True)
    for weapon in weapons:
        print(weapon.get('output','ERROR'))
```

also, the outputs are at the bottom of compare_item_lists, so you can comment out certain sections if you're only interested in weapons for example.
