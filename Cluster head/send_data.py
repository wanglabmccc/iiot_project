import meta_data
import socket
import time
import os
IIOT_SERVER_ADDR = "140.113.179.7"
while True:
	try:	
		client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		iiot_server_address = (IIOT_SERVER_ADDR,25000)
		client.connect(iiot_server_address)
		file = open("/root/"+meta_data.DEVICE_ID+".csv","r")
		file_name = meta_data.DEVICE_ID+".csv\n"
		client.send(file_name)
		l = file.read(1024)
		while (l):
			client.send(l)
			print('Sent ',repr(l))
			l = file.read(1024)
		file.close()
		os.remove("/root/"+meta_data.DEVICE_ID+".csv")
	except socket.error:
		print "retry."
		time.sleep(1)
		continue
	except IOError as e:
		print "retry."
		time.sleep(1)
		continue