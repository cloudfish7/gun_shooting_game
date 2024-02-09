from machine import Pin,I2C
from DFPModule import DFPlayer
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
import time
import random
import _thread

class Target:
    def __init__(self, led_pin_no, receiver_pin_no, sound_track_no):
        self.led = Pin(led_pin_no, Pin.OUT) 
        self.receiver = Pin(receiver_pin_no, Pin.IN)
        self.sound_track_no = sound_track_no


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

# DFPlayer
player = DFPlayer(8, 9, 10)
sound_set = {"start" : 1}

target_pin_list = [
    [2, 3, 5],
    [4, 5, 5],
]

# Game Status
ENEMY_COUNT = 2
GAME_TIME = 10 
is_start = False
is_game_running = False
score = 0

def get_rand_ind():
    return random.randint(0, ENEMY_COUNT - 1)

def next_target(current_target, previous_target):
    current_target = get_rand_ind()
    while True:
        if current_target == previous_target:
            current_target = get_rand_ind()
        else:
            break
    return current_target

def get_lcd(i2c):

    return I2cLcd(i2c, I2C_ADDR, LCD_ROWS, LCD_COLUMNS)

def show_title(i2c):

    global is_start
    lcd = get_lcd(i2c)

    # if game start, break loop
    while not is_start:
        lcd.putstr("   Shoot Here")
        time.sleep(1)
        lcd.clear()
        time.sleep(1)

def start_game(start_receiver, i2c):

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

            
            #lcd.putstr("  Game Start!!\n  Shoot Here")
            lcd.putstr("  Game Start!!")
            time.sleep(2)
            for i in range(3, 1, -1):
                lcd.clear()
                lcd.putstr("       " + str(i)) 
                time.sleep(1)

            lcd.clear()
            is_game_running = True
       
            break


# Game time gauge
def display_gauge(i2c, gauge_count):

    global is_game_running

    lcd = get_lcd(i2c)
    lcd.custom_char(0, custom_char)

    for i in range(gauge_count, 0, -1):
        lcd.clear()
        time.sleep(1)
        gauge_bar = chr(0) * i 
        lcd.putstr(gauge_bar + "\nSCORE " + str(score) ) 
        # play sound
        #player.play(sound_set["start"])
        time.sleep(1)

    is_game_running = False


def display_finish(i2c):

    lcd = get_lcd(i2c)
    # play finish sound
    #player.play(sound_set["start"])
    for i in range(3, 0, -1):
        lcd.clear()
        time.sleep(1)
        lcd.putstr("  Game Finish!!")
        time.sleep(1)
    lcd.clear()

def display_result(i2c):

    lcd = get_lcd(i2c)
    # LEVEL JUDGE
    for i in range(3, 0, -1):
        lcd.clear()
        time.sleep(1)
        lcd.putstr("   SCORE " + str(score))
        # play sound
        #player.play(sound_set["start"])
        time.sleep(1)
    lcd.clear()

def main():

    global is_game_running
    global is_start
    global score
    target_object = {}
    i2c=machine.I2C(1,sda=sda, scl=scl, freq=100000)

    start_receiver = Pin(16, Pin.IN)

    # initialize
    for index, row in enumerate(target_pin_list):
        target_object[index] = Target(row[0], row[1], row[2])

    while True:

        is_game_running = False
        is_start = False
        score = 0

        for k, v in target_object.items():
            v.led.off()
   
        # before start
        start_game(start_receiver, i2c)

        _thread.start_new_thread(display_gauge, (i2c, GAME_TIME))

        current_target = previous_target = get_rand_ind()
        target_object[current_target].led.on()
        print(f"current_target: {current_target}")

        # Main loop
        while is_game_running:

            for k, v in target_object.items():
                if v.receiver.value() == 0 and k == current_target:
                    print(f"Hit {current_target}!")
                    player.play(target_object[current_target].sound_track_no)
                    target_object[current_target].led.off()
                    score += 1

                    current_target = previous_target = next_target(current_target, previous_target)
                    target_object[current_target].led.on()

                    time.sleep(0.1)

        display_finish(i2c)

        display_result(i2c)
        time.sleep(2)

if __name__ == "__main__":
    main()