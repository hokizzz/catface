#!user/bin/env python3  
# -*- coding: gbk -*- 
import RPi.GPIO as GPIO
import time

class ServoMotor:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pin, 50)  # 50Hz
        self.pwm.start(0)

    def set_angle(self, angle):
        if 0 <= angle <= 180:
            duty = angle / 18 + 2
            GPIO.output(self.pin, True)
            self.pwm.ChangeDutyCycle(duty)
            time.sleep(0.5)  # 等待舵机移动
            GPIO.output(self.pin, False)
            self.pwm.ChangeDutyCycle(0)
        else:
            raise ValueError("角度必须在0到180之间")

    def cleanup(self):
        self.pwm.stop()
        #GPIO.cleanup()

if __name__ == "__main__":
    servo_pin = 21  # 根据实际情况设置引脚
    servo = ServoMotor(servo_pin)

    try:
        angle = float(input("请输入角度（0-180）："))
        servo.set_angle(angle)
    except KeyboardInterrupt:
        pass
    except ValueError as e:
        print(e)
    finally:
        servo.cleanup()
