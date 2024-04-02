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
dpiStepper = DPiStepper()
microstepping = 8
dpiStepper.setMicrostepping(microstepping)

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
        self.armupdown()

    def toggleMagnet(self):
        print("Process magnet here")
        self.magnet()
        
    def auto(self):
        print("Run the arm automatically here")

    def setArmPosition(self, position):
        print("Move arm here")
        self.armhoriz()

    def homeArm(self):
        # arm.home(self.homeDirection)
        # self.hardarmhome()
        pass

    def isBallOnTallTower(self):
        print("Determine if ball is on the top tower")

    def isBallOnShortTower(self):
        print("Determine if ball is on the bottom tower")
        
    def initialize(self):
        print("Home arm and turn off magnet")
        self.intializearmhor()

# /////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////

    def magnet(self):
        i = 0
        servo_number = 1
        for i in range(180):
            dpiComputer.writeServo(servo_number, i)
            sleep(.02)
# ////////////////////
#     def armupdown(self):
#         pass

    def intializearmhor(self):
        stepper_num = 0
        dpiStepper.setBoardNumber(0)
        # set stepper number & enable motors
        gear_ratio = 1
        motorStepPerRevolution = 1600 * gear_ratio
        dpiStepper.setStepsPerRevolution(stepper_num, motorStepPerRevolution)
        # set steps per rev
        dpiStepper.setCurrentPositionInRevolutions(stepper_num, 0)

        dpiStepper.setSpeedInRevolutionsPerSecond(stepper_num, 2)
        accel_in_revolutions_per_sec_per_sec = 2.0
        dpiStepper.setAccelerationInRevolutionsPerSecondPerSecond(stepper_num, accel_in_revolutions_per_sec_per_sec)
        # set position and speed and accel

    def armhoriz(self):
        dpiStepper.enableMotors(True)
        dpiStepper.moveToAbsolutePositionInRevolutions(0, 1, waitToFinishFlg=True)
        dpiStepper.enableMotors(False)
#
#
# ////////////////////

    def hardarmhome(self, dpiStepper=None):
        # dpiStepper.enableMotors(True)
        # speed_in_steps_per_sec = 5500  # self.ids.rampSpeed.value
        # MaxDistanceToMoveInSteps = 46000
        # dpiStepper.moveToHomeInSteps(0, 1, speed_in_steps_per_sec, MaxDistanceToMoveInSteps)
        dpiStepper.enableMotors(False)

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
