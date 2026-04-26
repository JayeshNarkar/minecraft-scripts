import minescript as ms
import time
from farming_utils import (
    kill_nearby_pests,
    stop_movement_and_attack,
    crop_route,
    move_left_and_attack,
    move_right_and_attack,
    check_farming_conditions,
    send_discord_message,
)
from player_utils import smooth_orientation

YAW, PITCH = 90, 5.35

VACCUM_SLOT = 2
HOE_SLOT = 1

# ACCEPTABLE_DISPLACEMENT=1


def move_till(movement_fun, dest_x, dest_z, dest_y=None, ACCEPTABLE_DISPLACEMENT=1):
    if dest_y is None:
        _, current_y, _ = ms.player_position()
        dest_y = int(current_y)
    movement_fun()
    while True:
        check_farming_conditions(YAW, PITCH, dest_y, ACCEPTABLE_DISPLACEMENT)
        x, _, z = ms.player_position()

        kill_nearby_pests(VACCUM_SLOT, HOE_SLOT, movement_fun, YAW, PITCH)

        if int(x) == dest_x and int(z) == dest_z:
            stop_movement_and_attack()
            break


def main():
    count = 0
    start_z, end_z = -238, 238
    common_x = -66
    start_y = 75

    while True:
        count += 1
        send_discord_message(f"Starting wheat farming run #{count}", mention=False)
        ms.execute("warp garden")
        time.sleep(2.0)
        smooth_orientation(YAW, PITCH)

        crop_route(
            common_x,
            start_z,
            end_z,
            start_y,
            move_left_and_attack,
            move_right_and_attack,
            move_till,
        )

        crop_route(
            common_x,
            start_z,
            end_z,
            start_y - 4,
            move_left_and_attack,
            move_right_and_attack,
            move_till,
        )

        move_till(move_left_and_attack, common_x, end_z)


if __name__ == "__main__":
    main()
