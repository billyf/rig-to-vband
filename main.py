import audioop
import platform
import signal
from enum import Enum

import pyaudio

AUDIO_THRESHOLD = 50
"""A RMS value above this will signify that the key is being pressed.
For the Icom 7300, the value when not pressed hovers around 1 on Linux and 6-10 on Windows.
Tweak to match your soundcard (you can view the realtime values by setting PRINT_RMS_VALUES=True)
"""

PRINT_RMS_VALUES = False
"""For debugging; prints the RMS values which AUDIO_THRESHOLD depends on"""

USB_NAME_TEXT = "USB Audio CODEC"
"""We search for this name among our device list to find the radio's microphone entry"""

if platform.system() == 'Windows':
    # pyautogui wasn't working correctly with Windows + Chrome; the KeyboardEvent.code value is empty.
    # Keys would get sent to the text input box but JS checks for 'code' value for keydown
    import pydirectinput
    keyboard = pydirectinput

    KYBD_KEY = 'ctrl'

    def send_key_down():
        keyboard.keyDown(KYBD_KEY)

    def send_key_up():
        keyboard.keyUp(KYBD_KEY)
else:
    from pynput.keyboard import Key, Controller
    keyboard = Controller()

    KYBD_KEY = Key.ctrl

    def send_key_down():
        keyboard.press(KYBD_KEY)

    def send_key_up():
        keyboard.release(KYBD_KEY)

    # TODO also try with a Mac

PRINT_KEYING = False
"""For debugging; prints the key states to the console"""

NUM_FRAMES = 128
"""Buffer size for reading the audio stream"""

EXCEPTION_ON_OVERFLOW = False


class KeyState(Enum):
    """Represents a straight key being held down (even if it came from a paddle - means sidetone is audible from rig)"""
    OFF = 0
    DOWN = 1


def print_key_state(c: str):
    if PRINT_KEYING:
        if c == '/':
            print()
        print(c, end='')
        if c == '\\':
            print()


class RigAudioListener:
    audio_format = pyaudio.paInt16  # 16-bit resolution
    channels = 1                    # 1 channel
    sample_rate = 44100             # 44.1kHz sampling rate

    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.device_index = self.find_device_index()
        if self.device_index == -1:
            self.cleanup()

        # pydirectinput has a 0.1 second pause by default
        if hasattr(keyboard, "PAUSE"):
            keyboard.PAUSE = 0

    def find_device_index(self) -> int:
        """Returns -1 when device is not found"""
        print(f"Looking for audio device name containing '{USB_NAME_TEXT}'...")
        for device_index in range(self.audio.get_device_count()):
            device = self.audio.get_device_info_by_index(device_index)
            name = device.get("name")
            max_input_channels = device.get("maxInputChannels")  # to find the microphone device, not the speaker
            print(device_index, name, max_input_channels)
            if name.find(USB_NAME_TEXT) != -1 and max_input_channels > 0:
                print("Using audio device:")
                print(device)
                return device_index
                # this picks the first matching one, there could be others
        print("ERROR: Didn't find audio device!")
        return -1

    def listen(self):
        try:
            self.stream = self.audio.open(format=self.audio_format, rate=self.sample_rate, channels=self.channels,
                                          input_device_index=self.device_index, input=True,
                                          frames_per_buffer=NUM_FRAMES)
        except OSError as ose:
            print("ERROR: Problem opening stream; is something else using the device?", ose)
            self.cleanup()

        signal.signal(signal.SIGINT, self.handle_stop)

        print()
        print("Listening; switch to VBand/Vail tab now (Ctrl-C to quit)")

        prev_state = KeyState.OFF

        while True:
            data = self.stream.read(NUM_FRAMES, exception_on_overflow=EXCEPTION_ON_OVERFLOW)

            rms = audioop.rms(data, 2)
            if PRINT_RMS_VALUES:
                print(rms)

            if rms > AUDIO_THRESHOLD:
                if prev_state == KeyState.OFF:
                    # started keying
                    print_key_state("/")
                    send_key_down()
                else:
                    print_key_state("X")
                prev_state = KeyState.DOWN
            else:
                if prev_state == KeyState.DOWN:
                    # stopped keying
                    print_key_state("\\")
                    send_key_up()
                else:
                    print_key_state(".")
                prev_state = KeyState.OFF

    def handle_stop(self, *_):
        """Called when app is closing (SIGINT)"""
        self.cleanup()

    def cleanup(self):
        print()
        print("Cleaning up resources...")
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()
        # making sure to release the key when finishing
        send_key_up()

        print("Exiting")
        exit(0)


if __name__ == '__main__':
    listener = RigAudioListener()
    listener.listen()
