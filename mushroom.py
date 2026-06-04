import queue
import random
import threading
import minescript as ms
import time
from farming_utils import (
    container_watcher_thread,
    # low_sack_listener_thread,
    move_forward_and_attack,
    kill_nearby_pests,
    sell_item_if_full,
    stop_movement_and_attack,
    check_farming_conditions,
    send_discord_message,
    auto_pet_rule,
    use_spray,
    container_movement_info,
)
from player_utils import chat_listener_thread, key_listener_thread, smooth_orientation

INIT_YAW, PITCH = -90, 0.1
YAW_ANGLE_ADJUSTMENT = 26.56

state = {"current_pet": None}

killed_pests = set()

chat_queue = queue.Queue(maxsize=10)


def move_till(
    movement_fun, dest_x, dest_z, YAW, dest_y=None, ACCEPTABLE_DISPLACEMENT=1
):
    container_movement_info["movement_fun"] = movement_fun
    if dest_y is None:
        _, current_y, _ = ms.player_position()
        dest_y = int(current_y)
    movement_fun()
    while True:
        sell_item_if_full(movement_fun)
        use_spray(movement_fun)
        check_farming_conditions(YAW, PITCH, dest_y, ACCEPTABLE_DISPLACEMENT)
        auto_pet_rule(chat_queue, movement_fun, state)
        global killed_pests
        kill_nearby_pests(movement_fun, YAW, PITCH, killed_pests)
        x, _, z = ms.player_position()
        if abs(int(x) - dest_x) <= 1 and int(z) == dest_z:
            stop_movement_and_attack()
            break


def mushroom_route(curr_x, start_z, end_z):
    YAW = INIT_YAW + YAW_ANGLE_ADJUSTMENT + random.uniform(0, 0.5)
    smooth_orientation(YAW, PITCH)
    move_till(move_forward_and_attack, curr_x + 6, end_z, YAW)

    YAW = INIT_YAW - YAW_ANGLE_ADJUSTMENT + random.uniform(0, 0.5)
    smooth_orientation(YAW, PITCH)
    move_till(move_forward_and_attack, curr_x + 12, start_z, YAW)


def main():
    threading.Thread(target=key_listener_thread, daemon=True).start()
    threading.Thread(
        target=chat_listener_thread, args=(chat_queue,), daemon=True
    ).start()
    threading.Thread(target=container_watcher_thread, daemon=True).start()
    # threading.Thread(target=low_sack_listener_thread, daemon=True).start()
    count = 0
    start_z, end_z = 48, 143
    init_x = -238

    while True:
        count += 1
        send_discord_message(f"Starting mushroom farming run #{count}", mention=False)
        ms.execute("warp garden")
        time.sleep(2.0)
        # smooth_orientation(INIT_YAW+YAW_ANGLE_ADJUSTMENT, PITCH)

        for i in range(7):
            curr_x = init_x + (i * 12)
            mushroom_route(
                curr_x,
                start_z,
                end_z,
            )

        YAW = INIT_YAW + YAW_ANGLE_ADJUSTMENT + random.uniform(0, 0.5)
        smooth_orientation(YAW, PITCH)
        move_till(move_forward_and_attack, -148, end_z, YAW)

        # YAW = INIT_YAW - YAW_ANGLE_ADJUSTMENT + random.uniform(0, 0.5)
        # smooth_orientation(YAW, PITCH)
        # move_till(move_forward_and_attack, -148, start_z, YAW)


if __name__ == "__main__":
    main()
