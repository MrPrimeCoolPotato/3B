# Import libraries
from statemachine import *
import time 
from pipeLine import pipeLine
from socket import *
import VisionSM
import numpy as np
from OAKWrapper import OAKCamColorDepth

# Start of code

##Constants 
lowValueObjectA = 1000
highValueObjectA = 1999

lowValueObjectB = 2000
highValueObjectB = 4000

#controle values
lowValueControl = 5200
highValueControl = 10000

##############################################

class SetupServer(State): # 0 - SetupServer and wait for connection
    def Enter(self):
        print('State: SetupServer - Setting up server')

    def Execute(self):
        HOSTIP = '192.168.1.100'
        PORT = 5940

        self.stateMachine.serverSocket = socket(AF_INET, SOCK_STREAM)
        self.stateMachine.serverSocket.bind((HOSTIP, PORT))
        print('Socket bind complete')
        self.stateMachine.serverSocket.listen(1)
        print('Socket now listening')
        self.stateMachine.clientSock, addr = self.stateMachine.serverSocket.accept()
        print('Connection from', self.stateMachine, addr)        
        self.stateMachine.ChangeState(Initializing())



class Initializing(State): #10 - Initialize and wait for robot to be ready
    def Enter(self):
        print('State: Initializing - waiting for communication to be OK')

    def Execute(self):
        self.stateMachine.cam = OAKCamColorDepth()
        time.sleep(4)         
        self.stateMachine.clientSock.sendall('visionOK'.encode('utf-8')) #Sending data to robot
        time.sleep(1)
        print('Vision OK')
        self.stateMachine.ChangeState(Idle())



class Idle(State): # 20 - Idle waitong for robot to request data
    def Enter(self):
        print("Idle")

    def Execute(self):
        time.sleep(2)
        data = self.stateMachine.clientSock.recv(1024) #Reciving data from robot
        recvDataFromRobot = data.decode('utf-8')
        print('From robot:', recvDataFromRobot)
        if recvDataFromRobot == 'object Coords':
            self.stateMachine.ChangeState(FindAndSendCoordinates())
        
        elif recvDataFromRobot == 'readyToControl':
            self.stateMachine.ChangeState(Control())



class FindAndSendCoordinates(State): #30 - Find And Send Coordinates to robot
    def Enter(self):
        print("Finding Coordinates")
        time.sleep(0.5)

    def Execute(self): # Get coordinates from pipeLine convert to string and send to robot
        robotCoords = pipeLine(self.stateMachine.cam, findObject=True, controlObject=False) 
        
        dataA = str(robotCoords[0]) + ',' + str(robotCoords[1]) + ',' + str('-195') + ',' + str(robotCoords[2]) #Creating data to send to robot
        dataB = str(robotCoords[0]) + ',' + str(robotCoords[1]) + ',' + str('-185') + ',' + str(robotCoords[2]) #Creating data to send to robot
        print("Area: ", robotCoords[3] , 'Area2: ', robotCoords[4])
        print("orientation:", robotCoords[2])
        
        
        #Send data to robot
        #If A obejct is detected
        if robotCoords[3] > lowValueObjectA and robotCoords[3] < highValueObjectA: 
            print('sending dataA', dataA)
            self.stateMachine.clientSock.sendall(dataA.encode('utf-8')) #Sending data to robot
            self.stateMachine.ChangeState(Idle()) #Changing state to Idle
            

        #If B obejct is detected
        elif robotCoords[3] > lowValueObjectB and robotCoords[3] < highValueObjectB: 
            print('sending dataB', dataB)
            self.stateMachine.clientSock.sendall(dataB.encode('utf-8')) #Sending data to robot
            self.stateMachine.ChangeState(Idle()) #Changing state to Idle

        #looping back to FindAndSendCoordinates if no object is detected
        else: 
            print('No object detected') 
            time.sleep(2)



class Control(State): # 40 - Control of obejckt detection after pickup
    def Enter(self):
        print("Control")
        time.sleep(0.5)

    def Execute(self): # Get Area from pipeLine tjek if area is in range and send OK/NotOK to robot
        pipelineoutput = pipeLine(self.stateMachine.cam, findObject=False, controlObject=True) #Get data from pipeLine

        #If an obejct is detected
        if pipelineoutput[4] > lowValueControl and pipelineoutput[4] < highValueControl:
            self.stateMachine.clientSock.sendall("OK".encode('utf-8')) #Sending data to robot
            print("OK")
            self.stateMachine.ChangeState(Idle())

        #If no obejct is detected
        elif pipelineoutput[4] < lowValueControl or pipelineoutput[4] > highValueControl:
            self.stateMachine.clientSock.sendall("NotOK".encode('utf-8')) #Sending data to robot
            print("NotOK")
            self.stateMachine.ChangeState(Idle())

        