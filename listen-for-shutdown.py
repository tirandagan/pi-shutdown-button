#!/usr/bin/env python3
# ------------------------------------------------------------------------------
# Name:         pi-power-button-extended.py
# Description:  This script monitors a physical push-button connected to GPIO pin 3
#               on a Raspberry Pi. It supports both Normally Open (NO) and Normally
#               Closed (NC) buttons. When a button press is detected (a transition
#               in pin state), the script broadcasts a message to all logged-in
#               users via the "wall" command and then initiates a system shutdown
#               via the "shutdown" command.
#
#               A short debounce delay helps mitigate false triggers caused by
#               mechanical bouncing. This script performs a single detection:
#               once it detects an edge (open->closed or closed->open) and confirms
#               the state has changed, it proceeds to shut down immediately.
#
# Wiring/Usage:
#   1. Connect a momentary push button between GPIO pin 3 (BCM numbering) and GND.
#   2. This script uses the internal pull-up resistor (PUD_UP). 
#      - For a Normally Open button, the pin will read HIGH when not pressed,
#        and LOW when pressed.
#      - For a Normally Closed button, the pin will read LOW when not pressed,
#        and HIGH when pressed.
#   3. Make the script executable (chmod +x pi-power-button-extended.py).
#   4. Run it (usually as root or via sudo, so it can call "shutdown").
#
# Notes:
#   - Based on the original project by Howchoo (https://howchoo.com/pi/pi-power-button).
#   - (c) 2025 Tiran Dagan
# ------------------------------------------------------------------------------
# Import necessary modules
import RPi.GPIO as GPIO
import subprocess
import time

def main():
    """
    Main function that sets up GPIO pin 3, waits for one state change (edge),
    debounces the signal, broadcasts a message, and initiates shutdown.
    """

    # Use BCM (Broadcom) pin numbering
    GPIO.setmode(GPIO.BCM)

    # Set up pin 3 as input with internal pull-up resistor
    #   - This means the pin is normally pulled HIGH (NO button is open, NC is closed).
    GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Capture the initial state of pin 3
    old_state = GPIO.input(3)

    # Block until an edge occurs (rising or falling)
    GPIO.wait_for_edge(3, GPIO.BOTH)

    # Delay for debounce (50ms is usually enough for mechanical buttons)
    time.sleep(0.05)

    # Read the new state after the edge
    new_state = GPIO.input(3)

    # If the state has truly changed, broadcast a message and shut down
    if new_state != old_state:
        subprocess.run(["wall", "Shutdown initiated by button press."])
        subprocess.call(["shutdown", "-h", "now"], shell=False)

if __name__ == "__main__":
    main()
