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
import signal
import sys
import os

# Define the GPIO pin for the button
BUTTON_PIN = 3
shutdown_triggered = False

def shutdown_system():
    """Function to broadcast message and shutdown the system"""
    print("Button press detected. Initiating shutdown...")
    subprocess.run(["sudo", "wall", "Shutdown initiated by button press."])
    #time.sleep(3)  # 1 second delay before shutdown
    subprocess.run(["sudo", "sync"])
    subprocess.run(["sudo", "halt"])

def button_callback(channel):
    """Callback function that will be executed when button is pressed"""
    global shutdown_triggered
    
    # Debounce
    time.sleep(0.05)
    
    # Prevent multiple rapid shutdowns
    if not shutdown_triggered:
        shutdown_triggered = True
        shutdown_system()

def cleanup_handler(signum, frame):
    """Handle cleanup when the script is terminated"""
    GPIO.cleanup()
    sys.exit(0)

def poll_button():
    """Polling-based approach as a fallback if event detection fails"""
    print("Using polling method for button detection...")
    prev_state = GPIO.input(BUTTON_PIN)
    
    try:
        while True:
            current_state = GPIO.input(BUTTON_PIN)
            
            # For normally open button with pull-up, we're looking for HIGH->LOW transition
            if prev_state == 1 and current_state == 0:
                # Debounce
                time.sleep(0.05)
                # Verify state is still LOW
                if GPIO.input(BUTTON_PIN) == 0:
                    shutdown_system()
            
            prev_state = current_state
            time.sleep(0.01)  # Short sleep to prevent CPU hogging
    except Exception as e:
        print(f"Error in polling loop: {e}")
    finally:
        GPIO.cleanup()

def main():
    """
    Main function that sets up GPIO pin detection and waits indefinitely
    for button presses.
    """
    # Check if script is run as root
    if os.geteuid() != 0:
        print("This script must be run as root (sudo). Exiting.")
        sys.exit(1)
        
    # Register signal handlers for clean exit
    signal.signal(signal.SIGTERM, cleanup_handler)
    signal.signal(signal.SIGINT, cleanup_handler)

    # Clean up GPIO in case it wasn't properly cleaned
    GPIO.cleanup()

    try:
        # Use BCM (Broadcom) pin numbering
        GPIO.setmode(GPIO.BCM)
        
        # Set up pin without internal pull-up first
        GPIO.setup(BUTTON_PIN, GPIO.IN)
        
        # Try event detection method first
        try:
            print(f"Setting up edge detection on GPIO pin {BUTTON_PIN}...")
            GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, 
                                 callback=button_callback, 
                                 bouncetime=200)
            
            print(f"Monitoring button on GPIO pin {BUTTON_PIN} using event detection...")
            
            # Keep the script running
            while True:
                time.sleep(1)
                
        except RuntimeError as e:
            print(f"Edge detection failed: {e}")
            print("Falling back to polling method...")
            
            # If event detection fails, fall back to polling
            GPIO.remove_event_detect(BUTTON_PIN)
            poll_button()
            
    except Exception as e:
        print(f"Setup error: {e}")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
