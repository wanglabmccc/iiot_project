'''
Created on 2013-9-24
The example client program uses some sockets to demonstrate how the server
with select() manages multiple connections at the same time . The client
starts by connecting each TCP/IP socket to the server
@author: mupeng
'''
 
import socket
import select
import time
import struct
import meta_data
import sys
import math
import os

current_milli_time = lambda: int(round(time.time() * 100000))

print "Connect to the server"

flag_log_file = 1
arrival_rate = 8
 
socks = []
number_connection = 1

current_milli_time = lambda: int(round(time.time() * 100000))
ts = 0


############################################
# sync time by ntp
import ntplib
import thread
global offset
offset = 0

global client 
client = ntplib.NTPClient()
def sys_time():	
	while 1:
		while 1:
			try:		
				response = client.request(meta_data.NTP_SERVER_ADDR)
				ts = int(response.tx_time*100000)
				global offset
				offset = current_milli_time()-ts
				break
			except ntplib.NTPException:
				print "retry ntp"
				time.sleep(1)
		time.sleep(30)

try:
	response = client.request(meta_data.NTP_SERVER_ADDR)
	ts = int(response.tx_time*100000)
	offset = current_milli_time()-ts
except ntplib.NTPException:
	print "sync fail"

print offset
try:
	thread.start_new_thread( sys_time ,())
except:
	print "Error: unable to start thread"
############################################


############################################
# get temperture from arduino
import sys
from time import sleep
global temperture
temperture = "NaN"
sys.path.insert(0, '/usr/lib/python2.7/bridge')
 
from bridgeclient import BridgeClient as bridgeclient

def get_temperture():
	value = bridgeclient()
	global temperture
	while True:
		try:
		    temperture = value.get('temperture')
		    print str(temperture)
		except socket.error:
			continue
			time.sleep(1)
try:
	thread.start_new_thread( get_temperture ,())
except:
	print "Error: unable to start thread"
############################################


############################################
# set arriaval rate


global refresh_arrival_rate
refresh_arrival_rate = arrival_rate
def set_traffic_model():
	while True:
		try:
			file = open('/root/traffic_model', 'r')
			global refresh_arrival_rate
			tmp = float(file.readline())
			if tmp > 0:
				refresh_arrival_rate = tmp
				file.close()
				os.remove('/root/traffic_model')
				print "change traffic_model" + str(refresh_arrival_rate)
			else :
				file.close()
		except :
			#print "retry."
			time.sleep(1)
			continue
try:
	thread.start_new_thread( set_traffic_model, () )
except:
	print "Error: unable to start thread"


while 1:
	#print socks
	for i in range(number_connection):
		s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		#print "add"
		socks.append(s)
	for s in socks:
		while True:
			try:
				#read ip from mqtt
				try:
					file = open('/root/ap_ip', 'r') 
					server_address = (file.readline() ,6666)
					file.close()
				except IOError as e:
					print "I/O error({0}): {1}".format(e.errno, e.strerror)
				try:
					s.connect(server_address)
					pre_time = current_milli_time()
					s.send(meta_data.DEVICE_ID + "," + str(pre_time-offset) + "," + str(temperture) + "\n")
					############################################
					# get block delay
					if flag_log_file == 1:
						f_simulation = open("/root/"+meta_data.DEVICE_ID+".csv","a")
						f_simulation.write(str(meta_data.DEVICE_ID)+","+str(pre_time-offset)+","+str(current_milli_time()-offset)+"\n")
						f_simulation.close()
					############################################	
				except:
					None
				s.close()
				break
			except socket.error:
				print "socket error retry..."
				time.sleep(1)
	socks=[]

	import random
	rand_num = random.expovariate(arrival_rate)
	if refresh_arrival_rate != arrival_rate:
		arrival_rate = refresh_arrival_rate
	time.sleep(rand_num)