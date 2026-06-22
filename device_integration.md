# Device integration — NodeMCU / ESP sample

This file contains a minimal example for an ESP8266/ESP32 (Arduino core) that posts three sensor BPM values to the Flask `/update_bpm` endpoint.

ESP8266 (Arduino) example
```cpp
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASS";
const char* serverUrl = "http://192.168.1.100:5000/update_bpm"; // change to your PC's IP

void setup(){
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print('.'); }
  Serial.println("Connected");
}

void loop(){
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    // Replace these with your sensor readings
    int s1 = 72;
    int s2 = 68;
    int s3 = 75;

    String payload = "{";
    payload += "\"bpm1\":" + String(s1) + ",";
    payload += "\"bpm2\":" + String(s2) + ",";
    payload += "\"bpm3\":" + String(s3) + "}";

    int httpCode = http.POST(payload);
    if (httpCode > 0) {
      String response = http.getString();
      Serial.println(response);
    } else {
      Serial.println("HTTP POST failed");
    }
    http.end();
  }
  delay(1000); // post every second (adjust as needed)
}
```

Notes
- Update `serverUrl` to point to the machine running the Flask app (use local IP if testing on same LAN).
- Ensure CORS is enabled in `app.py` (already present).
- For production use, secure the endpoint with tokens and TLS.
