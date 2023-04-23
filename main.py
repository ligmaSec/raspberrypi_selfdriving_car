from sensors.Ultrasonic import Ultrasonic
from sensors.Infrared import Infrared
from sensors.Rgbsensor import Rgbsensor
from motors.DCmotor import DCmotor
from motors.Servo import Servo
from threading import Thread
import RPi.GPIO as g
import time
lapCount = 3
#
class CarController:
    def __init__(self, left_sensor, right_sensor, front_sensor,ir_sensor, rgb_sensor, motor, servo):
        self.left_sensor = left_sensor
        self.right_sensor = right_sensor
        self.front_sensor = front_sensor
        self.ir_sensor = ir_sensor
        self.rgb_sensor = rgb_sensor
        self.motor = motor
        self.servo = servo
        self.speed = 35
        self.speed_error = 0
        self.finish_counter = 0
        self.started = False

    def run(self):
        while self.finish_counter < lapCount: # finish line detection not yet implemented, feel free to use sensors.Infrared class
            left_dist = self.left_sensor.distance()
            right_dist = self.right_sensor.distance()
            front_dist = self.front_sensor.distance()
            
            left_error =  left_dist - 20 # 20 cm on each side, feel free to change this
            right_error = right_dist - 20

            if not self.started:
                is_green = self.rgb_sensor.is_green()
                if is_green:
                    print("Green light detected, starting the car")
                    self.started = True
                else:
                    print("Waiting for green light ...")
                    time.sleep(1)
                    continue

            if front_dist < 20: 
                self.kp = 5  # steering angle multiplicator when close to an obstacle
                target_speed = 25 # slowing the car down as well, to counter inertia
            else:
                self.kp = 2 # steering angle multiplicator in normal situation
                target_speed = 35 # speed in normal situation
            steering_angle = int(self.kp * (left_error - right_error)) 

            # Adjust the servo position based on the steering angle
            current_position = 127 + steering_angle
            current_position = max(0, min(255, current_position))
            self.servo.turn(current_position)


            self.speed_error = target_speed - self.speed
            self.speed += self.speed_error / 10  # Adjust speed gradually

            self.motor.forwardWithSpeed(int(self.speed))


g.cleanup() # Clean up GPIO pins

ultrasonD = Ultrasonic(9, 11)
ultrasonG = Ultrasonic(19, 26)
ultrasonF = Ultrasonic(5, 6)
ir_sensor = Infrared(20)
rgb_sensor = Rgbsensor()
motor = DCmotor()
servo = Servo()

controller = CarController(ultrasonG, ultrasonD, ultrasonF,ir_sensor, rgb_sensor, motor, servo) # Passed all four parameters

car_thread = Thread(target=controller.run)
try:
    car_thread.daemon = True
    car_thread.start()
    while True:
        time.sleep(10)
except:
    motor.setSpeed(0)


