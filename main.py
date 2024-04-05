# ////////////////////////////////////////////////////////////////
# //                     IMPORT STATEMENTS                      //
# ////////////////////////////////////////////////////////////////
import math
import sys
import time

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import *
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.animation import Animation
from functools import partial
from kivy.config import Config
from kivy.core.window import Window
from pidev.kivy import DPEAButton
from pidev.kivy import PauseScreen
from time import sleep
from dpeaDPi.DPiComputer import *
from dpeaDPi.DPiStepper import *

# ////////////////////////////////////////////////////////////////
# //                     HARDWARE SETUP                         //
# ////////////////////////////////////////////////////////////////
"""Stepper goes into MOTOR 0
   Limit Sensor for Stepper Motor goes into HOME 0
   Talon Motor Controller for Magnet goes into SERVO 1
   Talon Motor Controller for Air Piston goes into SERVO 0
   Tall Tower Limit Sensor goes in IN 2
   Short Tower Limit Sensor goes in IN 1
   """
# ////////////////////////////////////////////////////////////////
# //                      GLOBAL VARIABLES                      //
# //                         CONSTANTS                          //
# ////////////////////////////////////////////////////////////////
START = True
STOP = False
UP = False
DOWN = True
ON = True
OFF = False
PINK = 1, 0.3, 0.5, 1
BLUE = 0.917, 0.796, 0.380, 1
CLOCKWISE = 0
COUNTERCLOCKWISE = 1
ARM_SLEEP = 2.5
DEBOUNCE = 0.10

lowerTowerPosition = 60
upperTowerPosition = 76


# ////////////////////////////////////////////////////////////////
# //            DECLARE APP CLASS AND SCREENMANAGER             //
# //                     LOAD KIVY FILE                         //
# ////////////////////////////////////////////////////////////////
class MyApp(App):

    def build(self):
        self.title = "Robotic Arm"
        return sm

Builder.load_file('main.kv')
Window.clearcolor = (.1, .1, .1, 1) # (WHITE)


# ////////////////////////////////////////////////////////////////
# //                    SLUSH/HARDWARE SETUP                    //
# ////////////////////////////////////////////////////////////////
sm = ScreenManager()

# SERVO
dpiComputer = DPiComputer()
dpiComputer.initialize()
# Stepper
arm = DPiStepper()
arm.initialize()
arm.enableMotors(True)
microstepping = 8
arm.setMicrostepping(microstepping)

# ////////////////////////////////////////////////////////////////
# //                       MAIN FUNCTIONS                       //
# //             SHOULD INTERACT DIRECTLY WITH HARDWARE         //
# ////////////////////////////////////////////////////////////////

class MainScreen(Screen):
    armPosition = 0
    lastClick = time.perf_counter()

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.initialize()

    def debounce(self):
        processInput = False
        currentTime = time.perf_counter()
        if (currentTime - self.lastClick) > DEBOUNCE:
            processInput = True
        self.lastClick = currentTime
        return processInput

    def toggleArm(self):
        print("Process arm movement here")
        global UP
        if UP == False:
            UP = True
            self.ids.armControl.text = 'Lower Arm'
            self.armGoUp()
        else:
            UP = False
            self.ids.armControl.text = 'Raise Arm'
            self.armGoDown()

    def toggleMagnet(self):
        print("Process magnet here")
        global ON
        if ON == True:
            self.ids.magnetControl.text = "Drop Ball"
            ON = False
            self.turnMagnetOn()
            print("BLAH")
        else:
            self.ids.magnetControl.text = "Hold Ball"
            ON = True
            self.turnMagnetOff()
        
    def auto(self):
        print("Run the arm automatically here")
        arm.setSpeedInStepsPerSecond(0, 1600)
        if self.isBallOnTallTower():
            # self.armPos0()
            arm.moveToAbsolutePositionInSteps(0, 800, True)
            sleep(.1)
            self.armGoDown()
            self.turnMagnetOn()
            time.sleep(2)
            self.armGoUp()
            time.sleep(.5)
            print("test ONE")

            self.armPos2()
            # arm.moveToAbsolutePositionInSteps(0, 1300, True)
            self.armGoDown()
            time.sleep(1)
            self.turnMagnetOff()
            sleep(.5)
            self.armGoUp()
            self.hardarmhome()
            print("text TWOOOO")
        elif self.isBallOnShortTower():
            # self.armPos2()
            arm.moveToAbsolutePositionInSteps(0, 1300, True)
            sleep(.1)
            self.armGoDown()
            self.turnMagnetOn()
            time.sleep(3)
            self.armGoUp()
            time.sleep(.5)
            print("test ONE")

            # self.armPos1()
            arm.moveToAbsolutePositionInSteps(0, 800, True)
            self.armGoDown()
            time.sleep(1)
            self.turnMagnetOff()
            sleep(.5)
            self.armGoUp()
            self.hardarmhome()
            print("text TWOOOO")
            print("RAwWR")
        else:
            print("no ball detected")
            print("please put ball on a tower and try again")
    def setArmPosition(self, position):
        print("Move arm here")
        arm.enableMotors(True)
        self.ids.armControlLabel.text = 'Arm Position: ' + str(self.armPosition)
        self.armPosition = position
        arm.setSpeedInStepsPerSecond(0, 1600)
        if position == 0:
            self.armPos0()
        elif position == 1:
            self.armPos1()
        elif position == 2:
            self.armPos2()
        else:
            print("something aint right")
        arm.enableMotors(False)

    def homeArm(self):
        self.hardarmhome()

    def isBallOnTallTower(self):
        print("Determine if ball is on the top tower")
        if dpiComputer.readDigitalIn(dpiComputer.IN_CONNECTOR__IN_2) == 0:
            return True
        else:
            return False

    def isBallOnShortTower(self):
        print("Determine if ball is on the bottom tower")
        if dpiComputer.readDigitalIn(dpiComputer.IN_CONNECTOR__IN_1) == 0:
            return True
        else:
            return False

    def initialize(self):
        print("Home arm and turn off magnet")
        self.turnMagnetOff()
        self.armGoUp()
        self.homeArm()


# /////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////

    def turnMagnetOn(self):
        dpiComputer.writeServo(1, 180)

    def turnMagnetOff(self):
        dpiComputer.writeServo(1, 90)
# ////////////////////

    def armGoDown(self):
        dpiComputer.writeServo(0, 180)

    def armGoUp(self):
        dpiComputer.writeServo(0, 90)

    def hardarmhome(self):
        arm.enableMotors(True)
        arm.moveToHomeInSteps(0, -1, 1600, 3200)
        arm.enableMotors(False)

    def armPos0(self):
        arm.moveToAbsolutePositionInSteps(0, 0, True)
    def armPos1(self):
        arm.moveToAbsolutePositionInSteps(0, 800, True)
    def armPos2(self):
        arm.moveToAbsolutePositionInSteps(0, 1300, True)


    # ////////////////////


    def resetColors(self):
        self.ids.armControl.color = PINK
        self.ids.magnetControl.color = PINK
        self.ids.auto.color = BLUE

    def quit(self):
        MyApp().stop()
    
sm.add_widget(MainScreen(name = 'main'))


# ////////////////////////////////////////////////////////////////
# //                          RUN APP                           //
# ////////////////////////////////////////////////////////////////

MyApp().run()
