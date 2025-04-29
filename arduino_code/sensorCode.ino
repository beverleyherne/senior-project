#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
#include <EEPROM.h>

#define TCA_ADDR 0x70
#define TEST_CHANNEL 5
#define EEPROM_ADDRESS 0

Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x29);
//sensor code for outputting data from the BNO055 IMU to the serial monitor
// and saving calibration data to EEPROM    
// designed to work with the TCA9548A I2C multiplexer
bool collecting = false;
bool waitingToStart = false;
bool headersPrinted = false;

void tcaSelect(uint8_t channel) {
  if (channel > 7) return;
  Wire.beginTransmission(TCA_ADDR);
  Wire.write(1 << channel);
  Wire.endTransmission();
}

void setup() {
  Wire.begin();
  Serial.begin(115200);
  while (!Serial);

  tcaSelect(TEST_CHANNEL);
  delay(100);

  Serial.println("Checking BNO055 on TCA channel 5...");

  if (!bno.begin()) {
    Serial.println("Sensor not detected on channel 5. Check wiring.");
    while (1);
  }

  bno.setExtCrystalUse(true);
  Serial.println("BNO055 on channel 5 initialized.");

  // Load calibration from EEPROM 
  adafruit_bno055_offsets_t calibrationData;
  EEPROM.get(EEPROM_ADDRESS, calibrationData);
  if (calibrationData.accel_offset_x != 0xFFFF && calibrationData.gyro_offset_x != 0xFFFF) {
    bno.setSensorOffsets(calibrationData);
    Serial.println("Loaded calibration data from EEPROM.");
  } else {
    Serial.println("No valid calibration data found in EEPROM.");
  }

  delay(1000);
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "start") {
      waitingToStart = true;
      collecting = false;
      headersPrinted = false;
      Serial.println("CALIBRATION_MONITORING");
    } else if (command == "stop") {
      collecting = false;
      waitingToStart = false;
      Serial.println("LOGGING_STOPPED");
    } else {
      Serial.print("Received: ");
      Serial.println(command);
    }
  }

  tcaSelect(TEST_CHANNEL);

  static unsigned long lastCalibSend = 0;
  if (waitingToStart && millis() - lastCalibSend > 1000) {
    uint8_t sys, gyro, accel, mag;
    bno.getCalibration(&sys, &gyro, &accel, &mag);
    Serial.print("CALIBRATION: ");
    Serial.print("Sys:"); Serial.print(sys);
    Serial.print(" Gyro:"); Serial.print(gyro);
    Serial.print(" Accel:"); Serial.print(accel);
    Serial.print(" Mag:"); Serial.println(mag);
    lastCalibSend = millis();

    if (sys > 1 && gyro > 1 && accel > 1 && mag > 1) {
      collecting = true;
      waitingToStart = false;
      Serial.println("LOGGING_STARTED");
    }
  }

  if (collecting) {
    tcaSelect(TEST_CHANNEL);
    unsigned long ts = millis();

    imu::Vector<3> linAccel = bno.getVector(Adafruit_BNO055::VECTOR_LINEARACCEL);
    imu::Vector<3> gyro = bno.getVector(Adafruit_BNO055::VECTOR_GYROSCOPE);
    imu::Vector<3> mag = bno.getVector(Adafruit_BNO055::VECTOR_MAGNETOMETER);
    imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);

    if (!headersPrinted) {
      Serial.println("Arduino_Timestamp_ms,Accel_X,Accel_Y,Accel_Z,Gyro_X,Gyro_Y,Gyro_Z,Mag_X,Mag_Y,Mag_Z,Euler_Heading,Euler_Roll,Euler_Pitch");
      headersPrinted = true;
    }

    Serial.print(ts); Serial.print(",");
    Serial.print(linAccel.x()); Serial.print(",");
    Serial.print(linAccel.y()); Serial.print(",");
    Serial.print(linAccel.z()); Serial.print(",");
    Serial.print(gyro.x()); Serial.print(",");
    Serial.print(gyro.y()); Serial.print(",");
    Serial.print(gyro.z()); Serial.print(",");
    Serial.print(mag.x()); Serial.print(",");
    Serial.print(mag.y()); Serial.print(",");
    Serial.print(mag.z()); Serial.print(",");
    Serial.print(euler.x()); Serial.print(",");
    Serial.print(euler.y()); Serial.print(",");
    Serial.println(euler.z());

    delay(100);
  }
}
