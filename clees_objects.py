# ----------------------------------
#             CLEES Objects
# Model Train Layout Objects
# Author : Tompa
# ----------------------------------


# --- General libs
import json
import time


# --- Private Libs
import clees_settings
import clees_io
import clees_mqtt
import clees_log


# --- VARs
cleesObjects = []
Turnouts = []
Buttons = []
Outputs = []


def init():
    global Turnouts
    global cleesObjects
    global Buttons
    global Outputs
    with open('clees_objects.json') as f:
        cleesObjects = json.load(f)
        Turnouts = cleesObjects["turnouts"]
        Buttons  = cleesObjects["buttons"]
        Outputs  = cleesObjects["outputs"]
    
    for i in range (0,len(Turnouts)):
        # Add internal variables    
        Turnouts[i]['action'] = '' 
        Turnouts[i]['curwid'] = 0
        Turnouts[i]['cmd_topic'] = clees_mqtt.gettopicstr('cmd','t',Turnouts[i]['id'])
        # Set default positions
        if Turnouts[i]['homeposition'] == 'T':
            init_width = Turnouts[i]['pwmwidththrown']
        else:
            init_width = Turnouts[i]['pwmwidthclosed']
        clees_io.Set_pca9685(Turnouts[i]['devicenr'],Turnouts[i]['pwmnr'],init_width)
        Turnouts[i]['curwid'] = init_width
        time.sleep(cleesObjects['homepositiondelayonstart'])

    # Make our IO buffer upp to speed with real values and not defaults
    clees_io.call_80Hz()
    clees_io.call_80Hz()
    clees_io.call_80Hz()
    clees_io.call_80Hz()
    for i in range (0,len(Buttons)):
        # Add internal variables    
        if Buttons[i]['inverted'] == 1:
            Buttons[i]['curstate'] = 0
        else:
            Buttons[i]['curstate'] = 1

    for i in range (0,len(Outputs)):
        # Add internal variables
        Outputs[i]['cmd_topic'] = clees_mqtt.gettopicstr('cmd','o',Outputs[i]['id'])
        Outputs[i]['curstate'] = 0
        if Outputs[i]['inverted'] == 1:
            Outputs[i]['curstate'] = 1
        if Outputs[i]['devicetype'] == 'pcf8574':
            clees_io.Set_pcf8574_bit(Outputs[i]['devicenr'],Outputs[i]['pinnr'],Outputs[i]['curstate'])
        if Outputs[i]['devicetype'] == 'pcf8574A':
            clees_io.Set_pcf8574A_bit(Outputs[i]['devicenr'],Outputs[i]['pinnr'],Outputs[i]['curstate'])

    # Now lets check if Turnouts have slave outputs, eg turnout polarization releays
    for i in range (0,len(Turnouts)):
        if Turnouts[i]['slaveoutputid'] != '':
            # This turnout have a slave output that also shall be set to reflect turnout homepos
            if Turnouts[i]['homeposition'] == 'T':
                set_outputobject(Turnouts[i]['slaveoutputid'],'activated')
            else:
                set_outputobject(Turnouts[i]['slaveoutputid'],'deactivated')

    return(0)

def set_outputobject(objectid,state):
    global Outputs
    for i in range (0,len(Outputs)):
        if (Outputs[i]['id'] == objectid):
            if state == 'activate':
                if Outputs[i]['inverted'] == 1:
                    Outputs[i]['curstate'] = 0
                if Outputs[i]['inverted'] == 0:
                    Outputs[i]['curstate'] = 1
                if Outputs[i]['devicetype'] == 'pcf8574':
                    clees_io.Set_pcf8574_bit(Outputs[i]['devicenr'],Outputs[i]['pinnr'],Outputs[i]['curstate'])
                if Outputs[i]['devicetype'] == 'pcf8574A':
                    clees_io.Set_pcf8574A_bit(Outputs[i]['devicenr'],Outputs[i]['pinnr'],Outputs[i]['curstate'])
            if state == 'deactivate':
                if Outputs[i]['inverted'] == 1:
                    Outputs[i]['curstate'] = 1
                if Outputs[i]['inverted'] == 0:
                    Outputs[i]['curstate'] = 0
                if Outputs[i]['devicetype'] == 'pcf8574':
                    clees_io.Set_pcf8574_bit(Outputs[i]['devicenr'],Outputs[i]['pinnr'],Outputs[i]['curstate'])
                if Outputs[i]['devicetype'] == 'pcf8574A':
                    clees_io.Set_pcf8574A_bit(Outputs[i]['devicenr'],Outputs[i]['pinnr'],Outputs[i]['curstate'])
    return (0)

def read_button(i):
    global Buttons
    if Buttons[i]['devicetype'] == 'pcf8574':
        # Read pcf8574 data
        tmpbuttonstate = (1 << Buttons[i]['pinnr']) & (clees_io.Get_filtered_pcf8574(Buttons[i]['devicenr']))
    if Buttons[i]['devicetype'] == 'pcf8574A':
        # Read pcf8574 data
        tmpbuttonstate = (1 << Buttons[i]['pinnr']) & (clees_io.Get_filtered_pcf8574A(Buttons[i]['devicenr']))
    if tmpbuttonstate > 0 :
        if Buttons[i]['inverted']:
            tmpbuttonstate = 0
    else :
        if Buttons[i]['inverted']:
            tmpbuttonstate = 1
    return(tmpbuttonstate)

def send_button_activated(i):
    global Buttons
    topic = clees_mqtt.gettopicstr('rep','b',Buttons[i]['id'])
    msg = 'activated';
    clees_mqtt.publish(topic, msg)
    return(0) 


def send_button_deactivated(i):
    global Buttons
    topic = clees_mqtt.gettopicstr('rep','b',Buttons[i]['id'])
    msg = 'deactivated';
    clees_mqtt.publish(topic, msg)
    return(0) 


def report_buttons():
    global Buttons
    for i in range (0,len(Buttons)):
        if read_button(i) > 0 :
            # button is activated
            send_button_activated(i)
        else:
            # button is not activated
            send_button_deactivated(i)
    return(0)

def send_turnout_closed(i):
    global Turnouts
    topic = clees_mqtt.gettopicstr('rep','t',Turnouts[i]['id'])
    clees_mqtt.publish(topic,'closed')
    return(0)

def send_turnout_thrown(i):
    global Turnouts
    topic = clees_mqtt.gettopicstr('rep','t',Turnouts[i]['id'])
    clees_mqtt.publish(topic,'thrown')
    return(0)

def send_turnout_changing(i):
    global Turnouts
    topic = clees_mqtt.gettopicstr('rep','t',Turnouts[i]['id'])
    clees_mqtt.publish(topic,'changing')
    return(0)


def report_turnouts():
    global Turnouts
    for i in range (0,len(Turnouts)):
        if Turnouts[i]['curwid'] == Turnouts[i]['pwmwidthclosed']:
            send_turnout_closed(i)
        elif Turnouts[i]['curwid'] == Turnouts[i]['pwmwidththrown']:
            send_turnout_thrown(i)
        else:     
            send_turnout_changing(i)

    return(0)


def process_mqtt_cmd_t(topic, msg):
    global Turnuts
    for i in range (0,len(Turnouts)):
        if (Turnouts[i]['cmd_topic'] == topic):
            if msg == 'close':
                Turnouts[i]['action'] = 'C'
                send_turnout_changing(i)
            if msg == 'throw':
                Turnouts[i]['action'] = 'T'
                send_turnout_changing(i)
    return (0)

def send_output_activated(i):
    global Outputs
    topic = clees_mqtt.gettopicstr('rep','o',Outputs[i]['id'])
    clees_mqtt.publish(topic,'activated')    
    return(0)

def send_output_deactivated(i):
    global Outputs
    topic = clees_mqtt.gettopicstr('rep','o',Outputs[i]['id'])
    clees_mqtt.publish(topic,'deactivated')    
    return(0)

def report_outputs():
    global Outputs
    for i in range (0,len(Outputs)):
      if Outputs[i]['curstate'] == 0:
          if Outputs[i]['inverted']:
              send_output_activated(i)
          else:
              send_output_deactivated(i)
      else:        
          if Outputs[i]['inverted']:
              send_output_deactivated(i)
          else:
              send_output_activated(i)
    return(0)

def outputid_to_outputindex(outputid):
    global Outputs
    x = -1 # means not found
    for i in range (0,len(Outputs)):
      if Outputs[i]['id'] == outputid:
          x = i
    return(x)

def process_mqtt_cmd_o(topic, msg):
    global Outputs
    for i in range (0,len(Outputs)):
        if (Outputs[i]['cmd_topic'] == topic):
            if msg == 'activate':
                if Outputs[i]['inverted'] == 1:
                    Outputs[i]['curstate'] = 0
                if Outputs[i]['inverted'] == 0:
                    Outputs[i]['curstate'] = 1
                if Outputs[i]['devicetype'] == 'pcf8574':
                    clees_io.Set_pcf8574_bit(Outputs[i]['devicenr'],Outputs[i]['pinnr'],Outputs[i]['curstate'])
                if Outputs[i]['devicetype'] == 'pcf8574A':
                    clees_io.Set_pcf8574A_bit(Outputs[i]['devicenr'],Outputs[i]['pinnr'],Outputs[i]['curstate'])
                send_output_activated(i)    
            if msg == 'deactivate':
                if Outputs[i]['inverted'] == 1:
                    Outputs[i]['curstate'] = 1
                if Outputs[i]['inverted'] == 0:
                    Outputs[i]['curstate'] = 0
                if Outputs[i]['devicetype'] == 'pcf8574':
                    clees_io.Set_pcf8574_bit(Outputs[i]['devicenr'],Outputs[i]['pinnr'],Outputs[i]['curstate'])
                if Outputs[i]['devicetype'] == 'pcf8574A':
                    clees_io.Set_pcf8574A_bit(Outputs[i]['devicenr'],Outputs[i]['pinnr'],Outputs[i]['curstate'])
                send_output_deactivated(i)    
    return (0)





# ----------------------------------
#              Monitor
# ----------------------------------
def call_80Hz ():
    global cleesObjects
    global Turnouts
    global Buttons
    global signalpwmpowercounter
    global signalpwmpowerrampupflag
    global signalpwmpowerup
    global signalpwmpowerdown 

    # Call this rutin every loop
           
    # --- Process any Turnouts movement
    # Walk throug our Turnouts and keep move them into position
    for i in range (0,len(Turnouts)):
        if Turnouts[i]['action'] == 'C':
            if Turnouts[i]['curwid'] == Turnouts[i]['pwmwidthclosed']:
                 Turnouts[i]['action'] = ''  # action done or already in position
                 # adjust any slave outputs
                 if Turnouts[i]['slaveoutputid'] != '':
                     # This turnout have a slave output that also shall be set to reflect turnout pos
                     set_outputobject(Turnouts[i]['slaveoutputid'],'deactivate')
                     x = outputid_to_outputindex(Turnouts[i]['slaveoutputid'])
                     if x > -1:
                         send_output_deactivated(x)
                 # Send closed
                 send_turnout_closed(i)
            elif Turnouts[i]['pwmwidthclosed'] < Turnouts[i]['pwmwidththrown']: # normaly case
                Turnouts[i]['curwid'] -= cleesObjects['speedsteps']
                if Turnouts[i]['curwid'] < Turnouts[i]['pwmwidthclosed']:
                    Turnouts[i]['curwid'] = Turnouts[i]['pwmwidthclosed']
                clees_io.Set_pca9685(Turnouts[i]['devicenr'],Turnouts[i]['pwmnr'],Turnouts[i]['curwid'])                    
            elif Turnouts[i]['pwmwidthclosed'] > Turnouts[i]['pwmwidththrown']: # inverted case
                Turnouts[i]['curwid'] += cleesObjects['speedsteps']
                if Turnouts[i]['curwid'] > Turnouts[i]['pwmwidthclosed']:
                    Turnouts[i]['curwid'] = Turnouts[i]['pwmwidthclosed']
                clees_io.Set_pca9685(Turnouts[i]['devicenr'],Turnouts[i]['pwmnr'],Turnouts[i]['curwid'])                    
            else :
                Turnouts[i]['action'] = '' # when closedwith = thrownwidth the turnout is disabled
        elif Turnouts[i]['action'] == 'T':
            if Turnouts[i]['curwid'] == Turnouts[i]['pwmwidththrown']:
                 Turnouts[i]['action'] = ''  # action done or already in position
                 # adjust any slave outputs
                 if Turnouts[i]['slaveoutputid'] != '':
                     # This turnout have a slave output that also shall be set to reflect turnout pos
                     set_outputobject(Turnouts[i]['slaveoutputid'],'activate')
                     x = outputid_to_outputindex(Turnouts[i]['slaveoutputid'])
                     if x > -1:
                         send_output_activated(x)
                 # Send thrown
                 send_turnout_thrown(i)
            elif Turnouts[i]['pwmwidthclosed'] < Turnouts[i]['pwmwidththrown']: # normaly case
                Turnouts[i]['curwid'] += cleesObjects['speedsteps']
                if Turnouts[i]['curwid'] > Turnouts[i]['pwmwidththrown']:
                    Turnouts[i]['curwid'] = Turnouts[i]['pwmwidththrown']
                clees_io.Set_pca9685(Turnouts[i]['devicenr'],Turnouts[i]['pwmnr'],Turnouts[i]['curwid'])                    
            elif Turnouts[i]['pwmwidthclosed'] > Turnouts[i]['pwmwidththrown']: # inverted case
                Turnouts[i]['curwid'] -= cleesObjects['speedsteps']
                if Turnouts[i]['curwid'] < Turnouts[i]['pwmwidththrown']:
                    Turnouts[i]['curwid'] = Turnouts[i]['pwmwidththrown']
                clees_io.Set_pca9685(Turnouts[i]['devicenr'],Turnouts[i]['pwmnr'],Turnouts[i]['curwid'])                    
            else :
                Turnouts[i]['action'] = '' # this case means the turnout is disabled
        else:    
            Turnouts[i]['action'] = '' # Unknow action, just skip this


    # --- Process any button pressed 
    # Walk throug our pushbuttons and see if any of them have been activated
    # When activated, we send a "report" mqtt msg
    for i in range (0,len(Buttons)):
        if read_button(i) > 0 :
            # button is activated
            if (Buttons[i]['curstate'] != 1):
                # Button have just been pressed, do send a report
                send_button_activated(i)
                # and save the state 
                Buttons[i]['curstate'] = 1
        else :
            # button is not activated
            if (Buttons[i]['curstate'] != 0):
                # Button have just been released, do send a report
                send_button_deactivated(i)
                # and save the state 
                Buttons[i]['curstate'] = 0
           
    return (0)

