import psutil, paho.mqtt.client as mqtt, time, paho.mqtt.publish as publish

HARDWARE_POLL_INTERVAL = 3
CPU_SAMPLES = 5
MQTT_POLL_INTERVAL = 5
MQTT_TOPIC_PREFIX = 'app_server/hardware/'
MQTT_AVAILABLE_TOPIC = MQTT_TOPIC_PREFIX + "available"
MQTT_HOST = '192.168.1.10'
MQTT_KEEP_ALIVE = 30

def on_connect(client, userdata, flags, rc):
    client.publish(MQTT_TOPIC_PREFIX + "available", "online")

def main():    
    payload = []
    cpuPercent = psutil.cpu_percent()
    memoryUtilization = psutil.virtual_memory().percent
    diskPercent = psutil.disk_usage('/').percent
    #print(f'CPU: {cpuPercent}\nMemory: {memoryUtilization}\nDisk: {diskPercent}\n')
    payload.append({"topic":MQTT_TOPIC_PREFIX + "cpu", "payload": cpuPercent})
    payload.append({"topic":MQTT_TOPIC_PREFIX + "memory", "payload": memoryUtilization})
    payload.append({"topic":MQTT_TOPIC_PREFIX + "disk", "payload": diskPercent})

    # Publish to MQTT
    will = {"topic":MQTT_AVAILABLE_TOPIC, "payload":"offline", "retain":True}
    publish.multiple(payload, hostname=MQTT_HOST, client_id="app_server_system_monitor", keepalive=MQTT_KEEP_ALIVE, will=will)

if __name__ == "__main__":
    main()