import minescript as ms
import time
import sys
from farming_utils import stop_movement_and_attack, move_backward_and_attack, move_forward_and_attack, move_left_and_attack, move_right_and_attack, check_farming_conditions, exit_fun
import random

YAW, PITCH = 0.02, -45.06

MAIN_Y = 72

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
        exit_fun("Not correct starting position")

    move_forward_and_attack()
    time.sleep(1)
    move_left_and_attack()
    time.sleep(2)
    stop_movement_and_attack()     

    move_till(move_forward_and_attack, init_x, end_z)
    
    move_right_and_attack()
    time.sleep(2)
    stop_movement_and_attack()     

    move_till(move_backward_and_attack, init_x - 1, start_z)    

    move_till(move_right_and_attack, init_x - 3, start_z)
    

def main():
    while True:
        ms.execute("warp garden")      
        time.sleep(3.0)  
        ms.player_set_orientation(YAW, PITCH)

        start_z, end_z = -238, 238

        for i in range(12):
            route_loop(-102 - (i*3), start_z, end_z)    
        
        # move_till(move_forward_and_attack, -141, 238)
        
        # move_till(move_right_and_attack, -142, 238)

        # move_till(move_backward_and_attack, -142, -238)
        

if __name__ == "__main__":
    main()
    