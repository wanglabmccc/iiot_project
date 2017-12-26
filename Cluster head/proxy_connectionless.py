'''
Created on 2013-9-24
Implementint asynchronous I/O using select().The program starts out by creating a nonblocking
TCP/IP socket and configuring it to listen on an address
@author: mupeng
'''
import select
import socket
import Queue
import time
import struct
import meta_data

import network_parameter

IIOT_SERVER_ADDR = meta_data.IIOT_SERVER_ADDR
bind_interface = None

current_milli_time = lambda: int(round(time.time() * 100000))

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

global proxy_server

import sys
if len(sys.argv) == 2:
	bind_interface = sys.argv[1]
else :
	print "Usage : python proxy_connetionless.py [interface]"
	exit()

try:
	global proxy_server
	# create a socket
	proxy_server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	proxy_server.setblocking(False)
	# set option reused
	proxy_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR  , 1)
	 
	proxy_server_address= (network_parameter.get_ip_address(bind_interface),6666)
	proxy_server.bind(proxy_server_address)
	 
	proxy_server.listen(10)
	print "start listen..."
except:
	print "Error: unable to init"
	 
# sockets from which we except to read
inputs = [proxy_server]
 
# sockets from which we expect to write
outputs = []
 
# Outgoing message queues (socket:Queue)
tmp_queues = {}
message_queues = Queue.Queue()
 
# A optional parameter for select is TIMEOUT
timeout = 0

#####################################
# read the factor size from MQTT
import thread
import os
global factor_size
factor_size = 3
global refresh_factor_size
refresh_factor_size = factor_size

def set_factor_size():
	while True:
		try:
			file = open('/root/factor_size', 'r')
			global refresh_factor_size
			tmp = float(file.readline())
			if tmp > 0:
				refresh_factor_size = tmp
				file.close()
				os.remove('/root/factor_size')
				print "change factor size" + str(refresh_factor_size)
			else :
				file.close()
		except:
			#print "retry."
			time.sleep(1)
			continue
		

try:
	thread.start_new_thread( set_factor_size, () )
except:
	print "Error: unable to start thread"

#####################################

#####################################
# get aggreation delay
# open simulation record file
# init variable
flag_log = 1
simulation_buffer = {}
#####################################


# send to iiot server from message queue
def send_data():
	global factor_size
	global refresh_factor_size
	next_msg = ""
	while True:
		try:
			iiot_server_address = (IIOT_SERVER_ADDR,7777)
			iiot_server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			iiot_server.connect(iiot_server_address)
			break
		except:
			print "retry..."
			time.sleep(1)

	#########################
	# get aggreation delay
	# get packet key

	keys = []

	#########################
	for i in range(message_queues.qsize()):
		tmp = message_queues.get()
		next_msg += (tmp + "\n")

		#########################
		# get aggreation delay
		# record send buffer

		keys.append(tmp)

		#########################


	# refresh factor size here
	if (refresh_factor_size != factor_size):
		factor_size = refresh_factor_size
	#print "send message ---> "+ next_msg

	#########################
	# get aggreation delay
	# record send buffer
	pre_time = current_milli_time()-offset
	#########################
	
	iiot_server.send(next_msg)

	#########################
	# get aggreation delay
	# record send buffer

	now_time = current_milli_time()-offset
	for key in keys:
		if flag_log == 1:
			f_simulation = open("/root/"+meta_data.DEVICE_ID+".csv","a")
			f_simulation.write(key+","+str(simulation_buffer[key])+","+str(pre_time)+","+str(now_time)+"\n")
		del simulation_buffer[key]
	#########################

	iiot_server.close()


 
while inputs:
	#print "waiting for next Client"
	try:
		readable , writable , exceptional = select.select(inputs, outputs, inputs)
	 	#print factor_size
		# When timeout reached , select return three empty lists
		if not (readable or writable or exceptional) :
			print "Time out ! "
			break
		for s in readable :
			if s is proxy_server:
				# A "readable" socket is ready to accept a connection
				connection, client_address = s.accept()
				#print "	connection from ", client_address
				connection.setblocking(0)
				inputs.append(connection)
				tmp_queues[connection] = ""			
			else:
				tmp_queues[s] += s.recv(1024)
				# print "data ---> " + tmp_queues[s]
				if tmp_queues[s]:
					lines = tmp_queues[s].split('\n')
					flag = 0
					if not tmp_queues[s].endswith('\n'):
						tmp_queues[s] = lines[len(lines)-1]
					else:
						# print "almost clear !\n"
						tmp_queues[s] = ""

					del lines[len(lines)-1]

					for line in lines:
						#print "message put =>" + line
						msg = line+","+meta_data.DEVICE_ID
						message_queues.put(msg)
						##################################
						# get aggreation delay

						simulation_buffer[msg] = current_milli_time()-offset

						##################################
						# print "queue size [" + str(message_queues.qsize()) + "]\n"
						if message_queues.qsize() >= factor_size:
							send_data()				
				else:
					# Interpret empty result as closed connection
					# print "closing", s.getpeername()
					inputs.remove(s)
					del tmp_queues[s]
					s.close()
		for s in exceptional:
			print " exception condition on ", s.getpeername()
			# stop listening for input on the connection
			if s in inputs:
				inputs.remove(s)
				del tmp_queues[s]
			s.close()
			# Remove message queue
	except :
		continue

