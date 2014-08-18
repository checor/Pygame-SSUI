# -*- coding: utf-8 -*-
"""
Created on Thu Jul 10 19:24:52 2014

@author: @checor

Usando el martillo que tengo para un chingo de clavos
"""

import pygame, sys
from pygame.locals import *
import xml.etree.ElementTree as ET
import os

size = width, height = 320, 240 #Elegimos el tamaño de la pantalla
surface = pygame.display.set_mode(size) #Pantalla completa a futuro
pygame.display.set_caption("Newtech Software") #Nombre de la ventana
clock = pygame.time.Clock()

"""
Variables para pygame
Estas seran movidas a un libreria mas adelante
"""

#Colores de guia de Firefox OS
colores = {"Blue" : (0, 170, 204) , "Orange" : (255,78,0) , "Brick" :
               (205,103,35) , "Red" : (185,0,0) , "Green" : (95,155,10),
               "Black" : (0,0,0) , "Warm grey" : (51,51,51) , "Warm Grey" :
               (44,57,59) , "Light grey" : (244,244,244) , "Ivory" : 
               (234,234,231) , "White" : (255,255,255) }
#Fuentes
pygame.init()
noFont = pygame.font.SysFont(None, 8)
"""Fin de variables"""

#Definiciones
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


#Objetos globales
pantallas = []

class Pantalla:
    """Crea un objeto para la pantalla. Lleva como hijos los cuadros que 
    necesita y los dibujara con sus valores"""
    pCount = 0
    names = []
    def __init__(self, nombre, color, screensaver = False):
        print "Pantalla creada: ", nombre
        self.nombre = nombre
        self.color = color
        self.screensaver = screensaver
        self.hijos = []
        Pantalla.pCount = Pantalla.pCount + 1
        Pantalla.names.append(nombre)
    def pintate(self):
        global surface
        surface.Fill(Colors[self.color])
    def update(self):
        pygame.display.update()
    def cuadrifica(self):
        for hijo in self.hijos: 
            pass
    def adopt(self, hijo):
        if isinstance(hijo, Cuadro) == True:
            print "Hijo", hijo.name, "creado"
            self.hijos.append(hijo)
    def awaken(self):
        global surface
        #Awaken my masters
        for child in self.hijos:
            print '\nDibujando ' + child.name
            child.draw()
        pygame.display.update()

class Cuadro:
    """Clase padre de una pantalla. Lleva todos sus atributos"""
    Count = 0
    names = []
    def __init__(self, nombre, color, pos = (0,0,0,0), rounded = False):
        print "Cuadro creado: ", nombre
        Cuadro.Count = Cuadro.Count + 1
        Cuadro.names.append(nombre)
        self.name = nombre
        self.pos = pos
        self.color = color
        self.gotText = False
        self.gotImage = False
        self.rounded = rounded
    def get_text(self, texto, tamano, fuente, color, pos=0):
        """Obtiene tiene texto para mostrar. En la varibale pos,
        0 es centrado, 1 es derecha, 2 es izquierda"""
        self.gotText = True
        self.tt = str(texto)
        self.ttam = tamano
        self.tf = fuente
        self.tpos = pos
        self.tcol = color
    def hay_text(self):
        return self.gotText
    def drawtext(self):
        """Dibuja en la pantalla el texto que tiene el cuadro"""
        #Falta agregar todo lo relacionado con la posicion
        if self.gotText:
            f = pygame.font.Font(get_font(self.tf), self.ttam)
            pgtext = f.render(self.tt, 1, (0,0,0))
            pgrect = pgtext.get_rect()
            pgrect.topleft = (self.pos[0], self.pos[1]) #Primitivo
            surface.blit(pgtext, pgrect)
    def get_image(self, imagepath, posx = 0, posy = 0):
        #Checar primero si existe el path
        if os.path.exists(imagepath):
            self.ipath = imagepath
            self.iposx = posx
            self.iposy = posy
            self.gotImage = True
        else:
            print 'Imagen no existente. Checar su ubicación'
    def drawimage(self):
        pass
    def draw(self):
        #Cambiar esto a otro tipo de rectangulo
        if not self.rounded:
            pygame.draw.rect(surface, self.color, self.pos)
            self.drawtext()
            self.drawimage()
        else:
            RoundRect(surface, self.pos, self.color)
            self.drawtext()

class Boton(Cuadro):
    """Crea un boton intereactivo en la pantalla. Puede tener diferentes
    acciones, dentro de el XML. Adicionalmente se le agrega texto e icono."""
    def get_icon(self, path, pos = 0):
        """Obtiene ubicacion de un icono para poner en el cuadro"""
        pass
    def got_icon(self):
        return self.got_icon
    def get_action(self, actionType, active=False):
        self.active = False
        #Agregar

class Menu(Cuadro):
    """Crea un menu de opciones el cual se puede mover y seleccionar acciones.
    Debe estar en pantalla completa idealmente para ser utilizado.
    El text agregado sirve para el título del menú."""
    def add_option(self, option):
        pass
    def set_action(self, action):
        pass

def get_font(font): #Esta debe ir en el import
    if font == 'None':
        return None
    elif font == 'Arial':
        return None
    else:
        return None

def get_color(color):
    global colores
    color = colores[color]
    return color
        
def loadtemplate(filename): #Idem
    global pantallas
    global colores
    global noFont
    tree = ET.parse(filename)
    root = tree.getroot()
    if root.tag == "Pantalla":
            print "Abirendo " + root.tag
            p = Pantalla("main", colores['White'])
            pantallas.append(p)
            for child in root.findall("Caja"):
                print "Caja encontrada! Nombre: " + child.attrib['Nombre']
                #comenzar a realizar los objetos
                #Mejorar esta parte del código
                x = child.find('PosX')
                print x.tag, x.text
                y = child.find('PosY')
                print y.tag, y.text
                al = child.find('Alto')
                print al.tag, al.text
                an = child.find('Ancho')
                print an.tag, an.text
                posc = (int(x.text), int(y.text), int(an.text), int(al.text))
                print posc
                color = child.find('Color').text
                color = get_color(color)
                c = Cuadro(str(child.attrib['Nombre']), color,  posc, True)
                pantallas[Pantalla.pCount - 1].adopt(c)
                for t in child.findall("Texto"):
                    ttext = t.find("Text").text
                    print "Texto encontrado: " + ttext
                    tsize = int(t.find("Tamano").text)
                    tfont = t.find("Fuente").text
                    tcolor = t.find("Color").text
                    tfont = None #Parche mamon
                    c.get_text(ttext, tsize, tfont, tcolor)
            print "Awaken my masters"
            pantallas[0].awaken() #Awaken my masters
    else:
        print "XML inválido."

def main():
    global pantallas
    print "Newtech software"
    print "Inicializando...\n"
    #pygame.init()      #cambio temporal
    surface.fill(colores['White'])
    loadtemplate('test.xml')
    pygame.display.update()
    #pantallas[0].
    time = clock.tick(30)
    running = True
    while running:
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
    return 0

if __name__ == '__main__':
    main()
