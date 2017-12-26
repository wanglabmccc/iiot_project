import sys
from time import sleep
sys.path.insert(0, '/usr/lib/python2.7/bridge')
 
from bridgeclient import BridgeClient as bridgeclient
value = bridgeclient()
 
while True:
	try:
	    tmp = value.get('temperture')
	    print str(tmp)
	except socket.error:
		time.sleep(1)
		continue