import time
import random
import network
from umqtt.robust import MQTTClient


CERT_FILE = "/f8fa6663669b3332e5e6ef0ead726231d75c1229b7c3ddc324868094e5255e22-certificate.pem.crt"
KEY_FILE = "/f8fa6663669b3332e5e6ef0ead726231d75c1229b7c3ddc324868094e5255e22-private.pem.key"

MQTT_CLIENT_ID = "IoTAGH1"
MQTT_PORT = 8883

PUB_TOPIC = "aghiot/write" #coming out of device
SUB_TOPIC = "aghiot/read"  #coming into device

MQTT_HOST = "axurg0y0vtb2z-ats.iot.eu-west-1.amazonaws.com"
WIFI_SSID = "pizmaknet"
WIFI_PW = "qwertyuiop"

MQTT_CLIENT = None

def network_connect():
    wifi = network.WLAN(network.STA_IF)
    if not wifi.isconnected():
        print('connecting to network...')
        wifi.active(True)
        wifi.connect(WIFI_SSID , WIFI_PW)
        while not wifi.isconnected():
            pass
    print('network config:', wifi.ifconfig())

def pub_msg(msg):
    global MQTT_CLIENT
    try:    
        MQTT_CLIENT.publish(PUB_TOPIC, msg)
        print("Sent: " + msg)
    except Exception as e:
        print("Exception publish: " + str(e))
        raise

def sub_cb(topic, msg):
    print('Device received a Message: ')
    print((topic, msg))  

def device_connect():    
    global MQTT_CLIENT

    try:
        with open(KEY_FILE, "r") as f: 
            key = f.read()
        print("Got Key")
       
        with open(CERT_FILE, "r") as f: 
            cert = f.read()
        print("Got Cert")

        MQTT_CLIENT = MQTTClient(client_id=MQTT_CLIENT_ID, server=MQTT_HOST, port=MQTT_PORT, keepalive=5000, ssl=True, ssl_params={"cert":cert, "key":key, "server_side":False})
        MQTT_CLIENT.connect()
        print('MQTT Connected')
        MQTT_CLIENT.set_callback(sub_cb)
        MQTT_CLIENT.subscribe(SUB_TOPIC)
        print('Subscribed to %s as the incoming topic' % (SUB_TOPIC))
        return MQTT_CLIENT
    except Exception as e:
        print('Cannot connect MQTT: ' + str(e))
        raise


#start execution
try:
    print("Connecting WIFI")
    network_connect()
    print("Connecting MQTT")
    device_connect()
    while True:
            pending_message = MQTT_CLIENT.check_msg()
            if pending_message != 'None':
                temp =  random.randint(0, 130)
                deviceTime = time.time()
                print("Publishing")
                pub_msg("{\n  \"temperature\": %d,\n \"timestamps\": %d\n}"%(temp,deviceTime))      
                print("published payload")
                time.sleep(5)
            
except Exception as e:
    print(str(e))