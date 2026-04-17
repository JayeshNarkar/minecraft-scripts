import minescript as ms
import time
from farming_utils import (
    stop_movement_and_attack,
    crop_route,
    move_left_and_attack,
    move_right_and_attack,
    check_farming_conditions,
)

YAW, PITCH = 90, 5.35

# ACCEPTABLE_DISPLACEMENT=1


def move_till(movement_fun, dest_x, dest_z, dest_y=None, ACCEPTABLE_DISPLACEMENT=1):
    if dest_y is None:
        _, current_y, _ = ms.player_position()
        dest_y = int(current_y)
    movement_fun()
    while True:
        check_farming_conditions(YAW, PITCH, dest_y, ACCEPTABLE_DISPLACEMENT)
        x, y, z = ms.player_position()
        if int(x) == dest_x and int(z) == dest_z:
            stop_movement_and_attack()
            break


def main():
    start_z, end_z = -238, 238
    common_x = -54
    start_y = 75

    while True:
        ms.execute("warp garden")
        time.sleep(2.0)
        ms.player_set_orientation(YAW, PITCH)

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
