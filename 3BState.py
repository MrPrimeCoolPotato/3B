from statemachine import *
import time 
import pipeLine
from Comms import *

#Constants
lowValueObjectA = 10
highValueObjectA = 100
zValueObjectA = 10

lowValueObjectB = 100
highValueObjectB = 200
zValueObjectB = 20

class Variables:
    def __init__(self, objectDetected, object, z, robotCords):
        self.objectDetected = objectDetected
        self.object = object
        self.z = z
        self.robotCords = robotCords


class DataComms:
    def Datacomms(self):
        self.recvDataFromRobot = DataFromRobot()    #Reciving data from robot
        self.sendDataToRobot = Senddata()       #Sending data to robot


class Initializing(State):      #0 - Initializing
    def Enter(self):
        print('State: Initializing - waiting for communication to be OK')

    def Execute(self):
        time.sleep(2)
        DataMain()  

        if DataComms.recvDataFromRobot == 'robot OK':
            self.stateMachine.ChangeState(ResetRobotPos())


class ResetRobotPos(State):     #10
    def Enter(self):
        print('State: ResetRobotPos - Resetting the position of the robot')
    
    def Execute(self):
        DataComms.sendDataToRobot('Reset Pos')
        time.sleep(1)
        self.stateMachine.ChangeState(ResetData())


class ResetData(State):         #20
    def Enter(self):
        print('State: Reset Data and wait for robot to finish moving')

    def Execute(self):
        if DataComms.recvDataFromRobot == 'Done moving to Home':
            Variables.objectDetected = False                          #Resetting variables
            Variables.object = ''
            Variables.robotCords = 0
            Variables.z = 0
            time.sleep(1)
            self.stateMachine.ChangeState(GetFrame())


class GetFrame(State):          #30
    def Enter(self):
        print('State: GetFrame - Getting and processing image')
    
    def Execute(self):
        time.sleep(1)
        pipeLine()
        if pipeLine.Output[3] > lowValueObjectA and pipeLine.Output[3] < highValueObjectA:        #Checking if object is detected and what object, from the area of the object
            Variables.object = 'A'
            Variables.z = zValueObjectA
            self.stateMachine.ChangeState(CalcCords())

        elif pipeLine.Output[3] > lowValueObjectB and pipeLine.Output[3] < highValueObjectB:
            Variables.object = 'B'
            Variables.z = zValueObjectB
            self.stateMachine.ChangeState(CalcCords())

        else:
            self.stateMachine.ChangeState(ResetRobotPos())


class CalcCords(State):         #40
    def Enter(self):
        print('State: CalcCords - Converting coordinates for robot')

    def Execute(self):
        time.sleep(1)
        if Variables.robotCords:
            self.stateMachine.ChangeState(SendCordsToRobot())


class SendCordsToRobot(State):  #50
    def Enter(self):
        print('State: SendCordsToRobot - Sending coordinates to robot and start first robot sequense')

    def Execute(self):
        DataComms.sendDataToRobot([pipeLine.Output[0], pipeLine.Output[1], pipeLine.Output[2], Variables.z])   #Sending coordinates to robot (x, y, orientation, z)
        time.sleep(1)
        self.stateMachine.ChangeState(waiting2())


class waiting2(State):          #60
    def Enter(self):
        print('State: waiting for robot to finish moving')

    def Execute(self):
        if DataComms.recvDataFromRobot == 'Done moving to control position':
           self.stateMachine.ChangeState(Control())


class Control(State):           #70
    def Enter(self):
        print('State: Control - Controlling if tool picked up object')

    def Execute(self):
        pipeLine()
        time.sleep(1)
        if pipeLine.Output[3] > lowValueObjectA and pipeLine.Output[3] < highValueObjectB:  #From lowest value of the two objects, to the highest value of the two objects
            Variables.objectDetected = True                                       
            self.stateMachine.ChangeState(RobotSequense2())


class RobotSequense2(State):    #80
    def Enter(self):
        print('State: RobotSequense2 -  Activating second prt of robot sequense')

    def Execute(self):
        if Variables.objectDetected and object == 'A':
            DataComms.sendDataToRobot('ObjectA') 
            time.sleep(1)
            self.stateMachine.ChangeState(ResetData())
        elif Variables.objectDetected and object == 'B':
            DataComms.sendDataToRobot('ObjectB')
            time.sleep(1)
            self.stateMachine.ChangeState(ResetData())
        else:
            DataComms.sendDataToRobot('ObjectError')
            time.sleep(1)
            self.stateMachine.ChangeState(ResetData())


sm = StateMachine(Initializing())
sm.Run()
