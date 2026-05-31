"""
Windows Low-Level Media Controller
===================================
A unified CLI tool that sends virtual hardware interrupt signals
to Windows OS via the user32.dll keyboard simulation API.

Usage:
    python media_controller.py play_pause
    python media_controller.py next
    python media_controller.py prev
    python media_controller.py mute
"""
import ctypes
import argparse
import sys

# ---------------------------------------------------------------------------
# Constants: Named Virtual Key Codes (VK_CODE) & Flags
# Reference: https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
# ---------------------------------------------------------------------------
VK_CODES = {
    "play_pause": 0xB3,   # VK_MEDIA_PLAY_PAUSE (179)
    "next":       0xB0,   # VK_MEDIA_NEXT_TRACK (176)
    "prev":       0xB1,   # VK_MEDIA_PREV_TRACK (177)
    "mute":       0xAD,   # VK_VOLUME_MUTE      (173)
}

KEYEVENTF_KEYUP = 0x0002  # Flag: simulate key release


def send_media_key(action: str) -> None:
    """Send a virtual media key event to the Windows OS kernel.

    This function injects a hardware-level keyboard interrupt signal
    (KeyDown + KeyUp) into the OS message queue via user32.dll,
    bypassing any application-level input handling.

    Args:
        action: One of the supported media actions (e.g. 'play_pause', 'next').
    """
    vk_code = VK_CODES.get(action)
    if vk_code is None:
        print(f"Error: Unknown action '{action}'. "
              f"Supported actions: {', '.join(VK_CODES.keys())}")
        sys.exit(1)

    # Simulate key press (KeyDown)
    ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
    # Simulate key release (KeyUp)
    ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)

    print(f"[OK] VK_MEDIA_{action.upper()} (0x{vk_code:02X}) sent successfully.")


if __name__ == "__main__":
    # Cross-platform defense: ctypes.windll is Windows-exclusive.
    # Running on macOS/Linux would cause an unrecoverable AttributeError.
    if sys.platform != "win32":
        print("Error: This script only supports Windows OS. "
              "ctypes.windll requires the Windows kernel.")
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="Windows Low-Level Media Controller — "
                    "Sends virtual hardware interrupt signals to the OS kernel."
    )
    parser.add_argument(
        "action",
        choices=VK_CODES.keys(),
        help="Media action to perform (e.g., play_pause, next, prev, mute)"
    )
    args = parser.parse_args()

    send_media_key(args.action)
