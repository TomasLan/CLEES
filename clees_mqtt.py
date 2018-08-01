# ----------------------------------
#             CLEES MQTT
# Author : Tompa
# ----------------------------------


# ------------------ General libs --------------
import paho.mqtt.client as mqtt

# ------------------ Private Libs --------------
import clees_settings
import clees_log
import clees_objects
import clees_directcontrol


mqttc = object
online = 0

def on_connect(mqttc, obj, flags, rc):
    global online
    if rc == 0:
        clees_log.logmqtt("  MQTT Connected to broker")
        online = 1
        generalfilter = getpretopic() + "/#"
        mqttc.subscribe(generalfilter, 0)
        # send status
        clees_objects.report_buttons()
        clees_objects.report_turnouts()
        clees_objects.report_outputs()
    if rc == 1:
        clees_log.logmqtt("  MQTT FAILED connect, incorrect protocol version")
    if rc == 2:
        clees_log.logmqtt("  MQTT FAILED connect, invalid client identifier")
    if rc == 3:
        clees_log.logmqtt("  MQTT FAILED connect, server unavailable")
    if rc == 4:
        clees_log.logmqtt("  MQTT FAILED connect, bad username or password")
    if rc == 5:
        clees_log.logmqtt("  MQTT FAILED connect, not authorised")
    if rc > 5:
        clees_log.logmqtt("  MQTT FAILED connect, error#"+str(rc))


def on_disconnect(mqttc, obj, rc):
    global online
    online = 0
    if rc == mqtt.MQTT_ERR_SUCCESS:
        clees_log.logmqtt("  MQTT Disconnected gracefully from broker")
    else:
        clees_log.logmqtt("  MQTT Disconnected unexpectedly from broker with code: "+str(rc))


def on_message(mqttc, obj, msg):
    clees_log.logmqtt("  MQTTmsg -* [QoS="+str(msg.qos)+"] topic="+str(msg.topic) +" msg="+str(msg.payload))


# --- cmd to turnout
def on_message_cmd_t(mqttc, obj, msg):
    clees_log.logmqtt("  MQTTmsg -t [QoS="+str(msg.qos)+"] topic="+str(msg.topic) +" msg="+str(msg.payload))
    clees_objects.process_mqtt_cmd_t(str(msg.topic),str(msg.payload))


# --- cmd to signal
def on_message_cmd_s(mqttc, obj, msg):
    clees_log.logmqtt("  MQTTmsg -s [QoS="+str(msg.qos)+"] topic="+str(msg.topic) +" msg="+str(msg.payload))
    # to be implemeted


# --- cmd to Output
def on_message_cmd_o(mqttc, obj, msg):
    clees_log.logmqtt("  MQTTmsg -o [QoS="+str(msg.qos)+"] topic="+str(msg.topic) +" msg="+str(msg.payload))
    clees_objects.process_mqtt_cmd_o(str(msg.topic),str(msg.payload))


def on_message_rep(mqttc, obj, msg):
    clees_log.logmqtt("  MQTTmsg [QoS="+str(msg.qos)+"] topic="+str(msg.topic) +" msg="+str(msg.payload))
    clees_directcontrol.process(str(msg.topic),str(msg.payload))


def on_publish(mqttc, obj, mid):
    clees_log.logmqtt("  MQTT #"+ str(mid) +" Publish successfully")
    


def on_subscribe(mqttc, obj, mid, granted_qos):
    clees_log.logmqtt("  MQTT #"+ str(mid) +" Subscribe successfully with [Qos="+str(granted_qos)+"]")


#def on_log(mqttc, obj, level, string):
#    print(string)


def publish(topic, msg):
    (result,mid)=mqttc.publish(topic,msg,clees_settings.get('mqtt-qos'))
    if result == mqtt.MQTT_ERR_NO_CONN:
        clees_log.logwarning('  MQTT: No broker connection. Msg was lost.')
    if result == mqtt.MQTT_ERR_QUEUE_SIZE:
        clees_log.logwarning('  MQTT: Msg que full. Msg was lost.')
    return (result)


def getpretopic():
    txt = "clees/"+clees_settings.get('stationshortname')
    txt = txt.lower()
    return(txt)
        
def gettopicstr(msgtype,objecttype,objectid):
    txt = getpretopic() + "/"+msgtype+"/"+objecttype+"/"+objectid
    txt = txt.lower()
    return (txt)

def getonline():
    global online
    return(online)
    

# -------------------- init ------------------------
def init():
    global mqttc 
    mqttc = mqtt.Client()
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    mqttc.on_disconnect = on_disconnect
    ipadr = clees_settings.get('mqtt-broker-ipadress')
    port  = clees_settings.get('mqtt-broker-port')
    keep  = clees_settings.get('mqtt-broker-keep-alive')
    mqttc.connect_async(ipadr,port,keep)
    # add special callbacks for subscription services
    cmd_t_filter  = getpretopic() + "/cmd/t/#"
    cmd_s_filter  = getpretopic() + "/cmd/s/#"
    cmd_o_filter  = getpretopic() + "/cmd/o/#"
    repfilter     = getpretopic() + "/rep/#"
    mqttc.message_callback_add(cmd_t_filter,on_message_cmd_t)
    mqttc.message_callback_add(cmd_s_filter,on_message_cmd_s)
    mqttc.message_callback_add(cmd_o_filter,on_message_cmd_o)
    mqttc.message_callback_add(repfilter,on_message_rep)
    return(0)


# ------------------ start --------------------------
def start():
    global mqttc
    mqttc.loop_start() 
    return(0)


# ----------------- stopanddisconnect ---------------
def stopanddisconnect():
    global mqttc 
    mqttc.loop_stop()
    clees_log.logmqtt("  MQTT Disconnecting from broker...")
    mqttc.disconnect()
    return(0)

