import socket
import time
import threading
import os

host = "localhost"
port = 5050
client = socket.socket()
running = None
connected = None

client.connect((host,port))


def start_connection():
    global running
    global connected
    try:
        name = input("Enter your name: ")
        client.send(name.encode('utf-8'))
        
        rec_thread = threading.Thread(target=receive())
        rec_thread.daemon = True
        rec_thread.start()
        
        running = True
        connected = True
        
    except:
        print("Server connection failed, closing connection...")
        time.sleep(2)
        client.close()
    
   
    
    


# sendMsg = input("Would you like to bid on the Car? (Y/N)")
# client.send(sendMsg.encode('utf-8'))
# # Reply from server for price:
# print(client.recv(1024).decode('utf-8'))


def receive():
    global running
    global connected
    while True:
        try:
            msg = client.recv(1024).decode('utf-8')
            if msg == "START":
                price = input("Enter the bidding price for the item: ")
                client.send(price.encode('utf-8'))
            elif msg == "STOP":
                print("Time's up, calculating winner...")
            elif msg == "Q":
                print("Server quit unexpectedly, closing connection...")
                time.sleep(3)
                os._exit(0)
                break
            else:
                print(msg)
            
        except (ConnectionRefusedError, BrokenPipeError) as e:
            print(f"Connection error: {e}")
            print("Closing connection")
            client.close()
            os._exit(0)
        except Exception as e:
            print(f"Unexpected error: {e}")
            client.close()
            os._exit(0)


start_connection()





# # List of dictionaries of items
# items = [
#     {"Item01", 2, 400},
#     {"Item02", 4, 500},
#     {"Item03", 2, 400},
#     {"Item04", 1, 250},
#     {"Item05", 1, 300},
#     {"Item06", 4, 477},
#     {"Item07", 2, 357},
#     {"Item08", 1, 156},
#     {"Item09", 1, 801},
#     {"Item10", 1, 401}
# ]

# Names = []

# # Bidding begins
# for i in range(0,10):
#     for j in range(0,3):
#         print(items[i][j])
        
# # get price and number of units for an item
# def getHighestBid(items, item, units):
#     currentPrice = items[item][2] 
#     max = max(Bidders.values())
#     winner = Bidders.keys()
            
#     print(f"The winner is {winner} for the {item} for ${max} for {units}")

# # also from which client it is 
# # if it is higher than the current price update the table and rebroadcast it to all

# getHighestBid(items, 5, 2)
# import time

# def countdown(mtime):
#     # mtime = 60
#     for x in range(mtime, -1, -1):
#         seconds = x % 60
#         minutes = int(x/60) % 60
#         print(f"\r{minutes:02}:{seconds:02}", end="", flush=True)
#         time.sleep(1)
    
#     print("\nTIME'S UP!")
    
    
# countdown(20)




