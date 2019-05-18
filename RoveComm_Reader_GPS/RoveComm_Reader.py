'''
pyinstaller RoveComm_Reader.py --onefile --icon=rover_1wP_icon.ico

'''
from RoveComm_Python import *
import datetime
import os

try:
	os.mkdir('0-Data Outputs')
except:
	pass
	
start_time = datetime.datetime.now()

RoveComm = RoveCommEthernetUdp()

file = open('0-Data Outputs/'+str(start_time).replace(':', '_')+'.csv', 'w')

ip_fourth_octet = "136"
data_id = "5100"

#Subscribe
packet = RoveCommPacket(ROVECOMM_SUBSCRIBE_REQUEST, 'b', (), ip_fourth_octet)
RoveComm.write(packet)

last_time = datetime.datetime.now()

file.write("Elapsed Time,Delta,Longitude,Latitude\n")

print("starting read");

while(1):
	packet = RoveComm.read()
	if(packet.data_id == int(data_id)):
		retrieved_time = datetime.datetime.now()
		elapsed_time = (retrieved_time-start_time).total_seconds()
		delta_time = (retrieved_time-last_time).total_seconds()
		last_time = retrieved_time
		
		file.write(str(elapsed_time) + "," + str(delta_time) + "," + str(-packet.data[0]/10000000) + "," + str(packet.data[1]/10000000) + "\n")
		print(delta_time)
		packet.print()
		
	