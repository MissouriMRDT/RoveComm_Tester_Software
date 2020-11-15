# RoveComm Communication Tester
A GUI to send and recieve RoveComm packets for communication tests.

## Setup
Make sure your computer is connected to the device's network. Most commonly, this is a direct ethernet cable from your laptop to the microcontroller, but this varies. Any standard networking devices can exist in that link, as long as the IP address of the device(s) is reachable. The tester assumes the network uses addresses within 192.168.1.0 to 192.168.1.255, which means the rovecomm device(s) you communicate with must have an IP address within that range.

## Download

Executables for this program exist in the releases section of this repository, [located here](https://github.com/MissouriMRDT/RoveComm_Tester_Software/releases).

Depending on your operating system, you'll download the Microsoft Windows EXE or Linux executable file.

## Usage

### Sender

#### Details

Each row within the sender table represents one packet definition. Fill in the packet details and check the enable box to activiate the send button.

There are two ways to send a packet(s) using Sender:
- Manually click the send button
- Utilize the rate input field to send every so milliseconds

Each piece of text input will be red when there is a known issue with that value. If any value is red, it's almost certain the packet will not send. The send button will also indicate this in the event a packet is unable to send. Assume your packet is valid and has been sent when the send button remains the default color when attempting to send. 

Across the top exists a "Add Send Row" button that adds additional packet definition rows to the interface.

The "Load Configs" and "Write Config" buttons allow pre-written packet setups to be loaded into the interface and saved into JSON files. "Write Config" will take all rows currently in the interface and write them to one file for use later using "Load Configs". This feature is to add convenience when communicating using similar packets for multiple sessions. We recommend using it to define a device config file. 

#### Troubleshooting

If the device you are communicating with appears to not recieve the packet, be sure to check the IP address and dataID of the packet you are sending in comparison to the device in question. A mismatch of these two values is more often than not the cause.

If the device recieves a packet, but does not do the expected behavior, check your packet data construction in Sender as well as the device's interpretation of the packet. Likely, there is a difference between these two.

If you are unable to communicate to a device correctly and you have troubleshooted through the two statements above, call for help. It's likely an issue above your paygrade.

### Reciever

#### Details

As packets are recieved on the device, the reciever table will populate with the contents and source IP address.

To setup Reciever to get packets, you must subscribe to the IP address of the device(s) you wish to listen to by typing in an octet and clicking the button. Once subscribed, packets that the device sends will be sent to Reciever and be populated in the table.

You can filter the packets that are populated through the filter field. 
It looks at these fields to find a match:
- Source IP
- DataID
- DataType
- Data

Using the logging checkbox, all new entries in the recieve table will be written into a comma seperated values (CSV) file. This is only effective for packets recieved after the box is checked. The output file will be named with a timestamp of the recording start.

Toggling the autoscroll box will do just that: stop scrolling of the recieve table. This is useful when the packets are coming in quickly and you'd rather take a yonder at a particular one.

#### Troubleshooting

If no packets are being recieved, try these measures:
- Attempt a resubscription to the device in question. It's possible the subscription packet was not recieved.
- Ensure the packet you are trying to capture can pass your filter statement. This is done by checking if the packet is recieved if the filter is removed.

## Build Information

The program executables are built with pyinstaller

```
pyinstaller -F --icon=rover_swoosh.ico RoveComm_Tester.py
```
