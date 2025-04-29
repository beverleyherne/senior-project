#include <Wire.h>

#define TCA_ADDR 0x70

void tcaSelect(uint8_t channel) {
  if (channel > 7) return;
  Wire.beginTransmission(TCA_ADDR);
  Wire.write(1 << channel);
  Wire.endTransmission();
}

void setup() {
  Serial.begin(115200);
  Wire.begin();

  for (uint8_t ch = 0; ch < 8; ch++) {
    tcaSelect(ch);
    delay(100);
    Serial.print("📡 Scanning TCA Channel "); Serial.println(ch);

    for (uint8_t addr = 0x08; addr <= 0x77; addr++) {
      Wire.beginTransmission(addr);
      if (Wire.endTransmission() == 0) {
        Serial.print("Found device at 0x");
        Serial.println(addr, HEX);
      }
    }
  }

  Serial.println("Scan complete.");
}

void loop() {}
