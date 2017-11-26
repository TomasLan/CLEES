# ----------------------------------
#             MSS MTLO Module
# Model Train Layout Objects
# By  : Tompa
# date: 2017-11-26
# ----------------------------------




# --- Defining Model Train objects
# Turnouts 
Turnout = [{
            'id': '823',             # String that identifies the turnout and is use to controll the turnout
            'homeposition': 'C',     # Position (C or T) that is the most common postion
            'device': 'pca9685',     # Name/Type of device that controls the turnout 
            'pwmmodule': 0,          # Module number 0..31. You may connect several pca9685 modules to the Pi
            'pwmnr': 0,              # Pwm index 0..15. Every module have 16 interna pwms
            'pwmwidthclosed': 200,   # Adjust this number to finetune the turnout toung position in its closed state
            'pwmwidththrown': 450,   # Adjust this number to finetune the turnout toung position in its thrown state
            # --- VAR ---
            'command': '',           # Variable used internaly
            'currentpwmwidth': -1    # Variable used internaly
            },{
            'id': '824',             # String that identifies the turnout and is use to controll the turnout
            'homeposition': 'T',     # Position (C or T) that is the most common postion
            'device': 'pca9685',     # Name/Type of device that controls the turnout 
            'pwmmodule': 0,          # Module number 0..31. You may connect several pca9685 modules to the Pi
            'pwmnr': 1,              # Pwm index 0..15. Every module have 16 internal pwms
            'pwmwidthclosed': 200,   # Adjust this number to finetune the turnout toung position in its closed state
            'pwmwidththrown': 465,   # Adjust this number to finetune the turnout toung position in its thrown state
            # --- VAR ---
            'command': '',           # Variable used internaly
            'currentpwmwidth': -1    # Variable used internaly
            }
           ]
SpeedSteps = 1  # pwm width amount change per 80Hz loops.  Must be 1 or higher. Higher means higher speed



# --- Private Libs
import mss_iomodule


def turnout_close (turnoutnr):
    Turnout[turnoutnr]['command'] = 'C'
    return (0)

def turnout_throw (turnoutnr):
    Turnout[turnoutnr]['command'] = 'T'
    return (0)





def init():
    for i in range (0,len(Turnout)):
        if Turnout[i]['homeposition'] == 'T':
            init_width = Turnout[i]['pwmwidththrown']
        else:
            init_width = Turnout[i]['pwmwidthclosed']
        mss_iomodule.Set_pca9685(Turnout[i]['pwmmodule'],Turnout[i]['pwmnr'],init_width)
        Turnout[i]['currentpwmwidth'] = init_width
    return(0) 


# ----------------------------------
#              Monitor
# ----------------------------------
def call_80Hz ():
    # Call this rutin every loop

    # --- Process any Turnouts movement
    # Walk throug our Turnouts and keep move them into position
    for i in range (0,len(Turnout)):
        if Turnout[i]['command'] == 'C':
            if Turnout[i]['currentpwmwidth'] == Turnout[i]['pwmwidthclosed']:
                 Turnout[i]['command'] = ''  # Command done or already in position
            elif Turnout[i]['pwmwidthclosed'] < Turnout[i]['pwmwidththrown']: # normaly case
                Turnout[i]['currentpwmwidth'] -= SpeedSteps
                if Turnout[i]['currentpwmwidth'] < Turnout[i]['pwmwidthclosed']:
                    Turnout[i]['currentpwmwidth'] = Turnout[i]['pwmwidthclosed']
                mss_iomodule.Set_pca9685(Turnout[i]['pwmmodule'],Turnout[i]['pwmnr'],Turnout[i]['currentpwmwidth'])                    
            elif Turnout[i]['pwmwidthclosed'] > Turnout[i]['pwmwidththrown']: # inverted case
                Turnout[i]['currentpwmwidth'] += SpeedSteps
                if Turnout[i]['currentpwmwidth'] > Turnout[i]['pwmwidthclosed']:
                    Turnout[i]['currentpwmwidth'] = Turnout[i]['pwmwidthclosed']
                mss_iomodule.Set_pca9685(Turnout[i]['pwmmodule'],Turnout[i]['pwmnr'],Turnout[i]['currentpwmwidth'])                    
            else :
                Turnout[i]['command'] = '' # this case means the turnout is disabled
        elif Turnout[i]['command'] == 'T':
            if Turnout[i]['currentpwmwidth'] == Turnout[i]['pwmwidththrown']:
                 Turnout[i]['command'] = ''  # Command done or already in position
            elif Turnout[i]['pwmwidthclosed'] < Turnout[i]['pwmwidththrown']: # normaly case
                Turnout[i]['currentpwmwidth'] += SpeedSteps
                if Turnout[i]['currentpwmwidth'] > Turnout[i]['pwmwidththrown']:
                    Turnout[i]['currentpwmwidth'] = Turnout[i]['pwmwidththrown']
                mss_iomodule.Set_pca9685(Turnout[i]['pwmmodule'],Turnout[i]['pwmnr'],Turnout[i]['currentpwmwidth'])                    
            elif Turnout[i]['pwmwidthclosed'] > Turnout[i]['pwmwidththrown']: # inverted case
                Turnout[i]['currentpwmwidth'] -= SpeedSteps
                if Turnout[i]['currentpwmwidth'] < Turnout[i]['pwmwidththrown']:
                    Turnout[i]['currentpwmwidth'] = Turnout[i]['pwmwidththrown']
                mss_iomodule.Set_pca9685(Turnout[i]['pwmmodule'],Turnout[i]['pwmnr'],Turnout[i]['currentpwmwidth'])                    
            else :
                Turnout[i]['command'] = '' # this case means the turnout is disabled
        else:    
            Turnout[i]['command'] = '' # Unknow command, just skip this
    return (0)

