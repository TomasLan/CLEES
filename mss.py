

# ----------------------------
# Name: mss (= ModuleSectionServer)
# By  : Tompa
# date: 2017-11-19
# ----------------------------
# Works on both RPi and OPi

VERS = "0.5.2"    # Added Support for "mtlo" (=model train layout object) = Turnouts




# Controlling Model Train Layout Objects
#
# ---- Controlling Turnouts ----
# Call:
#   http://172.16.1.14/mss?object=turnout&index=0&cmd=close
#
#       object=turnout  Identifies layout object type
#       index=0         Index 0.. of the object position in the Turnout list defined in the mtlo file
#       cmd=close       Operation to perform on that object
#
#
# Low level commands
#
# ---- Controlling PWMs  ----
# Call:
#   http://172.16.1.14/mss?device=pca9685&pwmmodule=0&pwmnr=0&pwmwidth=250&op=set
#        
#       device=pca9685  Name of the pwm module type
#       pwmmodule=0     0 => first module => using starting i2c-address
#                       1 => second module => using starting i2c-adress+1
#                       2 => third module ...
#       pwmnr=0         points out local pwm on a singel module, could be 0..15
#       pwmwidth=250    could be any number 0..4095 0=>0% pulswidth, 4095=>100% pulsewidth
#       op=set          To set a new value
#
# ---- Controlling GPIO  ----
# Call:
#   http://172.16.1.14/mss?device=gpio&gpionr=4&gpoistate=1&op=set
#        
#       device=gpio     Referes to the gpio pins in the 26/40pin connector
#       gpiopin=4       GPIO conector pin number (1..26 or 1..40 depening on hardware)
#       gpiostate=1     set to 0 or 1
#       op=set/get     To set a new value. use "get" to read. A read value will be returned in the HTML body as gpio4=1
#
# ---- Controlling IOmoduled
# Call:
#   http://172.16.1.14/mss?device=pcf8574&iommodule=0&ionr=0&iovalue=255&op=set
#        
#       device=pcf8574  Name of the io modul type
#       iommodule=0     0 => first module => using starting i2c-address
#                       1 => second module => using starting i2c-adress+1
#                       2 => third module ...
#       ionr=0/byte     bit 0..7 or byte=8bits together
#       iovalue=0..255  When set  
#       op=set/get      To set a new value. use "get" to read. A read value will be returned in the HTML body as pcf8574-n=1 where n=module number
#
# Call:
#   http://172.16.1.14/mss?device=pcf8574A&iommodule=0&ionr=0&iovalue=255&op=set
#        
#       device=pcf8574A  Name of the io modul type
#       iommodule=0      0 => first module => using starting i2c-address
#                        1 => second module => using starting i2c-adress+1
#                        2 => third module ...
#       ionr=0/byte      bit 0..7 or byte=8bits together
#       iovalue=0..255   When set  
#       op=set/get       To set a new value. use "get" to read. A read value will be returned in the HTML body as pcf8574A-n=1 where n=module number




DBGPRNT = 'Y'  # 'Y' = on,  '' = off to prevent debug printouts

# --- General libs ---
import socket
import select
import time
import string
from BaseHTTPServer import BaseHTTPRequestHandler
from StringIO import StringIO
from urlparse import urlparse, parse_qs

# --- Private Libs
import mss_iomodule
import mss_mtlo


class HTTPRequest(BaseHTTPRequestHandler):
    def __init__(self, request_text):
        self.rfile = StringIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message



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



# --- log/file/DBG -------------------------------------------------

inlogfile = ['io','socket','highlevelcmd']

def log2file(logline):
    termprint(logline)
    logline = logline.replace("\r", " ")
    logline = logline.replace("\n", " ")
    with open("msslog.txt","a") as f:
        f.write("%s | %s \r\n" %(getgmtdatetimestr(),logline))
        f.flush()

def logerror(errortxt):
    log2file("ERROR: %s" %(errortxt))
 
def logtxt(txt):
    log2file("%s" %(txt))

def logsocket(txt):
    if "socket" in inlogfile: logtxt(txt)

def logio(txt):
    if "io" in inlogfile: logtxt(txt)

def termprint(txt):
    if DBGPRNT == 'Y': print (txt)

ERROR_TEXT = ['',
              'GETparam "pwmmodule" is missing',             #1
              'GETparam "pwmindex" is missing',              #2
              'GETparam "pwmwidth" is missing',              #3
              'GETparam "op" is missing',                    #4 
              'GETparam "gpiopin" is missing',               #5
              'GETparam "op" must be "set" or "get"',        #6
              'GETparam "gpiostate" is missing',             #7
              'GETparam "iomodule" is missing',              #8
              'GETparam "iovalue" is missing',               #9
              'GETparam "index" is missing',                 #10
              'GETparam "cmd" is missing',                   #11
              'GETparam "cmd" must be "C" or "T"',           #12
              
              'Unknow Error'
              ]
# -------------------------------------------------------------




# --- Low Level Command from Client ---------------------------

def pca9685cmd ():
    # parse incomming command and set new pwm value
    if 'pwmmodule' not in mss_command : return (1) # Error=1
    pwm_module = int(mss_command['pwmmodule'][0]);
    if 'pwmnr' not in mss_command : return (2) # Error=2
    pwm_nr = int(mss_command['pwmnr'][0]);
    if 'pwmwidth' not in mss_command : return (3) # Error=3
    pwm_width = int(mss_command['pwmwidth'][0]);
    if 'op' not in mss_command : return (4) # Error=4
    pwmop = mss_command['op'][0];
    if pwmop == 'set':
        # set pwm
        mss_iomodule.Set_pca9685(pwm_module,pwm_nr,pwm_width)
        logio("Set PWMmodule=%i PWMnr=%i PWMwidth=%i" %(pwm_module,pwm_nr,pwm_width))
        return (0)


def gpiocmd ():
    global mss_returnvalue
    # parse incomming command and set/get gpio
    if 'gpiopin' not in mss_command : return (5) # Error=5
    if mss_command['gpiopin'][0] == 'all':
        #lets multi operate
        if 'op' not in mss_command : return (4) # Error=4
        gpioop = mss_command['op'][0];
        if gpioop == 'set':
            for i in range(0,len(mss_iomodule.Boardpins_used_for_output)):
                gpiopin = mss_iomodule.Boardpins_used_for_output[i]
                gpiostate = int(mss_command['gpiostate'][0]);
                mss_iomodule.Set_GPIO(gpiopin,gpiostate)
                logio("Set gpio #%i state=%i" %(gpiopin,gpiostate))
                return (0)
        elif gpioop == 'get':
            # get gpio
            for i in range(0,len(mss_iomodule.Boardpins_used_for_input)):
                gpiopin = mss_iomodule.Boardpins_used_for_input[i]
                gpiostate = mss_iomodule.Get_GPIO(gpiopin)
                mss_returnvalue += "gpio%i=%i<br>" %(gpiopin,gpiostate)
                logio("Get gpio #%i state=%i" %(gpiopin,gpiostate))
                return (0)
        else:
            return (6) # Error=6
    else :
        gpiopin = int(mss_command['gpiopin'][0]);
        if 'op' not in mss_command : return (4) # Error=4
        gpioop = mss_command['op'][0];
        if gpioop == 'set':
            # set gpio
            if 'gpiostate' not in mss_command : return (7) # Error=7
            gpiostate = int(mss_command['gpiostate'][0]);
            mss_iomodule.Set_GPIO(gpiopin,gpiostate)
            logio("Set gpio #%i state=%i" %(gpiopin,gpiostate))
            return (0)
        elif gpioop == 'get':
            # get gpio
            gpiostate = mss_iomodule.Get_GPIO(gpiopin)
            mss_returnvalue += "gpio%i=%i<br>" %(gpiopin,gpiostate)
            logio("Get gpio #%i state=%i" %(gpiopin,gpiostate))
            return (0)
        else:
            return (6) # Error=6

def pcf8574cmd ():
    global mss_returnvalue
    # parse incomming command and set/get pcf8574 pins
    if 'iomodule' not in mss_command : return (8) # Error=8
    io_module = int(mss_command['iomodule'][0]);
    if 'op' not in mss_command : return (4) # Error=4
    io_op = mss_command['op'][0];
    if io_op == 'set':
        # set iomodule byte
        if 'iovalue' not in mss_command : return (9) # Error=9
        io_value = int(mss_command['iovalue'][0]);
        mss_iomodule.Set_pfc8574(io_module,io_value)
        logio("Set pcf8574 #%i state=%i" %(io_module,io_value))
        return (0)
    elif io_op == 'get':
        # get iomodule byte
        io_value = mss_iomodule.Get_pfc8574(io_module)
        mss_returnvalue += "pcf8574-%i=%i<br>" %(io_module,io_value)
        logio("Get pcf8574 #%i value=%i" %(io_module,io_value))
        return (0)
    else:
        return (6) # Error=6
        

def pcf8574Acmd ():
    global mss_returnvalue
    # parse incomming command and set/get pcf8574A pins
    if 'iomodule' not in mss_command : return (8) # Error=8
    io_module = int(mss_command['iomodule'][0]);
    if 'op' not in mss_command : return (4) # Error=4
    io_op = mss_command['op'][0];
    if io_op == 'set':
        # set iomodule byte
        if 'iovalue' not in mss_command : return (9) # Error=9
        io_value = int(mss_command['iovalue'][0]);
        mss_iomodule.Set_pfc8574A(io_module,io_value)
        logio("Set pcf8574A #%i state=%i" %(io_module,io_value))
        return (0)
    elif io_op == 'get':
        # get iomodule byte
        io_value = mss_iomodule.Get_pfc8574A(io_module)
        mss_returnvalue += "pcf8574A-%i=%i<br>" %(io_module,io_value)
        logio("Get pcf8574A #%i value=%i" %(io_module,io_value))
        return (0)
    else:
        return (6) # Error=6
      
# -------------------------------------------------------------


# --- Object command from client ------------------------------
def turnoutcmd():
    global mss_returnvalue
    # parse incomming command and to contol turnouts
    if 'index' not in mss_command : return (10) # Error=10
    turnout_index = int(mss_command['index'][0]);
    if 'cmd' not in mss_command : return (11) # Error=11
    turnout_cmd = mss_command['cmd'][0];
    if turnout_cmd == 'C':
        return (mss_mtlo.turnout_close(turnout_index))
    elif turnout_cmd == 'T':
        return (mss_mtlo.turnout_throw(turnout_index))
    else:     
        return(12) # Error=12

# -------------------------------------------------------------





# --------------------------------------------------------------
#                              INIT
# --------------------------------------------------------------

# --- Start loggning
logtxt ("Starting MSS Ver:%s" %(VERS))

# --- Init HW
ErrTxt = mss_iomodule.IOmodule_Init()
if ErrTxt != "" :
    logerror (ErrTxt)

# --- Init MTLO
mss_mtlo.init()

# --- Init Socket
host = '' 
port = 8080
srvsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srvsock.bind((host, port))
srvsock.listen(1) # no que

# --- Init misc
mss_command     = ''


# --------------------------------------------------------------
#                              MAIN
# --------------------------------------------------------------


try:
    logtxt ("MSS Running")
    while ('mssshutdown' not in mss_command):

        time.sleep (0.0125)  # This while loop will run at 80Hz

        mss_mtlo.call_80Hz() 

        mss_command_error = 0
        mss_returnvalue = ''
        mss_txt = ''

        socks_ready_for_read, socks_ready_for_write, socks_with_error = select.select([srvsock],[],[srvsock],0)

        for anysock in socks_ready_for_read:
            client_conection_sock, caddr = anysock.accept()
            logsocket("Socket Connection from: " + `caddr`)
            
            req = client_conection_sock.recv(1024) 
            logsocket("Socket Connection " + `req`)

            # Client Request breakdown
            request = HTTPRequest(req)
            mss_txt =  "Client Request:\r\n"
            mss_txt += "  err:"+str(request.error_code) +"\r\n"
            mss_txt += "  cmd:"+request.command +"\r\n"
            mss_txt += "  path:"+request.path +"\r\n"
            mss_txt += "  ver:"+request.request_version +"\r\n"
            mss_txt += "  headsize:"+str(len(request.headers)) +"\r\n"
            mss_txt += "  headkeys"+`request.headers.keys()` +"\r\n"
            mss_txt += "  headhost:"+request.headers['host'] 
            logsocket(mss_txt)

            if request.error_code == None :  # no request error
                if string.find (request.path, '/mss') > -1:  # check that path includes /mss
                    mss_command = parse_qs(urlparse(request.path).query)
                    logsocket("Client request cmd %s" %(mss_command)) 

                    # --- Check incomming commands
                    try:
                        if 'device' in mss_command :
                            logsocket("Client request device="+mss_command['device'][0])
                            if mss_command['device'][0] == 'pca9685'  : mss_command_error = pca9685cmd()
                            if mss_command['device'][0] == 'gpio'     : mss_command_error = gpiocmd()
                            if mss_command['device'][0] == 'pcf8574'  : mss_command_error = pcf8574cmd()
                            if mss_command['device'][0] == 'pcf8574A' : mss_command_error = pcf8574Acmd()
                        elif 'object' in mss_command :
                            logsocket("Client request object="+mss_command['object'][0])
                            if mss_command['object'][0] == 'turnout'  : mss_command_error = turnoutcmd()
                    except: 
                        logsocket("Client request URL format incorrect")
            else:  # request has error
                logsocket("Client request failed")

            # --- Send OK reply
            if mss_command_error == 0 :
                mss_return  = "HTTP/1.0 200 OK\n"
                mss_return += "Content-Type: text/html\n\n"
                mss_return += "<html><head><title>MSS</title></head><body><H1>MSS server responce</H1>"
                if mss_returnvalue == '':
                    mss_return += "no values"
                else :
                    mss_return += mss_returnvalue
                mss_return += "</body></html>\n"
                client_conection_sock.sendall(mss_return)
            else:
                # upon error in command then return a 404 (page not found)
                mss_return  = "HTTP/1.0 404 Not Found\n"
                mss_return += "Content-Type: text/html\n\n"
                mss_return += "<html><head><title>MSS Error</title></head><body>"
                mss_return += "<H1>MSS Server Error %i </H1><br>" %(mss_command_error)
                mss_return += "cmd incomplete: %s</body></html>\n" %(ERROR_TEXT[mss_command_error])
                client_conection_sock.sendall(mss_return)
                logerror("#%i %s" %(mss_command_error,ERROR_TEXT[mss_command_error]))
            # Close this socket    
            client_conection_sock.close()

except KeyboardInterrupt:
    termprint ("\nCtrl-C pressed")
 
srvsock.close()
mss_iomodule.Close_GPIO()
logtxt ("MSS stopped gracefully")
