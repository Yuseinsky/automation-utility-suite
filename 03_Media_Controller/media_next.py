import ctypes
import time
import sys

sys.stdout.reconfigure(errors='replace')

print("⏭️ Sending VK_MEDIA_NEXT_TRACK event to Windows...")

# 0xB0 (decimal 176) is the virtual key code for VK_MEDIA_NEXT_TRACK in Windows
VK_MEDIA_NEXT_TRACK = 0xB0

# Simulate key press
ctypes.windll.user32.keybd_event(VK_MEDIA_NEXT_TRACK, 0, 0, 0)

# Simulate key release (2 represents KEYEVENTF_KEYUP)
ctypes.windll.user32.keybd_event(VK_MEDIA_NEXT_TRACK, 0, 2, 0)

print("✨ Event VK_MEDIA_NEXT_TRACK sent successfully.")
