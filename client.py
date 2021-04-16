import socket

SERVER = "10.9.186.13"
PORT = 15555

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))
client.sendall(bytes("This is from Client",'UTF-8'))
IP = client.getsockname()[0]
print(IP)

while True:
	in_data =  client.recv(1024)
	print("From Server :" ,in_data.decode())
	out_data = input()
	client.sendall(bytes(out_data,'UTF-8'))
	if out_data=='bye':
		break


client.close()
