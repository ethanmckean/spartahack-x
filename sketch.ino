#define LEDC_PIN 5
#define LEDC_RESOLUTION 10  // Set resolution to 10 bits
float multiplyfactor[4] = {0.075, 0.087, 0.075, 0.0625};

void setup() {
    // Set GPIO 2 (onboard LED) as an output
    pinMode(2, OUTPUT);
    // Start the serial communication at 9600 baud rate
    Serial.begin(9600);
    bool blinked = false;

    ledcAttach(LEDC_PIN, 50, LEDC_RESOLUTION);
}

void loop() {
    // Check if data is available to read
    if (Serial.available() > 0) {
        // Read the incoming byte:
        char command = Serial.read();

        if (command == '1') {
            // example usage
            for (int i = 0; i <= 3; i++) {
                int dutyCycle = (pow(2, LEDC_RESOLUTION) - 1) * multiplyfactor[i];
                ledcWrite(LEDC_PIN, dutyCycle);
                delay(1000);
            }
        }
        // For command '2': set servo to center (90°) using, say, a 1.5ms pulse (0.075)
        else if (command == '2') {
            int dutyCycle = (pow(2, LEDC_RESOLUTION) - 1) * 0.075;
            ledcWrite(LEDC_PIN, dutyCycle);
        }
        // For command '3': extend to full 180° using a 2.5ms pulse (0.125)
        else if (command == '3') {
            int dutyCycle = (pow(2, LEDC_RESOLUTION) - 1) * 0.125;
            ledcWrite(LEDC_PIN, dutyCycle);
        } else if (command == '4') {
            // For a 270° position, try using about a 3.0ms pulse
            // 3.0ms / 20ms = 0.15
            int dutyCycle = (pow(2, LEDC_RESOLUTION) - 1) * 0.15;
            ledcWrite(LEDC_PIN, dutyCycle);
        } else if (command == '5') {
            // For a 360° position, try using about a 3.5ms pulse
            // 3.5ms / 20ms = 0.175
            int dutyCycle = (pow(2, LEDC_RESOLUTION) - 1) * 0.175;
            ledcWrite(LEDC_PIN, dutyCycle);
        }
    }
}