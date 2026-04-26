import threading
import minescript as ms
import time
from farming_utils import (
    flower_sugar_route,
    kill_nearby_pests,
    move_backward_and_attack,
    stop_movement_and_attack,
    check_farming_conditions,
    send_discord_message,
)
from player_utils import key_listener_thread, smooth_orientation

YAW, PITCH = 135.2, 0.3

VACCUM_SLOT = 2
HOE_SLOT = 1

killed_pests = set()


def move_till(movement_fun, dest_x, dest_z, dest_y=None, ACCEPTABLE_DISPLACEMENT=1):
    if dest_y is None:
        _, current_y, _ = ms.player_position()
        dest_y = int(current_y)
    movement_fun()
    while True:
        check_farming_conditions(YAW, PITCH, dest_y, ACCEPTABLE_DISPLACEMENT)
        global killed_pests
        kill_nearby_pests(VACCUM_SLOT, HOE_SLOT, movement_fun, YAW, PITCH, killed_pests)
        x, _, z = ms.player_position()
        if int(x) == dest_x and int(z) == dest_z:
            stop_movement_and_attack()
            break


def main():
    threading.Thread(target=key_listener_thread, daemon=True).start()
    count = 0
    start_z, end_z = -238, -49
    init_x = 45

    while True:
        count += 1
        send_discord_message(
            f"Starting sunflower/moonflower farming run #{count}", mention=False
        )
        ms.execute("warp garden")
        time.sleep(2.0)
        smooth_orientation(YAW, PITCH)

        for i in range(15):
            curr_x = init_x - (i * 6)
            flower_sugar_route(
                curr_x if curr_x >= 0 else curr_x + 1,
                start_z,
                end_z,
                move_till,
            )
        move_till(move_backward_and_attack, -44, end_z)


if __name__ == "__main__":
    main()
