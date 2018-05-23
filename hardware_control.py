import gpiozero.output_devices as od
import threading
from geometry_2d import get_length
import time

# Constants
angle_threshold = 5
location_threshold = 5

left_motor = od.Motor(14, 15, pwm=True)
right_motor = od.Motor(20, 21, pwm=True)
current_point = (0, 0)
current_angle = 0
wanted_point = (0,0)
wanted_angle = 0

# Control interface


def move_forward(distance):
    pass


def move_backward(distance):
    pass


def move_to_point(point):
    pass


# Sensor readings

def get_proximity_readings():
    pass


def get_angle_reading():
    return current_angle


def update_speed_loop():
    while True:
        time.sleep(0.1)
        angle_reading = get_angle_reading()
        match_angle = abs(wanted_angle - angle_reading) >= angle_threshold
        match_point = get_length((wanted_point,current_point)) >= location_threshold
        if not match_angle and not match_point:
            if angle_reading > wanted_angle:
                right_motor.value()
            else:
                pass
        elif not match_angle:
            if angle_reading > wanted_angle:
                right_motor.forward(1)
                left_motor.backward(1)
            else:
                right_motor.backward(1)
                left_motor.forward(1)
        elif not match_point:
            pass
        else:
            right_motor.stop()
            left_motor.stop()


speed_control = threading.Thread(name='Speed_Control', target= update_speed_loop)
speed_control.start()
