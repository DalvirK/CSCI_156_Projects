
# TO DO:
# deal with clients with the same bid amount
# handle a client not entering any data at all (at all for the bidding(?))
    # Or if the client doesn't want to bid on an item they can write 0(we will skip them(?))

import socket
import time
import threading
import os
import tkinter as tk

HOST = "localhost"
PORT = 5050
ADDRESS = (HOST, PORT)
item = 0
time_up = ""

Bidder_Names = []
Bidder_Connections = []

Records = [] # list of dictionaries of records
Items = [
    {"Name":"Car", "Price":200, "Units":2}, # item_number = 0
    {"Name":"Air", "Price":200, "Units":1},
    {"Name":"Van", "Price":200, "Units":2} ]

server = socket.socket()

server.bind(ADDRESS)
print("Server started...")
server.listen()

# Timer for 1 min for each bid:
def countdown(mtime):
    global time_up
    for x in range(mtime, -1, -1):
        seconds = x % 60
        minutes = int(x/60) % 60
        print(f"\r{minutes:02}:{seconds:02}", end="", flush=True)
        #broadcast(f"\r{minutes:02}:{seconds:02}".encode('ascii'))
        time.sleep(1)
    
    #broadcast("\nTIME'S UP!")
    time_up = "TIME"
    Winner()

thread_timer = threading.Thread(target=countdown,args=(20,))
stop_thread = threading.Event()
  

# Will send message to all clients
def broadcast(message):
    for connection in Bidder_Connections:
        connection.send(message.encode('utf-8'))
        
def broadcastMinusOne(message, excluded_name):
    for name in Bidder_Names:  # clients is a list of all connected client sockets
        try:
            if name == excluded_name:
                continue
            else:
                connection = Bidder_Names.index(name)
                Bidder_Connections[connection].send(message.encode('utf-8'))
                
        except Exception as e:
            print(f"Error sending to client: {e}")  
            
def remove_connection(connection):
    if connection in Bidder_Connections:
        index = Bidder_Connections.index(connection)
        name = Bidder_Names[index]
        Bidder_Connections.remove(connection)
        Bidder_Names.remove(name)
        connection.close()
        broadcast(f"{name} has left the server.")
        print(f"{name} has left the server")
        
    # Check if all clients have left
    if not Bidder_Connections:
        print("All clients have disconnected. Closing the server.")
        connection.close()
        stop_thread.set()  # Signal the timer thread to stop
        thread_timer.join() 
        os._exit(0)
        

# This function will take client input for bids
# Store records of bidder name, item and price
# Call the function to find the highest bidder     
def handle_client(connection):
    global time_up
    while True:
        try:
            message = connection.recv(1024).decode("utf-8")   # When client sends a message to server
            if not message:
                remove_connection(connection)
                break
            
            global item
            product = Items[item]["Name"]
            new_price = int(message) # convert message to integer
            
            find_name = Bidder_Connections.index(connection) # get the index of the connection from list of connections
            name = Bidder_Names[find_name] # get the name of the client of the connection
            # create record of the clients input: client name + item + price 
            record = {"name": name, "item": product, "price": new_price}
            Records.append(record)
            
            print(record)    
            
        except Exception as e:
            print(f"handle_client function didn't work because: {e}")
           

def  Winner():
    broadcast("STOP") # to stop taking input for bidding
    global item 
    price = Items[item]["Price"] # getting current price
    count = continue_if()
    
    if all(record["price"] < price for record in Records): # If both bids are lower than the initial price:
            broadcast("All prices are less than the specified price.")
            # GO ON TO NEXT ITEM(?)
            # RESTART THE SAME ITEM BIDDING?
    
    for i in range(len(Records) - 1): 
        if Records[i]["price"] == Records[i+1]["price"]:
            broadcast("It was a tie!")
            # GO ON TO NEXT ITEM(?)
            # RESTART THE SAME ITEM BIDDING?
    
    # find highest bidder:
    for r in range(len(Records)):
        if Records[r]["price"] > price:
            current_winner = Records[r]["name"]
            price = Records[r]["price"]
  
    time.sleep(3) # Suspense
    broadcast(f"Winner of {Records[r]["item"]} is {current_winner} for a bid of {price}")
    time.sleep(3) # Time to read
    
    # updating the units of the item:
    if Items[item]["Units"] > 1:
        #print(f"Before: {Items[item]["Units"]}")
        Items[item]["Units"] = Items[item]["Units"] - 1
        Bidding()
        #print(f"After: {Items[item]["Units"]}")
    elif count > 0: 
        Items[item]["Units"] = 0
        count = continue_if()
        
        if count == 0:
            print("The bidding is completed!")
            broadcast("The bidding is completed!")
            # DO SOMETHING NOW LIKE ENDING CONNECTION(?)
        else:
            item += 1 # Updating the item to go to next item
            Bidding()


def Bidding():
    global time_up
    output = ""
    count = continue_if() # get the total count 
                
    if count > 0: 
        broadcast('\nWe are bidding the following items:')
        time.sleep(0.1)
        
        output += f"{'Item Number':<15}{'Item Name':<15}{'Units':<10}{'Price':<5}\n"
        output += "-" * 50
        for i in range(len(Items)):
            output += f"\n{i:<15}{Items[i]['Name']:<15}{Items[i]['Units']:<10}{Items[i]['Price']:<10}\n"
        broadcast(output)
    
        # While the 1 minute is running we are counting how many clients made a response:
        broadcast(f"We are starting the bid on one unit of the item: {Items[item]["Name"]}, Current Price: {Items[item]["Price"]}, You have 1 min to place a bid:")
        time.sleep(0.1)
        
        thread_timer = threading.Thread(target=countdown, args=(20,))
        thread_timer.start()
        
        broadcast("START")

    
# This function is used to track the 
# number of items available across 
# all products. The function helps 
# to keep track of whether there are 
# still units available for bidding
def continue_if():
    count = 0
    for item in Items:
        count = count + item["Units"]
    #print(f"total items in stock: {count}")
    
    return count
    

# Will create the connection between client and server
def receive():
    while True:
        try:
            connection, address = server.accept()
        
            # Send we are connected:
            name = connection.recv(1024).decode('utf-8')
            print(f"{name} Connected: {address}")
            
            Bidder_Connections.append(connection)  # Store the connection as same index as below
            Bidder_Names.append(name) # Store the name at same index as above
            msg = f"{name} has connected."
            
            broadcastMinusOne(msg, name)
            connection.send(f"Connected to server".encode("utf-8"))
            
            recv_thread = threading.Thread(target=handle_client, args=(connection,))  
            recv_thread.start()
            
            # Make sure there are at least four clients before beginning
            if (len(Bidder_Connections) < 2):
                broadcast(f"...Waiting for at least 4 bidders, current bidder count: {len(Bidder_Connections)}...")
                time.sleep(0.1)   
            else:
                Bidding()
        except:
            print("Error occurred")
            broadcast("Q")
            #connection.close()
            #stop_thread.set()  # Signal the timer thread to stop
            #thread_timer.join() 
            os._exit(0)
            break
        
        
    
receive() 
            
