import RPi.GPIO as GPIO
import time
import board
import busio
import adafruit_pca9685
import adafruit_tca9548a
from adafruit_as7341 import AS7341
from cmath import e

# For panel state switching -> GPIO 17, 27, 22 (Yellow, Orange, Violet)
# Setup RPi GPIO Parameters, set initial values to LOW (OFF)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)

GPIO.output(17, GPIO.LOW)
GPIO.output(27, GPIO.LOW)
GPIO.output(22, GPIO.LOW)

# Initializing objects for TCA9548a amd PCA9685
i2c_monitoring = board.I2C() # uses board.SCL and board.SDA
I2C_MUX = adafruit_tca9548a.TCA9548A(i2c_monitoring)

i2c_control = busio.I2C(board.SCL, board.SDA)
PWM_CONTROLLER = adafruit_pca9685.PCA9685(i2c_control)

# Configure light controller
# Set PWM frequency to 1kHz
PWM_CONTROLLER.frequency = 1000


# ----------------------------------------------------------------------------- #
#                           LED Panel class object                              #
# ----------------------------------------------------------------------------- #

class LEDPanel:

    def __init__(LED, RGB_RATIO, RGB_CHANNEL, RGB_DUTYCYCLE, STATE, PHOTOPERIOD):

        ### Write handler here if values are out of range

        # Create instance of the light controllers
        LED.LED_RED = RGB_CHANNEL[0]
        LED.LED_GREEN = RGB_CHANNEL[1]
        LED.LED_BLUE = RGB_CHANNEL[2]

        # Set RGB ratios in float between values 0 to 1, 1 for max brightness
        LED.MAX_RATIO_RED = RGB_RATIO[0]    
        LED.MAX_RATIO_GREEN = RGB_RATIO[1]  
        LED.MAX_RATIO_BLUE = RGB_RATIO[2]   

        # Set initial duty cycles for each, must be in integer between 0 to 65535
        LED.DUTYCYCLE_RED = RGB_DUTYCYCLE[0]
        LED.DUTYCYCLE_GREEN = RGB_DUTYCYCLE[1]
        LED.DUTYCYCLE_BLUE = RGB_DUTYCYCLE[2]

        # Set STATE and PHOTOPERIOD values
        LED.STATE = STATE               # ON/OFF
        LED.PHOTOPERIOD = PHOTOPERIOD   # Light cycle

    def getConfig(LED):
        print("--------------------------------------------------")
        print("         Current Panel light configuration        ")
        print("--------------------------------------------------")
        print("     LED        MAX RATIO        DUTY CYCLE    ")
        print("     RED          {0}             {1}        " .format(LED.MAX_RATIO_RED, LED.DUTYCYCLE_RED))
        print("    GREEN         {0}             {1}        " .format(LED.MAX_RATIO_GREEN, LED.DUTYCYCLE_GREEN))
        print("     BLUE         {0}             {1}        " .format(LED.MAX_RATIO_BLUE, LED.DUTYCYCLE_BLUE))
        print("\n          STATE   -> ", LED.STATE)
        print("  PHOTOPERIOD (HRs) -> D: {0}   N: {1}" .format(LED.PHOTOPERIOD[0], LED.PHOTOPERIOD[1]))
        print("--------------------------------------------------")

    def setRatioRGB(LED, newRED, newGREEN, newBLUE): 
        # Defines new RGB ratios, by default, will set duty cycles to maximum assigned ratio
        # Must input in float between 0 and 1

        # Handler here if values are out of range
        RED_VALID = True if newRED >= 0 and newRED <= 1 else False
        GREEN_VALID = True if newGREEN >= 0 and newGREEN <= 1 else False
        BLUE_VALID = True if newBLUE >= 0 and newBLUE <= 1 else False

        # Check as long as one of the three values are out of range, throw error
        if not RED_VALID or not GREEN_VALID or not BLUE_VALID:
            return print("Values are out of range. Please re-enter values.")
        else:
            # Calculate new ratios and set new duty cycles
            LED.MAX_RATIO_RED = newRED
            LED.MAX_RATIO_GREEN = newGREEN
            LED.MAX_RATIO_BLUE = newBLUE

            if (LED.MAX_RATIO_RED == 0):
                LED.DUTYCYCLE_RED = 0
            else:                     
                LED.DUTYCYCLE_RED = (LED.MAX_RATIO_RED * 65536) - 1

            if (LED.MAX_RATIO_GREEN == 0):
                LED.DUTYCYCLE_GREEN = 0
            else:                     
                LED.DUTYCYCLE_GREEN = (LED.MAX_RATIO_GREEN * 65536) - 1

            if (LED.MAX_RATIO_BLUE == 0):
                LED.DUTYCYCLE_BLUE = 0
            else:                     
                LED.DUTYCYCLE_BLUE = (LED.MAX_RATIO_BLUE * 65536) - 1


            # Set appropriate duty cycles for each, convert values to hex notation
            LED.LED_RED.duty_cycle = int(LED.DUTYCYCLE_RED)
            LED.LED_GREEN.duty_cycle = int(LED.DUTYCYCLE_GREEN)
            LED.LED_BLUE.duty_cycle = int(LED.DUTYCYCLE_BLUE)

    def setIntensity(LED, VALUE):
        # Defines overall intensity of light output (for PPFD adjustment using single light control, not per channel )
        # Input is in float between 0 and 1 describing duty cycle ratio (.5 for 50% duty cycle and so on...)

        # Handler here if values are out of range
        if VALUE < 0 or VALUE > 1:
            return print("Values are out of range. Please re-enter values.")
        else: 
            # Multiply duty cycle ratio to the set maximum ratio for each RGB channel corresponding to appropriate light levels for each color ratio mix
            # Calculate duty cycle target values for each ratio by multiplying to 65536
            RED_TARGET = LED.MAX_RATIO_RED * VALUE * 65536
            GREEN_TARGET = LED.MAX_RATIO_GREEN * VALUE * 65536
            BLUE_TARGET = LED.MAX_RATIO_BLUE * VALUE * 65536

            # Check if new RGB targets are less or greater than the desired value to apply appropriate dimming control
            # Update red
            if RED_TARGET - 1 > LED.DUTYCYCLE_RED:
                # Increase brightness
                print("Increasing brightness...")
                try:
                    for i in range(int(LED.DUTYCYCLE_RED), int(RED_TARGET)):
                        LED.LED_RED.duty_cycle = i
                    print("... task done.")                
                except:
                    print("Error occured.")
            else:
                # Decrease brightness
                try:
                    print("Decreasing brightness...")
                    for i in range(int(LED.DUTYCYCLE_RED), int(RED_TARGET), -1):
                        LED.LED_RED.duty_cycle = i
                    print("...task done.")
                except:
                    print("Error occured.")
                    
            # Update green
            if GREEN_TARGET - 1 > LED.DUTYCYCLE_GREEN:
                # Increase brightness
                print("Increasing brightness...")
                try:
                    for i in range(int(LED.DUTYCYCLE_GREEN), int(GREEN_TARGET)):
                        LED.LED_GREEN.duty_cycle = i
                    print("...task done.")
                except:
                    print("Error occured.")
            else:
                # Decrease brightness
                try:
                    print("Decreasing brightness...")            
                    for i in range(int(LED.DUTYCYCLE_GREEN), int(GREEN_TARGET), -1):
                        LED.LED_GREEN.duty_cycle = i
                    print("...task done.")            
                except:
                    print("Error occured.")
                            
            # Update blue
            if BLUE_TARGET - 1 > LED.DUTYCYCLE_BLUE:
                # Increase brightness
                print("Increasing brightness...")
                try:            
                    for i in range(int(LED.DUTYCYCLE_BLUE), int(BLUE_TARGET)):
                        LED.LED_BLUE.duty_cycle = i
                    print("...task done.")
                except:
                    print("Error occured.")
            else:
                # Decrease brightness
                try:
                    print("Decreasing brightness...")            
                    for i in range(int(LED.DUTYCYCLE_BLUE  ), int(BLUE_TARGET), -1):
                        LED.LED_BLUE.duty_cycle = i
                    print("...task done.")
                except:
                    print("Error occured.")
                    
            # Save new RGB duty cycle values
            LED.DUTYCYCLE_RED = RED_TARGET - 1
            LED.DUTYCYCLE_GREEN = GREEN_TARGET - 1
            LED.DUTYCYCLE_BLUE = BLUE_TARGET - 1        
                
    def turnON(LED):
        LED.STATE = True
        # execute code for switching MOSFET modules

    def turnOFF(LED):
        LED.STATE = False
        LED.LED_RED.duty_cycle = 0
        LED.LED_GREEN.duty_cycle = 0
        LED.LED_BLUE.duty_cycle = 0
        # execute code for switching MOSFET modules
        return 0

    def setPHOTOPERIOD(LED, VALUE):

        ### Write handler here if array values are valid, must be equal to 24

        LED.PHOTOPERIOD = VALUE

    def getSTATE(LED):
        return LED.STATE

    def getPHOTOPERIOD(LED):
        return LED.PHOTOPERIOD

# ----------------------------------------------------------------------------- #
#                       Spectral data capture class                             #
# ----------------------------------------------------------------------------- #

class SpectralSensor:

    def __init__ (self, SENSOR):
        self.SENSOR = SENSOR

    def bar_graph(read_value):
        scaled = int(read_value/1000)
        return "[%5d]" % read_value

    def get_f1(self):
        return self.SENSOR.channel_415nm

    def get_f2(self):
        return self.SENSOR.channel_445nm

    def get_f3(self):
        return self.SENSOR.channel_480nm

    def get_f4(self):
        return self.SENSOR.channel_515nm

    def get_f5(self):
        return self.SENSOR.channel_555nm

    def get_f6(self):
        return self.SENSOR.channel_590nm

    def get_f7(self):
        return self.SENSOR.channel_630nm

    def get_f8(self):
        return self.SENSOR.channel_680nm

    def get_nir(self):
        return self.SENSOR.channel_nir

    def disp_freq(self):
        print("------------------------------------------")
        print("F1 - 415nm/Violet [%5d]" % self.SENSOR.channel_415nm)
        print("F2 - 445nm/Indigo [%5d]" % self.SENSOR.channel_445nm)
        print("F3 - 480nm/Blue   [%5d]" % self.SENSOR.channel_480nm)
        print("F4 - 515nm/Cyan   [%5d]" % self.SENSOR.channel_515nm)
        print("F5 - 555nm/Green  [%5d]" % self.SENSOR.channel_555nm)
        print("F6 - 590nm/Yellow [%5d]" % self.SENSOR.channel_590nm)
        print("F7 - 630nm/Orange [%5d]" % self.SENSOR.channel_630nm)
        print("F8 - 680nm/Red    [%5d]" % self.SENSOR.channel_680nm)
        print("Nir               [%5d]" % self.SENSOR.channel_nir)
        print("------------------------------------------")

    def get_spectraldata(self):

        # gets spectral data from AS7341 sensor object and return the data in a list
        SPD = [self.SENSOR.channel_415nm, 
               self.SENSOR.channel_445nm,
               self.SENSOR.channel_480nm,
               self.SENSOR.channel_515nm,
               self.SENSOR.channel_555nm,
               self.SENSOR.channel_590nm,
               self.SENSOR.channel_630nm,
               self.SENSOR.channel_680nm,
               self.SENSOR.channel_nir]

        return SPD

# ----------------------------------------------------------------------------- #
#                                Main program
# ----------------------------------------------------------------------------- #

def capture_spectraldata():

    print("|=========================================================|\n")
    print("               SPECTRAL DATA CAPTURE PROGRAM                 ")
    print("|=========================================================|\n\n")
    print("                 Press enter to continue                     \n\n\n\n")

    # set brightness to 5% initial
    
    samples = [] # create list for storing data samples
    
    for x in range(20):
        spectraldata = SENSOR_TOP.get_spectraldata
        PPFD = input("\nEnter equivalent PPFD: ")
    
        for i in range(9):
            samples[x][i] = spectraldata[i]
            samples[x][9] = PPFD

        # increase brightness by 5%

def LIGHT_MONITORING_TEST(sensorOne, sensorTwo):

    print("             AS7341 One")
    sensorOne.disp_freq()
    print("             AS7341 Two")
    sensorTwo.disp_freq()

def LIGHT_CONTROL_TEST(LEDPANEL):

    x = input("Enter to start test by turning on LED panel")
    GPIO.output(17, GPIO.HIGH)
    time.sleep(3)

    x = input("Enter to start test for each color channel")
    LEDPANEL.setRatioRGB(1, 0, 0)
    LEDPANEL.getConfig()    
    x = input("Testing Red. Enter for next")
    LEDPANEL.setRatioRGB(0, 1, 0)
    LEDPANEL.getConfig()    
    x = input("Testing Green. Enter for next")
    LEDPANEL.setRatioRGB(0, 0, 1)    
    LEDPANEL.getConfig()    
    x = input("Testing Blue. Enter for next")

    x = input("Enter to set intensity to 50%")
    LEDPANEL.setIntensity(0.5)
    x = input("Enter to set ratio to 25%, 50%, 75%")
    LEDPANEL.setRatioRGB(0.25, 0.5, 0.75)

    x = input("Enter to next test, check if LED config was updated")
    LEDPANEL.getConfig()
    x = input("Enter to set intensity to full bright")
    LEDPANEL.setIntensity(1)
    x = input("Enter to set new ratio again, full bright")
    LEDPANEL.setRatioRGB(1, 1, 1)

    # Try wrong values
    x = input("Enter to try for wrong values for intensity")
    LEDPANEL.setIntensity(1.1)
    x = input("Enter to try for wrong values for ratio")
    LEDPANEL.setRatioRGB(0.1, 1.1, 1)

    x = input("Enter to finish test by turning off LED panel")
    
    LEDPANEL.turnOFF()

    GPIO.output(17, GPIO.LOW)
    time.sleep(3)

    # Create function to set all duty cycles to 0

    print("Testing for light controller is done.")


def main():
    
    # For light monitoring, create object for AS7341
    SENSOR_ONE = SpectralSensor(AS7341(I2C_MUX[4]))
    SENSOR_TWO = SpectralSensor(AS7341(I2C_MUX[3]))

    # For light control, create object for TCA9548A
    # (RGB_RATIO [R, G, B] where each index is a value between 0 and 1, 1 for max ratio, 
    #  RGB_CHANNEL pass TCA objects for respective RGB channel x [redchannel[x], greenchannel[x], bluechannel[x]], 
    #  RGB_DUTYCYCLE [R, G, B] initial duty cycle with values between 0 to 65535, 65535 for full brightness,
    #  STATE - False for OFF at initial state, 
    #  PHOTOPERIOD value [day hrs, night hrs])

    PANEL_TOP = LEDPanel( [1, 1, 1], [PWM_CONTROLLER.channels[8], PWM_CONTROLLER.channels[9], PWM_CONTROLLER.channels[10]], [0, 0, 0], False, [12, 12])
    # PANEL_TOP = LEDPanel( [1, 1, 1], [PWM_CONTROLLER.channels[4], PWM_CONTROLLER.channels[5], PWM_CONTROLLER.channels[6]], [0, 0, 0], False, [12, 12])    

    """
    while(True):
        LIGHT_MONITORING_TEST(SENSOR_ONE, SENSOR_TWO)
        time.sleep(2)"""

    LIGHT_CONTROL_TEST(PANEL_TOP)

    # capture_spectraldata()
  
    pass

if __name__=="__main__":
    main()
