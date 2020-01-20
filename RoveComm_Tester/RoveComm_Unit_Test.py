import time
from RoveComm_Python import RoveCommPacket, RoveCommEthernetTCP
rovecomm = RoveCommEthernetTCP()

data = (1,2,3,4)
packet = RoveCommPacket(int(9000), 'b', data, '99', 11006)

while True:
    rovecomm.write(packet)
    time.sleep(2)
