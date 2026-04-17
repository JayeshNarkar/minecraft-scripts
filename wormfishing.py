from minescript import echo, execute, player_inventory_select_slot, player_press_use, player_position
import random
import sys
import time


def usage():
    echo("Usage: script.py <rod_slot> <rc_weapon_slot>")
    echo("Both slots must be hotbar indices 0-8.")


def parse_slot(arg_name: str, value: str) -> int:
    try:
        slot = int(value)
    except ValueError:
        raise ValueError(f"{arg_name} must be an integer between 0 and 8.")

    if slot < 0 or slot > 8:
        raise ValueError(f"{arg_name} must be an integer between 0 and 8.")

    return slot


def click_right():
    player_press_use(True)
    time.sleep(0.1)
    player_press_use(False)


def has_moved(previous_position):
    current_position = player_position()
    for prev_coord, curr_coord in zip(previous_position, current_position):
        if abs(curr_coord - prev_coord) > 1e-3:
            return True
    return False


def wait_random_delay(previous_position, startTime, endTime):
    delay = random.uniform(startTime, endTime)
    echo(f"Waiting {delay:.1f} seconds before next action.")
    end_time = time.time() + delay
    while time.time() < end_time:
        if has_moved(previous_position):
            echo("Movement detected. Exiting game.")
            execute("/l")
            return True
        time.sleep(0.1)
    return False


def main():
    if len(sys.argv) < 3:
        usage()
        return

    rod_slot = parse_slot("rod_slot", sys.argv[1])
    rc_weapon_slot = parse_slot("rc_weapon_slot", sys.argv[2])

    echo(f"Starting alternating right-click loop between slots {rod_slot} and {rc_weapon_slot}.")

    while True:
        echo(f"Selecting slot {rod_slot} and right-clicking.")
        player_inventory_select_slot(rod_slot)
        click_right()
        previous_position = player_position()

        if wait_random_delay(previous_position, 120, 180):
            break

        echo(f"Selecting slot {rc_weapon_slot} and right-clicking.")
        player_inventory_select_slot(rc_weapon_slot)
        click_right()
        previous_position = player_position()

        if wait_random_delay(previous_position, 1, 3):
            break


if __name__ == "__main__":
    main()
