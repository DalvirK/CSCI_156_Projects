import threading
import socket

name = input("Enter your a name: ")

 #Each client program first connects with the server, receive the product information, and then repeat the bidding process. During each bidding, a client randomly choose one product and submit a higher than "current" price and waits to see if it wins. If it does not win, it will continue submitting higher price bid until it reaches its maximum acceptable price.
#The server should receive all bids and inform the results to each client. Your programs should continue until terminated "externally".

host = socket.gethostbyname(socket.gethostname()) # Gets local IP address of device
port = 5050
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

def receive():
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'NAME':
                client.send(name.encode('ascii'))
            elif message == 'START':
                price = input("Enter the price you ready to bid on this item: ")
                client.send(price.encode('ascii'))
            else:
                print(message, end="", flush=True)
        except:
            print("Error occurred")
            client.close()
            break
        

def write():
    while True:
        message = f'{name}: {input("")}' #always ask for new input
        client.send(message.encode('ascii'))
        

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()