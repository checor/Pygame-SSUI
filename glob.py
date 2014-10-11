"""Variables globales que se intercambian entre los diferentes .py"""

import Queue

def set_variable(name, val = None):
    dicc[name] = val

def get_variable(name):
    if name in dicc:
        return dicc[name]
    else:
        return None
        
def change_variable(name, val):
    if name in dicc:
        dicc[name] = val
        dicc_changes[name] = True 

def var_sum(name, val):
    if name in dicc:
        dicc[name] += val     
        dicc_changes[name] = True    

def var_changed(name):
    if name in dicc:
        if dicc_changes[name] == True:
            print name, "changed"
            dicc_changes[name] = False
            return True
        else:
            return False
    return None

q = Queue.Queue()  #Hasta el momento no se ha utilizado

dicc = {}
dicc_changes = {}
