# -*- coding: utf-8 -*-
"""
Created on Thu Jul 10 19:24:52 2014

@author: checor@gmail.com

Mejorar la documentacion
"""

import pygame, sys, re
from pygame.locals import *
import xml.etree.ElementTree as ET
import os
import yaml

import glob
import wavves

pi = False

#Parche feo, eliminar lo mas pronto posible:
input_on = False
num_changed = False

if os.uname()[4].startswith("arm"):
    print "Corremos en Raspberry Pi!"
    pi = True
    import GPIO

# Variables para Pygame
#modificar dependiendo de la pantalla a utilizar
size = width, height = 320, 240  # Elegimos el tamano de la pantalla
surface = pygame.display.set_mode(size,FULLSCREEN,24 )  # Pantalla completa a futuro
pygame.display.set_caption("Piezo")  # Nombre de la ventana
fps = 30  # Frames a los cuales se va a trabajar

#Colores de guia de Firefox OS
#Checar los colores, ya que se repite uno[]
colores = {"Blue": (0, 170, 204), "Orange": (255, 78, 0), "Brick":
           (205, 103, 35), "Red": (185, 0, 0), "Green": (95, 155, 10),
           "Black": (0, 0, 0), "Warm grey": (51, 51, 51), "Grey":
           (44, 57, 59), "Light grey": (244, 244, 244), "Ivory":
           (234, 234, 231), "White": (255, 255, 255)}

#Variables globales
pantallas = {}


class Pantalla(object):
    """Crea un objeto para la pantalla. Lleva como hijos los cuadros que
    necesita y los dibujara con sus valores

    nombre: identificador de la pantalla en el diccionario. No se debe repetir,
            se recomienda utilizar el nombre del archivo XML cargado.

    color: color de fondo de la pantalla. Al parecer no esta bien implementado.

    """
    pCount = 0
    pCurrent = None

    def __init__(self, nombre, col):
        self.nombre = nombre
        self.color = colores[col]
        #Elementos que se manejan
        self.hijos = []  # Chance toque cambiar esto a futuro
        self.botones = {}
        self.has_ss = False  # No tiene screensaver
        self.screensavers = {}
        self.popup_state = False
        self.popup = None
        self.inputs = {} #Kill me plz
        self.has_inputs = False
        #Variables de comportamiento
        self.handler = input_handler(self.nombre)
        Pantalla.pCount += 1
        self.dirty_rects = []
        self.state = False
        self.secs_elapsed = 0
        
        if Pantalla.pCurrent is None:
            Pantalla.pCurrent = self.nombre
    
    def adopt(self, hijo):
        """'Adopta' un objeto el cual se va a mostrar en la pantalla, como un
        cuadro o un boton. Estos seran mostrados en pantalla al utlizar awaken

        hijo: El objeto el cual se va a integrar a a la pantalla.
        """
        if type(hijo) is Cuadro:
            self.hijos.append(hijo)
        elif type(hijo) is Boton:
            if len(self.botones) == 0:
                hijo.set_s(True)
            else:
                hijo.set_s(False)
            self.botones[hijo.name] = hijo
            self.handler.add_button(hijo.name, *hijo.nav_xy)
        elif type(hijo) is Screensaver:
            self.has_ss = True
            self.screensavers[hijo.name] = hijo
        elif type(hijo) is Input:
            self.has_inputs = True
            self.inputs[hijo.name] = hijo
            print "Input %s cargado en pantalla" % hijo.name
        else:
            print "Advertencia: hijo no reconocido:", type(hijo)

    def awaken(self):
        """Muestra este objeto en la pantalla. Antes de mostrarlo, la pantalla
        anterior debe encargarse de limpiar la surface con self.sleep()

        bg_color: Color a utilizar de fondo. Opcional. No implementado.
        """
        Pantalla.pCurrent = self.nombre
        self.state = True
        for child in self.hijos:
            child.draw()
        for boton in self.botones:
            self.botones[boton].draw()
        for s in self.screensavers.itervalues():
            s.draw()
        for s in self.inputs:
            self.inputs[s].draw()
        pygame.display.update()

    def sleep(self, bg_color='Ivory'):
        """Oculta la pantalla de la surface, dejando el surface listo para
        mostar otra isntancia de pantalla.

        bg_color: Color con el cual limpiara la pantalla. Opcional.
        """
        surface.fill(colores[bg_color])
        surface.set_alpha(255)
        pygame.display.update()
        self.state = False

    def popup_toggle(self):
        """Aun no implementado.
        Se planea que muestre un popup, dandole control de la pantalla y el teclado.
        """
        self.popup_state = True

    def key(self, tecla):
        """Obtiene el valor de pulsación de tecla de PyGame, y realiza la accion
        correspondiente dependiendo de los botones que se encuentren en la pantalla.
        Tira error en print si se pulsa una tecla no asiganada.
        """
        if self.popup_state:
            self.popup.get_key(tecla)
        else:
            self.handler.move(tecla)

    def update(self):
        """Actualiza el contenido que se encuentra en pantalla. Por el momento,
        sólo se encarga de cuadros con texto que contenga variables y botones.
        """
        global num_changed
        if self.state:
            for child in self.hijos:
                child.redraw_text()
        if len(self.dirty_rects) > 0:
            pygame.display.update(self.dirty_rects)
        self.dirty_rects = []
        if self.has_inputs:
            for i in self.inputs:
                self.inputs[i].redraw_text()
            if num_changed:
                self.awaken()
                num_changed = False


    def rect_add(self, rect):
        """Añade un rectangulo el cual se va a actualizar al cambio de
        cuadro, mediante update()
        
        Argumentos:
            -rect: area donde se encuentra la variable
        """
        self.dirty_rects.append(rect)

    def sec(self):
        """Se llama cada segundo, para saber si se necesita cambiar un
        screensaver"""
        if self.screensavers == {}:
            return
        else:
            self.secs_elapsed += 1
            print self.secs_elapsed
            for e in self.screensavers.itervalues():
                if self.secs_elapsed % e.get_sec() == 0:
                    print "Pene"
                    e.next_pic()

    def has_screensaver(self):
        """Dice si tiene screensavers"""
        return self.has_ss
        
    def send_to_input(self, ch):
        if self.has_inputs:
            for i in self.inputs:
                self.inputs[i].enter(ch)



class Cuadro(object):
    """Lleva todos los atributos minimos necesarios para la utilizacion de un
    elemento en la pantalla. Acepta texto con o sin varaibles, e imágenes.

    nombre: identificador del cuadro. No debe repetirse.
    pos: posición en píxeles (x, y, alto, ancho)
    color: color de fondo del cuadro. Debe ser uno de los de guía, como por
           ejemplo, 'Ivory' o 'Blue' [Implementar mejor]
    rounded: Si se desea que el cuadro se muestre con las esquinas curveadas o
             no. Opcional, por defecto su valor es 0.
    """

    def __init__(self, nombre, col, pos=(0, 0, 0, 0), rounded=0):
        self.name = nombre
        self.pos = pos
        self.color = colores[col]
        self.rendered = False
        self.rounded = rounded
        self.textos = {}
        self.imagenes = []
        self.variables = {}
        self.rects = {}

    @staticmethod
    def load_font(font, size):
        if font == 'None':
            return pygame.font.SysFont(None, size)
        else:
            try:
                f = pygame.font.SysFont(font, size)
            except:
                print "Advertencia: Fuente ", font, " no encontrada"
                return pygame.font.SysFont(None, size)
            return f

    def get_text(self, string, tamano, fuente, col, **kwargs):
        """Obtiene tiene texto para mostrar.

        string: Texto a mostrar e identificador del mismo. No debe repetirse.
        tamano: Tamano del texto a mostrar. Por ejemplo, 12.
        fuente: Fuente a usar, si no se encuentra, se usa una por defecto.
        color: Color de texto. Debe estar en el diccionario.
        **kwargs: [No implementado.]
        
        pos aun no se encuentra implementado                        """
        self.textos[string] = (string, tamano, fuente, col, kwargs)

    def text_parser(self, string):
        """Toma un string el cual tenga texto, de esta forma:
        'Las aventuras de %s, el %s con pelos" % chicho nino'
        Y sustituye las variables para mostrarlas en pantalla.
        [Su implementación debe ser mejorar. Quitar TRY]
        """
        exp_re = re.compile("%[^ ]")
        split_re = re.compile("(?<=% )(.*)").search(string)
        var_re = re.compile("(\w+)")

        indicadores = exp_re.findall(string)  # %s , %s
        try:
            self.variables[string] = var_re.findall(split_re.groups()[0])
        except:
            return string
        for i, j in zip(indicadores, self.variables[string]):
            val = glob.get_variable(j)
            string = string.replace(i, str(val), 1)
        return re.findall("""["'](.*?)['"]""", string, re.DOTALL)[0]

    def check_changes(self, string):
        """Checa si existen cambios en las varaibles de los strings. De ser
        así, manda llamar a la pantalla activa para que haga el update
        """
        if string in self.variables:
            for elem in self.variables[string]:
                if glob.var_changed(elem):
                    pantallas[Pantalla.pCurrent]. \
                        rect_add(self.rects[string][1])
                    return True
        return False

    def text_render(self, target=None):
        """Se encarga de darle el formato adecuado al texto y su alineación
        Acepta cualquiera de las siguientes combinaciones:

        posx, poxy: Valores de pixeles en x, y, relativos al cuadro.
        posy, align: Valores de pixeles de y, y alineación en X
        line, align: Coloca al texto en la linea N respecto a su tamaño, así
                     su respectiva alineación en X.

        align -1 == Izquierda; 0 == Centro; 1 == Derecha
        [Target aun no implementado, pero funcional de todas maneras]
        """
        for elem in self.textos.itervalues():
            t = Cuadro.load_font(elem[2], elem[1])
            text = self.text_parser(elem[0])
            text_render = t.render(text, 1, (0, 0, 0))
            text_rect = text_render.get_rect()
            if 'posx' in elem[-1] and 'posy' in elem[-1]:  # elem[-1] = kwargs
                x = self.pos[0] + elem[-1]['posx']
                y = self.pos[1] + elem[-1]['posy']
                text_rect.topleft = (x, y)
            elif 'posy' in elem[-1] and 'align' in elem[-1]:
                if elem[-1]['align'] == -1:  # Izquierda
                    x = Rect(self.pos).left
                    y = self.pos[1] + elem[-1]['posy']
                    text_rect.topleft = (x, y)
                elif elem[-1]['align'] == 0:  # Centrado
                    x = Rect(self.pos).centerx
                    y = self.pos[1] + elem[-1]['posy']
                    text_rect.centerx = x
                    text_rect.top = y
                elif elem[-1]['align'] == 1:  # Derecho
                    x = Rect(self.pos).right
                    #y = text_rect.height * elem[-1]['align']
                    y = self.pos[1] + elem[-1]['posy']
                    text_rect.right = x
                    text_rect.top = y
                print "Fatal, mala alineacion", elem[-1]['align']
            elif 'line' in elem[-1] and 'align' in elem[-1]:
                if elem[-1]['align'] == -1:  # Izquierda
                    x = Rect(self.pos).left
                    text_rect.left = x
                elif elem[-1]['align'] == 0:  # Centrado
                    x = Rect(self.pos).centerx
                    text_rect.centerx = x
                elif elem[-1]['align'] == 1:  # Derecho
                    x = Rect(self.pos).right
                    text_rect.right = x
                else:
                    print "Fatal! No valor valido de alineacion",
                    elem[-1]['align']
                y = self.pos[1] + elem[-1]['line'] * text_rect.height
                text_rect.top = y
            else:
                print "Fatal! Texto mal alineado!!", elem[-1]
            self.rects[elem[0]] = (text_render, text_rect)
        self.rendered = True

    def draw_text(self, target=None, reparse=False):
        """Dibuja el texto en la pantalla. Se le puede indicar un
        target, esto es, el elemento el cual se debe de dibujar. Si no
        se indica, se redibuja todos.
        
        target: Indica si solo se dibujara de nuevo un elemento o todos.
                En caso de ser None, se dibuja todo.
                
        reparse: Si se indica True, se vuelve a renderizar el texto.
                 Este valor debe ser positivo para variables que hayan
                 sufrido de algún cambio.
        """
        if self.rendered == False or reparse == True:
            self.text_render()
        if target != None:
            textos = self.textos
        else:
            textos = self.textos
        for elem in textos.itervalues():
            surface.blit(*self.rects[elem[0]])

    def redraw_text(self):
        """Redibuja todo el texto si encuentra algún cambio en las variables
        monitoreadas."""
        for elem in self.textos.itervalues():
            if self.check_changes(elem[0]):
                pygame.draw.rect(surface, self.color,
                                 self.rects[elem[0]][1])
                self.draw_text(elem[0], True)

    def get_image(self, filename, posx=0, posy=0, folder='data'):
        """Recibe una imagen para ser mostrada en la pantalla.

        filename: Nombre del archivo, debe encontrarse en la carpeta data
        posx, posy = Ubicación de la imagen, relativa en pixeles.
        """
        fullname = os.path.join(folder, filename)
        try:
            image = pygame.image.load(fullname).convert_alpha()
        except pygame.error, message:
            print 'No se pudo cargar la imamen: ', fullname, message
        rect = image.get_rect()
        self.imagenes.append((image, rect, posx, posy))

    def roundrect(self, surface, rect, color, radius=0.4):
        """
        AAfilledRoundedRect(surface,rect,color,radius=0.4)

        surface : destination
        rect    : rectangle
        color   : rgb or rgba
        radius  : 0 <= radius <= 1
        """

        rect = Rect(rect)
        color = Color(*color)
        alpha = color.a
        color.a = 0
        pos = rect.topleft
        rect.topleft = 0, 0
        rectangle = pygame.Surface(rect.size, SRCALPHA)
        circle = pygame.Surface([min(rect.size) * 3] * 2, SRCALPHA)
        pygame.draw.ellipse(circle, (0, 0, 0), circle.get_rect(), 0)
        circle = pygame.transform.smoothscale(circle,
                                              [int(
                                                  min(rect.size) * radius)] * 2)
        radius = rectangle.blit(circle, (0, 0))
        radius.bottomright = rect.bottomright
        rectangle.blit(circle, radius)
        radius.topright = rect.topright
        rectangle.blit(circle, radius)
        radius.bottomleft = rect.bottomleft
        rectangle.blit(circle, radius)
        rectangle.fill((0, 0, 0), rect.inflate(-radius.w, 0))
        rectangle.fill((0, 0, 0), rect.inflate(0, -radius.h))
        rectangle.fill(color, special_flags=BLEND_RGBA_MAX)
        rectangle.fill((255, 255, 255, alpha), special_flags=BLEND_RGBA_MIN)
        return surface.blit(rectangle, pos)

    def draw_image(self, target=None):
        """Dibuja todas las imagenes cargadas."""
        if target is None:
            imagenes = self.imagenes
        else:
            imagenes = self.imagenes[target],
        for elem in imagenes:
            img_pos = Rect(self.pos[0], self.pos[1], self.pos[0] + elem[2],
                           self.pos[1] + elem[3])
            surface.blit(elem[0], img_pos)
            pantallas[Pantalla.pCurrent].rect_add(img_pos)
            #Cambiar esto por un verdadero update
            #pygame.display.flip()

    def draw(self):
        """Dibuja todo el cuadro en la surface"""
        if not self.rounded:
            pygame.draw.rect(surface, self.color, self.pos)
        else:
            self.roundrect(surface, self.pos, self.color)
        self.draw_text()
        if type(self) is not Screensaver:
            self.draw_image()
        else:
            self.draw_image(0)  # Solo dibujar la primer imagen


class Boton(Cuadro):
    """Crea un boton intereactivo en la pantalla. Puede tener diferentes
    acciones, dentro de el XML. Adicionalmente se le agrega texto e icon
    Se debe agregar a una clase pantalla, esta se encargara de activar
    y desactivar al engendro que tenemos por boton."""

    def set_values(self, in_color, nav_xy, action):
        self.ac_color = self.color
        self.in_color = colores[in_color]
        self.nav_xy = nav_xy
        self.action_string = action

    def do_action(self):
        """Herramienta que nos permite realizar acciones provenientes de un
        botón un menú, o cualquiero otro sistema. Obtiene un string,
        realiza la acción y devuelve el resultado de dicha acción"""
        action = self.action_string.split()[0]
        if action == 'OpenYAML':
            pantallas[Pantalla.pCurrent].sleep()
            name = self.action_string.split()[1] + '.yaml'
            if pantallas.has_key(name):
                pantallas[name].awaken()
            else:
                #try:
                load_yaml(name)
                #except Exception,e:
                #    print "Fatal: Imposible cargar pantalla", name
                #    print str(e)
                #    return
            pantallas[name].awaken()
        elif action == 'OpenPopup':
            pass
        elif action == 'Poweroff':
            print "Comienza secuencia de apagado iniciada por el usuario"
        elif action == "Wavves_start":
            wavves.start(glob.get_variable("wave"),glob.get_variable("freq"),
                glob.get_variable("gain"),glob.get_variable("time"))
        elif action == "Wavves_stop":
            wavves.stop()
        elif action == "set_wave":
            print self.action_string.split()[1]
            glob.set_variable("wave", self.action_string.split()[1])
            glob.pickle_save()
        elif action == "spwm_start":
            wavves.spwm_start(glob.get_variable("hertz"),glob.get_variable("period"),
                glob.get_variable("time"))
    def set_s(self, state):
        """Este estado se refiere a si se encuentra seleccionado o no. El
        cambio de estado cambia su color."""
        if state == True:
            self.color = self.ac_color
            self.state = False
        else:
            self.color = self.in_color
            self.state = True
        if pantallas[Pantalla.pCurrent].state == True:
            self.draw()
            pantallas[Pantalla.pCurrent].rect_add(self.pos)

class Input(Cuadro):
    """ALTAMENTE EXPERIMENTAL
    Cuadro de dialogo para  insertar texto
    """
    def __init__(self, *args):
	super(Input, self).__init__(*args)
        self.namevalue = ''
        self.value = 0
        
        
    def enter(self, char):
        global num_changed
        if char.isdigit():
            self.add(char)
            num_changed = True
        elif char == "*":
            self.delete()
        elif char == "#":
            #save data
            glob.pickle_save()
            pantallas[Pantalla.pCurrent].sleep()
            pantallas['piezo.yaml'].awaken()
    def set_input_vars(self, name):
        self.namevalue = name
        print name + "  ag tmr"
        self.value = int(glob.get_variable(name))
    
    def delete(self):
        if self.value < 10:
            self.value = 0
        else:
            self.value = int(str(self.value)[:-1])
        glob.change_variable(self.namevalue, self.value)
    
    def add(self, n):
        self.value = int(str(self.value) + str(n))
        glob.change_variable(self.namevalue, self.value)
        
class Matrix(object):
    """Matriz para el uso de botones y de menues, qque asigna posiciones
    de los objeteos y devuelve el objeto si se mueve hacia arriba, abajo
    izquierda, o derecha."""

    def __init__(self):
        self.m = [[]]
        self.position = [0, 0]

    def add_value(self, name, x, y):
        while x + 1 > len(self.m):
            self.m.append([])
        for i in xrange(len(self.m)):
            while len(self.m[i]) < y + 1:
                self.m[i].append([])
        self.m[x][y] = name

    def blank(self):
        if len(self.m[0]) == 0 and len(self.m) == 1:
            return True
        else:
            return False

    def print_matrix(self):
        for i in xrange(len(self.m)):
            print self.m[i]

    def get_value(self):
        try:
            return self.m[self.position[0]][self.position[1]]
        except:
            return None

    def move(self, direction):
        if direction == 'Up':
            if self.position[0] == 0:
                self.position[0] = len(self.m) - 1
            else:
                self.position[0] -= 1
        elif direction == 'Down':
            if self.position[0] == len(self.m) - 1:
                self.position[0] = 0
            else:
                self.position[0] += 1
        elif direction == 'Right':
            if len(self.m[self.position[0]]) - 1 == self.position[1]:
                self.position[1] = 0
            else:
                self.position[1] += 1
        elif direction == 'Left':
            if self.position[1] == 0:
                self.position[1] = len(self.m[self.position[0]]) - 1
            else:
                self.position[1] -= 1
        else:
            print "Warning: Movimiento no reconocido:", direction
        while self.get_value() == []:
            self.move(direction)
        return self.get_value()


#Mala implementacion! La pantalla debe hacerse cargo de sus propios botones
#y de sus propios elementos para dibujarse. De otro modo no se lograra usar
#clase en varias objetos que no sean Pantalla.


class input_handler(object):
    """Por el momento, esta clase solamente se encarga de tratar con
    los botones. Recibe las entradas directamente de Pygame, y hace
    los cambios necesario en la pantalla para reflejarlos en pantalla"""

    def __init__(self, pantalla_name):
        self.master = pantalla_name
        self.mapa = Matrix()
        self.active = True
        self.empty = True
        self.last_selected = None

    def add_button(self, name, x, y):
        """Obtiene los valores xy, de uno por uno. Se trata como si 
        fuera un array, el cual se usara para saber que elementos se
        tienen arriba, abajo, a la izquierda, o a la derecha"""
        self.mapa.add_value(name, x, y)
        self.empty = False
        self.last_selected = None

    def state(self, act=True):  # Que mierda es esto?
        self.active = act

    def move(self, mov):  # Tiene que ser un event.key
        #Cosas para el input
        if pantallas[Pantalla.pCurrent].has_inputs:
            print "Tenemos un input en este lado"
            try:
                if mov.startswith('k'):
                    num = mov[-1]
                    pantallas[Pantalla.pCurrent].send_to_input(num)
                return
            except:
                pass
        if not self.mapa.blank():
            last_selected = self.mapa.get_value()
        else:
            return
        if mov == K_UP or mov == 'k2':
            self.mapa.move("Up")
            button_name = self.mapa.get_value()
            pantallas[self.master].botones[last_selected].set_s(False)
            self.last_selected = button_name
            pantallas[self.master].botones[button_name].set_s(True)
        elif mov == K_DOWN or mov == 'k8':
            self.mapa.move("Down")
            button_name = self.mapa.get_value()
            pantallas[self.master].botones[last_selected].set_s(False)
            self.last_selected = button_name
            pantallas[self.master].botones[button_name].set_s(True)
        elif mov == K_LEFT or mov == 'k4':
            self.mapa.move("Left")
            button_name = self.mapa.get_value()
            pantallas[self.master].botones[last_selected].set_s(False)
            self.last_selected = button_name
            pantallas[self.master].botones[button_name].set_s(True)
        elif mov == K_RIGHT or mov == 'k6':
            self.mapa.move("Right")
            button_name = self.mapa.get_value()
            pantallas[self.master].botones[last_selected].set_s(False)
            self.last_selected = button_name
            pantallas[self.master].botones[button_name].set_s(True)
        elif mov == K_RETURN or mov == 'k5':
            button_name = self.mapa.get_value()
            pantallas[self.master].botones[button_name].do_action()
        #Pantalla matricial
        
        else:
            print "Tecla no reconocida:", mov
        pantallas[Pantalla.pCurrent].update()


class Popup(Cuadro):
    """Elemento el cual se coloca al frente de la pantalla, indicando algun
    error o adventencia. Se define un tiempo el cual va a estar activo, toma
    control del cualquier input en la pantalla, y tiene bonotes para aceptar
    o quitar la opcion. Este aparece siempre centrada en la patnalla
    """

    def __init__(self, nombre, color, tamano, tiempo=5):
        self.nombre = nombre
        self.color = color
        self.tamano = tamano
        self.tiempo = time
        self.botones = []
        self.textos = []
        self.imagenes = []
        cx = surface.get_rect().centerx
        cy = surface.get_rect().centery
        pos = (cx - tamano[0] / 2, cy - tamano[1] / 2, tamano[0], tamano[1])
        self.gotImage = False  #Parece que no se utiliza
        self.input_handler = input_handler()

    def add_button(self, button):
        self.botones[button.name] = button
        self.input_handler.add_button(button.name, *button.nav_xy)

    def get_key(self, key):
        if len(self.botones) == 0:
            return
        #elif pi == True and 
        else:
            self.input_handler.move(key)


class Screensaver(Cuadro):
    """Hace una dispositivas de imagenes las cuales haran update cuando
    se le sea indicado"""

    def __init__(self, *args):
        self.secs = 5
        self.cursor = 0
        self.img_num = 0
        super(Screensaver, self).__init__(*args)

    def get_image(self, *args):
        super(Screensaver, self).get_image(*args)
        self.img_num += 1

    def set_time(self, t=5):
        """Agrega el tiempo en segundos en el cual cambiara cada
        imagen o diasposotiva"""
        self.secs = t

    def get_sec(self):
        """Muestra los segundos sefl.secs"""
        return self.secs

    def next_pic(self):
        """Camvia la imagen la cual se va a mostrar en ese instante"""
        print 'Cambiemos de image', self.cursor, self.img_num
        if self.cursor == self.img_num - 1:
            self.cursor = 0
        else:
            self.cursor += 1
        self.draw_image(self.cursor)

    def load_folder(self, name, x=0, y=0):
        """
        Añade un folder completo de imágenes para ser mostradas
        Estas serán mostradas en 0,0
        """
        filelist = os.listdir(name)
        for e in filelist:
            if e.endswith('.png') or e.endswith('.jpg'):
                print "Imagen añadida"
                self.get_image(e, x, y, name)


class Screen(object):
    """Maneja por completo todo lo que se muestra en la pantalla,
    mediante el uso de pygame. No confundir con clase Pantalla."""

    def __init__(self):
        self.running = False

    @staticmethod  # Outdated
    def load_xml(filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        if root.tag == "Pantalla":
            p = Pantalla(filename, 'White')  # WAT
            pantallas[filename] = p
            for child in root.findall("Caja"):
                x = child.find('PosX')
                y = child.find('PosY')
                al = child.find('Alto')
                an = child.find('Ancho')
                posc = (int(x.text), int(y.text), int(an.text), int(al.text))
                col = child.find('Color').text
                col = colores[col]
                rounded = float(child.find('Redondez').text)
                c = Cuadro(str(child.attrib['Nombre']), col, posc,
                           rounded)
                for t in child.findall("Texto"):
                    ttext = t.find("Text").text
                    tsize = int(t.find("Tamano").text)
                    tfont = t.find("Fuente").text
                    tcolor = t.find("Color").text
                    tline = int(t.find("Linea").text)
                    talign = int(t.find("Alineacion").text)
                    c.get_text(ttext, tsize, tfont, tcolor, line=
                    tline, align=talign)
                for imag in child.findall("Imagen"):
                    imagen = imag.find("Filename").text
                    img_posx = int(imag.find("PosX").text)
                    img_posy = int(imag.find("PosY").text)
                    c.get_image(imagen, img_posx, img_posy)
                pantallas[filename].adopt(c)
            for child in root.findall("Boton"):
                x = child.find('PosX')
                y = child.find('PosY')
                al = child.find('Alto')
                an = child.find('Ancho')
                posc = (int(x.text), int(y.text), int(an.text), int(al.text))
                col = child.find('Color_activo').text
                col = colores[col]
                rounded = float(child.find('Redondez').text)
                b = Boton(str(child.attrib['Nombre']), col, posc, rounded)
                pantallas[filename].adopt(c)
                for t in child.findall("Texto"):
                    ttext = t.find("Text").text
                    tsize = int(t.find("Tamano").text)
                    tfont = t.find("Fuente").text
                    tcolor = t.find("Color").text
                    tline = int(t.find("Linea").text)
                    talign = int(t.find("Alineacion").text)
                    b.get_text(ttext, tsize, tfont, tcolor, line=
                    tline, align=talign)
                for imag in child.findall("Imagen"):
                    imagen = imag.find("Filename").text
                    img_posx = int(imag.find("PosX").text)
                    img_posy = int(imag.find("PosY").text)
                    b.get_image(imagen, img_posx, img_posy)
                color_in = child.find("Color_inactivo").text
                #Acciones especiales para el boton
                color_in = colores[color_in]
                action = child.find("Accion").text
                valx = int(child.find("ValX").text)
                valy = int(child.find("ValY").text)
                b.set_values(color_in, (valx, valy), action)
                pantallas[filename].adopt(b)
        else:
            print "XML inválido."

    @staticmethod
    def start(filename):
        pygame.init()
        pygame.font.init()
        clock = pygame.time.Clock()
        sec, sec_t = pygame.USEREVENT + 1, 1000  # Contador de segundos
        pygame.time.set_timer(sec, sec_t)
        surface.fill(colores['Ivory'])
        load_yaml(filename)
        pygame.display.update()
        running = True
        #Pantalla Matricial
        if pi == True:
            kp = GPIO.keypad()
            last_key = kp.getKey()
        while running:
            clock.tick(fps)
            if Pantalla.pCurrent is not None:
                pantallas[Pantalla.pCurrent].update()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    print 'Tecla'
                    if event.key == K_ESCAPE:
                        print "\nBye Bye"
                        pygame.quit()
                        running = False
                    elif event.key == K_q:
                        print "Press ESC to quit"
                    elif event.key == K_a:
                        pantallas[Pantalla.pCurrent].awaken()
                    elif event.key == K_s:
                        pantallas[Pantalla.pCurrent].sleep()
                    else:
                        pantallas[Pantalla.pCurrent].key(event.key)
                #Pantalla matricial
                if pi == True:
                    cur_key = kp.getKey()
                    if cur_key is not None and cur_key != last_key:
                        pantallas[Pantalla.pCurrent].key('k'+str(cur_key))
                        print "Presionado keypad"
                    last_key=cur_key
                #Fin pantalla    
                if event.type == sec:
                    pantallas[Pantalla.pCurrent].sec()

        return 0


def load_yaml(filename, folder='screens'):
    f = open(os.path.join(folder, filename), 'r')
    tree = yaml.load(f)
    if 'Pantalla' in tree:
        p = Pantalla(filename, 'White')
        pantallas[filename] = p
        if 'Caja' in tree['Pantalla']:
            for e in tree['Pantalla']['Caja']:
                nombre = e['_Nombre']
                alto = e['Alto']
                ancho = e['Ancho']
                col = e['Color']
                posx = e['PosX']
                posy = e['PosY']
                redo = e['Redondez']
                pos = (posx, posy, ancho, alto)
                c = Cuadro(nombre, col, pos, redo)
                if 'Texto' in e:
                    for t in e['Texto'],:
                        t_string = t['Text']
                        t_size = t['Tamano']
                        t_font = t['Fuente']
                        t_color = t['Color']
                        t_line = t['Linea']
                        t_align = t['Alineacion']
                        c.get_text(t_string, t_size, t_font, t_color,
                                   line=t_line, align=t_align)
                if 'Imagen' in e:
                    for i in e['Imagen'],:
                        i_file = i['Filename']
                        i_posx = i['PosX']
                        i_posy = i['PosY']
                        c.get_image(i_file, i_posx, i_posy)
                pantallas[filename].adopt(c)
        if 'Boton' in tree['Pantalla']:
            for e in tree['Pantalla']['Boton']:
                nombre = e['_Nombre']
                alto = e['Alto']
                ancho = e['Ancho']
                col = e['Color_activo']
                posx = e['PosX']
                posy = e['PosY']
                redo = e['Redondez']
                pos = (posx, posy, ancho, alto)
                b = Boton(nombre, col, pos, redo)
                if 'Texto' in e:
                    for t in e['Texto'],:
                        t_string = t['Text']
                        t_size = t['Tamano']
                        t_font = t['Fuente']
                        t_color = t['Color']
                        t_line = t['Linea']
                        t_align = t['Alineacion']
                        b.get_text(t_string, t_size, t_font, t_color,
                                   line=t_line, align=t_align)
                if 'Imagen' in e:
                    for i in e['Imagen'],:
                        i_file = i['Filename']
                        i_posx = i['PosX']
                        i_posy = i['PosY']
                        b.get_image(i_file, i_posx, i_posy)
                c_inac = e['Color_inactivo']
                action = e['Accion']
                valx = e['ValX']
                valy = e['ValY']
                b.set_values(c_inac, (valx, valy), action)
                pantallas[filename].adopt(b)
        if 'Screensaver' in tree['Pantalla']:
            for s in tree['Pantalla']['Screensaver']:
                pos = (s['PosX'], s['PosY'], s['Ancho'], s['Alto'])
                scr = Screensaver(s['_Nombre'], s['Color'], pos,
                                  s['Redondez'])
                if 'Folder' in s:
                    scr.load_folder(s['Folder'])
                pantallas[filename].adopt(scr)
        if 'Input' in tree['Pantalla']:
            for e in tree['Pantalla']['Input']:
                nombre = e['_Nombre']
                alto = e['Alto']
                ancho = e['Ancho']
                col = e['Color']
                posx = e['PosX']
                posy = e['PosY']
                redo = e['Redondez']
                in_var = e['Variable']
                pos = (posx, posy, ancho, alto)
                c = Input(nombre, col, pos, redo)
                print in_var
                c.set_input_vars(in_var)
                if 'Texto' in e:
                    for t in e['Texto'],:
                        t_string = t['Text'] #Texto inicial, debe ser numerico
                        t_size = t['Tamano']
                        t_font = t['Fuente']
                        t_color = t['Color']
                        t_line = t['Linea']
                        t_align = t['Alineacion']
                        c.get_text(t_string, t_size, t_font, t_color,
                                   line=t_line, align=t_align)
                if 'Imagen' in e:
                    for i in e['Imagen'],:
                        i_file = i['Filename']
                        i_posx = i['PosX']
                        i_posy = i['PosY']
                        c.get_image(i_file, i_posx, i_posy)
                pantallas[filename].adopt(c)
                
    else:
        print "YAML invalido!"


if __name__ == '__main__':
    print "Error: Esto modulo no es independiente. Corra Main."
