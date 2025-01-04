# rig-to-vband

An app for sending CW on VBand or Vail using your key and radio (if it provides a USB soundcard).

It monitors the audio level from your radio and virtually presses the Ctrl key when it detects your sidetone (or any volume spike).

## Usage:
1. First time only:
   - Download [main.py](https://raw.githubusercontent.com/billyf/icom-vband-test/main/main.py)
   - Perform the setup steps below
2. Rotate RF/SQL knob to maximum squelch (choose a quiet band if needed)
3. Run: `python main.py`
4. Click on the VBand/Vail browser tab
5. Key your radio (with break-in turned off)

The VBand/Vail tab needs to stay in focus to receive the Ctrl key.  
Quit the app before undoing the squelch so the Ctrl key won't be triggered from band noise.

## Setup:
### VBand / Vail site
- Settings -> Mode = **Straight Key / Cootie**
- You can disable your sidetone in the channel if listening to the rig sidetone

### Radio (Icom 7300 example)
- `Menu -> Set -> Connectors -> ACC/USB AF SQL` = **ON**  
(so the radio doesn't send audio to the soundcard while the squelch is enabled)

### For other USB devices:
- Modify AUDIO_THRESHOLD for the levels on your soundcard.  
You can set `PRINT_RMS_VALUES = True` to see what they are during key up and key down.

- Modify USB_NAME_TEXT to match your device if necessary.

### Python libraries:
- **pyaudio**
- **pynput** (Linux) or **pydirectinput** (Windows)
- `python -m pip install -r requirements.txt`
