import minescript as ms
import time
import sys
from farming_utils import (
    stop_movement_and_attack,
    move_forward_and_attack,
    move_left_and_attack,
    move_right_and_attack,
    check_farming_conditions,
)

YAW, PITCH = 90, 1.00

MAIN_Y = 68

# ACCEPTABLE_DISPLACEMENT=1


def move_till(movement_fun, dest_x, dest_z):
    movement_fun()
    while True:
        check_farming_conditions(YAW, PITCH, MAIN_Y)
        x, _, z = ms.player_position()
        if int(x) == dest_x and int(z) == dest_z:
            stop_movement_and_attack()
            break


def route_loop(init_x, start_z, end_z):
    x, _, z = ms.player_position()
    if int(x) != init_x and int(z) != start_z:
        ms.echo("Not the correct starting position!")
        sys.exit(0)

    move_till(move_left_and_attack, init_x, end_z)

    move_left_and_attack()
    time.sleep(1)
    move_forward_and_attack()
    time.sleep(1.5)
    stop_movement_and_attack()

    move_till(move_right_and_attack, init_x - 3, start_z)

    move_right_and_attack()
    time.sleep(1)
    move_forward_and_attack()
    time.sleep(1.5)
    stop_movement_and_attack()


def main():
    while True:
        ms.execute("warp garden")
        time.sleep(2.0)
        ms.player_set_orientation(YAW, PITCH)
        start_z, end_z = -238, 238
        for i in range(10):
            route_loop(-72 + (i * -6), start_z, end_z)


if __name__ == "__main__":
    main()
