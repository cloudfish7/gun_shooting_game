from machine import Pin,I2C,PWM,Timer
from DFPModule import DFPlayer
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
from pca9685 import PCA9685
from servo import Servos
import time
import random
import _thread

class Target:

    def __init__(self, target):

        #angle_0 = int(2.5 / 20 * 65536)
        #angle_75 = int(2.0 / 20 * 65536)
        #angle_90 = int(1.5 / 20 * 65536)
        #angle_150 = int(1.0 / 20 * 65536)
        #angle_180 = int(0.5 / 20 * 65536)

        if target["servo_flag"]  == False:
            self.led = Pin(target["led_pin_no"], Pin.OUT) 
            self.servo_flag = False
        else:
            self.servo_flag = True
            self.servo_index = target["servo_index"]
            self.servo_interval = target["servo_interval"]
            self.servo_angle_start = 75
            self.servo_angle_end = 150
            self.position_flag = 0

        self.receiver = Pin(target["receiver_pin_no"], Pin.IN)
        self.sound_track_no = target["sound_track_no"]


# LCD
I2C_ADDR = 0x27
LCD_COLUMNS = 16
LCD_ROWS = 2
sda=machine.Pin(26)
scl=machine.Pin(27)
custom_char = (
    0b11111,
    0b11111,
    0b11111,
    0b11111,
    0b11111,
    0b11111,
    0b11111,
    0b11111,
)

# Servo Driver
SERVO_SDA_PIN = 0
SERVO_SCL_PIN = 1
SERVO_ID = 0
servo_driver = None

# DFPlayer
VOLUME = 25
player = DFPlayer(8, 9, VOLUME)
sound_set = {
    "start" : 1,
    "start_countdown" : 2,
    "count" : 3,
    "game_finish" : 4,
    "result_show" : 5,
}

# Servo
ServoTimer   = Timer()

target_pin_list = {
    # Ghost
    0: {
        "servo_flag": False,
        "led_pin_no": 4,
        "receiver_pin_no": 5,
        "sound_track_no": 8,
    },
    # Slime
    1: { 
        "servo_flag": False,
        "led_pin_no": 14,
        "receiver_pin_no": 15,
        "sound_track_no": 8,
    },
    # Demon King
    2: { 
        "servo_flag": False,
        "led_pin_no": 22,
        "receiver_pin_no": 21,
        "sound_track_no": 8,
    },
    # Dragon
    3: { 
        "servo_flag": False,
        "led_pin_no": 19,
        "receiver_pin_no": 18,
        "sound_track_no": 8,
    },
    # Harpy
    4: { 
        "servo_flag": True,
        "servo_index": 0,
        "servo_interval": 2000,
        "receiver_pin_no": 28,
        "sound_track_no": 8,
    },
    # XXXX
    5: { 
        "servo_flag": True,
        "servo_index": 1,
        "servo_interval": 1500,
        "receiver_pin_no": 20,
        "sound_track_no": 8,
    },

}

target_object = {}

# Game Status
ENEMY_COUNT = len(target_pin_list)
GAME_TIME = 20 
is_start = False
is_game_running = False
#is_target_moving =False
is_playing = Pin(17, Pin.IN)
score = 0

def play_sound(track_no):

    while True:
        if is_playing.value() == 1:
            player.play(track_no)
            break
        time.sleep(0.1) 

def get_rand_ind():
    return random.randint(0, ENEMY_COUNT - 1)

def next_target(current_target, previous_target):
    ## For Servo Test
    #current_target = 5
    #return current_target

    current_target = get_rand_ind()
    while True:
        if current_target == previous_target:
            current_target = get_rand_ind()
        else:
            break
    return current_target

def get_lcd(i2c):

    return I2cLcd(i2c, I2C_ADDR, LCD_ROWS, LCD_COLUMNS)

def show_title(i2c) -> None:

    global is_start
    lcd = get_lcd(i2c)

    # if game start, break loop
    while not is_start:
        lcd.putstr("   Shoot Here")
        time.sleep(1)
        lcd.clear()
        time.sleep(1)

def start_game(start_receiver, i2c) -> None:

    global is_start
    global is_game_running

    lcd = get_lcd(i2c)

    _thread.start_new_thread(show_title, (i2c,))

    # start Game
    while True:
        if start_receiver.value() == 0:
            is_start = True
            lcd.clear()
            print("start!")
            player.play(sound_set["start"])

            lcd.putstr("  Game Start!!")
            time.sleep(2)
            # play count down
            player.play(sound_set["start_countdown"])
            for i in range(3, 1, -1):
                lcd.clear()
                lcd.putstr("       " + str(i)) 
                time.sleep(1)

            lcd.clear()
            is_game_running = True
       
            break

# time gauge
def display_gauge(i2c, gauge_count) -> None:

    global is_game_running

    lcd = get_lcd(i2c)
    lcd.custom_char(0, custom_char)

    for i in range(gauge_count, 0, -1):
        lcd.clear()
        time.sleep(1)
        gauge_bar = chr(0) * i 
        lcd.putstr(gauge_bar + "\nSCORE " + str(score) ) 
        # play sound
        if i <= 3:
            #player.play(sound_set["count"])
            play_sound(sound_set["count"])
        time.sleep(1)

        if i == 1:
            ServoTimer.deinit()

    is_game_running = False

def get_servo_driver():

    global servo_driver

    if servo_driver is None:
        i2c = I2C(id=SERVO_ID, sda=SERVO_SDA_PIN, scl=SERVO_SCL_PIN)
        #pca = PCA9685(i2c=i2c)
        servo_driver = Servos(i2c=i2c)

    return servo_driver

def move_servo(p) -> None:
    _move_servo()

def _move_servo() -> None:

    global current_target
    global target_object
    target = target_object[current_target]
    print("move servo")

    servo_driver = get_servo_driver()

    if target.position_flag == 0:
        servo_driver.position(index=target.servo_index, degrees=target.servo_angle_start)
        target.position_flag = 1
    else:
        servo_driver.position(index=target.servo_index, degrees=target.servo_angle_end)
        target.position_flag = 0
    time.sleep(1)


def show_next_target(target: Target) -> None:
    global current_target
    if target.servo_flag == True:
        # can't run more than one threads
        #_thread.start_new_thread(move_target, (target, ))
        #move_servo(target.servo)
        _move_servo()
        ServoTimer.init(period=target.servo_interval,  mode=Timer.PERIODIC, callback=move_servo )

        #target.receiver.irq(trigger = Pin.IRQ_FALLING, handler = hit_laser)
        #target.servo_moving_flag = True

    else:
        target.led.on()

def display_finish(i2c) -> None:

    lcd = get_lcd(i2c)
    # play finish sound
    player.play(sound_set["game_finish"])
    for i in range(2, 0, -1):
        lcd.clear()
        time.sleep(1)
        lcd.putstr("  Game Finish!!")
        time.sleep(1)
    ServoTimer.deinit()
    lcd.clear()

def display_result(i2c) -> None:

    lcd = get_lcd(i2c)
    # play sound
    player.play(sound_set["result_show"])
    # LEVEL JUDGE
    for i in range(3, 0, -1):
        lcd.clear()
        time.sleep(1)
        lcd.putstr("   SCORE " + str(score))
        time.sleep(1)
    lcd.clear()

def main():

    global is_game_running
    global is_start
    global score
    global target_object
    global current_target
    i2c=machine.I2C(1,sda=sda, scl=scl, freq=100000)

    start_receiver = Pin(16, Pin.IN)

    # initialize
    for index, target in target_pin_list.items():
        target_object[index] = Target(target)

    while True:

        is_game_running = False
        is_start = False
        score = 0

        for k, v in target_object.items():
            if v.servo_flag == False:
                v.led.off()
   
        # before start
        start_game(start_receiver, i2c)

        _thread.start_new_thread(display_gauge, (i2c, GAME_TIME))

        current_target = previous_target = -1
        current_target = previous_target = next_target(current_target, previous_target)
        show_next_target(target_object[current_target])
        print(f"current_target: {current_target}")

        # Main loop
        while is_game_running:

            for k, v in target_object.items():
                if v.receiver.value() == 0 and k == current_target:
                    print(f"Hit {current_target}!")
                    play_sound(target_object[current_target].sound_track_no)
                    if target_object[current_target].servo_flag == True:
                        ServoTimer.deinit()
                    else:
                        target_object[current_target].led.off()

                    score += 1

                    current_target = previous_target = next_target(current_target, previous_target)
                    show_next_target(target_object[current_target])

                    time.sleep(0.1)

        display_finish(i2c)

        display_result(i2c)
        time.sleep(2)

if __name__ == "__main__":
    main()