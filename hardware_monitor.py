import psutil, paho.mqtt.client as mqtt, time

HARDWARE_POLL_INTERVAL = 10
MQTT_TOPIC_PREFIX = 'app_server/hardware/'
MQTT_HOST = '192.168.1.10'
MQTT_KEEP_ALIVE = 60

def on_connect(client, userdata, flags, rc):
    client.publish(MQTT_TOPIC_PREFIX + "available", "online")

def main():    
    # Set up MQTT
    client = mqtt.Client("app_server_system_monitor")
    client.connect(MQTT_HOST, keepalive=MQTT_KEEP_ALIVE)
    client.on_connect = on_connect
    client.will_set(MQTT_TOPIC_PREFIX + "available", "offline")
    client.loop_start()

    # Hardware data to gather
    cpuPercent = 0.0
    memoryUtilization = 0.0
    diskPercent = 0.0

    done = False
    hardwareStartTime = hardwareEndTime = time.time()
    while not done:
        hardwareEndTime = time.time()
        # Hardware polling
        if (hardwareEndTime - hardwareStartTime > HARDWARE_POLL_INTERVAL):
            cpuPercent = psutil.cpu_percent()
            memoryUtilization = psutil.virtual_memory().percent
            diskPercent = psutil.disk_usage('/').percent
            #print(f'CPU: {cpuPercent}\nMemory: {memoryUtilization}\nDisk: {diskPercent}\n')
            client.publish(MQTT_TOPIC_PREFIX + "cpu", cpuPercent)
            client.publish(MQTT_TOPIC_PREFIX + "memory", memoryUtilization)
            client.publish(MQTT_TOPIC_PREFIX + "disk", diskPercent)
            client.publish(MQTT_TOPIC_PREFIX + "available", "online")
            hardwareStartTime = time.time()
        time.sleep(1)

    client.publish(MQTT_TOPIC_PREFIX + "available", "offline").wait_for_publish()
    client.loop_stop()
    client.disconnect()
    #print("Program terminating")

if __name__ == "__main__":
    main()