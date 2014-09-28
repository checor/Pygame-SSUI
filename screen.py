# -*- coding: utf-8 -*-
"""
Created on Thu Jul 10 19:24:52 2014

@author: checor@gmail.com

Posible cambio a classes
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
	#"Las aventuras de %s, el %s con pelos" % chicho nino
	exp_re = re.compile("%[^ ]")
	split_re = re.compile("(?<=% )(.*)").search(string)
	var_re = re.compile("(\w+)")
	
	indicadores = exp_re.findall(string)  # %s , %s
	variables = var_re.findall(split_re.groups()[0])  #chicho , nino
	
	value = []
	for i, j  in zip(indicadores, variables):
		exec("value.append(glob."+j+")")
		

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
    pcurrent = None
    def __init__(self, nombre, color):
        #print "Pantalla creada: ", nombre
        self.nombre = nombre
        self.color = color
        self.hijos = []
        Pantalla.pCount = Pantalla.pCount + 1
    def adopt(self, hijo):
        if isinstance(hijo, Cuadro):
            #print "Hijo", hijo.name, "creado"
            self.hijos.append(hijo)
        """elif isinstance(hijo, Popup):
            pass
        elif isinstance(hijo, Boton):
            pass
        elif isinstance(self, Pito):
            pass"""
    def awaken(self):
        global surface
        pcurrent = self.nombre
        for child in self.hijos:
            #print '\nDibujando ' + child.name
            child.draw()
        pygame.display.update()
    def sleep(self, color = 'Ivory'):
        global surface
        surface.fill(colores[color])
        pygame.display.update()
    def current(self):
        return pcurrent
    def update(self):
        pygame.display.update()
        
    
#class PopupMenu

class Cuadro:
    """Clase padre de una pantalla. Lleva todos sus atributos"""
    global surface
    Count = 0
    names = []
    def __init__(self, nombre, color, pos = (0,0,0,0), rounded = 0):
        #print "Cuadro creado: ", nombre
        Cuadro.Count = Cuadro.Count + 1
        Cuadro.names.append(nombre)
        self.name = nombre
        self.pos = pos
        self.color = color
        self.gotImage = False
        self.rounded = rounded
        self.textos = []
        self.imagenes = []
    def get_text(self, string, tamano, fuente, color, **kwargs):
        """Obtiene tiene texto para mostrar. En la varibale pos,
        0 es centrado, 1 es derecha, 2 es izquierda
        
        pos aun no se encuentra implementado                        """
        self.textos.append((str(string), tamano, fuente, kwargs))
    def got_text(self):
        return len(self.textos)
    def drawtext(self):
        for elem in self.textos:
            """f = get_font(elem[2], elem[1])
            pgtext = f.render(elem[0], 1, (0,0,0))
            pgrect = pgtext.get_rect()
            pgrect.topleft = (self.pos[0], self.pos[1])
            surface.blit(pgtext, pgrect)"""
            t = get_font(elem[2], elem[1])
            text_render = t.render(elem[0], 1, (0,0,0))
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
                print "Good"
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
                print x, y, self.pos[1]
                text_rect.top = y
            else:
                print "Fatal! Texto mal alineado!!", elem[-1]
            surface.blit(text_render, text_rect)
    def get_image(self, imagepath, posx = 0, posy = 0):
        img = load_image(imagepath)
        #print img
        self.imagenes.append((img[0], img[1], posx, posy))
    def draw_image(self):
        for elem in self.imagenes:
            #print "Hola", elem[0], self.pos
            img_pos = (self.pos[0] + elem[2], self.pos[1] + elem[3])
            surface.blit(elem[0], img_pos)
            pygame.display.flip()
    def draw(self):
        if not self.rounded:
            pygame.draw.rect(surface, self.color, self.pos)
            self.drawtext()
            self.draw_image()
        else:
            RoundRect(surface, self.pos, self.color)
            self.drawtext()
            self.draw_image()

class Boton(Cuadro):
    """Crea un boton intereactivo en la pantalla. Puede tener diferentes
    acciones, dentro de el XML. Adicionalmente se le agrega texto e icono.
    Se debe agregar a una clase pantalla, esta se encargara de activar
    y desactivar al engendro que tenemos por boton."""
    def __init__(self, nombre, color, pos = (0,0,0,0), rounded = 0):
        Cuadro.__init__(self, nombre, color, pos = (0,0,0,0), rounded = 0)  #Args
        """#print "Cuadro creado: ", nombre
        Cuadro.Count = Cuadro.Count + 1
        Cuadro.names.append(nombre)
        self.name = nombre
        self.pos = pos
        self.color = color #No debe usarse
        self.gotImage = False
        self.rounded = rounded
        self.textos = []
        self.imagenes = []
        #A partir de aquí comienza código especial de botón
        self.selected = False
        self.selected_color = None
        self.no_selected_color = color"""
    def set_action(self, action, objecto = None):
        """El hueso de un botón ¿que hará cuando se presione?

            actiontype = 'menu', 'popup', 'start', 'sleep' ...
            la accion viene directo del XML

            obejto = en caso de ser necesario

        Vea la documentación para mas informacion
        """
        actions = {"menu" : 0, "popup" : 1, "start" : 2, "sleep" : 3,
        "activate" : 4}
        try:
            action = actions[action]
        except:
            #print "Accion no reconocida", action
            return
        #Comienza a realizar la accion seleccionada
        if action == 0:
            pass
            #Agregar variable a la pantalla padre, how?
        """if action == 'menu':
            a = 0
            b = get_pantalla_number(objeto)
        elif action == 'popup'
            pass #Aun no se como implementar esta vaina"""
    def set_xy(self, xy = (0,0)):
        """Es importante esta opcion, si no nopodra ser seleccionada
        xy es una rejilla virtual para poder dezplazarse entre los
        otros botones de la pantalla (arriba/abajo/izq/der"""
        self.xy = (xy)
    def set_scolors(self, col):
        """Elegi el color el cual se va a utlizar cuando este
        selecionado"""
        self.selected_color = color
    def selected(self):
        self.selected = True
    def draw(self):
        if self.selected == True:
            draw_color = self.selected_color
        else:
            draw_color = self.unselected_color
        if not self.rounded:
            pygame.draw.rect(surface, draw_color, self.pos)
            self.drawtext()
            self.draw_image()
        else:
            RoundRect(surface, draw_color, self.color)
            self.drawtext()
            self.draw_image()

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
                print "Caja encontrada! Nombre: " + child.attrib['Nombre']
                #comenzar a realizar los objetos
                #Mejorar esta parte del código
                x = child.find('PosX')
                #print x.tag, x.text
                y = child.find('PosY')
                #print y.tag, y.text
                al = child.find('Alto')
                #print al.tag, al.text
                an = child.find('Ancho')
                #print an.tag, an.text
                posc = (int(x.text), int(y.text), int(an.text), int(al.text))
                #print posc
                color = child.find('Color').text
                color = get_color(color)
                rounded = float(child.find('Redondez').text)
                c = Cuadro(str(child.attrib['Nombre']), color,  posc, rounded)
                #pantallas[Pantalla.pCount - 1].adopt(c)
                pantallas[filename].adopt(c)
                for t in child.findall("Texto"):
                    ttext = t.find("Text").text
                    #print "Texto encontrado: " + ttext
                    tsize = int(t.find("Tamano").text)
                    tfont = t.find("Fuente").text
                    tcolor = t.find("Color").text
                    try:
                        var = t.find("Global_Variable").text
                        print var
                        exec("var_t = glob."+var)
                        print var_t
                        ttext += str(var_t)
                    except:
                        print "La cagaste ivan"
                    c.get_text(ttext, tsize, tfont, tcolor, line=.5, align=0)
                for imag in child.findall("Imagen"):
                    imagen = imag.find("Filename").text
                    img_posx = int(imag.find("PosX").text)
                    img_posy = int(imag.find("PosY").text)
                    c.get_image(imagen, img_posx, img_posy)
            #pantallas[0].awaken() #Awaken my masters
    else:
        print "XML inválido."

def main(filename):
    print glob.q

    pygame.init()
    pygame.font.init()
    noFont = pygame.font.SysFont(None, 8)

    clock = pygame.time.Clock()
    
    surface.fill(colores['Ivory'])
    loadtemplate(filename)
    pygame.display.update()
    running = True
    while running:
        clock.tick(30)  # 30 FPS
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
                    glob.q.put("Putos todos")
                elif event.key == K_a:
                    pantallas["test.xml"].awaken()
                elif event.key == K_s:
                    pantallas["test.xml"].sleep()
                elif event.key == K_m:
                    print clock.get_fps()
                    glob.numero_prueba += 1
    return 0

if __name__ == '__main__':
    main('')


class Screen:
    """Maneja por completo todo lo que se muestra en la pantalla,
    mediante el uso de pygame. No confundir con clase Pantalla."""
    def __init__(self):
        self.running = False
    def run(self, filename):
        global q
        main(filename)
        
