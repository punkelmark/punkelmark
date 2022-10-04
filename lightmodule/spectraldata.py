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
        # Create instance of the light controllers
        LED.LED_RED = RGB_CHANNEL[0]
        LED.LED_GREEN = RGB_CHANNEL[1]
        LED.LED_BLUE = RGB_CHANNEL[2]

        # Set RGB ratios in float between values 0 to 1, 1 for max brightness
        LED.MAX_RATIO_RED = RGB_RATIO[0]    
        LED.MAX_RATIO_GREEN = RGB_RATIO[1]  
        LED.MAX_RATIO_BLUE = RGB_RATIO[2]   

        # Set initial duty cycles for each, must be in integer between 0 to 66535
        LED.DUTYCYCLE_RED = RGB_DUTYCYCLE[0]
        LED.DUTYCYCLE_GREEN = RGB_DUTYCYCLE[1]
        LED.DUTYCYCLE_BLUE = RGB_DUTYCYCLE[2]

        # Set STATE and PHOTOPERIOD values
        LED.STATE = STATE               # ON/OFF
        LED.PHOTOPERIOD = PHOTOPERIOD   # Light cycle


    def setRatioRGB(LED, newRED, newGREEN, newBLUE): 
        # Defines new RGB ratios, by default, will set duty cycles to max per ratio
        # Must input in float between 0 to 1

        # Calculate new ratios and set new duty cycles
        LED.MAX_RATIO_RED = newRED * 65536
        LED.MAX_RATIO_GREEN = newGREEN * 65536
        LED.MAX_RATIO_BLUE = newBLUE * 65536

        LED.DUTYCYCLE_RED = LED.MAX_RATIO_RED - 1
        LED.DUTYCYCLE_GREEN = LED.MAX_RATIO_GREEN - 1
        LED.DUTYCYCLE_BLUE = LED.MAX_RATIO_BLUE - 1

        # Set appropriate duty cycles for each, convert values to hex notation
        LED.LED_RED.duty_cycle = hex(int(LED.DUTYCYCLE_RED))
        LED.LED_GREEN.duty_cycle = hex(int(LED.DUTYCYCLE_GREEN))
        LED.LED_BLUE.duty_cycle = hex(int(LED.DUTYCYCLE_BLUE))

    def setIntensity(LED, VALUE):
        # Calculate for new intensity values based on set RGB ratios
        RED_TARGET = LED.MAX_RATIO_RED * VALUE * 65536
        GREEN_TARGET = LED.MAX_RATIO_GREEN * VALUE * 65536
        BLUE_TARGET = LED.MAX_RATIO_BLUE * VALUE * 65536

        LED.DUTYCYCLE_RED = RED_TARGET - 1
        LED.DUTYCYCLE_GREEN = GREEN_TARGET - 1
        LED.DUTYCYCLE_BLUE = BLUE_TARGET - 1
        
        # Update red
        if RED_TARGET - 1 > LED.DUTYCYCLE_RED:
            # Increase brightness
            for i in range(int(LED.DUTYCYCLE_RED), RED_TARGET):
                LED.LED_RED.duty_cycle = i
                time.sleep(0.5)
        else:
            # Decrease brightness
            for i in range(int(LED.DUTYCYCLE_RED), RED_TARGET, -1):
                LED.LED_RED.duty_cycle = i
                time.sleep(0.5)

        # Update green
        if GREEN_TARGET - 1 > LED.DUTYCYCLE_GREEN:
            # Increase brightness
            for i in range(int(LED.DUTYCYCLE_GREEN), GREEN_TARGET):
                LED.LED_GREEN.duty_cycle = i
                time.sleep(0.5)
        else:
            # Decrease brightness
            for i in range(int(LED.DUTYCYCLE_GREEN), GREEN_TARGET, -1):
                LED.LED_GREEN.duty_cycle = i
                time.sleep(0.5)
        
        # Update blue
        if BLUE_TARGET - 1 > LED.DUTYCYCLE_BLUE:
            # Increase brightness
            for i in range(int(LED.DUTYCYCLE_BLUE), BLUE_TARGET):
                LED.LED_BLUE.duty_cycle = i
                time.sleep(0.5)
        else:
            # Decrease brightness
            for i in range(int(LED.DUTYCYCLE_BLUE  ), BLUE_TARGET, -1):
                LED.LED_BLUE.duty_cycle = i
                time.sleep(0.5)
        
                
    def turnON(LED):
        LED.STATE = True
        # execute code for switching MOSFET modules

    def turnOFF(LED):
        LED.STATE = False
        # execute code for switching MOSFET modules
        return 0

    def setPHOTOPERIOD(LED, VALUE):
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

def LIGHT_MONITORING_TEST(SENSOR_TOP, SENSOR_MID):
    
    print("\n###### FOR SENSOR TOP ######")
    SENSOR_TOP.disp_freq()
    print("\n###### FOR SENSOR MID ######")
    SENSOR_MID.disp_freq()

def main():
    
    # Create light controller and monitor objects
    
    # For light monitoring, create object for AS7341

    SENSOR_TOP = SpectralSensor(AS7341(I2C_MUX[4]))
    SENSOR_MID = SpectralSensor(AS7341(I2C_MUX[3]))

    # For light control, create object for TCA9548A
    PANEL_TOP = LEDPanel( [1, 1, 1], [PWM_CONTROLLER.channels[4], PWM_CONTROLLER.channels[5], PWM_CONTROLLER.channels[6]], [0, 0, 0], False, [12, 12])

    LIGHT_MONITORING_TEST(SENSOR_TOP, SENSOR_MID)

    # capture_spectraldata()

    pass

if __name__=="__main__":
    main()
