import minescript as ms
import time
import sys
from playsound3 import playsound


def stop_movement_and_attack():
    ms.player_press_sneak(False)
    ms.player_press_jump(False)

    ms.player_press_left(False)
    ms.player_press_right(False)
    ms.player_press_forward(False)
    ms.player_press_backward(False)

    ms.player_press_attack(False)


def move_backward_and_attack():
    ms.player_press_attack(True)
    ms.player_press_backward(True)


def move_left_and_attack():
    ms.player_press_left(True)
    ms.player_press_attack(True)


def move_right_and_attack():
    ms.player_press_right(True)
    ms.player_press_attack(True)


def move_forward_and_attack():
    ms.player_press_forward(True)
    ms.player_press_attack(True)


def move_downward():
    ms.player_press_sneak(True)


def move_upward():
    ms.player_press_jump(True)


def exit_fun(statement):
    stop_movement_and_attack()
    playsound("./minescript/gong_sound.mp3")
    ms.echo(statement)
    sys.exit(0)


def check_farming_conditions(
    target_yaw,
    target_pitch,
    target_y_level=-999,
    acceptable_displacement=1,
    tick_rate=0.05,
):
    time.sleep(tick_rate)

    player_yaw, player_pitch = ms.player_orientation()
    if target_yaw != player_yaw and target_pitch != player_pitch:
        exit_fun("Pitch or yaw changed!")

    hand = ms.player_hand_items()
    item = hand.main_hand.get("item")
    if "hoe" not in item and "axe" not in item and "diamond_sword" not in item:
        ms.echo()
        exit_fun("Hoe or axe or diamond sword not in mainhand!")

    _, y, _ = ms.player_position()
    if abs(int(y) - target_y_level) > acceptable_displacement:
        exit_fun(f"Y level changed! Expected {target_y_level}, got {int(y)}")


def move_sequence(*move_objects):
    for _, obj in enumerate(move_objects):
        move_func = obj["function"]
        delay = obj["delay"]

        move_func()
        time.sleep(delay)

    stop_movement_and_attack()


def crop_route(
    common_x, start_z, end_z, init_y, first_movement_fun, second_movement_fun, move_till
):
    x, _, z = ms.player_position()
    if int(x) != common_x and int(z) != start_z:
        exit_fun("Not the correct starting position!")

    move_sequence(
        {"function": first_movement_fun, "delay": 1},
        {"function": move_forward_and_attack, "delay": 0},
        {"function": move_upward, "delay": 0.2},
    )

    move_till(first_movement_fun, common_x, end_z, init_y, 2)

    move_sequence(
        {"function": first_movement_fun, "delay": 0.5},
        {"function": move_downward, "delay": 1.5},
    )

    move_sequence(
        {"function": second_movement_fun, "delay": 1},
        {"function": move_forward_and_attack, "delay": 0},
        {"function": move_upward, "delay": 0.2},
    )

    move_till(second_movement_fun, common_x, start_z, init_y - 2, 2)

    move_sequence(
        {"function": second_movement_fun, "delay": 0.5},
        {"function": move_downward, "delay": 1.5},
    )
