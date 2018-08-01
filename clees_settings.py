# ----------------------------------
#             CLEES Settings
# Author : Tompa
# ----------------------------------

import json

Settings = []

def load():
    global Settings
    with open('clees_settings.json') as f:
        Settings = json.load(f)

def get(settingsname):
    global Settings
    return (Settings[settingsname])


