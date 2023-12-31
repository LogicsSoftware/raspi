#!/usr/bin/env python3
########################################################################
# Filename    : ButtonLED.py
# Description : Control led with button.
# Author      : www.freenove.com
# modification: 2023/05/11
########################################################################
from gpiozero import LED, Button
from timeit import default_timer as timer

led = LED(17)       # define LED pin according to BCM Numbering
button = Button(18) # define Button pin according to BCM Numbering

start = timer()
counter = 0

def program_end():
    print("Ending program at counter", counter)
    end = timer()
    diff = end - start
    hz = counter / diff
    print("after diff", diff)
    print("with hz", hz)

def loop():
    while True:
        global counter
        counter = counter + 1
        if (counter >= 1000000000):
            print(counter, "enough counted")
            program_end()
            break
        if button.is_pressed:  # if button is pressed
            led.on()        # turn on led
            print(counter, "Button is pressed, led turned on >>>", timer()) # print information on terminal 
        else : # if button is relessed
            led.off() # turn off led 
            print(counter, "Button is released, led turned off <<<", timer())    

if __name__ == '__main__':     # Program entrance
    print ('Program is starting...')
    try:
        loop()
    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        program_end()
