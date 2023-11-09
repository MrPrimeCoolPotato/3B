from statemachine import State, StateMachine
import socket
import stateSlave

class VisionSM(StateMachine):
    def __init__(self, state: State):
        self.state: State = state
        self.state.stateMachine = self
        self.serverSock = socket.socket()
        self.clientSock = socket.socket()
        self.cam = None