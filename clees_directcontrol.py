# ----------------------------------
#             CLEES DirectControl
# Author : Tompa
# ----------------------------------


# --- General libs
import json


# --- Private Libs
import clees_mqtt


# VAR ---
Dircntl = []
Repmsg = []


def init():
    global Dircntl
    global Repmsg
    with open('clees_directcontrol.json') as f:
        Dircntl = json.load(f)
        Repmsg = Dircntl['reportmessages']
        # loop throgh all dircntls and add pretxt
        pretxt = clees_mqtt.getpretopic()
        for i in range (0,len(Repmsg)):
            Repmsg[i]['listenfor'] = pretxt +'/'+ Repmsg[i]['listenfor'] 
            Repmsg[i]['sendto'] = pretxt +'/'+ Repmsg[i]['sendto']
            

def process(topic,msg):
    global Repmsg
    for i in range (0,len(Repmsg)):
        if Repmsg[i]['listenfor'] == topic:
            if Repmsg[i]['whenmsg'] == msg:
                clees_mqtt.publish(Repmsg[i]['sendto'],Repmsg[i]['withmsg'])
                
            
