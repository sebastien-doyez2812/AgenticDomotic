#include <ESP8266WiFi.h>
#include <SoftwareSerial.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

const char* ssid = "YOUR_SSID";
const char* pwd  = "YOUR_PWD ";
const int MOSFET_GATE_INPUT = 14; // D5

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

  lcd.init();                      
  lcd.backlight();                 
  lcd.setCursor(0, 0);
  lcd.print("WiFi OK !\n");

  lcd.setCursor(0, 1);
  lcd.print( WiFi.localIP());
  pinMode(MOSFET_GATE_INPUT, OUTPUT);
  digitalWrite(MOSFET_GATE_INPUT, LOW);
}

void loop() {
  WiFiClient client = server.available(); 
  if (client)
  {
    Serial.println("Client connected!");
    while(client.connected())
    {
      if (client.available() > 0)
      {
        uint8_t data = client.read();
        if (data == 1)
        {
          Serial.println("Water Plant!");
          digitalWrite(MOSFET_GATE_INPUT, HIGH);
          delay(3000);
          digitalWrite(MOSFET_GATE_INPUT, LOW);
        }
      }
    }
  }  
}
