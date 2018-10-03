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
ROVECOMM_HEADER_FORMAT = ">HBB"

ROVECOMM_SUBSCRIBE_REQUEST   = 3
ROVECOMM_UNSUBSCRIBE_REQUEST = 4

types_int_to_byte  = {
						1:'b',
						2:'B',
						3:'h',
						4:'H',
						5:'l',
						6:'L',
					  }
					  
types_byte_to_int  = {
						'b':1,
						'B':2,
						'h':3,
						'H':4,
						'l':5,
						'L':6,
					  }
					  
					  
class RoveCommPacket:
	def __init__(self, data_id=0, data_type='b', data=(), ip_octet_4= '', port = ROVECOMM_PORT):
		self.data_id = data_id
		self.data_type = data_type
		self.data_count = len(data)
		self.data = data
		if(ip_octet_4 != ''):
			self.ip_address = ('192.168.1.' + ip_octet_4, port)
		else:
			self.ip_address = ('0.0.0.0', port)
		return
		
	def SetIp(self, address):
		self.ip_address = (address, self.ip_address[1])	
	
	def print(self):
		print('----------')
		print('{0:6s} {1}'.format('ID:', self.data_id))
		print('{0:6s} {1}'.format('Type:', self.data_type))
		print('{0:6s} {1}'.format('Count:', self.data_count))
		print('{0:6s} {1}'.format('IP:', self.ip_address))
		print('{0:6s} {1}'.format('Data:', self.data))
		print('----------')
			

class RoveCommEthernetUdp:
	def __init__(self, port=ROVECOMM_PORT):
		self.rove_comm_port = port
		self.subscribers = []
		
		self.RoveCommSocket = socket.socket(type = socket.SOCK_DGRAM)
		self.RoveCommSocket.setblocking(False)
		self.RoveCommSocket.bind(("", self.rove_comm_port))
	
	def write(self, packet):
		if not isinstance(packet.data, tuple):	
			raise ValueError('Must pass data as a list, Data: ' + str(data))
					
		rovecomm_packet = struct.pack(ROVECOMM_HEADER_FORMAT, packet.data_id, types_byte_to_int[packet.data_type], packet.data_count)
		
		for i in packet.data:
			rovecomm_packet = rovecomm_packet + struct.pack('>' + packet.data_type, i)
			
		for subscriber in self.subscribers:
			self.RoveCommSocket.sendto(rovecomm_packet, (subscriber))
		
		if(packet.ip_address != ('0.0.0.0', 0)):
			self.RoveCommSocket.sendto(rovecomm_packet, packet.ip_address)
		
	def read(self):
		#try:
			packet, remote_ip = self.RoveCommSocket.recvfrom(1024)
			header_size = struct.calcsize(ROVECOMM_HEADER_FORMAT)
		
			data_id, data_type, data_count = struct.unpack(ROVECOMM_HEADER_FORMAT, packet[0:header_size])
			data = packet[header_size:]
		
			if(data_id == ROVECOMM_SUBSCRIBE_REQUEST):
				if(self.subscribers.count(remote_ip) == 0):
					self.subscribers.append(remote_ip)
			elif(data_id == ROVECOMM_UNSUBSCRIBE_REQUEST):
				if(self.subscribers.count(remote_ip) != 0):
					self.subscribers.remove(remote_ip)
			
			data_type = types_int_to_byte[data_type]
			data = struct.unpack('>' + data_type*data_count, data)
			
			returnPacket = RoveCommPacket(data_id, data_type, data, '')
			returnPacket.ip_address = remote_ip
			return returnPacket
			
		#except:
			returnPacket = RoveCommPacket()
			return(returnPacket)
			
	#def readFrom ToDo: Change to getLastIp for C++ and Python
