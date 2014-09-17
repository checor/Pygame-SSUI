#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  config.py
#  
#  Copyright 2014 Sergio I. Urbina <checor@gmail.com>
#  

import ConfigParser
import os

def get_config(filename):
    conf = ConfigParser.ConfigParser()
    filepath = os.path.join('config', filename)
    if os.path.exists(filepath):
        conf.read(filepath)
        return conf
    else:
        print "Advertencia: Falta archivo", filename, "en la carpeta config"
        return    

def get_value(config, dad, son):
    try:
        return config.get(dad, son)
    except:
        print "Avertencia: Congif no encontrada: ", son
        return "<No value>"

class ConfigReader:
    """Lee toda la info necesaria y la obtiene en un bonito string, 
    int o float dependiendo de que variable sea"""
    def __init__(self, filename):
        self.config = get_config(filename)
        self.filename = filename
        self.configs = {}
        self.dicc = {}
    def search(self, filename, dad, son):
        key_string = filename + "_" + dad + "_" + son
        if self.dicc.has_key(key_string):
            return dicc[key_string]
        else:
            if not self.configs.has_key(filename):
                config[filename] = get_config(filename)
                self.dicc[key_string] = get_value(config, dad, son)
            else:
                self.dicc[key_string] = get_value(self.configs[filename],
                dad, son)


def main():
    #print "Este programa no corre solo. Arranque el archivo main"
    c = ConfigReader('info.ini')
    print c.operador()
    return 0

if __name__ == '__main__':
    main()

