import queue
import threading
import minescript as ms
import time
from farming_utils import (
    auto_pet_rule,
    kill_nearby_pests,
    low_sack_listener_thread,
    move_forward_and_attack,
    move_forward_left_and_attack,
    move_forward_right_and_attack,
    move_left_and_attack,
    move_right_and_attack,
    move_sequence,
    sell_item_if_full,
    stop_movement_and_attack,
    check_farming_conditions,
    send_discord_message,
    use_spray,
)
from player_utils import chat_listener_thread, key_listener_thread, smooth_orientation

YAW, PITCH = -90, -59.1

VACCUM_SLOT = 2
HOE_SLOT = 1


state = {"current_pet": None}

killed_pests = set()

chat_queue = queue.Queue(maxsize=10)


def move_till(movement_fun, dest_x, dest_z, dest_y=None, ACCEPTABLE_DISPLACEMENT=1):
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


def block_route(init_x, start_z, end_z, move_till):
    move_till(move_forward_right_and_attack, init_x + 3, end_z)

    # move_sequence(
    #     {"function": move_right_and_attack, "delay": 0.5},
    #     {"function": move_forward_and_attack, "delay": 1},
    # )

    move_till(move_forward_left_and_attack, init_x + 6, start_z)

    # move_sequence(
    #     {"function": move_left_and_attack, "delay": 0.5},
    #     {"function": move_forward_and_attack, "delay": 1},
    # )


def main():
    threading.Thread(target=key_listener_thread, daemon=True).start()
    threading.Thread(
        target=chat_listener_thread, args=(chat_queue,), daemon=True
    ).start()
    # threading.Thread(target=low_sack_listener_thread, daemon=True).start()
    count = 0
    start_z, end_z = 48, 143
    init_x = -47

    while True:
        count += 1
        send_discord_message(f"Starting Melon farming run #{count}", mention=False)
        ms.execute("warp garden")
        time.sleep(2.0)
        smooth_orientation(YAW, PITCH)

        for i in range(15):
            curr_x = init_x + (i * 6)
            block_route(
                curr_x,
                start_z,
                end_z,
                move_till,
            )
        move_till(move_forward_right_and_attack, 42, end_z)


if __name__ == "__main__":
    main()
