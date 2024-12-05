import socket
import threading
import sys

PORT = 8000
SERVER = socket.gethostbyname(socket.gethostname())

client_name = input("Enter a name:\n> ").strip()

client_type = input("Enter 1 for instructor, 0 for student\n> ").strip()
while client_type != "1" and client_type != "0":
    client_type = input("Invalid input\n> ")

wThreadRunning = True
rThreadRunning = True

def receive(client_socket):
    global rThreadRunning
    while rThreadRunning:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(message)
            else:
                print("Unknown message")
                break
        except:
            print("You have disconnected from the server")
            break
    client_socket.close()
    rThreadRunning = False

def write(client_socket):
    global wThreadRunning, rThreadRunning 
    while wThreadRunning:
        message = input("> ")
        if message == "!quit":
            wThreadRunning = False
            rThreadRunning = False
            client_socket.send(message.encode('utf-8'))
            break
        client_socket.send(message.encode('utf-8'))
    client_socket.close()

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((SERVER, PORT))
    except:
        print("Server not open")
        sys.exit(1)
    print("Successfully connected to server")

    client_info = client_type + client_name
    client_socket.send(client_info.encode('utf-8'))

    receive_thread = threading.Thread(target=receive, args=(client_socket,))
    receive_thread.start()
    write_thread = threading.Thread(target=write, args=(client_socket,))
    write_thread.start()

    receive_thread.join()
    write_thread.join()


if __name__ == "__main__":
    start_client()
