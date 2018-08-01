#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----- CLEES Model Train Section Server -------
# Author : Tompa
# 
# Works on both RPi and OPi
#
VERS = "0.6.0"    # 2018-07-31  MQTT first version
                  #   + MQTT
                  #   + JSON setup files
                  #   - HTTP GET commands
                  # Supportar
                  #   Turnouts (Växlar)
                  #   Buttons (Knappar)
                  #   Outputs (Utgångar, tex att driva LEDar)
                  #   Direktstyrning. (control turnouts using buttons)
                  #   Reconnect and broker connection status via LED, both pgio and clees object
                  #   Report outputs/turnouts/buttons upon startup and reconnect
                  #   Relä output till växlar för växelkorspolarisering
                  #   Settings for IPadress/port/keepalivetime for MQTT broker
                  #   Settings for logginfo
                  
                  # -- TODO for next release --
                  # not yet set


                  # -- TODO for upcomming releases
                  # Använda Pi:ens GPIO för in/out (io supporterar det med inte clees Objects)
                  # Lock/Unlock
                  # Route
                  # Signal
                  # spårledning
                  # HT16K33 stöd
                  # Flytta IO inställningarna i JSON fil
                  # Auto IPadress for MQTT broker
                  # Report latency
                  # Turnout time separations during runtime as during startup 
# ----------------------------------------------



# ------------------ General libs --------------
import time


# ------------------ Private Libs --------------
import clees_settings
import clees_io
import clees_objects
import clees_log
import clees_misc
import clees_mqtt
import clees_directcontrol




# --------------------------------------------------------------
#                              INIT
# --------------------------------------------------------------

# --- Start loggning
clees_log.logtxt ("Starting CLEES Ver:%s" %(VERS))

# --- Load settings
clees_settings.load()
clees_log.logtxt ("Settings loaded for %s [%s]" %(clees_settings.get('stationfullname'), clees_settings.get('stationshortname')))

# --- Init log
clees_log.init()

# --- Init HW
ErrTxt = clees_io.IO_init()
if ErrTxt != "" :
    clees_log.logerror (ErrTxt)

# --- Init MQTT
try:
    clees_mqtt.init()
except Exception as ex:
    clees_log.logerror("Fail to initialize MQTT' -> "+ repr(ex))

# --- Init Objects
try:
    clees_objects.init()
except Exception as ex:
    clees_log.logerror("Fail to load and initialize clees objects -> "+ repr(ex))
    
# --- Init DirectControl
try:
    clees_directcontrol.init()
except Exception as ex:
    clees_log.logerror("Fail to initialize DirectControl' -> "+ repr(ex))

# --- Misc Init
try:
    clees_misc.init()
except Exception as ex:
    clees_log.logerror("Fail to initialize Misc' -> "+ repr(ex))
statusledblinkcounter = 0
    

# --------------------------------------------------------------
#                              MAIN
# --------------------------------------------------------------

try:
    # Start mqtt thread
    clees_mqtt.start()
    clees_log.logtxt ("CLEES Server started")
    while (1):
        # This while loop will run at 80Hz   
        time.sleep(0.0125)
        statusledblinkcounter = statusledblinkcounter + 1
        if statusledblinkcounter > 80:
            statusledblinkcounter = 0
        # infact 80Hz it not importat any more as long we dont pwm control
        # swedich singal blink and that turned out not so fruitfull

        # process IO inputs
        try:
          clees_io.call_80Hz()
        except Exception as ex:
            clees_log.logerror("Monitor failed to process clees io -> "+ repr(ex))
        # process objects
        try:
          clees_objects.call_80Hz()
        except Exception as ex:
            clees_log.logerror("Monitor failed to process clees objects -> "+ repr(ex))

        # Check if we are online
        if clees_mqtt.getonline() == 1:
            clees_misc.set_statusled() 
        else:
            if statusledblinkcounter > 40:
                clees_misc.set_statusled()
            else:
                clees_misc.clr_statusled()


except KeyboardInterrupt:
    clees_log.termprint ("\nCtrl-C pressed")

clees_mqtt.stopanddisconnect()
clees_io.Set_GPIO(22,0)
clees_io.Close_GPIO()
time.sleep(0.5)
clees_log.logtxt ("CLEES Server stopped gracefully")

