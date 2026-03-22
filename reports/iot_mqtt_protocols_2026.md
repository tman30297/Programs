# IoT & MQTT Protocols - 2026

## Overview

The Internet of Things (IoT) connects physical devices to the internet, enabling automation, monitoring, and control. MQTT is the dominant protocol for IoT communication.

## IoT Architecture

```
Sensors/Actuators → IoT Gateway → Cloud/Local Server → Dashboard/Apps
       ↑                                    ↓
    Devices                             Users
```

## MQTT (Message Queuing Telemetry Transport)

### Why MQTT?
- Lightweight (minimal bandwidth)
- Low power consumption
- Reliable delivery (QoS levels)
- Pub/Sub model
- Designed for unstable networks

### Key Concepts

**Broker** - Server that routes messages
- Mosquitto (most popular, open-source)
- EMQX (scalable, enterprise)
- HiveMQ (enterprise)
- VerneMQ (Erlang-based)

**Topic** - Hierarchical message routing
```
home/livingroom/temperature
home/kitchen/light/state
home/+/temperature  # Wildcard
```

**QoS Levels**
- 0: At most once (fire and forget)
- 1: At least once (acknowledged)
- 2: Exactly once (guaranteed)

**Client** - Publishes or subscribes
- Paho (Python, C, Java)
- MQTT.js (JavaScript)
- Various Arduino libraries

### MQTT over WebSockets
- Port 9001 (native) or 443 (over WS)
- Useful for browser-based dashboards

## Home Assistant Integration

MQTT is natively supported in Home Assistant:
```yaml
mqtt:
  broker: 192.168.1.100
  port: 1883
  username: !secret mqtt_user
  password: !secret mqtt_password

sensor:
  - platform: mqtt
    name: "Living Room Temperature"
    state_topic: "home/livingroom/temperature"
    unit_of_measurement: "°C"
```

## Other IoT Protocols

### CoAP (Constrained Application Protocol)
- REST-like, designed for constrained devices
- UDP-based
- Good for simple sensor networks

### HTTP/REST
- Ubiquitous, well-understood
- Higher overhead than MQTT
- Good for occasional updates

### WebSockets
- Bidirectional, persistent
- Good for dashboards

### LoRaWAN
- Long range, low power
- Rural/agricultural applications
- Kilometers of range

### Zigbee / Z-Wave
- Short range, mesh networking
- Home automation
- Hue, SmartThings, etc.

### Matter
- Newer protocol (2022)
- Unifies smart home
- Apple/Google/Amazon supported

## Security Considerations

### MQTT Security
1. **TLS/SSL** - Use mqtt://s (port 8883) or WSS (9001)
2. **Authentication** - Username/password or certificates
3. **Authorization** - Topic-level access control
4. **Network segmentation** - VLAN for IoT devices
5. **Firmware updates** - Keep devices updated

### Example: TLS Config (Mosquitto)
```yaml
listener 8883
cafile /etc/mosquitto/certs/ca.crt
certfile /etc/mosquitto/certs/server.crt
keyfile /etc/mosquitto/certs/server.key
require_certificate true
```

## DIY IoT Projects

### ESP32/ESP8266 (Popular)
- WiFi capable
- Arduino compatible
- Very affordable ($3-10)
- Great for sensors, relays

### Example: ESP32 Temperature Sensor
```cpp
#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "YourSSID";
const char* password = "YourPassword";
const char* mqtt_server = "192.168.1.100";

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
}

void setup_wifi() {
  delay(10);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
}

void reconnect() {
  while (!client.connected()) {
    if (client.connect("ESP32Client")) {
      client.subscribe("home/command");
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  
  // Read temperature and publish
  float temp = readTemperature();
  char payload[50];
  snprintf(payload, 50, "%.1f", temp);
  client.publish("home/livingroom/temperature", payload);
  
  delay(60000); // Every minute
}
```

### Raspberry Pi as MQTT Broker
```bash
# Install Mosquitto
sudo apt update
sudo apt install -y mosquitto mosquitto-clients

# Enable and start
sudo systemctl enable mosquitto
sudo systemctl start mosquitto

# Test
# Terminal 1: mosquitto_sub -t "test/#"
# Terminal 2: mosquitto_pub -t "test/message" -m "Hello"
```

## Use Cases

### Home Automation
- Temperature/humidity monitoring
- Light control
- Motion detection
- Door/window sensors

### Agriculture
- Soil moisture monitoring
- Weather stations
- Automated irrigation

### Industrial
- Machine monitoring
- Predictive maintenance
- Environmental sensors

### Healthcare
- Wearable devices
- Remote patient monitoring
- Equipment tracking

## Tools & Dashboards

### Local
- Home Assistant
- Node-RED (visual flows)
- Grafana (visualization)

### Cloud (if needed)
- AWS IoT Core
- Google Cloud IoT
- Azure IoT Hub
- ThingsBoard

## Best Practices

1. **Network segmentation** - VLAN for IoT
2. **Local processing** - Reduce cloud dependency
3. **Retain messages** - Last known state
4. **Birth/last will** - Know when device goes offline
5. **Rate limiting** - Don't overwhelm broker
6. **Topic naming** - Consistent hierarchy
7. **TLS in production** - Never plain MQTT externally

## Future Trends

- Matter protocol adoption
- Edge AI on devices
- Thread protocol growth
- More local processing
- Improved security
