import minescript as ms
import time
from farming_utils import (
    check_farming_conditions,
    move_sequence,
    stop_movement_and_attack,
    move_forward_left_and_attack,
    move_forward_right_and_attack,
    move_left_and_attack,
    move_right_and_attack,
    move_forward_and_attack,
    exit_fun,
)

YAW, PITCH = -90, -59.1

MAIN_Y = 67


def move_till(movement_fun, dest_x, dest_z):
    movement_fun()
    while True:
        check_farming_conditions(YAW, PITCH, MAIN_Y)
        x, _, z = ms.player_position()
        if int(x) == dest_x and int(z) == dest_z:
            stop_movement_and_attack()
            break


def block_route(init_x, start_z, end_z, move_till):
    x, _, z = ms.player_position()
    if int(x) != init_x and int(z) != start_z:
        exit_fun("Not the correct starting position!")

    move_till(move_forward_left_and_attack, init_x + 3, end_z)

    move_sequence(
        {"function": move_left_and_attack, "delay": 0.5},
        {"function": move_forward_and_attack, "delay": 1},
    )

    move_till(move_forward_right_and_attack, init_x + 6, start_z)

    move_sequence(
        {"function": move_right_and_attack, "delay": 0.5},
        {"function": move_forward_and_attack, "delay": 1},
    )


def main():
    start_z, end_z = 238, -238
    start_x = 48

    while True:
        ms.execute("warp garden")
        time.sleep(2.0)
        ms.player_set_orientation(YAW, PITCH)

        for i in range(5):
            block_route(start_x + (i * 6), start_z, end_z, move_till)
        move_till(move_forward_left_and_attack, 81, end_z)

        move_sequence(
            {"function": move_left_and_attack, "delay": 0.5},
            {"function": move_forward_and_attack, "delay": 1},
        )

        move_till(move_forward_right_and_attack, 81, start_z)


if __name__ == "__main__":
    main()
