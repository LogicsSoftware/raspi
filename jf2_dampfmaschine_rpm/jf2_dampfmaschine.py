#!/usr/bin/env python3
########################################################################
# Filename    : ADC.py
# Description : Use ADC module to read the voltage value of potentiometer.
# Author      : www.freenove.com
# modification: 2023/05/11
########################################################################
import time
from ADCDevice import *
from timeit import default_timer as timer
from gpiozero import LED

adc = ADCDevice() # Define an ADCDevice class object
start = timer()
counter = 0
led = LED(17)       # define LED pin according to BCM Numbering
lastled = 0
threshold_ignore_change_s = 0.005
lastchangetime = 0
changes = 0
number_ignored_events = 0

changes_per_spoke = 2
number_of_spokes = 5

def setup():
    global adc
    if(adc.detectI2C(0x48)): # Detect the pcf8591.
        adc = PCF8591()
    elif(adc.detectI2C(0x4b)): # Detect the ads7830
        adc = ADS7830()
    else:
        print("No correct I2C address found, \n"
        "Please use command 'i2cdetect -y 1' to check the I2C address! \n"
        "Program Exit. \n");
        exit(-1)
        
def loop():
    while True:
        global counter, lastled, changes, threshold_ignore_change_s, number_ignored_events, lastchangetime, start

        if (timer() - start > 5):
            start = timer()
            changes = 0
        
        diff = timer() - start
        hzChanges = changes / diff
        rps = hzChanges / (changes_per_spoke*number_of_spokes)
        rpm = rps * 60

        counter += 1
        value = adc.analogRead(0)    # read the ADC value of channel 0
        voltage = value / 255.0 * 3.3  # calculate the voltage value
        print("rps", "{:.2f}".format(rps), "rpm", "{:.2f}".format(rpm), "voltage", "{:.2f}".format(voltage))
        if (voltage >= (3.3/2)):
            if (lastled == 0):
                if (timer() - lastchangetime >= threshold_ignore_change_s):
                    changes += 1
                    lastchangetime = timer()
                    diff = timer() - start
                    hzChanges = changes / diff
                    rps = hzChanges / (changes_per_spoke*number_of_spokes)
                    rpm = rps * 60
                    #print("change registered: lastled was 0, now 1; #changes: ", changes, "at time", diff, "and hzChanges", hzChanges, "rps", rps, "rpm", rpm)
                    lastled = 1
                    led.on()
                else:
                    number_ignored_events += 1
                    print("change ignored: lastled was 0; #changes: ", changes, "at time", timer() - start)
        else:
            if (lastled == 1):
                if (timer() - lastchangetime >= threshold_ignore_change_s):
                    changes += 1
                    lastchangetime = timer()
                    diff = timer() - start
                    hzChanges = changes / diff
                    rps = hzChanges / (changes_per_spoke*number_of_spokes)
                    rpm = rps * 60
                    #print("change registered: lastled was 1, now 0; #changes: ", changes, "at time", diff, "and hzChanges", hzChanges, "rps", rps, "rpm", rpm)
                    lastled = 0
                    led.off()
                else:
                    number_ignored_events += 1
                    print("change ignored: lastled was 1; #changes: ", changes, "at time", timer() - start)
        #print ('ADC Value : %d, Voltage : %.2f'%(value,voltage), "at time", timer() - start)
        #time.sleep(0.1)

def destroy():
    adc.close()
    
if __name__ == '__main__':   # Program entrance
    print ('Program is starting ... ')
    try:
        setup()
        loop()
    except KeyboardInterrupt: # Press ctrl-c to end the program.
        destroy()
        print("Ending program")
        end = timer()
        diff = end - start
        hzSampling = counter / diff
        print("after diff", diff, "counter is at", counter, "with hz", hzSampling, "ignored events", number_ignored_events)
        