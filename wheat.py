import queue
import threading
import minescript as ms
import time
from farming_utils import (
    move_backward_and_attack,
    move_forward_and_attack,
    move_left_and_attack,
    move_sequence,
    kill_nearby_pests,
    move_downward,
    move_upward,
    sell_item_if_full,
    stop_movement_and_attack,
    check_farming_conditions,
    send_discord_message,
    move_right_and_attack,
    auto_pet_rule,
    use_spray,
)
from player_utils import chat_listener_thread, key_listener_thread, smooth_orientation

YAW, PITCH = -90, 5.35

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
        if int(x) == dest_x and int(z) == dest_z:
            stop_movement_and_attack()
            break


def wheat_route(curr_x, start_z, end_z):
    move_sequence(
        {"function": move_left_and_attack, "delay": 0.5},
        {"function": move_forward_and_attack, "delay": 0.5},
    )
    move_till(move_right_and_attack, curr_x, end_z)
    move_sequence(
        {"function": move_right_and_attack, "delay": 0.5},
        {"function": move_forward_and_attack, "delay": 2.5},
    )
    move_till(move_left_and_attack, curr_x + 6, start_z)
    move_sequence(
        {"function": move_left_and_attack, "delay": 0.5},
        {"function": move_forward_and_attack, "delay": 2.5},
    )


def wheat_route_reverse(curr_x, start_z, end_z):
    move_sequence(
        {"function": move_right_and_attack, "delay": 1},
        {"function": move_forward_and_attack, "delay": 0.5},
    )
    move_till(move_right_and_attack, curr_x, end_z)
    move_sequence(
        {"function": move_right_and_attack, "delay": 0.5},
        {"function": move_backward_and_attack, "delay": 3},
    )
    move_sequence(
        {"function": move_left_and_attack, "delay": 1},
        {"function": move_forward_and_attack, "delay": 0.5},
    )
    move_till(move_left_and_attack, curr_x - 6, start_z)
    move_sequence(
        {"function": move_left_and_attack, "delay": 0.5},
        {"function": move_backward_and_attack, "delay": 3},
    )


def main():
    threading.Thread(target=key_listener_thread, daemon=True).start()
    threading.Thread(
        target=chat_listener_thread, args=(chat_queue,), daemon=True
    ).start()
    count = 0
    start_z, end_z = 48, 143
    init_x, end_x = 144, 234

    while True:
        count += 1
        send_discord_message(f"Starting Wheat farming run #{count}", mention=False)
        ms.execute("warp garden")
        time.sleep(2.0)
        smooth_orientation(YAW, PITCH)

        for i in range(7):
            curr_x = init_x + (i * 12)
            wheat_route(
                curr_x,
                start_z,
                end_z,
            )
        move_till(move_right_and_attack, 228, end_z)
        move_sequence(
            {"function": move_right_and_attack, "delay": 0.5},
            {"function": move_forward_and_attack, "delay": 2.5},
        )
        move_till(move_left_and_attack, 234, start_z)
        move_sequence(
            {"function": move_left_and_attack, "delay": 0.5},
            {"function": move_downward, "delay": 2.5},
        )
        move_sequence(
            {"function": move_right_and_attack, "delay": 0.5},
            {"function": move_upward, "delay": 0.5},
        )
        for i in range(7):
            curr_x = end_x - (i * 12)
            wheat_route_reverse(
                curr_x,
                start_z,
                end_z,
            )


if __name__ == "__main__":
    main()
