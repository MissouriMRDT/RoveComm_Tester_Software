import socket
import struct

'''
local_host_ip = "127.0.0.1"
test_var = 0xff

test_byte = struct.pack('L', test_var)

RoveCommSocket = socket.socket(type = socket.SOCK_DGRAM)
RoveCommSocket.bind(("", 11000))

RoveCommSocket.sendto(test_byte, (local_host_ip, 11000))

bytes, address = RoveCommSocket.recvfrom(1024)
print (test_byte)
print (bytes, address)
print (struct.unpack('L', test_byte))
'''

ROVECOMM_PORT = 11000
ROVECOMM_VERSION       = 1        #ToDo: Change in RC2
ROVECOMM_HEADER_FORMAT = ">BHBHH"
ROVCOMM_SEQ_NUM = 0x0F49
ROVECOMM_FLAGS  = 0x00

ROVECOMM_SUBSCRIBE_REQUEST   = 3
ROVECOMM_UNSUBSCRIBE_REQUEST = 4

class RoveCommEthernetUdp:
	def __init__(self, port=ROVECOMM_PORT):
		self.rove_comm_port = port
		self.subscribers = []
		#RC2: add last_data_type, last_data_count
		
		self.RoveCommSocket = socket.socket(type = socket.SOCK_DGRAM)
		self.RoveCommSocket.bind(("", self.rove_comm_port))
		
	def write(self, data_id, data_size, data): #RC2: add data_type, data_count
		if not isinstance(data, bytes):	
			raise ValueError('Must pass data as a packed struct, Data: ' + str(data))
		
		rovecomm_packet = struct.pack(ROVECOMM_HEADER_FORMAT, ROVECOMM_VERSION, ROVCOMM_SEQ_NUM, ROVECOMM_FLAGS, data_id, data_size) + data #Todo: Debug
		
		for subscriber in self.subscribers:
			self.RoveCommSocket.sendto(rovecomm_packet, (subscriber))
		
	def writeTo(self, data_id, data_size, data, ip_address, port=ROVECOMM_PORT): #RC2: add data_type, data_count
		if not isinstance(data, bytes):	
			raise ValueError('Must pass data as a packed struct, Data: ' + str(data))
		
		rovecomm_packet = struct.pack(ROVECOMM_HEADER_FORMAT, ROVECOMM_VERSION, ROVCOMM_SEQ_NUM, ROVECOMM_FLAGS, data_id, data_size) + data #Todo: Debug
		
		self.RoveCommSocket.sendto(rovecomm_packet, (ip_address, port))
		
	def read(self):
		packet, remote_ip = self.RoveCommSocket.recvfrom(1024)
		header_size = struct.calcsize(ROVECOMM_HEADER_FORMAT)
		
		rovecomm_version, seq_num, flags, data_id, data_size = struct.unpack(ROVECOMM_HEADER_FORMAT, packet[0:header_size])
		data = packet[header_size:]
		
		if(data_id == ROVECOMM_SUBSCRIBE_REQUEST):
			if(self.subscribers.count(remote_ip) == 0):
				self.subscribers.append(remote_ip)
		elif(data_id == ROVECOMM_UNSUBSCRIBE_REQUEST):
			if(self.subscribers.count(remote_ip) != 0):
				self.subscribers.remove(remote_ip)
		
		return (data_id, data_size, data)
			
	#def readFrom ToDo: Change to getLastIp for C++ and Python
