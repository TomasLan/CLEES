# ----------------------------------
#             CLEES IO
# Author : Tompa
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
start_adr_pca9685 = 0x41  # Adress to first pca9685 module.
                          # Aditionals modules excepts to be on consecutive adresses
freq_pca9685 = [50,60]    # List PWM freq for every pwm. Number of values in list must match number_of_pca9685

# PCF8574
# Comes in two flavors with different adress space and will here be defined as two separat board types with their lists.
number_of_pcf8574 = 1     # Number of pcf8574 modules connected to I2c
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
Boardpins_used_for_input  = [18]
Boardpins_used_for_output = [22]   #22 used for status LED (Steady=online, blink=wait for broker)



# ====================== IMPELEMTATION ===================
#
# Changing stuff beyond this point is for Developers only
#
# ========================================================
import Adafruit_PCA9685
import smbus

# ----------- Memory allocation for filtering IO -------
cur_value__pcf8574 = [0,0,0,0,0,0,0,0]
filterbuf0_pcf8574 = [0,0,0,0,0,0,0,0]
filterbuf1_pcf8574 = [0,0,0,0,0,0,0,0]

cur_value__pcf8574A = [0,0,0,0,0,0,0,0]
filterbuf0_pcf8574A = [0,0,0,0,0,0,0,0]
filterbuf1_pcf8574A = [0,0,0,0,0,0,0,0]

# --- Memory allocation for Input/Output management ----
outputmirrorbits_pcf8574  = [255,255,255,255,255,255,255,255]
outputmirrorbits_pcf8574A = [255,255,255,255,255,255,255,255]


# ------------- Generic Calls -----------
# Calling code should use the generic calls to
# communicate with the hardware
# Before any call the IO_Init must be called

def IO_init():

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

def Set_pcf8574(boardnr,abyte):
    pcf8574_list[boardnr].write_byte(start_adr_pcf8574+boardnr,abyte)
    outputmirrorbits_pcf8574[boardnr] = abyte
    return (0)

def Get_pcf8574(boardnr):
    return(pcf8574_list[boardnr].read_byte(start_adr_pcf8574+boardnr))

def Get_filtered_pcf8574(boardnr):
    return(cur_value__pcf8574[boardnr])

def Set_pcf8574A(boardnr,abyte):
    pcf8574A_list[boardnr].write_byte(start_adr_pcf8574A+boardnr,abyte)
    outputmirrorbits_pcf8574A[boardnr] = abyte
    return (0)

def Get_pcf8574A(boardnr):
    return(pcf8574A_list[boardnr].read_byte(start_adr_pcf8574A+boardnr))

def Get_filtered_pcf8574A(boardnr):
    return(cur_value__pcf8574A[boardnr])

def Set_pcf8574_bit(boardnr,bitnr,bit):
    if bit == 0:
        tmpbyte = outputmirrorbits_pcf8574[boardnr]
        tmpbyte = tmpbyte & ~(1 << bitnr)
        Set_pcf8574(boardnr,tmpbyte)
    elif bit == 1:
        tmpbyte = outputmirrorbits_pcf8574[boardnr]
        tmpbyte = tmpbyte | (1 << bitnr)
        Set_pcf8574(boardnr,tmpbyte)
     
def Set_pcf8574A_bit(boardnr,bitnr,bit):
    if bit == 0:
        tmpbyte = outputmirrorbits_pcf8574A[boardnr]
        tmpbyte = tmpbyte & ~(1 << bitnr)
        Set_pcf8574A(boardnr,tmpbyte)
    elif bit == 1:
        tmpbyte = outputmirrorbits_pcf8574A[boardnr]
        tmpbyte = tmpbyte | (1 << bitnr)
        Set_pcf8574A(boardnr,tmpbyte)

def call_80Hz():
    # Read io modules and filter input signals
    for i in range(0,number_of_pcf8574):
      newvalue = Get_pcf8574(i)
      tmp = newvalue ^ filterbuf0_pcf8574[i]
      tmp = tmp | (newvalue ^ filterbuf1_pcf8574[i])
      # Bits now set in tmp means bits is not consecutive = not the same in all bytes for 3 consecutive reads
      # Now push new value to buffer
      filterbuf0_pcf8574[i] = filterbuf1_pcf8574[i]
      filterbuf1_pcf8574[i] = newvalue
      # now combine a new current value
      cur_value__pcf8574[i] = tmp & cur_value__pcf8574[i]   # cur now holds old values on all bits not consecutive
      cur_value__pcf8574[i] = ((~tmp & newvalue) | cur_value__pcf8574[i])  # tmp filter out only ok filtered bits in the new value and add them to current value

    for i in range(0,number_of_pcf8574A):
      newvalue = Get_pcf8574A(i)
      tmp = newvalue ^ filterbuf0_pcf8574A[i]
      tmp = tmp | (newvalue ^ filterbuf1_pcf8574A[i])
      # Bits now set in tmp means bits is not consecutive = not the same in all bytes for 3 consecutive reads
      # Now push new value to buffer
      filterbuf0_pcf8574A[i] = filterbuf1_pcf8574A[i]
      filterbuf1_pcf8574A[i] = newvalue
      # now combine a new current value
      cur_value__pcf8574A[i] = tmp & cur_value__pcf8574A[i]   # cur now holds old values on all bits not consecutive
      cur_value__pcf8574A[i] = ((~tmp & newvalue) | cur_value__pcf8574A[i])  # tmp filter out only ok filtered bits in the new value and add them to current value


      
    return

