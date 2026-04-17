import minescript as ms
import time
import random
import sys

caught_counter = 0

def click_right():
    ms.player_press_use(True)
    time.sleep(0.01)
    ms.player_press_use(False)

def scan_named_armor_stands():
    for entity in ms.entities(nbt=True, sort="nearest", limit=200, type="entity.minecraft.armor_stand", name="!!!"):
        if entity.name:            
            time.sleep(random.uniform(0.0001, 0.01))
            click_right()            
            global caught_counter
            caught_counter+=1
            ms.echo(f"Fish caught! {caught_counter}")
            time.sleep(random.uniform(1.0, 3.0))
            click_right()                        

def main():
    if len(sys.argv) != 2:
        ms.echo("Usage: \autofisher <fishing_rod_slot>")
        ms.echo("Slot must be hotbar index 0-8.")
        return
    rod_slot = int(sys.argv[1])
    ms.player_inventory_select_slot(rod_slot)
    click_right()
    while True:
        item=ms.player_hand_items().main_hand
        if item and "fishing_rod" in item.get('item'):            
            scan_named_armor_stands()     
            time.sleep(0.01)   
        else:
            ms.echo("Must be holding a fishing rod!")
            break

if __name__ == "__main__":
    main()