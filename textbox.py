import string
import os
import pygame
import numpy as np
from scipy.stats import dweibull
from decimal import Decimal
import matplotlib.pyplot as plt


WHITE = (255, 255, 255)
WHITE2 = (247, 247, 247)
BLUE = (65, 105, 225)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
GRAY_2 = (108, 118, 118)
GRAY_3 = (70, 70, 70)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
SEMIWHITE = (245, 245, 245)
LIGHTGRAY = (192, 192, 192)
GANSBORO = (220, 220, 220)
SLATEGRAY = (112, 128, 144)
ACCEPTED = string.ascii_letters + '_-.' + string.digits
ACCEPTED_NUM = 'e-'+ string.digits

class TextBox(object):
    def __init__(self, rect, acepted=ACCEPTED, **kwargs):
        self.rect = pygame.Rect(rect)
        self.buffer = []
        self.final = None
        self.rendered = None
        self.render_rect = None
        self.render_area = None
        self.blink = True
        self.blink_timer = 0.0
        self.process_kwargs(kwargs)
        self.acepted = acepted  # Caracteres aceptados

    def process_kwargs(self, kwargs):
        defaults = {"id" : None,
                    "command" : None,
                    "active" : True,
                    "color" : pygame.Color("white"),
                    "font_color" : pygame.Color("black"),
                    "outline_color" : pygame.Color("black"),
                    "outline_width" : 1,
                    "active_color" : pygame.Color("red"),
                    "font" : pygame.font.SysFont('Arial', self.rect.height+2),
                    "clear_on_enter" : False,
                    "inactive_on_enter" : True}
        for kwarg in kwargs:
            if kwarg in defaults:
                defaults[kwarg] = kwargs[kwarg]
            else:
                raise KeyError("InputBox accepts no keyword {}.".format(kwarg))
        self.__dict__.update(defaults)

    def get_event(self, event):
        if event.type == pygame.KEYDOWN and self.active:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.execute()
            elif event.key == pygame.K_BACKSPACE:
                if self.buffer:
                    print(self.buffer)
                    self.buffer.pop()
                    print(self.buffer)
            elif event.unicode in self.acepted:
                self.buffer.append(event.unicode)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)

    def execute(self):
        if self.command:
            self.command(self.id, self.final)
        self.active = not self.inactive_on_enter
        if self.clear_on_enter:
            self.buffer = []

    def update(self):
        new = "".join(self.buffer)
        if new != self.final:
            self.final = new
            self.rendered = self.font.render(self.final, True, self.font_color)
            self.render_rect = self.rendered.get_rect(x=self.rect.x+2,
                                                      centery=self.rect.centery)
            if self.render_rect.width > self.rect.width-6:
                offset = self.render_rect.width-(self.rect.width-6)
                self.render_area = pygame.Rect(offset, 0, self.rect.width-6,
                                           self.render_rect.height)
            else:
                self.render_area = self.rendered.get_rect(topleft=(0, 0))
        if pygame.time.get_ticks() - self.blink_timer > 300:
            self.blink = not self.blink
            self.blink_timer = pygame.time.get_ticks()

    def draw(self, surface):
        outline_color = self.active_color if self.active else self.outline_color
        outline = self.rect.inflate(self.outline_width*2, self.outline_width*2)
        surface.fill(outline_color, outline)
        surface.fill(self.color, self.rect)
        if self.rendered:
            surface.blit(self.rendered, self.render_rect, self.render_area)
        if self.blink and self.active:
            curse = self.render_area.copy()
            curse.topleft = self.render_rect.topleft
            surface.fill(self.font_color, (curse.right+1, curse.y, 2, curse.h))


class ListBox:
    def __init__(self, size=(140, 210), posi=(120, 240)):
        self.size = size
        self.container_clases = pygame.Surface(size)  # listmenu de clases
        self.container_clases.fill(WHITE)
        self.posi_container = posi
        self.list_items = list()  # Contiene los elementos dentro del contenedor
        self.selected = 1  #
        self.conten_actual = 1
        self.selected_item = pygame.Rect(self.posi_container[0]+2, self.posi_container[1]+1*self.selected, 136, 28)
        self.dt = 30  # Altura de cada recta
        self.down = 0  # Indicar cuantos desplazamientos ha dado el scroll de clases
        self.rects = []
        self.num_rects = 7  # Número de rectas dentro del listbox
        self.font = pygame.font.SysFont('Arial', 14)
        self.time = np.linspace(0, 8760, 1000)
        self.make_rects()
        self.types = {'exp': 'Distribución Exponencial', 'ray': 'Distribución Rayleigh', 'wei': 'Distribución Weibull'}
        self.scroll = ScrollBar(self.posi_container, heigth=size[1], rects=self.num_rects)
        self.panel_back = pygame.Surface((size[0]+40, size[1]+60))
        self.panel_back.fill(GRAY_2)
        self.panel_pos = (posi[0]-10, posi[1]-20)
        self.accept = TextButton('Aceptar', 'ok', size=(60, 30), position=(posi[0]+size[0]/2-20, posi[1]+size[1]-10))

    def make_rects(self):
        for index in range(self.num_rects):
            self.rects.append(pygame.Rect(self.posi_container[0] + 1, self.posi_container[1] + (1+self.dt*index), 136, 28))

    def add_data(self, element):
        self.list_items.append(element)

    def del_data(self, element):
        self.list_items.remove(element)

    def consult_position(self, position):
        for index in range(self.num_rects):
            if self.rects[index].collidepoint(position):
                posible_indice = index+1
                if posible_indice >= len(self.list_items):  # Si la recta consultada supera la cantidad de elementos
                    self.conten_actual = len(self.list_items)
                else:
                    self.conten_actual = posible_indice

    def draw(self, screen, time):
        screen.blit(self.container_clases, self.posi_container)
        self.selected_class = pygame.Rect(self.posi_container[0] + 2,
                                          (self.posi_container[1] + (30 * (self.conten_actual - 1))) + 1, 136, 28)
        pygame.draw.rect(screen, BLUE, self.selected_class, 0)
        for index, element in enumerate(self.list_items):
            screen.blit(self.font.render(element.tag, True,
                                                  BLACK),
                                 (self.posi_container[0] + 5, self.posi_container[1] + 5 + (index * self.dt)))
        caja = self.list_items[self.conten_actual-1]
        self.make_plot(caja, time)
        self.scroll.draw_bar(screen, len(self.list_items), pos_der=self.size[0], pos_abajo=self.size[1])

    def draw_mod(self, screen):
        """Dibujo de listbox para modulos"""
        screen.blit(self.panel_back, self.panel_pos)
        screen.blit(self.container_clases, self.posi_container)
        self.accept.draw_button(screen)
        self.selected_class = pygame.Rect(self.posi_container[0] + 2,
                                          (self.posi_container[1] + (30 * (self.conten_actual - 1))) + 1, 136, 28)
        pygame.draw.rect(screen, BLUE, self.selected_class, 0)
        for index, element in enumerate(self.list_items):
            screen.blit(self.font.render(element.name, True,
                                                  BLACK),
                                 (self.posi_container[0] + 5, self.posi_container[1] + 5 + (index * self.dt)))
        self.scroll.draw_bar(screen, len(self.list_items), pos_der=self.size[0], pos_abajo=self.size[1])

    def make_plot(self, elemento, time):
        plt.style.use('seaborn')  # pretty matplotlib plots
        plt.cla()
        self.time = np.linspace(0, time, 500)
        t = self.time
        if elemento.tipo != 'paralelo' and elemento.tipo != 'modulo':
            plt.plot(self.time, eval(elemento.value), c='blue',
                     label=r'$\beta=%.3f,\ \lambda=%.3E$' % (float(elemento.betha), Decimal(elemento.alpha)))
            plt.xlabel('t')
            plt.ylabel(r'$p(t|\beta,\lambda)$')
            plt.title(self.types[elemento.mod])
            plt.legend()
        else:
            plt.plot(self.time, eval(elemento.value), c='blue')
            plt.xlabel('t')
            plt.ylabel(r'$p(t|\beta,\lambda)$')


class ScrollBar:
    """Clase que permite dibujar scrollbar"""
    def __init__(self, pos, width=25, heigth=40, rects=1):
        self.pos = pos
        self.width = width  # Ancho de la barra
        self.heigth = heigth-width*2
        self.rects = rects
        self.up = pygame.image.load(os.path.join("icons", "up.png"))
        self.down = pygame.image.load(os.path.join("icons", "down.png"))
        self.up_surface = pygame.Surface((width, width))
        self.up_surface.fill(WHITE2)
        self.down_surface = pygame.Surface((width, width))
        self.down_surface.fill(WHITE2)
        self.fondo_barra = pygame.Surface((width, heigth))
        self.fondo_barra.fill(GRAY_2)
        self.fondo_rect = self.fondo_barra.get_rect()
        self.dt = 10  # Indica el desplazamiento de la barra
        self.actual_pos = 0  # Posición actual

    def draw_bar(self, screen, num_rows, pos_abajo=0, pos_arriba=0, pos_der=0, pos_izq=0):
        if num_rows>self.rects:  # Indica si existen mas de los elementos posibles a visualizar en el contenedor
            self.barra = pygame.Surface(((self.width - 4), self.heigth-(num_rows-self.rects)*self.dt))
        else:
            self.barra = pygame.Surface(((self.width - 4), self.heigth))
        self.barra_rect = self.barra.get_rect()
        self.barra.fill(RED)
        self.down_surface.blit(self.down, (3, 3))
        self.up_surface.blit(self.up, (3, 3))
        self.barra_rect.center = (self.pos[0] + (self.width / 2) + pos_der, 0)
        self.barra_rect.y = self.pos[1]+self.width
        self.fondo_rect.center = (self.pos[0] + (self.width / 2) + pos_der, self.pos[1] + (self.heigth / 2))
        screen.blit(self.fondo_barra, self.fondo_rect)
        screen.blit(self.barra, self.barra_rect)
        screen.blit(self.down_surface, (self.pos[0] + pos_der, self.pos[1]+(pos_abajo-self.width)))
        screen.blit(self.up_surface, (self.pos[0] + pos_der, self.pos[1]))

    def action_bar(self):
        pass


class RadioButton:
    def __init__(self, name, texto, position=(0, 0), size=(26, 26), color=GRAY, active=False):
        self.name = name
        self.no_pushed = pygame.image.load(os.path.join("icons", "radio.png"))
        self.pushed = pygame.image.load(os.path.join("icons", "radio_check.png"))
        self.text = texto
        self.position = position
        self.size = size
        self.color = color
        self.own_surface = pygame.Surface(size)
        self.own_surface.fill(self.color)
        self.own_surface.blit(self.no_pushed, (0, 0))
        self.font = pygame.font.SysFont('Arial', 14)
        self.recta = pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])
        self.over = False
        self.push = active

    def draw(self, screen):
        if self.over:
            screen.blit(self.font.render(self.text, True, BLACK), (self.position[0] + 28, self.position[1] + 5))
            self.font.set_underline(True)
        else:
            screen.blit(self.font.render(self.text, True, BLACK), (self.position[0] + 28, self.position[1] + 5))
            self.font.set_underline(False)
        if self.push:
            self.own_surface.fill(self.color)
            self.own_surface.blit(self.pushed, (0, 0))
        else:
            self.own_surface.fill(self.color)
            self.own_surface.blit(self.no_pushed, (0, 0))
        screen.blit(self.own_surface, self.position)

class CheckButton:
    def __init__(self, name, texto, position=(0, 0), size=(26, 26), color=GRAY, active=False):
        self.name = name
        self.no_pushed = pygame.image.load(os.path.join("icons", "uncheck.png"))
        self.pushed = pygame.image.load(os.path.join("icons", "check.png"))
        self.text = texto
        self.position = position
        self.size = size
        self.color = color
        self.own_surface = pygame.Surface(size)
        self.own_surface.fill(self.color)
        self.own_surface.blit(self.no_pushed, (0, 0))
        self.font = pygame.font.SysFont('Arial', 14)
        self.recta = pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])
        self.over = False
        self.push = active

    def draw(self, screen):
        if self.over:
            screen.blit(self.font.render(self.text, True, BLACK), (self.position[0] + 28, self.position[1] + 5))
            self.font.set_underline(True)
        else:
            screen.blit(self.font.render(self.text, True, BLACK), (self.position[0] + 28, self.position[1] + 5))
            self.font.set_underline(False)
        if self.push:
            self.own_surface.fill(self.color)
            self.own_surface.blit(self.pushed, (0, 0))
        else:
            self.own_surface.fill(self.color)
            self.own_surface.blit(self.no_pushed, (0, 0))
        screen.blit(self.own_surface, self.position)


class TextButton:
    def __init__(self, text, name, position=(0, 0), size=(90, 30), text_position=(5, 5)):
        self.text = text
        self.name = name
        self.position = position
        self.size = size
        self.text_position = text_position
        self.own_surface = pygame.Surface(self.size)
        self.own_surface.fill(SEMIWHITE)
        self.recta = pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])
        self.font = pygame.font.SysFont('Arial', 13)
        self.own_surface.blit(self.font.render(self.text, True,
                              BLACK), self.text_position)
        self.over = False

    def draw_button(self, screen):
        if self.over:
            self.own_surface.fill(SLATEGRAY)
            self.own_surface.blit(self.font.render(self.text, True,
                                                   BLACK), self.text_position)
            self.font.set_underline(True)
        else:
            self.own_surface.fill(SEMIWHITE)
            self.own_surface.blit(self.font.render(self.text, True,
                                                   BLACK), self.text_position)
            self.font.set_underline(False)
        screen.blit(self.own_surface, self.position)
        pygame.draw.rect(screen, BLACK, self.recta, 1)
