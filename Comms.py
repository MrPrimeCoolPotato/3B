import socket

#Main for server
def DataMain():

    #Creat socket for server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket created")

    #setup socket so it reconects if there is an error
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    #bind socket to IP = 
    sock.bind(("127.0.0.1", 50007))
    print("Socket bind complete")

    #listen for connection
    sock.listen()
    print("Socket now listening")


    #Creat socket for robot
    clientSock, addr = sock.accept()
    print("Connection from", addr)

    #Recive data from robot
    while True:
        data = clientSock.recv(1024)
        if data:
            dataDecoded = data.decode("utf-8")
            print(dataDecoded)
        

    
#Data output and send to robot
def Senddata(input, clientSock):
    DataToRobot = input("utf-8")
    if DataToRobot:
        clientSock.sendall(DataToRobot)

def DataFromRobot(dataDecoded):
    return dataDecoded

