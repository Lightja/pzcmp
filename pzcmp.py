import os
import re

# Parses custom format item in .txt files
def parse_item(file_content):
    items = []
    item_pattern = re.compile(r'item (\w+)\s*\{(.*?)\}', re.DOTALL)
    stat_pattern = re.compile(r'(\w+)\s*=\s*([^,;]+)')
    for item_match in item_pattern.finditer(file_content):
        item_name = item_match.group(1)
        item_stats = {}
        stats_content = item_match.group(2)
        for stat_match in stat_pattern.finditer(stats_content):
            stat_name = stat_match.group(1)
            stat_value = stat_match.group(2).strip()
            if stat_value.upper() == "TRUE":
                stat_value = True
            elif stat_value.upper() == "FALSE":
                stat_value = False

            # semicolon-separated lists (e.g., Categories, Tags)
            if isinstance(stat_value, str) and ";" in stat_value:
                stat_value = stat_value.split(";")

            item_stats[stat_name] = stat_value

        items.append({"name": item_name, "stats": item_stats})

    return items

def parse_folder(folder_path):
    all_items = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    items = parse_item(file_content)
                    all_items.extend(items)
    return all_items
    
def calculate_weapon_output(item):
    stats = item.get('stats')
    display_name = stats.get("DisplayName", "")
    name = item.get("name", "")
    categories = stats.get("Categories", "")
    display_category = stats.get("DisplayCategory", "")
    sub_category = stats.get("SubCategory", "")
    weight = stats.get("Weight", "")
    min_damage = stats.get("MinDamage", "")
    max_damage = stats.get("MaxDamage", "")
    crit_chance = stats.get("CriticalChance", "0")
    crit_dmg_multiplier = stats.get("CritDmgMultiplier", "1")
    base_speed = stats.get("BaseSpeed", "1")
    weapon_length = stats.get("WeaponLength", "")
    door_damage = stats.get("DoorDamage", "")
    tree_damage = stats.get("TreeDamage", "")
    knockback_on_nodeath = stats.get("KnockBackOnNoDeath", "")
    pushback_mod = stats.get("PushbackMod", "")
    endurance_mod = stats.get("EnduranceMod","1")
    
    condition_max = stats.get("ConditionMax", "")
    condition_chance = stats.get("ConditionLowerChanceOneIn", "")
    if condition_max != "" and condition_chance != "":
        durability = int(float(condition_max) * float(condition_chance))
        stats["Durability"] = durability
    else:
        durability = ""
    if min_damage != "" and max_damage != "":
        avg_damage = (float(min_damage) + float(max_damage))/2.0
    else:
        avg_damage = ""
    if avg_damage != "" and base_speed != "" and crit_chance != "" and crit_dmg_multiplier != "":
        dps = (float(avg_damage) + float(avg_damage) * (( float(crit_chance) * float(crit_dmg_multiplier))/100.0)) * float(base_speed)
        stats["DPS"] = dps
    else:
        dps = ""
    if dps != "" and weight != "":
        dps_per_wgt = float(dps)/float(weight)/float(endurance_mod)
        stats["DPSwgt"] = dps_per_wgt
    else:
        dps_per_wgt = ""
        
    def round_val(value):
        return round(value, 3) if isinstance(value, float) else value
    
    output = f"{display_name} ({name}) - {categories} ({display_category}) - {sub_category}\n"
    output += f"    Dmg: {min_damage} - {max_damage}, Crit: {crit_chance}% ({crit_dmg_multiplier}x) (Wgt: {weight})\n"
    output += f"        DPS: {round_val(dps)} - DPS/Wgt: {round_val(dps_per_wgt)} - EnduranceMod: {endurance_mod}\n"
    output += f"    Durability: {durability} (Max: {condition_max}, Break: 1 in {condition_chance})\n"
    output += f"    Speed: {base_speed}, Length: {weapon_length}, DoorDmg: {door_damage}, TreeDmg: {tree_damage}\n"
    output += f"    Pushback: {knockback_on_nodeath} ({pushback_mod})"
    
    item['output'] = output
    
# For now, I'm just manually changing the ordering
def print_weapons(weapons):
    for weapon in weapons:
        calculate_weapon_output(weapon)
    weapons = sorted(weapons, key=lambda x: int(x["stats"].get("Durability",0)), reverse=True)
    # weapons = sorted(weapons, key=lambda x: int(x["stats"].get("DPS",0)), reverse=True)
    # weapons = sorted(weapons, key=lambda x: int(x["stats"].get("DPSwgt",0)), reverse=True)
    for weapon in weapons:
        print(weapon.get('output','ERROR'))

def compare_item_lists(list1, list2):
    list2_dict = {item['name']: item['stats'] for item in list2}
    identical_items = []
    missing_from_list2 = []
    added_items = []
    added_weapons = []
    general_items_with_differences = []
    weapon_items_with_differences = []
    stat_order = [
        "DisplayName", "Categories", "DisplayCategory", "TwoHandWeapon", "Weight", "CalculatedDurability",
        "BaseSpeed", "MinDamage", "MaxDamage", "WeaponLength", "CriticalChance",
        "CritDmgMultiplier", "DoorDamage", "TreeDamage", "PushbackMod", "KnockBackOnNoDeath",
        "SubCategory"
    ]

    # for better alignment
    padding_width = 24

    for item1 in list1:
        item_name = item1['name']
        item_stats_1 = item1['stats']
        
        if item_name not in list2_dict:
            missing_from_list2.append(item_name)
        else:
            item_stats_2 = list2_dict[item_name]
            differences = []
            
            # Compare stats
            for stat, value1 in item_stats_1.items():
                value2 = item_stats_2.get(stat)
                
                if value2 is None:
                    differences.append((stat, f"(REMOVED) {str(value2)}"))
                elif value1 != value2:
                    differences.append((stat, f"{str(value1)} ==> {str(value2)}"))
                if stat == "ConditionMax":
                    differences.append(("maxhp", value2))
                elif stat == "ConditionLowerChanceOneIn":
                    differences.append(("dmgchance", value2))
            
            # Check for stats in list2 (b42) that are not in list1 (b41)
            for stat, value2 in item_stats_2.items():
                value1 = item_stats_1.get(stat)
                if value1 is None:
                    differences.append((stat, f"(NEW) {str(value2)}"))
                    if stat == "ConditionMax":
                        differences.append(("maxhp", value2))
                    elif stat == "ConditionLowerChanceOneIn":
                        differences.append(("dmgchance", value2))
                        
            # ConditionMax and ConditionLowerChanceOneIn get added to differences list even when they arent different for calculating durability of updated weapons.
            found_differences = any(diff[0] not in ["ConditionMax","ConditionLowerChanceOneIn","maxhp","dmgchance"] for diff in differences)
               
            if found_differences:
                if item_stats_1.get('Type') == 'Weapon' or item_stats_2.get('Type') == 'Weapon':
                    updated_stats = [diff[0] for diff in differences]
                    for stat in stat_order:
                        if stat not in updated_stats and stat != "CalculatedDurability":
                            differences.append((stat, f"{item_stats_2.get(stat)}"))
                        if stat == "ConditionMax":
                            differences.append(("maxhp", value2))
                        elif stat == "ConditionLowerChanceOneIn":
                            differences.append(("dmgchance", value2))
                    stat_maxhp = 0
                    stat_dmgchance = 0
                    for diff in differences:
                        if diff[0] == "maxhp":
                            stat_maxhp = diff[1]
                        if diff[0] == "dmgchance":
                            stat_dmgchance = diff[1]
                    stat_durability = int(stat_maxhp) * int(stat_dmgchance)
                    differences.append(("CalculatedDurability", f"{stat_durability} (Max: {stat_maxhp} Break: 1 in {stat_dmgchance})"))
                    differences = [diff for diff in differences if diff[0] not in ["maxhp","dmgchance","ConditionMax","ConditionLowerChanceOneIn"]]
                    weapon_items_with_differences.append({"name": item_name, "differences": differences})
                else:
                    differences = [diff for diff in differences if diff[0] not in ["maxhp","dmgchance","ConditionMax","ConditionLowerChanceOneIn"]]
                    general_items_with_differences.append({"name": item_name, "differences": differences})
            else:
                identical_items.append(item_name)
    
    # Check for items in list2 (b42) that are missing in list1 (b41)
    list1_names = {item['name'] for item in list1}
    for item2 in list2:
        if item2['name'] not in list1_names:
            item_stats_2 = list2_dict[item2['name']]
            if item_stats_2.get('Type') == 'Weapon':
                added_weapons.append(item2)
            else:
                added_items.append(item2)
    
    def reorder_differences(differences):
        differences.sort(key=lambda x: stat_order.index(x[0]) if x[0] in stat_order else float('inf'))
        return differences

    print(f"Identical Items: {identical_items}")
    print(f"\nRemoved in b42: {missing_from_list2}")
    
    # too lazy to debug root cause, but items are getting added to the weapon list, idk why. Did this to fix afterwards. Something to do with shared names or something.
    added_weapons_actually_items = [item for item in added_weapons if item['stats'].get('Type') != 'Weapon'] 
    added_weapons = [item for item in added_weapons if item['stats'].get('Type') == 'Weapon']
        
    added_items = added_weapons_actually_items + added_items
    
    # can individually comment these out if you only want one section.
    
    print("\n~~~~~~~~~~~~~~~~~~~~\n")
    print("\nNew Items:")
    print("\n~~~~~~~~~~~~~~~~~~~~\n")
    for item in added_items:
        print(f"\n  NEW  {item['name']}")
        for stat, value in item['stats'].items():
            print(f"         {str(stat).rjust(padding_width)}: {value}")
    
    print("\n~~~~~~~~~~~~~~~~~~~~\n")
    print("\nNew Weapons:")
    print("\n~~~~~~~~~~~~~~~~~~~~\n")
    print_weapons(added_weapons)
    for item in added_weapons:
        print(f"\n  NEW  {item['name']}")
        for stat, value in item['stats'].items():
            print(f"         {str(stat).rjust(padding_width)}: {value}")
        print_weapon(item)
    
    print("\n~~~~~~~~~~~~~~~~~~~~\n")
    print("\nUpdated Items:")
    print("\n~~~~~~~~~~~~~~~~~~~~\n")
    for item in general_items_with_differences:
        print(f"\n{item['name']}:")
        sorted_diffs = reorder_differences(item['differences'])
        for stat, diff in sorted_diffs:
            print(f"    * {stat.ljust(padding_width)}: {diff}")

    print("\n~~~~~~~~~~~~~~~~~~~~\n")
    print("\nUpdated Weapons:")
    print("\n~~~~~~~~~~~~~~~~~~~~\n")
    for item in weapon_items_with_differences:
        print(f"\n{item['name']}:")
        sorted_diffs = reorder_differences(item['differences'])
        for stat, diff in sorted_diffs:
            print(f"    * {stat.ljust(padding_width)}: {diff}")

# need to manually change to your actual filepaths of compared media\scripts folders.
b41_scripts_path = r'C:\Users\Lightja\Desktop\dump\dump desktop\Decompiled\Zomboid\build 41\media\scripts' 
b41_items = parse_folder(b41_scripts_path)
b42_scripts_path = r'C:\Users\Lightja\Desktop\dump\dump desktop\Decompiled\Zomboid\build 42\media\scripts'
b42_items = parse_folder(b42_scripts_path)

compare_item_lists(b41_items, b42_items)
