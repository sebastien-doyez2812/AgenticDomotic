#include <ESP8266WiFi.h>
#include <SoftwareSerial.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

const char* ssid = "YOUR_SSID";
const char* pwd  = "YOUR_PWD ";

WiFiServer server(1234);
LiquidCrystal_I2C lcd(0x20, 16, 2);

void setup() {
  Serial.begin(115200);
  delay(20);
  Serial.println("Try to connect to Wifi...");

  // Config WIFI:
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, pwd);
  while(WiFi.status() != WL_CONNECTED)
  {
    Serial.println(".");
  }
  Serial.println("Conected!");
  Serial.print("Adresse IP : ");
  Serial.println(WiFi.localIP());

// Config I2C:
}

void loop() {
  // put your main code here, to run repeatedly:

}
