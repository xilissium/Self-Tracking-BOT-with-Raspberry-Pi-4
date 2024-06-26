// work only for the mbot2 platform
// made by xilissium

#include "MeMCore.h"

using namespace std;

int speed = 150;
int x = 0;


unsigned long lastExecutionTime = 0;
unsigned long interval = 100; 

MeUltrasonicSensor ultrasonic(3); //choos port of the ultrasonic sensor on your mbot2

void setup() {
  pinMode(6,OUTPUT); //motor1 pwm
  pinMode(7,OUTPUT); //motor1 direction

  pinMode(5,OUTPUT); //motor2 pwm
  pinMode(4,OUTPUT); //motor2 direction
  Serial.begin(115200); //use the same setting than on the python programe
  Serial.setTimeout(1);

}


void gofront(int v){
  analogWrite(6, v);
  analogWrite(5, v);
  digitalWrite(7,LOW); //motor direction for front rotation
  digitalWrite(4,HIGH); //LOW = front , HIGH = back
}

void goback(int v){
  analogWrite(6, v);
  analogWrite(5, v);
  digitalWrite(7,HIGH);
  digitalWrite(4,LOW);
}
void goright(int v){
  analogWrite(6, v);
  analogWrite(5, v);
  digitalWrite(7,LOW);
  digitalWrite(4,LOW);
}
void goleft(int v){
  analogWrite(6, v);
  analogWrite(5, v);
  digitalWrite(7,HIGH);
  digitalWrite(4,HIGH);
}
void stop(){
  analogWrite(6,0);
  analogWrite(5,0);
}




void loop() {
  unsigned long currentTime = micros();
  
  
  if (currentTime - lastExecutionTime >= interval) {
    Serial.println(ultrasonic.distanceCm());
    lastExecutionTime = currentTime;  // update laste execution time
  }

  
  if (Serial.available() > 0) {
    x = Serial.readString().toInt();
  
    if (x == 10) {
      gofront(speed);
    } else if (x == 11) {
      goback(speed);
    } else if (x == 12) {
      goleft(speed);
    } else if (x == 13) {
      goright(speed);
    } else {
      stop();
    }
  }
}

