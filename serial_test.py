import serial
import time

# Set up the serial connection (adjust the port name as necessary)
ser = serial.Serial('/dev/cu.usbserial-0001', 9600, timeout=1)

# Wait for the ESP32 to initialize
time.sleep(2)

# Send the command '1' to blink the LED
ser.write(b'1')

# Wait for the LED to blink (adjust timing as needed)
time.sleep(5)

# Close the serial connection
ser.close()


'''
GPIO:

motor: set pin __ high


'''