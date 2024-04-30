from simple_pid import PID
import RPi.GPIO as GPIO
from hx711 import HX711
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from multiprocessing import Process, Pipe, Value
import ctypes

# Stepper motor config
STEP_PIN = 18  
DIR_PIN = 21  
STEPS_PER_REVOLUTION = 200
RPM_MAX = 550  # Adjust -- 320 is gussed RPM 
RPM_CEIL = 1
def setup_hx711():
    GPIO.setmode(GPIO.BCM)
    hx = HX711(dout_pin=9, pd_sck_pin=11)
    print('Taring Scale... Please Wait')
    hx.zero(readings=10)
    hx.set_scale_ratio(2150)  #2150 was tested during calibration code 
    return hx

def convert_to_newtons(value):
    return value * 0.0098  # conversion factor for grams to newtons

def setup_stepper():
    GPIO.setup(STEP_PIN, GPIO.OUT)
    GPIO.setup(DIR_PIN, GPIO.OUT)

def stepper_motor_controller(conn, motor_speed_shared):
    setup_stepper()
    pid = PID(1.01, 0.0, 0.05, setpoint=2)  # Adjust these PID values based on testing
    pid.sample_time = 0.01   

    last_step_time = time.time()
    step_interval = float('inf')

    while True:
        current_time = time.time()

        # Read new tension value and update PID output at regular intervals
        if conn.poll():
            tension_value_newtons = conn.recv()
            pid_output = pid(tension_value_newtons)
            
            if pid_output > 0: 
                rpm = (pid_output / 2.0) * RPM_MAX * RPM_CEIL  # Adjust the PID output to RPM scaling -- Maybe lower RPM? or change PID
            else:
                rpm = (pid_output / 2.0) * RPM_MAX

            rpm = max(min(rpm, RPM_MAX), -RPM_MAX)
            motor_speed_shared.value = rpm

            steps_per_second = abs(rpm) * STEPS_PER_REVOLUTION / 60
            step_interval = 1 / steps_per_second if steps_per_second > 0 else float('inf')

        # Step the motor based on calculated interval
        if current_time - last_step_time >= step_interval:
            GPIO.output(DIR_PIN, GPIO.HIGH if rpm >= 0 else GPIO.LOW)
            GPIO.output(STEP_PIN, GPIO.HIGH)
            time.sleep(0.0001)  # Pulse width for the step signal
            GPIO.output(STEP_PIN, GPIO.LOW)

            last_step_time = current_time

def init_plot():
    global line1, line2
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    line1, = ax1.plot([], [], '-')
    line2, = ax2.plot([], [], '-')
    ax1.set_ylim(0, 5)
    ax1.set_xlim(-15, 0)
    ax2.set_ylim(-RPM_MAX, RPM_MAX)
    ax1.set_ylabel('Tension (Newtons)')
    ax2.set_ylabel('Motor Speed (RPM)')
    ax2.set_xlabel('Elapsed Time (Seconds)')
    return fig, ax1, ax2

def init():
    line1.set_data([], [])
    line2.set_data([], [])
    return line1, line2

def main():
    global line1, line2
    GPIO.setwarnings(False)
    GPIO.cleanup()  
    hx = setup_hx711()

    start_time = time.time()
    elapsed_times = []
    values = []
    motor_speeds = []

    fig, ax1, ax2 = init_plot()

    motor_speed_shared = Value(ctypes.c_double, 0.0)
    parent_conn, child_conn = Pipe()
    motor_proc = Process(target=stepper_motor_controller, args=(child_conn, motor_speed_shared))
    motor_proc.start()

    def update(frame):
        nonlocal start_time, elapsed_times, values, motor_speeds
        current_time = time.time() - start_time
        elapsed_times.append(current_time)

        raw_value = hx.get_weight_mean(readings=1)
        tension_value = convert_to_newtons(raw_value)
        parent_conn.send(tension_value)

        values.append(tension_value)
        motor_speeds.append(motor_speed_shared.value)

        while elapsed_times and elapsed_times[0] < current_time - 15:
            elapsed_times.pop(0)
            values.pop(0)
            motor_speeds.pop(0)

        line1.set_data(elapsed_times, values)
        line2.set_data(elapsed_times, motor_speeds)
        ax1.set_xlim(min(elapsed_times), max(elapsed_times))
        ax2.set_xlim(min(elapsed_times), max(elapsed_times))
        ax1.relim()
        ax1.autoscale_view()
        ax2.relim()
        ax2.autoscale_view()

        return line1, line2

    ani = FuncAnimation(fig, update, init_func=init, blit=True, interval=100)
    plt.show()

    motor_proc.terminate()
    motor_proc.join()
    GPIO.cleanup()

if __name__ == '__main__':
    main()

