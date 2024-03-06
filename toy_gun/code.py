import time
import board
import audiomp3
import audiopwmio
import digitalio

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
#led.value = True 

motor = digitalio.DigitalInOut(board.GP20)
motor.direction = digitalio.Direction.OUTPUT

audio = audiopwmio.PWMAudioOut(board.GP16)

def play_sound():
    sound_file = "./mp3/gunshot.mp3"
    sound_file = "./mp3/beem.mp3"
    sound_file = "./mp3/machinegun.mp3"
    sound_file = "./mp3/laser_16khz.mp3"
    decoder = audiomp3.MP3Decoder(open(sound_file, "rb"))
    audio.play(decoder)

def on_interrupt(pin):
    global motor
    if not pin.value:  # スイッチが押されたら（LOWになったら）
        #led_pin.value = True  # LEDを点灯させる
        print("click")
        play_sound()
        motor.value = True
        time.sleep(0.5)  # 0.1秒待つ（ボタンのバウンスを防ぐため）
        motor.value = False
        #led_pin.value = False  # LEDを消す


def main():
    #led.value = True

    switch_pin = digitalio.DigitalInOut(board.GP18)
    switch_pin.direction = digitalio.Direction.INPUT
    #switch_pin_interrupt.pull = digitalio.Pull.UP  # プルアップ抵抗を有効にする
    switch_pin.pull = digitalio.Pull.DOWN


#while not audio.playing:
    motor.value = True
    time.sleep(2)
    motor.value = False
#    pass
    switch_pin_state = switch_pin.value
    while True:
        if switch_pin.value != switch_pin_state:  # スイッチの状態が変化したら
            switch_pin_state = not switch_pin_state  # スイッチの状態を更新
            if not switch_pin_state:  # スイッチが押されたら
                on_interrupt(switch_pin)  # 割り込み処理を呼び出す
        time.sleep(0.01)
        #time.sleep(1)
        #audio.play(decoder)
        #led.value = True
        #time.sleep(1)
        #led.value = False

if __name__ == "__main__":
	main()

