import threading
import socket
import time
import random
import tkinter as tk


# # list of items
# items_list = ["Apple", "Samsung", "Android", "Strawberry", "Truck", "Toyota", "Lincoln", "Presidency", "School", "Dictionary", "Robe", "House", "Home", "Chair", "Cookies", "EarPhones"]
# # 10 random items form item list
# #ten_items = random.sample(items_list, 10)
# ten_items = ["Apple", "Samsung", "Android", "Strawberry", "Truck", "Toyota", "Lincoln", "Presidency", "School", "Dictionary"]
# # 10 random prices in a list
# prices = random.sample(range(100, 250), 10)
# quantity = random.sample(range(1, 20), 10)
# # Dictionary:
# # Create a dictionary where each item has both price and quantity
# items = {item: {"price": price, "quantity": quantity} for item, price, quantity in zip(ten_items, prices, quantity)} # ChatGPT
# #print(items)


host = socket.gethostbyname(socket.gethostname()) # Gets local IP address of device
# host = "localhost"
port = 5050
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# client = Name: Location
clients = {}
# Name, Item number, Units, Bid
winners = []
items = [ # Item number, Name, Units, Price:
    {"Item_Number": 0, "Name": "Item01", "Units": 2, "Price": 400},
    {"Item_Number": 1, "Name": "Item02", "Units": 4, "Price": 500},
    {"Item_Number": 2, "Name": "Item03", "Units": 2, "Price": 400},
    {"Item_Number": 3, "Name": "Item04", "Units": 1, "Price": 250},
    {"Item_Number": 4, "Name": "Item05", "Units": 1, "Price": 300},
    {"Item_Number": 5, "Name": "Item06", "Units": 4, "Price": 477},
    {"Item_Number": 6, "Name": "Item07", "Units": 2, "Price": 357},
    {"Item_Number": 7, "Name": "Item08", "Units": 1, "Price": 156},
    {"Item_Number": 8, "Name": "Item09", "Units": 1, "Price": 801},
    {"Item_Number": 9, "Name": "Item10", "Units": 1, "Price": 401}
]
inputs = []

# Timer for 1 min for each bid:
def countdown(mtime):
    # mtime = 60
    for x in range(mtime, -1, -1):
        seconds = x % 60
        minutes = int(x/60) % 60
        print(f"\r{minutes:02}:{seconds:02}", end="", flush=True)
        broadcast(f"\r{minutes:02}:{seconds:02}".encode('ascii'))
        time.sleep(1)
    
    broadcast("\nTIME'S UP!".encode('ascii'))

    
# output = f"{'\nDescription':<15}{'Units':<10}{'Price':<10}\n"
# for item in items:
#     description, units, price = item
#     output += f"{description:<15}{units:<10}{price:<10}\n"
    
    
# send message to all clients from server
def broadcast(message): 
    for name in clients:  # clients is a list of all connected client sockets
        try:
            clients[name].send(message)  # Send the message to the client
        except Exception as e:
            print(f"Error sending to client: {e}") 
            print(message) 

def broadcastMinusOne(message, excluded_name):
    for name in clients:  # clients is a list of all connected client sockets
        try:
            if name == excluded_name:
                continue
            else:
                clients[name].send(message)  # Send the message to the client
                
        except Exception as e:
            print(f"Error sending to client: {e}")  


# Get msg from client and send to other client
def handle(client): # EDIT CODE LATER TO MAKE MORE YOU MADE
    while True:
        try: 
            message = client.recv(1024)
            broadcast(message)
        except (ConnectionResetError, BrokenPipeError) as e:
            # Handle cleanup if the client is disconnected
            for key, value in clients.items():
                if value == client:
                    name = key  # Get the key from the value
                    print(f"{name} has disconnected.")
                    del clients[name]  # remove the client from the clients dictionary
                    client.close()  # close the client connection
                    broadcast(f'{name} left the chat'.encode('ascii'))
                    
                    break
            #client.close() # close the client connection
            
            # Delete client from the dictionary
            # for key, value in clients.items():
            #     if value == clients:
            #         name = value
            #         print(name)
            #         break  # get key of value(client)
            # del clients[name] # delete the key-value pair using the key
            
            # broadcast(f'{name} left the chat'.encode('ascii'))
            # print(f"{name} has left the room")
            break
      
def bidding():
    broadcast('START'.encode('ascii'))
    while True:
        client, address = server.accept()
        price = client.recv(1024).decode('ascii')
        print(price)
        #for item in items:
        item = 0
        print("Bidding on item: 0, 1 unit")
        broadcast(f"""\nItem Number: {items[item]["Item_Number"]}
        Name:  {items[item]["Name"]}
        Unit: 1
        Price:  {items[item]["Price"]}""".encode('ascii'))
    
    
# This function connects the client with server
# Sets a name for the client      
def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}") # print to server
        
        client.send('NAME'.encode('ascii'))
        name = client.recv(1024).decode('ascii')
        
        clients[name] = client
        
        print(f'Name of the client is {name}')
        broadcastMinusOne(f'\n{name} joined the chat'.encode('ascii'), name)
        clients[name].send('Connected to the server'.encode('ascii'))
        
        # Make sure there are at least four clients before beginning-------------------------------------
        if (len(clients) < 1):
            broadcast(f"\nWaiting for at least 4 bidders, current bidder count: {len(clients)}".encode('ascii'))
        else:
            broadcast('\nWelcome to Bidding! We will begin in 1 minute\n'.encode('ascii'))
            countdown(10)
            bidding() # Go to bidding function
        
        
        # Bidding begins
        # for i in range(0,10):
        #     for j in range(0,3):
        #         print(item[i][j])
                
        # get price and number of units for an item

        # also from which client it is 
        # if it is higher than the current price update the table and rebroadcast it to all
        
        
        thread = threading.Thread(target=handle,args=(client,))
        thread.start()
        
        #thread_timer = threading.Thread(target=countdown_timer,args=(60,))

receive()



