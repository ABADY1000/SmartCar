import time
try:
    import hardware_control
    hardware_control.turn_on(debugging=True, calibrate_first=True)
    time.sleep(1000)
    while False:
        angle = input("Enter the angle\n")
        if angle == 'i':
            print ("\nCurrent_Angle: {}".format(hardware_control.current_angle))
            print ("Wanted_Angle: {}".format(hardware_control.wanted_angle))
            print ("Current_Point: {}".format(hardware_control.current_point))
            print ("Wanted_Point: {}".format(hardware_control.wanted_point))
        else:
            hardware_control.rotate_to_angle(angle)
except (KeyboardInterrupt, SystemExit):
    print("Shutting down!")
    hardware_control.turn_off()
except:
    print("An unexpected error has occured. Shutting down!")
    hardware_control.turn_off()
    raise
