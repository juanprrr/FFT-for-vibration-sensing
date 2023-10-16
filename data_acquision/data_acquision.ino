#include "MPU9250.h"

#define I2Cclock 400000
#define I2Cport Wire
#define MPU9250_ADDRESS MPU9250_ADDRESS_AD0   // Use either this line or the next to select which I2C address your device is using
//#define MPU9250_ADDRESS MPU9250_ADDRESS_AD1

#define SerialDebug false  // Set to true to get Serial output for debugging

MPU9250 myIMU(MPU9250_ADDRESS, I2Cport, I2Cclock);
// Pin definitions
int intPin = 12;  // These can be changed, 2 and 3 are the Arduinos ext int pins
int myLed  = 13;  // Set up pin 13 led for toggling
float g_converter = 9.77589; //Costa Rica's g acceleration
char userInput;
void setup() {
  Wire.begin();
  // TWBR = 12;  // 400 kbit/sec I2C speed
  Serial.begin(115200);

  while(!Serial){};
  // Set up the interrupt pin, its set as active high, push-pull
  pinMode(intPin, INPUT);
  digitalWrite(intPin, LOW);
  pinMode(myLed, OUTPUT);
  digitalWrite(myLed, HIGH);

    // Read the WHO_AM_I register, this is a good test of communication
  byte c = myIMU.readByte(MPU9250_ADDRESS, WHO_AM_I_MPU9250);
//  Serial.print(F("MPU9250 I AM 0x"));
//  Serial.print(c, HEX);
//  Serial.print(F(" I should be 0x"));
//  Serial.println(0x71, HEX);
  if (c == 0x71) // WHO_AM_I should always be 0x71
  {
//    Serial.println(F("MPU9250 is online..."));

    // Calibrate gyro and accelerometers, load biases in bias registers
    myIMU.calibrateMPU9250(myIMU.gyroBias, myIMU.accelBias);

    myIMU.initMPU9250();
    // Initialize device for active mode read of acclerometer, gyroscope, and
    // temperature
//    Serial.println("MPU9250 initialized for active data mode....");

    // Get sensor resolutions, only need to do this once
    myIMU.getAres();

  } // if (c == 0x71)
  else
  {
    Serial.print("Could not connect to MPU9250: 0x");
    Serial.println(c, HEX);

    // Communication failed, stop here
    Serial.println(F("Communication failed, abort!"));
    Serial.flush();
    abort();
  }
}


void loop() {
//--------------------------------READ ACCELEROMETER DATA-------------------------
  if (myIMU.readByte(MPU9250_ADDRESS, INT_STATUS) & 0x01)
  {  
    userInput = Serial.read();
    if (userInput == 'g'){
      myIMU.readAccelData(myIMU.accelCount);  // Read the x/y/z adc values
      myIMU.ax = (float)myIMU.accelCount[0] * myIMU.aRes; // - myIMU.accelBias[0];
      myIMU.ay = (float)myIMU.accelCount[1] * myIMU.aRes; // - myIMU.accelBias[1];
      myIMU.az = (float)myIMU.accelCount[2] * myIMU.aRes; // - myIMU.accelBias[2];
      Serial.print(myIMU.ax*g_converter);
      Serial.print(",");
      Serial.print(myIMU.ay*g_converter);
      Serial.print(",");
      Serial.println(myIMU.az*g_converter);
      
      }
    
        
  } 
}
