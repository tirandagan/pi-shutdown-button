# pi-power-button

Scripts used in hochoo's article [Raspberry Pi power button guide](https://howchoo.com/g/mwnlytk3zmm/how-to-add-a-power-button-to-your-raspberry-pi).

> **Note**: This version has been updated by Tiran Dagan (tiran@tirandagan.com) to support both Normally Open (NO) and Normally Closed (NC) buttons, with improved debounce handling and user notifications.

## Installation

1. [Connect to your Raspberry Pi via SSH](https://howchoo.com/g/mgi3mdnlnjq/how-to-log-in-to-a-raspberry-pi-via-ssh)
1. Clone this repo: `git clone https://github.com/Howchoo/pi-power-button.git`
1. Optional: Edit line 9/10 in listen-for-shutdown.py to your preferred pin (Please see "Is it possible to use another pin other than Pin 5 (GPIO 3/SCL)?" below!)
1. Run the setup script: `./pi-power-button/script/install`

## Button Types & Operation

The script now supports both types of momentary push buttons:
- **Normally Open (NO)**: Circuit is open by default, closes when pressed
- **Normally Closed (NC)**: Circuit is closed by default, opens when pressed

When you press the button:
1. The script detects the state change
2. Waits 50ms to debounce the signal
3. Broadcasts a shutdown message to all logged-in users
4. Initiates a safe system shutdown

## Hardware

A full list of what you'll need can be found [here](https://howchoo.com/g/mwnlytk3zmm/how-to-add-a-power-button-to-your-raspberry-pi#parts-list). At a minimum, you'll need a momentary push button (either NO or NC), some jumper wires, and a soldering iron. If you _don't_ have a soldering iron or don't feel like breaking it out, you can use [this prebuilt button](https://howchoo.com/shop/product/prebuilt-raspberry-pi-power-button?utm_source=github&utm_medium=referral&utm_campaign=git-repo-readme) instead.

### Wiring

Connect the power button to Pin 5 (GPIO 3/SCL) and Pin 6 (GND) as shown in this diagram:

![Connection Diagram](https://raw.githubusercontent.com/Howchoo/pi-power-button/master/diagrams/pinout.png)

The script uses the internal pull-up resistor on GPIO3, so no external resistor is needed:
- For NO buttons: Pin reads HIGH when not pressed, LOW when pressed
- For NC buttons: Pin reads LOW when not pressed, HIGH when pressed

### Is it possible to use another pin other than Pin 5 (GPIO 3/SCL)?

Not for full functionality, no. There are two main features of the power button:

1. **Shutdown functionality:** Shut the Pi down safely when the button is pressed. The Pi now consumes zero power.
2. **Wake functionality:** Turn the Pi back on when the button is pressed again.

The **wake functionality** requires the SCL pin, Pin 5 (GPIO 3). There's simply no other pin that can "hardware" wake the Pi from a zero-power state. If you don't care about turning the Pi back _on_ using the power button, you could use a different GPIO pin for the **shutdown functionality** and still have a working shutdown button. Then, to turn the Pi back on, you'll need to disconnect and reconnect power (or use a cord with a physical switch in it) to "wake" the Pi.

Of course, for the GND connection, you can use [any other ground pin you want](https://pinout.xyz/).

## Uninstallation

If you need to uninstall the power button script in order to use GPIO3 for another project:

1. Run the uninstall script: `./pi-power-button/script/uninstall`
