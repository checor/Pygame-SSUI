# -*- coding: utf-8 -*-
"""
Created on Thu Jul 10 19:24:52 2014

@author: checor@gmail.com

Pensar en la forma de hacer updates
"""

import pygame, sys, re
from pygame.locals import *
import xml.etree.ElementTree as ET
import os

import glob

"""
Variables para pygame
Estas seran movidas a un libreria mas adelante
"""
size = width, height = 320, 240  #Elegimos el tamaño de la pantalla
surface = pygame.display.set_mode((size),0,24)  #Pantalla completa a futuro
pygame.display.set_caption("Newtech Software")  #Nombre de la ventana

#Colores de guia de Firefox OS
#Checar los colores, ya que se repite uno[]
colores = {"Blue": (0, 170, 204) , "Orange": (255,78,0) , "Brick":
               (205,103,35), "Red":(185,0,0), "Green":(95,155,10),
               "Black" : (0,0,0) , "Warm grey" : (51,51,51) , "Warm grey" :
               (44,57,59) , "Light grey" : (244,244,244) , "Ivory" :
               (234,234,231) , "White" : (255,255,255) }

#Fuentes
def get_font(font, size):
    if font == 'None':
        return pygame.font.SysFont(None, size)
    else:
        try:
            f = pygame.font.SysFont(font, size)
        except:
            print "Advertencia: Fuente ", font, " no encontrada"
            return pygame.font.SysFont(None, size)
        return f
"""Fin de variables"""

def text_parser(string):
    #Ejemplo 
    #"""""Las aventuras de %s, el %s con pelos" % chicho nino"""
    exp_re = re.compile("%[^ ]")
    split_re = re.compile("(?<=% )(.*)").search(string)
    var_re = re.compile("(\w+)")
    
    indicadores = exp_re.findall(string)  # %s , %s
    try:
        variables = var_re.findall(split_re.groups()[0])  #chicho , nino
    except:
        return string

    for i, j  in zip(indicadores, variables):
        val = glob.get_variable(j)

        string = string.replace(i, str(val), 1)
    return re.findall ( """["'](.*?)['"]""", string, re.DOTALL)[0]

def action_parser(string):
    """Herramienta que nos permite realizar acciones provenientes de un
    botón un menú, o cualquiero otro sistema. Obtiene un string,
    realiza la acción y devuelve el resultado de dicha acción"""
    action = string.split()[0]
    if action == 'OpenXML':
        pantallas[Pantalla.pCurrent].sleep()
        name = string.split()[1] + '.xml'
        if pantallas.has_key(name):
            pantallas[name].awaken()
        else:
            try:
                loadtemplate(name)
            except Exception,e:
                print "Fatal: Imposible cargar pantalla", name
                print str(e)
                return
            pantallas[name].awaken()
    elif action == 'OpenPopup':
        pass
    elif action == 'Poweroff':
        print "Comienza secuencia de apagado iniciada por el usuario"
    #Mcuhas mas secuencias deben ir aquí, pero no han sido cargadas

#Definiciones realtivas a la pantalla

def RoundRect(surface,rect,color,radius=0.4):

    """
    AAfilledRoundedRect(surface,rect,color,radius=0.4)

    surface : destination
    rect    : rectangle
    color   : rgb or rgba
    radius  : 0 <= radius <= 1
    """

    rect         = Rect(rect)
    color        = Color(*color)
    alpha        = color.a
    color.a      = 0
    pos          = rect.topleft
    rect.topleft = 0,0
    rectangle    = pygame.Surface(rect.size,SRCALPHA)

    circle       = pygame.Surface([min(rect.size)*3]*2,SRCALPHA)
    pygame.draw.ellipse(circle,(0,0,0),circle.get_rect(),0)
    circle       = pygame.transform.smoothscale(circle,[int(min(rect.size)*radius)]*2)

    radius              = rectangle.blit(circle,(0,0))
    radius.bottomright  = rect.bottomright
    rectangle.blit(circle,radius)
    radius.topright     = rect.topright
    rectangle.blit(circle,radius)
    radius.bottomleft   = rect.bottomleft
    rectangle.blit(circle,radius)

    rectangle.fill((0,0,0),rect.inflate(-radius.w,0))
    rectangle.fill((0,0,0),rect.inflate(0,-radius.h))

    rectangle.fill(color,special_flags=BLEND_RGBA_MAX)
    rectangle.fill((255,255,255,alpha),special_flags=BLEND_RGBA_MIN)

    return surface.blit(rectangle,pos)

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'No se pudo cargar la imamen: ', fullname
    image = image.convert_alpha()
    return image, image.get_rect()

#Objetos globales
pantallas = {}

class Pantalla:
    """Crea un objeto para la pantalla. Lleva como hijos los cuadros que
    necesita y los dibujara con sus valores"""
    pCount = 0
    pCurrent = None
    def __init__(self, nombre, color):
        self.nombre = nombre
        self.color = color
        self.hijos = []  #Chance toque cambiar esto a futuro
        self.botones = {}
        self.handler = input_handler(self.nombre)
        Pantalla.pCount = Pantalla.pCount + 1
        if Pantalla.pCurrent == None:
            Pantalla.pCurrent = self.nombre
    def adopt(self, hijo):
        if type(hijo) is Cuadro:
            self.hijos.append(hijo)
        elif type(hijo) is Boton:
            if len(self.botones) == 0:
                hijo.set_s(True)
            else:
                hijo.set_s(False)
            self.botones[hijo.name] = hijo
            self.handler.add_button(hijo.name, *hijo.nav_xy)
        else:
            print "Advertencia: hijo no reconocido:", hijo
    def awaken(self, bg_color = 'Ivory'):
        Pantalla.pCurrent = self.nombre
        for child in self.hijos:
            child.draw()
        for boton in self.botones:
            self.botones[boton].draw()
        pygame.display.update()
    def sleep(self, bg_color = 'Ivory'):
        surface.fill(colores[bg_color])
        surface.set_alpha(255)
        pygame.display.update()
    def current(self):
        return Pantalla.pCurrent
    def update(self):
        self.awaken()
    def key(self, tecla):
        self.handler.move(tecla)

class Cuadro(object):
    """Clase padre de una pantalla. Lleva todos los atributos minimos
    necesarios para la utilizacion de un elemento en la pantalla"""
    global surface
    Count = 0
    names = []
    def __init__(self, nombre, color, pos = (0,0,0,0), rounded = 0):
        Cuadro.Count = Cuadro.Count + 1
        Cuadro.names.append(nombre)
        self.name = nombre
        self.pos = pos
        self.color = color
        self.gotImage = False
        self.rounded = rounded
        self.textos = []
        self.imagenes = []
    def name(self):
        return self.name
    def get_text(self, string, tamano, fuente, color, **kwargs):
        """Obtiene tiene texto para mostrar. En la varibale pos,
        0 es centrado, 1 es derecha, 2 es izquierda
        
        pos aun no se encuentra implementado                        """
        self.textos.append((str(string), tamano, fuente, kwargs))
    def got_text(self):
        return len(self.textos)
    def draw_text(self):
        for elem in self.textos:
            text = text_parser(elem[0])
            t = get_font(elem[2], elem[1])
            text_render = t.render(text, 1, (0,0,0))
            text_rect = text_render.get_rect()
            if 'posx' in elem[-1] and 'posy' in elem[-1]:  # elem[-1] = kwargs
                x = self.pos[0] + elem[-1]['posx']
                y = self.pos[1] + elem[-1]['posy']
                text_rect.topleft = (x , y)
            elif 'posy' in elem[-1] and 'align' in elem[-1]:
                if elem[-1]['align'] == -1:  # Izquierda
                    x = Rect(self.pos).left
                    y = self.pos[1] + elem[-1]['posy']
                    text_rect.topleft = (x , y)
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
            surface.blit(text_render, text_rect)
    def get_image(self, imagepath, posx = 0, posy = 0):
        img = load_image(imagepath)
        self.imagenes.append((img[0], img[1], posx, posy))
    def draw_image(self):
        for elem in self.imagenes:
            img_pos = (self.pos[0] + elem[2], self.pos[1] + elem[3])
            surface.blit(elem[0], img_pos)
            pygame.display.flip()
    def draw(self):
        if not self.rounded:
            pygame.draw.rect(surface, self.color, self.pos)
            self.draw_text()
            self.draw_image()
        else:
            RoundRect(surface, self.pos, self.color)
            self.draw_text()
            self.draw_image()

class Boton(Cuadro):
    """Crea un boton intereactivo en la pantalla. Puede tener diferentes
    acciones, dentro de el XML. Adicionalmente se le agrega texto e icon
    Se debe agregar a una clase pantalla, esta se encargara de activar
    y desactivar al engendro que tenemos por boton."""
    def set_values(self, in_color, nav_xy, action):
        self.ac_color = self.color
        self.in_color = in_color
        self.nav_xy = nav_xy
        self.action = action
    def do_action(self):
        """Sucede cuando el boton se presiona. La forma en la cual se cuente
        que se presione depende de input_handler, no del boton per se."""
        action_parser(self.action)
    def set_s(self, state):
        """Este estado se refiere a si se encuentra seleccionado o no. El
        cambio de estado cambia su color."""
        if state == True:
            self.color = self.ac_color
            self.state = False
        else:
            self.color = self.in_color
            self.state = True
        
class Matrix(object):
    """Matriz para el uso de botones y de menues, qque asigna posiciones
    de los objeteos y devuelve el objeto si se mueve hacia arriba, abajo
    izquierda, o derecha."""
    def __init__(self):
        self.m = [[]]
        self.position = [0,0]
    def add_value(self, name, x, y):
        while x+1 > len(self.m):
            self.m.append([])
        for i in range(len(self.m)):
            while len(self.m[i]) < y +1 :
                self.m[i].append([])
        self.m[x][y] = name
    def blank(self):
        if len(self.m[0]) == 0 and len(self.m) == 1:
            return True
        else:
            return False
    def print_matrix(self):
        for i in range(len(self.m)):
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

class input_handler(object):
    """Por el momento, esta clase solamente se encarga de tratar con
    los botones. Recibe lsa entradas directamente de Pygame, y hace
    los cambios necesario en la pantalla para reflejarlos en pantalla"""
    def __init__(self, pantalla_name):
        self.master = pantalla_name
        self.mapa = Matrix()
        self.active = True
        self.empty = True
    def add_button(self, name, x, y):
        """Obtiene los valores xy, de uno por uno. Se trata como si 
        fuera un array, el cual se usara para saber que elementos se
        tienen arriba, abajo, a la izquierda, o a la derecha"""
        self.mapa.add_value(name, x,y)
        self.empty = False
    def state(self, act=True):  #Que mierda es esto?
        self.active = act
    def move(self, mov):  #Tiene que ser un event.key
        if self.mapa.blank() == False:
            last_selected = self.mapa.get_value()
        else:
            return
        if mov ==  K_UP:
            self.mapa.move("Up")
            button_name = self.mapa.get_value()
            pantallas[self.master].botones[last_selected].set_s(False)
            self.last_selected = button_name
            pantallas[self.master].botones[button_name].set_s(True)
        elif mov ==  K_DOWN:
            self.mapa.move("Down")
            button_name = self.mapa.get_value()
            pantallas[self.master].botones[last_selected].set_s(False)
            self.last_selected = button_name
            pantallas[self.master].botones[button_name].set_s(True)
        elif mov ==  K_LEFT:
            self.mapa.move("Left")
            button_name = self.mapa.get_value()
            pantallas[self.master].botones[last_selected].set_s(False)
            self.last_selected = button_name
            pantallas[self.master].botones[button_name].set_s(True)
        elif mov == K_RIGHT:
            self.mapa.move("Right")
            button_name = self.mapa.get_value()
            pantallas[self.master].botones[last_selected].set_s(False)
            self.last_selected = button_name
            pantallas[self.master].botones[button_name].set_s(True)
        elif mov ==  K_RETURN:
            button_name = self.mapa.get_value()
            pantallas[self.master].botones[button_name].do_action()
        else:
            print "Tecla no reconocida:", mov
        pantallas[Pantalla.pCurrent].update()
        
                
        
class Menu(Cuadro):
    """Crea un menu de opciones el cual se puede mover y seleccionar acciones.
    Debe estar en pantalla completa idealmente para ser utilizado.
    El text agregado sirve para el título del menú."""
    def add_option(self, option):
        pass
    def set_action(self, action):
        pass

def get_color(color):
    global colores
    color = colores[color]
    return color

def loadtemplate(filename): 
    tree = ET.parse(filename)
    root = tree.getroot()
    if root.tag == "Pantalla":
            print "Abirendo " + root.tag
            p = Pantalla(filename, colores['White'])  # WAT
            pantallas[filename] = p
            for child in root.findall("Caja"):
                x = child.find('PosX')
                y = child.find('PosY')
                al = child.find('Alto')
                an = child.find('Ancho')
                posc = (int(x.text), int(y.text), int(an.text), int(al.text))
                color = child.find('Color').text
                color = get_color(color)
                rounded = float(child.find('Redondez').text)
                c = Cuadro(str(child.attrib['Nombre']), color,  posc, rounded)
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
                color = child.find('Color_activo').text
                color = get_color(color)
                rounded = float(child.find('Redondez').text)
                b = Boton(str(child.attrib['Nombre']), color,  posc, rounded)
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
                b.set_values(color_in, (valx, valy), action )
                pantallas[filename].adopt(b)
    else:
        print "XML inválido."

def main(filename):
    pygame.init()
    pygame.font.init()
    noFont = pygame.font.SysFont(None, 8)

    clock = pygame.time.Clock()
    
    surface.fill(colores['Ivory'])
    loadtemplate(filename)
    pygame.display.update()
    running = True
    screen_state = True
    while running:
        clock.tick(30)
        if screen_state==True:
            try:
                pantallas[Pantalla.pCurrent].update()
            except:
                pass
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    print "\nBye Bye"
                    pygame.quit()
                    running = False
                elif event.key == K_q:
                    print "Press ESC to quit"
                elif event.key == K_a:
                    screen_state = True
                    pantallas[Pantalla.pCurrent].awaken()
                elif event.key == K_s:
                    screen_state = False
                    pantallas[Pantalla.pCurrent].sleep()
                elif event.key == K_m:
                    action_parser("OpenXML test2")
                elif event.key == K_n:
                    action_parser("OpenXML test")
                else:
                    pantallas[Pantalla.pCurrent].key(event.key)
    return 0

if __name__ == '__main__':
    print "Error: Esto modulo no es independiente. Corra Main."

class Screen(object):
    """Maneja por completo todo lo que se muestra en la pantalla,
    mediante el uso de pygame. No confundir con clase Pantalla."""
    def __init__(self):
        self.running = False
    def run(self, filename):
        global q
        main(filename)
