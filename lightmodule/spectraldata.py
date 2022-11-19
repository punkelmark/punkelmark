import RPi.GPIO as GPIO
import time
import board
import busio
import adafruit_pca9685
from adafruit_as7341 import AS7341
from cmath import e
import numpy

# ==============================  Project Notes  ============================== #
"""
    Notes:
    Catch exceptions for object instantiations (to catch if hardware devices are not detected)
    Take note that light comes out at 50% duty cycle (32768-1) and below

    Next steps:
    Optimize light controller and monitoring program
    Fix Spectral Data Program (reverse intensity values)
    MLR Algorithm
"""
# ==============================  SETUP OBJECT INITIALIZATIONS AND GPIO  ============================== #

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
spectrometer = AS7341(i2c_monitoring) # For light monitoring, create object for AS7341
# I2C_MUX = adafruit_tca9548a.TCA9548A(i2c_monitoring)

i2c_control = busio.I2C(board.SCL, board.SDA)
PWM_CONTROLLER = adafruit_pca9685.PCA9685(i2c_control)

# Configure light controller, set PWM frequency to 1kHz
PWM_CONTROLLER.frequency = 1000

# Other globals
MINIMAL_LIGHT_VALUE = 65536/2

# ----------------------------------------------------------------------------- #
#                           LED Panel class object                              #
# ----------------------------------------------------------------------------- #

class LEDPanel:

    def __init__(LED, RGB_RATIO, RGB_CHANNEL, SWITCH, STATE, PHOTOPERIOD):

        ### Write handler here if values are out of range, either within this class or before object initialization in main program

        # Create instance of the light controllers
        LED.LED_RED = RGB_CHANNEL[0]
        LED.LED_GREEN = RGB_CHANNEL[1]
        LED.LED_BLUE = RGB_CHANNEL[2]

        # Set RGB ratios in float values between values 0 to 1
        LED.MAX_RATIO_RED = RGB_RATIO[0]    
        LED.MAX_RATIO_GREEN = RGB_RATIO[1]  
        LED.MAX_RATIO_BLUE = RGB_RATIO[2]   

        # Lowest value to be used will be half of the total, it is the minimum value where sufficient minimal light is emitted
        # Set to low
        LED.DUTYCYCLE_RED = MINIMAL_LIGHT_VALUE
        LED.DUTYCYCLE_GREEN = MINIMAL_LIGHT_VALUE
        LED.DUTYCYCLE_BLUE = MINIMAL_LIGHT_VALUE

        LED.LED_RED.duty_cycle = int(LED.DUTYCYCLE_RED)
        LED.LED_GREEN.duty_cycle = int(LED.DUTYCYCLE_GREEN)
        LED.LED_BLUE.duty_cycle = int(LED.DUTYCYCLE_BLUE)

        # Set STATE and PHOTOPERIOD values
        LED.SWITCH = SWITCH             # Assigned GPIO pin for switching
        LED.STATE = STATE               # ON/OFF
        LED.PHOTOPERIOD = PHOTOPERIOD   # Day/Night cycle

        ## Write test code to configure initializations on hardware

    def turnON(LED):
        # Turn on panel
        GPIO.output(LED.SWITCH, GPIO.HIGH)
        LED.STATE = True

    def turnOFF(LED):
        # Turn off panel  
        GPIO.output(LED.SWITCH, GPIO.LOW)
        LED.STATE = False

    def getSTATE(LED):
        # Returns TRUE if LEDs are ON, otherwise FALSE
        return LED.STATE

    def setPHOTOPERIOD(LED, VALUE):
        # Handler here if array values are valid, must be equal to 24
        # Check if day and night cycles are equals 24 hours, index 0 for day, 1 for night
        LED.PHOTOPERIOD = VALUE if VALUE[0] + VALUE[1] == 24 else print("Invalid photoperiod")

    def getPHOTOPERIOD(LED):
        return LED.PHOTOPERIOD

    def getConfig(LED):
        print("--------------------------------------------------")
        print("         Current Panel light configuration        ")
        print("--------------------------------------------------")
        print("     LED        MAX RATIO        CURRENT DUTY CYCLE    ")
        print("     RED          {0}                {1}        " .format(LED.MAX_RATIO_RED, LED.DUTYCYCLE_RED))
        print("    GREEN         {0}                {1}        " .format(LED.MAX_RATIO_GREEN, LED.DUTYCYCLE_GREEN))
        print("     BLUE         {0}                {1}        " .format(LED.MAX_RATIO_BLUE, LED.DUTYCYCLE_BLUE))
        print("\n          STATE   -> ", LED.STATE)
        print("\n          SWITCH  -> ", LED.SWITCH)
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
            # Calculate new ratios and update to new duty cycle values
            LED.MAX_RATIO_RED = newRED
            LED.MAX_RATIO_GREEN = newGREEN
            LED.MAX_RATIO_BLUE = newBLUE

            # Calculate new duty cycle values and save them
            LED.DUTYCYCLE_RED = 0 if 1 - newRED == 0 else ((1 - newRED) * MINIMAL_LIGHT_VALUE) - 1
            LED.DUTYCYCLE_GREEN = 0 if 1 - newGREEN == 0 else ((1 - newGREEN) * MINIMAL_LIGHT_VALUE) - 1
            LED.DUTYCYCLE_BLUE = 0 if 1 - newBLUE == 0 else ((1 - newBLUE) * MINIMAL_LIGHT_VALUE) - 1            

            # Set appropriate duty cycles for each color channel
            LED.LED_RED.duty_cycle = int(LED.DUTYCYCLE_RED)
            LED.LED_GREEN.duty_cycle = int(LED.DUTYCYCLE_GREEN)
            LED.LED_BLUE.duty_cycle = int(LED.DUTYCYCLE_BLUE)

    def setIntensityRED(LED, VALUE):
        # Check if values are out of range
        if VALUE < 0 or VALUE > 1:
            return print("Values are out of range. Please re-enter values.")
        else: 
            # Multiply duty cycle ratio to the set maximum ratio for each RGB channel corresponding to appropriate light levels for each color ratio mix
            # Calculate duty cycle target values for each ratio by multiplying to MINIMAL_LIGHT_VALUE
            RED_TARGET = 0 if 1 - VALUE == 0 else (LED.MAX_RATIO_RED * (1 - VALUE) * MINIMAL_LIGHT_VALUE) - 1

            # Check if new RGB targets are less or greater than the desired value to apply appropriate dimming control
            # Update red
            if RED_TARGET > LED.DUTYCYCLE_RED:
                # Decrease brightness
                try:
                    print("Decreasing brightness...", end = " ")                    
                    for i in range(int(LED.DUTYCYCLE_RED), int(RED_TARGET)):
                        LED.LED_RED.duty_cycle = i
                    print("...task done.")
                    LED.LED_RED.duty_cycle = int(RED_TARGET)                      
                except Exception as e:
                    print("Error occured: " + str(e))
            else:
                # Increase brightness
                try:
                    print("Increasing brightness...", end = " ")
                    for i in range(int(LED.DUTYCYCLE_RED), int(RED_TARGET), -1):
                        LED.LED_RED.duty_cycle = i
                    print("...task done.")
                    LED.LED_RED.duty_cycle = int(RED_TARGET)
                except Exception as e:
                    print("Error occured: " + str(e))

    def setIntensityGREEN(LED, VALUE):
        # Check if values are out of range
        if VALUE < 0 or VALUE > 1:
            return print("Values are out of range. Please re-enter values.")
        else: 
            # Multiply duty cycle ratio to the set maximum ratio for each RGB channel corresponding to appropriate light levels for each color ratio mix
            # Calculate duty cycle target values for each ratio by multiplying to MINIMAL_LIGHT_VALUE
            GREEN_TARGET = 0 if 1 - VALUE == 0 else (LED.MAX_RATIO_GREEN * (1 - VALUE) * MINIMAL_LIGHT_VALUE) - 1

            # Check if new RGB targets are less or greater than the desired value to apply appropriate dimming control
            # Update green
            if GREEN_TARGET > LED.DUTYCYCLE_GREEN:
                # Decrease brightness
                try:
                    print("Decreasing brightness...", end = " ")
                    for i in range(int(LED.DUTYCYCLE_GREEN), int(GREEN_TARGET)):
                        LED.LED_GREEN.duty_cycle = i
                    print("... task done.")
                    LED.LED_GREEN.duty_cycle = int(GREEN_TARGET)                
                except Exception as e:
                    print("Error occured: " + str(e))
            else:
                # Increase brightness
                try:
                    print("Increasing brightness...", end = " ")
                    for i in range(int(LED.DUTYCYCLE_GREEN), int(GREEN_TARGET), -1):
                        LED.LED_GREEN.duty_cycle = i
                    print("...task done.")
                    LED.LED_GREEN.duty_cycle = int(GREEN_TARGET)
                except Exception as e:
                    print("Error occured: " + str(e))

    def setIntensityBLUE(LED, VALUE):
        # Check if values are out of range
        if VALUE < 0 or VALUE > 1:
            return print("Values are out of range. Please re-enter values.")
        else: 
            # Multiply duty cycle ratio to the set maximum ratio for each RGB channel corresponding to appropriate light levels for each color ratio mix
            # Calculate duty cycle target values for each ratio by multiplying to MINIMAL_LIGHT_VALUE
            BLUE_TARGET = 0 if 1 - VALUE == 0 else (LED.MAX_RATIO_BLUE * (1 - VALUE) * MINIMAL_LIGHT_VALUE) - 1

            # Check if new RGB targets are less or greater than the desired value to apply appropriate dimming control
            # Update blue           
            if BLUE_TARGET > LED.DUTYCYCLE_RED:
                # Decrease brightness
                try:
                    print("Decreasing brightness...", end = " ")
                    for i in range(int(LED.DUTYCYCLE_BLUE), int(BLUE_TARGET)):
                        LED.LED_BLUE.duty_cycle = i
                    print("... task done.")
                    LED.LED_BLUE.duty_cycle = int(BLUE_TARGET)                
                except Exception as e:
                    print("Error occured: " + str(e))
            else:
                # Increase brightness
                try:
                    print("Increasing brightness...", end = " ")
                    for i in range(int(LED.DUTYCYCLE_BLUE), int(BLUE_TARGET), -1):
                        LED.LED_BLUE.duty_cycle = i
                    print("...task done.")
                    LED.LED_BLUE.duty_cycle = int(BLUE_TARGET)                
                except Exception as e:
                    print("Error occured: " + str(e))
                             
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
        # Gets spectral data from AS7341 sensor object and return the data in a list
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

def LIGHT_MONITORING_TEST(sensor):
    print("================================================")
    print("             AS7341 Spectral Data")
    sensor.disp_freq()
    print("================================================")

def LIGHT_CONTROL_TEST(LEDPANEL):

    x = input("Enter to start test by turning on LED panel")
    LEDPANEL.turnON()
    time.sleep(3)

    x = input("Enter to start test for each color channel")
    print("Testing red...")
    LEDPANEL.setRatioRGB(1, 0, 0)
    LEDPANEL.getConfig()    
    x = input("Testing Red done. Enter for next")
    print("Testing green...")
    LEDPANEL.setRatioRGB(0, 1, 0)
    LEDPANEL.getConfig()    
    x = input("Testing Green done. Enter for next")
    print("Testing blue...")
    LEDPANEL.setRatioRGB(0, 0, 1)    
    LEDPANEL.getConfig()    
    x = input("Testing Blue done. Enter for next")

    x = input("Enter to set intensity to 50% and ratio to max")
    LEDPANEL.setRatioRGB(1, 1, 1)    
    LEDPANEL.setIntensityRED(0.5)
    LEDPANEL.setIntensityGREEN(0.5)
    LEDPANEL.setIntensityBLUE(0.5)
    LEDPANEL.getConfig()

    x = input("Enter to set ratio to 25%, 50%, 75%")
    LEDPANEL.setRatioRGB(.25, .5, .75)
    LEDPANEL.getConfig()

    x = input("Enter to next test, check if LED config was updated")
    x = input("Enter to set intensity to full bright")
    LEDPANEL.setIntensityRED(0)
    LEDPANEL.setIntensityGREEN(0)
    LEDPANEL.setIntensityBLUE(0)
    LEDPANEL.getConfig()

    x = input("Enter to set new ratio again, full bright")
    LEDPANEL.setRatioRGB(1, 1, 1)
    LEDPANEL.getConfig()

    # Try wrong values
    x = input("Entering 1.1 to try for wrong values for intensity")
    LEDPANEL.setIntensityRED(1.1)
    LEDPANEL.setIntensityGREEN(1.1)
    LEDPANEL.setIntensityBLUE(1.1)

    x = input("Entering 0.1, 1.1, 1 to try for wrong values for ratio")
    LEDPANEL.setRatioRGB(0.1, 1.1, 1)

    x = input("Enter to finish test by turning off LED panel")
    
    LEDPANEL.turnOFF()

    time.sleep(3)

    # Create function to set all duty cycles to 0

    print("Testing for light controller is done.")

def LIGHT_CONTROL_TEST_2(LEDPANEL):
    LEDPANEL.turnON()

    LEDPANEL.getConfig()

    intensity_counter = 0

    try:
        for x in range(20):
            print("Updating intensity...")
            LEDPANEL.setIntensityRED(intensity_counter)
            LEDPANEL.setIntensityGREEN(intensity_counter)
            LEDPANEL.setIntensityBLUE(intensity_counter)            
            print("Intensity set to ", intensity_counter)
            LEDPANEL.getConfig()
            x = input("Enter to increment intensity by 5%...")
            intensity_counter += 0.05
    except Exception as e:
        print("Encountered an error: " + str(e))
    
    LEDPANEL.turnOFF()

def SPECTRAL_DATA_CAPTURE(PANEL_TOP, SENSOR_ONE):

    PANEL_TOP.turnOFF()

    print("|=========================================================|\n")
    print("               SPECTRAL DATA CAPTURE PROGRAM                 ")
    print("|=========================================================|\n\n")
    x = input("                 Press enter to continue                     \n\n\n\n")
    PANEL_TOP.turnON()

    intensity_counter = 0.05

    try:
        # Set brightness to 5% initial
        PANEL_TOP.setIntensityRED(intensity_counter)
        PANEL_TOP.setIntensityGREEN(intensity_counter)
        PANEL_TOP.setIntensityBLUE(intensity_counter)

        # Create list for storing data samples
        samples = [["CH1", "CH2", "CH3", "CH4", "CH5", "CH6", "CH7", "CH8", "NIR", "PPFD"]]
        
        # Iterate data capture for 20 light levels
        for x in range(3):
            try:
                spectraldata = SENSOR_ONE.get_spectraldata()
                print("Spectral data captured at light intensity {0} ...".format(intensity_counter))
            except:
                print("Spectral data capture failed")
            PPFD = input("Enter equivalent PPFD: ")
        
            spectraldata.append(PPFD)
            spectraldata
            samples.append(spectraldata)
            samples

            # Increase brightness by 5%
            print("\n\nIncreasing brightness by  5%...")
            intensity_counter += 0.05
            PANEL_TOP.setIntensityRED(intensity_counter)
            PANEL_TOP.setIntensityGREEN(intensity_counter)
            PANEL_TOP.setIntensityBLUE(intensity_counter)

        print("Spectral data capture program has finished...")

        # Save data values in excel file
        numpy.savetxt("spd.csv", samples, delimiter = ",")
    except Exception as e:
        print("Spectral data capture program encountered an error: " + str(e))


def main():

    spectralsensor = SpectralSensor(spectrometer)

    # Initialize panel with OFF and light intensities are LOW
    # Arguments in order: RGB Ratio (0 to 1), TCA objects, MOSFET Switch GPIO Pin, Switch state (false for OFF), Photoperiod (Day, night)
    PANEL_TOP = LEDPanel( [1, 1, 1], [PWM_CONTROLLER.channels[4], PWM_CONTROLLER.channels[5], PWM_CONTROLLER.channels[6]], 17, False, [12, 12])

    # Uncomment to conduct light controlling tests
    # LIGHT_CONTROL_TEST(PANEL_TOP) # First light control test
    # LIGHT_CONTROL_TEST_2(PANEL_TOP) # Second light control test

    # Uncomment to conduct light monitoring tests
    # LIGHT_MONITORING_TEST(spectralsensor)

    # Uncomment to conduct spectral data acquisition tests
    SPECTRAL_DATA_CAPTURE(PANEL_TOP, spectralsensor)

if __name__=="__main__":
    main()
