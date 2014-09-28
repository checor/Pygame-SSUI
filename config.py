#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  config.py
#  
#  Copyright 2014 Sergio I. Urbina <checor@gmail.com>
#  

import ConfigParser
import os

class ConfigReader:
    """Lee toda la info necesaria y la obtiene en un bonito string, 
    int o float dependiendo de que variable sea. Usa archivos .ini
    
    filename: Nombre del arhivo en la carpera config, de la cual se
              obtendra la config
              
    dad: Categoría padre, [Ejemplo]
    
    son: Atributo el cual se desea, Ej = Valor"""
    
    def __init__(self):
        self.configs = {}
        self.dicc = {}    
    def get_config(self,filename):
        conf = ConfigParser.ConfigParser()
        filepath = os.path.join('config', filename)
        if os.path.exists(filepath):
            conf.read(filepath)
            return conf
        else:
            print "Advertencia: Falta archivo", filename, "en la carpeta config"
            return
    def get_value(self,config, dad, son):
        try:
            return config.get(dad, son)
        except:
            print "Avertencia: Config no encontrada: ", son
            return "<No value>"
    def search(self, filename, dad, son):
        key_string = filename + "_" + dad + "_" + son
        if self.dicc.has_key(key_string):
            return self.dicc[key_string]
        else:
            if not self.configs.has_key(filename):
                self.configs[filename] = self.get_config(filename)
                self.dicc[key_string] = self.get_value(self.configs[filename],
                dad, son)
            else:
                self.dicc[key_string] = self.get_value(self.configs[filename],
                dad, son)
            return self.dicc[key_string]

#class CsvReader:

def main():
    #print "Este programa no corre solo. Arranque el archivo main"
    c = ConfigReader()
    print c.search('info.ini','Empresa', 'Tel')
    return 0

if __name__ == '__main__':
    main()
