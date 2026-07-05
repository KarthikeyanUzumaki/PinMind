// [Warning] Gemini API call failed: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
// Falling back to Simulation Mode.

/*
 * ==========================================================================
 * PINMIND GENERATION ENGINE - PARAMETERIZED LOCAL TEMPLATE
 * MCU: ESP32-WROOM | Framework: Arduino | Intent: LED_BLINK
 * Mapped Pin: led on GPIO20
 * Extracted Params: interval_ms=500, baud_rate=115200, resolution=12-bit, duty=100%
 * ==========================================================================
 */

void setup() {
  pinMode(20, OUTPUT);
}

void loop() {
  digitalWrite(20, HIGH);
  delay(500);
  digitalWrite(20, LOW);
  delay(500);
}