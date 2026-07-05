#include <Arduino.h>

// Pin Assignments
const int led_pin = 32; // GPIO32 for LED output

// Volatile variable to store the current LED state, shared between main code and ISR
volatile bool led_state = LOW;

// Pointer to the hardware timer object
hw_timer_t *timer = NULL;

// Interrupt Service Routine (ISR) for the timer
// IRAM_ATTR ensures the function is placed in IRAM for faster execution and
// to avoid issues when flash cache is disabled.
void IRAM_ATTR onTimer() {
  // Toggle the LED state
  led_state = !led_state;
  // Write the new state to the LED pin
  digitalWrite(led_pin, led_state);
}

void setup() {
  // Configure the LED pin as an output
  pinMode(led_pin, OUTPUT);
  // Set initial state of the LED to LOW
  digitalWrite(led_pin, led_state);

  // Initialize UART communication at 115200 baud rate
  Serial.begin(115200);
  Serial.println("UART Initialized and ready for communication.");
  Serial.println("LED will blink using a hardware timer interrupt every 500ms.");

  // Configure and start hardware timer for LED blinking
  // timerBegin(timer_num, prescaler, count_up)
  //   timer_num: 0-3 for ESP32 hardware timers. Using Timer 0.
  //   prescaler: 80. APB_CLK is 80MHz, so 80MHz / 80 = 1MHz tick frequency (1us per tick).
  //   count_up: true for a count-up timer.
  timer = timerBegin(0, 80, true);

  // Attach the ISR function to the timer
  // timerAttachInterrupt(timer_handle, ISR_function, edge_trigger)
  //   timer_handle: Pointer to the timer object.
  //   ISR_function: Pointer to the function to be called on interrupt.
  //   edge_trigger: true to trigger on timer's alarm edge.
  timerAttachInterrupt(timer, &onTimer, true);

  // Set the timer alarm value and auto-reload behavior
  // timerAlarmWrite(timer_handle, alarm_value, auto_reload)
  //   timer_handle: Pointer to the timer object.
  //   alarm_value: 500,000 ticks. Since each tick is 1us, this means 500ms.
  //   auto_reload: true to automatically reload the alarm after it triggers,
  //                making the interrupt periodic.
  timerAlarmWrite(timer, 500000, true); // Trigger every 500ms

  // Enable the timer alarm, starting the periodic interrupts
  timerAlarmEnable(timer);
}

void loop() {
  // The LED blinking is handled entirely by the timer interrupt in the background.
  // The loop function can be used for other tasks without blocking the LED blink.
  // For demonstration, print a message periodically to show the loop is active.
  static unsigned long last_print_time = 0;
  const unsigned long print_interval_ms = 2000; // Print every 2 seconds

  if (millis() - last_print_time >= print_interval_ms) {
    Serial.println("Loop is running...");
    last_print_time = millis();
  }
}