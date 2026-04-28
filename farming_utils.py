import os
import queue
import random
import minescript as ms
import time
import math
import re
from player_utils import (
    exit_fun,
    send_discord_message,
    smooth_look_at,
    smooth_orientation,
)

BASE_FOLDER = "minescript/"

PEST_FILE = BASE_FOLDER + "pest_status.txt"
os.makedirs(os.path.dirname(PEST_FILE), exist_ok=True)

SPRAY_FILE = BASE_FOLDER + "spray_status.txt"
os.makedirs(os.path.dirname(SPRAY_FILE), exist_ok=True)

INVENTORY_FILE = BASE_FOLDER + "inventory_status.txt"
os.makedirs(os.path.dirname(INVENTORY_FILE), exist_ok=True)

ROD_SLOT = 4
SPRAY_SLOT = 3
VACCUM_SLOT = 2
HOE_SLOT = 1

PESTS = [
    "Fly",
    "Cricket",
    "Locust",
    "Rat",
    "Mosquito",
    "Earthworm",
    "Mite",
    "Moth",
    "Slug",
    "Beetle",
    "Praying Mantis",
    "Dragonfly",
]


def clean_entity_name(name):
    if not name:
        return ""

    # Remove Minecraft color codes (§ followed by hex digit)
    cleaned = re.sub(r"§[0-9a-fk-or]", "", name)

    # Remove everything that isn't basic printable ASCII
    cleaned = re.sub(r"[^\x20-\x7E]", "", cleaned)

    # Remove extra whitespace
    cleaned = " ".join(cleaned.split())

    if cleaned.endswith("600"):
        return cleaned[:-3].strip()  # remove "600" from end
    else:
        return ""


def contains_pest_name(entity_name):
    cleaned = clean_entity_name(entity_name).lower()

    for pest in PESTS:
        if pest.lower() in cleaned:
            return pest
    return None


def distance_calculator(playerPos, entityPos):
    return math.sqrt(
        (playerPos[0] - entityPos[0]) ** 2
        + (playerPos[1] - entityPos[1]) ** 2
        + (playerPos[2] - entityPos[2]) ** 2
    )


def stop_movement_and_attack():
    ms.player_press_sneak(False)
    ms.player_press_jump(False)

    ms.player_press_left(False)
    ms.player_press_right(False)
    ms.player_press_forward(False)
    ms.player_press_backward(False)

    ms.player_press_attack(False)


def move_backward_and_attack():
    ms.player_press_attack(True)
    ms.player_press_backward(True)


def move_left_and_attack():
    ms.player_press_left(True)
    ms.player_press_attack(True)


def move_right_and_attack():
    ms.player_press_right(True)
    ms.player_press_attack(True)


def move_forward_and_attack():
    ms.player_press_forward(True)
    ms.player_press_attack(True)


def move_downward():
    ms.player_press_sneak(True)


def move_upward():
    ms.player_press_jump(True)


def move_forward():
    ms.player_press_forward(True)


def check_farming_conditions(
    target_yaw,
    target_pitch,
    target_y_level=-999,
    acceptable_displacement=1,
    tick_rate=0.05,
):
    time.sleep(tick_rate)

    player_yaw, player_pitch = ms.player_orientation()
    if target_yaw != player_yaw and target_pitch != player_pitch:
        exit_fun(
            f"Pitch or yaw changed! got {player_yaw}, {player_pitch}. Expected {target_yaw}, {target_pitch}."
        )

    hand = ms.player_hand_items()
    item = hand.main_hand.get("item")
    if "hoe" not in item and "axe" not in item and "diamond_sword" not in item:
        exit_fun("Hoe or axe or diamond sword not in mainhand!")

    _, y, _ = ms.player_position()
    if abs(int(y) - target_y_level) > acceptable_displacement:
        exit_fun(f"Y level changed! Expected {target_y_level}, got {int(y)}.")


def move_sequence(*move_objects):
    for _, obj in enumerate(move_objects):
        move_func = obj["function"]
        delay = obj["delay"]

        move_func()
        time.sleep(delay)

    stop_movement_and_attack()


def move_forward_left_and_attack():
    ms.player_press_forward(True)
    ms.player_press_left(True)
    ms.player_press_attack(True)


def move_forward_right_and_attack():
    ms.player_press_forward(True)
    ms.player_press_right(True)
    ms.player_press_attack(True)


def move_right_forward_and_attack():
    ms.player_press_right(True)
    ms.player_press_forward(True)
    ms.player_press_attack(True)


def move_left_forward_and_attack():
    ms.player_press_left(True)
    ms.player_press_forward(True)
    ms.player_press_attack(True)


def flower_sugar_route(init_x, start_z, end_z, move_till):
    move_till(move_backward_and_attack, init_x, end_z)
    move_sequence(
        {"function": move_left_and_attack, "delay": 1},
    )
    move_sequence(
        {"function": move_right_and_attack, "delay": 0.5},
    )
    move_till(move_right_forward_and_attack, init_x - 3, start_z)
    move_sequence(
        {"function": move_forward, "delay": 1},
    )


def crop_route(
    common_x, start_z, end_z, init_y, first_movement_fun, second_movement_fun, move_till
):
    x, _, z = ms.player_position()
    if int(x) != common_x and int(z) != start_z:
        exit_fun("Not the correct starting position!")

    move_sequence(
        {"function": first_movement_fun, "delay": 1},
        {"function": move_forward_and_attack, "delay": 0},
        {"function": move_upward, "delay": 0.2},
    )

    move_till(first_movement_fun, common_x, end_z, init_y, 2)

    move_sequence(
        {"function": first_movement_fun, "delay": 0.5},
        {"function": move_downward, "delay": 1.5},
    )

    move_sequence(
        {"function": second_movement_fun, "delay": 1},
        {"function": move_forward_and_attack, "delay": 0},
        {"function": move_upward, "delay": 0.2},
    )

    move_till(second_movement_fun, common_x, start_z, init_y - 2, 2)

    move_sequence(
        {"function": second_movement_fun, "delay": 0.5},
        {"function": move_downward, "delay": 1.5},
    )


def use_spray(move_fun):
    if read_spray_status() == "none":
        stop_movement_and_attack()
        time.sleep(0.5 + random.uniform(0, 0.5))
        ms.player_inventory_select_slot(SPRAY_SLOT)
        ms.player_press_use(True)
        time.sleep(0.1 + random.uniform(0, 0.1))
        ms.player_press_use(False)
        time.sleep(0.5 + random.uniform(0, 0.5))
        ms.player_inventory_select_slot(HOE_SLOT)
        time.sleep(0.5 + random.uniform(0, 0.5))
        move_fun()


def use_rod(move_fun):
    stop_movement_and_attack()
    ms.player_inventory_select_slot(ROD_SLOT)
    time.sleep(0.5 + random.uniform(0, 0.5))
    ms.player_press_use(True)
    time.sleep(0.1 + random.uniform(0, 0.1))
    ms.player_press_use(False)
    time.sleep(0.5 + random.uniform(0, 0.5))
    ms.player_inventory_select_slot(HOE_SLOT)
    time.sleep(0.5 + random.uniform(0, 0.5))
    move_fun()


def wait_for_autopet(chat_queue, keyword, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            msg = chat_queue.get_nowait().lower()
            if "autopet" in msg and keyword.lower() in msg:
                return True
        except queue.Empty:
            time.sleep(0.1)
    return False


def read_spray_status():
    try:
        with open(SPRAY_FILE, "r") as f:
            status = f.read().strip().lower()
            if status == "none":
                return "none"
            else:
                return "exists"
    except:
        return "exists"


def read_inventory_status():
    try:
        with open(INVENTORY_FILE, "r") as f:
            status = f.read().strip().lower()
            return "full" if status == "full" else "not_full"
    except:
        return "not_full"


def sell_item_if_full(move_fun):
    if read_inventory_status() != "full":
        return

    stop_movement_and_attack()
    ms.execute("desk")
    time.sleep(2)

    # items = ms.container_get_items()
    # if items is None:
    #     ms.echo("Failed to open desk, resuming...")
    #     move_fun()
    #     return

    # ms.echo("Waiting for SkyMart seller to finish...")
    while ms.container_get_items() is not None:
        time.sleep(0.5)

    ms.echo("Selling done, resuming...")
    time.sleep(2.5 + random.uniform(0, 0.5))
    move_fun()


def read_pest_status():
    try:
        with open(PEST_FILE, "r") as f:
            status = f.read().strip().lower()
            if status == "ready":
                return "ready"
            else:
                return "not_ready"
    except:
        return "not_ready"


def auto_pet_rule(chat_queue, move_fun, state):
    status = read_pest_status()
    target_pet = "slug" if status == "ready" else "mooshroom"

    if state["current_pet"] == target_pet:
        return
    while True:
        use_rod(move_fun)
        if wait_for_autopet(chat_queue, target_pet):
            state["current_pet"] = target_pet
            break


def kill_nearby_pests(
    move_fun,
    YAW=90,
    PITCH=0,
    killed_pests=None,
    detection_range=15,
):
    entities = ms.get_entities(max_distance=detection_range, sort="nearest")

    for entity in entities:
        if contains_pest_name(entity.name):
            killed_pests.add(entity.uuid)
            stop_movement_and_attack()
            send_discord_message(
                f"Killing pest: {clean_entity_name(entity.name)}. Count: {len(killed_pests)}",
                mention=False,
            )
            ms.player_inventory_select_slot(VACCUM_SLOT)
            smooth_look_at(entity.position[0], entity.position[1], entity.position[2])
            ms.player_press_use(True)
            time.sleep(4)
            ms.player_press_use(False)

            smooth_orientation(YAW, PITCH)
            ms.player_inventory_select_slot(HOE_SLOT)
            time.sleep(0.5 + random.uniform(0, 0.5))
            move_fun()
