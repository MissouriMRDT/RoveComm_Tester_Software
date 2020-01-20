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
file.write('Time,Delta,Dela Prev,Data Id,Data Type,Data Count,Ip Address,Data\n')

ip_fourth_octet = input("IP Fourth Octet:")
data_id = input("Data ID:")

#Subscribe
packet = RoveCommPacket(ROVECOMM_SUBSCRIBE_REQUEST, 'b', (), ip_fourth_octet)
RoveComm.write(packet)

last_time = datetime.datetime.now()

while(1):
	packet = RoveComm.read()
	if(packet.data_id == int(data_id)):
		retrieved_time = datetime.datetime.now()
		elapsed_time = (retrieved_time-start_time).total_seconds()
		delta_time = (retrieved_time-last_time).total_seconds()
		last_time = retrieved_time
		
		print(delta_time)
		packet.print()
		
		file.write(str(retrieved_time)+','
						+str(elapsed_time)+','
						+str(delta_time)+','
						+str(packet.data_id)+','
						+str(packet.data_type)+','
						+str(packet.data_count)+','
						+str(packet.ip_address).replace(',', ';')+','
						+str(packet.data)+'\n')
		
	