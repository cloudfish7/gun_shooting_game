import machine
import utime

# --- DFPlayerの使い方 ---
# microSDカード直下に"mp3"という名称のフォルダを作成し"0001.mp3"のような連番でファイルを格納しておく。
# 第1引数でTXピン番号、第2引数でRXピン番号を指定する。
# 第3引数（オプション）でボリューム値を指定をする場合は、0〜30までの数値で指定する。デフォルト値は15。

def add_numbers(a, b):
    return a + b

THIS_VERSION = 1.0

class DFPlayer:

	def __init__(self, tx:int, rx:int, volume:int=15):
		self.uart = machine.UART(1, baudrate=9600, tx=machine.Pin(tx), rx=machine.Pin(rx))

		# sd初期化
		self._command(0x3F, 0x02)
		utime.sleep_ms(500)

		# volume設定
		self.set_volume(volume)

		print("DFPlayer initialized (ver.{})".format(THIS_VERSION))

	def _command(self, command, parameter=0x00):
		query = bytes([0x7e, 0xFF, 0x06, command, 0x00, 0x00, parameter, 0xEF])
		self.uart.write(query)

	# 以下、制御メソッド

	def set_volume(self, volume:int):
		self._command(0x06, volume)
		print("Volume: {}".format(volume))
		utime.sleep_ms(500)

	def play(self, num:int):
		self._command(0x12, num)
		print("Play: {}".format(num))
		utime.sleep_ms(500)

	def repeat(self):
		self._command(0x08)
		print("Repeat ON")
		utime.sleep_ms(500)

	def pause(self):
		self._command(0x0E)
		print("Pause")
		utime.sleep_ms(500)

	def resume(self):
		self._command(0x0D)
		print("Resume")
		utime.sleep_ms(500)

	def stop(self):
		self._command(0x16)
		print("Stop / Repeat OFF")
		utime.sleep_ms(500)