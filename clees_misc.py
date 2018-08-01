# ----------------------------------
#             CLEES Misc
# Author : Tompa
# ----------------------------------

# ------------------ General libs --------------
import time

# ------------------ Private Libs --------------
import clees_settings
import clees_io
import clees_objects


# --- date/time -----------------------------------------------
def  formatdatetime(tstruct):
    resultdate = "%i" %(tstruct.tm_year)
    if tstruct.tm_mon < 10:
        resultdate += "0%i" %(tstruct.tm_mon)
    else:
        resultdate += "%i" %(tstruct.tm_mon)
    if tstruct.tm_mday < 10:
        resultdate += "0%i" %(tstruct.tm_mday)
    else:
        resultdate += "%i" %(tstruct.tm_mday)
    resultdate += '-'
    if tstruct.tm_hour < 10:
        resultdate += "0%i" %(tstruct.tm_hour)
    else:
        resultdate += "%i" %(tstruct.tm_hour)
    resultdate += ':'
    if tstruct.tm_min < 10:
        resultdate += "0%i" %(tstruct.tm_min)
    else:
        resultdate += "%i" %(tstruct.tm_min)
    resultdate += ':'
    if tstruct.tm_sec < 10:
        resultdate += "0%i" %(tstruct.tm_sec)
    else:
        resultdate += "%i" %(tstruct.tm_sec)
    return (resultdate)


def getgmtdatetimestr():
    return (formatdatetime(time.gmtime(time.time())))
# -------------------------------------------------------------


statusledstate = 0
sysledgpio = 0
sysledobj = ""

# --- init
def init():
    global statusledstate
    global sysledgpio
    global sysledobj
    sysledgpio = clees_settings.get('systemledgpio')
    if sysledgpio > 40:
        sysledgpio == 0
    sysledobj = clees_settings.get('systemledoutputobjectid')
    statusledstate = 1
    clr_statusled()
    return

def set_statusled():
    global statusledstate
    global sysledgpio
    global sysledobj
    if statusledstate == 0:
        if sysledgpio > 0: 
            clees_io.Set_GPIO(sysledgpio,1)
        if sysledobj != "":
            clees_objects.set_outputobject(sysledobj,"activate")
    statusledstate = 1        
    return(0)
                    
def clr_statusled():
    global statusledstate
    global sysledgpio
    global sysledobj
    if statusledstate == 1:
        if sysledgpio > 0:
            clees_io.Set_GPIO(sysledgpio,0)
        if sysledobj != "":
            clees_objects.set_outputobject(sysledobj,"deactivate")
    statusledstate = 0        
    return(0)

