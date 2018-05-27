import gpiozero.output_devices as od
import gpiozero.input_devices as id
import threading
from geometry_2d import *
import time

# Constants
angle_threshold = 5
location_threshold = 5
speed_step = 0.02

# Motors
speed_factors = {'left_max': 1, 'left_min': 0.3, 'right_max': 1, 'right_min': 0.3}
speed_factor_pairs = []
response_time = 0.5
left_motor = od.Motor(14, 15, pwm=True)
right_motor = od.Motor(20, 21, pwm=True)

# Sensors
ldr = id.DigitalInputDevice(0)
length_moved_per_pulse = 0.01  # 1cm
proximity_sensors = {'Front': id.DigitalInputDevice(0), 'Right': id.DigitalInputDevice(0),
                     'Left': id.DigitalInputDevice(0)}
# Variables
debug = False
running = False
current_point = (0, 0)
current_angle = 0
wanted_point = (0, 0)
wanted_angle = 0


def move_forward(distance):
    global wanted_point
    p = to_cartesian(distance, wanted_angle)
    wanted_point = wanted_point[0] + p[0], wanted_point[1] + p[1]


def move_backward(distance):
    global wanted_point
    p = to_cartesian(distance, wanted_angle)
    wanted_point = wanted_point[0] - p[0], wanted_point[1] - p[1]


def move_to_point(x, y):
    global wanted_point
    wanted_point = x, y


def stop():
    global wanted_point, wanted_angle
    wanted_point = current_point
    wanted_angle = current_angle


def calibrate():
    global response_time, speed_factor_pairs, speed_factors
    if not current_angle_updater_thread.is_alive():
        raise RuntimeError('Cannot calibrate before starting the angle updater thread')
    speed_control_lock.acquire()
    cbegin = time.perf_counter()
    lprint("Calibrating...")
    right_motor.stop()
    left_motor.stop()
    lprint("Computing maximum motor-sensor response time")
    values = []
    for motor in [right_motor,left_motor]:
        for i in range(3):
            current_angle_change_event.clear()
            begin = time.perf_counter()
            motor.forward(1)
            current_angle_change_event.wait()
            values += [time.perf_counter() - begin]
            motor.stop()
            response_time = max(values)
            time.sleep(response_time)
    lprint("= {}ms".format(response_time))

    def min_speed_factor(motor, upper_bound, lower_bound):
        for i in range(5):
            mid_point = (upper_bound+lower_bound)/2
            motor.forward(mid_point)
            current_angle_change_event.clear()
            if current_angle_change_event.wait(response_time):
                upper_bound = mid_point
            else:
                lower_bound = mid_point
        motor.stop()
        return upper_bound # The safer boundary
    lprint("Computing minimum speed factor for right motor")
    speed_factors['right_min'] = min_speed_factor(right_motor, speed_factors['right_max'], 0)
    lprint('= {}'.format(speed_factors['right_min']))
    lprint("Computing minimum speed factor for left motor")
    speed_factors['left_min'] = min_speed_factor(left_motor, speed_factors['left_max'], 0)
    lprint('= {}'.format(speed_factors['left_min']))

    lprint("Computing speed differences between motors")
    for o in 0, 1:
        for i in numpy.arange(1, max(speed_factors['right_min'],speed_factors['left_min']), -0.1):
            if o == 0:
                right_motor.forward(i)
                left_motor.forward(i)
            else:
                right_motor.backward(i)
                left_motor.backward(i)
            while True:
                current_angle_change_event.clear()
                angle = current_angle
                if current_angle_change_event.wait(response_time * 2):
                    if angle > current_angle:  # Rotating clockwise
                        if o == 0:
                            left_motor.forward(left_motor.value() - speed_step)
                        else:
                            right_motor.backward(left_motor.value() - speed_step)

                    else:  # Rotating counter clockwise
                        if o == 0:
                            right_motor.forward(left_motor.value() - speed_step)
                        else:
                            left_motor.backward(left_motor.value() - speed_step)
                else:
                    speed_factor_pairs += [(left_motor.value(), right_motor.value())]
                    break
    lprint("= {}".format(speed_factor_pairs))
    a = tuple(zip(*speed_factor_pairs))
    lm, rm = max(a[0]), max(a[1])
    speed_factors['left_max'] = lm
    speed_factors['right_max'] = rm
    lprint("Finished calibrating in {}ms".format(time.perf_counter() - cbegin))
    speed_control_lock.release()


def get_proximity_readings():
    readings = {}
    if proximity_sensors['Front'].is_active():
        readings['Front'] = 0.1
    if proximity_sensors['Right'].is_active():
        readings['Right'] = 0.02
    if proximity_sensors['Left'].is_active():
        readings['Left'] = 0.02
    return readings


def speed_control():
    global current_angle, wanted_angle
    while running:
        time.sleep(response_time)
        speed_control_lock.acquire()
        wanted_angle = get_angle(wanted_point, current_point, principal=False)
        angle_dif = abs(principal_angle(wanted_angle) - principal_angle(current_angle))
        match_point = get_length((wanted_point, current_point)) >= location_threshold
        # If the difference was high Or if we arrived at wanted_point then stop and correct the angle
        if angle_dif > angle_threshold * 4 or (not match_point and angle_dif > angle_threshold):
            lprint('Big angle difference stopping and correcting')
            if angle_dif > 90:
                rs = speed_factors['right_max']
                ls = speed_factors['left_max']
            elif angle_dif > 45:
                rs = (speed_factors['right_max'] + speed_factors['right_min']) / 2
                ls = (speed_factors['left_max'] + speed_factors['left_min']) / 2
            else:
                rs = speed_factors['right_min']
                ls = speed_factors['left_min']
            if current_angle > wanted_angle:
                left_motor.forward(ls)
                right_motor.backward(rs)
            else:
                left_motor.backward(ls)
                right_motor.forward(rs)
        # If there is a small angle difference but we still need to get to a point then correct it as the car is moving
        elif angle_dif > angle_threshold and match_point:
            lprint('Small angle difference while moving to point. Correcting ls={} rs{}'.format(left_motor.value(),right_motor.value()))
            if current_angle > wanted_angle:
                if right_motor.value() <= 0 or left_motor.value <= 0:
                    right_motor.forward(speed_factors['right_max'])
                    left_motor.forward(speed_factors['left_max'] - speed_step)
                else:
                    if left_motor + speed_step < speed_factors['left_max']:
                        left_motor.forward(left_motor.value() + speed_step)
                    else:
                        right_motor.forward(right_motor.value() - speed_step)
            else:
                if right_motor.value() <= 0 or left_motor.value <= 0:
                    right_motor.forward(speed_factors['right_max'] - speed_step)
                    left_motor.forward(speed_factors['left_max'])
                else:
                    if right_motor + speed_step < speed_factors['right_max']:
                        right_motor.forward(right_motor.value() + speed_step)
                    else:
                        left_motor.forward(left_motor.value() - speed_step)

        # If the angle is okay but we need to get to the wanted_point
        elif match_point:
            lprint('Angle is okay moving to wanted point')
            if right_motor.value() <= 0 or left_motor.value <= 0:
                right_motor.forward(speed_factors['right_max'])
                left_motor.forward(speed_factors['left_max'])
        # If we arrived at wanted_point and wanted_angle then stop
        else:
            right_motor.stop()
            left_motor.stop()
        speed_control_lock.release()
    lprint('speed_control thread is exiting.')


def current_angle_updater():
    event_current_angle = current_angle
    while running:
        time.sleep(0.1)
        current_angle_change_event.set()
    lprint('current_angle_updater thread is exiting')


def current_point_updater():
    while running:
        global current_point
        ldr.wait_for_active()
        # Only update the current_point if the car is not turning
        if left_motor.value() > 0 and right_motor.value > 0:
            p = to_cartesian(length_moved_per_pulse, current_angle)
            current_point = current_point[0] + p[0], current_point[1] + p[1]
        current_point_change_event.set()
        ldr.wait_for_inactive()  # We may not need this !!!
    lprint('current_point_updater thread is exiting')


speed_control_thread = threading.Thread(name='speed_control', target=speed_control)
speed_control_lock = threading.RLock()
current_angle_updater_thread = threading.Thread(name='current_angle_updater', target=current_angle_updater)
current_angle_change_event = threading.Event()
current_point_updater_thread = threading.Thread(name='current_point_updater', target=current_point_updater)
current_point_change_event = threading.Event()


def turn_on(calibrate_first=False, debugging=False):
    global running, debug
    debug = debugging
    running = True
    current_angle_updater_thread.start()
    if calibrate_first:
        calibrate()
    current_point_updater_thread.start()
    speed_control_thread.start()


def turn_off():
    global running
    running = False
    right_motor.stop()
    left_motor.stop()


def lprint(msg):
    if debug:
        print(msg)
