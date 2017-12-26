import json

def json_keep_alive(device_id, **kwargs):
	message = {}
	if kwargs is not None:
		for key ,value in kwargs.iteritems():
			message[key] = value
		
	return_json = {'device_id': device_id, 'message': message}
	return json.dumps(return_json)

def json_traffic_model(device_id, **kwargs):
	message = {}
	key_type = ['type','interval']
	if kwargs is not None:
		for key, value in kwargs.iteritems():
			for _type in key_type:
				if key == _type :
					message[key] = value
	message['device_id'] = device_id
	return json.dumps(message)

def json_set_cluster_item(device_id, **kwargs):
	message = {}
	key_type = ['ssid','password','cluster_member','ap_ip']
	if kwargs is not None:
		for key, value in kwargs.iteritems():
			for _type in key_type:
				if key == _type :
					message[key] = value
	message['device_id'] = device_id
	return message

def json_set_cluster(*argv):
	message = []
	for arg in argv:
		message.append(arg)
	return json.dumps(message)

def json_get_cluster_parameter(device_id, **kwargs):
	message = {}
	key_type = ['load']
	if kwargs is not None:
		for key, value in kwargs.iteritems():
			for _type in key_type:
				if key == _type :
					message[key] = value
	return_json = {'device_id': device_id, 'clustering_parameter': message}
	return json.dumps(return_json)

def json_set_aggregator_item(device_id, **kwargs):
	message = {}
	key_type = ['factor_size']
	if kwargs is not None:
		for key, value in kwargs.iteritems():
			for _type in key_type:
				if key == _type :
					message[key] = value
	message['device_id'] = device_id
	return message

def json_set_aggregator(*argv):
	message = []
	for arg in argv:
		message.append(arg)
	return json.dumps(message)

def json_get_aggregator_parameter(device_id, **kwargs):
	message = {}
	key_type = ['arrival_rate']
	if kwargs is not None:
		for key, value in kwargs.iteritems():
			for _type in key_type:
				if key == _type :
					message[key] = value
	return_json = {'device_id': device_id, 'factor_parameter': message}
	return json.dumps(return_json)

if __name__ == "__main__":
	import sys
	print json_keep_alive(123,ssid="MJ onair")
	print json_traffic_model(123,type="period",interval=12)
	device_1_member = ['123','456']
	device_1 = json_set_cluster_item('device_1',ssid='test_ssid1' \
									 ,password='nopassword',cluster_member=device_1_member)
	device_2_member = ['234','345']
	device_2 = json_set_cluster_item('device_2',ssid='test_ssid2' \
									 ,password='nopassword',cluster_member=device_2_member)
	
	print json_set_cluster(device_1,device_2)
	print json_get_cluster_parameter(123,load='hungry')

	device_1_member = ['123','456']
	device_1 = json_set_aggregator_item('device_1',factor_size=24)
	device_2_member = ['234','345']
	device_2 = json_set_aggregator_item('device_2',factor_size=56)
	
	print json_set_aggregator(device_1,device_2)
	print json_get_aggregator_parameter(123,load='hungry')

