import minescript as ms
import time
import sys
from farming_utils import stop_movement_and_attack, move_backward_and_attack, move_forward_and_attack, move_left_and_attack, move_right_and_attack, check_farming_conditions

YAW, PITCH = 135.16, 3.00

MAIN_Y = 73

# ACCEPTABLE_DISPLACEMENT=1        

def move_till(movement_fun, dest_x, dest_z):
    movement_fun()
    while True:
        check_farming_conditions(YAW, PITCH, MAIN_Y)
        x, _, z = ms.player_position()
        if int(x) == dest_x and int(z) == dest_z:
            stop_movement_and_attack()
            break

def route_loop(init_x, init_z, first_x, first_z, second_x, second_z, third_x, third_z, fourth_x, fourth_z):
    x, _, z = ms.player_position()
    if int(x) != init_x and int(z) != init_z:        
        ms.echo("Not the correct starting position!")
        sys.exit(0)

    move_till(move_backward_and_attack, first_x, first_z)
    
    move_till(move_left_and_attack, second_x, second_z)    

    move_till(move_right_and_attack, third_x, third_z)    

    move_till(move_forward_and_attack, fourth_x, fourth_z)
    

def main():
    while True:
        ms.execute("warp garden")      
        time.sleep(3.0)  
        ms.player_set_orientation(YAW, PITCH)

        route_loop(-74, -238, -74, 238, -78, 238, -77, -238, -81, -238)

        route_loop(-81, -238, -80, 238, -84, 238, -83, -238, -87, -238)

        route_loop(-87, -238, -86, 238, -90, 238, -89, -238, -93, -238)

        route_loop(-93, -238, -92, 238, -96, 238, -95, -238, -99, -238)
        
        move_till(move_backward_and_attack, -98, 238)        
        

if __name__ == "__main__":
    main()
    