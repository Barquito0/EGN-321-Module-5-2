// EGN 321 - Virtual Sensor Reliability Lab
// Arduino Uno + NTC Temperature Sensor
// VERSION 6 - FIXED SUSPICIOUS CHANGE LOGIC
//
// Serial output:
// sample,time_seconds,raw_adc,temperature_c,unit,status

#include <math.h>

const int SENSOR_PIN = A0;
const float BETA = 3950.0;

const float MIN_VALID_TEMP_C = 0.0;
const float MAX_VALID_TEMP_C = 50.0;
const float MIN_NORMAL_TEMP_C = 18.0;
const float MAX_NORMAL_TEMP_C = 30.0;
const float MAX_ALLOWED_CHANGE_C = 3.0;

unsigned long sampleNumber = 1;
float previousTemperature = 0.0;
bool havePreviousTemperature = false;

float adcToCelsius(int rawValue) {
  if (rawValue <= 0 || rawValue >= 1023) {
    return NAN;
  }

  float temperatureC =
    1.0 /
    (
      log(
        1.0 / (1023.0 / rawValue - 1.0)
      ) / BETA
      + 1.0 / 298.15
    )
    - 273.15;

  return temperatureC;
}

void setup() {
  Serial.begin(9600);
  Serial.println("VERSION_6_FIXED_SUSPICIOUS_LOGIC");
  Serial.println("sample,time_seconds,raw_adc,temperature_c,unit,status");
}

void loop() {
  int rawValue = analogRead(SENSOR_PIN);
  float temperatureC = adcToCelsius(rawValue);

  String status;

  if (isnan(temperatureC)) {
    status = "MISSING";
  }
  else if (
    temperatureC < MIN_VALID_TEMP_C ||
    temperatureC > MAX_VALID_TEMP_C
  ) {
    status = "INVALID_OUT_OF_RANGE";
  }
  else if (
    temperatureC < MIN_NORMAL_TEMP_C ||
    temperatureC > MAX_NORMAL_TEMP_C
  ) {
    status = "SUSPICIOUS_TEMP";
  }
  else if (
    havePreviousTemperature &&
    fabs(temperatureC - previousTemperature) > MAX_ALLOWED_CHANGE_C
  ) {
    status = "SUSPICIOUS_CHANGE";
  }
  else {
    status = "OK";
  }

  if (
    !isnan(temperatureC) &&
    temperatureC >= MIN_VALID_TEMP_C &&
    temperatureC <= MAX_VALID_TEMP_C
  ) {
    previousTemperature = temperatureC;
    havePreviousTemperature = true;
  }

  Serial.print(sampleNumber);
  Serial.print(",");
  Serial.print(millis() / 1000.0, 1);
  Serial.print(",");
  Serial.print(rawValue);
  Serial.print(",");

  if (isnan(temperatureC)) {
    Serial.print("");
  } else {
    Serial.print(temperatureC, 1);
  }

  Serial.print(",C,");
  Serial.println(status);

  sampleNumber++;
  delay(1000);
}
