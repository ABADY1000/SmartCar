try:
    import hardware_control
    hardware_control.turn_on()
    while True:
        point = input("Enter the point to go to")
        hardware_control.move_to_point(point)
except (KeyboardInterrupt, SystemExit):
    print("Shutting down!")
    hardware_control.turn_off()
except:
    print("An unexpected error has occured. Shutting down!")
    hardware_control.turn_off()
    raise
