#-------------------------------------------------------------------------------
# Name:        PyMon_ConfigFile
# Purpose:     Object to save / read configuration parameter in json file
#
# Author:      Legros
#
# Created:     22/06/2021
# Copyright:   (c) Legros 2021
# License:     Private Property
#-------------------------------------------------------------------------------

import json

#-------------------------------------------------------------------------------
#
# Clash to share all common graphic feature between modules
#
#-------------------------------------------------------------------------------

class ConfigGraph():

    def __init__(self):
        # set default color
        self.WIN_FOREGROUND = "#EEE"
        self.WIN_HIGH_LIGHT ="#CCC"
        self.WIN_BACKGROUND = "#333"
        self.TRACE_BACKGROUND = "#AAA"
        self.CMD_BACKGROUND = "#EEE"

        self.LABEL_BACKGROUND = self.WIN_BACKGROUND
        self.LABEL_FOREGROUND = self.WIN_FOREGROUND
        self.ENTRY_COLOR     = self.CMD_BACKGROUND

        #defaut size for button
        self.BUTTON_DEF_WIDTH = 10

        #defaut size for entry zone
        self.ENTRY_DEF_WIDTH = 15



#-------------------------------------------------------------------------------
#
# Clash to save and reload config parameters (between 2 executions)
#
#-------------------------------------------------------------------------------

class ConfigFile():

    def __init__(self, ConfigFileName = "Ziot.json"):
        #save file name
        self.ConfigFileName = ConfigFileName

        #read config file
        try:
            with open(self.ConfigFileName, "r") as jsonfile:
                self.ConfData = json.load(jsonfile)
                jsonfile.close()
        except:
            #set default config value, before to try to read them
            self.ConfData={}
            self.save_Settings()


# to take (get) a parameter in config file.
# If it doesn't yet exist, it is created with # the given default value

    def take(self,section,item,default=None):
        Update_ConfData = False
        if section in self.ConfData:
            if item in self.ConfData[section]:
                # if the selected item exit, return it
                return self.ConfData[section][item]
            else:
                # if the selected item doesn't exit, set default and saved
                self.ConfData[section][item] = default
                Update_ConfData = True
        else:
            # if the section doesn't exit, create section, set default and saved
            self.ConfData[section]={}
            self.ConfData[section][item] = default
            Update_ConfData = True

        if Update_ConfData:
            self.save_Settings()

        return default


# to put (set) a parameter in config file.
# If it doesn't yet exist, it is created with # the given default value

    def put(self,section,item,value):
        if section in self.ConfData:
                self.ConfData[section][item] = value
        else:
            # if the selected item doesn't exit, set default and saved
            self.ConfData[section] = {}
            self.ConfData[section][item] = value

        self.save_Settings()


# private method to save ConfData in json file

    def save_Settings(self):
        MyJSON = json.dumps(self.ConfData, indent=4, sort_keys=True)
        with open(self.ConfigFileName, "w") as jsonfile:
            jsonfile.write(MyJSON)
            jsonfile.close()



# main is a unitary test (+ demonstration) features

def main():
    cf=ConfigFile()
    Nom=cf.take("Famille","Nom", "philippe")
    print("Nom =" + Nom)
    divers=cf.take("Famille","divers")
    if divers:
        print("divers =" + divers)
    else:
        print("divers = None")
    cf.put("Famille","Nom", "pauline")
    Nom=cf.take("Famille","Nom", "philippe")
    print("Nom =" + Nom)



if __name__ == '__main__':
    main()
