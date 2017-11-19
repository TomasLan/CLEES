# ----------------------------------
#             MSS IO Module
# By  : Tompa
# date: 2017-11-19
# ----------------------------------


# --------- Hardware Definition ---------
# Define what Hardware you ar running on by
# Comment out all except the platform you
# are running on
HW = "RPi-3B"      # Raspberry Pi 3 Model B
#HW = "OPi0-H2"     # Orange Pi Zero with H2 Chipset

# --- I2C Hardware

# PCA9685
number_of_pca9685 = 1     # Number of pca9685 modules connected to I2c
start_adr_pca9685 = 0x40  # Adress to first pca9685 module.
                          # Aditionals modules excepts to be on consecutive adresses
freq_pca9685 = [50,60]    # List PWM freq for every pwm. Number of values in list must match number_of_pca9685

# PCF8574
# Comes in two flavors with different adress space and will here be defined as two separat board types with their lists.
number_of_pcf8574 = 2     # Number of pcf8574 modules connected to I2c
start_adr_pcf8574 = 0x20  # Adress to first pcf8574 module.
                          # Aditionals modules excepts to be on consecutive adresses
number_of_pcf8574A = 1    # Number of pcf8574A modules connected to I2c
start_adr_pcf8574A = 0x38 # Adress to first pcf8574A module.
                          # Aditionals modules excepts to be on consecutive adresses


# --- GPIO
# List Board Connector pin numbers separated by commas
# Boardspins means the actual pin number in the board connector, not Port och Soc pin numbering
# Boardpins that are not GPIO (eg tied to GND, VCC , .. ) can ofcasue not be used and will through an error
# Don't use boardpins = 3+5 that is used for I2c since that will screw up I2c communication
Boardpins_used_for_input  = [19]
Boardpins_used_for_output = [23]



# ====================== IMPELEMTATION ===================
#
# Changing stuff beyond this point is for Developers only
#
# ========================================================
import Adafruit_PCA9685
import smbus



# ------------- Generic Calls -----------
# Calling code should use the generic calls to
# communicate with the hardware
# Before any call the IOmodule_Init must be called

def IOmodule_Init():

    # --- Initiate 9685 modules
    try:
        global pca9685_list
        pca9685_list = []  # create a list
        for i in range(0,number_of_pca9685):
            if HW == "RPi-3B":
                pca9685_list.append(Adafruit_PCA9685.PCA9685(address=start_adr_pca9685+i, busnum=1))
            if HW == "OPi0-H2":
                pca9685_list.append(Adafruit_PCA9685.PCA9685(address=start_adr_pca9685+i, busnum=0))
            pca9685_list[i].set_pwm_freq(freq_pca9685[i])
    except IOError as e:
        ErrTxt = "{0}: {1}".format(e.errno,e.strerror)
        if e.errno == 121: ErrTxt += " - Problem could be that a defined PCA9685 I2C device is not present on the bus"
        if e.errno == 2:   ErrTxt += " - Problem could be that /dev/i2c is not activated or have a different device number"
        return (ErrTxt)
    except:
        return ("Init PCA9685 failed")

    # --- Initiate GPIO
    try:
        global GPIO
        if HW == "RPi-3B":
            import RPi.GPIO as GPIO
        if HW == "OPi0-H2":
            import OPi.GPIO as GPIO
        GPIO.setwarnings(0) 
        GPIO.setmode(GPIO.BOARD)
        if Boardpins_used_for_output != None : 
            for i in Boardpins_used_for_output :
                GPIO.setup(i, GPIO.OUT)
        if Boardpins_used_for_input != None :
            for i in Boardpins_used_for_input :
                GPIO.setup(i, GPIO.IN)
    except Exception, e:
        ErrTxt = "GPIO " + `e`
        return (ErrTxt)
    except:
        return ("Init GPIO failed")

    # --- PCF8574
    try:
        global pcf8574_list
        pcf8574_list = []  # Creates a list
        for i in range(0,number_of_pcf8574):
            if HW == "RPi-3B":
                pcf8574_list.append(smbus.SMBus(1))
            if HW == "OPi0-H2":
                pcf8574_list.append(smbus.SMBus(0))
            pcf8574_list[i].write_byte(start_adr_pcf8574+i,0xFF)  # Makes all inputs
        global pcf8574A_list
        pcf8574A_list = []  # Creates a list
        for i in range(0,number_of_pcf8574A):
            if HW == "RPi-3B":
                pcf8574A_list.append(smbus.SMBus(1))
            if HW == "OPi0-H2":
                pcf8574A_list.append(smbus.SMBus(0))
            pcf8574A_list[i].write_byte(start_adr_pcf8574A+i,0xFF)  # Makes all inputs
    except IOError as e:
        ErrTxt = "{0}: {1}".format(e.errno,e.strerror)
        if e.errno == 2:   ErrTxt += " - Problem could be that /dev/i2c is not activated or have a different device number"
        if e.errno == 6:   ErrTxt += " - Problem could be that a defined PCF8574 I2C device is not present on the bus"
        return (ErrTxt)
    except:
        return ("Init PCF8574 failed")
    return ("")



def Set_pca9685 (boardnr=0, pwmnr=0, pwmwidth=0):
    if pwmwidth > 4095:
        pca9685_list[boardnr].set_pwm(pwmnr, 4096, 0)
    else:    
        pca9685_list[boardnr].set_pwm(pwmnr, 0, pwmwidth)
    return (0)

def Set_GPIO(gpionr,outputstate):
    GPIO.output(gpionr, outputstate)  
    return (0)

def Get_GPIO(gpionr):
    return (GPIO.input(gpionr))

def Close_GPIO():
    GPIO.cleanup()
    return (0)

def Set_pfc8574(boardnr,abyte):
    pcf8574_list[boardnr].write_byte(start_adr_pcf8574+boardnr,abyte)
    return (0)

def Get_pfc8574(boardnr):
    return(pcf8574_list[boardnr].read_byte(start_adr_pcf8574+boardnr))

def Set_pfc8574A(boardnr,abyte):
    pcf8574A_list[boardnr].write_byte(start_adr_pcf8574A+boardnr,abyte)
    return (0)

def Get_pfc8574A(boardnr):
    return(pcf8574A_list[boardnr].read_byte(start_adr_pcf8574A+boardnr))

