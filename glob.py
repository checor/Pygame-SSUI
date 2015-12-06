"""Variables globales que se intercambian entre los diferentes .py"""

import Queue, pickle

def pickle_save():
    a = ["hertz", "time" ,"period", "wave"]
    b= {}
    for i in a:
        b[i] = get_variable(i)
    pickle.dump(b, open("settings.txt", "wb"))

def set_variable(name, val = None):
    print "Added %s " % name
    dicc[name] = val
    dicc_changes[name] = True

def get_variable(name):
    if name in dicc:
        return dicc[name]
    else:
        return 0
        
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
            dicc_changes[name] = False
            return True
        else:
            return False
    return None

q = Queue.Queue()  #Hasta el momento no se ha utilizado

dicc = {}
dicc_changes = {}
