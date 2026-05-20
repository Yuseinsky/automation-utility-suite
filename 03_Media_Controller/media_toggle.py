import ctypes
import time
import sys

sys.stdout.reconfigure(errors='replace')

print("⏸️ Sending VK_MEDIA_PLAY_PAUSE event to Windows...")

# 0xB3 (decimal 179) is the virtual key code for VK_MEDIA_PLAY_PAUSE in Windows
VK_MEDIA_PLAY_PAUSE = 0xB3

# Simulate key press
ctypes.windll.user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 0, 0)

# Simulate key release (2 represents KEYEVENTF_KEYUP)
ctypes.windll.user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 2, 0)

print("✨ Event VK_MEDIA_PLAY_PAUSE sent successfully.")
