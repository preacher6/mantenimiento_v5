import os
import sys
import pygame
import pickle
import numpy as np
from textbox import *
from objects import *
from containers import *
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg


ACCEPTED_NUM = 'e-'+ string.digits
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)


class Property(pygame.sprite.Sprite):
    def __init__(self, workspace_size=(900, 520)):
        pygame.sprite.Sprite.__init__(self)
        self.load_pics()
        self.SIZE_WORKSPACE = workspace_size  # Tamaño del espacio de trabajo
        self.font = pygame.font.SysFont('Arial', 15)
        self.text_boxes()
        self.surfaces()
        self.cont = 1
        self.tag = 1
        self.drawing = False
        self.hold_caja = False
        self.hold_knn = False
        self.hold_stand = False
        self.hold_kdn = False
        self.hold_module = False
        self.elementos = {'containers': pygame.sprite.Group(),
                          'opciones': pygame.sprite.Group()}  # Inicializar diccionario de elementos}
        self.actions = [0] * 9
        self.checking_text = False  # Indica si se está usando algun campo de texto
        self.lista_text = None  # Elementos de texto a iterar
        self.draw = False  # Indica si se encuentra dibujando
        self.elem_proper = False  # Propiedades doble click izquierdo
        self.elem_type = False  # Propiedades click derecho
        self.elem_selected = None  # Etiqueta de elemento seleccionado (propiedad del elemento)
        self.put_position = (0, 0)
        self.text_status = [0]*5  # Estado de cajas de texto. 1. name, 2. alpha, 3. betha, 4. alpha y betha
        self.text_buttons = list()  # Lista de botones de texto
        self.init_properties()
        self.type_element = 1  # Indica el tipo de elemento. Si es 1 es caja, 2 es knn, 3 stand by
        self.line_able = False  # Indica si es posible empezar a construir conexion
        self.hold_line = False  # Permite dibujar linea
        self.init_pos = [0, 0]  # Posicion inicial de la linea
        self.end_line = [0, 0]  # Posicion final de la linea
        self.line_conections = []  # Almacena los puntos de la conexion que se está dibujando
        self.connecting = False  # Indica si se estan realizando conexiones
        self.elem1 = None  # Nombre del elemento inicial de una conexion
        self.elem2 = None  # Nombre del elemento final de una conexion
        self.duple_conection = list()  # Almacena cada punto inicial y final para una conexion que se este dibujando
        self.fig = plt.figure(figsize=[6, 4],  # En pulgadas                                                                       
                         dpi=100,  # 100 puntos por pulgada
                         tight_layout=True)
        self.element_moved = None  # Indica el elemento a desplazarse
        self.moving = False  # indica si se encuentra desplazando algun elemento
        self.draw_module = False  # Permite dibujar la caja de modulo
        self.elem_modulo = None
        self.module_lista = []
        self.module_names = []
        self.data_general = {}
        self.data_file = 'datos/data.txt'
        self.list_box_modules = ListBox(posi=(360, 230))
        self.config_bit = False
        self.time = True
        self.move_inside = False # Garantiza que lo que se este moviendo quede dentro del area de trabajo
        self.line_element = None  # Conexion a eliminar
        self.line_delete = False  # Disponible a eliminar conexion
        self.mensaje = MessageBox(position=(400, 240), text_position=(15, 30), button_position=[445, 320])  # Objeto para desplegar mensajes
        self.show_msg = False

    def init_properties(self):
        self.container = Container((self.pos_workspace[0],
                               self.pos_workspace[1] - 30), self.cont, self.tag)  # Primera pestaña
        self.elementos['containers'].add(self.container)  # Agregar pestaña a lista de pestañas (Dentro de diccionario)
        opciones = ['module', 'plot', 'play', 'config']  # Pestañas de opciones disponibles
        for elem, opcion in enumerate(opciones):
            active = True if elem == 0 else False  # Esta activa la pestaña si es la primera opcion
            position = (self.pos_workspace[0] - 30, self.pos_workspace[1])
            pestana_opcion = OptionPanels(opcion, position, elem, active=active)
            self.elementos['opciones'].add(pestana_opcion)

        self.rect_actions(self.pos_button_action)  # Inicializar rectas de las acciones
        self.rect_elements(self.pos_button_elements)  # Inicializar rectas de los elementos
        exp = TextButton('Exponencial', 'exp', position=(self.pos_proper[0]+116, self.pos_proper[1]+30), size=(72, 30))
        ray = TextButton('Rayleigh', 'ray', position=(self.pos_proper[0] + 116, self.pos_proper[1]+65), size=(72, 30),
                         text_position=(14, 5))
        wei = TextButton('Weibull', 'wei', position=(self.pos_proper[0] + 116, self.pos_proper[1] + 100), size=(72, 30),
                         text_position=(18, 5))
        self.text_buttons = [exp, ray, wei]
        self.check = CheckButton('Check', 'Rotar', position=(self.pos_proper[0]+15, self.pos_proper[1]+130))
        radio1_out = RadioButton('Radio1', 'Confiabilidad', position=(self.pos_plot[0] + 15, self.pos_plot[1] + 30),
                                 active=True)
        radio2_out = RadioButton('Radio2', 'Medida Importancia', position=(self.pos_plot[0] + 15, self.pos_plot[1] + 60))
        self.radio_out = [radio1_out, radio2_out]

    # --------------------------------- Relacionado a contenedores------------------------------------------

    def draw_containers(self, screen):
        """Dibujar pestañas"""
        for pestana in self.elementos['containers']:
            pestana.draw_cont(screen)

        self.container.draw_new(screen, self.cont)

        for option in self.elementos['opciones']:
            option.draw_option(screen)

    def add_container(self, new=True, old_container=None):
        """Añadir pestañas a la interfaz. Cada pestaña es un area de trabajo diferente"""
        existe = False
        if new:  # Indica si es un nuevo contenedor (no modulo)
            self.cont += 1  # Contador de pestañas
            self.tag += 1  # Etiqueta pestaña
            container_new = Container((self.pos_workspace[0], self.pos_workspace[1]-30), self.cont, self.tag)
            self.time_field.buffer = [str(container_new.time)]
        else:
            if old_container in self.elementos['containers']:  # Se evalua si el modulo esta abierto
                existe = True
            else:  # Si no esta dentro de la lista es porque esta cerrado, se abre
                self.cont += 1  # Contador de pestañas
                self.tag += 1  # Etiqueta pestaña
                container_new = old_container
                container_new.cont = self.cont
                container_new.tag = self.tag
                container_new.selected = True
        if not existe:  # Si es nuevo se crea y se añade al grupo de contenedores
            self.elementos['containers'].add(container_new)
            for container in self.elementos['containers']:  # Verifica cuales pestañas no estan seleccionad
                if self.cont != container.cont:
                    container.selected = False
        else:  # En caso que exista el viejo se activa la pestaña en que esté
            old_container.selected = True
            for container in self.elementos['containers']:  # Verifica cuales pestañas no estan seleccionad
                if container != old_container:
                    container.selected = False

    def delete_container(self, position):
        """Eliminar pestaña deseada"""
        if len(self.elementos['containers']) > 1:
            for container in self.elementos['containers']:
                if container.recta_close.collidepoint(position):
                    contador = container.cont
                    self.elementos['containers'].remove(container)
                    self.cont -= 1
                    not_in = False  # Permite seleccionar la ultima pestaña
                    for contain in self.elementos['containers']:  # En caso de eliminarse una se renombran las demas
                        print('contador', contador)
                        print(contain.cont)
                        if contain.cont > contador:
                            print('in')
                            contain.cont -= 1
                            if container.selected:
                                not_in = True
                                contain.selected = True
                                container.selected = False
                    if not not_in:
                        for contain in self.elementos['containers']:  # En caso de eliminarse una se renombran las demas
                            if contain.cont == len(self.elementos['containers']):
                                contain.selected = True
                            else:
                                contain.selected = False

        if len(self.elementos['containers']) == 1:
            for container in self.elementos['containers']:
                container.selected = True

    def select_container(self, position):
        """Seleccionar pestaña a activar"""
        for container in self.elementos['containers']:
            if container.rect.collidepoint(position):
                container.selected = True
                self.time_field.buffer = [str(container.time)]
                for contain in self.elementos['containers']:
                    if container.cont != contain.cont:
                        contain.selected = False

        if not 1 in self.text_status:  # Verifica que no haya ninguna textbox al aire antes de poder cambiar entre pantallas
            for option in self.elementos['opciones']:
                if option.rect.collidepoint(position):
                    option.active = True
                    for opt in self.elementos['opciones']:
                        if option.name != opt.name:
                            opt.active = False

    def draw_cont_elements(self, screen):
        """Dibujar elementos del contenedor seleccionado"""
        for contain in self.elementos['containers']:
            if contain.selected:
                contain.draw_elements(screen)
    # ---------------------------------------------------------------------------Fin containers
    # Acciones a realizar

    def check_actions(self, position):
        """Verificar que acción se va a realizar"""
        if self.connect_rect.collidepoint(position):  # conectar
            self.actions = [0] * 9
            self.actions[0] = 1
        if self.disconnect_rect.collidepoint(position):  # Desconectar
            self.actions = [0] * 9
            self.actions[1] = 1
        if self.move_rect.collidepoint(position):  # Mover
            self.actions = [0]*9
            self.actions[2] = 1
        if self.delete_rect.collidepoint(position):  # Eliminar
            self.actions = [0] * 9
            self.actions[3] = 1
        if self.export_rect.collidepoint(position):  # Exportar
            self.actions = [0] * 9
            # Verificar si es posible importar, o sea, todo está bien conectado
            for container in self.elementos['containers']:
                if container.selected:
                    if container.all_connected:
                        self.actions[4] = 1
                    else:
                        self.show_msg = True
                        self.mensaje.text = 'Hay elementos desconectados'

        if self.import_rect.collidepoint(position):  # Importar
            self.actions = [0] * 9
            # Preguntar si existen elementos a importar, o sea, si existen modulos
            if self.module_lista:
                self.actions[5] = 1
            else:
                self.show_msg = True
                self.mensaje.text = 'No existen módulos'
        if self.rename_rect.collidepoint(position):
            self.actions = [0]*9
            self.actions[6] = 1

    @staticmethod
    def round_posit(position, base=20):
        """Determinar posicion dentro de las reticulas"""
        posx = base*round(position[0]/base)-10
        posy = base*round(position[1]/base)
        new_pos = (posx, posy)
        return new_pos

    def draw_line(self, screen):
        pygame.draw.aaline(screen, BLACK, self.init_pos, self.end_line)
        for linea in self.duple_conection:
            pygame.draw.aaline(screen, BLACK, linea[0], linea[1])
        self.connecting = True

    def connect_nodes(self):
        for container in self.elementos['containers']:
            if container.selected:
                container.connections.add()

    def exec_actions(self, screen, position, abs_position):
        """Ejecutar las acciones"""
        if self.actions[0]:  # Connect
            #print('conectar')
            pygame.mouse.set_visible(False)
            valid_workspace = pygame.Rect(self.pos_workspace[0], self.pos_workspace[1],
                                          self.SIZE_WORKSPACE[0], self.SIZE_WORKSPACE[1])
            new_position = (position[0], position[1])
            if valid_workspace.collidepoint(new_position):
                put_position = self.round_posit(new_position)
                self.end_line = (put_position[0]+10, put_position[1]+10)
                for container in self.elementos['containers']:
                    if container.selected:
                        for nodo in container.nodos:
                            if nodo.rect.collidepoint((put_position[0]+10, put_position[1]+10)):
                                screen.blit(self.line_on, put_position)
                                self.line_able = True
                                if not self.hold_line:  # Define la posicion inicial de una conexion
                                    self.init_pos = (put_position[0]+10, put_position[1]+10)
                                    self.elem1 = nodo
                                break
                            else:
                                self.line_able = False
                                screen.blit(self.line_off, put_position)

            else:
                screen.blit(self.line_off, new_position)
        elif self.actions[1]:
            pygame.mouse.set_visible(False)
            new_position = (position[0] - 15, position[1] - 15)
            self.delete_line_rect.x = position[0] - 15
            self.delete_line_rect.y = position[1] - 15
            screen.blit(self.delete_line, new_position)
            for container in self.elementos['containers']:
                if container.selected:
                    for conexion in container.conections:
                        for tramo in conexion.puntos_internos:
                            if self.delete_line_rect.collidepoint(tramo):
                                self.line_element = conexion
                                self.line_delete = True

        elif self.actions[2]:  # Desplazar elementos
            pygame.mouse.set_visible(False)
            new_position = (position[0]-15, position[1]-15)
            screen.blit(self.move_n, new_position)
            for container in self.elementos['containers']:
                if container.selected:
                    for caja in container.cajas:
                        if caja.rect.collidepoint(abs_position):
                            disconect = True  # Indica si el elemento tiene conexiones
                            for nodo in caja.nodos:
                                for key in container.keys:  # Remover elemento de lista de conexiones nodales
                                    if nodo in container.nodos_sistema[key]:
                                        disconect = False
                                        break
                            if disconect:
                                self.element_moved = caja.tag
                            else:
                                pygame.mouse.set_visible(True)
                                self.show_msg = True
                                self.mensaje.text = 'El elemento debe estar desconectado'
                    for paralelo in container.knn:
                        if paralelo.rect.collidepoint(abs_position):
                            self.element_moved = paralelo.tag
        elif self.actions[3]:
            pygame.mouse.set_visible(False)
            new_position = (position[0] - 15, position[1] - 15)
            screen.blit(self.delete_n, new_position)
        elif self.actions[4]:  # Exportar modulo
            for container in self.elementos['containers']:
                if container.selected:
                    if container.name not in self.module_names:
                        if container.all_connected:
                            self.module_lista.append(container)
                            self.module_names.append(container.name)
                            self.data_general = {'modulos': self.module_lista, 'nombres': self.module_names}
                            self.list_box_modules.add_data(container)
                            self.cancel()
                            break
        elif self.actions[5]:  # Importar modulo
            self.list_box_modules.consult_position(abs_position)
            self.list_box_modules.draw_mod(screen)
            if self.list_box_modules.accept.recta.collidepoint(position):
                self.list_box_modules.accept.over = True
            else:
                self.list_box_modules.accept.over = False
        elif self.actions[6]:  # Dar nombre a pestaña
            self.text_status[0] = 1  # Activa name text
            self.name.active = True
            self.name_surface(screen, position)  # Dibuja la superficie
            if self.ok_rect.collidepoint(abs_position):  # Si se presiona sobre ok
                for container in self.elementos['containers']:
                    if container.selected == True:
                        container.name = "".join(self.name.buffer)
                self.name.buffer = [""]  # Reinicia el buffer
                self.actions[6] = 0  # Cierra ventana name

    def element_property(self, pushed, proper=0):  # Acciones de doble click
        """Propiedad de un elemento
        Coloca en la ventana de doble click los valores del elementos seleccionado
        """
        for container in self.elementos['containers']:
            if container.selected:
                for caja in container.cajas:
                    if caja.rect.collidepoint(pushed):
                        self.elem_selected = caja.tag  # Coloca el nombre de la caja en la caja de texto del elemento seleccionado
                        self.type_element = 1
                        if not proper:
                            self.elem_type = True
                        else:
                            self.elem_proper = True
                for knn_ind in container.knn:
                    for set_box in knn_ind.cols:
                        for caja in set_box:
                            if caja.rect.collidepoint(pushed):
                                self.type_element = 1
                                self.elem_selected = caja.tag
                                if not proper:  # Indica si no es click izquierdo
                                    self.elem_type = True
                                else:
                                    self.elem_proper = True
                    if knn_ind.rect.collidepoint(pushed):
                        self.type_element = 2
                        self.elem_selected = knn_ind.tag
                        if not proper:
                            self.elem_type = True
                        else:
                            self.elem_proper = True

                for stand_ind in container.stand:
                    for caja in stand_ind.cajas:
                        if caja.rect.collidepoint(pushed):
                            self.type_element = 1
                            self.elem_selected = caja.tag
                            if not proper:
                                self.elem_type = True
                            else:
                                self.elem_proper = True
                    if stand_ind.rect.collidepoint(pushed):
                        self.type_element = 3
                        self.elem_selected = stand_ind.tag
                        if not proper:
                            self.elem_type = True
                        else:
                            self.elem_proper = True

                for kdn in container.kdn:
                    for caja in kdn.cajas:
                        if caja.rect.collidepoint(pushed):
                            self.type_element = 1
                            self.elem_selected = caja.tag
                            if not proper:
                                self.elem_type = True
                            else:
                                self.elem_proper = True
                    if kdn.rect.collidepoint(pushed):
                        self.type_element = 4
                        self.elem_selected = kdn.tag
                        if not proper:
                            self.elem_type = True
                        else:
                            self.elem_proper = True

                for module in container.module:
                    if module.rect.collidepoint(pushed):
                        self.add_container(new=False, old_container=module.container)

    def add_red_elements(self, push_position):
        """Agregar o quitar paralelos a un knn"""
        if self.elem_type:
            if self.type_element == 2:
                for container in self.elementos['containers']:
                    if container.selected:
                        for knn_ind in container.knn:
                            if self.addline_rect.collidepoint(push_position):  # Adicionar paralelo
                                if knn_ind.num_rows < 5:
                                    if knn_ind.tag == self.elem_selected:
                                        caja = Caja(
                                            (knn_ind.pos[0] + 20, knn_ind.pos[1] + knn_ind.num_rows * knn_ind.dt)
                                            , 1, name=knn_ind.tag + "_" + str(knn_ind.num_rows))
                                        hit = pygame.sprite.spritecollide(caja, container.real_items,
                                                                          False)  # Verifica si no colisiona sobre otro elemento
                                        if not hit:
                                            container.real_items.add(caja)
                                            for nodo in container.nodos:
                                                if nodo.name_element == self.elem_selected:
                                                    container.nodos.remove(nodo)
                                            knn_ind.cols[knn_ind.num_rows].add(caja)
                                            container.list_box.add_data(caja)  # Agregar item a list box
                                            knn_ind.num_rows += 1
                                            knn_ind.calc_lines()
                                            knn_ind.calc_nodes()
                                            for nodo in knn_ind.nodos:
                                                container.nodos.add(nodo)
                                        else:
                                            self.show_msg = True
                                            self.mensaje.text = 'Colisión'

                            if self.reduceline_rect.collidepoint(push_position):  # Eliminar paralelo
                                if knn_ind.num_rows > 2:
                                    if knn_ind.tag == self.elem_selected:
                                        for nodo in container.nodos:
                                            if nodo.name_element == self.elem_selected:
                                                container.nodos.remove(nodo)
                                        for caja in knn_ind.cols[knn_ind.num_rows - 1]:  # Remueve elementos que son reducidos del paralelo
                                            container.real_items.remove(caja)
                                        knn_ind.cols[knn_ind.num_rows - 1] = pygame.sprite.Group()
                                        knn_ind.num_rows -= 1
                                        knn_ind.calc_lines()
                                        knn_ind.calc_nodes()
                                        for nodo in knn_ind.nodos:
                                            container.nodos.add(nodo)

                            for ind, recta in enumerate(self.rects_knn_add):  # Adicionar serie
                                if recta.collidepoint(push_position):
                                    if knn_ind.tag == self.elem_selected:
                                        if len(knn_ind.cols[ind]) < 7:
                                            caja = Caja((knn_ind.pos[0] + 20+knn_ind.dt*len(knn_ind.cols[ind]),
                                                                        knn_ind.pos[1] + ind * knn_ind.dt),
                                                                        len(knn_ind.cols[ind])+1,
                                                                        name=knn_ind.tag + "_" + str(ind))
                                            hit = pygame.sprite.spritecollide(caja, container.real_items,
                                                                              False)  # Verifica si no colisiona sobre otro elemento
                                            if not hit:
                                                container.real_items.add(caja)
                                                knn_ind.cols[ind].add(caja)
                                                for nodo in container.nodos:
                                                    if nodo.name_element == self.elem_selected:
                                                        container.nodos.remove(nodo)
                                                knn_ind.calc_lines()
                                                knn_ind.calc_nodes()
                                                for nodo in knn_ind.nodos:
                                                    container.nodos.add(nodo)
                                                container.list_box.add_data(caja)

                            for ind, recta in enumerate(self.rects_knn_reduce):  # Eliminar serie
                                if recta.collidepoint(push_position):
                                    if knn_ind.tag == self.elem_selected:
                                        if len(knn_ind.cols[ind]) > 1:
                                            for caja in knn_ind.cols[ind]:
                                                if caja.id == len(knn_ind.cols[ind]):
                                                    container.real_items.remove(caja)
                                                    knn_ind.cols[ind].remove(caja)
                                                    for nodo in container.nodos:
                                                        if nodo.name_element == self.elem_selected:
                                                            container.nodos.remove(nodo)
                                                    knn_ind.calc_lines()
                                                    knn_ind.calc_nodes()
                                                    for nodo in knn_ind.nodos:
                                                        container.nodos.add(nodo)

            elif self.type_element == 3:
                for container in self.elementos['containers']:
                    if container.selected:
                        for stand_ini in container.stand:
                            if self.addline_rect.collidepoint(push_position):  # Adicionar paralelo
                                if stand_ini.num_elements < 5:
                                    if stand_ini.tag == self.elem_selected:
                                        stand_ini.num_elements += 1

                            if self.reduceline_rect.collidepoint(push_position):  # Eliminar elemento
                                if stand_ini.num_elements > 2:
                                    if stand_ini.tag == self.elem_selected:
                                        stand_ini.num_elements -= 1

            elif self.type_element == 4:
                for container in self.elementos['containers']:
                    if container.selected:
                        for kdn in container.kdn:
                            if self.addline_rect_kdn.collidepoint(push_position):  # Adicionar linea
                                if kdn.num_rows < 10:
                                    if kdn.tag == self.elem_selected:
                                        kdn.num_rows+=1
                            if self.reduceline_rect_kdn.collidepoint(push_position):  # Adicionar linea
                                if kdn.num_rows > kdn.num_active:
                                    if kdn.tag == self.elem_selected:
                                        kdn.num_rows-=1

                            if self.addline_rect_kdn2.collidepoint(push_position):  # Adicionar linea
                                if kdn.num_active < kdn.num_rows:
                                    if kdn.tag == self.elem_selected:
                                        kdn.num_active+=1
                            if self.reduceline_rect_kdn2.collidepoint(push_position):  # Adicionar linea
                                if kdn.num_active <= kdn.num_rows and kdn.num_active>1:
                                    if kdn.tag == self.elem_selected:
                                        kdn.num_active-=1

    def move_element(self, screen, position):
        position = self.round_pos(position)
        for container in self.elementos['containers']:
            if container.selected:
                for caja in container.cajas:
                    if caja.tag == self.element_moved:
                        valid_workspace = pygame.Rect(self.pos_workspace[0], self.pos_workspace[1],
                                                      self.SIZE_WORKSPACE[0] - 180, self.SIZE_WORKSPACE[1] - 80)
                        self.move_inside_work(screen, position, caja.rect, valid_workspace)
                        for nodo in caja.nodos:
                            container.nodos.remove(nodo)
                        caja.rect.x = position[0]
                        caja.rect.y = position[1]
                        caja.pos = position
                        caja.calc_nodes()
                for paralelo in container.knn:
                    if paralelo.tag == self.element_moved:
                        valid_workspace = pygame.Rect(self.pos_workspace[0], self.pos_workspace[1],
                                                      self.SIZE_WORKSPACE[0] - 200, self.SIZE_WORKSPACE[1] - 180)
                        self.move_inside_work(screen, position, paralelo.rect, valid_workspace)
                        for nodo in paralelo.nodos:
                            container.nodos.remove(nodo)
                        paralelo.rect.x = position[0]-20
                        paralelo.rect.y = position[1]-20
                        paralelo.pos = [position[0]-20, position[1]-20]
                        for index, set_caja in enumerate(paralelo.cols):
                            for caja in set_caja:
                                caja.rect.x = position[0]
                                caja.rect.y = position[1]+index*paralelo.dt
                                caja.pos = [position[0], position[1]+index*paralelo.dt]

                        paralelo.calc_nodes()
                        #paralelo.calc_lines()

    def move_inside_work(self, screen, position, elemento, space):
        """Funcion para definir la manera en q se ubica el elemento dependiendo de donde se encuentre"""
        if space.collidepoint(position):
            self.move_inside = True
            print('in')
            self.put_position = self.round_pos(position)
        else:
            self.move_inside = False
            print('out')

    def repos_element(self):  # Reposicionar elemento
        for container in self.elementos['containers']:
            if container.selected:
                for caja in container.cajas:
                    if caja.tag == self.element_moved:
                        for nodo in caja.nodos:
                            container.nodos.add(nodo)
                        self.cancel()

    def delete_element(self, position):  # Elimina el elemento seleccionado
        for container in self.elementos['containers']:
            if container.selected:
                for caja in container.cajas:
                    if caja.rect.collidepoint(position):
                        container.cont_cajas -= 1
                        container.list_box.del_data(caja)
                        for nodo in caja.nodos:
                            for key in container.keys:  # Remover elemento de lista de conexiones nodales
                                if nodo in container.nodos_sistema[key]:
                                    container.nodos_sistema[key].remove(nodo)
                            container.nodos.remove(nodo)  # Remover nodo de lista de nodos del contenedor
                        container.cajas.remove(caja)
                        container.own_items.remove(caja.tag)
                        container.items.remove(caja)
                        container.real_items.remove(caja)
                for paralelo in container.knn:
                    if paralelo.rect.collidepoint(position):
                        container.cont_knn -= 1
                        for col in paralelo.cols:
                            for caja in col:
                                container.list_box.del_data(caja)
                                container.real_items.remove(caja)
                        container.list_box.del_data(paralelo)
                        for nodo in paralelo.nodos:
                            for key in container.keys:  # Remover elemento de lista de conexiones nodales
                                if nodo in container.nodos_sistema[key]:
                                    container.nodos_sistema[key].remove(nodo)
                            container.nodos.remove(nodo)
                        container.real_items.remove(paralelo)
                        container.knn.remove(paralelo)
                        container.own_items.remove(paralelo.tag)
                        container.items.remove(paralelo)
                for stand in container.stand:
                    if stand.rect.collidepoint(position):
                        container.cont_stand -= 1
                        container.list_box.del_data(stand)
                        for caja in stand.cajas:
                            container.real_items.remove(caja)
                        for nodo in stand.nodos:
                            for key in container.keys:  # Remover elemento de lista de conexiones nodales
                                if nodo in container.nodos_sistema[key]:
                                    container.nodos_sistema[key].remove(nodo)
                            container.nodos.remove(nodo)
                        container.real_items.remove(stand)
                        container.stand.remove(stand)
                        container.own_items.remove(stand.tag)
                        container.items.remove(stand)
                for kdn in container.kdn:
                    if kdn.rect.collidepoint(position):
                        container.cont_kdn -= 1
                        container.list_box.del_data(kdn)
                        for caja in kdn.cajas:
                            container.real_items.remove(caja)
                        for nodo in kdn.nodos:
                            for key in container.keys:  # Remover elemento de lista de conexiones nodales
                                if nodo in container.nodos_sistema[key]:
                                    container.nodos_sistema[key].remove(nodo)
                            container.nodos.remove(nodo)
                        container.real_items.remove(kdn)
                        container.real_items.remove(kdn)
                        container.kdn.remove(kdn)
                        container.own_items.remove(kdn.tag)
                        container.items.remove(kdn)

                for conexion in container.conections:
                    if conexion.elem1 in container.nodos and conexion.elem2 in container.nodos:
                        pass
                    else:
                        container.conections.remove(conexion)
                        for nodo in container.nodos:
                            nodo.connected = False

    def delete_line_elements(self, elemento):
        for container in self.elementos['containers']:
            if container.selected:
                for caja in container.cajas:
                    print(elemento.tag)
                    if caja.tag == elemento.tag:
                        container.cont_cajas -= 1
                        container.list_box.del_data(caja)
                        for nodo in caja.nodos:
                            for key in container.keys:  # Remover elemento de lista de conexiones nodales
                                if nodo in container.nodos_sistema[key]:
                                    container.nodos_sistema[key].remove(nodo)
                            container.nodos.remove(nodo)  # Remover nodo de lista de nodos del contenedor
                        container.cajas.remove(caja)
                        container.own_items.remove(caja.tag)
                        container.items.remove(caja)
                        container.real_items.remove(caja)

                for conexion in container.conections:
                    if conexion.elem1 in container.nodos and conexion.elem2 in container.nodos:
                        pass
                    else:
                        container.conections.remove(conexion)
                        for nodo in container.nodos:
                            nodo.connected = False

    def build_rect_points(self, puntos, num_points=20):  # Funcion recta. Construye los puntos de la recta para cada linea de una conexion
        x1, y1 = puntos[0]
        x2, y2 = puntos[1]
        x_spacing = (x2-x1)/(num_points+1)
        y_spacing = (y2 - y1) / (num_points + 1)
        return [[x1+i*x_spacing, y1+i*y_spacing] for i in range(1, num_points+1)]


    def close_elements(self, position, force=False):
        if self.close_name_rect.collidepoint(position) or force:
            self.actions = [0]*9
            self.draw = False
            self.elem_type = False
            self.elem_proper = False
            self.name.buffer = [""]
            self.line_element = None
            self.line_delete = False

    # --------------Relacionado al texto--------------------------
    def text_boxes(self):
        """Cajas de texto disponibles"""
        self.name = TextBox((410, 230, 140, 20), id="name_con", active=True,
                            clear_on_enter=False, inactive_on_enter=True)
        self.name_element = TextBox((485, 220, 100, 20), id="name_con", active=True,
                                    clear_on_enter=False, inactive_on_enter=True)
        self.box_field1 = TextBox((485, 250, 100, 20), acepted=ACCEPTED_NUM, id="name_con", active=False,
                                  clear_on_enter=False, inactive_on_enter=True)
        self.box_field2 = TextBox((485, 280, 100, 20), acepted=ACCEPTED_NUM, id="name_con", active=False,
                                  clear_on_enter=False, inactive_on_enter=True)
        self.time_field = TextBox((150, 260, 100, 20), acepted=ACCEPTED_NUM, id="name_con", active=True,
                                  clear_on_enter=False, inactive_on_enter=True)

    def check_text(self, event):
        if self.text_status[0] == 1:
            self.name.get_event(event)
        elif self.text_status[1] == 1:
            self.name_element.get_event(event)
            self.box_field1.get_event(event)
        elif self.text_status[2] == 1:
            self.name_element.get_event(event)
            self.box_field1.get_event(event)
        elif self.text_status[3] == 1:
            self.name_element.get_event(event)
            self.box_field1.get_event(event)
            self.box_field2.get_event(event)
        elif self.text_status[4] == 1:
            self.name_element.get_event(event)
        if self.config_bit:
            self.time_field.get_event(event)

    def draw_text(self, screen):
        if self.text_status[0] == 1:
            self.name.update()
            self.name.draw(screen)
        elif self.text_status[1] == 1:
            self.name_element.update()
            self.name_element.draw(screen)
            self.box_field1.color = WHITE
            self.box_field1.update()
            self.box_field1.draw(screen)
            self.box_field2.active = False
            self.box_field2.color = GRAY
            self.box_field2.update()
            self.box_field2.draw(screen)
        elif self.text_status[2] == 1:
            self.name_element.update()
            self.name_element.draw(screen)
            self.box_field1.update()
            self.box_field1.draw(screen)
            self.box_field1.color = WHITE
            self.box_field2.active = False
            self.box_field2.update()
            self.box_field2.color = GRAY
            self.box_field2.draw(screen)
        elif self.text_status[3] == 1:
            self.name_element.update()
            self.name_element.draw(screen)
            self.box_field1.update()
            self.box_field1.draw(screen)
            self.box_field2.update()
            self.box_field2.draw(screen)
            self.box_field1.color = pygame.Color("white")
            self.box_field2.color = pygame.Color("white")
        elif self.text_status[4] == 1:
            self.name_element.update()
            self.name_element.draw(screen)

    # ------------------------------------------------------------

    # -------------- Dibujar sobre la superficie--------------------
    def draw_selected(self, screen, position, pushed):
        """Dibuja sobre la interfaz el elemento seleccionado"""
        if self.caja_mini_rect.collidepoint(pushed) or self.hold_caja:
            self.hold_caja = True
            valid_workspace = pygame.Rect(self.pos_workspace[0], self.pos_workspace[1],
                                          self.SIZE_WORKSPACE[0] - 180, self.SIZE_WORKSPACE[1] - 80)
            elemento = self.caja
            self.title = 'caja'
            self.draw_inside_work(screen, position, elemento, valid_workspace)
        elif self.knn_mini_rect.collidepoint(pushed) or self.hold_knn:
            self.hold_knn = True
            valid_workspace = pygame.Rect(self.pos_workspace[0], self.pos_workspace[1],
                                          self.SIZE_WORKSPACE[0] - 200, self.SIZE_WORKSPACE[1] - 180)
            elemento = self.knn
            self.title = 'knn'
            self.draw_inside_work(screen, position, elemento, valid_workspace)
        elif self.stand_mini_rect.collidepoint(pushed) or self.hold_stand:
            self.hold_stand = True
            valid_workspace = pygame.Rect(self.pos_workspace[0], self.pos_workspace[1],
                                          self.SIZE_WORKSPACE[0] - 200, self.SIZE_WORKSPACE[1] - 180)
            elemento = self.stand
            self.title = 'stand'
            self.draw_inside_work(screen, position, elemento, valid_workspace)
        elif self.kdn_mini_rect.collidepoint(pushed) or self.hold_kdn:
            self.hold_kdn = True
            valid_workspace = pygame.Rect(self.pos_workspace[0], self.pos_workspace[1],
                                          self.SIZE_WORKSPACE[0] - 200, self.SIZE_WORKSPACE[1] - 180)
            elemento = self.kdn
            self.title = 'kdn'
            self.draw_inside_work(screen, position, elemento, valid_workspace)
        elif self.draw_module or self.hold_module:
            self.hold_module = True
            valid_workspace = pygame.Rect(self.pos_workspace[0], self.pos_workspace[1],
                                          self.SIZE_WORKSPACE[0] - 200, self.SIZE_WORKSPACE[1] - 180)
            elemento = self.module
            self.title = 'module'
            self.actions = [0]*9
            self.draw_inside_work(screen, position, elemento, valid_workspace)

    def draw_inside_work(self, screen, position, elemento, space):
        """Funcion para definir la manera en q se ubica el elemento dependiendo de donde se encuentre"""
        if space.collidepoint(position):
            self.drawing = True
            self.put_position = self.round_pos(position)
            screen.blit(elemento, self.put_position)
        else:
            self.drawing = False
            screen.blit(elemento, position)

    @staticmethod
    def round_pos(position, base=20):
        """Determinar posicion dentro de las reticulas"""
        posx = base*round(position[0]/base)+1
        posy = base*round(position[1]/base)-9
        new_pos = (posx, posy)
        return new_pos

    def put_element(self):
        """Poner elemento sobre el area de trabajo (contenedor)"""
        if self.hold_caja:
            for container in self.elementos['containers']:
                if container.selected:
                    container.cont_cajas += 1
                    container.all_cajas += 1
                    caja = Caja(self.put_position, container.all_cajas)
                    hit = pygame.sprite.spritecollide(caja, container.real_items, False)  # Verifica si no colisiona sobre otro elemento
                    if not hit:
                        container.list_box.add_data(caja)
                        for nodo in caja.nodos:
                            container.nodos.add(nodo)
                        container.cajas.add(caja)
                        container.own_items.append(caja.tag)
                        container.items.add(caja)
                        container.real_items.add(caja)
                    else:
                        container.cont_cajas -= 1
                        container.all_cajas -= 1
        elif self.hold_knn:
            for container in self.elementos['containers']:
                if container.selected:
                    container.cont_knn += 1
                    container.all_knn += 1
                    knn = Knn(self.put_position, container.all_knn)
                    colision = False
                    for col in knn.cols:
                        for caja in col:
                            hit = pygame.sprite.spritecollide(caja, container.real_items,
                                                              False)  # Verifica si no colisiona sobre otro elemento
                            if hit:
                                colision = True
                                break
                    if not colision:  # Si ninguna de las cajas del paralelo colisiona entonces sea crea
                        for col in knn.cols:
                            for caja in col:
                                container.list_box.add_data(caja)
                                container.real_items.add(caja)
                        container.list_box.add_data(knn)
                        container.real_items.add(knn)
                        for nodo in knn.nodos:
                            container.nodos.add(nodo)
                        container.knn.add(knn)
                        container.own_items.append(knn.tag)
                        container.items.add(knn)
                    else:
                        container.cont_knn -= 1
                        container.all_knn -= 1
        elif self.hold_stand:
            for container in self.elementos['containers']:
                if container.selected:
                    container.cont_stand += 1
                    container.all_stand += 1
                    stand = Stand(self.put_position, container.all_stand)
                    colision = False
                    hit_stand = pygame.sprite.spritecollide(stand, container.real_items,
                                                False)  # Verifica si no colisiona sobre otro elemento
                    if hit_stand:
                        colision = True
                    for caja in stand.cajas:
                        hit = pygame.sprite.spritecollide(caja, container.real_items,
                                                          False)  # Verifica si no colisiona sobre otro elemento
                        if hit:
                            colision = True
                            break
                    if not colision:
                        for nodo in stand.nodos:
                            container.nodos.add(nodo)
                        for caja in stand.cajas:
                            container.real_items.add(caja)
                        container.real_items.add(stand)
                        container.list_box.add_data(stand)
                        container.stand.add(stand)
                        container.own_items.append(stand.tag)
                        container.items.add(stand)
                    else:
                        container.cont_stand -= 1
                        container.all_stand -= 1
        elif self.hold_kdn:
            for container in self.elementos['containers']:
                if container.selected:
                    container.cont_kdn += 1
                    container.all_kdn += 1
                    kdn = Kdn(self.put_position, container.all_kdn)
                    hit_kdn = pygame.sprite.spritecollide(kdn, container.real_items,
                                                            False)  # Verifica si no colisiona sobre otro elemento
                    colision = False
                    if hit_kdn:
                        colision = True
                    for caja in kdn.cajas:
                        hit = pygame.sprite.spritecollide(caja, container.real_items,
                                                          False)  # Verifica si no colisiona sobre otro elemento
                        if hit:
                            colision = True
                            break
                    if not colision:
                        for nodo in kdn.nodos:
                            container.nodos.add(nodo)
                        for caja in kdn.cajas:
                            container.real_items.add(caja)
                        container.real_items.add(kdn)
                        container.list_box.add_data(kdn)
                        container.kdn.add(kdn)
                        container.own_items.append(kdn.tag)
                        container.items.add(kdn)
                    else:
                        container.cont_kdn -= 1
                        container.all_kdn -= 1
        elif self.hold_module:
            for container in self.elementos['containers']:
                if container.selected:
                    container.all_module += 1
                    module = Module(self.put_position, container.all_module, self.elem_modulo.plot_all, self.elem_modulo,
                                    self.elem_modulo.func_sym, name=self.elem_modulo.name)
                    for nodo in module.nodos:
                        container.nodos.add(nodo)
                    container.list_box.add_data(module)
                    container.module.add(module)
                    container.own_items.append(module.tag)
                    container.items.add(module)

    def draw_grid(self, screen, screen_pos):
        """Dibujar rejilla"""
        iter_fila = screen_pos[1]
        for fila in range(25):
            iter_fila += 20
            iter_col = screen_pos[0]
            for columna in range(44):
                iter_col += 20
                pos_circle = (iter_col, iter_fila)
                screen.blit(self.grid, pos_circle)

    def draw_plot(self):
        pass

    def draw_on_screen(self, screen, position, push_position):  # Aca se dibujan la mayoria de acciones realizadas
        """Dibujar estructuras del sistema en pantalla"""
        screen.blit(self.button_act_panel, self.pos_button_action)
        screen.blit(self.button_ele_panel, self.pos_button_elements)
        #screen.blit(self.button_info, self.pos_info_buttons)
        screen.blit(self.workspace, self.pos_workspace)
        self.draw_elements(screen)
        for elemento in self.elementos['opciones']:
            if elemento.name == 'module':
                self.config_bit = False
                if elemento.active:
                    self.draw_grid(screen, self.pos_workspace)
                    self.draw_cont_elements(screen)
                    self.draw_selected(screen, position, push_position)
                if self.elem_proper:  # Dibujar panel de propiedades
                    self.proper_surface(screen, position)
                    if self.ok_rect2.collidepoint(push_position):  # Si se presiona sobre ok
                        for container in self.elementos['containers']:
                            if container.selected:  # Agregar nombre a cajas
                                nombre = "".join(self.name_element.buffer)
                                buffer1 = "".join(self.box_field1.buffer)
                                buffer2 = "".join(self.box_field2.buffer)
                                if nombre not in container.own_items or nombre==self.elem_selected:  # Verifica que no sea nombre repetido. A menos que sea el de si mismo
                                    if not 'Caja_' in nombre or nombre==self.elem_selected:  # Verifica que no sea el nombre del sistema. A menos que sea el de si mismo
                                        try:  # Verifica que los datos númericos sean validos
                                            if (isinstance(eval(buffer1), float) or isinstance(eval(buffer2), int)) \
                                                    and (isinstance(eval(buffer2), float) or isinstance(eval(buffer2), int)):
                                                for caja in container.cajas:
                                                    if caja.tag == self.elem_selected:
                                                        if nombre and buffer1 and buffer2:
                                                            for item in container.items:
                                                                if item.tag==caja.tag:
                                                                    item.tag = "".join(self.name_element.buffer)
                                                            caja.tag = "".join(self.name_element.buffer)
                                                            caja.alpha = "".join(self.box_field1.buffer)
                                                            caja.betha = "".join(self.box_field2.buffer)
                                                            self.elem_proper = False
                                                            self.text_status = [0]*5
                                                        else:
                                                            self.show_msg = True
                                                            self.mensaje.text = 'Todos los campos deben estar llenos'

                                                for knn_ind in container.knn:
                                                    if knn_ind.tag == self.elem_selected:
                                                        if nombre:  # Verificar si el nombre no está vacío
                                                            knn_ind.tag = "".join(self.name_element.buffer)
                                                    for set_boxes in knn_ind.cols:
                                                        for caja in set_boxes:
                                                            if caja.tag == self.elem_selected:
                                                                if nombre and buffer1 and buffer2:
                                                                    caja.tag = "".join(self.name_element.buffer)
                                                                    caja.alpha = "".join(self.box_field1.buffer)
                                                                    caja.betha = "".join(self.box_field2.buffer)
                                                                    self.elem_proper = False
                                                for stand_ind in container.stand:
                                                    for caja in stand_ind.cajas:
                                                        if caja.tag == self.elem_selected:
                                                            if nombre and buffer1 and buffer2:
                                                                caja.tag = "".join(self.name_element.buffer)
                                                                caja.alpha = "".join(self.box_field1.buffer)
                                                                caja.betha = "".join(self.box_field2.buffer)
                                                                self.elem_proper = False
                                                for kdn in container.kdn:
                                                    if kdn.tag == self.elem_selected:
                                                        if nombre and buffer1 and buffer2:
                                                            kdn.tag == "".join(self.name_element.buffer)
                                                            kdn.alpha = "".join(self.box_field1.buffer)
                                                            kdn.betha = "".join(self.box_field2.buffer)
                                                            self.elem_proper = False
                                            else:
                                                self.show_msg = True
                                                self.mensaje.text = 'Los valores deben ser númericos'
                                        except:
                                            self.show_msg = True
                                            self.mensaje.text = 'Ingrese un dato valido'
                                    else:
                                        self.show_msg = True
                                        self.mensaje.text = 'Nombre reservado por el sistema'
                                else:
                                    self.show_msg = True
                                    self.mensaje.text = 'Nombre ya existente'

                    if self.ok_rect.collidepoint(push_position):  # Si se presiona sobre ok
                        for container in self.elementos['containers']:
                            if container.selected:
                                for knn in container.knn:
                                    if knn.tag == self.elem_selected:
                                        if nombre:
                                            knn.tag = "".join(self.name_element.buffer)
                                            self.elem_proper = False
                if self.elem_type:
                    self.type_surface(screen, position, push_position)

            elif elemento.name == 'plot':
                if elemento.active:
                    for container in self.elementos['containers']:
                        if container.selected:
                            if len(container.list_box.list_items) > 0:
                                screen.blit(self.plot_surface, self.pos_plot)
                                t = container.time
                                container.list_box.draw(screen, t)
                                container.list_box.consult_position(push_position)
                                screen.blit(self.canvas_space(self.fig), (310, 240))
                            else:
                                elemento.active = False
                                for elem in self.elementos['opciones']:
                                    if elem.name == 'module':
                                        elem.active = True

            elif elemento.name == 'play':
                if elemento.active:
                    for container in self.elementos['containers']:
                        if container.selected:
                            if container.all_connected:
                                screen.blit(self.plot_surface, self.pos_plot)
                                container.system_plot()
                                screen.blit(self.canvas_space(self.fig), (310, 240))
                                t = container.time
                                screen.blit(self.font.render('La confiabilidad del sistema es: '+str(round(eval(container.plot_all)*100,3))+'%' , True, (0, 0, 0)), (80, 300))
                                screen.blit(self.font.render('La inconfiabilidad del sistema es: ' + str(
                                    round((1-eval(container.plot_all)) * 100, 3)) + '%', True, (0, 0, 0)), (80, 330))
                                for radio in self.radio_out:
                                    radio.draw(screen)
                                    if len(container.items) > 3:
                                        if radio.recta.collidepoint(push_position):
                                            radio.push = True
                                            if radio.name == 'Radio1':
                                                container.type_plot = 1
                                            else:
                                                container.type_plot = 0
                                            for otro_radio in self.radio_out:
                                                if otro_radio.name != radio.name:
                                                    otro_radio.push = False
                            else:
                                elemento.active = False
                                for elem in self.elementos['opciones']:
                                    if elem.name == 'module':
                                        elem.active = True

            elif elemento.name == 'config':
                if elemento.active:
                    for container in self.elementos['containers']:
                        if container.selected:
                            self.config_bit = True
                            self.config_panel(container, screen, position, push_position)

        self.draw_actions(screen, position)

    def config_panel(self, container, screen, over_mouse, pushed):
        if self.time:
            self.time_field.buffer = [char for char in str(container.time)]
        self.time = False
        screen.blit(self.font.render('Parámetros del contenedor "'+container.name+'"', True, (0, 0, 0)), self.pos_config)
        screen.blit(self.font.render('Tiempo:', True, (0, 0, 0)), (self.pos_config[0], self.pos_config[1]+39))
        #self.time_field.buffer = [str(container.time)]
        self.time_field.update()
        self.time_field.draw(screen)
        screen.blit(self.ok_n, self.ok_rect3)
        if self.ok_rect3.collidepoint(over_mouse):  # Mouse over button
            screen.blit(self.ok_s, self.ok_rect3)
        if self.ok_rect3.collidepoint(pushed):  # Boton presionado
            container.time = "".join(self.time_field.buffer)
            container.time = int(container.time)
            self.new_time = True

    def cancel(self):
        """Cancelar acciones en ejecución"""
        self.actions = [0]*9
        self.drawing = False
        self.hold_caja = False
        self.hold_knn = False
        self.hold_stand = False
        self.hold_kdn = False
        self.hold_module = False
        self.elem_proper = False
        self.elem_type = False
        self.line_able = False
        self.hold_line = False
        self.connecting = False
        self.init_pos = [0, 0]  # Posicion inicial de la linea
        self.end_line = [0, 0]  # Posicion final de la linea
        self.duple_conection = list()
        self.points_conection = list()
        self.element_moved = None  # Indica el elemento a desplazarse
        self.moving = False  # indica si se encuentra desplazando algun elemento
        self.draw_module = False
        self.elem_modulo = None
        pygame.mouse.set_visible(True)
        position = (0, 0)
        self.text_status[:4] = [0]*4
        return position

    #  -----------------------Relacionado a superficies----------------------------
    def surfaces(self):
        """Superficies disponibles"""
        self.pos_button_action = (400, 10)  # Inicio de posiciones acciones
        self.button_act_panel = pygame.Surface((150, 120))  # Superficie para las acciones
        self.button_act_panel.fill(WHITE)
        self.pos_button_elements = (580, 10)  # Inicio de posiciones acciones
        self.button_ele_panel = pygame.Surface((260, 120))  # Superficie para las acciones
        self.button_ele_panel.fill(WHITE)
        self.pos_info_buttons = (870, 10)  # Inicio de posiciones acciones
        self.button_info = pygame.Surface((80, 120))  # Superficie para las acciones
        self.button_info.fill(WHITE)
        self.pos_rename = (400, 180)  # inicio espacio de trabajo
        self.rename_panel = pygame.Surface((200, 90))  # Superficie para las acciones
        self.rename_panel.fill(GRAY)
        self.workspace = pygame.Surface(self.SIZE_WORKSPACE)
        self.workspace.fill(WHITE)
        self.pos_workspace = (60, 170)  # inicio espacio de trabajo
        self.proper_panel = pygame.Surface((200, 160))
        self.proper_panel.fill(GRAY)
        self.pos_proper = (400, 180)
        self.proper_panel_knn = pygame.Surface((200, 240))
        self.proper_panel_knn.fill(GRAY)
        self.pos_proper = (400, 180)
        self.plot_surface = pygame.Surface((self.SIZE_WORKSPACE[0]-30, self.SIZE_WORKSPACE[1]-30))
        self.plot_surface.fill(GRAY)
        self.pos_plot = (self.pos_workspace[0]+15, self.pos_workspace[1]+15)
        self.pos_config = (95, 210)  # posicion para configuración

    def options_panel(self, position, cont):
        self.image = self.option_s  # Imagen actual de la pestaña opcion (activa)
        self.image_off = self.option_n
        self.rect = self.image.get_rect()  # Recta de la imagen
        self.rect.x = position[0]
        self.rect.y = position[1]*cont

    def proper_surface(self, screen, position):
        """Superficie para propiedades del elemento seleccionado"""
        if self.type_element == 1 or self.type_element == 4:  # Aca se identifica si el panel es para caja, knn o standby
            screen.blit(self.proper_panel, self.pos_proper)
        else:
            screen.blit(self.rename_panel, self.pos_rename)
        screen.blit(self.close, self.close_name_rect)
        screen.blit(self.font.render('Propiedades ' + self.elem_selected, True, (0, 0, 0)),
                    (self.pos_proper[0] + 10, self.pos_proper[1] + 10))
        screen.blit(self.font.render('Nombre: ', True, (0, 0, 0)),
                    (self.pos_proper[0] + 15, self.pos_proper[1] + 40))
        if self.type_element == 1:  # Si es tipo 1, o sea solo caja
            screen.blit(self.font.render('Alpha: ', True, (0, 0, 0)),
                        (self.pos_proper[0] + 25, self.pos_proper[1] + 70))
            screen.blit(self.font.render('Betha: ', True, (0, 0, 0)),
                        (self.pos_proper[0] + 25, self.pos_proper[1] + 100))
            for containter in self.elementos['containers']:
                if containter.selected:
                    for caja in containter.cajas:
                        if caja.tag == self.elem_selected:
                            if caja.mod == 'exp':
                                self.text_status = [0, 1, 0, 0, 0]
                            elif caja.mod == 'ray':
                                self.text_status = [0, 0, 1, 0, 0]
                            elif caja.mod == 'wei':
                                self.text_status = [0, 0, 0, 1, 0]

                    for knn_ind in containter.knn:
                        for set_boxes in knn_ind.cols:
                            for caja in set_boxes:
                                if caja.tag == self.elem_selected:
                                    if caja.mod == 'exp':
                                        self.text_status = [0, 1, 0, 0, 0]
                                    elif caja.mod == 'ray':
                                        self.text_status = [0, 0, 1, 0, 0]
                                    elif caja.mod == 'wei':
                                        self.text_status = [0, 0, 0, 1, 0]

                    for stand_ind in containter.stand:
                        for caja in stand_ind.cajas:
                            if caja.tag == self.elem_selected:
                                if caja.mod == 'exp':
                                    self.text_status = [0, 1, 0, 0, 0]
                                elif caja.mod == 'ray':
                                    self.text_status = [0, 0, 1, 0, 0]
                                elif caja.mod == 'wei':
                                    self.text_status = [0, 0, 0, 1, 0]

            if self.ok_rect2.collidepoint(position):  # Verificar si los parámetros son validos
                screen.blit(self.ok_s, self.ok_rect2)
                screen.blit(self.font.render('Aceptar', True, (0, 0, 0)),
                            (position[0] + 8, position[1] + 8))
            else:
                screen.blit(self.ok_n, self.ok_rect2)

        elif self.type_element == 2:
            for container in self.elementos['containers']:
                if container.selected:
                    for knn_ind in container.knn:
                        print(knn_ind.tag)
                        if knn_ind.tag == self.elem_selected:
                            self.text_status = [0, 0, 0, 0, 1]

            if self.ok_rect.collidepoint(position):
                screen.blit(self.ok_s, self.ok_rect)
                screen.blit(self.font.render('Aceptar', True, (0, 0, 0)),
                            (position[0] + 8, position[1] + 8))
            else:
                screen.blit(self.ok_n, self.ok_rect)
        elif self.type_element == 3:  # Stand by
            self.text_status = [0, 0, 0, 0, 1]
            if self.ok_rect.collidepoint(position):
                screen.blit(self.ok_s, self.ok_rect)
                screen.blit(self.font.render('Aceptar', True, (0, 0, 0)),
                            (position[0] + 8, position[1] + 8))
            else:
                screen.blit(self.ok_n, self.ok_rect)
        elif self.type_element == 4:  # KDN
            screen.blit(self.font.render('Alpha: ', True, (0, 0, 0)),
                        (self.pos_proper[0] + 25, self.pos_proper[1] + 70))
            screen.blit(self.font.render('Betha: ', True, (0, 0, 0)),
                        (self.pos_proper[0] + 25, self.pos_proper[1] + 100))
            for container in self.elementos['containers']:
                for kdn in container.kdn:
                    if kdn.tag == self.elem_selected:
                        if kdn.mod == 'exp':
                            self.text_status = [0, 1, 0, 0, 0]
                        elif caja.mod == 'ray':
                            self.text_status = [0, 0, 1, 0, 0]
                        elif caja.mod == 'wei':
                            self.text_status = [0, 0, 0, 1, 0]
                if self.ok_rect2.collidepoint(position):
                    screen.blit(self.ok_s, self.ok_rect2)
                    screen.blit(self.font.render('Aceptar', True, (0, 0, 0)),
                                (position[0] + 8, position[1] + 8))
                else:
                    screen.blit(self.ok_n, self.ok_rect2)

    def type_surface(self, screen, position, pushed):
        """Superficie para tipo del elemento seleccionado"""
        if self.type_element == 1:  # Propiedades para caja sola
            screen.blit(self.proper_panel, self.pos_proper)
            screen.blit(self.close, self.close_name_rect)
            screen.blit(self.font.render('Estructura '+self.elem_selected, True, (0, 0, 0)),
                        (self.pos_proper[0] + 10, self.pos_proper[1] + 5))
            screen.blit(self.font.render('Tipo Distribución: ', True, (0, 0, 0)),
                        (self.pos_proper[0] + 10, self.pos_proper[1] + 30))
            self.check.draw(screen)
            for container in self.elementos['containers']:
                if container.selected:
                    for caja in container.cajas:
                        if caja.tag == self.elem_selected:
                            self.check.push = not caja.orientation
            for textbutton in self.text_buttons:  # Recorrer todos los botones de texto
                textbutton.draw_button(screen)  # Dibujar el boton
                if textbutton.recta.collidepoint(position):  # Si se pasa sobre el boton
                    textbutton.over = True  # Se marca como sobrepuesto
                    if textbutton.recta.collidepoint(pushed):  # Se presiona el boton
                        for container in self.elementos['containers']:  # Buscar contenedor actual
                            if container.selected:
                                for caja in container.cajas:  # Cajas del contenedor actual
                                    if caja.tag == self.elem_selected:  # Si la caja tiene el nombre del elem seleccionado
                                        caja.mod = textbutton.name  # Se cambia el tipo de confiabilidad
                                for knn_ind in container.knn:
                                    for set_boxes in knn_ind.cols:
                                        for caja in set_boxes:
                                            if caja.tag == self.elem_selected:  # Si la caja tiene el nombre del elem seleccionado
                                                caja.mod = textbutton.name  # Se cambia el tipo de confiabilidad
                                for stand_ind in container.stand:
                                    for caja in stand_ind.cajas:
                                        if caja.tag == self.elem_selected:
                                            caja.mod = textbutton.name
                else:
                    textbutton.over = False
        elif self.type_element == 2:  # Propiedades para knn
            screen.blit(self.proper_panel_knn, self.pos_proper)
            screen.blit(self.close, self.close_name_rect)
            screen.blit(self.font.render('Estructura ' + self.elem_selected, True, (0, 0, 0)),
                        (self.pos_proper[0] + 10, self.pos_proper[1] + 10))
            num_rows = 1
            for container in self.elementos['containers']:
                if container.selected:
                    for knn_ind in container.knn:
                        if knn_ind.tag == self.elem_selected:
                            num_rows = knn_ind.num_rows
            screen.blit(self.font.render('Nro. parelelos:  ' + str(num_rows), True, (0, 0, 0)),
                        (self.pos_proper[0] + 10, self.pos_proper[1] + 40))

            if self.addline_rect.collidepoint(position):
                screen.blit(self.addline_s, self.addline_rect)
                screen.blit(self.font.render('Agregar paralelo', True, (0, 0, 0)),
                            (position[0] + 8, position[1] + 8))
            else:
                screen.blit(self.addline_n, self.addline_rect)

            if self.reduceline_rect.collidepoint(position):
                screen.blit(self.reduceline_s, self.reduceline_rect)
                screen.blit(self.font.render('Reducir paralelo', True, (0, 0, 0)),
                            (position[0] + 8, position[1] + 8))
            else:
                screen.blit(self.reduceline_n, self.reduceline_rect)

            for ind, recta in enumerate(self.rects_knn_add):  # Recta de agregar series
                screen.blit(self.font.render('Paralelo ' + str(ind+1) + ':', True, (0, 0, 0)),
                            (self.pos_proper[0] + 35, (self.pos_proper[1] + 75) + (ind*35)))
                for container in self.elementos['containers']:
                    if container.selected:
                        for knn_ind in container.knn:
                            if ind < knn_ind.num_rows:
                                if recta.collidepoint(position):
                                    screen.blit(self.addline_s, recta)
                                    screen.blit(self.font.render('Agregar serie', True, (0, 0, 0)),
                                                (position[0] + 8, position[1] + 8))
                                else:
                                    screen.blit(self.addline_n, recta)
                            else:
                                screen.blit(self.addline_not, recta)

            for ind, recta in enumerate(self.rects_knn_reduce):  # Rectar de reducir series
                for container in self.elementos['containers']:
                    if container.selected:
                        for knn_ind in container.knn:
                            if ind < knn_ind.num_rows:
                                if recta.collidepoint(position):
                                    screen.blit(self.reduceline_s, recta)
                                    screen.blit(self.font.render('Reducir serie', True, (0, 0, 0)),
                                                (position[0] + 8, position[1] + 8))
                                else:
                                    screen.blit(self.reduceline_n, recta)
                            else:
                                screen.blit(self.reduceline_not, recta)

        elif self.type_element == 3:
            screen.blit(self.rename_panel, self.pos_rename)
            screen.blit(self.close, self.close_name_rect)
            screen.blit(self.font.render('Estructura ' + self.elem_selected, True, (0, 0, 0)),
                        (self.pos_proper[0] + 10, self.pos_proper[1] + 10))
            num_elements = 1
            for container in self.elementos['containers']:
                if container.selected:
                    for stand_ind in container.stand:
                        if stand_ind.tag == self.elem_selected:
                            num_elements = stand_ind.num_elements
            screen.blit(self.font.render('Nro. elementos:  ' + str(num_elements), True, (0, 0, 0)),
                        (self.pos_proper[0] + 10, self.pos_proper[1] + 40))
            if self.addline_rect.collidepoint(position):
                screen.blit(self.addline_s, self.addline_rect)
                screen.blit(self.font.render('Agregar elemento', True, (0, 0, 0)),
                            (position[0] + 8, position[1] + 8))
            else:
                screen.blit(self.addline_n, self.addline_rect)

            if self.reduceline_rect.collidepoint(position):
                screen.blit(self.reduceline_s, self.reduceline_rect)
                screen.blit(self.font.render('Eliminar elemento', True, (0, 0, 0)),
                            (position[0] + 8, position[1] + 8))
            else:
                screen.blit(self.reduceline_n, self.reduceline_rect)

        elif self.type_element == 4:
            screen.blit(self.proper_panel, self.pos_proper)
            screen.blit(self.close, self.close_name_rect)
            screen.blit(self.font.render('Estructura ' + self.elem_selected, True, (0, 0, 0)),
                        (self.pos_proper[0] + 10, self.pos_proper[1] + 5))
            screen.blit(self.font.render('Tipo Distribución: ', True, (0, 0, 0)),
                        (self.pos_proper[0] + 10, self.pos_proper[1] + 30))
            for textbutton in self.text_buttons:  # Recorrer todos los botones de texto
                textbutton.draw_button(screen)  # Dibujar el boton
                if textbutton.recta.collidepoint(position):  # Si se pasa sobr eel boton
                    textbutton.over = True  # Se marca como sobrepuesto
                    if textbutton.recta.collidepoint(pushed):  # Se presiona el boton
                        for container in self.elementos['containers']:  # Buscar contenedor actual
                            if container.selected:
                                for kdn in container.kdn:
                                    if kdn.tag == self.elem_selected:
                                        kdn.mode = textbutton.name
                else:
                    textbutton.over = False

            num_rows = 1
            num_active = 1
            for container in self.elementos['containers']:
                if container.selected:
                    for kdn in container.kdn:
                        if kdn.tag == self.elem_selected:
                            num_rows = kdn.num_rows
                            num_active = kdn.num_active
            screen.blit(self.font.render('n: ' + str(num_rows), True, (0, 0, 0)),
                        (self.pos_proper[0] + 10, self.pos_proper[1] + 80))
            screen.blit(self.font.render('K: ' + str(num_active), True, (0, 0, 0)),
                        (self.pos_proper[0] + 10, self.pos_proper[1] + 110))

            if self.addline_rect_kdn.collidepoint(position):
                screen.blit(self.addline_s, self.addline_rect_kdn)
                screen.blit(self.font.render('Agregar elemento', True, (0, 0, 0)),
                            (position[0] + 8, position[1] + 8))
            else:
                screen.blit(self.addline_n, self.addline_rect_kdn)

            if self.reduceline_rect_kdn.collidepoint(position):
                screen.blit(self.reduceline_s, self.reduceline_rect_kdn)
                screen.blit(self.font.render('Eliminar elemento', True, (0, 0, 0)),
                            (position[0] + 8, position[1] + 8))
            else:
                screen.blit(self.reduceline_n, self.reduceline_rect_kdn)


            if self.addline_rect_kdn2.collidepoint(position):
                screen.blit(self.addline_s, self.addline_rect_kdn2)
                screen.blit(self.font.render('Agregar elemento', True, (0, 0, 0)),
                            (position[0] + 8, position[1] + 8))
            else:
                screen.blit(self.addline_n, self.addline_rect_kdn2)

            if self.reduceline_rect_kdn2.collidepoint(position):
                screen.blit(self.reduceline_s, self.reduceline_rect_kdn2)
                screen.blit(self.font.render('Eliminar elemento', True, (0, 0, 0)),
                            (position[0] + 8, position[1] + 8))
            else:
                screen.blit(self.reduceline_n, self.reduceline_rect_kdn2)

    def name_surface(self, screen, position):
        screen.blit(self.rename_panel, self.pos_rename)
        screen.blit(self.close, self.close_name_rect)
        screen.blit(self.font.render('Nombre pestaña:', True, (0, 0, 0)),
                    (self.pos_rename[0]+10, self.pos_rename[1]+10))
        if self.ok_rect.collidepoint(position):
            screen.blit(self.ok_s, self.ok_rect)
            screen.blit(self.font.render('Aceptar', True, (0, 0, 0)),
                        (position[0] + 8, position[1] + 8))
        else:
            screen.blit(self.ok_n, self.ok_rect)

    # ---------------Lo constante-------------------------------
    def load_pics(self):
        """Cargar imagenes"""
        self.addline_s = pygame.image.load(os.path.join('icons', 'addline_s.png'))
        self.addline_n = pygame.image.load(os.path.join('icons', 'addline_n.png'))
        self.reduceline_s = pygame.image.load(os.path.join('icons', 'reduceline_s.png'))
        self.reduceline_n = pygame.image.load(os.path.join('icons', 'reduceline_n.png'))
        self.addline_not = pygame.image.load(os.path.join('icons', 'addline_not.png'))
        self.reduceline_not = pygame.image.load(os.path.join('icons', 'reduceline_not.png'))
        self.pestana_s = pygame.image.load(os.path.join('pics', 'pesta_s.png'))
        self.pestana_n = pygame.image.load(os.path.join('pics', 'pesta_n.png'))
        self.new = pygame.image.load(os.path.join('pics', 'pesta_new.png'))
        self.option_s = pygame.image.load(os.path.join('pics', 'option_s.png'))
        self.option_n = pygame.image.load(os.path.join('pics', 'option_n.png'))
        self.close = pygame.image.load(os.path.join('icons', 'close.png'))
        self.add = pygame.image.load(os.path.join('icons', 'add.png'))
        self.grid = pygame.image.load(os.path.join('pics', 'punto.png'))
        self.check = pygame.image.load(os.path.join('icons', 'check.png'))
        self.uncheck = pygame.image.load(os.path.join('icons', 'uncheck.png'))
        # Acciones
        self.connect_n = pygame.image.load(os.path.join('icons', 'connect_n.png'))
        self.connect_s = pygame.image.load(os.path.join('icons', 'connect_s.png'))
        self.disconnect_n = pygame.image.load(os.path.join('icons', 'disconnect_n.png'))
        self.disconnect_s = pygame.image.load(os.path.join('icons', 'disconnect_s.png'))
        self.move_n = pygame.image.load(os.path.join('icons', 'move_n.png'))
        self.move_s = pygame.image.load(os.path.join('icons', 'move_s.png'))
        self.delete_n = pygame.image.load(os.path.join('icons', 'delete_n.png'))
        self.delete_s = pygame.image.load(os.path.join('icons', 'delete_s.png'))
        self.export_n = pygame.image.load(os.path.join('icons', 'export_n.png'))
        self.export_s = pygame.image.load(os.path.join('icons', 'export_s.png'))
        self.import_n = pygame.image.load(os.path.join('icons', 'import_n.png'))
        self.import_s = pygame.image.load(os.path.join('icons', 'import_s.png'))
        self.rename_n = pygame.image.load(os.path.join('icons', 'rename_n.png'))
        self.rename_s = pygame.image.load(os.path.join('icons', 'rename_s.png'))
        self.save_n = pygame.image.load(os.path.join('icons', 'save_n.png'))
        self.save_s = pygame.image.load(os.path.join('icons', 'save_s.png'))
        self.load_n = pygame.image.load(os.path.join('icons', 'load_n.png'))
        self.load_s = pygame.image.load(os.path.join('icons', 'load_s.png'))
        self.ok_n = pygame.image.load(os.path.join('icons', 'ok_n.png'))
        self.ok_s = pygame.image.load(os.path.join('icons', 'ok_s.png'))
        self.delete_line = pygame.image.load(os.path.join('icons', 'delete_lines.png'))
        self.info_n = pygame.image.load(os.path.join('icons', 'info_n.png'))
        self.info_s = pygame.image.load(os.path.join('icons', 'info_s.png'))
        self.help_n = pygame.image.load(os.path.join('icons', 'help_n.png'))
        self.help_s = pygame.image.load(os.path.join('icons', 'help_s.png'))
        # Elementos
        self.caja_mini = pygame.image.load(os.path.join('pics', 'caja_mini.png'))
        self.stand_mini = pygame.image.load(os.path.join('pics', 'stand_by_mini.png'))
        self.knn_mini = pygame.image.load(os.path.join('pics', 'knn_mini.png'))
        self.kdn_mini = pygame.image.load(os.path.join('pics', 'kdn_mini.png'))
        # Normales
        self.caja = pygame.image.load(os.path.join('pics', 'caja.png'))
        self.stand = pygame.image.load(os.path.join('pics', 'stand_by.png'))
        self.knn = pygame.image.load(os.path.join('pics', 'knn.png'))
        self.kdn = pygame.image.load(os.path.join('pics', 'kdn.png'))
        self.module = pygame.image.load(os.path.join('pics', 'modulo.png'))
        #Acciones
        self.line_on = pygame.image.load(os.path.join('pics', 'linea_on.png'))
        self.line_off = pygame.image.load(os.path.join('pics', 'linea_off.png'))

    def rect_actions(self, pos_actions):
        # Botones arriba y abajo del scroll
        self.up = pygame.image.load(os.path.join("icons", "up.png"))
        self.down = pygame.image.load(os.path.join("icons", "down.png"))
        width = 25
        self.up_surface = pygame.Surface((width, width))
        self.up_surface.fill(WHITE2)
        self.down_surface = pygame.Surface((width, width))
        self.down_surface.fill(WHITE2)
        #----------------------------------
        self.connect_rect = self.connect_n.get_rect()
        self.connect_rect.x = pos_actions[0]+2
        self.connect_rect.y = pos_actions[1]+1
        self.disconnect_rect = self.disconnect_n.get_rect()
        self.disconnect_rect.x = pos_actions[0] + 52
        self.disconnect_rect.y = pos_actions[1] + 1
        self.move_rect = self.move_n.get_rect()
        self.move_rect.x = pos_actions[0] + 105
        self.move_rect.y = pos_actions[1] + 1
        self.delete_line_rect = self.delete_line.get_rect()
        # 2da fila
        self.delete_rect = self.delete_n.get_rect()
        self.delete_rect.x = pos_actions[0]+2
        self.delete_rect.y = pos_actions[1]+40
        self.export_rect = self.export_n.get_rect()
        self.export_rect.x = pos_actions[0] + 54
        self.export_rect.y = pos_actions[1] + 42
        self.import_rect = self.import_n.get_rect()
        self.import_rect.x = pos_actions[0] + 107
        self.import_rect.y = pos_actions[1] + 42
        # 3ra fila
        self.rename_rect = self.rename_n.get_rect()
        self.rename_rect.x = pos_actions[0] + 2
        self.rename_rect.y = pos_actions[1] + 81
        self.save_rect = self.save_n.get_rect()
        self.save_rect.x = pos_actions[0] + 54
        self.save_rect.y = pos_actions[1] + 83
        self.load_rect = self.load_n.get_rect()
        self.load_rect.x = pos_actions[0] + 107
        self.load_rect.y = pos_actions[1] + 83
        self.close_name_rect = self.close.get_rect()
        self.close_name_rect.x = self.pos_rename[0] + 170
        self.close_name_rect.y = self.pos_rename[1] + 5
        self.ok_rect = self.ok_n.get_rect()
        self.ok_rect.x = self.pos_rename[0] + 159
        self.ok_rect.y = self.pos_rename[1] + 45
        self.ok_rect2 = self.ok_n.get_rect()  # Ok para propiedades
        self.ok_rect2.x = self.pos_proper[0] + 85
        self.ok_rect2.y = self.pos_proper[1] + 125
        self.ok_rect3 = self.ok_n.get_rect()  # Ok para configu
        self.ok_rect3.x = self.pos_config[0] + 85
        self.ok_rect3.y = self.pos_config[1] + 125
        self.addline_rect = self.addline_n.get_rect()
        self.addline_rect.x = self.pos_proper[0] + 110
        self.addline_rect.y = self.pos_proper[1] + 35
        self.reduceline_rect = self.reduceline_n.get_rect()
        self.reduceline_rect.x = self.pos_proper[0] + 145
        self.reduceline_rect.y = self.pos_proper[1] + 35
        self.addline_rect_kdn = self.addline_n.get_rect()
        self.addline_rect_kdn.x = self.pos_proper[0] + 35
        self.addline_rect_kdn.y = self.pos_proper[1] + 75
        self.reduceline_rect_kdn = self.reduceline_n.get_rect()
        self.reduceline_rect_kdn.x = self.pos_proper[0] + 65
        self.reduceline_rect_kdn.y = self.pos_proper[1] + 75
        self.addline_rect_kdn2 = self.addline_n.get_rect()
        self.addline_rect_kdn2.x = self.pos_proper[0] + 35
        self.addline_rect_kdn2.y = self.pos_proper[1] + 104
        self.reduceline_rect_kdn2 = self.reduceline_n.get_rect()
        self.reduceline_rect_kdn2.x = self.pos_proper[0] + 65
        self.reduceline_rect_kdn2.y = self.pos_proper[1] + 104
        self.rects_knn_add = []
        self.rects_knn_reduce = []
        for number in range(5):
            recta_red = self.reduceline_rect.copy()
            recta_red.x = self.pos_proper[0] + 145
            recta_red.y = self.pos_proper[1] + 35*(number+2)
            self.rects_knn_reduce.append(recta_red)
            recta_add = self.addline_rect.copy()
            recta_add.x = self.pos_proper[0] + 110
            recta_add.y = self.pos_proper[1] + 35 * (number + 2)
            self.rects_knn_add.append(recta_add)
        self.rect_check_orien = self.check.get_rect()
        self.rect_check_orien.x = self.pos_proper[0]+100
        self.rect_check_orien.y = self.pos_proper[0] + 160
        # Info y ayuda
        self.info_rect = self.info_n.get_rect()
        self.info_rect.x = pos_actions[0] + 54
        self.info_rect.y = pos_actions[1] + 83
        self.help_rect = self.help_n.get_rect()
        self.help_rect.x = pos_actions[0] + 107
        self.help_rect.y = pos_actions[1] + 83

    def draw_actions(self, screen, position):
        if self.connect_rect.collidepoint(position):
            screen.blit(self.connect_s, self.connect_rect)
            screen.blit(self.font.render('Conectar', True, (0, 0, 0)),
                        (position[0] + 8, position[1] + 8))
        else:
            screen.blit(self.connect_n, self.connect_rect)

        if self.disconnect_rect.collidepoint(position):
            screen.blit(self.disconnect_s, self.disconnect_rect)
            screen.blit(self.font.render('Desconectar', True, (0, 0, 0)),
                        (position[0] + 8, position[1] + 8))
        else:
            screen.blit(self.disconnect_n, self.disconnect_rect)

        if self.move_rect.collidepoint(position):
            screen.blit(self.move_s, self.move_rect)
            screen.blit(self.font.render('Mover', True, (0, 0, 0)),
                        (position[0] + 8, position[1] + 8))
        else:
            screen.blit(self.move_n, self.move_rect)

        if self.delete_rect.collidepoint(position):
            screen.blit(self.delete_s, self.delete_rect)
            screen.blit(self.font.render('Borrar elemento', True, (0, 0, 0)),
                        (position[0] + 8, position[1] + 8))
        else:
            screen.blit(self.delete_n, self.delete_rect)

        if self.export_rect.collidepoint(position):
            screen.blit(self.export_s, self.export_rect)
            screen.blit(self.font.render('Exportar módulo', True, (0, 0, 0)),
                        (position[0] + 8, position[1] + 8))
        else:
            screen.blit(self.export_n, self.export_rect)

        if self.import_rect.collidepoint(position):
            screen.blit(self.import_s, self.import_rect)
            screen.blit(self.font.render('Importar módulo', True, (0, 0, 0)),
                        (position[0] + 8, position[1] + 8))
        else:
            screen.blit(self.import_n, self.import_rect)

        if self.rename_rect.collidepoint(position):
            screen.blit(self.rename_s, self.rename_rect)
            screen.blit(self.font.render('Renombrar pestaña', True, (0, 0, 0)),
                        (position[0] + 8, position[1] + 8))
        else:
            screen.blit(self.rename_n, self.rename_rect)

        if self.info_rect.collidepoint(position):
            screen.blit(self.info_s, self.info_rect)
            screen.blit(self.font.render('Información', True, (0, 0, 0)),
                        (position[0] + 8, position[1] + 8))
        else:
            screen.blit(self.info_n, self.info_rect)

        if self.help_rect.collidepoint(position):
            screen.blit(self.help_s, self.help_rect)
            screen.blit(self.font.render('Ayuda', True, (0, 0, 0)),
                        (position[0] + 8, position[1] + 8))
        else:
            screen.blit(self.help_n, self.help_rect)

        if self.caja_mini_rect.collidepoint(position):
            screen.blit(self.font.render('Elemento individual', True, (0, 0, 0)),
                        (position[0] + 8, position[1] + 8))

        if self.knn_mini_rect.collidepoint(position):
            screen.blit(self.font.render('Paralelo', True, (0, 0, 0)),
                        (position[0] + 8, position[1] + 8))

        if self.stand_mini_rect.collidepoint(position):
            screen.blit(self.font.render('Stand By', True, (0, 0, 0)),
                        (position[0] + 8, position[1] + 8))

        if self.kdn_mini_rect.collidepoint(position):
            screen.blit(self.font.render('KdN', True, (0, 0, 0)),
                        (position[0] + 8, position[1] + 8))

    def rect_elements(self, position):
        self.caja_mini_rect = self.caja_mini.get_rect()
        self.caja_mini_rect.x = position[0] + 15
        self.caja_mini_rect.y = position[1] + 40
        self.knn_mini_rect = self.knn_mini.get_rect()
        self.knn_mini_rect.x = position[0] + 75
        self.knn_mini_rect.y = position[1] + 40
        self.stand_mini_rect = self.stand_mini.get_rect()
        self.stand_mini_rect.x = position[0] + 125
        self.stand_mini_rect.y = position[1] + 40
        self.kdn_mini_rect = self.kdn_mini.get_rect()
        self.kdn_mini_rect.x = position[0] + 195
        self.kdn_mini_rect.y = position[1] + 40

    def draw_elements(self, screen):
        """Dibujar elementos a seleccionar (caja-mini, stand-by y knn)"""
        screen.blit(self.caja_mini, self.caja_mini_rect)
        screen.blit(self.knn_mini, self.knn_mini_rect)
        screen.blit(self.stand_mini, self.stand_mini_rect)
        screen.blit(self.kdn_mini, self.kdn_mini_rect)

    @staticmethod
    def canvas_space(fig):
        """Dibujar axis sobre la GUI"""
        canvas = agg.FigureCanvasAgg(fig)
        canvas.draw()
        renderer = canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        size = canvas.get_width_height()
        surf = pygame.image.fromstring(raw_data, size, "RGB")
        return surf
