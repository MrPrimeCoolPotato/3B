from stateSlave import *
import VisionSM
import statemachine

#MainBlock

#sm = statemachine.StateMachine(SetupServer())
sm = VisionSM.VisionSM(SetupServer())
sm.Run()