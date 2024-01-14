#!/usr/bin/env python3
########################################################################
# Filename    : ADC.py
# Description : Use ADC module to read the voltage value of potentiometer.
# Author      : www.freenove.com
# modification: 2023/05/11
########################################################################
import time
from timeit import default_timer as timer

###########################################################################
# for calibration tests: shine the LDR with a PWM LED
#   with specified  frequency and duty cycle
###########################################################################
from gpiozero import PWMLED
pwmLed = PWMLED(27)
'''
start or restart the pwmLed with specified params.
:param int frequency:
        The frequency (in Hz) of pulses emitted to drive the LED. Defaults to 1/sec.
        Uses software PWM: max frequence = 1000 Hz
:param float dutyCycle:
        Defines the ratio of ON - OFF states for each cycle: 0.0 .. 1.0.
        Exampel: 0.1 specifies ON for 10% (and OFF for 90%) of the cycle: "short pulse"
'''
def startPwmLed(frequency=1, dutyCycle=0.1):  # blinks very slow (1/sec); short ON (10%), long OFF (90%)
    pwmLed.on()     # must turn on before setting value!
    pwmLed.frequency = frequency
    pwmLed.value = dutyCycle
    print("startPwmLed: frequency=", pwmLed.frequency, ", dutyCyle=", pwmLed.value)
    time.sleep(3)

###########################################################################
# Button controlled by LDR + R-Bridge
#   instead of ADC
###########################################################################
from gpiozero import Button
#button = Button(18, bounce_time=5) # does not work for button.is_pressed
#button = Button(18)
#button = Button(18, bounce_time=0.005)
button = Button(18, bounce_time=0.001)


###########################################################################
# test LCD
###########################################################################
#import smbus
def initLCD() :
    from LCD1602 import CharLCD1602
    lcd1602 = CharLCD1602() 
    lcd1602.init_lcd()
    lcd1602.clear()
    lcd1602.write(0, 0, "TEST" )
    lcd1602.write(0, 1, "EINS" )
    return lcd1602
#initLCD()


###########################################################################
# the test loop
#   analogRead of LDR voltage (8bit), or digital  is_pressed, or wait_for_press/release
#   handle HIGH/LOW value
#   turn led ON/OFF
#   prints ADC sample time and value
###########################################################################
def testLoop(verbose=False, digital=False):
    print("testloop:", "digital=" + str(digital), "verbose=" + str(verbose))

    startTest = timer()    
    startRPS = 0
    timeRPS = 0
    countON = 0
    countOFF = 0

    led.off()
    loops = 0
    while True:
        loops += 1 

        # read the ADC (voltage) of channel 0
        startADC = timer()
        if (digital):
            #voltage = 3.3 if button.is_pressed else 0
            if (led.is_lit):
                button.wait_for_release()
                voltage = 0
            else:
                button.wait_for_press()
                voltage = 3.3
        else:
            value = adc.analogRead(0)
            voltage = value / 255.0 * 3.3   # calculate the voltage value
        now = timer()
        waitADC = (now - startADC)*1000

        # handle HIGH / LOW
        if (voltage > 3.3/2):
            # detected ON
            if led.is_lit:
                # already ON: continue ON
                countON += 1
                text = "ON"
            else:
                # transition OFF -> ON: start next cycle, start ON
                if (startRPS == 0):
                    # startup only
                    text = "ON FIRST"
                else:
                    timeRPS = now - startRPS
                    text = "ON last={:>.3f}ms".format(timeRPS) + ", {:>5.1f} Hz".format(1/timeRPS) + ", on={:>2d}".format(countON) + ", off={:>2d}".format(countOFF) + ", duty={:2.2f}%".format(100 * countON/(countON + countOFF))
                
                # start next cycle
                led.on()
                startRPS = now
                countON = 1
                countOFF = 0
        else:
            # detected OFF
            if not led.is_lit:
                # already OFF: contimue OFF
                pass
            else:
                # transition ON -> OFF: start OFF
                led.off()
            countOFF += 1
            text = "  "

        # common logging
        if verbose == True or text.startswith("ON "):
            # show detail
            print("{:5}:".format(loops),
                "time {:2.6f}".format(now - startTest),
                #"after {:2.3f}ms".format(waitADC),
                "after {:>6.3f}ms".format(waitADC),
                "shows", "{:.3f}V:".format(voltage),
                text,
                )


###########################################################################
# result LED
#   ON if LDR voltage HIGH
#   OFF else
###########################################################################
from gpiozero import LED
led = LED(17)       # define LED pin according to BCM Numbering


###########################################################################
# init ADC
###########################################################################
from ADCDevice import *
adc = ADCDevice() # Define an ADCDevice class object
def startADC():
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
#startADC()


###########################################################################
# start version jf2_dampfmaschine
###########################################################################


###########adc = ADCDevice() # Define an ADCDevice class object
start = timer()
globalstart = timer() # does not get reset
counter = 0
##################led = LED(17)       # define LED pin according to BCM Numbering
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
        # https://docs.python.org/3/howto/argparse.html
        import argparse
        parser  = argparse.ArgumentParser()
        parser.add_argument("frequency", help="frequency of the PWM LED (1 .. 1000, default 10)", type=int, nargs = "?", default=10) 
        parser.add_argument("dutycycle", help="duty cycle of the PWM LED (0 .. 1, default 0.1)", type=float, nargs="?", default=0.1)
        parser.add_argument("-t", "--test", help="run test loop; default: run production loop", action="store_true")
        parser.add_argument("-d", "--digital", help="use digital input; default: use ADC input", action="store_true")
        parser.add_argument("-v", "--verbose", help="show all sampled values; default: only show rising edge", action="store_true")
        args = parser.parse_args()
        print (args)

        # show lcd message
        lcd1602 = initLCD()
        lcd1602.clear()
        lcd1602.write(0, 0, str(args.frequency) + " " + str(args.dutycycle))
        lcd1602.write(0, 1, ("-t " if args.test else "") + ("-d " if args.digital else "") + ("-v " if args.verbose else ""))
        
        startADC()

        startPwmLed(args.frequency, args.dutycycle)


        #startPwmLed(10, 0.1)
        #startPwmLed(10, 0.5)
        #startPwmLed(50, 0.1)   # 10.05 rps
        #startPwmLed(50, 0.5)   # 10.02 rps
        #startPwmLed(60, 0.1)   # 12.02 rps
        #startPwmLed(60, 0.5)   # 11.8 rps
        #startPwmLed(70, 0.1)   # 14.02 rps
        #startPwmLed(70, 0.5)   # NO: 0.75 rps
        #startPwmLed(80, 0.1)   # 15.8 rps
        #startPwmLed(90, 0.1)   # 17..18 rps
        #startPwmLed(100, 0.1)  # NO: 11 rps
        #startPwmLed(100, 0.5)  # NO: 0.0

        if (args.test):
            testLoop(args.verbose, args.digital)
        else:
            loop()
    except KeyboardInterrupt: # Press ctrl-c to end the program.
        destroy()
        print("Ending program")
        end = timer()
        diff = end - globalstart
        hzSampling = counter / diff
        print("after diff", diff, "counter is at", counter, "with hz", hzSampling, "ignored events", number_ignored_events)
        