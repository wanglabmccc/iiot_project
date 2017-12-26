import meta_data

from subprocess import check_output
def send_command(str):
    print check_output(str,shell=True)

def set_wifi_state(mode,ssid,password):

	command_interface = "uci set wireless.@wifi-iface[0]"
	command_type ={ "encryption": "psk2", \
	               "ssid":ssid, \
	               "key": password, \
	               "mode": mode }
	command_keys = command_type.keys()
	command_save= "uci commit wireless"
	command_restart= "wifi" 
	for key in command_keys:
		str = command_interface + '.' + key + "=\"" + command_type[key]+"\""
		send_command(str)
	send_command(command_save)
	send_command(command_restart)
if __name__ == "__main__":
	set_wifi_state("sta","MJ onair",'gugululu')


