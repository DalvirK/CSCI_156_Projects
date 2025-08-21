# Terminal Breakout-group Chat Room
Client/Server program written in Python.

Clients consist of a user and administrator (student and teacher respectively for this project). Administrators (admins) have additional breakout-group privileges including creation and deletion.

# Requirements
- Python 3.0+

# Quickstart
NOTE: clients may only connect to the server on the same network

1. Run `python BRP_server.py` on a machine terminal. The program will automatically start a server and create the chat-room structure, starting with room 'main'. It will also start listening for client connections.
2. Run `python BRP_client.py` on another machine terminal and follow the prompts.
   ***Ensure that the client connects to the correct server hostname/port.*** You may need to manually tweak the `HOST` variable in the source code. If you know the host's machine name you can easily do this with `socket.gethostbyname()`.
3. Upon successful client connection, the client will be brought to the server's 'main' room.
4. To disconnect your client from the server, use `!quit`. 

# Commands
Clients may send requests to the server as commands indicated by the command prefix. The default prefix is '!' but may be changed per preference in the source code. 

Global commands (both user and admins):
- `room` - returns the room name that the client is currently in
- `list` - returns a list of available rooms in the server
- `join <room>` - move the client to *room* if it exists
- `whisper <client> <message>` - sends *message* to only *client*
- `quit` - disconnect from the main server and broadcast a message to all rooms.

Admin commands:
- `create <room_name>` - create a room with name _room_name_ in the server
- `close <room_name>` - close a room with name _room_name_ if it exists in the server
- `closeall` - close all rooms in the server except for the main room
- `broadcast <message>` - send _message_ to all rooms in the server as a broadcast message

NOTE: For client disconnection, it is recommended to use the `quit` command. Please avoid command-line program termination via `CTRL-C`, etc.  
