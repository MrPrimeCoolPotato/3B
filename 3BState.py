from statemachine import *
import time 
from pipeLine import *
from Comms import *
from OAKWrapper import OAKCamColorDepth 
#For main
 


class Variables:
    def __init__(self, objectDetected, object, robotCords, cameraOK):
        self.objectDetected = objectDetected
        self.object = object
        self.robotCords = robotCords
        self.cameraOK = OAKCamColorDepth.cameraOK

class DataComms:
    def Datacomms(self):
        self.dataFromRobot = DataFromRobot()
        self.sendDataToRobot = Senddata()

class Initializing(State): #0
    def Enter(self):
        print('State: Initializing - waiting for communication to be OK')

    def Execute(self):
        time.sleep(2)
        DataMain()  

        if DataComms.sendDataToRobot == 'robot OK' and Variables.cameraOK:
            self.stateMachine.ChangeState(ResetRobotPos())

class ResetRobotPos(State): # 10
    def Enter(self):
        print('State: ResetRobotPos - Resetting the position of the robot')
    
    def Execute(self):
        DataComms.sendDataToRobot('Reset Pos')
        time.sleep(1)
        self.stateMachine.ChangeState(ResetData())

class ResetData(State):
    def Enter(self):
        print('State: Reset Data and wait for robot to finish moving')

    def Execute(self):
        if DataComms.dataFromRobot == 'Done moving to Home':
            Variables.objectDetected = False
            Variables.object = ''
            Variables.robotCords = 0
            time.sleep(1)
            self.stateMachine.ChangeState(GetFrame())

class GetFrame(State): #20
    def Enter(self):
        print('State: GetFrame - Getting and processing image')
    
    def Execute(self):
        time.sleep(1)
        pipeLine()
        if pipeLine.Output[3] > 10 and pipeLine.Output[3] < 100:
            Variables.object = 'A'
            self.stateMachine.ChangeState(CalcCords())

        elif pipeLine.output[3] > 110 and pipeLine.output[3] < 200:
            Variables.object = 'B'
            self.stateMachine.ChangeState(CalcCords())

        else:
            self.stateMachine.ChangeState(ResetRobotPos())

class CalcCords(State): #30
    def Enter(self):
        print('State: CalcCords - Converting coordinates for robot')

    def Execute(self):
        time.sleep(1)
        if Variables.robotCords:
            self.stateMachine.ChangeState(SendCordsToRobot())

class SendCordsToRobot(State): #40
    def Enter(self):
        print('State: SendCordsToRobot - Sending coordinates to robot and start first robot sequense')

    def Execute(self):
        DataComms.sendDataToRobot([pipeLine.Output[0], pipeLine.Output[1], pipeLine.Output[2], Variables.object])
        time.sleep(1)
        self.stateMachine.ChangeState(waiting2())

class waiting2(State):
    def Enter(self):
        print('State: waiting for robot to finish moving')

    def Execute(self):
        if DataComms.dataFromRobot == 'Done moving to control position':
           self.stateMachine.ChangeState(Control())

class Control(State):
    def Enter(self):
        print('State: Control - Controlling if tool picked up object')

    def Execute(self):
        pipeLine()
        time.sleep(1)
        if pipeLine.Output[3] > 10 and pipeLine.Output[3] < 200:
            Variables.objectDetected = True                                       
            self.stateMachine.ChangeState(RobotSequense2())

class RobotSequense2(State):
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
