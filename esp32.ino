// https://www.engineersgarage.com/raspberry-pi-esp32-esp8266-mqtt-iot/

#include “PubSubClient.h”
#include “WiFi.h”

// WiFi
const char* ssid = “PLDTHOMEFBIR6c3e0”;                
const char* wifi_password = “#Senoj2000”;

// MQTT
const char* mqtt_server = “192.168.1.5”; 
const char* data_topic = “data”;
const char* mqtt_username = “hydropo”; // MQTT username
const char* mqtt_password = “hydropo”; // MQTT password
const char* clientID = “client_hydro”; // MQTT client ID

// Initialise the WiFi and MQTT Client objects
WiFiClient wifiClient;

// 1883 is the listener port for the Broker
PubSubClient client(mqtt_server, 1883, wifiClient);

 

// Custom function to connect to the MQTT broker via WiFi
void connect_MQTT(){
  Serial.print(“Connecting to “);
  Serial.println(ssid);

  // Connect to the WiFi
  WiFi.begin(ssid, wifi_password);

  // Wait until the connection is confirmed
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(“.”);
  }

  // Debugging – Output the IP Address of the ESP8266
  Serial.println(“WiFi connected”);
  Serial.print(“IP address: “);
  Serial.println(WiFi.localIP());

  // Connect to MQTT Broker
  if (client.connect(clientID, mqtt_username, mqtt_password)) {
    Serial.println(“Connected to MQTT Broker!”);
  }
  else {
    Serial.println(“Connection to MQTT Broker failed…”);
  }
}

void setup() {
  Serial.begin(9600);
  dht.begin();
}

void loop() {
  connect_MQTT();
  Serial.setTimeout(2000);

  Serial.println("Sending data...");

  // MQTT can only transmit strings
  String hs=”Hum: “+String((float)h)+” % “;
  String ts=”Temp: “+String((float)t)+” C “;
  
   String data_data = "DATA";

  if (client.publish(data_topic, String(data_data).c_str())) {
    Serial.println(“Data sent!”);
  }
  else {
    Serial.println(“Data failed to send. Reconnecting to MQTT Broker and trying again”);
    client.connect(clientID, mqtt_username, mqtt_password);
    delay(10); // This delay ensures that client.publish doesn’t clash with the client.connect call
    client.publish(data_topic, String(data_data).c_str());
  }

  client.disconnect();  // disconnect from the MQTT broker
  delay(1000*60);       // print new values after 1 Minute
}
