import socket
import threading
import time

# Get port and server info
PORT = 8000
SERVER = socket.gethostbyname(socket.gethostname())


# Store client info
client_sockets = {}

# Store rooms for multicasting/breakout room implementation
# Initialize with the main room
rooms = { 'main': [] }

# Command prefix
command_prefix = '!'

def listRooms():
    """Returns a list of available rooms
    Return:
        output (string)
    """
    output = ""
    for key in rooms:
        output += key + "\n"
    return output

def createRoom(room_name):
    """Create an empty room
    Args:
        room_name (string): name of the room 
    Return:
        message (string): confirmation string to send to client
    """

    # Check if room exists
    if room_name in rooms:
        return "Room already exists"

    # Use room_name is key and give it an empty list
    rooms[room_name] = []
   
    return "Room created" 

def closeRoom(client_socket, addr, room_name):
    """Thread function for removing an existing room 
    Args:
        client_socket (socket): client socket that sent the message
        addr (string): address of client socket
        room_name (string): name of the room
    """
    if room_name not in rooms:
        client_socket.send(f"{room_name} does not exist".encode('utf-8'))
    else:
        for i in reversed(range(5)):
            broadcast(f"This room will be closed in {i} seconds...", room_name)
            time.sleep(1)

        for client, addr in rooms[room_name][:]:
            client.send(moveClient(client, addr, 'main').encode('utf-8'))
        
        del rooms[room_name]
        client_socket.send(f"{room_name} closed".encode('utf-8'))
    
def closeRoomThreaded(client_socket, addr, room_names):
    """Close a list of rooms using threads
    Args:
        client_socket (socket): client socket that sent the message
        addr (string): address of client socket
        room_names (list[str]): list of rooms to be closed
    """
    if len(rooms) > 0:
        for room in room_names:
            close_thread = threading.Thread(target=closeRoom, args=(client_socket, addr, room))
            close_thread.start();

def moveClient(client_socket, addr, room_name):
    """Move client from one room to another
    Args:
        client_socket (socket): the client socket to be moved
        addr (string): address of the client socket
        room_name (string): name of the room 
    Return:
        message (string): confirmation string to send to client
    """
    
    # Check if room exists
    if room_name not in rooms:
        return "Room does not exist"

    # Remove client from client's room and broadcast to that room
    rooms[client_sockets[addr]['room']].remove((client_socket, addr))
    broadcast(f"{client_sockets[addr]['name']} has left the room", client_sockets[addr]['room'])

    # Add client to new room and change client's info
    client_sockets[addr]['room'] = room_name
    rooms[room_name].append((client_socket, addr))

    # Broadcast to new room
    broadcast(f"{client_sockets[addr]['name']} has joined the room", room_name, client_socket)

    # Send message to client that they have successfully joined the new room
    return f"You have joined room {room_name}"

def broadcast(message, room_name, client_except=None):
    """Sends a message to all clients in a room

    Args:
        message (string): Message to be broadcasted to
        room (string): name of the room to be broadcasted in 
        client_except (socket): Client socket which will not get the message (optional)
    """

    # Using room_name as key iterate through each client in the room
    for client, _ in rooms[room_name]:
        if client != client_except:
            client.send(message.encode('utf-8'))

def handle_command(client_socket, addr, split_message):
    """handle messages from the client that start with '!' (command)
    Args:
        client_socket (socket): the client socket that sent the command
        addr (string): aaddress of the client socket
        split_message (list[str]): message split into a list by space char
    """

    split_message[0] = split_message[0].lower()

    if split_message[0] == 'room':
        client_socket.send(client_sockets[addr]['room'].encode('utf-8'))
    elif split_message[0] == 'list':
        client_socket.send(listRooms().encode('utf-8'))
    elif split_message[0] == 'join' and len(split_message) > 1:
        client_socket.send(moveClient(client_socket, addr, split_message[1]).encode('utf-8'))
    elif split_message[0] == 'create' and len(split_message) > 1 and client_sockets[addr]['type']:
        client_socket.send(createRoom(split_message[1]).encode('utf-8'))
    elif split_message[0] == 'close' and len(split_message) > 1 and client_sockets[addr]['type']:
        closeRoomThreaded(client_socket, addr, split_message[1:])
    elif split_message [0] == 'closeall' and len(split_message) == 1 and client_sockets[addr]['type']:
        allrooms = list(rooms.keys())[1:]
        closeRoomThreaded(client_socket, addr, allrooms)
    elif split_message[0] == 'broadcast' and len(split_message) > 1 and client_sockets[addr]['type']:
        for room in rooms:
            broadcast(f"[BROADCAST] {client_sockets[addr]['name']}: " + ' '.join(split_message[1:]), room, client_socket)
        client_socket.send("Message broadcasted to all rooms".encode('utf-8'))
    else:
        client_socket.send("Unknown Command".encode('utf-8'))

def handle_message(client_socket, addr, message):
    """Handles messages from the client

    Args:
        client_socket (socket): The client socket that sent the message
        addr (string): Address of the client socket
        message (string): The client's message

    """

    if client_sockets[addr]['type']:
        client_type = "(INSTRUCTOR)" 
    else:
        client_type = "(STUDENT)"

    output = f"{client_type} {client_sockets[addr]['name']}: {message}"

    print(f"[{client_sockets[addr]['room']}] {output}")

    if message[0] != command_prefix:
        broadcast(output, client_sockets[addr]['room'], client_socket);
    else:
        handle_command(client_socket, addr, message[1:].split())
    
def handle_client(client_socket, addr):
    """Handles client connections via multithreading

    Args:
        client_socket (socket):
        addr (string): Address of the client
    """
    connected = True
    while connected:
        message = client_socket.recv(1024).decode('utf-8')
        if message:
            if message == "!quit":
                connected = False
                rooms[client_sockets[addr]['room']].remove((client_socket, addr))
                for room in rooms:
                    broadcast(f"{client_sockets[addr]['name']} has left", room)
                client_socket.close()
            else:
                handle_message(client_socket, addr, message)

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER, PORT))
    server_socket.listen(5)
    print(f"Server listening on port {PORT}")

    while True:
        client_socket, addr = server_socket.accept()

        client_info = client_socket.recv(1024).decode('utf-8')
        client_sockets[addr] = {
                'type': int(client_info[0]),
                'name': client_info[1:],
                'room': 'main'
                }

        rooms['main'].append( (client_socket, addr) )

        print(f"{client_sockets[addr]} connected from {addr}")
        for room in rooms:
            broadcast(f"{client_sockets[addr]['name']} has joined main room", room)

        client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))


        client_handler.start()

        

if __name__ == "__main__":
    start_server()

