#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <BluetoothSerial.h>

WiFiClient client;
HTTPClient http;
BluetoothSerial SerialBT;

const char *ssid = "PIRATES NETWORK"; // Replace with your Wi-Fi network name
const char *password = "CAPTAINJS";   // Replace with your Wi-Fi password
String URL = "https://192.168.51.17/your_endpoint";
String mac = "48:74:12:94:62:6a";

int inputPin = 15; // choose the input pin (for PIR sensor)
int val = 0;      // variable for reading the pin status
unsigned long previousMillis = 0;
unsigned long interval = 10000; // 10 seconds in milliseconds

const int MAX_DEVICES = 10;           // Maximum number of devices to store
String deviceAddresses[MAX_DEVICES]; // Array to store device MAC addresses
int deviceCount = 0;                 // Counter for the number of devices


void setup()
{
    pinMode(inputPin, INPUT); // declare sensor as input
    Serial.begin(115200);
    SerialBT.begin("ESP32test"); // Bluetooth device name

    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }


    Serial.println(F(""));
    Serial.println(F("WiFi connected"));
    Serial.print(F("IP address: "));
    Serial.println(WiFi.localIP());
}

void btAdvertisedDeviceFound(BTAdvertisedDevice *pDevice)
{
    Serial.printf("Found a device asynchronously: %s \t %s\n", pDevice->getName().c_str(), pDevice->getAddress().toString().c_str());

    if (deviceCount < MAX_DEVICES)
    {
        deviceAddresses[deviceCount] = pDevice->getAddress().toString().c_str();
        deviceCount++;
    }
}

void loop()
{
    unsigned long currentMillis = millis();

    if (currentMillis - previousMillis >= interval)
    {
        // It's time to check for motion every 10 seconds
        previousMillis = currentMillis;

        // PIR Sensor Code
        val = digitalRead(inputPin); // read input value

        if (val == HIGH)
        {
            // Motion detected
            Serial.println(F("Motion detected!"));

            // Bluetooth Code - Start Discovery
            Serial.println(F("Starting asynchronous discovery..."));
            if (SerialBT.discoverAsync(btAdvertisedDeviceFound))
            {
                Serial.println(F("Findings will be reported in \"btAdvertisedDeviceFound\""));
                delay(10000); // Run discovery for 10 seconds
                Serial.println(F("Stopping discoverAsync..."));
                SerialBT.discoverAsyncStop();
                Serial.println(F("Stopped"));

                // HTTP POST Request with Device Names and MAC Addresses
                http.begin(URL);
                String message_name = "message_sent";
                String message_value = "Motion detected," + mac + "," ;

                for (int i = 0; i < deviceCount; i++)
                {
                    message_value += deviceAddresses[i];
                    if (i < deviceCount - 1)
                    {
                        message_value += ",";
                    }
                }

                String payload_request = message_name + "=" + message_value; // Combine the name and value
                http.addHeader("Content-Type", "application/x-www-form-urlencoded");
                int httpResponseCode = http.sendRequest("POST", payload_request);

                if (httpResponseCode > 0)
                {
                    String payload_response = http.getString();
                    Serial.println("HTTP Response Code: " + String(httpResponseCode));
                    Serial.println("Response: " + payload_response);
                }
                else
                {
                    Serial.println("HTTP Response Code: " + String(httpResponseCode));
                    Serial.println(F("HTTP Request failed"));
                }

                http.end();

                // Reset deviceCount for the next iteration
                deviceCount = 0;
                delay(10000);
            }
            else
            {
                Serial.println(F("Error on discoverAsync, not working after a \"connect\""));
            }
        }
        else
        {
            // No motion
            Serial.println(F("No motion"));
        }
    }
}

// Flash mode:Dio
// Flash size:4MB
// Partition:huge app
// Input pin: 15
