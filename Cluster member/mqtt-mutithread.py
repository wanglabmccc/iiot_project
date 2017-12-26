import thread
import time

import paho.mqtt.client as mqtt
import mqtt_controller

import prototype
import meta_data

import network_parameter

global client
global AP_SSID

import socket
client = None
AP_SSID = 'default'

bind_interface = None

import json

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	
	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	client.subscribe("iiot/cluster")
	client.subscribe("iiot/traffic_model")
	print "keep_alive ssid ==> " + AP_SSID
	#device_1_member = ['sta01']
	#device_1 = prototype.json_set_cluster_item('ap01',ssid='MJ onair' \
	#									 ,password='gugululu',cluster_member=device_1_member)
	#cluster_msg = prototype.json_set_cluster(device_1)
	#client.publish("iiot/cluster",cluster_msg)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	print(msg.topic+" "+str(msg.payload))
	if msg.topic == "iiot/cluster":
		ssid = None
		password = None
		ap_ip = None
		fptr = open('/root/ap_ip', 'w')
		mqtt_msgs = json.loads(msg.payload)
		for mqtt_msg in mqtt_msgs:
			print mqtt_msg
			for member in mqtt_msg['cluster_member']:
				if member == meta_data.DEVICE_ID :
					ssid = mqtt_msg['ssid']
					password = mqtt_msg['password']
					fptr.write(mqtt_msg['ap_ip'])
					global AP_SSID
					AP_SSID = ssid
					fptr.close()
					print "message ssid ==> " + AP_SSID
					client.disconnect()
					mqtt_controller.set_wifi_state('sta',ssid,password)
	if msg.topic == "iiot/traffic_model":
		mqtt_msg = json.loads(msg.payload)
		print mqtt_msg['device_id']
		if meta_data.DEVICE_ID == mqtt_msg['device_id']:
			fptr = open('/root/traffic_model', 'w')
			fptr.write(str(mqtt_msg['interval']))
			fptr.close()




# The callback when client public a message.
def on_publish(client, userdata, mid):
	print("Message publish...")

def on_disconnect(client, userdata, rc):
	print("MQTT disconnect")
	client.connect(MQTT_SERVER_IP, 1883, 60)


MQTT_SERVER_IP = "140.113.179.7"
MQTT_SERVER_PORT = 1883


def start_mqtt_loop():
	global client
	global AP_SSID
	client = mqtt.Client("", True, None, mqtt.MQTTv31)
	client.on_connect = on_connect
	client.on_message = on_message
	client.on_disconnect = on_disconnect
	print "start connect"
	ret = client.connect(MQTT_SERVER_IP, 1883, 60)
	# Blocking call that processes network traffic, dispatches callbacks and
	# handles reconnecting.
	# Other loop*() functions are available that give a threaded interface and a
	# manual interface.
	counter = 0 
	while 1:
		try:
			ret = client.loop(timeout=0.01, max_packets=1)
			if ret != 0 :
				client.connect(MQTT_SERVER_IP, 1883, 60)
			
			if counter == 100 :
				client.publish("iiot/keep_alive", \
					prototype.json_keep_alive(meta_data.DEVICE_ID,ssid=AP_SSID,ip=network_parameter.get_ip_address(bind_interface)))
				counter = 0
			counter += 1
		except :
			print "retry"
			time.sleep(1)
			continue

	print "stop connect"

import sys
if len(sys.argv) == 2:
	bind_interface = sys.argv[1]
else :
	print "Usage : python proxy_connetionless.py [interface]"
	exit()

start_mqtt_loop()