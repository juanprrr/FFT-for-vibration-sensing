#include "MPU9250.h"

#define I2Cclock 400000
#define I2Cport Wire
#define MPU9250_ADDRESS MPU9250_ADDRESS_AD0   // Use either this line or the next to select which I2C address your device is using
//#define MPU9250_ADDRESS MPU9250_ADDRESS_AD1


#define SerialDebug true  // Set to true to get Serial output for debugging


MPU9250 myIMU(MPU9250_ADDRESS, I2Cport, I2Cclock);
// Pin definitions
int intPin = 12;  // These can be changed, 2 and 3 are the Arduinos ext int pins
int myLed  = 13;  // Set up pin 13 led for toggling

// Set variables for position and velocity calculation
float _velocity = 0.0;
float _initialVelocity = 0.0;

float _position = 0.0;
float _initialPosition = 0.0;

float acceleration_magnitude = 0.0;

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
  Serial.print(F("MPU9250 I AM 0x"));
  Serial.print(c, HEX);
  Serial.print(F(" I should be 0x"));
  Serial.println(0x71, HEX);
  if (c == 0x71) // WHO_AM_I should always be 0x71
  {
    Serial.println(F("MPU9250 is online..."));

    // Calibrate gyro and accelerometers, load biases in bias registers
    myIMU.calibrateMPU9250(myIMU.gyroBias, myIMU.accelBias);

    myIMU.initMPU9250();
    // Initialize device for active mode read of acclerometer, gyroscope, and
    // temperature
    Serial.println("MPU9250 initialized for active data mode....");

    // Read the WHO_AM_I register of the magnetometer, this is a good test of
    // communication

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
    myIMU.readAccelData(myIMU.accelCount);  // Read the x/y/z adc values

    // Now we'll calculate the accleration value into actual g's
    // This depends on scale being set
    myIMU.ax = (float)myIMU.accelCount[0] * myIMU.aRes; // - myIMU.accelBias[0];
    myIMU.ay = (float)myIMU.accelCount[1] * myIMU.aRes; // - myIMU.accelBias[1];
    myIMU.az = (float)myIMU.accelCount[2] * myIMU.aRes; // - myIMU.accelBias[2];
    acceleration_magnitude = get_acc_magnitude(myIMU.ax, myIMU.ay, myIMU.az);
    
  } // if (readByte(MPU9250_ADDRESS, INT_STATUS) & 0x01)

//------------------------UPDATE DATA IN CONSOLE----------------------------------
  myIMU.updateTime();
  myIMU.delt_t = millis() - myIMU.count;
  if (myIMU.delt_t > 500)
  {
    
    if(SerialDebug)
    {
      // Print acceleration values in milligs!
      Serial.print("X-acceleration: "); Serial.print(1000 * myIMU.ax);
      Serial.print(" mg ");
      Serial.print("Y-acceleration: "); Serial.print(1000 * myIMU.ay);
      Serial.print(" mg ");
      Serial.print("Z-acceleration: "); Serial.print(1000 * myIMU.az);
      Serial.println("mg ");
      Serial.print("Acceleration Magnitude: ");
      Serial.print(acceleration_magnitude*1000);
      Serial.println(" mg");
    }
    myIMU.count = millis();
    digitalWrite(myLed, !digitalRead(myLed));  // toggle led
    myIMU.sumCount = 0;
    myIMU.sum = 0;
  
  }  

}

float get_acc_magnitude(float ax, float ay, float az){
  float acceleration_magnitude = sqrt(ax*ax + ay*ay + az*az);
  return acceleration_magnitude;

}
