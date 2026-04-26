import minescript as ms
import time
from farming_utils import (
    check_farming_conditions,
    kill_nearby_pests,
    move_sequence,
    stop_movement_and_attack,
    move_forward_left_and_attack,
    move_forward_right_and_attack,
    move_left_and_attack,
    move_right_and_attack,
    move_forward_and_attack,
    exit_fun,
)
from player_utils import smooth_orientation

YAW, PITCH = -90, -59.1

MAIN_Y = 67

VACCUM_SLOT = 2
HOE_SLOT = 1


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
    start_x = 84

    while True:
        ms.execute("warp garden")
        time.sleep(2.0)
        smooth_orientation(YAW, PITCH)
        for i in range(5):
            block_route(start_x + (i * 6), start_z, end_z, move_till)
        move_till(move_forward_left_and_attack, 117, end_z)

        move_sequence(
            {"function": move_left_and_attack, "delay": 0.5},
            {"function": move_forward_and_attack, "delay": 1},
        )

        move_till(move_forward_right_and_attack, 117, start_z)


if __name__ == "__main__":
    main()
