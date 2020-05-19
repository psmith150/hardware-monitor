import psutil, paho.mqtt.client as mqtt, time, logging, logging.handlers, os

HARDWARE_POLL_INTERVAL = 10 # Seconds between polling of hardware
MQTT_TOPIC_PREFIX = 'app_server/hardware/' # MQTT topic to use as prefix
MQTT_HOST = '192.168.1.10' # MQTT host
MQTT_KEEP_ALIVE = 60 # Keep alive time
LOG_PATH = 'logs\\'

def on_connect(client, userdata, flags, rc):
    client.publish(MQTT_TOPIC_PREFIX + "available", "online")

def main():    
    # Set up logging
    # Create path if doesn't exist
    os.makedirs(LOG_PATH, exist_ok=True)
    fileLogger = logging.getLogger('FileLogger')
    fileLogger.setLevel(logging.WARNING)
    handler = logging.handlers.RotatingFileHandler(filename=LOG_PATH + 'hardware_monitor.log', maxBytes=1024, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s:%(message)s')
    handler.setFormatter(formatter)
    fileLogger.addHandler(handler)

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
    fileLogger.info('Starting system monitoring')
    while not done:
        hardwareEndTime = time.time()
        # Hardware polling
        if (hardwareEndTime - hardwareStartTime > HARDWARE_POLL_INTERVAL):
            try:
                cpuPercent = psutil.cpu_percent()
                memoryUtilization = psutil.virtual_memory().percent
                diskPercent = psutil.disk_usage('/').percent
                fileLogger.info(f'CPU: {cpuPercent}% - Memory: {memoryUtilization}% - Disk: {diskPercent}%\n')
                client.publish(MQTT_TOPIC_PREFIX + "cpu", cpuPercent)
                client.publish(MQTT_TOPIC_PREFIX + "memory", memoryUtilization)
                client.publish(MQTT_TOPIC_PREFIX + "disk", diskPercent)
                client.publish(MQTT_TOPIC_PREFIX + "available", "online")
                hardwareStartTime = time.time()
            except Exception as ex:
                fileLogger.exception(f'Exception occurred: {ex}')
                raise
        time.sleep(1)
    client.publish(MQTT_TOPIC_PREFIX + "available", "offline").wait_for_publish()
    client.loop_stop()
    client.disconnect()
    logging.info('Program terminating')
    #print("Program terminating")

if __name__ == "__main__":
    main()