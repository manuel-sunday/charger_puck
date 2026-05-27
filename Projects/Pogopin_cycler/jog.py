#!/usr/bin/env python3
"""
Keyboard jog control for the linear rail.

  Hold +  →  move forward
  Hold -  →  move backward
  Release →  stop
  ESC     →  quit

Usage:
  pip install pyserial pynput
  python jog.py          # auto-detects port
  python jog.py COM4     # specify port
"""

import sys
import serial
import serial.tools.list_ports
from pynput import keyboard

BAUD = 115200
JOG_KEYS = {'f', 'b'}


def find_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "usbserial" in p.device or "usbmodem" in p.device or "CH340" in (p.description or ""):
            return p.device
    if ports:
        return ports[0].device
    return None


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else find_port()
    if not port:
        print("No serial port found. Plug in the Arduino or pass port as argument.")
        sys.exit(1)

    print(f"Connecting to {port} at {BAUD} baud...")
    ser = serial.Serial(port, BAUD)
    print("Connected.  Hold F to move forward, hold B to move backward.  ESC to quit.\n")

    def on_press(key):
        try:
            if key.char == 'f':
                ser.write(b'f')
            elif key.char == 'b':
                ser.write(b'b')
        except AttributeError:
            pass

    def on_release(key):
        if key == keyboard.Key.esc:
            ser.write(b's')
            ser.close()
            return False  # stop listener
        try:
            if key.char in JOG_KEYS:
                ser.write(b's')
        except AttributeError:
            pass

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    print("Disconnected.")


if __name__ == "__main__":
    main()
