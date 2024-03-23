from adafruit_as7341 import AS7341
import board
import busio

i2c_monitoring = board.I2C() # uses board.SCL and board.SDA
spectrometer = AS7341(i2c_monitoring) # For light monitoring, create object for AS7341


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


def LIGHT_MONITORING_TEST(sensor):
    print("================================================")
    print("             AS7341 Spectral Data")
    sensor.disp_freq()
    print("================================================")

def main():

    spectralsensor = SpectralSensor(spectrometer)

    # Uncomment to conduct light monitoring tests
    LIGHT_MONITORING_TEST(spectralsensor)


if __name__=="__main__":
    main()
