import minescript as ms
import time
from farming_utils import stop_movement_and_attack, exit_fun, move_forward_and_attack, move_left_and_attack, move_right_and_attack, move_downward,move_upward, check_farming_conditions

YAW, PITCH = 90, 5.35

# ACCEPTABLE_DISPLACEMENT=1        

def move_till(movement_fun, dest_x, dest_z, dest_y = -999, ACCEPTABLE_DISPLACEMENT = 1):
    movement_fun()
    while True:
        check_farming_conditions(YAW, PITCH, dest_y, ACCEPTABLE_DISPLACEMENT)
        x, y, z = ms.player_position()        
        if int(x) == dest_x and int(z) == dest_z:
            stop_movement_and_attack()
            break

def route_loop(common_x, start_z, end_z, init_y, first_y):
    x, _, z = ms.player_position()
    if int(x) != common_x and int(z) != start_z:        
        exit_fun("Not the correct starting position!")
        
    move_left_and_attack()
    time.sleep(2)
    move_forward_and_attack()    
    time.sleep(1)
    move_upward()
    time.sleep(0.2)
    stop_movement_and_attack()

    move_till(move_left_and_attack, common_x, end_z, init_y, 2)
    
    move_left_and_attack()
    time.sleep(1)
    move_downward()
    time.sleep(1.5)
    stop_movement_and_attack()

    move_right_and_attack()   
    time.sleep(1)
    move_forward_and_attack()        
    move_upward()
    time.sleep(0.3)
    stop_movement_and_attack()

    move_till(move_right_and_attack, common_x, start_z, first_y, 2)    

    move_right_and_attack()
    time.sleep(1)
    move_downward()
    time.sleep(1.5)
    stop_movement_and_attack()            
    

def main():
    start_z, end_z = -238, 238
    common_x = -66
    while True:
        ms.execute("warp garden")    
        time.sleep(2.0)  
        ms.player_set_orientation(YAW, PITCH)  
        ms.player_press_forward(True)
        time.sleep(2.0)  
        ms.player_press_forward(False)        
                
        route_loop(common_x, start_z, end_z , 75, 73)

        route_loop(common_x, start_z, end_z, 71, 69)
        
        move_till(move_left_and_attack, common_x , 238, 67)        
        

if __name__ == "__main__":
    main()
    