import math
import threading
from farming_utils import kill_nearby_pests
import minescript as ms
import os
import re
from player_utils import chat_listener_thread, exit_fun, send_discord_message
import sys

# import time
# from playsound3 import playsound

LOG_FILE = "minescript/logs.txt"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def clean_message(msg):
    return msg.encode("utf-8", errors="ignore").decode("utf-8")


def log_to_file(statement):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(clean_message(str(statement)) + "\n")


if __name__ == "__main__":
    threading.Thread(target=chat_listener_thread, daemon=True).start()
    while True:
        pass

    # try:
    #     minecraft = ms.java_class("net.minecraft.class_310")
    #     member = ms.java_member(minecraft, "getInstance")
    #     mc_instance = ms.java_call_method(minecraft, member)
    #     connection = ms.java_call_method(mc_instance, "getConnection")
    #     online_players = ms.java_call_method(connection, "getOnlinePlayers")
    #     ms.echo(f"Online players: {str(online_players)}")
    # except Exception as e:
    #     ms.echo(f"An error occurred: {str(e)}")
    #     log_to_file(f"Error occurred: {str(e)}")
    # x, y, z = ms.player_position()
    # ms.echo(f"Player position: {int(x)}, {int(y)}, {int(z)}")
    # kill_nearby_pests(
    #     2,
    #     1,
    #     lambda: ms.player_press_forward(False),
    # )


# log_to_file(str(entities))
# list = ms.job_info()
# log_to_file(str(list))
# ms.echo("Job info logged")

# playsound("./minescript/gong_sound.mp3")
# with ms.EventQueue() as event_queue:
#     event_queue.register_key_listener()
#     while True:
#         event = event_queue.get()
#         if event.type == ms.EventType.KEY and event.action == 0 and event.key == 72:
#             ms.press_key_bind("key.jump",True)
#             time.sleep(2.2)
#             ms.press_key_bind("key.jump",False)
#             ms.echo("Key pressed")

# ms.player_press_pick_item(True)
# time.sleep(0.1)
# ms.player_press_pick_item(False)
# ms.echo("Item picked")

# inventory = ms.container_get_items()
# ms.echo("Container logged")
# log_to_file(str(inventory))
# ItemStack(item='minecraft:barrier', count=1, nbt='{components:{"minecraft:custom_data":{},"minecraft:custom_name":{extra:[{color:"red",text:"Close"}],italic:0b,text:""}},count:1,id:"minecraft:barrier"}', slot=49, selected=None),
# log_to_file(str(inventory[-1].item))
# break

# block = ms.player_get_targeted_block()
# if block:
#     ms.echo(str(block))

# with ms.EventQueue() as event_queue:
#     event_queue.register_key_listener()
#     while True:
#         event = event_queue.get()
#         if event.type == ms.EventType.KEY and event.action == 0 and event.key == 72:
#             ms.echo(f"Got key with code {event.key}")
#             break

# x,y,z = ms.player_position()
# block = ms.get_block(x,y,z)
# if block:
#     ms.echo(str(block))
#     ms.echo(f"{x}, {y}, {z}")
