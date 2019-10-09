import pygame
import sys
import os
import matplotlib.pyplot as plt
from properties import *
from pygame.locals import *


WHITE = (255, 255, 255)
GRAY = (112, 128, 144)


class PGManten:
    """
    Clase para trabajar con pygame
    """
    def __init__(self, window_size=(1000, 700)):
        self.initialize_pygame()
        self.clock = pygame.time.Clock()
        self.WINDOW_SIZE = window_size  # Tamaño ventana principal
        self.screen_form = pygame.display.set_mode(self.WINDOW_SIZE)
        self.property_class = Property(workspace_size=(900, 520))  # Instancia de propiedades

    @staticmethod
    def initialize_pygame():
        pygame.init()
        os.environ['SDL_VIDEO_CENTERED'] = '1'  # Centra la interfaz
        pygame.display.set_caption('Diagramas confiabilidad')

    def execute_pygame(self):
        position_mouse = (0, 0)  # Inicializar posicion presionad
        grid = True  # Rejilla habilitada
        close = False
        timer = 0  # Necesario para el doble click
        dt = 0  # Incrementos del timer
        while not close:
            keys = pygame.key.get_pressed()  # Obtencion de tecla presionada
            for event in pygame.event.get():
                if self.property_class.draw:  # Eventos para texto de name
                    self.property_class.check_text(event)
                if event.type == pygame.QUIT:
                    close = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    position_mouse = pygame.mouse.get_pos()
                    if pygame.mouse.get_pressed()[0]:  # Boton izquierdo
                        if timer == 0:
                            timer = 0.001
                            for container in self.property_class.elementos['containers']:  #Acciones de ingreso de texto
                                if container.selected:
                                    pass
                        elif timer < 0.3 and not self.property_class.elem_type:  # Doble click apertura modulo/Debo bloquear esto mientras aun se este ejecutando el panel de propiedades
                            timer = 0
                            self.property_class.name_element.active = True  # Activar casilla de nombre propiedades
                            self.property_class.element_property(position_mouse, 1)  # Activar propiedad elemento
                            if self.property_class.elem_selected:
                                self.property_class.name_element.buffer = \
                                    [char for char in self.property_class.elem_selected]
                            # Aca se le pone al buffer el texto del elemento seleccionado
                            for container in self.property_class.elementos['containers']:  #Acciones de ingreso de texto
                                if container.selected:
                                    for caja in container.cajas:
                                        if caja.tag == self.property_class.elem_selected:
                                            self.property_class.box_field1.buffer = [char for char in str(caja.alpha)]  # se le pone a los buffers los valores de los elementos seleccionados
                                            self.property_class.box_field2.buffer = [char for char in str(caja.betha)]
                                    for knn_ind in container.knn:
                                        for col in knn_ind.cols:
                                            for caja in col:
                                                if caja.tag == self.property_class.elem_selected:
                                                    self.property_class.box_field1.buffer = \
                                                        [char for char in str(caja.alpha)]
                                                    self.property_class.box_field2.buffer = \
                                                        [char for char in str(caja.betha)]
                                    for stand_ind in container.stand:
                                            for caja in stand_ind.cajas:
                                                if caja.tag == self.property_class.elem_selected:
                                                    self.property_class.box_field1.buffer = [char for char in str(caja.alpha)]
                                                    self.property_class.box_field2.buffer = [char for char in str(caja.betha)]
                                    for kdn in container.kdn:
                                        if kdn.tag == self.property_class.elem_selected:
                                            self.property_class.box_field1.buffer = [char for char in str(kdn.alpha)]
                                            self.property_class.box_field2.buffer = [char for char in str(kdn.betha)]
                        if self.property_class.container.recta_new.collidepoint(position_mouse) \
                                and self.property_class.cont < 7:  # Agregar pestañas si son menos de 7
                            self.property_class.add_container()
                        self.property_class.delete_container(position_mouse)  # Verificar si alguna pestaña se cierra
                        self.property_class.select_container(position_mouse)  # Seleccionar pestaña
                        self.property_class.check_actions(position_mouse)  # verifica acciones
                        self.property_class.close_elements(position_mouse)  # Cerrar elementos
                        self.property_class.add_red_elements(position_mouse)
                        if self.property_class.connecting:  # Si se encuentra la linea de dibujo activa se pueden adicionar elementos a la conexion
                            self.property_class.duple_conection.append([self.property_class.init_pos, self.property_class.end_line])
                            if self.property_class.end_line != self.property_class.duple_conection[0][0]:
                                self.property_class.init_pos = self.property_class.end_line
                                for container in self.property_class.elementos['containers']:
                                    if container.selected:
                                        for nodo in container.nodos:
                                            if nodo.rect.collidepoint(self.property_class.end_line):
                                                self.property_class.hold_line = False  # Deja de dibujar la linea
                                                self.property_class.line_able = False  # Deja de habilitar linea
                                                self.property_class.connecting = False  # Deja de conectar
                                                self.property_class.elem2 = nodo  # Elemento final de la conexion
                                                conexion = Conexion(self.property_class.duple_conection,
                                                                                            self.property_class.elem1,
                                                                                            self.property_class.elem2)
                                                container.conections.add(conexion)
                                                self.property_class.duple_conection = []
                                                # Verificar a que nodo del sistema van los nodos fisicos del objeto
                                                container.check_node(self.property_class.elem1, self.property_class.elem2)

                            else:
                                self.property_class.duple_conection.pop()
                        if self.property_class.actions[3]:  # Eliminar elemento
                            self.property_class.delete_element(position_mouse)
                        if self.property_class.actions[5]:  # importa modulo
                            if self.property_class.list_box_modules.accept.recta.collidepoint(position_mouse):
                                self.property_class.draw_module = True
                                self.property_class.elem_modulo = self.property_class.list_box_modules.list_items[self.property_class.list_box_modules.conten_actual-1]
                        """if self.property_class.rect_up.collidepoint(position_mouse):
                            self.property_class.scroll()"""
                        if self.property_class.line_able:  # Permitir dibujar linea
                            self.property_class.hold_line = True
                        if self.property_class.drawing:  # Poner elemento
                            self.property_class.put_element()
                        if self.property_class.moving and self.property_class.move_inside:  # Redesplazar elemento
                            self.property_class.repos_element()
                        if self.property_class.check.recta.collidepoint(position_mouse):  # Para rotar cajitas
                            for container in self.property_class.elementos['containers']:
                                if container.selected:
                                    for caja in container.cajas:
                                        if caja.tag == self.property_class.elem_selected:
                                            caja.orientation = not caja.orientation
                                            self.property_class.check.push = caja.orientation
                                            for nodo in caja.nodos:
                                                container.nodos.remove(nodo)
                                            caja.calc_nodes()
                                            for nodo in caja.nodos:
                                                container.nodos.add(nodo)

                    elif pygame.mouse.get_pressed()[2]:  # Boton derecho
                        self.property_class.element_property(position_mouse)
                elif keys[K_ESCAPE]:  # Acciones al presionar tecla escape
                    position_mouse = self.property_class.cancel()
                    self.property_class.close_elements((0, 0), force=True)
                    self.property_class.box_field1.active = False
                    self.property_class.box_field2.active = False
            if timer != 0:  # Incremento del timer
                timer += dt
                if timer >= 0.5:  # Reinicio del timer
                    timer = 0
            abs_position = pygame.mouse.get_pos()
            self.screen_form.fill(GRAY)
            self.property_class.draw_containers(self.screen_form)
            self.property_class.draw_on_screen(self.screen_form, abs_position, position_mouse)
            self.property_class.exec_actions(self.screen_form, abs_position, position_mouse)  # Ejecutar acciones: Mover, borrar...
            if self.property_class.actions[6] or self.property_class.elem_proper or self.property_class.config_bit:  # Escribir nombre de pestañas
                self.property_class.draw_text(self.screen_form)
                self.property_class.draw = True
            if self.property_class.hold_line:  # Dibujando linea en caliente
                self.property_class.draw_line(self.screen_form)
            if self.property_class.element_moved != None:  # Mover elementos
                self.property_class.move_element(self.screen_form, abs_position)
                self.property_class.moving = True
            self.clock.tick(60)
            dt = self.clock.tick(30) / 1000  # Delta del timer
            pygame.display.flip()
