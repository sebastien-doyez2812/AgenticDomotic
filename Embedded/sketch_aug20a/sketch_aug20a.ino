#include <ArduinoWiFiServer.h>
#include <BearSSLHelpers.h>
#include <CertStoreBearSSL.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiAP.h>
#include <ESP8266WiFiGeneric.h>
#include <ESP8266WiFiGratuitous.h>
#include <ESP8266WiFiMulti.h>
#include <ESP8266WiFiSTA.h>
#include <ESP8266WiFiScan.h>
#include <ESP8266WiFiType.h>
#include <WiFiClient.h>
#include <WiFiClientSecure.h>
#include <WiFiClientSecureBearSSL.h>
#include <WiFiServer.h>
#include <WiFiServerSecure.h>
#include <WiFiServerSecureBearSSL.h>
#include <WiFiUdp.h>

#include <ESP8266WiFi.h>
#include <SoftwareSerial.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

const char* ssid = "YOUR_SSID_HERE"
const char* pwd  = "YOUR_PASSWORD_HERE"

WiFiServer server(1234);
LiquidCrystal_I2C lcd(0x20, 16, 2);

void setup() {
// Config WIFI:
WiFi.mode(WIFI_STA);
WiFi.begin(ssid, pwd);
while(WiFi.status() != WL_CONNECTED)
{
  Serial.println(".");
}
// Config I2C:
}

void loop() {
  // put your main code here, to run repeatedly:

}
