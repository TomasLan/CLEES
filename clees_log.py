# ----------------------------------
#             CLEES Log
# Author : Tompa
# ----------------------------------

DBGPRNT = 'Y'  # 'Y' => on,  '' => off to prevent debug printouts



# ------------------ Private Libs --------------
import clees_misc
import clees_settings


inlogfile = []

def init():
    global inlogfile
    if clees_settings.get('log-io') == 1:
        inlogfile.append('io')
    if clees_settings.get('log-mqtt') == 1:
        inlogfile.append('mqtt')
    return(0)
    

def log2file(logline):
    termprint(logline)
    logline = logline.replace("\r", " ")
    logline = logline.replace("\n", " ")
    with open("clees_log.txt","a") as f:
        f.write("%s | %s \r\n" %(clees_misc.getgmtdatetimestr(),logline))
        f.flush()

def logerror(errortxt):
    log2file("ERROR: %s" %(errortxt))

def logwarning(warningtxt):
    log2file("WARNING: %s" %(warningtxt))    
 
def logtxt(txt):
    log2file("%s" %(txt))

def logmqtt(txt):
    if "mqtt" in inlogfile: logtxt(txt)

def logio(txt):
    if "io" in inlogfile: logtxt(txt)

def termprint(txt):
    if DBGPRNT == 'Y': print (txt)

# -------------------------------------------------------------
